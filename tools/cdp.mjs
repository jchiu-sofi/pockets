#!/usr/bin/env node
/**
 * Minimal Chrome DevTools Protocol driver — evaluate a script in a page at an exact
 * viewport, and optionally screenshot it.
 *
 * Why this exists: headless Chrome clamps `--window-size` to a ~500px minimum layout
 * viewport and then crops the capture to whatever size was requested, so mobile
 * screens get laid out wider than the phone they're meant for and the right edge is
 * sheared off. Loading in a fixed-width iframe fixes the layout but breaks
 * `--dump-dom` (which serializes only the top document) and blocks parent access
 * across opaque file:// origins. `Emulation.setDeviceMetricsOverride` just sets the
 * viewport, with no workaround needed.
 *
 *   node tools/cdp.mjs --eval-file tools/ui-audit-expr.js docs/screens/*.html
 *   node tools/cdp.mjs --shot-dir renders --width 390 --height 844 docs/screens/*.html
 *
 * Prints one JSON line per page to stdout. No dependencies.
 */
import { spawn } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve, basename } from "node:path";

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9333 + (process.pid % 500);

const args = process.argv.slice(2);
const opt = (name, fallback = null) => {
  const i = args.indexOf(name);
  if (i === -1) return fallback;
  const v = args[i + 1];
  args.splice(i, 2);
  return v;
};
const evalFile = opt("--eval-file");
const shotDir = opt("--shot-dir");
const width = Number(opt("--width", "390"));
const height = Number(opt("--height", "844"));
const scale = Number(opt("--scale", "1"));
const fullPage = args.includes("--full-page");
if (fullPage) args.splice(args.indexOf("--full-page"), 1);
const files = args.filter((a) => !a.startsWith("--"));

if (!files.length) {
  console.error("usage: cdp.mjs [--eval-file f.js] [--shot-dir d] [--width n] [--height n] <files...>");
  process.exit(1);
}
const expression = evalFile ? readFileSync(evalFile, "utf8") : null;

const profile = mkdtempSync(join(tmpdir(), "cdp-"));
const chrome = spawn(CHROME, [
  "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
  "--no-default-browser-check", "--disable-extensions",
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`,
  "about:blank",
], { stdio: "ignore" });

const cleanup = () => {
  try { chrome.kill("SIGKILL"); } catch {}
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
};
process.on("exit", cleanup);
process.on("SIGINT", () => { cleanup(); process.exit(130); });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function browserWs() {
  // Chrome needs a moment before the debugging endpoint answers.
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/version`);
      return (await r.json()).webSocketDebuggerUrl;
    } catch { await sleep(150); }
  }
  throw new Error("Chrome DevTools endpoint never came up");
}

class Session {
  constructor(ws) {
    this.ws = ws;
    this.id = 0;
    this.pending = new Map();
    this.waiters = [];
    ws.addEventListener("message", (ev) => {
      const msg = JSON.parse(ev.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve: res, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        msg.error ? reject(new Error(msg.error.message)) : res(msg.result);
      } else if (msg.method) {
        this.waiters = this.waiters.filter((w) => {
          if (w.method !== msg.method) return true;
          w.resolve(msg.params);
          return false;
        });
      }
    });
  }

  send(method, params = {}, sessionId) {
    const id = ++this.id;
    const payload = { id, method, params };
    if (sessionId) payload.sessionId = sessionId;
    this.ws.send(JSON.stringify(payload));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }

  once(method, timeoutMs = 15000) {
    return new Promise((resolve, reject) => {
      const w = { method, resolve };
      this.waiters.push(w);
      setTimeout(() => {
        this.waiters = this.waiters.filter((x) => x !== w);
        reject(new Error(`timeout waiting for ${method}`));
      }, timeoutMs);
    });
  }
}

const wsUrl = await browserWs();
const ws = new WebSocket(wsUrl);
await new Promise((res, rej) => {
  ws.addEventListener("open", res, { once: true });
  ws.addEventListener("error", rej, { once: true });
});
const s = new Session(ws);

const { targetId } = await s.send("Target.createTarget", { url: "about:blank" });
const { sessionId } = await s.send("Target.attachToTarget", { targetId, flatten: true });
await s.send("Page.enable", {}, sessionId);
await s.send("Runtime.enable", {}, sessionId);

for (const file of files) {
  const url = "file://" + resolve(file);
  const result = { file: basename(file) };
  try {
    await s.send("Emulation.setDeviceMetricsOverride", {
      width, height, deviceScaleFactor: scale, mobile: true,
    }, sessionId);

    const loaded = s.once("Page.loadEventFired");
    await s.send("Page.navigate", { url }, sessionId);
    await loaded;
    // Webfonts and the Tailwind CDN finish after load; layout shifts until they do.
    await sleep(1200);

    if (expression) {
      const r = await s.send("Runtime.evaluate", {
        expression, returnByValue: true, awaitPromise: true,
      }, sessionId);
      if (r.exceptionDetails) throw new Error(r.exceptionDetails.text || "eval threw");
      Object.assign(result, r.result.value);
    }

    if (shotDir) {
      const shot = await s.send("Page.captureScreenshot", {
        format: "png", captureBeyondViewport: fullPage,
      }, sessionId);
      const out = join(shotDir, basename(file).replace(/\.html?$/, "") + ".png");
      writeFileSync(out, Buffer.from(shot.data, "base64"));
      result.screenshot = out;
    }
  } catch (e) {
    result.error = e.message;
  }
  console.log(JSON.stringify(result));
}

ws.close();
cleanup();
process.exit(0);

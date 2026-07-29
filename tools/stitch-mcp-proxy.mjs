#!/usr/bin/env node
/**
 * stdio -> HTTP proxy for Google's Stitch MCP server.
 *
 * Why this exists: stitch.googleapis.com/mcp advertises `upload_design_md` with an
 * outputSchema containing `$ref: "#/$defs/ScreenInstance"` and an empty `$defs`.
 * Claude Code validates every schema when it loads a server, and one dangling
 * reference makes the whole tools/list fail — all 15 tools disappear with
 * "can't resolve reference #/$defs/ScreenInstance from id #".
 *
 * This proxy forwards JSON-RPC over stdio to the HTTP endpoint and repairs
 * unresolvable $refs in tools/list responses on the way back. Remove it once
 * Google fixes the schema; nothing else here is load-bearing.
 *
 * Credential: read from STITCH_API_KEY, else ~/.config/stitch/api-key.
 * Never pass the key on the command line — it would land in shell history.
 */
import { createInterface } from "node:readline";
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const ENDPOINT = process.env.STITCH_MCP_URL ?? "https://stitch.googleapis.com/mcp";
const KEY_FILE = join(homedir(), ".config", "stitch", "api-key");

function loadKey() {
  if (process.env.STITCH_API_KEY?.trim()) return process.env.STITCH_API_KEY.trim();
  try {
    const k = readFileSync(KEY_FILE, "utf8").trim();
    if (k) return k;
  } catch {}
  process.stderr.write(
    `stitch-mcp-proxy: no API key. Set STITCH_API_KEY or write it to ${KEY_FILE}\n`,
  );
  process.exit(1);
}
const API_KEY = loadKey();

const log = (msg) => process.stderr.write(`stitch-mcp-proxy: ${msg}\n`);
const send = (obj) => process.stdout.write(JSON.stringify(obj) + "\n");

/** Collect every $ref target under a node. */
function collectRefs(node, acc = new Set()) {
  if (Array.isArray(node)) {
    for (const v of node) collectRefs(v, acc);
  } else if (node && typeof node === "object") {
    for (const [k, v] of Object.entries(node)) {
      if (k === "$ref" && typeof v === "string") acc.add(v);
      else collectRefs(v, acc);
    }
  }
  return acc;
}

/** Replace any object containing an unresolvable local $ref with a permissive stub. */
function pruneBrokenRefs(node, defs) {
  if (Array.isArray(node)) return node.map((v) => pruneBrokenRefs(v, defs));
  if (!node || typeof node !== "object") return node;

  const ref = node.$ref;
  if (typeof ref === "string" && ref.startsWith("#/$defs/")) {
    if (!defs.has(ref.slice("#/$defs/".length))) {
      // Dangling reference. Substitute something the validator accepts.
      const { $ref, ...rest } = node;
      return { type: "object", additionalProperties: true, ...rest };
    }
  }
  return Object.fromEntries(
    Object.entries(node).map(([k, v]) => [k, pruneBrokenRefs(v, defs)]),
  );
}

function repairSchema(schema, label) {
  if (!schema || typeof schema !== "object") return schema;
  const defs = new Set(Object.keys(schema.$defs ?? {}));
  const broken = [...collectRefs(schema)].filter(
    (r) => r.startsWith("#/$defs/") && !defs.has(r.slice("#/$defs/".length)),
  );
  if (broken.length === 0) return schema;
  log(`repaired ${label}: dangling ${broken.join(", ")}`);
  return pruneBrokenRefs(schema, defs);
}

function repairToolsList(result) {
  if (!Array.isArray(result?.tools)) return result;
  for (const tool of result.tools) {
    for (const key of ["inputSchema", "outputSchema"]) {
      if (tool[key]) tool[key] = repairSchema(tool[key], `${tool.name}.${key}`);
    }
  }
  return result;
}

/** The endpoint may answer with plain JSON or an SSE stream; accept either. */
async function parseBody(res) {
  const text = await res.text();
  if (!text.trim()) return null;
  if ((res.headers.get("content-type") ?? "").includes("text/event-stream")) {
    const payloads = text
      .split(/\r?\n/)
      .filter((l) => l.startsWith("data:"))
      .map((l) => l.slice(5).trim())
      .filter(Boolean);
    const last = payloads.at(-1);
    return last ? JSON.parse(last) : null;
  }
  return JSON.parse(text);
}

async function forward(message) {
  const isNotification = message.id === undefined;
  let res;
  try {
    res = await fetch(ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json, text/event-stream",
        "X-Goog-Api-Key": API_KEY,
      },
      body: JSON.stringify(message),
      // Screen generation and edits legitimately take minutes.
      signal: AbortSignal.timeout(15 * 60 * 1000),
    });
  } catch (err) {
    log(`transport error on ${message.method}: ${err.message}`);
    if (!isNotification) {
      send({
        jsonrpc: "2.0",
        id: message.id,
        error: { code: -32000, message: `proxy transport error: ${err.message}` },
      });
    }
    return;
  }

  let body;
  try {
    body = await parseBody(res);
  } catch (err) {
    log(`unparseable response to ${message.method}: ${err.message}`);
    if (!isNotification) {
      send({
        jsonrpc: "2.0",
        id: message.id,
        error: { code: -32000, message: `proxy parse error (HTTP ${res.status})` },
      });
    }
    return;
  }

  if (!body) return; // Notification or empty 202. Nothing to relay.
  if (message.method === "tools/list" && body.result) {
    body.result = repairToolsList(body.result);
  }
  send(body);
}

const rl = createInterface({ input: process.stdin, crlfDelay: Infinity });

// Requests are handled concurrently: a long generate_screen call must not block
// subsequent get_screen polls. But stdin closing must not kill in-flight work
// either, so drain before exiting.
let inFlight = 0;
let stdinClosed = false;
const maybeExit = () => {
  if (stdinClosed && inFlight === 0) process.exit(0);
};

rl.on("line", (line) => {
  const trimmed = line.trim();
  if (!trimmed) return;
  let parsed;
  try {
    parsed = JSON.parse(trimmed);
  } catch {
    log(`ignoring non-JSON line (${trimmed.length} bytes)`);
    return;
  }
  for (const msg of Array.isArray(parsed) ? parsed : [parsed]) {
    inFlight += 1;
    forward(msg)
      .catch((err) => log(`unhandled: ${err.message}`))
      .finally(() => {
        inFlight -= 1;
        maybeExit();
      });
  }
});
rl.on("close", () => {
  stdinClosed = true;
  maybeExit();
});

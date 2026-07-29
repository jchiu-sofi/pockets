#!/usr/bin/env bash
# Run tools/ui-audit.js against each screen at a true 390px viewport and print JSON.
set -euo pipefail
cd "$(dirname "$0")/.."
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W=390; H=1600
for f in docs/screens/*.html; do
  tmp=$(mktemp -t audit).html
  python3 - "$f" "$tmp" tools/ui-audit.js <<'PY'
import sys, pathlib
src = pathlib.Path(sys.argv[1]).read_text()
js = pathlib.Path(sys.argv[3]).read_text()
# The audit must run after layout settles, inside a real 390px viewport.
inject = f'<script>window.addEventListener("load",()=>setTimeout(()=>{{{js}}},900));</script>'
pathlib.Path(sys.argv[2]).write_text(src.replace("</body>", inject + "</body>", 1))
PY
  wrap=$(mktemp -t wrap).html
  cat > "$wrap" <<EOF
<!doctype html><meta charset="utf-8"><body style="margin:0">
<iframe src="file://$tmp" scrolling="no" style="width:${W}px;height:${H}px;border:0;display:block"></iframe>
EOF
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-first-run \
    --window-size=$((W+220)),$H --virtual-time-budget=9000 --dump-dom "file://$wrap" 2>/dev/null \
    | python3 -c "
import sys, re, html
m = re.search(r'AUDIT0\s*(.*?)\s*AUDIT1', sys.stdin.read(), re.S)
print(html.unescape(m.group(1)) if m else '{\"findings\":[],\"error\":\"probe did not run\"}')
"
  rm -f "$tmp" "$wrap"
done

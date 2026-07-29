#!/usr/bin/env bash
# Render every docs/screens/*.html to renders/*.png with headless Chrome, then
# rebuild docs/index.html as a browsable gallery (also what GitHub Pages serves).
#
#   ./render.sh                 # all screens
#   ./render.sh 05-rent         # just one (name or partial match)
#   SCALE=2 ./render.sh         # retina, for the deck
#   TALL=1 ./render.sh          # full-length shots instead of one viewport
#   ./render.sh --gallery-only  # skip rendering, just rebuild the gallery
set -euo pipefail
cd "$(dirname "$0")"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W=${W:-390}
H=${H:-844}    # one phone viewport; these designs are viewport-based with a fixed tab bar
SCALE=${SCALE:-1}
FILTER=${1:-}

mkdir -p renders
shopt -s nullglob

build_gallery() {
  {
    cat <<'HEAD'
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SoFi Pockets — screens</title>
<style>
  :root { --ink:#201747; --blue:#00A2C7; --gray:#E5E1E6; --taupe:#AB989D; }
  * { box-sizing:border-box; }
  body { margin:0; padding:40px 32px 64px; background:var(--ink); color:#fff;
         font:15px/1.5 Inter, -apple-system, system-ui, sans-serif; }
  header { max-width:900px; margin:0 0 36px; }
  .eyebrow { font-size:11px; font-weight:600; letter-spacing:.08em;
             text-transform:uppercase; color:var(--blue); margin-bottom:10px; }
  h1 { font-size:30px; font-weight:800; margin:0 0 10px; letter-spacing:-.01em; }
  p  { color:var(--gray); margin:0 0 6px; max-width:70ch; }
  .hint { color:var(--taupe); font-size:13px; }
  .grid { display:grid; gap:28px;
          grid-template-columns:repeat(auto-fill, minmax(390px, 1fr)); }
  figure { margin:0; }
  .phone { position:relative; width:390px; height:844px; border-radius:22px;
           overflow:hidden; background:#fff; box-shadow:0 12px 32px rgba(0,0,0,.4); }
  iframe { width:390px; height:844px; border:0; display:block; }
  figcaption { margin-top:10px; display:flex; align-items:baseline; gap:8px; }
  .num { font:500 12px/1 "Roboto Mono", monospace; color:var(--taupe); }
  .name { font-weight:600; }
  a.open { margin-left:auto; font-size:12px; color:var(--blue); text-decoration:none; }
  a.open:hover { text-decoration:underline; }
</style>
<header>
  <div class="eyebrow">SoFi Pockets · UI mockups</div>
  <h1>Spendable pockets in checking, shared with roommates</h1>
  <p>Generated in Google Stitch, pulled down as editable HTML. Each frame below is
     live — scroll inside it to see the whole screen, or open it full size.</p>
  <p class="hint">Design decisions, open issues, and legal edge cases live in
     <code>decisions.md</code>. Screen prompts live in <code>stitch-prompt.md</code>.</p>
</header>
<div class="grid">
HEAD
    for f in docs/screens/*.html; do
      n=$(basename "$f" .html)
      num=${n%%-*}
      label=$(echo "${n#*-}" | tr '-' ' ')
      printf '<figure><div class="phone"><iframe src="screens/%s" loading="lazy" title="%s"></iframe></div>' \
        "$(basename "$f")" "$label"
      printf '<figcaption><span class="num">%s</span><span class="name">%s</span>' "$num" "$label"
      printf '<a class="open" href="screens/%s" target="_blank">open &rarr;</a></figcaption></figure>\n' \
        "$(basename "$f")"
    done
    echo '</div>'
  } > docs/index.html
  echo "docs/index.html rebuilt"
}

if [[ "$FILTER" == "--gallery-only" ]]; then
  build_gallery
  exit 0
fi

files=()
for f in docs/screens/*.html; do
  [[ -n "$FILTER" && "$f" != *"$FILTER"* ]] && continue
  files+=("$f")
done

if [[ ${#files[@]} -eq 0 ]]; then
  echo "No matching screens in docs/screens/."
  exit 0
fi

height=$H
suffix=""

# Headless Chrome clamps --window-size to a ~500px minimum layout viewport, which
# silently lays screens out wider than a phone and crops the right edge off the
# capture. So each screen is loaded inside an exact-width iframe pinned to the top
# left of an oversized window, and the surrounding window is cropped away after.
WRAP=$(mktemp -t pockets-wrap).html
trap 'rm -f "$WRAP"' EXIT

for f in "${files[@]}"; do
  name=$(basename "$f" .html)
  cat > "$WRAP" <<EOF
<!doctype html><meta charset="utf-8">
<body style="margin:0;background:#fff">
<iframe src="file://$PWD/$f" scrolling="no"
        style="width:${W}px;height:${height}px;border:0;display:block"></iframe>
</body>
EOF
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-first-run \
    --force-device-scale-factor="$SCALE" \
    --window-size="$((W + 220)),$height" \
    --screenshot="renders/$name$suffix.png" \
    --virtual-time-budget=6000 \
    "file://$WRAP" >/dev/null 2>&1
  python3 tools/trim-png.py --crop-width "$((W * SCALE))" "renders/$name$suffix.png" >/dev/null
  echo "renders/$name$suffix.png"
done

build_gallery
echo "${#files[@]} screens rendered"

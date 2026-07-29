#!/usr/bin/env python3
"""Pull the generated screens back onto the real SoFi palette, and make them fit a phone.

Stitch seeded a Material tonal palette from SoFi Blue, which produced a darker teal
(#006780) as `primary` and lavender/mint pastels for the secondary and tertiary
containers. The brand is SoFi Blue, Ink, and warm off-white, with the secondaries as
sparing accents — see the palette table in stitch-prompt.md.

This rewrites the inline `tailwind.config` colour values by token name, so every
`bg-primary` / `text-on-surface` utility in the markup follows automatically without
touching a single class attribute. The generated markup is otherwise left alone.

Idempotent: safe to re-run.

    python3 tools/apply-brand.py            # apply
    python3 tools/apply-brand.py --check    # report drift without writing
"""
import pathlib
import re
import sys

SCREENS = pathlib.Path("docs/screens")

# Brand palette. Primary = SoFi Blue, Ink for dark panels and figures, warm
# off-white surfaces, secondaries only where an accent is genuinely needed.
TOKENS = {
    # SoFi Blue carries headers, primary fills, and links.
    "primary": "#00A2C7",
    "on-primary": "#FFFFFF",
    # Stitch treats primary-container as a saturated fill with light content on
    # top (bg-primary-container + text-surface-container-lowest), so this has to
    # stay brand cyan rather than becoming a pale tint.
    "primary-container": "#00A2C7",
    "on-primary-container": "#FFFFFF",
    "primary-fixed": "#CFEFF8",
    "on-primary-fixed": "#001F28",
    "primary-fixed-dim": "#7FD9EF",
    "on-primary-fixed-variant": "#00485A",
    "surface-tint": "#00A2C7",
    "inverse-primary": "#7FD9EF",
    # Ink replaces the lavender secondary entirely.
    "secondary": "#201747",
    "on-secondary": "#FFFFFF",
    "secondary-container": "#E5E1E6",
    "on-secondary-container": "#201747",
    "secondary-fixed": "#E5E1E6",
    "on-secondary-fixed": "#201747",
    "secondary-fixed-dim": "#C9C4CE",
    "on-secondary-fixed-variant": "#3A2F63",
    # Tertiary is Buttercup, reserved for warnings and low-balance states.
    "tertiary": "#8A6D1F",
    "on-tertiary": "#FFFFFF",
    "tertiary-container": "#FEEFC7",
    "on-tertiary-container": "#4A3A0A",
    "tertiary-fixed": "#FED880",
    "on-tertiary-fixed": "#3A2C00",
    "tertiary-fixed-dim": "#F5C95F",
    "on-tertiary-fixed-variant": "#5C4708",
    # Warm off-white surfaces, matching the live app rather than a blue-grey.
    "background": "#F7F5F2",
    "on-background": "#201747",
    "surface": "#F7F5F2",
    "surface-bright": "#FFFFFF",
    "surface-dim": "#E5E1E6",
    "surface-container-lowest": "#FFFFFF",
    "surface-container-low": "#FBFAF8",
    "surface-container": "#F2F0EC",
    "surface-container-high": "#ECE9E4",
    "surface-container-highest": "#E5E1E6",
    "surface-variant": "#E9E6E1",
    "on-surface": "#201747",
    "on-surface-variant": "#53565A",
    "inverse-surface": "#201747",
    "inverse-on-surface": "#F7F5F2",
    "outline": "#8A8D91",
    "outline-variant": "#D9D5D0",
    # Poppy for errors instead of a generic red.
    "error": "#E03E52",
    "on-error": "#FFFFFF",
    "error-container": "#FCE4E7",
    "on-error-container": "#7A0C1B",
}

# Pastels and blue-greys that also appear as literal hex values in arbitrary
# Tailwind values or inline styles, outside the config block.
LITERALS = {
    "#006780": "#00A2C7",  # Material-derived teal -> SoFi Blue
    "#60578b": "#201747",  # lavender -> Ink
    "#cdc2fd": "#E5E1E6",
    "#cabffa": "#C9C4CE",
    "#e6deff": "#E5E1E6",
    "#564d80": "#201747",
    "#f8f9fe": "#F7F5F2",  # blue-tinted white -> warm off-white
    "#eff1f5": "#F7F5F2",
    "#e1e2e7": "#E5E1E6",
    "#eceef2": "#F2F0EC",
    "#e6e8ed": "#ECE9E4",
    "#f2f3f8": "#FBFAF8",
    "#d8dadf": "#E5E1E6",
    "#969593": "#AB989D",
    "#5e5e5c": "#53565A",
    "#6d797e": "#8A8D91",
    "#bdc8ce": "#D9D5D0",
    "#3d484d": "#53565A",
    "#191c1f": "#201747",
    "#2d3134": "#201747",
    "#ba1a1a": "#E03E52",
    "#ffdad6": "#FCE4E7",
    "#93000a": "#7A0C1B",
    "#5dd5fb": "#7FD9EF",
    "#b7eaff": "#CFEFF8",
    "#003240": "#00485A",
    "#004e61": "#00485A",
}



# The Stitch project's design system is Figtree (headline/display), Inter (body,
# label, eyebrow) and Roboto Mono (tabular numerals). Its canvas renders with that
# system, but some screens were exported with a per-screen stack instead — screens
# 02 and 15 embed Plus Jakarta Sans and JetBrains Mono, and request them from Google
# Fonts. That's why a header reads as "some random font" next to screen 01.
#
# Token names differ between export batches (balance-display vs data-display), so
# the family is chosen from the token's name rather than a fixed list.
FONT_HEADLINE = "Figtree"
FONT_BODY = "Inter"
FONT_MONO = "Roboto Mono"

GOOGLE_FONTS_HREF = (
    "https://fonts.googleapis.com/css2"
    "?family=Figtree:wght@400;500;600;700;800;900"
    "&family=Inter:wght@400;500;600;700"
    "&family=Roboto+Mono:wght@400;500"
    "&display=swap"
)


def family_for(token: str) -> tuple[str, str]:
    """Canonical family for a fontFamily token name, plus its CSS generic fallback."""
    t = token.lower()
    # Tabular figures first: `numeric-table` also contains no display keyword, but
    # check mono-ish names before the display ones so nothing is misrouted.
    if any(k in t for k in ("numeric", "mono", "tabular", "code")):
        return FONT_MONO, "monospace"
    if any(k in t for k in ("headline", "display", "balance", "cents", "title", "heading")):
        return FONT_HEADLINE, "sans-serif"
    return FONT_BODY, "sans-serif"


def rewrite_fonts(html: str) -> tuple[str, int]:
    """Point every fontFamily token at the design system's families."""
    count = 0
    # Keys are quoted in some exports and bare in others.
    block = re.search(r'(["\']?fontFamily["\']?\s*:\s*\{)(.*?)(\n\s*\})', html, re.S)
    if block:
        body = block.group(2)

        def sub_entry(m: re.Match) -> str:
            nonlocal count
            token = m.group("token")
            family, generic = family_for(token)
            want = f'"{family}", "{generic}"'
            if m.group("val").strip() == want:
                return m.group(0)
            count += 1
            return f'{m.group("head")}[{want}]'

        body = re.sub(
            r'(?P<head>["\']?(?P<token>[\w-]+)["\']?\s*:\s*)\[(?P<val>[^\]]*)\]',
            sub_entry, body)
        html = html[:block.start(2)] + body + html[block.end(2):]

    # Repoint the webfont request too, or the families above resolve to nothing.
    def sub_link(m: re.Match) -> str:
        nonlocal count
        href = m.group(1)
        if "Material+Symbols" in href:
            return m.group(0)
        if href == GOOGLE_FONTS_HREF.replace("&", "&amp;"):
            return m.group(0)
        count += 1
        return m.group(0).replace(href, GOOGLE_FONTS_HREF.replace("&", "&amp;"))

    html = re.sub(r'href="(https://fonts\.googleapis\.com/css2\?[^"]*)"', sub_link, html)

    # Some exports also set the family in a plain <style> rule, which would override
    # the config for anything without an explicit font utility.
    def sub_css(m: re.Match) -> str:
        nonlocal count
        stack = m.group(1)
        if FONT_HEADLINE in stack or FONT_BODY in stack or FONT_MONO in stack:
            return m.group(0)
        count += 1
        generic = "monospace" if "monospace" in stack.lower() else "sans-serif"
        family = FONT_MONO if generic == "monospace" else FONT_BODY
        return f"font-family: '{family}', {generic}"

    html = re.sub(r"font-family:\s*([^;}\n]+)", sub_css, html)

    # Keep the stale generated comment from contradicting the file.
    html = html.replace(
        "<!-- Google Fonts: JetBrains Mono and Plus Jakarta Sans -->",
        "<!-- Google Fonts: Figtree, Inter, Roboto Mono -->")

    # The design system sets the hero balance at weight 800 (`balance-display`).
    # The `data-display` token invented by two exports uses 600, which reads
    # visibly lighter next to the other screens. Align the display weights.
    def sub_weight(m: re.Match) -> str:
        nonlocal count
        token, size, inner = m.group("token"), m.group("size"), m.group("inner")
        if not any(k in token.lower() for k in ("balance", "data-display", "cents")):
            return m.group(0)
        # Inner keys are quoted in some exports and bare in others.
        fixed = re.sub(r'(["\']?fontWeight["\']?\s*:\s*")(\d+)(")',
                       r"\g<1>800\g<3>", inner)
        if fixed == inner:
            return m.group(0)
        count += 1
        return m.group(0).replace(inner, fixed)

    html = re.sub(
        r'"(?P<token>[\w-]+)":\s*\[\s*"(?P<size>[\d.]+px)",\s*\{(?P<inner>[^}]*)\}',
        sub_weight, html)
    return html, count


# Stitch's HTML export ships a borderRadius scale shifted a step smaller than the
# one its own design system declares, so every `rounded-xl` card renders at 12px
# instead of the 24px the DESIGN.md specifies (and `sm`/`md` are dropped entirely,
# silently falling back to Tailwind's defaults). These are the declared values.
RADII = {
    "sm": "0.25rem",
    "DEFAULT": "0.5rem",
    "md": "0.75rem",
    "lg": "1rem",
    "xl": "1.5rem",
    "full": "9999px",
}


def rewrite_radii(html: str) -> tuple[str, int]:
    """Replace the whole borderRadius block with the declared scale."""
    m = re.search(r'("borderRadius":\s*\{)(.*?)(\n(\s*)\})', html, re.S)
    if not m:
        return html, 0

    indent = " " * (len(m.group(4)) + 8)
    body = ",\n".join(f'{indent}"{k}": "{v}"' for k, v in RADII.items())
    replacement = f"{m.group(1)}\n{body}{m.group(3)}"
    if replacement == m.group(0):
        return html, 0
    return html[:m.start()] + replacement + html[m.end():], 1


# Every export hardcodes `body { min-height: max(884px, 100dvh) }` — 884px is the
# Stitch canvas height. On any shorter phone (844px on an iPhone 16) that floor makes
# the document 40px taller than the viewport, so anything anchored to `bottom-0` (a
# bottom sheet and its call-to-action, a docked footer) is pushed below the fold with
# no way to scroll to it, because these layouts are `overflow-hidden`.
def rewrite_min_height(html: str) -> tuple[str, int]:
    fixed = re.sub(r"min-height:\s*max\(\d+px,\s*100dvh\)", "min-height: 100dvh", html)
    return fixed, int(fixed != html)


# `h-[header-height]` wraps a spacing *token name* in arbitrary-value brackets, which
# emits `height: header-height` — invalid CSS, silently dropped, so the element gets
# no height at all. The token exists in the config; it just needs the normal syntax.
def rewrite_bracketed_tokens(html: str) -> tuple[str, int]:
    fixed = re.sub(r"\b([a-z]{1,3})-\[([a-z][a-z-]*)\]", r"\1-\2", html)
    return fixed, int(fixed != html)


# Hairline borders were drawn with four subtly different greys — outline-variant
# (#D9D5D0), surface-variant (#E9E6E1), surface-container-high (#ECE9E4) and
# surface-container (#F2F0EC) — so dividers and card edges never quite matched.
# outline-variant is the token meant for boundaries; the others are fill colours.
# border-surface-container-lowest is left alone: that is the deliberate white ring
# that separates stacked avatars.
def rewrite_borders(html: str) -> tuple[str, int]:
    pattern = (r"\bborder-surface-"
               r"(?:variant|dim|container-highest|container-high|container(?!-))\b")
    fixed, n = re.subn(pattern, "border-outline-variant", html)
    return fixed, n


# Two screens use Tailwind's build-time `theme('colors.x')` function inside a plain
# <style> block. That only resolves when a compiler processes the CSS; under the
# Play CDN the declaration is invalid at runtime and silently dropped — which left
# screen 07's Ink card with no background at all, rendering white text on white.
# Resolve them against the screen's own colour config.
def rewrite_theme_calls(html: str) -> tuple[str, int]:
    block = re.search(r'["\']?colors["\']?\s*:\s*\{(.*?)\n\s{4,}\}', html, re.S)
    defined = dict(re.findall(r'["\']?([\w-]+)["\']?\s*:\s*["\'](#[0-9a-fA-F]{6})',
                              block.group(1))) if block else {}

    def sub(m: re.Match) -> str:
        name = m.group(1)
        return defined.get(name) or TOKENS.get(name) or m.group(0)

    fixed, n = re.subn(r"theme\(\s*['\"]colors\.([\w-]+)['\"]\s*\)", sub, html)
    return fixed, n


def rewrite_tokens(html: str) -> tuple[str, int]:
    """Replace "token": "#hex" pairs inside the tailwind config block."""
    count = 0

    def sub(m: re.Match) -> str:
        nonlocal count
        token, current = m.group(1), m.group(2)
        target = TOKENS.get(token)
        if target and current.lower() != target.lower():
            count += 1
            return f'"{token}": "{target}"'
        return m.group(0)

    html = re.sub(r'"([a-z0-9-]+)":\s*"(#[0-9a-fA-F]{6})"', sub, html)
    return html, count


def rewrite_literals(html: str) -> tuple[str, int]:
    count = 0
    for old, new in LITERALS.items():
        pattern = re.compile(re.escape(old), re.IGNORECASE)
        html, n = pattern.subn(new, html)
        count += n
    return html, count


def main() -> int:
    check = "--check" in sys.argv
    files = sorted(SCREENS.glob("*.html"))
    if not files:
        print("No screens found in docs/screens/")
        return 1

    total_tokens = total_literals = 0
    for path in files:
        original = path.read_text(encoding="utf-8")
        html, n_tokens = rewrite_tokens(original)
        html, n_literals = rewrite_literals(html)
        html, n_radii = rewrite_radii(html)
        html, n_fonts = rewrite_fonts(html)
        html, n_minh = rewrite_min_height(html)
        html, n_brackets = rewrite_bracketed_tokens(html)
        html, n_borders = rewrite_borders(html)
        html, n_theme = rewrite_theme_calls(html)

        total_tokens += n_tokens
        total_literals += n_literals
        status = []
        if n_tokens:
            status.append(f"{n_tokens} tokens")
        if n_literals:
            status.append(f"{n_literals} literals")
        if n_radii:
            status.append("radii")
        if n_fonts:
            status.append(f"{n_fonts} fonts")
        if n_minh:
            status.append("min-height")
        if n_brackets:
            status.append("bracketed tokens")
        if n_borders:
            status.append(f"{n_borders} borders")
        if n_theme:
            status.append(f"{n_theme} theme() calls")
        print(f"  {path.name:<30} {', '.join(status) or 'already on brand'}")

        if not check and html != original:
            path.write_text(html, encoding="utf-8")

    verb = "would change" if check else "changed"
    print(f"\n{verb} {total_tokens} config tokens and {total_literals} "
          f"literal hexes across {len(files)} screens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

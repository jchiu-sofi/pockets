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
    "primary-container": "#E3F4FA",
    "on-primary-container": "#00485A",
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

        total_tokens += n_tokens
        total_literals += n_literals
        status = []
        if n_tokens:
            status.append(f"{n_tokens} tokens")
        if n_literals:
            status.append(f"{n_literals} literals")
        print(f"  {path.name:<30} {', '.join(status) or 'already on brand'}")

        if not check and html != original:
            path.write_text(html, encoding="utf-8")

    verb = "would change" if check else "changed"
    print(f"\n{verb} {total_tokens} config tokens and {total_literals} "
          f"literal hexes across {len(files)} screens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

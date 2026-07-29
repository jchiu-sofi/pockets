#!/usr/bin/env python3
"""Give every currency figure one consistent treatment.

The SoFi app uses two distinct patterns, visible in the reference screenshots:

  Hero / stat figures   $ and cents reduced to ~52% and lifted to cap height,
                        digits full size:   $1,282.¹²
  Row / list amounts    cents at full size, inline:   $27,282.12

Stitch produced six different structures across sixteen screens — cents inline at
full size, cents at 45% nudged with margins, `vertical-align: super` at 61%,
`vertical-align: top` at 73% with a `top-[-6px]` correction, and the dollar sign
split into its own element. This normalises all of them.

Round amounts also lose their `.00`, per the copy style guide ("avoid using cents
when writing a round amount").

Idempotent: safe to re-run.

    python3 tools/normalize-currency.py
    python3 tools/normalize-currency.py --check
"""
from __future__ import annotations

import pathlib
import re
import sys

SCREENS = pathlib.Path("docs/screens")

# Lifting by a fraction of the *parent* em keeps the glyphs on the cap line at any
# figure size, which `vertical-align: super` does not do consistently.
STYLE = """
        /* Hero currency: reduced $ and cents sitting on the cap line, matching the
           SoFi app's stat figures. Row amounts keep full-size cents. */
        .money-sym,
        .money-cents {
            font-size: 52%;
            font-weight: inherit;
            letter-spacing: 0;
            position: relative;
            top: -0.42em;
        }
        .money-sym { margin-right: 0.06em; }
"""

# A figure is "hero" when it carries a display token or any large text size. Gating
# on the text also being a pure currency figure keeps the clock ("9:41") and masked
# card numbers ("•••• 4417") out, even though they use the same display font.
HERO = ("text-balance-display", "text-data-display", "text-headline-md",
        "text-headline-lg", "text-2xl", "text-3xl", "text-4xl", "text-5xl",
        "text-6xl", "text-7xl")
BIG_ARBITRARY = re.compile(r"text-\[(\d+)px\]")


def is_hero(attrs: str) -> bool:
    if any(tok in attrs for tok in HERO):
        return True
    m = BIG_ARBITRARY.search(attrs)
    return bool(m) and int(m.group(1)) >= 24

FIGURE = re.compile(r"^\s*(?P<sign>[-−+]?)\$\s*(?P<int>\d{1,3}(?:,\d{3})*|\d+)(?:\.(?P<cents>\d{2}))?\s*$")


def canonical(sign: str, whole: str, cents: str | None) -> str:
    """Rebuild a figure with the reduced sign and cap-height cents."""
    out = f'{sign}<span class="money-sym">$</span>{whole}'
    # "$300.00" reads as machine output; the style guide wants "$300".
    if cents and cents != "00":
        out += f'<span class="money-cents">.{cents}</span>'
    return out


def rewrite_hero(html: str) -> tuple[str, int]:
    """Two passes: figures that already wrap their cents in a span, then plain-text
    figures. A single regex lets a parent element match first and swallow the child,
    so the nested case has to be handled on its own."""
    count = 0

    def sub(m):
        nonlocal count
        tag, attrs, inner = m.group("tag"), m.group("attrs"), m.group("inner")
        if not is_hero(attrs):
            return m.group(0)
        text = re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", inner))
        fig = FIGURE.match(text)
        if not fig:
            return m.group(0)
        rebuilt = canonical(fig.group("sign"), fig.group("int"), fig.group("cents"))
        if rebuilt == inner.strip():
            return m.group(0)
        count += 1
        return "<%s%s>%s</%s>" % (tag, attrs, rebuilt, tag)

    TAGS = r"(?P<tag>span|div|h1|h2|h3|p)"
    # Nested: inner holds one or more spans (the existing cents markup).
    html = re.sub(
        "<" + TAGS + r'(?P<attrs>[^>]*)>(?P<inner>[^<]*(?:<span[^>]*>[^<]*</span>[^<]*)+)</\1>',
        sub, html)
    # Plain: inner is text only, so no parent can swallow a child figure.
    html = re.sub("<" + TAGS + r'(?P<attrs>[^>]*)>(?P<inner>[^<>]*)</\1>', sub, html)
    return html, count


def rewrite_split_sign(html: str) -> tuple[str, int]:
    """Some screens put the $ in its own element next to the digits."""
    count = 0

    def sub(m: re.Match) -> str:
        nonlocal count
        if not is_hero(m.group("a1")):
            return m.group(0)
        fig = FIGURE.match("$" + m.group("num"))
        if not fig:
            return m.group(0)
        count += 1
        return (f'<span{m.group("a1")}>'
                f'{canonical("", fig.group("int"), fig.group("cents"))}</span>')

    html = re.sub(
        r'<span(?P<a1>[^>]*)>\s*\$\s*</span>\s*'
        r'<span(?P<a2>[^>]*)>\s*(?P<num>[\d,]+(?:\.\d{2})?)\s*</span>',
        sub, html)
    return html, count


def rewrite_row_amounts(html: str) -> tuple[str, int]:
    """Row amounts get full-size cents; drop the shrunken-cents spans."""
    count = 0

    def sub(m: re.Match) -> str:
        nonlocal count
        count += 1
        return m.group("head") + m.group("cents")

    html = re.sub(
        r'(?P<head>\$\s?\d{1,3}(?:,\d{3})*\.)'
        r'<span class="text-\[\d+px\]">(?P<cents>\d{2})</span>',
        sub, html)
    return html, count


def ensure_style(html: str) -> tuple[str, int]:
    if ".money-cents" in html:
        return html, 0
    if "</style>" in html:
        return html.replace("</style>", STYLE + "    </style>", 1), 1
    return html.replace("</head>", f"<style>{STYLE}</style>\n</head>", 1), 1


def main() -> int:
    check = "--check" in sys.argv
    files = sorted(SCREENS.glob("*.html"))
    totals = [0, 0, 0]
    for path in files:
        original = path.read_text(encoding="utf-8")
        html, n_hero = rewrite_hero(original)
        html, n_split = rewrite_split_sign(html)
        html, n_rows = rewrite_row_amounts(html)
        if n_hero or n_split or n_rows:
            html, _ = ensure_style(html)
        totals = [t + n for t, n in zip(totals, (n_hero, n_split, n_rows))]

        bits = []
        if n_hero:
            bits.append(f"{n_hero} hero")
        if n_split:
            bits.append(f"{n_split} split-sign")
        if n_rows:
            bits.append(f"{n_rows} row")
        print(f"  {path.name:<30} {', '.join(bits) or 'consistent'}")

        if not check and html != original:
            path.write_text(html, encoding="utf-8")

    verb = "would normalise" if check else "normalised"
    print(f"\n{verb} {totals[0]} hero figures, {totals[1]} split signs, "
          f"{totals[2]} row amounts across {len(files)} screens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

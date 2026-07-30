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



# The caption under a hero balance ("of $300 this month") and the caption under a
# pocket tile ("$128 left of $300") each came out at a different size, opacity and
# font per screen. Two tiers, one treatment each: 16px at 80% opacity for the hero
# subtitle, 12px body for the tile caption. Colour is left alone — these sit on
# cyan, Buttercup and Ink headers, so each needs its own contrast pairing. `font-
# eyebrow` is dropped from captions: per the brand guidelines the eyebrow style is
# for all-caps labels, not sentence-case captions.
CAPTIONS = [
    # (before, after)
    ("font-body-sm text-body-sm text-surface-container-lowest/80 mt-1",
     "font-body-md text-body-md text-surface-container-lowest opacity-80 mt-1"),
    ("font-body-md text-body-md opacity-70",
     "font-body-md text-body-md opacity-80"),
    ("text-primary-fixed-dim font-body-md text-body-md opacity-90",
     "text-primary-fixed-dim font-body-md text-body-md opacity-80"),
    ("font-body-md text-body-md text-on-primary opacity-90 mb-4",
     "font-body-md text-body-md text-on-primary opacity-80 mb-4"),
    ("font-eyebrow text-[10px] text-outline",
     "font-body-sm text-[12px] text-outline"),
    ("font-body-sm text-body-sm text-outline text-xs mt-1",
     "font-body-sm text-[12px] text-outline mt-1"),
]


def rewrite_captions(html: str) -> tuple[str, int]:
    count = 0
    for before, after in CAPTIONS:
        n = html.count(before)
        if n:
            html = html.replace(before, after)
            count += n
    # A round amount inside a caption keeps its .00 because it is not a standalone
    # figure; the style guide drops it either way.
    html, n = re.subn(r"(\$\d{1,3}(?:,\d{3})*)\.00\b", r"\1", html)
    return html, count + n



# Money figures belong to two tiers: the screen's hero balance at 44px
# (`balance-display`) and a pocket-tile stat at 24px (`headline-md`). Screens 02 and
# 15 came out of a different generation batch using a non-system `data-display` token
# at 28px for the hero and 20px for tiles, so the same figure was a different size
# depending on which screen you were looking at. Screen 07's share amount was set in
# Roboto Mono, which the brand guidelines reserve strictly for tabulated numerals.
TIERS = [
    # Hero balance -> 44px
    ("font-data-display text-data-display text-surface-container-lowest",
     "font-balance-display text-balance-display text-surface-container-lowest"),
    ("font-data-display text-data-display text-on-primary mb-4",
     "font-balance-display text-balance-display text-on-primary mb-4"),
    # Pocket tile stat -> 24px, matching screen 01
    ("font-data-display text-data-display text-on-surface text-xl",
     "font-headline-md text-headline-md text-on-surface"),
    # A single share amount is not a table of figures. text-3xl (30px) is also off
    # the scale; headline-lg is the 32px step.
    ("font-numeric-table text-numeric-table text-3xl font-bold",
     "font-balance-display text-headline-lg font-bold"),
    ("font-balance-display text-3xl font-bold",
     "font-balance-display text-headline-lg font-bold"),
    # The transaction amount is that screen's hero, so it takes the hero tier — and
    # it was set in Roboto Mono at an arbitrary 32px, off both the family and scale.
    ("font-numeric-table text-[32px] leading-[40px] font-medium",
     "font-balance-display text-balance-display"),
]


def rewrite_tiers(html: str) -> tuple[str, int]:
    count = 0
    for before, after in TIERS:
        n = html.count(before)
        if n:
            html = html.replace(before, after)
            count += n
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
        html, n_caps = rewrite_captions(html)
        html, n_tiers = rewrite_tiers(html)
        if n_hero or n_split or n_rows or n_caps or n_tiers:
            html, _ = ensure_style(html)
        totals = [t + n for t, n in zip(totals, (n_hero, n_split, n_rows))]

        bits = []
        if n_hero:
            bits.append(f"{n_hero} hero")
        if n_split:
            bits.append(f"{n_split} split-sign")
        if n_rows:
            bits.append(f"{n_rows} row")
        if n_caps:
            bits.append(f"{n_caps} caption")
        if n_tiers:
            bits.append(f"{n_tiers} tier")
        print(f"  {path.name:<30} {', '.join(bits) or 'consistent'}")

        if not check and html != original:
            path.write_text(html, encoding="utf-8")

    verb = "would normalise" if check else "normalised"
    print(f"\n{verb} {totals[0]} hero figures, {totals[1]} split signs, "
          f"{totals[2]} row amounts across {len(files)} screens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

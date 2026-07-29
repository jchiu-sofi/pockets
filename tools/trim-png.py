#!/usr/bin/env python3
"""Trim uniform trailing rows from a PNG, in place.

Screens are captured at a viewport tall enough that the page never scrolls — a
vertical scrollbar steals ~15px of layout width and silently clips right-aligned
content. That leaves dead space under short screens, which this removes.

Stdlib only (no Pillow on this machine).

    python3 tools/trim-png.py renders/*.png
"""
import pathlib
import struct
import sys
import zlib

PAD = 16  # keep a little breathing room below the last real content


def decode(data: bytes):
    pos, idat = 8, bytearray()
    w = h = ct = None
    while pos < len(data):
        (ln,) = struct.unpack(">I", data[pos:pos + 4])
        typ = data[pos + 4:pos + 8]
        if typ == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", data[pos + 8:pos + 18])
            if bd != 8 or ct not in (2, 6):
                raise ValueError(f"unsupported PNG: depth={bd} colour={ct}")
        elif typ == b"IDAT":
            idat += data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
    bpp = 4 if ct == 6 else 3
    raw = zlib.decompress(bytes(idat))
    stride = w * bpp
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        f = raw[i]; i += 1
        line = bytearray(raw[i:i + stride]); i += stride
        if f:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                if f == 1: line[x] = (line[x] + a) & 255
                elif f == 2: line[x] = (line[x] + b) & 255
                elif f == 3: line[x] = (line[x] + (a + b) // 2) & 255
                elif f == 4:
                    p = a + b - c
                    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                    line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
                else:
                    raise ValueError(f"bad filter {f}")
        prev = line
        rows.append(bytes(line))
    return w, h, bpp, rows


def encode(w: int, h: int, bpp: int, rows) -> bytes:
    def chunk(typ: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + typ + payload
                + struct.pack(">I", zlib.crc32(typ + payload) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6 if bpp == 4 else 2, 0, 0, 0)
    body = b"".join(b"\x00" + r for r in rows)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(body, 9)) + chunk(b"IEND", b""))


def trim(path: pathlib.Path) -> str:
    w, h, bpp, rows = decode(path.read_bytes())
    bg = rows[-1][(w - 1) * bpp:(w - 1) * bpp + bpp]
    uniform = bg * w
    last = h - 1
    while last > 0 and rows[last] == uniform:
        last -= 1
    keep = min(h, last + 1 + PAD)
    if keep >= h:
        return f"{path.name}: nothing to trim ({w}x{h})"
    path.write_bytes(encode(w, keep, bpp, rows[:keep]))
    return f"{path.name}: {h} -> {keep}px"


def thumb(path: pathlib.Path, rows_kept: int) -> str:
    """Write a viewport-height crop into renders/thumbs/ for README use.

    Cropping a correct full-height capture is the only safe way to get a
    one-viewport image: rendering at 844px would make the page scroll, and the
    scrollbar is what clipped the layout in the first place.
    """
    w, h, bpp, rows = decode(path.read_bytes())
    out_dir = path.parent / "thumbs"
    out_dir.mkdir(exist_ok=True)
    keep = min(h, rows_kept)
    (out_dir / path.name).write_bytes(encode(w, keep, bpp, rows[:keep]))
    return f"{path.name}: thumb {w}x{keep}"


def crop_width(path: pathlib.Path, cols: int) -> str:
    """Keep the leftmost `cols` columns, in place.

    Headless Chrome clamps --window-size to a ~500px minimum layout viewport, so
    screens are captured inside an exact-width iframe pinned to the top left and
    the surrounding window is cropped away here.
    """
    w, h, bpp, rows = decode(path.read_bytes())
    if cols >= w:
        return f"{path.name}: no crop needed ({w}x{h})"
    cut = cols * bpp
    path.write_bytes(encode(cols, h, bpp, [r[:cut] for r in rows]))
    return f"{path.name}: {w} -> {cols}px wide"


def main() -> int:
    args = sys.argv[1:]
    rows_kept = cols_kept = None
    if "--thumb" in args:
        i = args.index("--thumb")
        rows_kept = int(args[i + 1])
        del args[i:i + 2]
    if "--crop-width" in args:
        i = args.index("--crop-width")
        cols_kept = int(args[i + 1])
        del args[i:i + 2]
    paths = [pathlib.Path(a) for a in args]
    if not paths:
        print(__doc__)
        return 1
    for p in paths:
        try:
            if cols_kept:
                print("  " + crop_width(p, cols_kept))
            elif rows_kept:
                print("  " + thumb(p, rows_kept))
            else:
                print("  " + trim(p))
        except Exception as e:
            print(f"  {p.name}: skipped ({e})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

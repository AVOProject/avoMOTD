#!/usr/bin/env python3
"""Make a 64x64 server-icon.png from a wide banner without over-zooming.

A banner is ~7:1, so a plain centre square crop shows barely a tenth of it - just
a couple of letters. This finds the logo (the run of columns with the strongest
edge energy through the middle band - text has hard edges, scenery does not),
crops it with a margin, fits that into 64x64 and fills the letterbox with the
banner's own sky/ground colours so it reads as a framed sign rather than a crop.

Usage:
    python make_icon.py <banner.png> <out-icon.png> [zoom]

frac: fraction of the banner width to keep, centred (default 0.55).
      Smaller = more zoomed in on the wordmark; 1.0 = the whole banner.
"""
from __future__ import annotations

import sys

from PIL import Image


def trim_border(img: Image.Image) -> Image.Image:
    px = img.load()
    w, h = img.size

    def near(a, b):
        return all(abs(a[i] - b[i]) < 24 for i in range(3))

    def row_uniform(y):
        c = px[0, y]
        return all(near(px[x, y], c) for x in range(0, w, 11))

    def col_uniform(x, y0, y1):
        c = px[x, y0]
        return all(near(px[x, y], c) for y in range(y0, y1, 11))

    y0, y1, x0, x1 = 0, h, 0, w
    while y0 < y1 - 1 and row_uniform(y0):
        y0 += 1
    while y1 > y0 + 1 and row_uniform(y1 - 1):
        y1 -= 1
    while x0 < x1 - 1 and col_uniform(x0, y0, y1):
        x0 += 1
    while x1 > x0 + 1 and col_uniform(x1 - 1, y0, y1):
        x1 -= 1
    return img.crop((x0, y0, x1, y1))


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def logo_window(b: Image.Image, frac: float) -> tuple[int, int]:
    """Centred window of `frac` of the width.

    Edge-energy detection was tried and rejected: on these banners the scenery
    (barn, animals, windmill) carries more edges than the lettering, so it kept
    selecting the wrong side. These banners always centre the wordmark, so the
    centre is both simpler and more reliable."""
    W, _ = b.size
    half = int(W * frac / 2)
    cx = W // 2
    return max(0, cx - half), min(W, cx + half)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    src_path, out_path = sys.argv[1], sys.argv[2]
    frac = float(sys.argv[3]) if len(sys.argv) > 3 else 0.55

    banner = trim_border(Image.open(src_path).convert("RGB"))
    W, H = banner.size
    x0, x1 = logo_window(banner, min(1.0, frac))
    crop = banner.crop((x0, 0, x1, H))
    cw, ch = crop.size

    scale = min(64 / cw, 64 / ch)
    tw, th = max(1, round(cw * scale)), max(1, round(ch * scale))
    strip = crop.resize((tw, th), Image.LANCZOS)

    # letterbox fill: the banner's own sky above, ground below
    sky = banner.resize((1, 4), Image.LANCZOS).getpixel((0, 0))
    ground = banner.resize((1, 4), Image.LANCZOS).getpixel((0, 3))
    icon = Image.new("RGB", (64, 64))
    ip = icon.load()
    top = (64 - th) // 2
    for y in range(64):
        c = sky if y < top else (ground if y >= top + th else (0, 0, 0))
        for x in range(64):
            ip[x, y] = c
    icon.paste(strip, ((64 - tw) // 2, top))
    # Quantise to 256 colours before saving. The favicon is base64'd into the
    # SAME 32767-char status string as the banner, and a full-colour 64x64 PNG
    # can eat 16k of it - enough to push a full banner over the limit, which
    # makes the whole ping fail ("Can't connect to server"). 256 colours is
    # indistinguishable at 64px and roughly a third of the size.
    icon.quantize(colors=256, method=Image.MEDIANCUT).save(out_path, "PNG", optimize=True)
    print(f"centre crop cols {x0}-{x1} of {W} ({(x1 - x0) / W * 100:.0f}% of width)")
    print(f"crop {cw}x{ch} (aspect {cw / ch:.1f}:1) -> strip {tw}x{th} px inside 64x64")
    import os
    size = os.path.getsize(out_path)
    print(f"wrote {out_path} ({size} bytes, ~{size * 4 // 3} base64 chars in the status packet)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Stitch three pictures - left scene | name sign | right scene - into one
2112x136 banner source for avoMOTD.

    python stitch.py left.png centre.png right.png out.png
    python stitch.py left.png centre.png right.png out.png --crop-c 77 386 1458 610
    python stitch.py L.png C.png R.png out.png --ay-l 0.50 --ay-r 0.55

Why three pictures: the banner has to be 15.5:1 and no image model will draw
that shape - the widest any of them goes is about 2.4:1. Three ordinary 3:2
pictures, each cropped to a horizontal band and laid side by side, get there
without squashing anything. Put the server's name on a sign in the middle one:
the sign's frame hides both joins, which is what makes three separate pictures
read as one.

--crop-c   crop the centre picture first (x0 y0 x1 y1, in its own pixels). Crop
           it tight to the lettering, not to the whole plank: the banner is only
           17 pixels tall, and with the frame included the letters come out ~9px
           and the gap between the two MOTD lines cuts them in half. Tight, they
           fill ~13 of the 17 rows and read cleanly.
--centre-w width of the middle slot. Leave it at 0 and it is worked out from the
           centre picture's own aspect, so the sign is never stretched.
--ay-*     vertical anchor (0 top, 1 bottom) of the band taken from each picture
           when it is taller than its slot. Aim it at the action.

Also writes <out>_preview.png: the banner as the client will draw it - scaled to
264x17, split into the two 8-pixel lines, with the white shadow copy one pixel
down-right that shadow_color:-1 produces - blown up 4x. Look at that one, not the
full-size picture, before spending MineSkin quota; the full-size one always
looks fine.
"""
import argparse

from PIL import Image, ImageDraw

W, H = 2112, 136


def crop_fill(img, w, h, anchor_y):
    """Cut img to w:h without distorting it, then scale it to exactly w x h."""
    img = img.convert("RGB")
    sw, sh = img.size
    target = w / h
    if sw / sh > target:            # wider than the slot: trim the sides evenly
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        box = (x0, 0, x0 + nw, sh)
    else:                           # taller than the slot: take a band at anchor_y
        nh = int(sw / target)
        y0 = int((sh - nh) * anchor_y)
        box = (0, y0, sw, y0 + nh)
    return img.crop(box).resize((w, h), Image.LANCZOS)


def seam_shadow(canvas, x, width=18, strength=150):
    """A soft dark band over a join, so it reads as the edge of the sign."""
    shade = Image.new("L", (width * 2, H), 0)
    draw = ImageDraw.Draw(shade)
    for i in range(width * 2):
        draw.line([(i, 0), (i, H)], fill=max(0, int(strength * (1 - abs(i - width) / width))))
    canvas.paste(Image.new("RGB", (width * 2, H), (8, 10, 6)), (x - width, 0), shade)


def preview(banner):
    """What the server list will actually show, at 4x."""
    small = banner.resize((264, 17), Image.LANCZOS)
    top, bottom = small.crop((0, 0, 264, 8)), small.crop((0, 9, 264, 17))
    out = Image.new("RGB", (266, 19), (16, 16, 20))
    for part, y in ((top, 0), (bottom, 10)):
        out.paste(part, (1, y + 1))   # the shadow copy shadow_color:-1 draws
        out.paste(part, (0, y))
    return out.resize((266 * 4, 19 * 4), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser(description="left | sign | right -> 2112x136 banner source")
    ap.add_argument("left")
    ap.add_argument("centre")
    ap.add_argument("right")
    ap.add_argument("out")
    ap.add_argument("--crop-c", type=int, nargs=4, metavar=("X0", "Y0", "X1", "Y1"),
                    help="crop the centre picture first - tight to the lettering")
    ap.add_argument("--centre-w", type=int, default=0,
                    help="middle slot width; 0 = from the centre picture's aspect")
    ap.add_argument("--ay-l", type=float, default=0.55)
    ap.add_argument("--ay-c", type=float, default=0.5)
    ap.add_argument("--ay-r", type=float, default=0.55)
    a = ap.parse_args()

    centre = Image.open(a.centre).convert("RGB")
    if a.crop_c:
        centre = centre.crop(tuple(a.crop_c))
    centre_w = a.centre_w or round(H * centre.width / centre.height)
    centre_w = max(64, min(W - 256, centre_w))

    left_w = (W - centre_w) // 2
    right_w = W - centre_w - left_w
    canvas = Image.new("RGB", (W, H))
    canvas.paste(crop_fill(Image.open(a.left), left_w, H, a.ay_l), (0, 0))
    canvas.paste(crop_fill(centre, centre_w, H, a.ay_c), (left_w, 0))
    canvas.paste(crop_fill(Image.open(a.right), right_w, H, a.ay_r), (left_w + centre_w, 0))
    seam_shadow(canvas, left_w)
    seam_shadow(canvas, left_w + centre_w)

    canvas.save(a.out)
    preview_path = a.out.rsplit(".", 1)[0] + "_preview.png"
    preview(canvas).save(preview_path)
    print(f"wrote {a.out} {canvas.size}  (left {left_w} | centre {centre_w} | right {right_w})")
    print(f"      {preview_path}  <- check this one before spending MineSkin quota")


if __name__ == "__main__":
    main()

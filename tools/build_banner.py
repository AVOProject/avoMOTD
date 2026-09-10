#!/usr/bin/env python3
"""Build avoMOTD's full 1.21.9 object-component banner from a PNG.

A 264x16 image is split into 66 tiles of 8x8. Each unique tile is baked into a
Minecraft skin (the tile in the head's face UV) and uploaded to MineSkin to get a
permanent textures.minecraft.net URL. The banner MOTD is then 66 "object"/player
face components (33 wide x 2 rows), each carrying a minimal unsigned texture value
(just that URL, ~180 chars) - under the 32767-char status-string limit, and with
no dependency on which MineSkin account uploaded it (profile-id lookups do NOT
render on the client; embedding the URL does).

Usage:
    python build_banner.py <image.png> <mineskin-key> <out-banner.json>

The output path is required on purpose - it is per server
(<server>/plugins/avoMOTD/banner.json), and a wrong default silently writes the
banner into the wrong server.
Caches tile-hash -> profile id in tools/banner-cache.json so re-runs are instant
and unchanged tiles are never re-uploaded.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import subprocess
import sys
import time

from PIL import Image

COLS, ROWS = 33, 2          # 264x16 / 8 = 33 x 2 tiles
TILE = 8

# How hard to fade each row next to the line break: {rows from the break: brightness}.
# See fade_seam(). Empty dict = leave the artwork alone.
SEAM_FADE = {1: 0.12, 2: 0.38, 3: 0.70}
MINESKIN = "https://api.mineskin.org/v2/generate"
DELAY = 3.4                 # MineSkin per-key delay is ~3s; stay just above it

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "banner-cache.json")   # tile-hash -> texture URL, shared across servers


def trim_border(img: Image.Image) -> Image.Image:
    """Crop away a uniform (white/transparent) margin, like the plugin does."""
    px = img.convert("RGBA").load()
    w, h = img.size

    def near(a, b):
        if a[3] < 40 and b[3] < 40:
            return True
        return all(abs(a[i] - b[i]) < 24 for i in range(3))

    def row_uniform(y):
        c = px[0, y]
        return all(near(px[x, y], c) for x in range(0, w, 7))

    def col_uniform(x, y0, y1):
        c = px[x, y0]
        return all(near(px[x, y], c) for y in range(y0, y1, 7))

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


def fade_seam(banner: Image.Image) -> None:
    """Darken the rows either side of the line break, in place.

    The client draws the two MOTD lines ~2px further apart than a face sprite is
    tall, and that strip is the server-list background - no text component can
    paint into it, because it belongs to neither line. Against bright artwork it
    reads as a black slash through the picture.

    So do what the banners that look seamless do: bring the picture down to meet
    the gap. Fading the rows next to the break turns one hard black line into a
    short shadow, which reads as a deliberate divider rather than damage. Set
    SEAM_FADE to {} to keep the artwork untouched.
    """
    if not SEAM_FADE:
        return
    px = banner.load()
    width = COLS * TILE
    for distance, amount in SEAM_FADE.items():
        # distance 1 = the rows touching the break; the sampled row TILE is the
        # one hidden inside the gap and is never drawn.
        for y in (TILE - distance, TILE + distance):
            if not 0 <= y < ROWS * TILE + 1:
                continue
            for x in range(width):
                r, g, b, a = px[x, y]
                px[x, y] = (int(r * amount), int(g * amount), int(b * amount), a)


def uuid_to_ints(hex32: str) -> list[int]:
    b = bytes.fromhex(hex32)
    return [int.from_bytes(b[i:i + 4], "big", signed=True) for i in range(0, 16, 4)]


def upload_tile(tile: Image.Image, key: str) -> str:
    """Bake the 8x8 tile into a skin face, upload, return the texture URL.

    Respects MineSkin's rate limit: on a throttled response it waits the time the
    API reports and retries, so the whole 66-tile run just paces itself."""
    skin = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    skin.paste(tile, (8, 8))                       # face UV
    skin.paste(tile, (40, 8))                      # hat UV too, harmless
    tmp = os.path.join(HERE, "_tile.png")
    skin.save(tmp)

    for attempt in range(40):
        out = subprocess.run(
            ["curl", "-s", "-m", "90", "-X", "POST", MINESKIN,
             "-H", "Authorization: Bearer " + key, "-H", "User-Agent: avoMOTD/1.0",
             "-F", "file=@" + tmp.replace("\\", "/"),
             "-F", "variant=classic", "-F", "visibility=unlisted"],
            capture_output=True, text=True)
        try:
            data = json.loads(out.stdout)
        except json.JSONDecodeError:
            time.sleep(5)
            continue
        if data.get("success"):
            value = data["skin"]["texture"]["data"]["value"]
            # Permanent textures.minecraft.net URL - referenced directly, so the
            # banner never depends on which MineSkin account uploaded it.
            return json.loads(base64.b64decode(value))["textures"]["SKIN"]["url"]
        # throttled -> wait exactly as long as the API says. The hourly window
        # (100/key) is the one that bites on a 66-tile run; its reset is an epoch
        # second, so honour that rather than retrying on a short timer.
        wait = 5.0
        rl = data.get("rateLimit") or {}
        lim = rl.get("limit") or {}
        hour = lim.get("hour") or {}
        minute = lim.get("minute") or {}
        nxt = rl.get("next") or {}
        if hour.get("remaining") == 0 and hour.get("reset"):
            wait = max(wait, hour["reset"] - time.time() + 5)
        elif minute.get("remaining") == 0 and minute.get("reset"):
            wait = max(wait, minute["reset"] - time.time() + 2)
        elif isinstance(nxt.get("relative"), (int, float)):
            wait = max(wait, nxt["relative"] + 1)
        elif rl.get("delay", {}).get("seconds"):
            wait = max(wait, rl["delay"]["seconds"] + 1)
        wait = min(wait, 3900)
        print(f"    throttled, waiting {wait:.0f}s (attempt {attempt + 1})", flush=True)
        time.sleep(wait)
    raise RuntimeError("MineSkin: gave up after retries: " + out.stdout[:200])


def main() -> int:
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    image_path, key = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else \
        r"E:\code\Plugin_avo\Server\Farm\plugins\avoMOTD\banner.json"

    cache = {}
    if os.path.isfile(CACHE):
        cache = json.load(open(CACHE))

    # The two MOTD lines are 9px apart but a face sprite is only 8px tall, so one
    # source row is hidden in the gap between them. Sample 17 rows and skip row 8
    # -> the picture keeps its true proportions and the seam lands on a row that
    # was never meant to be seen (the dark line itself cannot be removed).
    banner = trim_border(Image.open(image_path).convert("RGBA")).resize(
        (COLS * TILE, ROWS * TILE + 1), Image.LANCZOS)
    fade_seam(banner)

    faces, uploads, reused = [], 0, 0
    for row in range(ROWS):
        if row:
            faces.append("\n")
        for col in range(COLS):
            top = row * (TILE + 1)          # row 0 -> y0..8, row 1 -> y9..17
            tile = banner.crop((col * TILE, top, col * TILE + TILE, top + TILE))
            h = hashlib.sha1(tile.tobytes()).hexdigest()
            entry = cache.get(h)
            if isinstance(entry, dict) and entry.get("url"):
                url = entry["url"]
                reused += 1
            else:
                url = upload_tile(tile, key)
                cache[h] = {"url": url}
                json.dump(cache, open(CACHE, "w"))     # persist after each upload
                uploads += 1
                print(f"  tile {row},{col} uploaded ({uploads})")
                time.sleep(DELAY)
            # Minimal unsigned texture value: the client only needs the skin URL.
            # ~180 chars/face keeps 66 faces well under the 32767-char status limit.
            value = base64.b64encode(json.dumps(
                {"textures": {"SKIN": {"url": url}}}, separators=(",", ":")).encode()).decode()
            # Compact on purpose: the whole status response (description + favicon)
            # must fit 32767 chars. No "name", no "hat" (the tile is baked into the
            # hat UV too, so the default hat layer draws the same pixels).
            faces.append({"object": "player",
                          "player": {"properties": [{"name": "textures", "value": value}]}})

    # white at the root: sprites are tinted by the inherited text colour
    motd = {"text": "", "color": "white", "extra": faces}
    js = json.dumps(motd, separators=(",", ":"))
    open(out_path, "w", encoding="utf-8").write(js)
    size = len(js)
    print(f"banner.json written: {out_path}")
    print(f"tiles={COLS * ROWS} uploaded={uploads} reused={reused} json_size={size} (limit 32767)")
    if size > 32767:
        print("WARNING: over the 32767 status-string limit - reduce or dedupe tiles")
    return 0


if __name__ == "__main__":
    sys.exit(main())

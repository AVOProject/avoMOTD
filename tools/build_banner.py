#!/usr/bin/env python3
"""Build avoMOTD's full 1.21.9 object-component banner from a PNG.

A 264x16 image is split into 66 tiles of 8x8. Each unique tile is baked into a
Minecraft skin (the tile in the head's face UV) and uploaded to MineSkin, which
returns a Mojang-resolvable profile. The banner MOTD is then 66 "object"/player
face components (33 wide x 2 rows) referenced by profile id (int-array) - small
enough to stay under the 32767-char status-string limit, unlike embedding the
texture per face.

Usage:
    python build_banner.py <image.png> <mineskin-key> [out.json]

Writes the banner JSON (default: plugins/avoMOTD/banner.json under the server).
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
MINESKIN = "https://api.mineskin.org/v2/generate"
DELAY = 3.4                 # MineSkin per-key delay is ~3s; stay just above it

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "banner-cache.json")


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


def uuid_to_ints(hex32: str) -> list[int]:
    b = bytes.fromhex(hex32)
    return [int.from_bytes(b[i:i + 4], "big", signed=True) for i in range(0, 16, 4)]


def upload_tile(tile: Image.Image, key: str) -> list[int]:
    """Bake the 8x8 tile into a skin face, upload, return the profile id ints.

    Respects MineSkin's rate limit: on a throttled response it waits the time the
    API reports and retries, so the whole 66-tile run just paces itself."""
    skin = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    skin.paste(tile, (8, 8))                       # face UV
    skin.paste(tile, (40, 8))                      # hat UV too, harmless
    tmp = os.path.join(HERE, "_tile.png")
    skin.save(tmp)

    for attempt in range(12):
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
            profile_id = json.loads(base64.b64decode(value))["profileId"]
            return uuid_to_ints(profile_id)
        # throttled or error -> wait what the API tells us, then retry
        wait = 5.0
        rl = data.get("rateLimit") or {}
        nxt = rl.get("next") or {}
        if isinstance(nxt.get("relative"), (int, float)):
            wait = max(wait, nxt["relative"] + 1)
        elif rl.get("delay", {}).get("seconds"):
            wait = max(wait, rl["delay"]["seconds"] + 1)
        print(f"    throttled, waiting {wait:.0f}s (attempt {attempt + 1})")
        time.sleep(wait)
    raise RuntimeError("MineSkin: gave up after retries: " + out.stdout[:200])


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    image_path, key = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else \
        r"E:\code\Plugin_avo\Server\Farm\plugins\avoMOTD\banner.json"

    cache = {}
    if os.path.isfile(CACHE):
        cache = json.load(open(CACHE))

    banner = trim_border(Image.open(image_path).convert("RGBA")).resize(
        (COLS * TILE, ROWS * TILE), Image.LANCZOS)

    faces, uploads, reused = [], 0, 0
    for row in range(ROWS):
        if row:
            faces.append("\n")
        for col in range(COLS):
            tile = banner.crop((col * TILE, row * TILE, col * TILE + TILE, row * TILE + TILE))
            h = hashlib.sha1(tile.tobytes()).hexdigest()
            if h in cache:
                ids = cache[h]
                reused += 1
            else:
                ids = upload_tile(tile, key)
                cache[h] = ids
                json.dump(cache, open(CACHE, "w"))     # persist after each upload
                uploads += 1
                print(f"  tile {row},{col} uploaded ({uploads})")
                time.sleep(DELAY)
            faces.append({"type": "object", "object": "player",
                          "player": {"name": "t", "id": ids}, "hat": False})

    motd = {"text": "", "extra": faces}
    open(out_path, "w", encoding="utf-8").write(json.dumps(motd))
    size = len(json.dumps(motd))
    print(f"banner.json written: {out_path}")
    print(f"tiles={COLS * ROWS} uploaded={uploads} reused={reused} json_size={size} (limit 32767)")
    if size > 32767:
        print("WARNING: over the 32767 status-string limit - reduce or dedupe tiles")
    return 0


if __name__ == "__main__":
    sys.exit(main())

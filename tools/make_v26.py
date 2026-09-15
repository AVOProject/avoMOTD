#!/usr/bin/env python3
"""Derive banner-26.json (26.x player-sprite format) from an existing banner.json.

26.x reworked the chat/MOTD player sprite: the old properties-only profile now
parses as an unresolved "Partial" profile and renders as "[unknown player head]".
Giving each face a full profile - a stable unique id + a name alongside the same
textures property - lets the 26.x client resolve it and download the skin URL.

No re-upload: it reuses the textures.minecraft.net URLs already baked into
banner.json. Run after build_banner.py, then deploy banner-26.json next to
banner.json and /avomotd reload.

  python tools/make_v26.py plugins/avoMOTD/banner.json plugins/avoMOTD/banner-26.json
"""
import hashlib
import json
import sys
import uuid


def face_id(value: str) -> str:
    # Deterministic, unique-per-tile UUID from the texture value, so identical
    # tiles share one id (and the client caches one skin) while different tiles
    # never collide in the profile/skin cache.
    return str(uuid.UUID(bytes=hashlib.md5(value.encode()).digest()))


def convert(src: str, dst: str) -> int:
    motd = json.load(open(src, encoding="utf-8"))
    faces = motd.get("extra", [])
    n = 0
    for i, face in enumerate(faces):
        if not isinstance(face, dict):
            continue   # the "\n" line-break string between the two rows
        player = face.get("player")
        if not isinstance(player, dict):
            continue
        props = player.get("properties")
        value = None
        if isinstance(props, list) and props and isinstance(props[0], dict):
            value = props[0].get("value")
        if not value:
            continue
        # Full resolvable profile: id + name + the same textures property.
        player["id"] = face_id(value)
        player["name"] = "a%d" % i          # <= 16 chars, unique enough per face
        n += 1
    js = json.dumps(motd, separators=(",", ":"))
    open(dst, "w", encoding="utf-8").write(js)
    print("banner-26.json written: %s  faces=%d  size=%d (limit 32767)" % (dst, n, len(js)))
    if len(js) > 32767:
        print("WARNING: over the 32767 status-string limit - the id+name pushed it over")
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: make_v26.py <banner.json> <banner-26.json>")
        sys.exit(2)
    sys.exit(convert(sys.argv[1], sys.argv[2]))

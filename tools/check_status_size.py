#!/usr/bin/env python3
"""Check how close a server's status response is to the 32767-char limit.

The server-list ping puts the MOTD *and* the base64 favicon into one string that
Minecraft caps at 32767 characters. Go over and the server cannot encode the
packet at all - the client just shows "Can't connect to server". A full 66-tile
banner (~17k) plus a full-colour 64x64 icon (~16k) is already over, so check
after changing either.

Usage:
    python check_status_size.py [host] [port]      (default 127.0.0.1 25565)
"""
from __future__ import annotations

import json
import socket
import struct
import sys

LIMIT = 32767


def _varint(n: int) -> bytes:
    out = b""
    while True:
        b = n & 0x7F
        n >>= 7
        out += bytes((b | (0x80 if n else 0),))
        if not n:
            return out


def _read_varint(sock: socket.socket) -> int:
    n = shift = 0
    while True:
        b = sock.recv(1)[0]
        n |= (b & 0x7F) << shift
        if not b & 0x80:
            return n
        shift += 7


def ping(host: str, port: int) -> dict:
    with socket.create_connection((host, port), timeout=8) as s:
        handshake = b"\x00" + _varint(767) + _varint(len(host)) + host.encode() \
            + struct.pack(">H", port) + b"\x01"
        s.sendall(_varint(len(handshake)) + handshake)
        s.sendall(_varint(1) + b"\x00")
        _read_varint(s)            # packet length
        _read_varint(s)            # packet id
        length = _read_varint(s)
        buf = b""
        while len(buf) < length:
            buf += s.recv(length - len(buf))
    return {"raw_len": length, "json": json.loads(buf.decode("utf-8"))}


def main() -> int:
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 25565

    try:
        result = ping(host, port)
    except OSError as exc:
        print(f"could not ping {host}:{port} - {exc}")
        return 1

    data = result["json"]
    total = result["raw_len"]
    favicon = len(data.get("favicon", "") or "")
    description = len(json.dumps(data.get("description", ""), separators=(",", ":")))
    faces = json.dumps(data.get("description", "")).count('"player"')

    headroom = LIMIT - total
    pct = total / LIMIT * 100
    print(f"{host}:{port}")
    print(f"  mode        : {'full banner (' + str(faces) + ' faces)' if faces else '2px strip / plain'}")
    print(f"  description : {description:>6} chars")
    print(f"  favicon     : {favicon:>6} chars")
    print(f"  TOTAL       : {total:>6} / {LIMIT}  ({pct:.0f}%)")
    print(f"  headroom    : {headroom:>6} chars")

    if headroom < 0:
        print("  STATUS      : OVER THE LIMIT - the ping will fail for clients")
        return 2
    if headroom < 2000:
        print("  STATUS      : TIGHT - shrink the icon (fewer colours) before adding anything")
        return 0
    print("  STATUS      : ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())

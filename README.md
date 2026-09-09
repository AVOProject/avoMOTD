# avoMOTD 🖼️

Drop-in **pixel-art server-list MOTD** for **Paper 1.21.x**. Point it at a PNG and
it renders the image as your two-line server-list banner — or falls back to a
built-in farm scene. Reusable across every server.

> © 2026 **AVOX2** — proprietary, All Rights Reserved. See [LICENSE](LICENSE).

---

## The one thing to understand first

The multiplayer **server-list ping is only two text lines tall**, and a text
component has **no background colour**. So the banner is rendered as a **2-row
grid of full-block pixels** (`█`), one RGB each — i.e. the picture is **exactly
2 pixels tall**, however big your PNG is.

- A wide image becomes a **colourful horizon / scene strip**. 
- A readable logo or small sprites **cannot survive at 2px** — bake those into the
  **64×64 `server-icon.png`** instead (that one is a real image).

avoMOTD trims uniform margins off your PNG and box-averages it down to `width × 2`.

---

## Install

1. Drop `avoMOTD-<ver>.jar` into `plugins/`.
2. Start once → `plugins/avoMOTD/config.yml` is created.
3. (Optional) put your banner at `plugins/avoMOTD/motd.png`.
4. `/avomotd reload` (needs no restart) or reload the server.

Needs **Paper** (uses `PaperServerListPingEvent`). Folia-safe (the handler builds
text only). PlugMan-reloadable.

## config.yml

```yaml
enabled: true          # take over the server-list MOTD
image: motd.png        # PNG in plugins/avoMOTD/ ; blank/missing -> built-in scene
stamp-name: false      # overlay a 2-row block-font logo on top
name: avoMOTD          # ...this name, when stamp-name is true
width: 42              # block columns (≈46 is the safe max before the list clips)
icon: icon.png         # optional 64x64 PNG favicon (plugins/avoMOTD/); blank = leave server-icon.png
max-players: 0         # "/ N" after the online count; 0 = keep the server's
```

Change the PNG or any value, then `/avomotd reload`.

## What renders

- **image present** → your PNG, margin-trimmed, averaged to `width × 2`.
- **no image** → a built-in farm scene (sky/sun/clouds/tree tops over
  wheat/field/pond/soil).
- **stamp-name: true** → a chunky 2-row block-font name laid over either of the
  above (useful on a plain scene; at 2px it is deliberately blocky).

## Command

| Command | |
|---|---|
| `/avomotd reload` (alias `/amotd`) | re-read `config.yml` + the PNG, rebuild the banner. Permission `avomotd.admin` (op). |

## Full 16px pixel-art banner (advanced)

avoMOTD can also emit the **full 1.21.9 face-tile banner** (like the "ImageMOTD"
servers): a 264x16 image split into **66 tiles of 8x8**, each baked into a
Minecraft skin and shown in the MOTD as a 1.21.9 `object`/player-face component
(33 wide x 2 rows). Faces are referenced by **profile id** (not embedded), which
keeps the status response under the 32767-char limit; 1.21.9-1.21.11 clients
resolve and render them.

This is done entirely in-plugin (no ImageMOTD, no ProtocolLib): a Netty handler
added via Paper's internal `ChannelInitializeListenerHolder` rewrites the outbound
status packet, parsing our raw JSON through Mojang's own component codec (which
Adventure's serializer cannot emit).

**How to enable it**

1. Get a free MineSkin API key at https://account.mineskin.org/keys .
2. Generate the banner (uploads 66 skin tiles, cached):
   ```
   python tools/build_banner.py your-banner.png <mineskin-key>
   ```
   -> writes `plugins/avoMOTD/banner.json`.
3. `/avomotd reload`. Present `banner.json` -> full banner; remove it -> the 2px strip.

**Two things that make or break it** (both handled by `build_banner.py`):
- Reference the tile by its **permanent `textures.minecraft.net` URL** embedded as
  an unsigned texture value. A profile *id* lookup does **not** render — the client
  will not resolve the MineSkin account behind it.
- Put **`"color":"white"`** on the root component. Face sprites are tinted by the
  inherited text colour, so without it the whole banner renders at ~50% brightness.
- Keep it compact: description + favicon share one **32767-char** status string.
  No per-face `name`/`hat`, colour only at the root (66 tiles ≈ 17 KB).

**Caveats (by design of the MC feature):**
- **Version-specific.** It compiles against the Mojang-mapped Paper server jar
  (`pom.xml` `paper.jar`/`paper.libs` - point them at your server) and touches the
  NMS status packet, so a major MC update can require a rebuild.
- Clients older than 1.21.9 fall back to the 2px block strip.
- At 264x16 a detailed image reads as a colourful mosaic - design the source for
  low resolution.

## Build

```
mvn clean package        # target/avoMOTD-1.0.0.jar
```

Java 21 + Maven. The base plugin (2px strip + favicon) needs only `paper-api`;
the full-banner classes additionally need the Mojang-mapped server jar (see the
`paper.jar` / `paper.libs` properties in `pom.xml`).

---

Part of the [AVOProject](https://github.com/AVOProject) server toolkit.

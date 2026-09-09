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

## Build

```
mvn clean package        # target/avoMOTD-1.0.0.jar
```

Java 21 + Maven, `paper-api` provided. No shaded dependencies.

---

Part of the [AVOProject](https://github.com/AVOProject) server toolkit.

# Locked baseline — simulator-ready headless stack

**Tag:** `sim-ready-2026-06-07`
**Date:** 2026-06-07

This tag marks the **Grid (Floor Is Lava)** headless migration at simulator parity: session marathon (5-min timer, persistent score/life across levels), overlap priority (green > red/deduct > blue/orange), true 2-player scoring on `----`-tier `.ledb` levels, and a 16×26 square floor rendered in-browser via `led_display`.

**Level tiers** (`games/source/`):

| Tier folder | Levels | Format | Notes |
|---|---|---|---|
| `-` | 10 | `.led` | 1P, easy |
| `--` | 15 | `.led` | 1P, medium |
| `---` | 14 | `.led` | 1P, hard |
| `----` | 13 | `.ledb` | 2P — real two-player levels |

**Scoring policy:** no-divide. `scode_divide_person` and `scode_divide_time` are both `False` by default (see `docs/SETTINGS.md`, `api/game_manager.py` DEFAULT_SETTINGS) — raw scores are NOT divided by player count or elapsed time; each player's score stands on its own.

**Grid:** 16 rows × 26 cols (the largest floor of the 5 games — 416 tiles).

| Service | Port |
|---------|------|
| UI | 5176 |
| API | 8003 (see `ONSITE.md`; `api/config.py` default differs — confirm at deploy time) |
| ws_bridge | 8769 |

**Hardware status:** Hardware driver code exists (`_hw_init()`, `USE_SERIAL_HD` env gate, `led.led_control` serial calls in `api/game_manager.py`) but as of this tag it has **never been run against real physical hardware** — it was implemented by analogy from led-hoops/led-climb's real-hardware findings, not verified on a floor of its own. Treat any onsite hardware session for this game as a first-time validation, not a re-test. See `HARDWARE_VALIDATION.md` for the validation plan and checklist.

**Canonical docs:** [`ONSITE.md`](./ONSITE.md) (single-machine setup), [`HARDWARE_VALIDATION.md`](./HARDWARE_VALIDATION.md) (hardware test plan/history). Note: `docs/` in this repo is a stale copy-paste from the Climb migration (its own `docs/README.md` is titled "Climb — Documentation Index") — not Grid-specific; treat it as unreliable for this game until re-audited.

**Checkout this baseline:**
```bash
git checkout sim-ready-2026-06-07
```

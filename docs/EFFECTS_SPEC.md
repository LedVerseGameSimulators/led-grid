# LED Grid (Floor is Lava) — effects spec

Audio, countdown, and LED floor behavior for **LED Grid / Floor is Lava**.

Global rules: [activerse_final_changes/docs/game-effects/GLOBAL_RULES.md](../../docs/game-effects/GLOBAL_RULES.md)

Matrix reference: [GRID_MATRICES.md](../../docs/game-effects/GRID_MATRICES.md)

---

## Floor layout (16 × 26)

| Dimension | Value |
|-----------|--------|
| **Grid size** | **16 rows × 26 columns** |
| **Total LEDs** | **416** |
| **Indexing** | Row **0** = top, col **0** = left → row **15**, col **25** bottom-right |
| **Usable area** | **Full 16×26** — all cells |

### Color legend

| Color | Meaning |
|-------|---------|
| **Green** | Countdown digits (3, 2, 1) |
| **Blue** | Level clear / pass |
| **Red** | Level fail |
| **Off** | LEDs off (background) |

### Effects flow diagram

![Grid effects flows](./assets/grid-effects-flows.png)

---

## Audio assets

| Asset | File / source |
|-------|---------------|
| **BGM** | *Bye Bye Bye* (NSync) — level play only |
| **Positive score SFX** | Shared positive MP3 (cross-game) |
| **Negative score SFX** | Shared negative MP3 (cross-game) |
| **Countdown** | Tick/noise during 3-2-1; **no BGM** |
| **Level transition** | Short stinger ~2–3 s (asset TBD / stock OK) |

---

## Countdown (every level start)

Runs before **every level** — first level of the session, after level clear,
and after level fail restart. **Not** repeated when the session has ended.

Tick/noise audio; no BGM. Each digit is **green**, **centered horizontally
and vertically** on the full 16×26 floor.

| Step | Duration | LED pattern |
|------|----------|-------------|
| **3** | ~0.8 s | Green **"3"** centered on floor |
| **2** | ~0.8 s | Green **"2"** centered on floor |
| **1** | ~0.8 s | Green **"1"** centered on floor |
| **Start** | — | Digit clears → level play begins (BGM on) |

> Grid floor countdown is **3-2-1** only (no **GO** glyph on the floor).
> The UI may still show **GO** on screen — keep UI and floor in sync on timing.

Timings are suggestions — tune to show pace.

---

## Level clear

**All 416 LEDs → solid blue.**

1. Hold clear pattern ~2–3 s with transition stinger (not BGM)
2. **Countdown** (3-2-1 sequence above)
3. **Next level** play begins

If more levels remain: clear → stinger → countdown → next level play.

---

## Level fail (all lives lost, >10 s session time left)

**All 416 LEDs → solid red.**

Triggered when **all lives are lost** while more than **10 s** remains on the session timer.

1. Hold fail pattern ~2–3 s with transition stinger (not BGM)
2. **Countdown** (3-2-1 sequence above)
3. **Same level** restart play begins (HP refilled after countdown)

---

## Session end (no countdown)

Same LED treatment as **level clear** (full floor **blue** via `level_clear.led`).

Applies when **any** of:

- Session **timer expires** mid-level
- **All lives lost** with **≤10 s** session time remaining
- **Last level cleared** (marathon sequence exhausted)

Sequence:

1. Hold clear pattern ~2–3 s with transition stinger (not BGM)
2. All LEDs **black / off**
3. **No countdown** — session is over

---

## Effect files (locked)

Per [LOCKED_DECISIONS.md](../../docs/game-effects/LOCKED_DECISIONS.md), exactly three archives under `games/source/effects/`:

| File | Purpose |
|------|---------|
| `countdown.led` | Green 3-2-1 centered digits (~0.8 s each); **no GO glyph on floor** |
| `level_clear.led` | Solid blue full floor |
| `level_fail.led` | Solid red full floor |

Shared transition audio: `games/audio/transition_stinger.mp3` (clear **and** fail).

---

## Reference media

Capture and timing reference: **`~/Downloads/Floor is lava/`**

Use for LED pattern design only — not frontend video playback.

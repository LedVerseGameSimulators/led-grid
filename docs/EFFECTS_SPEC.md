# LED Grid (Floor is Lava) — effects spec

Audio, countdown, and LED behavior for **LED Grid / Floor is Lava**.

Global rules: [activerse_final_changes/docs/game-effects/GLOBAL_RULES.md](../../docs/game-effects/GLOBAL_RULES.md)

Matrix reference: [GRID_MATRICES.md](../../docs/game-effects/GRID_MATRICES.md)

---

## Grid layout (effects design)

| Dimension | Value |
|-----------|--------|
| **Effects matrix** | **16 rows × 26 columns** |
| **Usable area** | **Full 16×26** — all cells for pattern design |

> Countdown, level-clear, and level-fail patterns TBD (same workflow as Hoops /
> Laser / Climb).

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
and after level fail restart.

Tick/noise audio; no BGM. LED pattern TBD.

| Step | LED pattern |
|------|-------------|
| **3** | TBD |
| **2** | TBD |
| **1** | TBD |
| **GO** | Level play begins |

UI countdown and floor LEDs stay in sync.

---

## Level clear

1. Level-clear LED pattern TBD
2. ~2–3 s transition with stinger SFX (not BGM)
3. **Countdown** (3-2-1-GO)
4. **Next level** play begins

---

## Level fail

Triggered when **all lives are lost**.

1. Level-fail LED pattern TBD
2. ~2–3 s transition with stinger SFX (not BGM)
3. **Countdown** (3-2-1-GO)
4. **Same level** restart play begins

---

## Timer expire

Same LED treatment as **level clear**.

If the timer expires on the **final level** and the session ends → all LEDs
**black / off** after the clear transition (no further countdown).

---

## Reference media

Capture and timing reference: **`~/Downloads/Floor is lava/`**

Use for LED pattern design only — not frontend video playback.

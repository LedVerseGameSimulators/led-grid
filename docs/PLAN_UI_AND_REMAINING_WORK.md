# Grid (Floor Is Lava) — UI redesign + remaining work

**Date:** 2026-09-16  
**Repo:** `led-grid`  
**Parent:** `docs/PLAN_FE_REDESIGN_AND_WORK_INDEX.md`

---

## Locked FE decisions

| Topic | Decision |
|-------|----------|
| Journey | **Mode → Settings\* → Login → Play** (*Tournament skips Settings) |
| Modes | **Quick Play** / **Team Battle** / **Tournament** |
| Levels | QP + TB: **20 + 20** placeholders, Medium; Tournament: existing **~10**, **no level select** |
| Login | **Always** — RFID **or** play without RFID → **random names**; **no** name-typing form |
| Tournament names | UI **1, 2, 3…** on HUD + results/leaderboards (never file names) |
| Orientation | **Landscape only** |
| Video | **One** bg loop per game (reuse across Mode / Login / Results) |
| How-to-play | **We write** short copy; client can edit later |
| Countdown | **Both** — TV overlay on play **and** floor `countdown.led` |
| Screen order | **Locked = today’s order** (mock Login→Setup→Countdown is visual ref only) |

---

## Implementation status

- [x] Decisions locked (2026-09-16)
- [ ] **After Hex FE shell** is the template — apply same shell here
- [ ] Wire modes + 20+20 placeholders + Tournament skip Settings
- [ ] Login: RFID path + guest random names
- [ ] Copy `grid_background.mp4` → `frontend/public/media/` + wire bg
- [ ] Restyle Play HUD + Results; Tournament labels 1, 2, 3…

---

## Score/RFID labels

Hex-style contract (logical names for RFID / LB):

- `/save-score` stores FE display strings (`"1"`, `"2"`, …) as `level` / `end_level`
- Also stores `level_file` / `end_level_file` = real stems (ops/debug only)
- Guests (empty/missing `cardId`): skip `/save-score` and `/logout` (kiosk-only)
- Never save literal `"auto"` — tournament maps to first playlist stem → display `"1"`
- Results leaderboard key = same logical `result.level` (start display name)
- Placeholder playlists: `frontend/src/levelPlaylists.js` (swap when team delivers final 20s)

---

## Non-FE leftovers

- [x] Shared **2P rules Phase A** (lives-only red/DEDUCT; goal-color HUD) — see parent `PLAN_MULTIPLAYER_SCORING_AND_HUD.md`
- [x] Shared **2P rules Phase B** (either-player wave advance + vacuous latch) — **`docs/MP_PHASE_B_TEST_LEVELS.md`**
- [ ] Optional: delete dead `CountdownScreen` / `SettingsScreen`

### Notes
- Red-over-scoreable display already OK on Grid — no Hex-style paint fix needed.

---

## Assets

| Asset | Path (not in repo yet) |
|-------|------------------------|
| Loop | `~/Downloads/activerse_redesign/grid_background.mp4` |
| Still | `~/Downloads/activerse_redesign/grid.jpeg` |

## Product Q&A (2026-09-17 MP Phase A)

- Team Battle **DEDUCT = lives only** (no score) — **final for now** (Hex / Climb / Grid).
- Keep **red cooldown** vs **DEDUCT one-shot** asymmetry.
- Climb DK packs may omit DEDUCT today; later levels may add it — OK.
- Hex **normal** levels: hurt SFX on red/DEDUCT hits; score SFX on scoreable hits (P1 and P2).
- Stale “2P red hits both scores” comments updated to lives-only wording.

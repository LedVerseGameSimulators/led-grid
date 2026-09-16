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

- [ ] Shared **2P rules** later (lives-only red; either-player advance; goal-color HUD) — parent `PLAN_MULTIPLAYER_SCORING_AND_HUD.md`
- [ ] Optional: delete dead `CountdownScreen` / `SettingsScreen`

### Notes
- Red-over-scoreable display already OK on Grid — no Hex-style paint fix needed.

---

## Assets

| Asset | Path (not in repo yet) |
|-------|------------------------|
| Loop | `~/Downloads/activerse_redesign/grid_background.mp4` |
| Still | `~/Downloads/activerse_redesign/grid.jpeg` |

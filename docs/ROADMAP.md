# Implementation Roadmap (post-study)

> **Updated checklists:** [`CLIMB_DEVELOPMENT_PLAYBOOK.md`](./CLIMB_DEVELOPMENT_PLAYBOOK.md) · [`../led-hexagon/docs/LED_HEX_DEVELOPMENT_PLAYBOOK.md`](../led-hexagon/docs/LED_HEX_DEVELOPMENT_PLAYBOOK.md)

Many Phase 1 items below are **done** for Hex/Climb/Hoops headless sim (scoring, HP, session, 2P, overlap). Remaining work is mostly **hardware I/O (Phase 2)** and polish (Phase 3).

Ordered by value × confidence × dependency. Each item: why, effort, risk.

Guiding facts:
- Real goal = replace Tkinter + deploy to physical LED floor, faithful gameplay.
- Our 10 `Extra/*.led` are **single-player `.led`** → our single-player impl is right.
- 3-ring model maps 1:1 to hardware. Logic is I/O-agnostic (state_table in, display out).

---

## Phase 1 — Gameplay fidelity (quick, verified, high-confidence)

**1.1 Fix `cover_action` "disappear" (replaces the wrong respawn)**  ⏱S · risk:low
- Real: an un-stepped goal tile vanishes after `blue_hide_max_time` (~5s). Our
  respawn does the opposite (replenishes). Remove respawn; implement timed
  disappearance of un-stepped goals. Verified in code. **Fixes an active wrong behavior.**

**1.2 DEDUCT_COLOR as its own penalty**  ⏱S · risk:low
- `(254,0,48)` = consume + (−1 score, −1 life), distinct from RED (stays, repeats).
  We currently lump it into red. Small classifier change.

**1.3 Board result + end states**  ⏱M · risk:med
- Track `cur_game_time` (board length = max group end_time) AND session time;
  end → result code **win(1)/lose(0)/timeout(2)**. Show on Result screen.
- Pre-step: verify whether `Extra/*.led` carry `game_accomplished`/`clap_light`
  end-fragment data. If yes → play end-fragment board; if no → result code only.

---

## Phase 2 — Hardware readiness (the real deliverable)

**2.1 I/O driver abstraction**  ⏱M · risk:low (no behavior change)
- Refactor `_run_game` so input/output flow through a `Driver`:
  `read_input(state_table)` + `write_output(led_display)`. `SimDriver` = today
  (clicks via /game-input, output via API→ws_bridge). Clean seam for hardware.

**2.2 HardwareDriver**  ⏱L · risk:med (calibration needs the floor)
- `init_com` + `init_layout` from `led_parameter`; per-frame `read()`→state_table
  (non-blocking/short timeout); flatten `led_display` (3-ring) → 9-byte/tile serial
  via `rect_position_arr`. Flip `USE_SERIAL_HD`. Dry-run with a fake serial now;
  calibrate COM/layout/ring-format on-site (client ~1 week out).

---

## Phase 3 — Breadth / polish (as needed)

**3.1 Leaderboard alignment**  ⏱S
- Reuse/align with existing tourist `game_results` (`score_p1/p2`, `lives`) instead
  of parallel `hex_scores`; optionally session-time credit (`time_left`).

**3.2 Media**  ⏱M
- Per-game audio (real mp3s where available), countdown/idle/type-intro videos.
  Browser-side where it fits the React kiosk.

**3.3 Two-player (`.ledb` / EditorGame2)**  ⏱L
- Only if deploying `.ledb` games: two goal colors (WALL=p1, SCREEN=p2), per-player
  scores. Not needed for our single-player `.led` levels.

**3.4 Multi-board games + game-type catalog**  ⏱M
- Nested fragments + operator browse of `source/` 3 types / 58 games.

---

## Parallel track — replicate to the other 4 games

Original objective: Hoops, Climb, Laser, Battle Arena (built from LED Hex, decompiled).
Apply the same decoupling: mock `LedTable` in each game's `game_running.py`, point at
the same API/frontend. LED Hex is now the proven template. This is a **separate major
phase** — decide when to branch off vs. finishing LED Hex fidelity/hardware.

---

## Recommended order

1. **Phase 1** (1.1 → 1.2 → 1.3) — quick, verified, fixes the wrong respawn. ~1 sitting.
2. **Phase 2** (2.1 → 2.2) — the actual deployment path; build now, calibrate on-site.
3. Then decide: **replicate to 4 games** (original goal) vs **Phase 3 polish**.

Rationale: Phase 1 corrects known-wrong behavior cheaply. Phase 2 is the real
end-goal and is well-scoped (logic already I/O-agnostic). Polish + 2-player + media
are valuable but lower-urgency and partly need assets/hardware we don't have yet.

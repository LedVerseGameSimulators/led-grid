# Known Gaps & Open Questions

> **Primary status & pending work:** [`CLIMB_DEVELOPMENT_PLAYBOOK.md`](./CLIMB_DEVELOPMENT_PLAYBOOK.md) (Climb) · [`../led-hexagon/docs/LED_HEX_DEVELOPMENT_PLAYBOOK.md`](../led-hexagon/docs/LED_HEX_DEVELOPMENT_PLAYBOOK.md) (Hex)

This file focuses on **LED Hex** verification history. Climb-specific gaps (session marathon, square grid, multi-COM) are tracked in the Climb playbook.

Tracks where our headless impl diverges from the real decompiled game, what is
**verified in code** vs **inferred/guessed**, and what's still uncertain.

Legend: ✅ verified in code · 🟡 inferred · ❓ uncertain/unconfirmed · ⛔ guessed (not grounded)

---

## 1. Board / stage progression  ❓ (partially verified)

**Hardware observation (user):** hitting the last matching tile → a new board with
a different color combination appears; "~100s refresh".

**Verified in code:**
- `gui_game.start_game` iterates `self.list_game` (a set of selected games) and
  runs each via `game_running()` in sequence, then shows the result. ✅
- `gui_editor_game.running`: each board runs for `cur_game_time =
  get_max_end_time_in_all_group(dict_group)` (or `game_time`) — **TIME-based**. ✅
- When a board's time ends, it checks `game_record_rt.game_result`:
  - lose (life≤0) → loads `game.clap_light` end-fragment
  - win/time  → loads `game.game_accomplished` end-fragment (a **new board**) ✅
- The end-callback terminates on `life<=0` **or `total_pass > cur_game_time`** —
  **no "all goals cleared → advance" check found.** ✅ (absence verified)

**NOT verified / contradicts:**
- "Clear last tile → instant new board" — ⛔ not found in code. Code advances on
  TIME, then plays `game_accomplished` (new colors). That end-board may be the
  "new board" the user saw.
- Our earlier proposed "loop 17→26 on clear" was ⛔ a guess — do NOT build.

**Our impl:** single board, no progression. Goal **respawn (~5s)** added — has
some code basis (`list_hidden_tread_show` reappear) but its role vs board-advance
is ❓ uncertain.

**Open question for client / original build:** does clearing all tiles early-advance
the board, or is it purely time-based with a win/lose end-fragment?

---

## 2. Goal color  ✅

Within one `.led`, goal color is **constant** (lvl24 green, lvl25 magenta); the
field is 3 permanent `normal_led` groups (0–600s). No in-level rotation. ✅
`running_by_blue` goal-color sequencing is decompile-broken and unused. ✅

---

## 3. Mechanics seen in code but NOT implemented

| Mechanic | Evidence | Status |
|---|---|---|
| Win/lose **end-fragments** (`game_accomplished`, `clap_light`) | gui_editor_game.running | ❌ not impl |
| **Hidden-tile hint/prompt** (`hidden_prompt_score`, breath `#FAFA0A`, prompt cost) | life_value_calculation, list_hidden_group | ❌ |
| **DEDUCT_COLOR** `(254,0,48)` penalty tiles | calculation_editor_group_scode | ❌ |
| **Safe tiles / `cover_action`** (disappear vs prompt) | gui_editor_game (safe_color, cover_action) | ❌ |
| **Multiplayer** (`COLOR_ARR`, per-player scores) | gui_editor_game2 color_array/color_scode | ❌ |
| **Wall lights** (`goal_led` strip) / **Screen lights** (`goal2_led`, numbers) | calculation_one_second_wall_light/screen | ❌ (off in our levels) |
| Real **audio** mp3s (bg/blood/score) | game_music, Audio | 🟡 synth beeps only |
| **Videos** (intro/idle/type) | game_obj.*_video | ❌ |
| **Result screen** ranking + DB record (`game_player_group`) | gui_game.game_result | 🟡 our own hex_scores |
| **RFID/barcode** session + 60-min timer | gui_player_login, check_session | ❌ |

---

## 4. Things we changed / fixed (for the record)

- `Play.running()` movement gating (decompile bug: moved every frame) → fixed ✅
- Mock `LedTable` (Tkinter widget unrecoverable) → reconstructed from usage ✅
- 3-ring color model, breath, consume, type-aware goal scoring, HP, 300s time,
  zone, leaderboard, audio — implemented (see STATUS.md).

---

## 5. Next: deep code study (TODO)

Systematically read the real game flow end-to-end to find more divergences:
- `gui/gui_game.py`, `gui/gui_game_main.py` — session/board orchestration
- `gui/gui_editor_game.py`, `gui_editor_game2.py` — per-board run + scoring
- `game_play/game_util.py` — level/fragment loading, time calc
- `game_play/life_value_calculation.py` — all scoring variants
- `game_play/Play.py` — run modes (running / running_by_blue / running_new)
- `model_in/led_group.py` — group behaviors (blink/breath/vary/end)

Goal: a verified mechanic-by-mechanic map of real vs our impl.

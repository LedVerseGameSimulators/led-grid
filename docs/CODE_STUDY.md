# Deep Code Study — Real Game vs Our Impl

Systematic read of the decompiled engine (Play, gui_game, gui_editor_game/2,
life_value_calculation, game_util, led_group). Verified mechanic map + ranked
discrepancies. ✅=verified in code · ❓=uncertain · ⛔=decompile-broken.

---

## A. Board / session end model  ✅ (big discrepancy)

Real (`gui_editor_game.running` + `callback_in_every_frame`):
- Two timers run together:
  - `cur_game_time = get_max_end_time_in_all_group(dict_group)` — **board** length (from the data's max group end_time)
  - `game_time_left = game_time * 60` — **session** timer (5min = 300s)
- Board ends when **ANY**: `life<=0` | `total_pass > cur_game_time` | `game_time_left<=0`
- Sets `game_result`: **0 = lose** (life), **1 = win** (board time done), **2 = timer expired**
- Then loads an **end-fragment**: `clap_light` (lose) or `game_accomplished` (win) — a
  separate board/animation — and runs it with a no-score callback.
- A session iterates `list_game` (selected games); `game_result()` shows the result screen.

**Our impl:** single 300s timeout + HP; **no win/lose/timeout distinction**, **no
end-fragment**, **no board-length (`cur_game_time`)**. ❌

**No "clear all → advance" exists in code** — advance is time/life only. The
"new board" the user saw = the `game_accomplished` end-fragment (new colors).

---

## B. `cover_action` = "disappear" vs "prompt"  ✅ (conflicts with our respawn!)

`game.cover_action` False → **"disappear"** (lvl25 is False):
- A static goal/DEDUCT tile that's been visible > `blue_hide_max_time` (5s) and
  isn't covering other/safe/red → **permanently removed**. Goals you don't step
  in time **vanish** (timed challenge). They do **not** come back.

"prompt" (cover_action True):
- Tile is hidden after the window; can be **revealed by stepping its goal spot**
  at a cost of `prompt_cost` score + 1 life (`list_hidden_group`, `prompt_time`).

**Our impl:** we made goals **respawn every ~5s** (opposite of "disappear") and
have no prompt/reveal. ⛔ Our respawn is likely **wrong** — real mode removes
un-stepped goals, not replenishes them. Needs rethink.

---

## C. Two-player model  ✅ (structural)

`gui_editor_game2` (the multiplayer runner): `player_nums = 2` hardcoded.
- Player 1 goal color = `WALL_LIGHT` (goal_led); Player 2 = `SCREEN_LIGHT` (goal2_led).
- Per-player scores `color_scode[i]`, cumulative `total_scode[i]`.
- "two-color mode" when both goal types present; `frame_auto_jump` advances when
  both players' goals active.
- A level with only `goal_led` (no `goal2_led`, e.g. lvl25/24) → effectively **1
  player / 1 goal color**.

**Our impl:** single score. ✅ fine for our 1-color levels, but the engine is
fundamentally 2-player; multi-color/2-goal levels would need per-player scoring.

---

## D. Scoring by tile (verified exact)

| Tile | Score | Life | Consumed? |
|---|---|---|---|
| **goal_color** floor | +1 | — | yes (removed) |
| **RED** `(254,0,0)` | −1 | −1 (every `TIME`=1.2s) | **no** (stays, repeats) |
| **DEDUCT_COLOR** `(254,0,48)` | −1 | −1 (if not on red) | yes |
| **safe_color** | 0 | 0 | reappears (hidden tread) |
| other | 0 | 0 | — |

**Our impl:** goal +1/consume ✅; red −1/HP/no-consume ✅; **DEDUCT lumped into red**
(our `_rgb_is_red` matches (254,0,48) since b=48<80) — wrong consume behavior ❌;
safe/other neutral ✅ (no hidden-tread).

---

## E. Engine details (verified)

- **Run mode:** all our levels `play_order=False` → real uses `running_by_blue`
  (we use `running`). `running_by_blue` adds `frame_auto_jump` goal-sequencing,
  but that's ⛔ decompile-broken (`append(a,b)`, `removemember`) → no-op anyway.
  Movement identical. Acceptable. ✅
- **Movement:** speed = cells/sec, gated by `move_distance`; cells leaving
  `activity_area` are dropped (disappear) or **bounce** when all would leave.
  Our `running()` fix matches this. ✅
- **goal_led** start_member forced to `goal_led_coors` single point → it's a
  fixed indicator. ✅ (matches our finding)
- **Frame rate:** real targets **30 FPS** (`sleep = 1/30 - elapsed`); we run ~100fps.
  Cosmetic; could match. 🟡
- **LedGroup.breath**: pulses each ring's dominant channel over `BREATH_SECOND=2s`.
  We call it ✅. **blink** (3× flash on collect) and **vary** (life_period
  countdown for hidden tiles) — `vary` is ⛔ decompile-broken. We use our own flash.
- **Group types:** `normal_led`=floor, `goal_led`=wall indicator, `goal2_led`=screen
  numbers/text. We handle floor + treat goal_led as indicator; **goal2_led/screen
  text not handled** ❌ (off in our levels).

---

## F. Loaders (verified)

- `.led` = ZIP → folder → `game_file` shelve with `dict_group` + `para_key_game`.
- `read_game_and_group` also rescales groups if layout differs (`group_size_scale`)
  and forces wall groups to `goal_led_coors`.
- A "game" can hold **multiple board subfolders** (fragments); `read_game_frag` /
  `read_game_parameter_game_frag` load them (used for end-fragments + variants).
  Our `Extra/*.led` are **single-folder (one board)**. ❌ multi-board games unhandled.

---

## Ranked discrepancies (what to fix, by impact)

1. **Board end model + win/lose + end-fragment** (A) — biggest. We have a flat
   300s timeout; real has board-time + session-time + win/lose + accomplished board.
2. **cover_action "disappear"** (B) — our respawn is likely backwards; real
   *removes* un-stepped goals. Rethink respawn vs disappear.
3. **DEDUCT_COLOR** (D) — separate from red (consume + penalty).
4. **2-player / per-player scoring** (C) — for multi-goal levels.
5. **Hidden/prompt reveal** (B) — prompt_cost reveal mechanic.
6. **goal2_led screen text**, **multi-board games**, **30fps**, **blink-on-collect** — lower.

---

## Honest status of our "complete" claims

What we built is a **faithful single-board, 1-player, time-boxed** version with
real patterns/movement/breath/goal-scoring/HP/leaderboard. But the **board
lifecycle** (win/lose/end-fragment/board-vs-session time) and **cover_action
disappear** are materially different from the real game. The respawn we added
contradicts "disappear" mode and should be revisited.

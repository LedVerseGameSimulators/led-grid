# Deep Code Study II — Hardware I/O, DB/Session, Deployed Content

Second pass: serial hardware path, database/session/login, and the real deployed
game catalog + media. ✅ verified · ❓ uncertain · ⛔ decompile-broken.

---

## 1. Hardware serial I/O  ✅ (great news for HardwareDriver)

### Output (PC → LEDs) — `led_control.draw_led_color`
Frame: `[255, 255]` header, then per tile **9 bytes = 3 rings × RGB**, sent
**outer→mid→inner** (`for k in range(2,-1,-1)`), tiles in **reversed** order.

> **Our 3-ring `led_display` maps 1:1 to hardware** — each hex tile is physically
> **3 concentric LEDs**, exactly our outer/mid/inner. Sending = flatten our display
> buffer to this byte order. The whole 3-ring effort pays off directly on hardware.

### Input (sensors → PC) — `led_control.read(com, state_table, start, size, block)`
- 3 bytes per sensor; a byte `== 10` (0x0A) means **pressed**.
- `0xFC` (252) frames the packet; data split before/after the marker.
- Result written straight into `state_table[row][col]` — **our exact input array**.
- ⛔ The before/after reverse-indexing in `read()` has decompile bugs (lines ~202)
  — would need fixing/verification against real hardware.

### Mapping — `init_layout(layout_type, row, col, position_no_use)`
- Builds `rect_position_arr` = 1D wire order → `(row,col)`, via `position_convert`
  (8 **serpentine** layout types). `position_no_use` (= `floor_layout_coors_no_use`)
  drops dead/corner cells. `corner_line_start` splits wall vs floor.

### Ports — `init_com(list_com_info)`
- `list_com_info = [[port, start_idx, end_idx, type], ...]` e.g.
  `['COM9','1','33','normal_led']` → tiles 1–33 on COM9. **Multiple ports** (floor /
  wall / screen) supported. 115200 baud, 0.3s timeout (`communication.py`).

### Failure mode (USE_SERIAL_HD=True, no hardware)
- `init_com` leaves dead ports as `None` (logged, continues).
- **`read()` blocks up to 0.3s per port** → wrecks loop timing with multiple ports.
  A HardwareDriver must use **non-blocking / short-timeout** reads.

**Implication for our HardwareDriver:** input = call `read()` → state_table each
frame; output = flatten `led_display` (3-ring) → 9-byte/tile frame via
`rect_position_arr`. Init `init_com` + `init_layout` from `led_parameter`. Logic
untouched. The serpentine mapping + serial framing + non-blocking reads are the work.

---

## 2. Database / session / login  ✅

- **Engine:** sqlite `setting/ledplaydb.sqlite` (originally MySQL @192.168.225.50).
- **Barcode mode** scores → `game_player_group` (joins `game_group` + `player_group`,
  multiplayer). Leaderboard: `search_game_result*` `ORDER BY scode DESC`.
- **Tourist mode** (no card) → a **separate** `./data/local_data.db` `game_results`
  table — rich: `score, score_p1, score_p2, lives_start, lives_left, duration_min,
  time_played_sec`. There's already a `TouristRecord` API for this.
- **Player** (`custom_info`): `custom_id, phone_num, name, public, time_left, card_id`.
- **Session/60-min:** `time_left` = **minutes credit** per player; validated at login
  (`time_left - game_time*count < 0` → reject), decremented after each game via
  `custom_comsume` + `update_custom_info_by_id`. Not a hard wall-clock 60-min.
- **net_socket** (UDP): remote `START/STOP/GETSTATUS/GETRANKING/GETGAMEDICT` — for a
  remote controller (ip 192.168.x:3020). ⛔ decompile cut at line ~194.

**Our `hex_scores` vs reality:** closest to **tourist `game_results`** (we even have
score/life/time). Adequate for a single-player kiosk leaderboard. Missing: barcode
multiplayer grouping (game_group/player_group joins), per-player p1/p2 columns,
session-time credit decrement. The original **already had a tourist leaderboard** —
we partly reinvented it.

---

## 3. Deployed content + media  ✅ (important structural finding)

### Catalog: `source/` = **58 games in 3 types** (we have 10 in `Extra/`)
```
source/-/    00.led … 16.led     (17 large games)
source/--/   YC01.led … YC18.led (18 medium games)
source/---/  DK01.ledb … , YCDK*.ledb, "Mind level 01.ledb"  (23 small/variant)
```
- **`.led` → `EditorGame`** (single-player runner). **`.ledb` → `EditorGame2`**
  (the **2-player / multi-fragment** runner). The extension picks the runner!
- Some games have **nested board folders** (multi-board fragments); ours are flat
  single-board. `Extra/17–26.led` are **single-player `.led`** games → our
  single-player impl is correct **for these**.

### Audio (`game_music.py` + `audio.py`, pygame mixer)
Per-game overrides, fallback to settings: `rule_introduce`, `bmg_video` (loops),
`count_down`, `red_tread` (life-loss), `blue_tread` (score), `clap_light` (win),
`error_clap`, `correct`, `game_accomplished`. Flow: intro → countdown → bmg loop;
win → accomplished. **We use synth beeps; per-game mp3s on Windows paths we lack.**

### Video
`countdown.mp4` (between select and start), **idle/attract** video (VLC subprocess
after ~5min idle), **game-type intro** videos. We have none.

### Flow (`gui_game_main`)
operator: **pick game type → pick game name → level select → countdown video →
game**. Idle video loops on the attract screen. We have login→select→settings→play.

---

## Cross-cutting takeaways

1. **3-ring was the right call** — maps directly to the physical 3-LED hex tile and
   the serial output format. Hardware output = flatten our display buffer.
2. **`.led` = single-player, `.ledb` = 2-player.** Our 10 `Extra/*.led` are
   single-player; our impl matches. 2-player only matters if we run `.ledb` games.
3. **A tourist leaderboard already existed** (`game_results`, score_p1/p2/lives) —
   align our `hex_scores` to it or reuse `TouristRecord` instead of a parallel table.
4. **Hardware mode is well-scoped**: write a `HardwareDriver` (read→state_table,
   display→serial via `rect_position_arr`), init from `led_parameter`, non-blocking
   reads, flip `USE_SERIAL_HD`. No game-logic change. Calibration is the on-site work.
5. **Media/flow gaps** (countdown/idle/type videos, per-game audio, game-type catalog
   browsing) are presentation — needed for a polished kiosk, not for core gameplay.

## Decompile-broken spots noted (avoid relying on)
- `led_control.read()` before/after reverse indexing (lines ~202), `get_com_num`
  slice, `init_led_screen` array init.
- `Play.frame_auto_jump` / `goal_led_group_start_time_list` (append/removemember).
- `LedGroup.vary` body missing.
- `net_socket` truncated.

# Settings & Config Reference (shared across floor games)

> **Current implementation status per game:** see each repo’s development playbook (`CLIMB_DEVELOPMENT_PLAYBOOK.md`, `LED_HEX_DEVELOPMENT_PLAYBOOK.md`, `HOOPS_DEVELOPMENT_PLAYBOOK.md`).

Source of truth for shelve fields. Documents config keys, typical values, and **original** implementation status when this doc was first written.

**Headless API (2026-06):** Most “Game rules” fields below are now **read from shelve** in all three games (`game_time_sw`, `life_value_sw`, `value_high`/`value_width`, etc.). Treat ❌ rows in early sections as **historical** unless the playbook still lists them as pending.

Status legend:
- ✅ **used** — we read/honor it
- 🟡 **hardcoded** — we use a fixed value, not the real setting
- ❌ **ignored** — not implemented yet
- 🔌 **hardware** — only relevant on the physical LED floor (deferred)

---

## 1. `setting/led_parameter` (shelve DB) — ~60 fields

### Game rules
| Key | Real value | Controls | Status |
|---|---|---|---|
| `game_time_sw` | 5.0 (minutes → 300s) | total game length | 🟡 hardcoded 180s → fix to 300 |
| `life_value_sw` | 20 | starting HP / blood | ❌ no HP system |
| `leval_span_sw` | 0.9 | level speed span (feeds `get_game_speed`) | 🟡 hardcoded `game_level_speed` |
| `player_num_sw` | 1 | number of players | ❌ single-score only |
| `game_scode_divide_person_sw` | False | divide score by player count | ❌ |
| `game_scode_divide_time_sw` | False | divide score by time | ❌ |
| `corner_line_start` | 0 | wall corner line start | ❌ |
| `barcode_function_sw` | False | RFID/barcode login + scoring | ❌ |

### Hidden-tile bonus mechanic
| Key | Real value | Controls | Status |
|---|---|---|---|
| `hidden_show_time` | 5.0 | how long a revealed hidden tile shows | ❌ |
| `hidden_prompt_score` | 5 | score cost/bonus for prompt | ❌ |
| `hidn_tread_show_time` | 100.0 | hidden-after-tread show time | ❌ |
| `hidden_prompt_breath_color` | #FAFA0A | breath color of prompt tile | ❌ |
| `goal_led_coors_row` / `_col` | 1 / 5 | goal indicator position | ❌ |

### Wall / screen LED outputs (secondary strips)
| Key | Real value | Controls | Status |
|---|---|---|---|
| `wall_light` | False | enable wall LED strip | ❌ (off in our levels) |
| `screen_light` | False | enable screen LED (numbers/text) | ❌ (off in our levels) |
| `wall_light_layout_real/_logic` | [1..16] | wall LED layout | 🔌 |
| `wall_light_table` | coords | wall LED positions | 🔌 |
| `wall_layout_start/direct/delete` | — | wall layout build | 🔌 |

### Audio
| Key | Real value | Controls | Status |
|---|---|---|---|
| `game_bg_audio_sw` | TRON mp3 | background music | ❌ silent |
| `game_blood_sw` | A02.mp3 | life-lost / bomb sound | ❌ |
| `game_scode_sw` | 001.mp3 | score sound | ❌ |
| `local_music_sw` | True | use local music | ❌ |
| `game_failure_sw` | "" | failure sound | ❌ |

### Video / presentation
| Key | Real value | Controls | Status |
|---|---|---|---|
| `game_start_video_sw` | "" | intro video | ❌ |
| `game_idle_video_sw` / `idle_video_sw` | "" | idle/attract video | ❌ |
| `idle_video_time_span` | 1 | idle trigger delay | ❌ |
| `game_type_video_sw` .. `_video4_sw` | mp4s | game-type select videos | ❌ |
| `game_type_name_sw` .. `_name4_sw` | -, --, ... | game-type labels | ❌ |
| `text_introduce1_sw` .. `4_sw` | "" | intro text | ❌ |
| `game_leval_editable_sw` | True | level editable in UI | ❌ |
| `game_time_editable_sw` | False | time editable | ❌ |
| `life_value_editable_sw` | False | life editable | ❌ |
| `player_num_editable_sw` | False | player count editable | ❌ |

### Blue-mode / goal sequencing
| Key | Real value | Controls | Status |
|---|---|---|---|
| `blue_hide_max_time_sw` | 5.0 | blue tile hide window | ❌ |
| `game_leval` / `game_leval_sw` | 1 | level index | ✅ (level chosen in UI) |

### Layout / grid
| Key | Real value | Controls | Status |
|---|---|---|---|
| `value_width` / `value_high` | 9 / 5 | active zone size (9 cols × 5 rows) | 🟡 render full 16×26 |
| `floor_layout_coors_no_use` | coords | dead/unused floor cells | ❌ |
| `led_layout_type` | 1 | floor layout type | 🔌 |

### Network / hardware
| Key | Real value | Controls | Status |
|---|---|---|---|
| `list_com_info` | COM9 normal_led | floor serial port | 🔌 |
| `list_wall_com_info` / `list_screen_com_info` | [] | wall/screen serial | 🔌 |
| `ip_address` / `local_ip_address` / `local_ip_port` | 192.168.x / 3020 | remote/net play | 🔌 |
| `list_game_name` | ['新游戏2','新游戏1'] | saved game names | ❌ |

---

## 2. `setting/debug_parameter` (shelve DB) — 5 fields

| Key | Real value | Controls | Status |
|---|---|---|---|
| `tread_red_time` | 0.01 | seconds on red before life loss | ❌ instant penalty |
| `life_value_count_time` | 1.2 | min interval between life losses | ❌ |
| `com_is_block` | True | serial blocking mode | 🔌 |
| `log` | True | logging on | ✅ (we log) |
| `game_display` | True | show display | ✅ (sim) |

---

## 3. Per-level game object (`para_key_game` inside each `.led`)

| Attr | Lvl 25 value | Controls | Status |
|---|---|---|---|
| `play_order` | **False** | False → `running_by_blue` (goal-color mode); True → `running` | ⚠️ we always use `running` |
| `row` / `col` | 5 / 9 | active zone size | 🟡 |
| `zone_row_from/to`, `zone_col_from/to` | 0–5 / 0–9 | play zone bounds | ❌ |
| `game_level` | 'standard' | difficulty band | 🟡 |
| `game_type` | 'default' | game variant | ❌ |
| `cover_action` | False | disappear vs prompt on tread | 🟡 (we always consume) |
| `safe_color` | [None×3] | safe tile color | ❌ |
| `wall_light` / `screen` | False | secondary outputs | ❌ |
| `background` | (0,0,0) | bg color | ✅ (black) |
| `blue_tread` / `red_tread` | None | event audio | ❌ |
| `count_down` | None | countdown overlay | ❌ |

---

## 4. Color constants (`model/setting.py`)

| Const | Value | Meaning |
|---|---|---|
| `RED` | (254,0,0) | hazard / penalty tile |
| `GREEN` | (0,254,0) | goal marker (ring 0) |
| `BLUE` | (0,0,254) | blue-mode target |
| `DEDUCT_COLOR` | (254,0,48)×3 | dedicated penalty tile |
| `COLOR_ARR` | 8 colors | per-player colors (multiplayer) |
| `WHITE/YELLOW/GRAY/TEST_COLOR` | — | misc |
| group types | `normal_led`=FLOOR, `goal_led`=WALL, `goal2_led`=SCREEN | — |

---

## Implementation order (planned)

1. **Load real settings** — read `led_parameter` / `debug_parameter` once; replace hardcodes (game_time=300s, life_value=20, leval_span=0.9, red timing).
2. **Run loop** — honor `play_order`: use `running_by_blue` + goal-color sequencing (the real core mechanic).
3. **Type-aware scoring** — goal_led vs normal_led vs DEDUCT/RED; HP/life system.
4. **Zone** — confine play to 5×9 active area.
5. Breadth: hidden tiles, multiplayer, audio, DB leaderboard, videos.

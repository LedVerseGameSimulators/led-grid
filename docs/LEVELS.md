# LED Hex Game — Levels Overview

67 levels across 4 categories. All levels share a 5×9 active zone on a 16×26 full grid, 300s session, and 20 HP.

---

## Summary Table

| Category | Files | Count | Players | Goal Color | Stagger | Special Mechanics |
|----------|-------|-------|---------|------------|---------|-------------------|
| extra    | Extra/17-26.led | 10 | 1P | Magenta | Groups span t=0–600 (no stagger) | Moving red hazard, green indicator; test/dev levels |
| basic (DK) | source/---/DK01–DK11.ledb | 11 | 2P | Blue (P1) + Orange (P2) | None | 8s respawn on consumed tiles |
| basic (YCDK) | source/---/YCDK02–YCDK11.ledb | 11 | 2P | White (P1) + Yellow (P2) | Some levels | Dark teal decor, DEDUCT tiles, 8s respawn |
| advanced | source/--/YC01–YC18.led | 18 | 1P | Magenta | None | Dark teal decor, cover_action=True (prompt mode) |
| pro      | source/-/00–16.led | 17 | 1P | Cyan | Yes — groups at t=40s intervals | Natural wave progression |

---

## Core Mechanics

### Session & Grid

- **Full grid:** 16×26 tiles
- **Active zone:** 5×9
- **Session time:** 300s (session ends before `board_time_sec` in most levels)
- **`board_time_sec`:** Equal to the max group `end_time` — typically 600s
- **Starting HP:** 20

### Tile Types

Every level contains at minimum:

- **`normal_led`** — Floor tiles (safe, no effect)
- **`goal_led`** — P1 goal indicator at position (0,4). Fires in 1-second windows every 2–4s to set the current goal color.
- **`goal2_led`** — P2 goal indicator (`.ledb` files only)

Additional tile types by category:

| Tile | Effect | Present in |
|------|--------|------------|
| Red hazard `(254, 0, 0)` (in most levels) | −1 score, −1 HP on step | extra, advanced, pro |
| `DEDUCT (254, 0, 48)` | −1 score, −1 HP + tile consumed | basic/YCDK |
| Dark teal decor | Safe (no effect) | advanced/YC, basic/YCDK |
| Green indicator | Goal indicator variant | extra |

### Scoring

- Step a tile matching the current goal color: **+1 score**
- Step a red hazard tile: **−1 score, −1 HP**
- Step a DEDUCT tile `(254, 0, 48)`: **−1 score, −1 HP**, and the tile is consumed

### Stagger (Group Start Times)

- **1P levels (pro):** Tile groups have staggered `start_time` values (e.g. t=0, 40, 80, 120s), creating a natural wave progression without respawn.
- **1P levels (extra, advanced):** No stagger — all groups run t=0–600s simultaneously.
- **2P levels (basic/DK):** No stagger. The 8-second respawn on consumed tiles provides natural board refresh.
- **2P levels (basic/YCDK):** Some levels have stagger.

### Respawn

- **1P levels:** No respawn. Level progression is driven by staggered group `start_time` values (pro series) or static boards (extra, advanced).
- **2P levels (`.ledb`):** 8-second respawn on consumed tiles. This is the primary progression mechanism for the DK series, which has no stagger.

### Cover Action / Prompt Mode

When `cover_action=True` and a `safe_color` is set (teal in YC levels), the game enters **prompt mode**: tiles are covered and revealed via player interaction.

- Present in: **advanced/YC** (all 18 levels), implicitly in YCDK levels with dark teal decor.

---

## Special Levels

| Level | Notable Property |
|-------|-----------------|
| **Extra/17** | 3 staggered magenta groups at t=0–60s, t=60–120s, t=120–600s — the only extra-category level with stagger |
| **Pro/00** | 4 staggered cyan groups at t=0, 40, 80, 120s — cleanest example of the 40s natural wave interval pattern |
| **DK03** | P1 and P2 share the same goal color (cyan). Board is split by checkerboard rule: tiles where `(row+col) % 2 == 0` are P1 territory; odd tiles are P2 |
| **DK09** | P2 goal color is red `(254, 0, 0)`. Red tiles on the board are P2 goals, not hazards — context-dependent tile semantics |
| **YC01** | `cover_action=True`, `safe_color=teal`. The canonical prompt-mode level; the advanced series reference implementation |

---

## File Format

`.led` and `.ledb` files are **ZIP archives** containing a Python `shelve` database. The database holds two top-level keys:

| Key | Type | Contents |
|-----|------|----------|
| `dict_group` | dict | Map of group name → `LedGroup` objects. Each group defines a set of tiles with a color, `start_time`, `end_time`, and behavior flags. |
| `para_key_game` | `Game` object | Global level parameters: active zone bounds, `cover_action`, `safe_color`, session HP, and other game-wide settings. |

**File extension meaning:**

- `.led` — Single-player level
- `.ledb` — Two-player level (adds `goal2_led` group and respawn logic)

**Source directory layout:**

```
source/
  -/        ← pro levels (00–16.led)
  --/       ← advanced levels (YC01–YC18.led)
  ---/      ← basic levels (DK01–DK11.ledb, YCDK02–YCDK11.ledb)
Extra/      ← extra/test levels (17–26.led)
```

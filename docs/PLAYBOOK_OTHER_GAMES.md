# Playbook: Headless Decoupling for Hoops, Climb, Laser, Battle Arena

LED Hex is the proven template. All 4 games share the same Python skeleton but
have **different hardware routing** — verified from actual decompiled source.

---

## Verified game differences (from source code + video)

| Game | Floor | Wall Lights | Input method | Grid |
|---|---|---|---|---|
| **Battle Arena** | Hex LED (same as LED Hex) | Yes, indicators | Hex tile step | 16×26 hex |
| **Climb** | Square LED | Optional | Walk on lit floor path | 16×26 square |
| **Laser** | Square LED | **Wall pressure buttons** | Press lit wall box | 16×26 + 1D wall perimeter |
| **Hoops** | Square LED | **Hoop sensors** (the hoops ARE wall lights) | Ball through hoop sensor | 16×26 + wall |

**Video ↔ game mapping:**
- Basketball hoops lit up → **Hoops** (wall hoop sensors, not floor)
- Square LED floor, walking → **Climb** (floor tile tracking)
- Dark room, wall boxes lit → **Laser** (wall pressure buttons, 1D array)

**Porting order (easiest → hardest):**
1. Battle Arena — identical hex architecture to LED Hex
2. Climb — square grid, same floor tile logic, just not hex
3. Laser — wall button 1D array, different input model
4. Hoops — external hoop sensor, most different input path

---

## Source locations (verified)

| Game | Python source | Level data |
|---|---|---|
| Battle Arena | `/Users/apple/Desktop/activerse/battle arena/ledhexagon_py_source/` (40 files) | `ledhexagon_source_code/source/` |
| Climb | `/Users/apple/Desktop/activerse/climb/climb_py_source/` (25 files) | `ledplay/source/{-,--,---}/` |
| Laser | `/Users/apple/Desktop/activerse/laser/lasertrap_py_source/` (40 files, has database + audio) | `_unpacked/lasertrap10/lasertrap/source/` |
| Hoops | `/Users/apple/Desktop/activerse/hoops/hoops_py_source/` (25 files) | `ledplay/source/{-,--,---}/` |

---

## What is shared across all games (copy from LED Hex, no changes needed)

- `game_hw.py` — serial LED control (identical code)
- `Play.py` run modes, movement gating (same bugs, same fixes)
- `model/setting.py` — Color, FLOOR_LIGHT, WALL_LIGHT, SCREEN_LIGHT, directions
- `model/group.py`, `model/game.py` — Group and Game object structure
- `GameInstance`, `GameManager`, frame callback pattern (copy from LED Hex API)
- `_normalize_rings`, `_cell_is_lit`, `_group_main_color`, `_rgb_is_red` helpers
- Frontend: same React app, same SimulatorScreen — just register a new game type

---

## Step-by-step per game

## LED floor game migrations — shared steps

> **Decompilation:** Prefer **Docker pycdc** over uncompyle6. See `led-grid/scripts/decompile-pycdc.sh`  
> and `CLIMB_MIGRATION_PLAYBOOK.md` §2b. Extract exe with Python **3.7** so PYZ is complete.

### STEP 1 — Copy LED Hex mock LedTable into the game

**What:** `game_running.py` has an unrecoverable Tkinter import. Replace it.

**Do:**
```bash
cp /Users/apple/parallel-work/ledhexagon_clone/game_play/game_running.py \
   /Users/apple/Desktop/activerse/<game>/<source>/game_play/game_running.py
```

**EXCEPTION — Climb/Hoops/Laser:** The mock LedTable uses `led_row=16, led_col=26`
for hexagonal layout. Square games also use 16×26 so mock is compatible.
No change needed to the mock itself.

**Verify:** `python -c "from game_play.game_running import LedTable; t=LedTable(100); print('ok')"` from the game source dir.

**Pitfall:** Some games import `led_table` from `gui2.gui_led_table_editor` — confirm
the import is gone after copy.

---

### STEP 2 — Fix Play.py decompile bugs

**What:** Copy the fixed Play.py from LED Hex (movement gating fixed).

```bash
cp /Users/apple/parallel-work/ledhexagon_clone/game_play/Play.py \
   /Users/apple/Desktop/activerse/<game>/<source>/game_play/Play.py
```

**Known bugs fixed:**
- `running()` movement — groups moved every frame regardless of speed (frame-rate bug)
- `goal_led_group_start_time_list()` — `append(a, b)` TypeError
- `frame_auto_jump()` — `removemember` AttributeError

**Verify:** `python -c "from game_play.Play import Play; print('ok')`"

---

### STEP 3 — Stub game_hw.py Tkinter messageboxes

**What:** `game_hw.py` calls `messagebox.showinfo/showerror` which crash headlessly.

```bash
cp /Users/apple/parallel-work/ledhexagon_clone/game_play/game_hw.py \
   /Users/apple/Desktop/activerse/<game>/<source>/game_play/game_hw.py
```

Or patch just the messagebox lines → `logger.warning(...)`.

**Verify:** `python -c "from game_play.game_hw import GameHW; print('ok')"` (no Tkinter error).

---

### STEP 4 — Load and inspect the level data

**What:** Open a `.led`/`.ledb` level file, dump `dict_group` structure, understand this game's tile/group types.

```python
import zipfile, tempfile, shelve, os
from collections import Counter

f = '/path/to/level.led'   # or .ledb
with tempfile.TemporaryDirectory() as t:
    with zipfile.ZipFile(f) as z: z.extractall(t)
    for root,_,files in os.walk(t):
        if any(fi.startswith('game_file') for fi in files):
            db = shelve.open(os.path.join(root,'game_file'))
            dg = db.get('dict_group'); g = db.get('para_key_game')
            types = Counter(getattr(x,'type',None) for x in dg.values())
            print('group types:', dict(types))
            print('game zone:', g.zone_row_from, g.zone_row_to, g.zone_col_from, g.zone_col_to)
            # sample colors
            for grp in list(dg.values())[:5]:
                print(type(grp).__name__, getattr(grp,'type',None), getattr(grp,'color',None))
            db.close(); break
```

**Key questions:**
- Which group type is the scoring target? (`FLOOR_LIGHT` / `WALL_LIGHT` / `SCREEN_LIGHT`)
- What colors are used?
- Any groups with `speed > 0` (moving hazards)?
- What is the play zone (`zone_row_from/to`, `zone_col_from/to`)?

**Game-specific expectations:**

| Game | Scoring group type | Notes |
|---|---|---|
| Battle Arena | `FLOOR_LIGHT` + `WALL_LIGHT` | Same as LED Hex |
| Climb | `FLOOR_LIGHT` | Walk path on floor, blue = goal |
| Laser | `WALL_LIGHT` | 1D wall perimeter positions, not 2D grid cells |
| Hoops | `WALL_LIGHT` | Hoop positions in 1D wall array |

---

### STEP 5 — Implement game-specific classifier

**What:** In the frame callback, classify cells by group type into goal/red/deduct/decor.
This is the only truly game-specific logic.

**Battle Arena:** Copy LED Hex classifier exactly — same hex floor, same color rules.

**Climb:** Same classifier as LED Hex for FLOOR_LIGHT groups. Blue tiles = goal.
Scoring = walk on lit tiles (hold step).

**Laser (CRITICAL DIFFERENCE):**
- Scoring tiles are `WALL_LIGHT` not `FLOOR_LIGHT`
- `group.start_member` = list of **wall indices** (integers), not (row, col) tuples
- Wall perimeter formula: `perimeter = (2*row + 2*col - 4) / 3`
- `state` for wall = `led_table.get_wall_light_state_array()` not `state_table`
- Classifier must read `wall_state[idx]` not `state_table[row][col]`

```python
# Laser scoring loop (replace the 2D state_table loop)
wall_state = led_table.get_wall_light_state_array()
wall_groups = [g for g in dgroup.values() if getattr(g,'type',None) == Setting.WALL_LIGHT
               and g.start_time_sec <= total_pass <= g.end_time_sec]
for g in wall_groups:
    for idx in g.start_member:
        if wall_state[int(idx)]:
            game.try_score_cell_wall(int(idx))  # new method for wall scoring
```

**Hoops (CRITICAL DIFFERENCE):**
- Hoop detection is **external** — a ball sensor fires an event, not the floor state_table
- `WALL_LIGHT` groups = lit hoops (display only)
- Input path: sensor event → `apply_wall_input(wall_idx)` → `try_score_wall(idx)`
- Need to understand how the hoop sensor callback reaches the Python code
  - Check `game_hw.py` for sensor read methods beyond `update_led`
  - Look for callback hooks in `Play.running_new()` `parent` parameter
- **This is the most uncertain step — investigate before implementing**

---

### STEP 6 — Wire to GameManager + API

**What:** Add this game as a new `game_type` in the API. Minimal changes.

In `api/game_manager.py`:
- Add the game's source path to `sys.path` (same pattern as LED Hex)
- Extend `candidates` list in path resolution to include this game's level dirs
- The `GameInstance`, `_frame_callback`, `Play.running()` pattern is identical

In `api/main.py`:
- `/levels` endpoint: add glob pattern for this game's level directory
- `/start-game`: accept `game_type` param to route to correct `game_manager` instance
  (or run separate API process per game on different ports)

In `frontend/src/screens/GameSelectionScreen.jsx`:
- Add the game to `GAMES` array — it auto-routes via `game` field in config.

---

### STEP 7 — Test end-to-end

Checklist per game:

```
[ ] game_running.py imports without Tkinter error
[ ] Play.py imports and running() can be called
[ ] Level file loads: dict_group not empty, para_key_game readable
[ ] Frame callback fires (check API logs at ~60fps debug line)
[ ] led_display has correct lit cells (check via /game-state)
[ ] Goal tiles classified correctly (scoring group matches expected type)
[ ] Press a goal tile → score increments
[ ] Press a red/hazard tile → score decrements, HP decrements
[ ] Life system: HP drains to 0 → game_over=True
[ ] Time: 300s session counts down correctly
[ ] Result screen shows correct score and leaderboard
[ ] ws_bridge broadcasts frames to simulator (check active tiles > 0)
```

---

## Game-specific investigation checklist (before starting each game)

### Battle Arena
- [ ] Confirm hex vs square grid in `setting.type` or `led_parameter`
- [ ] Check if any groups use `goal2_led` (SCREEN_LIGHT) for 2P mode
- [ ] Likely identical to LED Hex — run the level dump first to confirm

### Climb
- [ ] Inspect level data: is it walk-path (groups = sequential path segments)?
- [ ] Check `life_value_calculation.py` for any climb-specific scoring (combo, speed bonus)
- [ ] Square grid → `LedTable(led_row=16, led_col=26)` same as LED Hex mock
- [ ] Confirm `FLOOR_LIGHT` groups are the scoring zones (blue = goal?)
- [ ] DK series `.ledb` files → likely 2P mode, same as LED Hex DK levels

### Laser
- [ ] Confirm wall scoring: read `get_wall_light_state_array()` not `state_table`
- [ ] Map wall perimeter indices to physical button positions
- [ ] Check audio events (laser has `audio_play/` module) — hit/miss sounds
- [ ] Database module — scores written to DB directly in original code
- [ ] Test `apply_wall_input()` equivalent for button press

### Hoops
- [ ] Find how hoop sensor events enter the Python code (check all `game_hw.py` methods)
- [ ] Understand `WALL_LIGHT` layout — are hoops indexed 1–6 in the wall array?
- [ ] Simulate sensor event for testing (since no physical hoops in dev)
- [ ] Check `play_order` flag — hoops may use sequence-based mode
- [ ] Audio: cheer/buzz on score/miss

---

## Known decompile issues (per game, from source inspection)

| Game | Issue | Fix |
|---|---|---|
| All | `game_running.py` Tkinter import | Replace with LED Hex mock |
| All | `Play.running()` movement gating bug | Copy LED Hex's fixed Play.py |
| All | `goal_led_group_start_time_list()` append bug | Fixed in LED Hex Play.py |
| Laser | Named level IDs (`C01`, `B01`, `A001`) | `StartGameRequest.level: Union[int,str]` already handles this |
| Hoops | Hoop sensor input path unclear | Investigate game_hw.py deeply before starting |
| Climb | `get_g_wall_has_been_tread_arr2()` tread tracking | Verify mock LedTable implements this |

---

## Quick-start commands

```bash
# 1. Activate LED Hex env
cd /Users/apple/parallel-work/ledhexagon_clone

# 2. Test a game's source imports
python3 -c "
import sys
sys.path.insert(0, '/Users/apple/Desktop/activerse/battle arena/ledhexagon_py_source')
from game_play.Play import Play
from game_play.game_running import LedTable
print('imports OK')
"

# 3. Load a level
python3 << 'EOF'
import sys, zipfile, tempfile, shelve, os, glob
sys.path.insert(0, '/Users/apple/Desktop/activerse/climb/climb_py_source')
f = sorted(glob.glob('/Users/apple/Desktop/activerse/climb/ledplay/source/---/*.ledb'))[0]
with tempfile.TemporaryDirectory() as t:
    with zipfile.ZipFile(f) as z: z.extractall(t)
    for root,_,files in os.walk(t):
        if any(fi.startswith('game_file') for fi in files):
            db=shelve.open(os.path.join(root,'game_file'))
            dg=db.get('dict_group')
            from collections import Counter
            print(f, Counter(getattr(x,'type',None) for x in dg.values()))
            db.close(); break
EOF
```

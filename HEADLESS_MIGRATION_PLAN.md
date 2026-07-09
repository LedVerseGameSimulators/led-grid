# Floor Is Lava (Snake/Grid) → Headless API Migration Plan

**Raw .exe:** `/Users/apple/Downloads/wetransfer_ledplayv020505_2026-06-08_0522.zip`  
**Extracted to:** `/Users/apple/Desktop/activerse/floor_is_lava/raw/ledplayv020505/ledplay/`  
**Target repo:** `/Users/apple/activerse_final_changes/led-grid/`  
**Reference (working headless game):** `/Users/apple/activerse_final_changes/led-climb/`  
**Migration playbook:** `/Users/apple/activerse_final_changes/CLIMB_MIGRATION_PLAYBOOK.md`

---

## What this game is

LED floor game. **16×26 RECTANGULAR grid** of square tiles on the floor.  
Single RGB per cell (same as Climb, NOT 3-ring like LED-Hex simulator).  
"Floor is lava" / snake-style mechanics — avoid red lava, step blue safe tiles.

Two game variants inside same exe (confirmed by audio sub-folders):
- `audio/snake/` → snake-style levels (moving red lava patterns)
- `audio/tennes/` → tennis-style levels (different pattern behavior)

**IMPORTANT — `led_layout_type=6` means `RIGHT_DOWN_LEFT`**  
This is only the physical LED wiring order for serial hardware output.  
It does NOT affect the game grid shape — all games use rectangular grids.  
`led_layout_type` values across games:
- 0 = LEFT_TOP_RIGHT (Hoops)
- 1 = LEFT_TOP_DOWN (LED Hex)  
- 5 = LEFT_DOWN_UP (Climb)
- 6 = RIGHT_DOWN_LEFT (this game) ← same rectangular grid, different wiring

**Colors in use:**
- RED `(254,0,0)` — lava/hazard tiles (most common — ~60-70% of all tiles)
- BLUE `(0,0,254)` — scoreable tiles (step to score)
- GREEN `(0,254,0)` — safe platform (shields from lava)
- ORANGE `(254,128,0)` — scoreable 2P (---- series only)

**Grid:** `value_high=16`, `value_width=26` → 16 rows × 26 cols, rectangular  
**Session:** `game_time_sw=5.0` min, `life_value_sw=20`  
**Score divide:** `game_scode_divide_person=False`, `game_scode_divide_time=False`  
(No division — raw score is final score)

**Level series:**
| Series | Folder | Count | Type |
|--------|--------|-------|------|
| `-` | `source/-/` | 10 | 1P `.led` |
| `--` | `source/--/` | 15 | 1P `.led` |
| `---` | `source/---/` | 14 | 1P `.led` (hard) |
| `----` | `source/----/` | 13 | 2P `.ledb` |

---

## Step 1 — Extract PyInstaller .exe → .pyc files

The game source is inside `ledplay.exe` (PyInstaller bundle). Extract with `pyinstxtractor`:

```bash
pip3 install pyinstxtractor

cd /Users/apple/Desktop/activerse/floor_is_lava/raw/ledplayv020505/ledplay/

# Run on macOS targeting Windows exe (cross-platform extraction)
python3 -m pyinstxtractor ledplay.exe
# Output: ledplay.exe_extracted/
```

Expected output structure:
```
ledplay.exe_extracted/
├── PYZ-00.pyz_extracted/    ← all game .pyc files here
│   ├── game_play/
│   │   ├── Play.pyc
│   │   ├── game_running.pyc
│   │   ├── game_hw.pyc
│   │   ├── game_music.pyc
│   │   ├── game_util.pyc
│   │   └── life_value_calculation.pyc
│   ├── gui/
│   ├── gui2/
│   ├── model/
│   └── ...
└── struct.pyc
```

If pyinstxtractor fails on macOS for Windows exe, try:
```bash
pip3 install uncompyle6 decompile3
# Or use the already-extracted climb source as reference —
# model/setting.py is ALREADY uncompiled in the raw folder
```

---

## Step 2 — Decompile .pyc → .py

**Prefer Docker + pycdc (Decompyle++) over uncompyle6.**  
Same toolchain used for Climb/Hoops/Laser (`# Source Generated with Decompyle++` in `*_py_source` trees).  
uncompyle6 often fails on `Play.py` (`deal_all_direction` parse error); pycdc usually succeeds.

### Recommended: Docker pycdc (led-grid/scripts/)

Prerequisite: Step 1 extraction must use **Python 3.7** so the PYZ archive is fully extracted.

```bash
# One-time: builds activerse-pycdc image (~1 min first run)
cd /Users/apple/activerse_final_changes/led-grid
./scripts/decompile-pycdc.sh \
  /path/to/ledplay.exe_extracted/PYZ-00.pyz_extracted \
  /path/to/grid_py_source
```

Decompiles priority files: `Play.py`, `game_running.py`, `life_value_calculation.py`,  
`game_util.py`, `game_hw.py`, `game_music.py`.

Then apply Step 3 fixes to `Play.py` (see `led-climb/games/game_play/Play.py` for the rigid-bounce `deal_all_direction`).

**Headless note:** pycdc `game_running.py` may contain syntax errors (stray `:` etc.).  
The API does not use it — `game_manager.py` imports `Play` directly and uses `HeadlessLedTable`.  
Keep Climb's `game_running.py` or fix pycdc output manually if something else imports it.

### Fallback: uncompyle6 (bulk / non-critical modules)

```bash
pip3 install uncompyle6

cd /Users/apple/Desktop/activerse/floor_is_lava/

mkdir -p py_source

find raw/ledplayv020505/ledplay/ledplay.exe_extracted/PYZ-00.pyz_extracted \
  -name "*.pyc" | while read f; do
    rel="${f#raw/ledplayv020505/ledplay/ledplay.exe_extracted/PYZ-00.pyz_extracted/}"
    outdir="py_source/$(dirname $rel)"
    mkdir -p "$outdir"
    outfile="py_source/${rel%.pyc}.py"
    uncompyle6 -o "$outfile" "$f" 2>/dev/null || true
    echo "decompiled: $rel"
done
```

Use uncompyle6 for gui/model/led bulk trees; **always re-decompile `Play.py` with pycdc** if uncompyle6 reports parse errors.

**Model files already uncompiled** — copy directly:
```bash
cp -r raw/ledplayv020505/ledplay/model py_source/model
cp -r raw/ledplayv020505/ledplay/data py_source/data 2>/dev/null
```

### Priority files to decompile (game logic):
1. `game_play/Play.py` — main game loop (CRITICAL)
2. `game_play/game_running.py` — level orchestration  
3. `game_play/life_value_calculation.py` — scoring/life formula
4. `game_play/game_util.py` — level loading utilities
5. `model/setting.py` — constants (ALREADY UNCOMPILED ✓)
6. `net/net_socket.py` — UDP protocol (already seen in climb)

---

## Step 3 — Fix decompiler errors

Known decompiler bugs to fix immediately (same as Climb):

### Bug A — `Play.get_game_speed` UnboundLocalError
```python
# BROKEN (decompiler omits default):
def get_game_speed(self, game_level, leval_span):
    if game_level <= 1:
        game_level_speed = 1 - leval_span
        ...
    return game_level_speed  # ← UnboundLocalError if game_level > 1

# FIX:
def get_game_speed(self, game_level, leval_span):
    game_level_speed = 1  # ADD DEFAULT
    if game_level <= 1:
        ...
```

### Bug B — `deal_all_direction` erodes pattern width on bounce
```python
# BROKEN: drops out-of-bounds cells per frame
# FIX: rigid bounce — move whole pattern, reverse on edge hit
# (copy exact fix from led-climb/games/game_play/Play.py)
```

### Other common decompiler artifacts:
- `_iter_` variables in lambda comprehensions → fix manually
- Missing `elif` branches → restore from logic context
- Indentation errors around nested `if/elif/else`

---

## Step 4 — Create repo structure

```bash
cp -r /Users/apple/activerse_final_changes/led-climb \
      /Users/apple/activerse_final_changes/led-grid

cd /Users/apple/activerse_final_changes/led-grid
git checkout -b main
# strip old commits — fresh start
```

Or create fresh and copy selectively:
```bash
mkdir -p /Users/apple/activerse_final_changes/led-grid
# Copy API skeleton from climb (same structure)
cp -r /Users/apple/activerse_final_changes/led-climb/api led-grid/
cp -r /Users/apple/activerse_final_changes/led-climb/frontend led-grid/
cp    /Users/apple/activerse_final_changes/led-climb/ws_bridge.py led-grid/
cp -r /Users/apple/activerse_final_changes/led-climb/simulator led-grid/
```

Then copy game source:
```bash
cp -r /Users/apple/Desktop/activerse/floor_is_lava/py_source/* \
      /Users/apple/activerse_final_changes/led-grid/games/

# Copy level data + settings (already uncompiled)
cp -r /Users/apple/Desktop/activerse/floor_is_lava/raw/ledplayv020505/ledplay/source \
      /Users/apple/activerse_final_changes/led-grid/games/
cp -r /Users/apple/Desktop/activerse/floor_is_lava/raw/ledplayv020505/ledplay/setting \
      /Users/apple/activerse_final_changes/led-grid/games/
```

---

## Step 5 — Adapt `api/config.py`

```python
GAME_NAME = "grid"   # or "floor_is_lava"
_REPO_ROOT = Path(__file__).resolve().parent.parent
GAMES_ROOT = Path(os.getenv("GAMES_ROOT", str(_REPO_ROOT / "games")))
API_PORT = int(os.getenv("API_PORT", 8004))  # next free port after laser :8003
```

---

## Step 6 — Adapt `api/game_manager.py`

Key differences from Climb:

### Grid dimensions
```python
# value_high=16, value_width=26 → 16×26 RECTANGULAR (same engine as Climb)
# led_layout_type=6 = RIGHT_DOWN_LEFT — hardware wiring only, ignore for headless
# Single RGB per cell (same as Climb)
```

### Color classification
```python
# From level data analysis:
# RED   (254,0,0)   → hazard (lava) — most tiles in most levels
# BLUE  (0,0,254)   → scoreable (+1 on step)
# GREEN (0,254,0)   → safe platform (shields red damage)
# ORANGE (254,128,0) → scoreable 2P (---- series)
#
# Priority: green(3) > red(2) > blue/orange(1)  [same as Climb]
```

### Score division
```python
# game_scode_divide_person = False
# game_scode_divide_time   = False
# → NO division. final_score = raw_score
def compute_final_score(self, raw_score):
    return float(raw_score)
```

### Level series + naming
```python
BUCKETS = [
    ("easy",   "source/-/*.led",    False, "led"),
    ("medium", "source/--/*.led",   False, "led"),
    ("hard",   "source/---/*.led",  False, "led"),
    ("2player","source/----/*.ledb", True, "ledb"),
]
```

### Multiplayer detection
`----` series uses `.ledb` AND has orange tiles. Same detection as Climb:
```python
has_blue   = any(mc == (0,0,254)    for g in dg.values())
has_orange = any(mc == (254,128,0)  for g in dg.values())
if has_blue and has_orange:
    game.multiplayer = True
```

### Module mocks (same as Climb — copy entire block)
All same external deps: tkinter, serial, pygame, led, net, encryption, gui2, etc.

---

## Step 7 — Adapt `api/main.py` levels endpoint

```python
@app.get("/levels")
async def get_levels():
    BUCKETS = [
        ("easy",    os.path.join(src, "source", "-",    "*.led"),   False, "led"),
        ("medium",  os.path.join(src, "source", "--",   "*.led"),   False, "led"),
        ("hard",    os.path.join(src, "source", "---",  "*.led"),   False, "led"),
        ("2player", os.path.join(src, "source", "----", "*.ledb"),  True,  "ledb"),
    ]
    ...
```

---

## Step 8 — Adapt `simulator/static/index.html`

Grid = **16×26 RECTANGULAR square tiles, single RGB per cell**.  
Same format as Climb — copy Climb's square-grid simulator, update dimensions:

```bash
cp /Users/apple/activerse_final_changes/led-climb/simulator/static/index.html \
   /Users/apple/activerse_final_changes/led-grid/simulator/static/index.html
```

Change defaults at top of JS:
```javascript
let ROWS = 16, COLS = 26;  // was 6x33 for Climb
```

Update title: `Climb Floor Simulator` → `Floor Is Lava Simulator`

---

## Step 9 — Adapt `ws_bridge.py`

Rectangular single-color. Copy Climb's ws_bridge format exactly:
```python
rows = int(game_state.get("grid_rows", 16))
cols = int(game_state.get("grid_cols", 26))
# single [r,g,b] per cell — same as Climb
```

---

## Step 10 — Adapt frontend

Update `frontend/src/App.jsx`:
```javascript
game: 'grid',
level: '001',  // first level in - series
```

Update `frontend/src/screens/GameSettingsScreen.jsx`:
```javascript
const CAT_LABEL = {
  'easy':    { label: 'Easy',     desc: '001-010 (1P)' },
  'medium':  { label: 'Medium',   desc: '002-015 (1P)' },
  'hard':    { label: 'Hard',     desc: '001-014 HARD (1P)' },
  '2player': { label: '2-Player', desc: '01-05 (2P)' },
}
```

---

## Step 11 — Add to start-all-games.sh

```bash
start_stack "Floor Is Lava" led-grid 8004 8769 5177
```

---

## Game mechanics (from level data + model/setting.py)

**Session marathon** (same as Climb):
- 5-min session timer spans all levels
- Score + 20 lives persist across levels
- Clear level → auto-advance to next
- Within-level: auto-jump between time-staggered waves
- life=0 → session ends

**Scoring:**
- BLUE tile step → +1 score (consume tile)
- RED tile stand → -1 life every 1.2s (time-gated, `life_value_count_time`)
- GREEN tile → safe platform, shields from red, not scoreable
- ORANGE tile (2P ---- series) → +1 score P2
- No score division (raw = final)

**Priority overlap:** green > red > blue/orange (same logic as Climb)

**Bounce:** Rigid bounce — preserve full pattern width (same fix as Climb)

---

## Files already uncompiled (no decompilation needed)

```
games/model/setting.py   ✓ uncompiled in raw
games/model/game.py      ✓ uncompiled in raw
games/model/group.py     ✓ uncompiled in raw
```

---

## Known gaps / things to verify

1. **Play.py** — may differ from Climb. Check `__init__` signature. Climb needs `(obj_led_table, setting, partial_fun_cb, game_level)`.
2. **game_running.py** — check which `Play.running*` method it calls (`running`, `running_by_blue`, or `running_new`).
3. **life_value_calculation.py** — verify `ONE_LIFE_VALUE`, `ONE_SCODE_VALUE` constants.
4. **3-ring vs single-color** — verify `group.color` format for this game. LED-Hex uses 3-ring; Climb uses single. Check first group's color in levels: if `isinstance(g.color[0], (list,tuple))` → 3-ring.
5. **`----` 2P series** — verify orange color value: may be `(254,128,0)` or different.

---

## Testing steps (in order)

```bash
# 1. API starts
cd /Users/apple/activerse_final_changes/led-grid
python3 -m api.main
curl http://localhost:8004/health
# expect: { status: ok, game: grid }

# 2. Levels load
curl http://localhost:8004/levels
# expect: 52 total levels across 4 categories

# 3. Start game
curl -X POST http://localhost:8004/start-game \
  -d '{"card_id":"t","level":"001","difficulty":"normal"}'
# expect: game_id returned

# 4. Game state has data
sleep 3
curl http://localhost:8004/game-state
# expect: grid_rows=16, grid_cols=26, lit cells > 0, life=20

# 5. WS bridge
python3 ws_bridge.py  # separate terminal
# check: ws frame has rows=16, cols=26

# 6. Frontend
cd frontend && npm run dev
# open localhost:5177
# verify: hex grid renders, tiles visible

# 7. Press blue tile → score increases
# 8. Press red tile → life decreases
# 9. Press all blue tiles → level advances to next
# 10. Life = 0 → session ends
```

---

## Start prompt for new agent

You are migrating the "Floor Is Lava" LED floor game from a Windows `.exe` to a headless FastAPI + React web app.

**Read first (in order):**
1. `/Users/apple/Desktop/activerse/floor_is_lava/HEADLESS_MIGRATION_PLAN.md` — this file, full spec
2. `/Users/apple/activerse_final_changes/CLIMB_MIGRATION_PLAYBOOK.md` — proven migration pattern used for all games
3. `/Users/apple/activerse_final_changes/led-climb/api/game_manager.py` — reference implementation to adapt
4. `/Users/apple/activerse_final_changes/led-climb/games/game_play/Play.py` — reference Play.py with known fixes

**Raw game files:**
- Extracted exe: `/Users/apple/Desktop/activerse/floor_is_lava/raw/ledplayv020505/ledplay/`
- Model (already uncompiled): `raw/ledplayv020505/ledplay/model/setting.py`
- Levels: `raw/ledplayv020505/ledplay/source/{-,--,---,----}/`
- Settings: `raw/ledplayv020505/ledplay/setting/led_parameter`

**Target repo:** `/Users/apple/activerse_final_changes/led-grid/`  
**API port:** 8004. **WS port:** 8769. **UI port:** 5177.

**Key facts (do not deviate):**
1. Grid = 16×26 RECTANGULAR square tiles, SINGLE RGB per cell (same format as Climb, NOT 3-ring)
2. `led_layout_type=6` = hardware wiring direction only — does NOT mean hexagon. All games are rectangular.
3. Colors: RED=lava/hazard, BLUE=score, GREEN=safe/shield, ORANGE=score 2P
4. Priority: green > red > blue/orange (same as Climb)
5. No score division (raw = final — both divide flags are False)
6. 4 level series: `-`(easy/10), `--`(medium/15), `---`(hard/14), `----`(2P/13)
7. Session marathon: 5-min, 20 lives, score+life persist across levels
8. Simulator HTML: copy from **led-climb** (square grid, single color) — update ROWS=16, COLS=26
9. ws_bridge: copy from led-climb (single rgb format)
10. Same module mocks as Climb (tkinter, serial, pygame, led, net, etc.)
11. Same decompiler bugs to fix: get_game_speed default + deal_all_direction bounce

**Build order:**
1. Extract .pyc from ledplay.exe using pyinstxtractor (**Python 3.7** for full PYZ)
2. Decompile .pyc → .py using **Docker pycdc** (`led-grid/scripts/decompile-pycdc.sh`)
3. Fix decompiler bugs in Play.py (get_game_speed + deal_all_direction)
4. Create led-grid/ repo (copy led-climb as base)
5. Copy decompiled source + level data into games/
6. Adapt api/config.py (port=8004, game_name=grid)
7. Adapt api/game_manager.py (grid dims 16x26, single RGB, color classification, no score division)
8. Adapt api/main.py (levels endpoint, 4 series)
9. Copy Climb simulator HTML, update ROWS=16 COLS=26, update title
10. Adapt ws_bridge.py (16x26, single RGB format)
11. Adapt frontend (game=grid, 4 categories)
12. Run all 10 test steps

**Do not use Vercel, Next.js, or cloud. Local LAN Python/React app.**  
**Test after each step. Commit working state before moving to next step.**

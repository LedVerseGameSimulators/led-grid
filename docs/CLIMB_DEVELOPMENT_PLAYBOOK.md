# Climb — Development Playbook & Status

**Last updated:** 2026-06-07  
**Repo:** `/Users/apple/activerse_final_changes/led-climb`  
**Original source:** `climb/ledplay/` (decompiled under `games/`)  
**Migration reference:** `../CLIMB_MIGRATION_PLAYBOOK.md` (parent repo), `../led-hoops/docs/HOOPS_DEVELOPMENT_PLAYBOOK.md`

---

## What this game is

LED **square floor** climbing game — **6 rows × 33 columns**. Single RGB per cell (not hex, not 3-ring).

| Mode | Behavior |
|------|----------|
| **1P (A/B series)** | Step scoreable colors (blue, orange, yellow, cyan, magenta, white) → +1 |
| **2P (DK `.ledb`)** | P1 = blue `(0,0,254)`, P2 = orange `(254,128,0)` |
| **Hazards** | RED → −1 score + −1 HP while standing (rate-limited ~1.2s) |
| **Safe** | GREEN shields from red (non-scoring) |
| **DEDUCT** | `(254,0,48)` → −1 score, consume tile (no extra life loss in faithful impl) |
| **Session** | 5-min marathon through level series; score + lives persist |

Headless stack: **simulator + API**. Hardware drivers exist under `games/` but are **not wired** into `api/game_manager.py`.

---

## Status at a glance

| Area | Status |
|------|--------|
| Headless API + `Play.running()` loop | ✅ Done |
| Square grid simulator (6×33) | ✅ Done |
| A-series / B-series / DK levels | ✅ Done |
| Session marathon + level progression | ✅ Done |
| Priority overlap (green > red > goal) | ✅ Done |
| Moving pattern rigid bounce fix | ✅ Done |
| 2P DK scoring + respawn (~8s) | ✅ Done |
| Parallel ports (8001 / 8766 / 5174) | ✅ Done |
| Hardware serial (3 COM ports on real install) | ⏳ Pending — code exists |
| Sensor input from floor | ⏳ Pending |
| RFID / MySQL prod login | ⚠️ Partial |
| Audio / video | ⏳ Mocked |

---

## Architecture

```
led-climb/
├── api/
│   ├── main.py
│   ├── game_manager.py      # Session loop, HeadlessLedTable, scoring
│   └── config.py            # API_PORT=8001
├── games/
│   ├── game_play/Play.py    # MODIFIED — get_game_speed, deal_all_direction
│   ├── led/                 # Serial drivers (not used by API)
│   ├── game_play/game_hw.py
│   ├── source/
│   │   ├── -/               # A-series 1P (*.led)
│   │   ├── --/              # B-series 1P (*.led)
│   │   └── ---/             # DK-series 2P (*.ledb)
│   └── setting/             # led_parameter (6×33, multi-COM)
├── frontend/                # React — Climb-branded selection UI
├── simulator/static/        # Square grid canvas
├── ws_bridge.py
└── scripts/start-dev.sh
```

### Data flow (simulator — today)

```
React → /start-game → GameManager → Play.running()
    → frame callback → led_display [R,G,B] per cell
    → /game-state → ws_bridge → square simulator
    → click tile → /game-input → press_cell → try_score_cell
```

### Data flow (hardware — future)

Same as Hex/Hoops pattern: `GameHW` + `led_control.init_com` (possibly **3 COM ports** for Climb) → read `state_table` → score → `draw_screen_by_com`.

Example shelve config (machine-specific):

```
list_com_info = [
  ['COM3', '81', '132', 'floor_light'],
  ['COM4', '1', '48', 'floor_light'],
  ['COM5', '49', '80', 'floor_light'],
]
value_high=6, value_width=33
```

---

## Run locally

```bash
cd led-climb
./scripts/start-dev.sh
```

| Service | Port |
|---------|------|
| Frontend | 5174 |
| API | 8001 |
| ws_bridge | 8766 |

Parallel with Hoops (8000/8765/5173) and Hex (8002/8767/5175).

---

## What has been done

### Migration & core loop
- [x] Headless FastAPI decoupled from Tkinter
- [x] `HeadlessLedTable` (6×33 square grid)
- [x] Full dependency mocks in `game_manager.py`
- [x] Real settings from `games/setting/led_parameter`
- [x] Level load: `.led` / `.ledb` ZIP → shelve

### Gameplay fidelity
- [x] `Play.py` decompiler fixes (`get_game_speed`, rigid-bounce `deal_all_direction`)
- [x] Session marathon (A001→… / B01→… / DK01→… from chosen start)
- [x] Priority overlap resolution — moving red cannot permanently block blue
- [x] Goal-color scoring, red penalty, deduct tiles
- [x] Green = safe / non-scoring
- [x] Wave auto-skip when scoreable wave cleared
- [x] 2P: `.ledb` + blue/orange detection, separate scores, respawn delay
- [x] Board result codes (lose / win / timeout)

### Frontend & dev
- [x] Climb-only game selection + branded screens
- [x] `frontend/src/config.js` centralized URLs
- [x] `scripts/start-dev.sh` dedicated ports
- [x] `.gitignore` for `*.rar` archives

### Git milestones
| Commit | Summary |
|--------|---------|
| `212174d` | Overlap priority + moving-pattern bounce |
| `4ca1bdb` | Session marathon + scoring fidelity |
| `a88a17a` | Progression, 2P scoring, green non-scoring |
| `c8ca4a6` | Parallel dev ports + Climb UI |
| `161551d` | Ignore source `.rar` |

---

## Pending checklist

### P0 — Before hardware floor test
- [ ] Confirm **3-COM layout** matches venue wiring (indices 1–132 split across ports)
- [ ] Stand-on-tile scoring vs momentary — Climb uses **held** state for red drain; verify sensor hold behavior
- [ ] USB dongle / `yanqian()` on Windows kiosk
- [ ] `com_is_block` tuning — blocking reads can stall loop with 3 ports

### P1 — Hardware integration
- [ ] Hardware mode or sidecar bridge (see `HARDWARE_MODE.md`)
- [ ] `led_control.init_com` + `init_layout` for **square** layout type (not hex serpentine)
- [ ] Per-frame: read sensors → `state_table`, write `led_table` → serial
- [ ] I/O driver abstraction (`SimDriver` / `HardwareDriver`) — see `ROADMAP.md` Phase 2
- [ ] On-site: tile index ↔ (row,col) calibration

### P2 — Kiosk / production
- [ ] Fix hardcoded `_SCORES_DB` path in `api/database.py`
- [ ] MySQL player lookup for RFID
- [ ] RFID wedge on LoginScreen
- [ ] Production start script / env docs

### P3 — Polish
- [ ] Real MP3 audio (optional)
- [ ] Hidden-tile / cover_action prompt mode (if levels need it)
- [ ] End-fragments (`game_accomplished`, `clap_light`) — see `GAPS.md`
- [ ] Automated API smoke tests
- [ ] Frontend: send `player_count` for 2P (may lag Hoops — verify SimulatorScreen)

### P4 — Later
- [ ] Wall / screen LEDs (if enabled in settings)
- [ ] Original Tkinter admin GUI

---

## How to continue development

### Quick-start

```bash
cd /Users/apple/activerse_final_changes/led-climb
./scripts/start-dev.sh
# http://localhost:5174
```

### Level buckets (`/levels`)

| Category | Path | 2P |
|----------|------|-----|
| `a-series` | `source/-/*.led` | No |
| `b-series` | `source/--/*.led` | No |
| `dk-series` | `source/---/*.ledb` | Yes |

### Gameplay changes

1. Compare with `games/gui/gui_editor_game.py` (`calculation_editor_group_scode`).
2. Edit `api/game_manager.py` frame callback — not `Play.py` unless movement bug.
3. Restart API on `:8001`.

### Hardware path

Original stack in `games/led/`, `games/game_play/game_hw.py` — same pattern as Hex/Hoops. Climb-specific: **square grid**, often **multiple COM ports**, **step-and-hold** input (not hoop momentary press).

Do not remove API mocks until hardware path is tested.

---

## Key files

| File | Role |
|------|------|
| `api/game_manager.py` | Session loop, overlap priority, scoring |
| `games/game_play/Play.py` | Movement, bounce |
| `simulator/static/index.html` | Square grid UI |
| `games/led/led_control.py` | Future serial I/O |
| `../CLIMB_MIGRATION_PLAYBOOK.md` | Step-by-step migration history |

---

## Related docs (this repo)

| Doc | Purpose |
|-----|---------|
| `HARDWARE_MODE.md` | I/O-agnostic design, driver abstraction |
| `STATUS_HARDWARE.md` | Hex-oriented hardware steps (adapt grid to 6×33) |
| `GAPS.md` | Verified vs unverified mechanics |
| `ROADMAP.md` | Phased implementation plan |
| `SETTINGS.md` | Shelve field reference (partially outdated — see playbook status) |

---

*Update this document when closing pending items.*

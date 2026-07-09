# LED Hex — Implementation Status & Hardware Deployment

> **Hex playbook (sim + pending):** [`../led-hexagon/docs/LED_HEX_DEVELOPMENT_PLAYBOOK.md`](../led-hexagon/docs/LED_HEX_DEVELOPMENT_PLAYBOOK.md)  
> **Climb hardware notes:** 6×33 square grid, often **3 COM ports** — adapt Step 1–3 grid/COM values in [`CLIMB_DEVELOPMENT_PLAYBOOK.md`](./CLIMB_DEVELOPMENT_PLAYBOOK.md).

**Last updated:** 2026-06-07
**Overall completion:** ~90% (simulator fully functional; hardware I/O layer pending)

---

## Implementation Status

### Completed

| Area | Detail |
|------|--------|
| Game loop | Full headless loop via `Play.running()` — real patterns, movement, 3-ring colors, breath shimmer |
| Scoring | Goal-color scoring with type awareness: goal tile +1/consume, red tile -1/-1HP, DEDUCT tile -1/-1HP/consume, decor neutral |
| 2-player mode | `.ledb` file support — P1/P2 goal indicators, separate scores, checkerboard split for same-color levels |
| Level library | 67 levels across 4 categories: extra / basic / advanced / pro |
| HP system | 20 life, 300s session, board result codes: 0=lose / 1=win / 2=timeout |
| 2P tile respawn | 8-second delay for `.ledb` multiplayer levels |
| Leaderboard | `hex_scores` table in `ledplaydb.sqlite`; per-level top scores shown on result screen |
| Browser audio | Synth beeps: ding on score event, buzz on HP loss |
| Countdown screen | 3-2-1-GO sequence before game start |
| Resume on reload | `/active-game` endpoint restores in-progress session |
| Settings | Loaded from `led_parameter` shelve: `game_time=300s`, `life=20`, etc. |
| React UI | Full flow: game select → settings → 1P/2P login → countdown → simulator → result |

---

## Known Gaps (Low Priority)

These are intentionally deferred and do not block normal simulator gameplay.

- **No MP3 audio** — synth beeps only; real audio files reference Windows absolute paths and are not portable
- **No intro / idle / countdown video** — video playback not wired up
- **No hidden-tile prompt mechanic** — `safe_color` reveal-at-cost feature not implemented
- **No wall/screen LED outputs** — disabled in all current levels; physical wall panels not targeted
- **No barcode/RFID session time credit** — hardware readers not integrated
- **No true 2P multiplayer** — `.ledb` 2P levels run on one machine only; separate-player-session multiplayer not implemented

---

## Hardware Deployment Steps

### Step 1 — Serial Port Initialization

**Goal:** Open COM ports to the floor LED/sensor hardware before the game loop starts.

1. Read `list_com_info` from the `led_parameter` shelve.
   - Expected format: `[['COM_name', start_idx, end_idx, normal_led], ...]`
   - Example entry: `['COM9', 0, 67, 1]`
2. Call `led_control.init_com(list_com_info)` — opens each port via pyserial at 115200 baud, 0.3s timeout.
3. Call `led_control.init_layout(layout_type, 16, 26, floor_layout_coors_no_use)` — builds `rect_position_arr`, the serpentine mapping table from grid coordinates to physical tile order.
4. **Calibration check:** Confirm that COM port names in `led_parameter` match the actual USB-serial adapter assignments on the floor PC. On Windows these are `COM9`, `COM10`, etc.; on Linux/Mac they will be `/dev/ttyUSB0`, `/dev/ttyUSB1`, etc.

---

### Step 2 — LED Output (PC → Physical Floor)

**Goal:** Drive real floor tiles with the same `led_display` data the simulator already produces.

**Wire protocol:**
- Frame header: `[255, 255]`
- Per tile: 9 bytes — 3 rings × RGB (R, G, B), rings sent **outer → mid → inner**
- Tiles are written in **reversed physical order** as determined by `rect_position_arr`

**Implementation task — `HardwareDriver.write_output(led_display)`:**

```python
def write_output(self, led_display):
    # led_display[i*26 + j] = [[R0,G0,B0], [R1,G1,B1], [R2,G2,B2]]
    # Maps 1:1 to the 3 physical LEDs (outer/mid/inner) per hex tile
    frame = [255, 255]
    for phys_idx in reversed(rect_position_arr):
        tile = led_display[phys_idx]
        for ring in tile:          # outer → mid → inner
            frame.extend(ring)     # R, G, B
    com_port.write(bytes(frame))
```

- Use `rect_position_arr` to translate logical grid index to physical serial order.
- Verify ring order (outer/mid/inner) matches physical tile construction on-site.

---

### Step 3 — Sensor Input (Floor → PC)

**Goal:** Read hex tile press events from the floor sensors and feed them into the game loop.

**Wire protocol:**
- 3 bytes per sensor
- `byte == 0x0A` (decimal 10) = tile pressed
- `0xFC` frames/delimits packets

**Implementation requirements:**

1. Call `led_control.read(com, state_table, start_num, read_size, block=False)` with **`block=False`** and a short timeout to avoid a 0.3s-per-port stall on every game loop iteration.
2. **Known decompiled bug:** There is a suspected reverse-indexing error in `read()` around line ~202. This must be tested against real hardware and corrected before go-live. The symptom would be sensor presses registering on the wrong tile.
3. `scored_active` edge-trigger logic already handles sensor debounce — repeated reads of a held tile will not double-score.

---

### Step 4 — I/O Driver Abstraction

**Goal:** Keep `game_manager` clean and swappable between simulator and hardware without logic duplication.

**Interface contract:**

```python
class Driver:
    def read_input(self, state_table) -> state_table: ...
    def write_output(self, led_display): ...
```

**Implementations:**

| Driver | Input source | Output destination |
|--------|--------------|--------------------|
| `SimDriver` | Click events via `/game-input` API | `led_display` → API → `ws_bridge` → browser |
| `HardwareDriver` | `led_control.read()` via serial | `led_control.write()` via serial |

**Integration point:** In `game_manager._run_game`, replace direct I/O calls with `self.driver.read_input(...)` and `self.driver.write_output(...)`. The driver is selected at startup based on `USE_SERIAL_HD`.

---

### Step 5 — On-Site Calibration Checklist

Run through this checklist at the venue before opening to players.

- [ ] **COM port names** — confirm Windows port assignments (`COM9`, etc.) match `led_parameter` values; reassign if USB hubs differ from dev machine
- [ ] **Layout type** — verify `layout_type` value (serpentine direction) matches physical wire routing direction on the floor
- [ ] **Dead cells** — confirm `floor_layout_coors_no_use` covers all physically missing or inactive tiles
- [ ] **Ring color order** — send a known test pattern and visually confirm outer/mid/inner ring order matches physical tile construction
- [ ] **Sensor mapping** — step on individual tiles and confirm the correct logical grid cell registers a press (tests the `read()` reverse-index fix from Step 3)
- [ ] **Sweep speed** — tune `game_level_speed` so pattern sweep feels natural at full floor scale; simulator speed may feel too fast on the large physical grid
- [ ] **Sensor debounce** — hold a tile and confirm it does not continuously re-score; `scored_active` edge-trigger should prevent this but verify under real hardware timing

---

### Step 6 — Enable Hardware Mode

**Option A — Code constant (simple):**

Edit `model/setting.py`:

```python
USE_SERIAL_HD = True   # was False
```

**Option B — Runtime config (preferred for flexibility):**

Read the flag from an environment variable or from a field in the `led_parameter` shelve at startup:

```python
import os
USE_SERIAL_HD = os.environ.get("USE_SERIAL_HD", "0") == "1"
# or: led_parameter["use_serial_hd"]
```

This allows switching between simulator and hardware mode without a code change — useful for testing at the venue before cabling is finalized.

---

## Architecture Notes

### Driver Swap Pattern

The core game loop in `game_manager` should never reference `SimDriver` or `HardwareDriver` directly. The driver is injected at construction time:

```
GameManager(driver=SimDriver())    ← development / CI
GameManager(driver=HardwareDriver())  ← on-site deployment
```

### Data Flow (Simulator)

```
Browser click → POST /game-input
    → game_manager.handle_input()
    → game loop tick
    → led_display updated
    → GET /game-state
    → ws_bridge pushes frame
    → React simulator renders tiles
```

### Data Flow (Hardware)

```
Floor sensor press → serial read
    → HardwareDriver.read_input()
    → game_manager.handle_input()
    → game loop tick
    → led_display updated
    → HardwareDriver.write_output()
    → serial write → physical floor LEDs
```

### Key Files

| File | Role |
|------|------|
| `api/game_manager.py` | Core game loop, scoring, state management |
| `api/main.py` | FastAPI routes, WebSocket bridge integration |
| `ws_bridge.py` | WebSocket relay: API → browser |
| `model/setting.py` | `USE_SERIAL_HD` flag and all tunable constants |
| `led_parameter` (shelve) | Runtime config loaded from Windows game install: COM ports, game_time, life, layout |
| `led_control` (external) | Decompiled pyserial wrapper — `init_com`, `init_layout`, `read`, `write` |

### Threading / Timing Notes

- The game loop runs at fixed tick rate; serial reads must be non-blocking (`block=False`) to avoid frame drops.
- Each COM port adds up to 0.3s latency if `read()` blocks — with multiple ports this stacks and will break real-time feel.
- `rect_position_arr` is built once at `init_layout` time and reused every frame; do not rebuild per-tick.

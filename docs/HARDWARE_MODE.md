# Will the headless impl work on the real LED floor?

> **Per-game playbooks:** [Climb](./CLIMB_DEVELOPMENT_PLAYBOOK.md) · [Hex](../led-hexagon/docs/LED_HEX_DEVELOPMENT_PLAYBOOK.md) · [Hoops](../led-hoops/docs/HOOPS_DEVELOPMENT_PLAYBOOK.md)

Short answer: **yes, mostly** — the game logic is I/O-agnostic. It operates on
two arrays:

- `state_table[row][col]` — input (1 = tile pressed)
- the LED display buffer — output (per-cell colors)

In **sim mode** today:
- input = simulator click → `/game-input` → `led_table.press_cell` → `state_table`
- output = `led_display` (built each frame) → API state → ws_bridge → canvas

In **hardware mode** the SAME logic runs; only the I/O source/sink changes:
- input = `led_control.read(com, state_table, …)` fills `state_table` from floor sensors
- output = `led_display` → `led_control` serial → physical LEDs

The decompiled hardware hooks already exist (gated by `Setting.USE_SERIAL_HD`):
- `led_control.init_com(list_com_info)` — open serial ports
- `led_control.init_layout(type, 16, 26, no_use_coords)` — map grid ↔ physical LEDs
- `led_control.read(com, state_table, start_num, read_size)` — sensors → state_table
- `game_hw.GameHW` — wraps init/draw/read for floor + wall + screen

## What already fits (no change)

- ✅ **Game logic** — scoring, movement, breath, consume, HP, time, goal-color.
  All read/write `state_table` + display buffer. Source of input and sink of
  output don't matter to it.
- ✅ **Separate display buffer** — we deliberately keep `led_table` static for
  scoring and build `led_display` (with breath/flash) separately. On hardware,
  send `led_display` to the LEDs — effects show on the physical floor.
- ✅ **state_table as the input contract** — sensors fill the same array clicks do.
- ✅ **Settings already read from `led_parameter`** (COM ports, layout live there).

## What must be ADDED for hardware (the I/O bridge)

1. **Init (on USE_SERIAL_HD=True)**: at game start call
   `led_control.init_com(setting.list_com_info)` +
   `led_control.init_layout(led_layout_type, 16, 26, floor_layout_coors_no_use)`.
2. **Per-frame input**: in the run-loop callback, call
   `led_control.read(com, state_table, start, size)` to refresh `state_table`
   from sensors — replaces the click-driven `apply_input`.
3. **Per-frame output**: push `led_display` to the LED serial each frame
   (the original used `draw_hw_led_color_inc_wal(led_table)`; we point it at our
   display buffer so breath/flash render on the floor).
4. **Toggle**: flip `Setting.USE_SERIAL_HD = True` (currently False for sim).

## Recommended design: an I/O driver abstraction

Keep the game loop unchanged; inject a driver that does input+output:

```
loop frame:
    driver.read_input(state_table)      # sim: no-op (clicks async) | hw: led_control.read
    play.update(...)                    # game logic (unchanged)
    build led_display (breath/flash)    # unchanged
    driver.write_output(led_display)    # sim: ws_bridge/API | hw: led_control serial
```

- **SimDriver** (today): input via `/game-input`, output via API→ws_bridge→canvas.
- **HardwareDriver**: input via `led_control.read`, output via `led_control` serial.
- **Both** can run together: drive the physical floor AND mirror to the React
  operator console (login/level/score still on a screen).

Because input is `state_table` and output is the display buffer, swapping drivers
is localized to `game_manager._run_game` — the rest is untouched.

## Risks / unknowns to verify on real hardware

- **3-ring → physical LEDs**: each hex tile has 3 concentric rings. Confirm the
  floor has 3 LEDs/tile (or how rings map). `led_control.init_layout` + the
  color-send routine handle this; verify the byte format.
- **Coordinate mapping**: `list_com_info` = `['COM9','1','33','normal_led']`
  (port, start index, count, type). Confirm sensor index ↔ (row,col) and
  LED index ↔ (row,col) match our 16×26 grid + `floor_layout_coors_no_use`.
- **Serial throughput / pacing**: 416 cells × RGB per frame over serial. The
  original paced via blocking serial (`com_is_block=True`). Our tight
  `running()` loop + `sleep(0.01)` may need retuning to serial latency.
- **Sensor debounce**: real floor sensors may need debounce; our edge-trigger
  scoring (`scored_active`) already handles repeat reads, but verify.
- **Wall / screen LEDs**: off in our levels (`wall_light/screen=False`), but the
  driver should init them if a level enables them.

## Bottom line

The architecture was built the right way for this: **logic decoupled from I/O**,
input as `state_table`, output as a display buffer. Going to hardware = writing
one `HardwareDriver` (serial read → state_table, display buffer → serial) and
flipping `USE_SERIAL_HD`. No game-logic rewrite. Main on-site work is
calibration: COM ports, coordinate mapping, ring→LED format, and pacing.

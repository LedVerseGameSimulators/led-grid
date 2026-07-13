# Hardware Validation — LED Grid (Floor Is Lava)

> **Status: NOT YET VALIDATED ON REAL HARDWARE.** This is a first-time
> hardware test for this game. Read this whole document before the onsite
> session — see "Why this is different from Hoops/Climb" below.

---

## 1. What hardware integration exists

- **Floor size:** 16 rows × 26 cols (416 tiles) — the largest floor of the 5
  games.
- **COM ports:** 3 (per `HARDWARE_INTEGRATION_PLAN.md`'s Grid section —
  `Grid: 16×26 · COM: 3 ports · Layout: 6 · Protocol: 3 bytes/tile`).
  `init_com` distributes the floor across the 3 ports automatically; each
  port drives roughly a third of the 416 tiles.
- **Layout type:** 6 (read from the `led_parameter` shelve at runtime — see
  `ONSITE.md` Step 4 to confirm the actual value on this machine).
- **Mechanism** (`api/game_manager.py`):
  - `USE_SERIAL_HD` — env var gate (`os.environ.get("USE_SERIAL_HD", "0") ==
    "1"`). When unset/`0`, the game runs fully headless/simulator-only; the
    hardware driver module (`led.led_control`) is mocked out and never
    imported.
  - `_hw_init()` — lazily imports the real `led.led_control`, opens the
    `led_parameter` shelve (read-only) for COM port list / layout type /
    grid dimensions, calls `_lc.init_layout(...)` and `_lc.init_com(...)`,
    and sets non-blocking serial timeouts. Runs once per process, gated by
    `_hw_led_control is not None`.
  - `_hw_draw_floor(layout_type, led_2d)` — per-frame draw call, sends the
    current `led_display` buffer to the floor via
    `_hw_led_control.draw_screen_by_com(layout_type, safe)`. Called from the
    frame callback at `_HW_DRAW_INTERVAL` (~45ms / ~22fps, tuned for the
    ~80-150ms full-floor serial write time across 3 ports).
  - `_hw_read_sensors(...)` — reads pressure/step sensor state from the
    floor (`update_screen_state_by_com`), used to detect tile presses.
  - `_hw_blank_floor(led_table)` — **new in this pass** — sends one
    all-`[0,0,0]` frame via the same `_hw_draw_floor` call. Added at every
    session-end / stop / clear_all() path (see "Blank-on-stop fix" below).
    Not yet exercised on real hardware.
  - All serial I/O is serialized through a single `_hw_serial_lock`
    (module-level `threading.Lock()`) — only the game thread touches COM
    ports.

## 2. Validation history

**This is a first-time real-hardware test.** Unlike led-hoops and
led-climb — which each have a documented on-site hardware pass (see
`led-hoops/WINDOWS_HARDWARE_INTEGRATION.md` and the equivalent for Climb) —
Grid's hardware code has **no dedicated "Hardware integration" commit** in
its git history and no `WINDOWS_HARDWARE_INTEGRATION.md`-equivalent
write-up. The `_hw_init()` / `USE_SERIAL_HD` / `led.led_control` plumbing
was added as an undocumented part of a larger commit, implemented **by
analogy** from Hoops/Climb's real-hardware findings — it has never been run
against an actual physical floor.

**There is also no "known good baseline" to fall back on.** The game logic
itself (marathon session rework, RFID/credits integration, settings push
from the central server, 2P scoring on `----`-tier levels) has continued to
change *after* the point where Hoops/Climb's hardware code was last
validated. So this onsite session is validating two things at once, for
the first time, together:

1. The hardware driver code itself (never tested on real hardware, any
   game).
2. The current game logic running through that hardware path (changed
   since the only comparable hardware passes on other games).

Do not assume "it worked on Hoops/Climb" implies it will work here — the
grid dimensions (16×26 vs 6×33), COM port count (3, same as Climb but a
different physical loom), and layout type (6, game-specific) are all
different, and the game logic driving `led_display` has diverged.

## 3. Onsite validation checklist

Run these in order. Stop and debug before continuing if any step fails —
later steps assume earlier ones passed.

- [ ] **Env var set.** Confirm `USE_SERIAL_HD=1` is set in the shell that
      launches uvicorn (`echo %USE_SERIAL_HD%` / `$env:USE_SERIAL_HD` on
      Windows — see `ONSITE.md` Step 7). Server log must show
      `Hardware ready: 3 port(s), 16×26, layout=6` on startup, not a
      `Hardware init failed` error.
- [ ] **`games/test_hardware.py` standalone diagnostic.** Run it directly
      (`python test_hardware.py` from `games/`, per `ONSITE.md` Step 6)
      before starting the full API. Expected: all 3 COM ports open OK, full
      16×26 floor lights solid green for ~3s, stepping on tiles logs
      `PRESS detected: row=X col=Y`, floor clears at the end.
- [ ] **Grid mapping / orientation.** With the game running
      (`USE_SERIAL_HD=1`, real floor), spot-check that browser-simulator
      tile (row, col) lights the SAME physical tile:
      - [ ] Corner (0, 0)
      - [ ] Corner (0, 25)
      - [ ] Corner (15, 0)
      - [ ] Corner (15, 25)
      - [ ] 2-3 interior tiles picked at random
      - [ ] **Explicitly rule out row/col transposition** — light row 0 only
        (a full row, not a single tile) and confirm it's a physical row, not
        a column, on the floor. This is the single most common first-time
        hardware bug (see Troubleshooting below).
- [ ] **Full marathon session, 1P.** Start a game, play through to natural
      session end (5-min timer or life exhausted) on a real 1P level (`-`
      or `--` tier). Confirm score/life track correctly and the simulator
      and physical floor stay in sync throughout (no visible lag beyond the
      ~22fps HW draw ceiling).
- [ ] **Real 2P session on a `----`-tier `.ledb` level.** Confirm both
      players' tiles render distinctly on the physical floor (not just the
      simulator), scoring is tracked separately (score / score2), and the
      no-divide scoring policy holds (`scode_divide_person` /
      `scode_divide_time` both `False` — final scores are NOT divided by
      player count).
- [ ] **Blank-on-stop fix (new in this pass).** For each of the following,
      confirm the physical floor goes fully dark within ~1s — not just the
      simulator/scoreboard:
      - [ ] Let a level run to session timeout (no manual stop).
      - [ ] Force life to 0 with time remaining is a *restart*, not a real
        end — instead let the full session time out or run the sequence to
        exhaustion for a genuine game-over, then confirm blank.
      - [ ] Manually stop via the frontend's stop control (hits `/logout` →
        `stop_game()`).
      - [ ] Start a **new** game immediately after a stale pattern was
        showing (skip the blank check above once to reproduce a stuck
        frame first) — confirm `clear_all()`'s blank fires before the new
        game's first real frame is drawn.
      - [ ] Confirm no regression: floor still draws normally at full frame
        rate during active gameplay (the blank call must not fire mid-game
        or throttle the per-frame draw).

## 4. Troubleshooting — likely first-time failure modes

- **COM port ordering wrong / floor sections dark or scrambled.** The
  shelve's `list_com_info` order determines which physical loom maps to
  which third of the 416-tile floor. If one third is dark or two thirds are
  swapped, the COM port order in the shelve doesn't match the physical
  cabling on this machine. Trace which physical section is dark, identify
  its cable, and reorder `list_com_info` (or the cables) to match — do
  **not** edit `led_layout_type` or grid dimensions to compensate for a
  wiring/order issue.
- **Row/col transposition.** If pressing/lighting tile (r, c) actually
  affects (c, r), or a "row" appears as a column on the floor, this is a
  layout-type or wiring convention mismatch — check `layout_type` (6) is
  correct for this specific floor's physical wiring, not copied from
  another game's layout number.
- **Off-by-one indexing.** With a 16×26 grid, an off-by-one shows up as the
  last row or column being dark/dead or wrapping onto the first. Spot-check
  index 0 and index (rows-1)/(cols-1) specifically, not just the middle of
  the floor.
- **Partial lighting on `test_hardware.py`'s green-floor test.** Expected
  behavior is ALL 416 tiles green. If only ~1/3 or ~2/3 light up, that's a
  COM port problem (see above), not a code bug — each of the 3 ports
  should cover roughly a third of the floor.
- **Floor doesn't blank after stop (blank-on-stop fix not working).** Check
  `logs/api.log` for `HW blank failed: ...` warnings from `_hw_blank_floor`
  — the surrounding `try/except` swallows failures into a log line rather
  than crashing, so a silent failure here won't be obvious unless the log
  is checked. Also consider: COM ports may already be closing/contended if
  the blank races the game thread's own last in-flight draw (an open
  question flagged when this fix was designed — see the equivalent
  discussion in `led-hoops/docs/TODO_HARDWARE_BLANK_ON_STOP.md`). If a
  single blank write doesn't stick, try sending it twice in a row before
  concluding it's a deeper bug.
- **Server log shows `Hardware init failed` instead of `Hardware ready`.**
  Almost always one of: `USE_SERIAL_HD` not actually set in the shell that
  launched uvicorn, the `led_parameter` shelve missing/corrupt, or a COM
  port in the shelve not present on this machine (check with
  `python -c "import serial.tools.list_ports; ..."` per `ONSITE.md` Step 5).

## 5. Report back

After running the checklist, report pass/fail for each item individually
(not just an overall "it worked") — see `AGENT_PROMPT.md` for the exact
report format expected from an onsite agent.

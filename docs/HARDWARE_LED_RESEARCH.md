# Hardware LED Floor Research (Floor Is Lava / LED Grid)

On-site investigation for the 16×26 LED floor driven over COM4/COM3/COM6 (WCH USB-serial). Documents symptoms, root causes, benchmarks, fixes, and tuning knobs validated July 2026.

## Symptoms Reported

| Symptom | When |
|--------|------|
| Very low FPS on physical floor | Initial integration |
| Simulator lagging | Same period |
| Tile clicks not registering (sim + HW) | Same period |
| Hardware stuck on one frame | After partial fixes |
| Red strip “jumps” instead of sliding (0&1 off, then 1&2 on) | After artificial slowdown |
| Movement too fast / glitchy transitions | Before final tuning |

## Environment

- **Grid:** 16×26, layout type 6
- **COM ports:** COM4, COM3, COM6 (from `games/setting/led_parameter` shelve — do not edit onsite)
- **API:** port 8003, `USE_SERIAL_HD=1`
- **Controller:** WCH USB2MCOM multi-channel device (COM3/4/6 are channels on one USB chip, not independent pipes)

## Benchmarks (Measured Onsite)

From `python scripts/bench_serial.py`:

| Operation | Avg time | Implied max rate |
|-----------|----------|------------------|
| DRAW only (full floor, 3 ports) | **38.8 ms** | ~25.8 fps |
| READ only (sensors) | **0.1 ms** | — |
| READ + DRAW | **40.8 ms** | **~24.5 fps** |

**Conclusion:** Serial **draw** is the bottleneck. Game logic can run much faster (~100+ fps) when not blocked by full-floor redraws.

## Root Causes Found

### 1. Two games fighting for COM ports

`clear_all()` set `running=False` but did not join old game threads. Zombie threads kept reading/writing COM ports → garbled sensor data, access violations, missed input.

**Fix:** `clear_all()` now joins threads (3s timeout) before clearing the games dict.

### 2. Background sensor thread (removed)

A `_HwSensorReader` thread polled COM while the game thread drew on the same ports. WCH drivers are not thread-safe → corrupt reads, crashes (`exit code 3221225477`).

**Fix:** All COM I/O on the **game thread only**, guarded by `_hw_serial_lock`.

### 3. Stale state for scoring

Scoring used a `state_table` snapshot taken before the hardware sensor read.

**Fix:** Read sensors immediately before the scoring loop each frame.

### 4. Draw crash — malformed RGB cells (`IndexError`)

`Play.clear_led_table()` used default `color=(Color.BLACK,)` — a **1-tuple wrapping RGB**, not `[0,0,0]`. Every cleared cell became `((0,0,0),)`. `draw_screen_by_com` then failed on `tuple_color[1]` → **every draw aborted on COM4** → floor frozen on first partial frame.

**Fix:**
- `Play.clear_led_table(self, color=Color.BLACK)` (no trailing comma tuple)
- `_normalize_rgb()` in `_hw_draw_floor()` as a safety net

### 5. Simulator clicks wiped by hardware read

With `USE_SERIAL_HD=1`, each frame’s sensor read overwrote `state_table`, erasing simulator mouse presses.

**Fix:** Track `game._sim_pressed` in `apply_input()`; merge with hardware state during scoring and `/hw-debug`.

### 6. Artificial slowdown made motion worse (not better)

Setting `HW_DRAW_INTERVAL=0.75` (~1.3 updates/sec) did **not** slow the game’s wave logic — only LED refresh. Between draws the pattern advanced several cells, producing visible “teleport” (0&1 off → 1&2 on).

**Fix:** Match hardware refresh to the **physical serial ceiling** (~22–25 fps), not arbitrary slow values. If motion still feels too fast, tune **level `group.speed`** in the level file, not draw interval below ~25 fps.

### 8. Zombie game thread from double `/start-game` race (July 7, ~22:00 IST)

**Symptom:** Intermittently, after a fix had already been validated ("looks and plays way better"), the exact same class of bug would reappear — pattern moving "way too fast" again, simulator not reflecting hardware state, simulator clicks silently failing. It looked like a previous fix had been "reverted," but no code had regressed — a **race condition** was reintroduced by an unrelated change.

**Root cause (two parts, confirmed from timestamped logs):**

1. **Trigger:** `frontend/src/main.jsx` wraps the app in `<React.StrictMode>`, which deliberately mounts→unmounts→remounts every component once in dev mode. `SimulatorScreen.jsx`'s "start game on mount" `useEffect` had no re-entry guard, so it fired `POST /start-game` **twice**, ~17ms apart, from the same browser tab (confirmed: two `OPTIONS /start-game` + two `Start game request` log lines back to back).
2. **The actual regression:** `game.running` was being set `True` **inside** `_run_game()`, only after ~45ms of setup (HW init, module imports, `Play` creation) — not synchronously at game creation. When the second `/start-game` call's `clear_all()` set `running = False` on the first game while it was still mid-setup, the first game's own thread reached its setup code a few milliseconds later and set `running = True` again, **silently clobbering the stop signal**. The callback's `if not game.running: return False` check never fired again. `clear_all()`'s `thread.join(timeout=3)` timed out ("Game thread ... did not stop within 3s"), gave up, and started a second game anyway — leaving the first (zombie) thread still fully alive and hitting the same COM ports concurrently with the new game's thread. This produced the exact same `data_want` garbled-read corruption as root cause #1/#2 above, just via a different trigger. Corrupted reads caused phantom "presses" in `state_table`, which auto-consumed tiles nobody touched, which cleared levels/advanced `total_pass` far faster than intended — perceived as "pattern moving way too fast."

**Fix:**
- `frontend/src/screens/SimulatorScreen.jsx`: added a `startedRef` guard so the start-game effect fires at most once per real mount, immune to StrictMode's double-invoke.
- `api/game_manager.py`: `game.running = True` is now set **synchronously inside `create_game()`**, immediately after the `GameInstance` is constructed — before the background thread even starts, and it is never set `True` again afterward. This makes any concurrent stop signal (`clear_all()` or `stop_game()`) permanent; nothing can race it.
- `api/game_manager.py`: `create_game()` now wraps `clear_all()` + instance creation in a dedicated `_create_lock` (defense in depth — not required under the current single-worker/async-without-await request model, but cheap insurance if that ever changes).
- `api/main.py` `/hw-debug`: exposes `zombie_threads` — a list of any thread that ever failed to join in time. Should always be empty; if it's not, the hardware is likely being hit by two threads at once again.

**Lesson:** a "fix" that changes *when* a flag is set (not just *what* it's set to) can reintroduce concurrency bugs that have nothing to do with the original problem it was solving. Always ask: can two calls to this code path overlap in time, and if so, can a later write from the "loser" of the race stomp on the "winner"'s intent?

### 9. `ws_bridge` polling too fast, starving WebSocket keepalive (July 7, ~22:40 IST)

**Symptom:** Even after root cause #8 was fixed (hardware itself confirmed working well for 3 levels), the simulator still showed hardware presses late/inconsistently, and clicking tiles in the simulator did not register at all.

**Root cause:** `ws_bridge.py`'s `poll_game_state()` polled the API's `/active-game` endpoint every **8ms (125Hz)** — far faster than the hardware itself can ever update (~22fps draw ceiling from root cause #7). Each poll does a full HTTP round trip + JSON encode/decode of the entire `led_display` grid, then a broadcast to all connected simulator clients. At 125Hz this piled up enough CPU/event-loop work on `ws_bridge`'s single asyncio event loop thread to intermittently starve WebSocket ping/pong handling, which the browser then killed as `keepalive ping timeout` (confirmed repeatedly in the `ws_bridge` log). While the socket was down, the simulator's `sendMsg()` silently no-ops on every click (`if (ws && ws.readyState === WebSocket.OPEN)`), so presses never reached the backend — and frame broadcasts queued up or dropped, producing the sync lag.

Additionally, `broadcast_state()`/`broadcast_blank()` sent to each connected client **sequentially** with `await ws.send_text(...)` in a `for` loop — one slow or already-dead client (e.g. a stale leftover browser tab, several of which were found still reconnecting from earlier test sessions) could delay delivery to every other client in that same broadcast.

**Fix (`ws_bridge.py`):**
- Reduced poll interval from `0.008s` (125Hz) to `0.033s` (~30Hz) — still well above the ~22fps hardware ceiling, but ~4x less HTTP/JSON/broadcast churn.
- `broadcast_state()`/`broadcast_blank()` now send to all clients **concurrently** via `asyncio.gather()` instead of sequentially, so one dead/slow connection can't delay the rest.

**Lesson:** polling faster than the underlying data source can possibly change doesn't make things feel more real-time — past a certain point it just burns CPU that should be spent servicing other work (like WebSocket keepalives), making everything *less* responsive.

### 10. WCH multi-channel USB architecture

`Get-PnpDevice` shows COM3/COM4/COM6 as channels `USB55D9_COM_00/01/02` on instance `...&30D1F5A1&0&...`. All channels share one USB bulk pipe (CH348-family behaviour). Full-floor draw = 3 sequential port writes ≈ 39 ms total. This is a **hardware/driver limit**, not fixable by parallel Python threads.

Registry on COM4 shows `PollingPeriod: 0` under WCH `Device Parameters` (no FTDI-style latency timer exposed).

## Architecture (Final)

```
Play.running() loop (game thread)
  └─ Play.update() → fills led_table colors
  └─ _frame_callback:
       1. Classify cells (goal/red/green) from active groups
       2. READ sensors (before scoring)
       3. Score pressed cells (HW + simulator)
       4. Build led_display (simulator / API state, with pulse)
       5. DRAW to hardware (throttled, normalized RGB)
```

Original decompiled game order in `update_led()` was **draw then read**. Current headless path reads before score (input accuracy) and draws after building `led_display` (valid RGB buffer).

## Tuning Parameters

| Variable | Default | Meaning |
|----------|---------|---------|
| `USE_SERIAL_HD` | `0` (set `1` onsite) | Enable real COM I/O |
| `HW_DRAW_INTERVAL` | `0.045` (~22 fps) | Min seconds between full-floor draws |

**Do not** set `HW_DRAW_INTERVAL` much above `0.04` unless debugging — it causes jumpy motion, not smoother motion.

**Rejected approach:** Temporal smoothing / tail persistence on hardware frames (user feedback: looked worse).

## Diagnostics

| Tool | Command | Purpose |
|------|---------|---------|
| Live HW monitor | `python scripts/hw_live_test.py` | Press/release lines from `/hw-debug` |
| Debug loop | `python scripts/debug_loop.py` | Frame rate, draw rate, lit pixels, **zombie threads, dual-game detection** |
| Serial bench | `python scripts/bench_serial.py` | Raw draw/read timing |
| API bench | `python scripts/bench_api.py` | Simulator input latency |
| State rate | `python scripts/bench_state_rate.py` | How fast `led_display` changes |
| HTTP | `GET http://localhost:8003/hw-debug` | `frame_count`, `hw_draw_count`, `lit_pixels`, presses, `zombie_threads`, `active_games` |

## Files Changed

| File | Change |
|------|--------|
| `api/game_manager.py` | Single-thread HW I/O, RGB normalize, sim press merge, draw throttle, thread join, `running=True` set synchronously at creation (not late), `_create_lock`, `zombie_threads` tracking |
| `api/main.py` | `GET /hw-debug` endpoint (now also returns `zombie_threads`) |
| `games/game_play/Play.py` | Fix `clear_led_table` default color tuple bug |
| `scripts/hw_live_test.py` | Onsite press monitor |
| `scripts/debug_loop.py` | Live FPS / draw-rate monitor; now also flags zombie threads / >1 active game |
| `frontend/src/screens/SimulatorScreen.jsx` | `startedRef` guard against React StrictMode double-firing `/start-game`; iframe now passes `game_id` to `ws_bridge` |
| `ws_bridge.py` | Poll rate 125Hz → 30Hz; concurrent (not sequential) broadcast to clients; forwards `pressed_tiles` and resolves `game_id` from client query param |
| `simulator/static/index.html` | Renders `serverPressed` (hardware + sim presses reported by the server) as a white overlay, in addition to the local click overlay |

## Validation (July 2026)

- Hardware test: green floor + sensor press at row=12 col=12 ✓
- Level 007: red pattern sweeps left-to-right on physical floor ✓
- Input: physical presses score correctly ✓
- Final tuning (`HW_DRAW_INTERVAL=0.045`, no smoothing): "looks and plays way better" ✓
- Round 2 (zombie thread + ws_bridge poll rate fixes): played 3 levels on real hardware with correct speed, `active_games` stayed at 1 and `zombie_threads` stayed empty throughout (checked live via `/hw-debug`), simulator reflected hardware presses, and simulator-only clicks scored correctly ✓

## Debugging Setup (reusable in a fresh Cursor session)

Everything below was the actual working setup used to find and validate the Round 2 fixes (section 8/9). Use this checklist to get back to a known-good debugging state quickly, without re-deriving it from scratch.

### Services & ports

| Service | Port | Start command (from repo root unless noted) |
|---------|------|----------------------------------------------|
| API | 8003 | `$env:USE_SERIAL_HD="1"; python -m uvicorn api.main:app --host 0.0.0.0 --port 8003` |
| ws_bridge | 8769 | `$env:API_PORT="8003"; $env:WS_BRIDGE_PORT="8769"; python ws_bridge.py` |
| Frontend (Vite) | 5176 | `cd frontend; npm run dev` |

Do **not** set `HW_DRAW_INTERVAL` unless intentionally testing a different draw rate — the default (`0.045`) is the validated value. Leave it unset.

### Finding what's actually running

Terminal metadata files can go stale fast in a long session (many restarts pile up). The reliable way to find the *real* current process for a port:

```powershell
Get-NetTCPConnection -LocalPort 8003,8769,5176 -State Listen | Select-Object LocalPort,OwningProcess
Get-Process -Id <pid> | Select-Object Id,ProcessName,Path,StartTime
```

Kill and restart cleanly with `Stop-Process -Id <pid> -Force`.

### Live monitor (run this whenever testing)

```powershell
python scripts/debug_loop.py
```

Polls `GET /hw-debug` every 500ms and prints frame rate, hw draw rate, lit pixel count, and pressed tiles. Critically, it now prints a loud banner if:
- `zombie_threads` is non-empty (a stale game thread outlived its stop signal and may still be hitting hardware — see root cause #8)
- `active_games > 1` (two games registered at once — should never happen; kiosk model is one game at a time)

If you only check one thing after restarting the stack, check this. Both fields being empty/1 across a multi-level play session is the signal that root cause #8 is actually fixed.

### Manually probing the API

```powershell
# Current game(s), zombie threads, active game count
Invoke-RestMethod http://localhost:8003/hw-debug | ConvertTo-Json -Depth 5

# Full state for a specific game
Invoke-RestMethod http://localhost:8003/game-state/<game_id> | ConvertTo-Json -Depth 5

# Simulate a simulator click directly (bypasses the browser/ws_bridge entirely —
# useful to isolate "is the backend broken" vs "is the transport broken")
$body = @{ row=5; col=5; type="press"; game_id="<game_id>" } | ConvertTo-Json
Invoke-WebRequest http://localhost:8003/game-input -Method Post -Body $body -ContentType "application/json" -UseBasicParsing
```

**Important:** grab `game_id` from `/hw-debug` *immediately* before using it — games are short-lived (kiosk model clears on next start / on timeout), so a `game_id` that was valid 15 seconds ago may already 404 with `"Game not found"`. Don't mistake that for a bug.

### Reading logs for the actual smoking gun

Don't trust "it feels laggy" reports alone — grep the actual API/ws_bridge terminal output for these specific signatures, which is how both Round 2 bugs were actually diagnosed (not guessed):

| Signature | Means |
|-----------|-------|
| `Game created: X` appearing twice within ~1s, second one after `did not stop within 3s` | Zombie thread race (root cause #8) — two games' threads are now fighting over the same COM ports |
| `data_want:b'...'` / `index in rect_position_arr 416` in `led.led_control` errors | Corrupted serial read — almost always a symptom of two threads hitting the hardware at once, not a hardware fault by itself |
| `[ERR] Send error: ... keepalive ping timeout` in `ws_bridge` output | WebSocket to the simulator died — check poll rate / broadcast pattern in `ws_bridge.py` (root cause #9) |
| `WebSocket /ws` (no `?game_id=`) connecting | A stale/leftover simulator tab or iframe from an earlier test is still alive and reconnecting — close all browser tabs and start fresh before trusting any lag/sync test |

### Frontend gotcha: React StrictMode

`frontend/src/main.jsx` wraps the app in `<React.StrictMode>`, which **intentionally double-invokes mount effects in dev mode**. Any `useEffect` that fires a one-time side effect on mount (like starting a game) needs a `useRef` re-entry guard, or it will silently run twice. This was the trigger for root cause #8. If a *new* one-shot-on-mount effect is ever added anywhere in this app, guard it the same way `SimulatorScreen.jsx`'s `startedRef` does.

### Before declaring anything fixed

1. Close **all** browser tabs pointed at the app (not just refresh) — stale iframes/WebSockets from earlier tests linger and pollute results.
2. Restart API + ws_bridge fresh.
3. Start `scripts/debug_loop.py` and leave it running during the test.
4. Play through at least 2-3 levels on real hardware, not just a few seconds — root cause #8 specifically only showed up a few seconds into a session, after the race actually landed.
5. Check `zombie_threads` and `active_games` stayed clean the whole time, not just at the end.

## If Motion Still Feels Too Fast

The level animation speed comes from `group.speed` and `game_level_speed` in the level’s `.led` file, not from draw rate. Options:

1. Edit level difficulty / speed in the level editor (preferred)
2. Lower `Play.game_level_speed` for headless API sessions (code change)
3. Do **not** throttle hardware draw below ~25 fps — causes visible stepping

## References

- WCH CH348 Linux driver (`ch348.c`): multiplexed bulk endpoints for octal UART
- FTDI latency timer docs (analogous concept; WCH uses `PollingPeriod` instead)
- WLED / NeoPixelBus: low-FPS LED updates cause visible stepping; match refresh to hardware capability

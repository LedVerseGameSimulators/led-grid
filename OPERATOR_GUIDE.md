# LED Grid (Floor Is Lava) — Studio Operator Guide

This game does **not** start from a single `.exe` like the old LedPlay program.
It needs **three small programs** running together. You do **not** need to start
them by hand — use the starter file below.

---

## Start the game (normal open)

1. Make sure the LED floor PC is on and the floor USB cable(s) are plugged in.
2. Open the game folder:
   `C:\Users\Administrator\Downloads\led-grid`
   *(or wherever this copy lives on the studio PC)*
3. **Double-click** `START_GAME.bat`
4. Wait about 10 seconds. Your browser should open the game screen at:
   **http://localhost:5176/**
5. Leave the **three black console windows** open while the floor is in use.
   Closing them stops the game.

| Window title | What it does |
|---|---|
| LED Grid — Floor Engine | Talks to the physical LED floor and runs the game logic |
| LED Grid — Display Bridge | Keeps the on-screen map in sync |
| LED Grid — Game Screen | The UI guests / operators use |

---

## Play a session

1. On the landing screen, pick a mode:
   - **Single** — 1 player; then pick tier/level/difficulty
   - **Multi** — 2 players; then pick 2P levels
   - **Group** — skips level picker; uses the Group playlist (`games\source_group`)
2. On login:
   - RFID: scan / enter card → **Validate** first → then **Start Game**
     (team roster names show after a successful validate when the RFID server sends them)
   - Or use **Skip — Play as Guest** if RFID is not set up
3. The physical floor should show the same pattern as the on-screen grid.
4. Guests score by stepping on safe tiles; lava tiles cost life.

---

## Stop the game (end of day / restart)

1. **Double-click** `STOP_GAME.bat`
2. Or manually close the three “LED Grid — …” windows.

If the game feels stuck or the floor does not update, stop with `STOP_GAME.bat`,
wait 5 seconds, then run `START_GAME.bat` again.

---

## Quick troubleshooting

| Problem | What to try |
|---|---|
| Starter says Python not found | Python 3.11 must be installed with “Add to PATH” |
| Starter says npm not found | Install Node.js LTS from https://nodejs.org |
| Floor stays dark / no green on old test | USB / COM ports — ask tech; do not edit `games\setting` |
| Browser page will not load | Wait a few more seconds, then open http://localhost:5176/ yourself |
| “Port already in use” | Run `STOP_GAME.bat`, then `START_GAME.bat` again |
| RFID card login fails | Use Guest mode for now — network RFID is set up separately |

**Do not** edit files inside `games\setting\` (floor COM port config).
**Do not** run the old `D:\ledplayv020507\ledplay` program at the same time —
both would fight for the same floor USB ports.

---

## For technicians only

| Service | Address |
|---|---|
| Game UI | http://localhost:5176 |
| Game API | http://localhost:8003 |
| Display bridge | http://localhost:8769 |

Hardware mode is turned on automatically by `START_GAME.bat`
(`USE_SERIAL_HD=1`). Floor settings are loaded from `games\setting\led_parameter`.

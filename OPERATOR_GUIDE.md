# LED Grid (Floor Is Lava) — Operator Guide

Simple start / play / stop for floor staff. No coding needed.

## Start

1. Double-click **`START_GAME.bat`** in this folder.
2. Wait until you see **LED GRID is running (HARDWARE)**.
3. The API window must say **HARDWARE MODE ON**.
4. The browser opens in **fullscreen kiosk** at **http://127.0.0.1:5176/**.
5. **Ctrl+Shift+K** exits fullscreen only (the game keeps running). Use **`STOP_GAME.bat`** to stop the game.
6. Leave the minimized service windows open while playing.
7. When a game starts, the **physical floor** and the on-screen sim both run.

**Engineers / debug:** use `scripts\start-dev.bat` (normal browser, Vite dev server — not kiosk).

## Play

1. On the landing screen, pick a mode:
   - **Single** — 1 player; then pick tier/level/difficulty
   - **Multi** — 2 players; then pick 2P levels
   - **Group** — skips level picker; uses the Group playlist (`games\source_group`)
2. On login:
   - RFID: scan / enter card → **Validate** first → then **Start Game**
   - Or use **Skip — Play as Guest** if RFID is not set up
3. Use **one browser tab only**.
4. The physical floor and the on-screen simulator run together.

## Stop

1. Double-click **`STOP_GAME.bat`**.
2. Wait until it says the game stopped.
3. Close any leftover black windows if they are still open.

## Common fixes

| Problem | What to do |
|---------|------------|
| Start says Python not found | Ask tech to install Python 3.11 with "Add to PATH". |
| Start says Node.js not found | Ask tech to install Node.js LTS. |
| Start says floor settings missing | Ask tech to copy `games\setting\` files onto this PC. |
| Browser page blank / won't load | Wait 10–15 seconds after start, then refresh. Or run `STOP_GAME.bat`, then `START_GAME.bat` again. |
| Floor LEDs dark but game runs in browser | Check USB cable to the floor controller. Run start again. |
| Two games fighting each other / freeze | Close all browser tabs, run `STOP_GAME.bat`, then start once with one tab. |
| Need to reboot game mid-day | `STOP_GAME.bat` → wait → `START_GAME.bat`. |

## Packaging / updates

- Download the latest release zip from **GitHub Releases** (operators do not need git).
- Extract the zip to a folder on the PC.
- Double-click **`LED Grid.exe`** (or **`START_GAME.bat`** — both start the game the same way).
- **First time on a new PC:** a technician runs **`SETUP_FIRST_TIME.bat`** once to install Python packages and frontend dependencies. The PC must already have **Python 3.11**, **Node.js LTS**, and **Chrome or Edge** installed.
- **Updates:** stop the game with `STOP_GAME.bat`, then replace the folder with the new release zip (or drop in the new `LED Grid.exe`).

## Notes

- These buttons only **run and stop** LED Grid on this PC.
- They do **not** change Wi‑Fi / LAN / RFID server settings.
- Port used by the game UI: **5176**.

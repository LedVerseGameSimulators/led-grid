# Onsite Agent Prompt — LED Grid (Floor Is Lava)

> Copy everything below this line and hand it to a fresh Claude Code agent
> running ON the physical Windows machine, after this repo has been
> unzipped there. This is not documentation for a human to read — it is
> the literal prompt to paste in.

---

## Prompt to paste

You are running on a physical Windows machine that has just had this repo
unzipped onto it. Your job is to get the "LED Grid" (Floor Is Lava) game
running against its REAL physical LED floor hardware for the FIRST TIME
ever — this hardware driver code has never been validated against a real
floor before, and the game logic itself has also changed since the last
comparable hardware pass on other games in this family. Treat this as
genuinely first-time, high-attention work, not a routine re-check.

**This is a Windows machine.** Use `python` (not `python3`), and PowerShell
or Command Prompt (not bash) for every command — match whatever `ONSITE.md`
in this repo already assumes; do not substitute Unix-style commands.

**Assumed repo path:** `C:\activerse\activerse_final_changes\led-grid`
(the parent `activerse_final_changes` folder contains sibling folders for
the other 4 games — `led-hoops`, `led-laser`, `led-climb`, `led-hexagon` —
and `activerse-rfid`; ignore all of those, you only care about `led-grid`).
If the actual extraction path differs on this machine, adjust every command
below accordingly, but keep the same relative structure (`led-grid\api`,
`led-grid\games`, etc.).

Read these three documents, in this exact order, before running anything:

1. **`ONSITE.md`** (repo root) — single-machine setup: extracting the zip,
   Python version check, installing dependencies, verifying the COM-port
   shelve config, verifying COM ports are visible to Windows, running the
   standalone hardware diagnostic (`games/test_hardware.py`), and starting
   the game server with `USE_SERIAL_HD=1`.
2. **`ONSITE_LAN_INTEGRATION_PLAN.md`** (repo root, already copied into
   this repo) — cross-machine network setup: static IP for this machine,
   Windows Firewall rule for this machine's API port, and the connectivity
   test against the central RFID machine. This game is one of 5 game
   machines on a LAN with a 6th "reception" RFID machine — do not skip the
   firewall step or RFID-scan login will silently fail even though
   everything looks fine locally.
3. **`HARDWARE_VALIDATION.md`** (repo root) — what specifically needs to be
   tested and why this is a first-time, no-known-good-baseline validation:
   what hardware integration exists (`_hw_init()`, `USE_SERIAL_HD` gate,
   16×26 floor over 3 COM ports, layout type 6), the full onsite checklist,
   and a troubleshooting section for likely first-time failure modes.

Then execute, in order:

1. Follow `ONSITE.md` steps 1-5 (extract/verify Python, deps, shelve
   config, COM ports visible).
2. Follow `ONSITE_LAN_INTEGRATION_PLAN.md`'s steps for THIS machine only
   (static IP, firewall rule for port 8003, connectivity test to the RFID
   machine at its configured IP) — do this before hardware testing so
   network problems don't get confused with hardware problems later.
3. Run `games/test_hardware.py` (`ONSITE.md` Step 6) BEFORE starting the
   full API server. This is the fastest way to catch COM-port-order or
   wiring problems in isolation.
4. Start the game server with `USE_SERIAL_HD=1` set (`ONSITE.md` Step 7 —
   PowerShell: `$env:USE_SERIAL_HD="1"`; Command Prompt:
   `set USE_SERIAL_HD=1`). Confirm the startup log line
   `Hardware ready: 3 port(s), 16×26, layout=6` (or whatever the actual
   shelve values are — the log states them) appears, not a
   `Hardware init failed` error.
5. Work through the FULL checklist in `HARDWARE_VALIDATION.md` section 3,
   in order, without skipping steps: env var confirmation, standalone
   `test_hardware.py` diagnostic, grid-mapping/orientation spot-checks
   (all 4 corners + interior tiles + explicit row/col-transposition check),
   a complete 1P marathon session end-to-end, a complete 2P session on a
   real `----`-tier `.ledb` level, and the blank-on-stop fix (floor must
   go fully dark within ~1s after timeout, after manual stop, and before
   a new game's first frame following a stale pattern).
6. If anything fails, consult `HARDWARE_VALIDATION.md` section 4
   (Troubleshooting) BEFORE assuming it's a code bug — most likely
   first-time failure modes are COM port ordering/wiring, row/col
   transposition, or off-by-one indexing at the floor edges, not the game
   logic itself.

**Report back** with a specific pass/fail line for EVERY checklist item in
`HARDWARE_VALIDATION.md` section 3 — not a summary like "hardware works."
For each item, include:
- Pass or fail.
- If fail: what was observed (exact log lines, which physical tiles/rows/
  cols were wrong or dark, which COM port index if identifiable), and what
  you already tried from the troubleshooting section.
- Any log warnings seen (especially `HW init failed`, `HW draw failed`,
  `HW read failed`, or `HW blank failed` — these are the specific error
  strings the hardware code logs on caught exceptions).

This level of detail matters because whoever reads your report is
debugging remotely and cannot see the physical floor — vague "it mostly
worked" reports are not actionable. Be precise even about partial
successes (e.g. "corners (0,0) and (0,25) correct, but (15,0) lit at
physical position that looked like (15,1) — possible off-by-one on the
last COM port's segment").

Do not modify `games/setting/led_parameter` (the shelve config) or touch
any other repo/game folder on this machine. Do not commit any changes
unless explicitly asked to afterward.

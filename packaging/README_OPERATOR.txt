LED Grid - Operator package
============================

Double-click  "LED Grid.exe"  to start the game.
It does everything START_GAME.bat did: starts the game engine and bridge,
turns the floor hardware ON, and opens the game full screen.

  Exit full screen ........ Ctrl+Shift+K
  Stop the game ........... double-click STOP_GAME.bat
  Health check ............ run  "LED Grid.exe" --selftest  and send the output

Needs on this PC (already installed on floor PCs)
-------------------------------------------------
  - Google Chrome or Microsoft Edge
  - LED floor USB serial driver
  - The central RFID server reachable on the network

Settings that belong to THIS venue (keep them when updating)
-----------------------------------------------------------
  games\setting\                 floor / LED / COM settings and the scores database
  games\setting\activerse.json   {"rfid_api_url": "http://192.168.1.106:9000"}
                                 (optional; default is http://localhost:9000)

Updating
--------
  Copy the new release over a NEW folder, then copy your existing
  games\setting\ folder into it. Never replace games\setting\ with the one from a
  release zip unless you want to reset this venue's settings and scores.

Troubleshooting
---------------
  Logs are in the logs\ folder. Do not edit files in this package other than
  games\setting\activerse.json. Windows SmartScreen may warn about an
  unsigned app: choose "More info" -> "Run anyway".

Developers: --sim runs the simulator only (no serial); ACTIVERSE_KIOSK=0 opens a
normal browser window instead of kiosk.

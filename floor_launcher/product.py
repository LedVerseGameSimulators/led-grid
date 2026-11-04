"""Per-product constants. This is the only file that differs between game repos."""

SLUG = "grid"             # kiosk profile slug (open-ui.bat ... 5176 grid), release/zip names
DISPLAY_NAME = "LED Grid"
API_PORT = 8003           # must match frontend/src/config.js
BRIDGE_PORT = 8769
# Ports freed on STOP (same set STOP_GAME.bat frees; 5176 = legacy vite preview UI).
STOP_PORTS = (8003, 8769, 5176)

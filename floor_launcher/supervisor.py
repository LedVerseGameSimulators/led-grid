"""
Floor supervisor — what START_GAME.bat does, as one program.

  1. refuse to start without floor settings (games/setting/led_parameter.dat)
  2. stop any previous run (STOP /quiet)
  3. start the API with USE_SERIAL_HD=1 (hardware) unless --sim
  4. start the WebSocket bridge
  5. wait for the UI (served by the API), confirm /hw-debug says hardware is on
  6. open the isolated kiosk browser + Ctrl+Shift+K exit hotkey
  7. stay alive; if a child dies, stop everything and say so
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import List

from api.runtime_paths import games_root, install_root, self_exe

from . import kiosk, procs
from .product import API_PORT, BRIDGE_PORT, DISPLAY_NAME, SLUG

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


def _log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} [supervisor] {msg}"
    try:
        print(line, flush=True)
    except (OSError, ValueError):
        pass
    try:
        with open(procs.logs_dir() / "supervisor.log", "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def fail(msg: str, code: int = 1) -> None:
    """Log, and on Windows tell the operator (console is hidden)."""
    _log(f"ERROR: {msg}")
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, msg + "\n\nSee the logs folder.", DISPLAY_NAME, 0x10)
        except Exception:
            pass
    sys.exit(code)


def hide_console() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


def _get(url: str, timeout: float = 2.0):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.status, resp.read()


def _wait_ui(tries: int = 30) -> bool:
    for _ in range(tries):
        try:
            status, _ = _get(f"http://127.0.0.1:{API_PORT}/")
            if status == 200:
                return True
        except (urllib.error.URLError, OSError, TimeoutError):
            pass
        time.sleep(2)
    return False


def _spawn(role: str, env: dict, root: Path) -> subprocess.Popen:
    out = open(procs.logs_dir() / f"{role}.console.log", "ab")
    return subprocess.Popen(
        self_exe() + ["--role", role],
        env=env,
        cwd=str(root),
        stdout=out,
        stderr=subprocess.STDOUT,
        creationflags=CREATE_NO_WINDOW,
    )


def main(argv: List[str]) -> None:
    sim = "--sim" in argv or os.environ.get("ACTIVERSE_SIM") == "1"
    kiosk_on = os.environ.get("ACTIVERSE_KIOSK", "1") != "0"
    no_browser = "--no-browser" in argv  # CI / headless smoke tests
    if "--console" not in argv and os.environ.get("ACTIVERSE_CONSOLE") != "1":
        hide_console()

    root = install_root()
    os.chdir(str(root))
    _log(f"{DISPLAY_NAME} starting — mode={'SIMULATOR' if sim else 'HARDWARE'} install_root={root}")

    if not (games_root() / "setting" / "led_parameter.dat").is_file():
        fail(f"Floor settings missing: {games_root() / 'setting' / 'led_parameter.dat'}")

    _log("stopping any previous run")
    procs.stop_all()
    time.sleep(2)

    env = os.environ.copy()
    env["USE_SERIAL_HD"] = "0" if sim else "1"
    env["API_PORT"] = str(API_PORT)
    env["WS_BRIDGE_PORT"] = str(BRIDGE_PORT)
    env["GAMES_ROOT"] = str(games_root())

    api = _spawn("api", env, root)
    time.sleep(3)
    bridge = _spawn("bridge", env, root)
    children = [api, bridge]
    procs.write_pids([os.getpid()] + [p.pid for p in children])
    _log(f"API pid={api.pid} :{API_PORT}  bridge pid={bridge.pid} :{BRIDGE_PORT}")

    def _stop_and_exit(code: int = 0) -> None:
        for p in children:
            if p.poll() is None:
                procs.kill_tree(p.pid)
        kiosk.kill_kiosk(SLUG)
        procs.free_ports()
        sys.exit(code)

    if not _wait_ui():
        _log("WARNING: UI did not respond in time; continuing")

    if not sim:
        try:
            _, body = _get(f"http://127.0.0.1:{API_PORT}/hw-debug", timeout=5)
            if not json.loads(body).get("use_serial_hd"):
                _stop_and_exit_msg = "HARDWARE MODE OFF - the floor would stay dark."
                for p in children:
                    procs.kill_tree(p.pid)
                fail(_stop_and_exit_msg)
            _log("HARDWARE MODE: ON")
        except (urllib.error.URLError, OSError, ValueError, TimeoutError):
            _log("WARNING: could not confirm hardware mode yet")

    listener = None
    if kiosk_on and not no_browser:
        listener = kiosk.HotkeyListener(SLUG)
        listener.start()
        listener.registered.wait(2)
    try:
        if not no_browser:
            kiosk.launch(f"http://127.0.0.1:{API_PORT}/", SLUG, kiosk=kiosk_on)
    except RuntimeError as exc:
        _stop_and_exit_msg = str(exc)
        for p in children:
            procs.kill_tree(p.pid)
        fail(_stop_and_exit_msg)

    _log(f"{DISPLAY_NAME} is running ({'SIMULATOR' if sim else 'HARDWARE'}). Ctrl+Shift+K exits kiosk. STOP to quit.")
    while True:
        for p in children:
            code = p.poll()
            if code is not None:
                _log(f"child pid={p.pid} exited code={code}; stopping everything")
                _stop_and_exit(1)
        time.sleep(1)

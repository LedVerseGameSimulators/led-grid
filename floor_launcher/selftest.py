"""
`LED Grid.exe --selftest` — one pass/fail report to send back from a floor PC.

Read-only: it never opens the LED serial port (that could disturb a running floor).
"""
from __future__ import annotations

import json
import os
import shelve
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import List, Tuple

from api.runtime_paths import games_root, install_root, is_frozen, simulator_static, ui_dir

from . import kiosk
from .product import API_PORT, BRIDGE_PORT, DISPLAY_NAME

Result = Tuple[str, bool, str]


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0


def run() -> int:
    out: List[Result] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        out.append((name, ok, detail))

    ir, gr = install_root(), games_root()
    check("frozen build", is_frozen(), f"install_root={ir}")
    check("UI present", (ui_dir() / "index.html").is_file(), str(ui_dir()))
    check("simulator static", simulator_static().is_dir(), str(simulator_static()))
    check("level data", (gr / "source").is_dir() and (gr / "source_group").is_dir(), str(gr))
    check("audio", any(f.suffix.lower() in (".mp3", ".wav") for f in (gr / "audio").rglob("*")), str(gr / "audio"))

    # LFS pointer stubs would make levels/audio unreadable.
    stubs = []
    for d in ("source", "source_group", "audio"):
        for f in list((gr / d).rglob("*"))[:5000]:
            if f.is_file() and f.stat().st_size < 200:
                try:
                    if f.read_bytes().startswith(b"version https://git-lfs"):
                        stubs.append(f.name)
                except OSError:
                    pass
    check("no git-lfs pointer stubs", not stubs, ", ".join(stubs[:5]))

    check("playlists file", (install_root() / "api" / "mode_playlists.json").is_file(), "api/mode_playlists.json")
    check("debug_parameter (LED port settings)", (gr / "setting" / "debug_parameter.dat").is_file(), str(gr / "setting"))

    lp = gr / "setting" / "led_parameter"
    check("floor settings file", (gr / "setting" / "led_parameter.dat").is_file(), str(lp))
    try:
        with shelve.open(str(lp), flag="r") as db:
            keys = list(db.keys())
        check("settings readable (shelve)", bool(keys), f"{len(keys)} keys")
    except Exception as exc:
        check("settings readable (shelve)", False, repr(exc))

    cfg = gr / "setting" / "activerse.json"
    rfid = os.getenv("RFID_API_URL", "")
    if not rfid and cfg.is_file():
        try:
            rfid = json.loads(cfg.read_text(encoding="utf-8")).get("rfid_api_url", "")
        except (OSError, ValueError):
            rfid = ""
    rfid = rfid or "http://localhost:9000"
    try:
        with urllib.request.urlopen(rfid.rstrip("/") + "/health", timeout=3) as r:
            check("RFID server reachable", r.status < 500, rfid)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        check("RFID server reachable", False, f"{rfid} ({exc})")

    for name, mod in (("pyserial", "serial"), ("pygame", "pygame"), ("uvicorn", "uvicorn"), ("fastapi", "fastapi")):
        try:
            __import__(mod)
            check(f"import {name}", True)
        except Exception as exc:
            check(f"import {name}", False, repr(exc))
    try:
        from serial.tools import list_ports

        ports = [p.device for p in list_ports.comports()]
        check("serial ports visible", bool(ports), ", ".join(ports) or "none")
    except Exception as exc:
        check("serial ports visible", False, repr(exc))

    check("browser (Chrome/Edge)", bool(kiosk.find_browser()), str(kiosk.find_browser()))
    for label, port in (("API", API_PORT), ("bridge", BRIDGE_PORT)):
        check(f"{label} port {port} free", _port_free(port), "in use (game running?)" if not _port_free(port) else "")

    width = max(len(n) for n, _, _ in out)
    print(f"\n{DISPLAY_NAME} self-test\n" + "-" * 60)
    for name, ok, detail in out:
        print(f"{'PASS' if ok else 'FAIL'}  {name.ljust(width)}  {detail}")
    failed = [n for n, ok, _ in out if not ok]
    print("-" * 60 + f"\n{'ALL PASS' if not failed else 'FAILED: ' + ', '.join(failed)}\n")
    return 0 if not failed else 1

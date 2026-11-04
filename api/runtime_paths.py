"""
Install-root / resource path helpers for frozen (Nuitka/PyInstaller) and dev.

When frozen, operator data (ui/, games/, simulator/) lives next to the release
root. Onedir builds may place each exe in a named subfolder (grid-api/, …);
in that case install_root() is the parent of that folder.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Named onedir folders used by packaging/stage + freeze scripts.
_FROZEN_BIN_DIRS = frozenset(
    {
        "grid-api",
        "grid-bridge",
        "LED-Grid",
        "LED Grid",
        "run_api",
        "run_bridge",
        "supervisor",
    }
)


def is_frozen() -> bool:
    """True under PyInstaller (sys.frozen) or Nuitka (__compiled__)."""
    if getattr(sys, "frozen", False):
        return True
    # Nuitka injects __compiled__ into compiled modules' globals.
    return bool(globals().get("__compiled__"))


def self_exe() -> list:
    """Command that re-launches this program (used to spawn role processes)."""
    if is_frozen():
        argv0 = Path(sys.argv[0]).resolve() if sys.argv and sys.argv[0] else None
        if argv0 is not None and argv0.is_file() and argv0.suffix.lower() != ".py":
            return [str(argv0)]
        return [sys.executable]
    return [sys.executable, "-m", "floor_launcher.entry"]


def _frozen_exe_dir() -> Path:
    argv0 = Path(sys.argv[0]).resolve() if sys.argv and sys.argv[0] else None
    if argv0 is not None and argv0.is_file() and argv0.suffix.lower() != ".py":
        return argv0.parent
    return Path(sys.executable).resolve().parent


def install_root() -> Path:
    """
    Directory that contains ui/, games/, simulator/ (and bin folders when frozen).

    Dev: led-grid repo root (parent of api/).
    Frozen: exe directory, or its parent when exe lives in a known onedir folder.
    """
    if is_frozen():
        exe_dir = _frozen_exe_dir()
        if exe_dir.name in _FROZEN_BIN_DIRS:
            return exe_dir.parent
        return exe_dir
    # api/runtime_paths.py -> api/ -> repo root
    return Path(__file__).resolve().parent.parent


def games_root() -> Path:
    """games/ data + (in dev) Python packages. Honors GAMES_ROOT env."""
    env = os.getenv("GAMES_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return install_root() / "games"


def ui_dir() -> Path:
    """
    Frontend static assets.
    Frozen/operator: install_root()/ui
    Dev: frontend/dist
    Honors UI_DIR env.
    """
    env = os.getenv("UI_DIR")
    if env:
        return Path(env).expanduser().resolve()
    if is_frozen():
        return install_root() / "ui"
    return install_root() / "frontend" / "dist"


def simulator_static() -> Path:
    """Bridge simulator static files. Honors SIMULATOR_STATIC env."""
    env = os.getenv("SIMULATOR_STATIC")
    if env:
        return Path(env).expanduser().resolve()
    return install_root() / "simulator" / "static"

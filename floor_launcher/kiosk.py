"""
Kiosk browser control — native equivalent of scripts/kiosk/*.bat|ps1.

- find_browser      <- find-browser.bat (Chrome, then Edge; PATH last)
- launch            <- open-ui.bat (isolated per-product profile, --kiosk)
- kill_kiosk        <- kill-kiosk-browser.ps1 (match the profile dir in the command line)
- HotkeyListener    <- kiosk-exit-listener.ps1 (global Ctrl+Shift+K -> kill the kiosk browser)
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional

from .product import SLUG

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


def profile_dir(slug: str = SLUG) -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "ActiverseKiosk" / slug
    return Path.home() / ".activerse-kiosk" / slug


def find_browser() -> Optional[str]:
    if sys.platform == "win32":
        pf = os.environ.get("ProgramFiles", r"C:\Program Files")
        pf86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        for c in (
            Path(pf) / r"Google\Chrome\Application\chrome.exe",
            Path(pf86) / r"Google\Chrome\Application\chrome.exe",
            Path(pf86) / r"Microsoft\Edge\Application\msedge.exe",
            Path(pf) / r"Microsoft\Edge\Application\msedge.exe",
        ):
            if c.is_file():
                return str(c)
        return shutil.which("chrome") or shutil.which("msedge")
    if sys.platform == "darwin":
        for c in (
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            str(Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ):
            if Path(c).is_file():
                return c
        return None
    return shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("microsoft-edge")


def launch(url: str, slug: str = SLUG, kiosk: bool = True) -> Optional[subprocess.Popen]:
    """Open the UI. kiosk=False (ACTIVERSE_KIOSK=0) opens the default browser."""
    if not kiosk:
        import webbrowser

        webbrowser.open(url)
        return None
    browser = find_browser()
    if not browser:
        raise RuntimeError("Chrome or Edge not found. Install Google Chrome or Microsoft Edge.")
    prof = profile_dir(slug)
    prof.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(
        [
            browser,
            "--kiosk",
            "--no-first-run",
            "--disable-session-crashed-bubble",
            "--disable-infobars",
            f"--user-data-dir={prof}",
            url,
        ]
    )


def kill_kiosk(slug: str = SLUG) -> None:
    """Kill browser processes whose command line carries this product's profile dir."""
    if sys.platform == "win32":
        needle = f"ActiverseKiosk\\{slug}"
        ps = (
            "Get-CimInstance Win32_Process -Filter \"Name = 'chrome.exe' OR Name = 'msedge.exe'\" "
            "-ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -and "
            f"($_.CommandLine -like '*{needle}*') }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId "
            "-Force -ErrorAction SilentlyContinue }"
        )
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            creationflags=CREATE_NO_WINDOW,
            capture_output=True,
        )
    else:
        subprocess.run(["pkill", "-f", f".activerse-kiosk/{slug}"], capture_output=True)


class HotkeyListener(threading.Thread):
    """Global Ctrl+Shift+K -> kill the kiosk browser (Windows). No-op elsewhere."""

    MOD_CONTROL = 0x0002
    MOD_SHIFT = 0x0004
    VK_K = 0x4B
    WM_HOTKEY = 0x0312
    WM_QUIT = 0x0012

    def __init__(self, slug: str = SLUG):
        super().__init__(name="kiosk-exit-hotkey", daemon=True)
        self.slug = slug
        self._tid = None
        self.registered = threading.Event()
        self.ok = False

    def run(self) -> None:
        if sys.platform != "win32":
            return
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        self._tid = kernel32.GetCurrentThreadId()
        self.ok = bool(user32.RegisterHotKey(None, 1, self.MOD_CONTROL | self.MOD_SHIFT, self.VK_K))
        self.registered.set()
        if not self.ok:
            return
        msg = wintypes.MSG()
        try:
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == self.WM_HOTKEY:
                    kill_kiosk(self.slug)
                    break
        finally:
            user32.UnregisterHotKey(None, 1)

    def stop(self) -> None:
        if sys.platform == "win32" and self._tid:
            import ctypes

            ctypes.windll.user32.PostThreadMessageW(self._tid, self.WM_QUIT, 0, 0)

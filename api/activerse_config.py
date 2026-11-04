"""
Runtime (per-PC) UI configuration for packaged builds.

The React bundle is built once in CI, so per-floor values (the central RFID
server address) cannot be baked in at build time. They are injected into
index.html when it is served, from (highest priority first):

1. RFID_API_URL environment variable
2. games/setting/activerse.json  {"rfid_api_url": "http://192.168.1.106:9000"}

The settings dir is the one directory an update never overwrites.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from .runtime_paths import games_root


def _config_file() -> Path:
    return games_root() / "setting" / "activerse.json"


def load_runtime_config() -> Dict[str, str]:
    cfg: Dict[str, str] = {}
    path = _config_file()
    try:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                url = data.get("rfid_api_url")
                if isinstance(url, str) and url.strip():
                    cfg["rfidApiUrl"] = url.strip()
    except (OSError, ValueError):
        pass
    env_url = os.getenv("RFID_API_URL", "").strip()
    if env_url:
        cfg["rfidApiUrl"] = env_url
    return cfg


def inject_runtime_config(html: str) -> str:
    """Insert window.__ACTIVERSE__ before the first </head>."""
    payload = json.dumps(load_runtime_config()).replace("</", "<\\/")
    tag = f"<script>window.__ACTIVERSE__={payload};</script>"
    if "</head>" in html:
        return html.replace("</head>", tag + "</head>", 1)
    return tag + html

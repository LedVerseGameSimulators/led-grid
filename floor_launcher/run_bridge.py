"""Bridge role: same as `python ws_bridge.py` from the repo root."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> None:
    from api.runtime_paths import games_root, install_root, simulator_static

    ir = install_root()
    os.environ.setdefault("GAMES_ROOT", str(games_root()))
    os.environ.setdefault("SIMULATOR_STATIC", str(simulator_static()))
    os.chdir(str(ir))
    if str(ir) not in sys.path:
        sys.path.insert(0, str(ir))

    import uvicorn
    import ws_bridge

    print(f"[bridge] listening on {ws_bridge.HOST}:{ws_bridge.PORT}", flush=True)
    uvicorn.run(ws_bridge.app, host=ws_bridge.HOST, port=ws_bridge.PORT, log_level="info", loop="asyncio")


if __name__ == "__main__":
    main()

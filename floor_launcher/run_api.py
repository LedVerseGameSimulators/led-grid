"""API role: same as scripts/run-api-hardware.bat (uvicorn api.main:app, 0.0.0.0)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> None:
    from api.runtime_paths import games_root, install_root

    from .product import API_PORT

    ir = install_root()
    gr = games_root()
    os.environ.setdefault("GAMES_ROOT", str(gr))

    # The bat runs the API with cwd = repo root; keep that (cwd-relative logs/ etc.).
    # Engine settings are read via absolute GAMES_ROOT paths, same as on the floor today.
    os.chdir(str(ir))
    (ir / "logs").mkdir(exist_ok=True)
    for p in (str(ir), str(gr)):
        if p not in sys.path:
            sys.path.insert(0, p)

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", str(API_PORT)))

    import uvicorn
    from api.main import app

    print(f"[api] USE_SERIAL_HD={os.environ.get('USE_SERIAL_HD')} GAMES_ROOT={gr} cwd={ir}", flush=True)
    print(f"[api] listening on {host}:{port}", flush=True)
    uvicorn.run(app, host=host, port=port, log_level="info", loop="asyncio")


if __name__ == "__main__":
    main()

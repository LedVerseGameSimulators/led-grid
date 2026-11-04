"""
Single entry point for the packaged game (one exe, several roles):

  LED Grid.exe                 start everything (what START_GAME.bat did)
  LED Grid.exe --sim           same, simulator only (no serial)
  LED Grid.exe --stop          what STOP_GAME.bat did
  LED Grid.exe --selftest      read-only health report
  LED Grid.exe --role api|bridge   internal: spawned by the supervisor
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main(argv=None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--role" in argv:
        role = argv[argv.index("--role") + 1]
        if role == "api":
            from floor_launcher import run_api

            run_api.main()
        elif role == "bridge":
            from floor_launcher import run_bridge

            run_bridge.main()
        else:
            sys.exit(f"unknown role: {role}")
        return

    if "--selftest" in argv:
        from floor_launcher import selftest

        sys.exit(selftest.run())

    if "--stop" in argv:
        from floor_launcher import procs

        procs.stop_all()
        print("Stopped.")
        return

    from floor_launcher import supervisor

    supervisor.main(argv)


if __name__ == "__main__":
    main()

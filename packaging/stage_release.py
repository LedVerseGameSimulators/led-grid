#!/usr/bin/env python3
"""
Cross-platform operator-package stager (used by the Windows build; the macOS
shell stager does the same job). Copies the data allowlist next to the frozen
exe directory. NEVER ships .py/.pyc, local dev DBs, or untracked files.

usage: stage_release.py <stage_dir> <frozen_dist_dir>
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIRS = ("games/source", "games/source_group", "games/setting", "games/audio")
EXCLUDE = re.compile(r"\.(py|pyc|mp4|md|rar)$|/ledplaydb\.sqlite$", re.I)
STOP_BAT = '@echo off\r\n"%~dp0LED Grid.exe" --stop\r\n'


def main(stage: Path, dist: Path) -> int:
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    # frozen runtime (exe + dlls) at the root, next to data
    shutil.copytree(dist, stage, dirs_exist_ok=True)

    # UI
    shutil.copytree(ROOT / "frontend" / "dist", stage / "ui")

    # data: tracked files only (real LFS content once checked out)
    out = subprocess.run(
        ["git", "ls-files", "-z", "--", *DATA_DIRS], cwd=ROOT, capture_output=True, check=True
    ).stdout.decode("utf-8")
    n = 0
    for rel in filter(None, out.split("\0")):
        if EXCLUDE.search(rel):
            continue
        dst = stage / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)
        n += 1

    # api data (playlist order; JSON, no code)
    (stage / "api").mkdir(exist_ok=True)
    shutil.copy2(ROOT / "api" / "mode_playlists.json", stage / "api" / "mode_playlists.json")

    # simulator static (bridge)
    sim = ROOT / "simulator" / "static"
    if sim.is_dir():
        shutil.copytree(sim, stage / "simulator" / "static")

    (stage / "STOP_GAME.bat").write_bytes(STOP_BAT.encode("ascii"))
    shutil.copy2(ROOT / "packaging" / "README_OPERATOR.txt", stage / "README_OPERATOR.txt")

    bad = [p for p in stage.rglob("*") if p.suffix.lower() in (".py", ".pyc")]
    if bad:
        print("ERROR: Python source/bytecode in operator package:")
        for p in bad[:20]:
            print("  ", p)
        return 1
    print(f"staged {n} data files -> {stage}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()))

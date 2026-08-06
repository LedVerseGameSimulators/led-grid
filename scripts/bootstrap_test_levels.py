#!/usr/bin/env python3
"""Bootstrap tiny gameplay .led fixtures for effects session-loop tests."""

from __future__ import annotations

import os
import pickle
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAMES = ROOT / "games"
for p in (ROOT, GAMES):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import dbm.dumb  # noqa: E402

from model.game import Game  # noqa: E402
from model.group import Group  # noqa: E402
from model.setting import Color, Setting  # noqa: E402

ROWS, COLS = 16, 26
BLUE3 = [list(Color.BLUE)] * 3
RED3 = [list(Color.RED)] * 3
ACTIVITY = [(0, ROWS), (0, COLS)]


def _group(name, cells, color, *, end: float = 30.0) -> Group:
    return Group(
        name,
        member=set(cells),
        start_time_sec=0.0,
        end_time_sec=end,
        color=color,
        speed=0,
        direct=Setting.STATIC,
        edge_run_into=Setting.BACK,
        gtype=Setting.FLOOR_LIGHT,
        scale=Setting.SIDE_NONE,
        start_area=1,
        activity_area=ACTIVITY,
    )


def _game(name: str) -> Game:
    g = Game(
        name,
        row=ROWS,
        col=COLS,
        zone_row_from=0,
        zone_row_to=ROWS,
        zone_col_from=0,
        zone_col_to=COLS,
        zone_scale=Setting.SIDE_NONE,
        wall_light=Setting.NO,
        screen=Setting.NO,
    )
    g.play_order = False
    return g


def _write(path: Path, groups: dict, game: Game) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shelf_dir = Path(tmp) / "level"
        shelf_dir.mkdir()
        shelf_path = str(shelf_dir / "game_file")
        db = dbm.dumb.open(shelf_path, "n")
        try:
            db["para_key_game"] = pickle.dumps(game, protocol=4)
            db["dict_group"] = pickle.dumps(groups, protocol=4)
            db.sync()
        finally:
            db.close()
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _dirs, files in os.walk(tmp):
                for fname in files:
                    full = Path(root) / fname
                    zf.write(full, full.relative_to(tmp))


def main() -> int:
    out = ROOT / "tests" / "fixtures" / "levels"
    # One blue tile — quick clear when stepped on (T2, T6, T8).
    _write(
        out / "quick_clear.led",
        {"goal": _group("goal", {(4, 4)}, BLUE3, end=30.0)},
        _game("quick_clear"),
    )
    # Second level for mid-session advance (T2).
    _write(
        out / "level_b.led",
        {"goal": _group("goal", {(5, 5)}, BLUE3, end=30.0)},
        _game("level_b"),
    )
    # Red hazard for life loss (T3, T5, T7 during playing for T8 contrast).
    _write(
        out / "hazard.led",
        {
            "goal": _group("goal", {(4, 4)}, BLUE3, end=30.0),
            "red": _group("red", {(6, 6)}, RED3, end=30.0),
        },
        _game("hazard"),
    )
    print(f"Wrote test levels under {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

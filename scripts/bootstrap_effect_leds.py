#!/usr/bin/env python3
"""Bootstrap countdown / level_clear / level_fail .led archives at native 16×26."""

from __future__ import annotations

import argparse
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
GREEN = Color.GREEN
BLUE = Color.BLUE
RED = Color.RED
BLACK3 = [list(Color.BLACK)] * 3
GREEN3 = [list(GREEN)] * 3
BLUE3 = [list(BLUE)] * 3
RED3 = [list(RED)] * 3
ACTIVITY = [(0, ROWS), (0, COLS)]


def _all_cells() -> set[tuple[int, int]]:
    return {(r, c) for r in range(ROWS) for c in range(COLS)}


# Simple 8×8 block digits (rows 0-7, cols 0-7); placed at row_offset, col_offset.
_DIGIT_3 = {
    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
    (1, 5), (2, 5),
    (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
    (4, 5), (5, 5),
    (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
}
_DIGIT_2 = {
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
    (1, 5), (2, 5),
    (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
    (4, 0), (5, 0),
    (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
}
_DIGIT_1 = {
    (0, 3), (0, 4),
    (1, 2), (1, 3), (1, 4),
    (2, 1), (2, 3), (2, 4),
    (3, 0), (3, 3), (3, 4),
    (4, 3), (4, 4),
    (5, 3), (5, 4),
    (6, 3), (6, 4),
    (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5),
}


def _center_glyph(cells: set[tuple[int, int]], row_off: int = 4, col_off: int = 9) -> set[tuple[int, int]]:
    return {(row_off + r, col_off + c) for r, c in cells}


def _floor_group(name, cells, color, *, start: float, end: float) -> Group:
    return Group(
        name,
        member=set(cells),
        start_time_sec=start,
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


def build_countdown_groups(*, digit_sec: float = 0.8) -> dict[str, Group]:
    t = digit_sec
    return {
        "digit_3": _floor_group("digit_3", _center_glyph(_DIGIT_3), GREEN3, start=0.0, end=t),
        "digit_2": _floor_group("digit_2", _center_glyph(_DIGIT_2), GREEN3, start=t, end=2 * t),
        "digit_1": _floor_group("digit_1", _center_glyph(_DIGIT_1), GREEN3, start=2 * t, end=3 * t),
    }


def build_solid_group(name: str, rgb: tuple[int, int, int], *, hold_sec: float) -> dict[str, Group]:
    rings = [list(rgb)] * 3
    return {
        name: _floor_group(name, _all_cells(), rings, start=0.0, end=hold_sec),
    }


def build_game(name: str) -> Game:
    game = Game(
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
    game.play_order = False
    return game


def _write_shelf(shelf_path: str, game: Game, groups: dict) -> None:
    db = dbm.dumb.open(shelf_path, "n")
    try:
        db["para_key_game"] = pickle.dumps(game, protocol=4)
        db["dict_group"] = pickle.dumps(groups, protocol=4)
        db.sync()
    finally:
        db.close()


def write_archive(path: Path, groups: dict, game: Game) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        shelf_dir = Path(tmp) / "effect"
        shelf_dir.mkdir()
        shelf_path = str(shelf_dir / "game_file")
        _write_shelf(shelf_path, game, groups)
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _dirs, files in os.walk(tmp):
                for fname in files:
                    full = Path(root) / fname
                    zf.write(full, full.relative_to(tmp))
    print(f"Wrote {path} ({path.stat().st_size} bytes)")


def bootstrap(out_dir: Path, *, fast: bool = False) -> None:
    digit = 0.15 if fast else 0.8
    hold = 0.2 if fast else 2.5
    write_archive(out_dir / "countdown.led", build_countdown_groups(digit_sec=digit), build_game("countdown"))
    write_archive(out_dir / "level_clear.led", build_solid_group("clear", BLUE, hold_sec=hold), build_game("level_clear"))
    write_archive(out_dir / "level_fail.led", build_solid_group("fail", RED, hold_sec=hold), build_game("level_fail"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=GAMES / "source" / "effects")
    parser.add_argument("--fast", action="store_true", help="Short timings for pytest fixtures")
    args = parser.parse_args()
    bootstrap(args.out, fast=args.fast)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

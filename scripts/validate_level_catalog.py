#!/usr/bin/env python3
"""Validate every shipped Grid level through the production load/scale path."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from numbers import Integral, Real
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GAMES_ROOT = ROOT / "games"
for import_root in (ROOT, GAMES_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from api.game_manager import _load_level_boards, _load_level_file  # noqa: E402
from api.level_scaler import prepare_level_for_platform  # noqa: E402


FLOOR_LIGHT = "floor_light"
WALL_LIGHT = "wall_light"
SCREEN_LIGHT = "screen_light"
P1_COLOR = (0, 0, 254)
P2_COLOR = (254, 128, 0)
SCOREABLE_COLORS = frozenset((P1_COLOR, P2_COLOR))
DEFAULT_ROWS = 16
DEFAULT_COLS = 26
PRODUCTION_1P_TIERS = frozenset(("-", "--", "---"))

# These exact legacy boards are shipped below a nested archival directory but
# are not reachable from the production 37-file 1P marathon. The reason text
# is intentionally exact: any different failure remains unexplained.
KNOWN_LEGACY_EXCLUSIONS = {
    (
        "---/---/JZDS002.led",
        "JZDS0022",
    ): "no scoreable floor members on an expected playable board",
    (
        "---/---/YC16.led",
        "YC162",
    ): (
        "production preparation failed: level '隐藏游戏16', group '蓝色(1)': "
        "group '蓝色(1)' activity_area col range must be non-empty and ordered, "
        "got (89, 24)"
    ),
    (
        "---/---/ZZDK01.ledb",
        "ZZ032",
    ): "group '绿色14(81)' has invalid activity time range (569.6, 560.4)",
}


class CatalogValidationError(ValueError):
    """One archive does not satisfy the playable-board contract."""


@dataclass(frozen=True)
class GameplayBoard:
    """One deterministic play_order=False shelf from an archive."""

    identity: str
    groups: dict[Any, Any]
    game: Any


def discover_level_archives(source_root: Path) -> list[Path]:
    """Return every .led/.ledb below source_root in stable path order."""
    source_root = Path(source_root)
    return sorted(
        (
            path
            for path in source_root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".led", ".ledb"}
        ),
        key=lambda path: path.as_posix(),
    )


def discover_main_gameplay_boards(path: Path) -> list[GameplayBoard]:
    """Load every main board using the production deterministic archive reader."""
    return [
        GameplayBoard(identity, groups, game)
        for identity, groups, game in _load_level_boards(path)
    ]


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise CatalogValidationError(f"{label} must be an integer, got {value!r}")
    return int(value)


def _dimensions(game: Any) -> tuple[int, int]:
    rows = _integer(getattr(game, "row", None), "authored rows")
    cols = _integer(getattr(game, "col", None), "authored cols")
    if rows <= 0 or cols <= 0:
        raise CatalogValidationError(
            f"authored dimensions must be positive, got {rows}x{cols}"
        )
    return rows, cols


def _main_color(group: Any) -> tuple[int, int, int] | None:
    color = getattr(group, "color", None)
    try:
        candidate = color[1] if color and isinstance(color[0], (list, tuple)) else color
        if not isinstance(candidate, (list, tuple)) or len(candidate) < 3:
            return None
        channels = tuple(_integer(value, "color channel") for value in candidate[:3])
    except (IndexError, TypeError):
        return None
    return channels


def _validate_time_range(group: Any, name: str) -> None:
    start = getattr(group, "start_time_sec", None)
    stop = getattr(group, "end_time_sec", None)
    if (
        isinstance(start, bool)
        or isinstance(stop, bool)
        or not isinstance(start, Real)
        or not isinstance(stop, Real)
        or not math.isfinite(float(start))
        or not math.isfinite(float(stop))
        or start > stop
    ):
        raise CatalogValidationError(
            f"group {name!r} has invalid activity time range ({start!r}, {stop!r})"
        )


def _floor_cells(
    groups: dict[Any, Any],
    *,
    rows: int,
    cols: int,
    phase: str,
) -> list[tuple[int, int]]:
    cells: list[tuple[int, int]] = []
    for key, group in groups.items():
        name = str(getattr(group, "name", key))
        _validate_time_range(group, name)
        if getattr(group, "type", None) != FLOOR_LIGHT:
            continue
        members = getattr(group, "start_member", None)
        if members is None:
            continue
        try:
            values = list(members)
        except TypeError as exc:
            raise CatalogValidationError(
                f"{phase} floor group {name!r} members are not iterable"
            ) from exc
        for index, member in enumerate(values):
            if not isinstance(member, (tuple, list)) or len(member) != 2:
                raise CatalogValidationError(
                    f"{phase} floor group {name!r} member {index} "
                    f"must be a (row, col) pair, got {member!r}"
                )
            row = _integer(member[0], f"{phase} floor group {name!r} row")
            col = _integer(member[1], f"{phase} floor group {name!r} col")
            if not (0 <= row < rows and 0 <= col < cols):
                raise CatalogValidationError(
                    f"{phase} floor group {name!r} member ({row}, {col}) "
                    f"is outside {rows}x{cols}"
                )
            cells.append((row, col))
    return cells


def _zone(game: Any, rows: int, cols: int) -> list[int]:
    values = [
        _integer(getattr(game, "zone_row_from", None), "zone row start"),
        _integer(getattr(game, "zone_row_to", None), "zone row stop"),
        _integer(getattr(game, "zone_col_from", None), "zone col start"),
        _integer(getattr(game, "zone_col_to", None), "zone col stop"),
    ]
    if not (0 <= values[0] < values[1] <= rows):
        raise CatalogValidationError(
            f"invalid transformed row zone ({values[0]}, {values[1]}) for {rows} rows"
        )
    if not (0 <= values[2] < values[3] <= cols):
        raise CatalogValidationError(
            f"invalid transformed col zone ({values[2]}, {values[3]}) for {cols} cols"
        )
    return values


def _snapshot(groups: dict[Any, Any], game: Any) -> dict[str, Any]:
    group_states = []
    for key, group in sorted(groups.items(), key=lambda item: str(item[0])):
        members = getattr(group, "start_member", None)
        if isinstance(members, (set, list, tuple)):
            canonical_members = sorted(
                [list(member) if isinstance(member, (tuple, list)) else member
                 for member in members],
                key=lambda member: json.dumps(member, ensure_ascii=False),
            )
        else:
            canonical_members = members
        area = getattr(group, "activity_area", None)
        canonical_area = (
            [list(bounds) for bounds in area]
            if isinstance(area, (list, tuple))
            else area
        )
        group_states.append(
            {
                "key": str(key),
                "name": str(getattr(group, "name", key)),
                "type": getattr(group, "type", None),
                "members": canonical_members,
                "activity_area": canonical_area,
                "scale": getattr(group, "scale", None),
                "start_area": getattr(group, "start_area", None),
                "start_time_sec": getattr(group, "start_time_sec", None),
                "end_time_sec": getattr(group, "end_time_sec", None),
                "color": _main_color(group),
            }
        )
    return {
        "dimensions": [game.row, game.col],
        "zone": [
            game.zone_row_from,
            game.zone_row_to,
            game.zone_col_from,
            game.zone_col_to,
        ],
        "groups": group_states,
    }


def _digest(snapshot: dict[str, Any]) -> str:
    payload = json.dumps(
        snapshot,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _prepare_loaded(groups: dict[Any, Any], game: Any, rows: int, cols: int):
    if game is None:
        raise CatalogValidationError(
            "production raw loader could not find a main gameplay board"
        )
    if not hasattr(groups, "items"):
        raise CatalogValidationError("loaded groups are not a mapping")
    if not groups:
        raise CatalogValidationError("empty group mapping")
    authored_rows, authored_cols = _dimensions(game)
    _floor_cells(
        groups,
        rows=authored_rows,
        cols=authored_cols,
        phase="authored",
    )
    try:
        prepared_groups, prepared_game = prepare_level_for_platform(
            groups,
            game,
            target_rows=rows,
            target_cols=cols,
            enable_wall_light=False,
            enable_screen_light=False,
        )
    except Exception as exc:
        raise CatalogValidationError(f"production preparation failed: {exc}") from exc
    return groups, game, prepared_groups, prepared_game


def _load_and_prepare(path: Path, rows: int, cols: int):
    groups, game = _load_level_file(path)
    if groups is None or game is None:
        raise CatalogValidationError(
            "production raw loader could not find a main gameplay board"
        )
    return _prepare_loaded(groups, game, rows, cols)


def _report_from_runs(
    path: Path,
    board_identity: str,
    runs: list[tuple[dict[Any, Any], Any, dict[Any, Any], Any]],
    target_rows: int,
    target_cols: int,
) -> dict[str, Any]:
    first_raw, first_game, first_groups, first_prepared_game = runs[0]
    snapshots = [_snapshot(run[2], run[3]) for run in runs]
    if snapshots[0] != snapshots[1]:
        raise CatalogValidationError("nondeterministic output across two fresh reloads")

    authored_rows, authored_cols = _dimensions(first_game)
    floor_groups = [
        group
        for group in first_groups.values()
        if getattr(group, "type", None) == FLOOR_LIGHT
    ]
    cells = _floor_cells(
        first_groups,
        rows=target_rows,
        cols=target_cols,
        phase="transformed",
    )
    if not floor_groups:
        raise CatalogValidationError("no retained floor groups")
    if not cells:
        raise CatalogValidationError("no retained floor members")

    scoreable_groups = [
        group for group in floor_groups if _main_color(group) in SCOREABLE_COLORS
    ]
    scoreable_members = sum(
        len(getattr(group, "start_member", None) or ())
        for group in scoreable_groups
    )
    if not scoreable_members:
        raise CatalogValidationError(
            "no scoreable floor members on an expected playable board"
        )

    p1_colors = sorted(
        {_main_color(group) for group in floor_groups if _main_color(group) == P1_COLOR}
    )
    p2_colors = sorted(
        {_main_color(group) for group in floor_groups if _main_color(group) == P2_COLOR}
    )
    zone = _zone(first_prepared_game, target_rows, target_cols)
    bounds = {
        "row_min": min(row for row, _ in cells),
        "row_max": max(row for row, _ in cells),
        "col_min": min(col for _, col in cells),
        "col_max": max(col for _, col in cells),
    }
    return {
        "path": path.as_posix(),
        "board": board_identity,
        "board_name": str(getattr(first_game, "name", board_identity)),
        "authored_dimensions": [authored_rows, authored_cols],
        "scale_modes": sorted(
            {
                getattr(group, "scale", None)
                for group in first_raw.values()
                if getattr(group, "type", None) == FLOOR_LIGHT
            },
            key=lambda value: str(value),
        ),
        "transformed_bounds": bounds,
        "retained_floor_groups": len(floor_groups),
        "retained_floor_members": len(cells),
        "ignored_wall_groups": sum(
            getattr(group, "type", None) == WALL_LIGHT
            for group in first_raw.values()
        ),
        "ignored_screen_groups": sum(
            getattr(group, "type", None) == SCREEN_LIGHT
            for group in first_raw.values()
        ),
        "scoreable_groups": len(scoreable_groups),
        "scoreable_members": scoreable_members,
        "p1_colors": [list(color) for color in p1_colors],
        "p2_colors": [list(color) for color in p2_colors],
        "multiplayer": bool(p1_colors and p2_colors),
        "zone": zone,
        "digest": _digest(snapshots[0]),
    }


def validate_archive(
    path: Path,
    *,
    target_rows: int = DEFAULT_ROWS,
    target_cols: int = DEFAULT_COLS,
) -> dict[str, Any]:
    """Reload and prepare one archive twice, returning its validation report."""
    path = Path(path)
    runs = [
        _load_and_prepare(path, target_rows, target_cols),
        _load_and_prepare(path, target_rows, target_cols),
    ]
    return _report_from_runs(
        path, ".", runs, target_rows, target_cols
    )


def validate_archive_boards(
    path: Path,
    *,
    target_rows: int = DEFAULT_ROWS,
    target_cols: int = DEFAULT_COLS,
) -> dict[str, Any]:
    """Validate every deterministic main board in one archive twice."""
    path = Path(path)
    board_runs = [
        discover_main_gameplay_boards(path),
        discover_main_gameplay_boards(path),
    ]
    identities = [[board.identity for board in run] for run in board_runs]
    if not identities[0]:
        return {
            "reports": [],
            "failures": [
                {
                    "path": path.as_posix(),
                    "board": None,
                    "board_name": None,
                    "error": "production raw loader could not find a main gameplay board",
                }
            ],
            "board_count": 0,
        }
    if identities[0] != identities[1]:
        return {
            "reports": [],
            "failures": [
                {
                    "path": path.as_posix(),
                    "board": None,
                    "board_name": None,
                    "error": (
                        "nondeterministic main board identities across two fresh "
                        f"reloads: {identities[0]!r} != {identities[1]!r}"
                    ),
                }
            ],
            "board_count": max(len(run) for run in board_runs),
        }

    selected_groups, selected_game = _load_level_file(path)
    canonical = board_runs[0][0]
    if (
        selected_groups is None
        or selected_game is None
        or _snapshot(selected_groups, selected_game)
        != _snapshot(canonical.groups, canonical.game)
    ):
        return {
            "reports": [],
            "failures": [
                {
                    "path": path.as_posix(),
                    "board": canonical.identity,
                    "board_name": str(getattr(canonical.game, "name", canonical.identity)),
                    "error": (
                        "production loader selection does not match deterministic "
                        f"canonical board {canonical.identity!r}"
                    ),
                }
            ],
            "board_count": len(identities[0]),
        }

    reports = []
    failures = []
    for board_index, identity in enumerate(identities[0]):
        outcomes = []
        for reload_index in range(2):
            board = board_runs[reload_index][board_index]
            try:
                outcomes.append(
                    (
                        "ok",
                        _prepare_loaded(
                            board.groups,
                            board.game,
                            target_rows,
                            target_cols,
                        ),
                    )
                )
            except Exception as exc:
                outcomes.append(("error", str(exc)))

        board_name = str(
            getattr(board_runs[0][board_index].game, "name", identity)
        )
        if outcomes[0][0] != outcomes[1][0]:
            error = "nondeterministic preparation success/failure across fresh reloads"
        elif outcomes[0][0] == "error":
            if outcomes[0][1] != outcomes[1][1]:
                error = (
                    "nondeterministic preparation errors across fresh reloads: "
                    f"{outcomes[0][1]!r} != {outcomes[1][1]!r}"
                )
            else:
                error = outcomes[0][1]
        else:
            try:
                reports.append(
                    _report_from_runs(
                        path,
                        identity,
                        [outcomes[0][1], outcomes[1][1]],
                        target_rows,
                        target_cols,
                    )
                )
                continue
            except Exception as exc:
                error = str(exc)
        failures.append(
            {
                "path": path.as_posix(),
                "board": identity,
                "board_name": board_name,
                "error": error,
            }
        )
    return {
        "reports": reports,
        "failures": failures,
        "board_count": len(identities[0]),
    }


def _archive_identity(path: Path, source_root: Path) -> str:
    try:
        return path.resolve().relative_to(source_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _is_production_1p_archive(identity: str, path: Path) -> bool:
    parts = Path(identity).parts
    return (
        len(parts) == 2
        and parts[0] in PRODUCTION_1P_TIERS
        and path.suffix.lower() == ".led"
    )


def validate_catalog(
    source_root: Path,
    *,
    target_rows: int = DEFAULT_ROWS,
    target_cols: int = DEFAULT_COLS,
) -> dict[str, Any]:
    """Validate all discovered archives without stopping at the first failure."""
    source_root = Path(source_root)
    reports = []
    failures = []
    known_exclusions = []
    processed_boards = 0
    production_archives = 0
    production_boards = 0
    production_failures = []
    archives = discover_level_archives(source_root)
    for path in archives:
        identity = _archive_identity(path, source_root)
        in_production = _is_production_1p_archive(identity, path)
        if in_production:
            production_archives += 1
        archive_result = validate_archive_boards(
            path,
            target_rows=target_rows,
            target_cols=target_cols,
        )
        processed_boards += archive_result["board_count"]
        if in_production:
            production_boards += archive_result["board_count"]
        for report in archive_result["reports"]:
            report["archive"] = identity
            report["production_sequence"] = in_production
            reports.append(report)
        for failure in archive_result["failures"]:
            failure["archive"] = identity
            key = (identity, failure["board"])
            if KNOWN_LEGACY_EXCLUSIONS.get(key) == failure["error"]:
                failure["policy"] = "known_nested_legacy_exclusion"
                known_exclusions.append(failure)
            else:
                failures.append(failure)
                if in_production:
                    production_failures.append(failure)
    return {
        "source": source_root.as_posix(),
        "target_dimensions": [target_rows, target_cols],
        "processed": len(archives),
        "processed_archives": len(archives),
        "processed_boards": processed_boards,
        "valid": len(reports),
        "failed": len(failures),
        "known_excluded": len(known_exclusions),
        "reports": reports,
        "failures": failures,
        "known_exclusions": known_exclusions,
        "production_sequence": {
            "archives": production_archives,
            "boards": production_boards,
            "failed": len(production_failures),
            "failures": production_failures,
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=GAMES_ROOT / "source",
        help="catalog root (default: games/source)",
    )
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat documented known legacy exclusions as failures",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print one concise metadata line per valid archive",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = validate_catalog(
        args.source,
        target_rows=args.rows,
        target_cols=args.cols,
    )
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        if args.verbose:
            for report in result["reports"]:
                print(
                    f"OK {report['path']}#{report.get('board', '.')}: "
                    f"{report['authored_dimensions'][0]}x"
                    f"{report['authored_dimensions'][1]} -> "
                    f"{args.rows}x{args.cols}; "
                    f"floor={report['retained_floor_groups']}/"
                    f"{report['retained_floor_members']}; "
                    f"scoreable={report['scoreable_groups']}/"
                    f"{report['scoreable_members']}; "
                    f"digest={report['digest'][:12]}"
                )
        print(
            f"Validated {result.get('processed_archives', result.get('processed', 0))} "
            f"archive(s), {result.get('processed_boards', result.get('processed', 0))} "
            f"board(s): {result['valid']} valid, {result['failed']} failed, "
            f"{result.get('known_excluded', 0)} known legacy exclusion(s)."
        )
        if result.get("known_exclusions"):
            print("Known legacy exclusions:", file=sys.stderr)
            for exclusion in result["known_exclusions"]:
                print(
                    f"- {exclusion['path']}#{exclusion['board']}: "
                    f"{exclusion['error']}",
                    file=sys.stderr,
                )
        if result["failures"]:
            print("Failures:", file=sys.stderr)
            for failure in result["failures"]:
                print(
                    f"- {failure['path']}#{failure.get('board')}: {failure['error']}",
                    file=sys.stderr,
                )
    return 1 if result["failures"] or (
        args.strict and result.get("known_exclusions")
    ) else 0


if __name__ == "__main__":
    raise SystemExit(main())

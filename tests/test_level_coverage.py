"""Playlist coverage, strip-adapt regression, and parent-parity guards."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

from api.game_manager import _level_progress_action, _load_level_file
from api.level_scaler import prepare_level_for_platform, should_strip_adapt_level
from scripts.validate_level_catalog import (
    P1_COLOR,
    P2_COLOR,
    _main_color,
    _snapshot,
    discover_level_archives,
)


ROOT = Path(__file__).resolve().parents[1]
PLAYLISTS = ROOT / "api" / "mode_playlists.json"
TARGET_ROWS = 16
TARGET_COLS = 26
FLOOR_LIGHT = "floor_light"
PARENT_SCALER_REV = "319c7d9"
PARENT_SCALER_PATH = Path(f"/tmp/grid_parent_{PARENT_SCALER_REV}/api/level_scaler.py")

PREPARE_SKIP_ARCHIVES = {
    "games/source/---/---/YC16.led": (
        "corrupt activity_area col range (89, 24); not in mode_playlists.json"
    ),
}

JZDS_ARCHIVES = tuple(
    f"games/source/---/---/JZDS00{index}.led" for index in range(1, 6)
)


def _prepare(groups, game):
    return prepare_level_for_platform(
        groups,
        game,
        target_rows=TARGET_ROWS,
        target_cols=TARGET_COLS,
        enable_wall_light=False,
        enable_screen_light=False,
        platform_corner_line_start=0,
    )


def _digest(groups, game):
    return hashlib.sha256(repr(_snapshot(groups, game)).encode()).hexdigest()


def _parent_scaler_module():
    if not PARENT_SCALER_PATH.is_file():
        PARENT_SCALER_PATH.parent.mkdir(parents=True, exist_ok=True)
        source = subprocess.check_output(
            ["git", "show", f"{PARENT_SCALER_REV}:api/level_scaler.py"],
            cwd=ROOT,
            text=True,
        )
        PARENT_SCALER_PATH.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(
        "parent_level_scaler",
        PARENT_SCALER_PATH,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _all_shipped_archives():
    paths = []
    for source_root in (ROOT / "games" / "source", ROOT / "games" / "source_group"):
        paths.extend(discover_level_archives(source_root))
    return paths


def _scoreable_member_count(groups, *, multiplayer: bool):
    colors = {P2_COLOR, P1_COLOR} if multiplayer else {P1_COLOR}
    total = 0
    for group in groups.values():
        if getattr(group, "type", None) != FLOOR_LIGHT:
            continue
        if _main_color(group) not in colors:
            continue
        total += len(getattr(group, "start_member", None) or ())
    return total


def _playlist_entries():
    data = json.loads(PLAYLISTS.read_text(encoding="utf-8"))
    for mode, entries in data.items():
        for entry in entries:
            yield mode, entry["id"], entry["path"]


def _span_col_percent(groups):
    cols = []
    for group in groups.values():
        if getattr(group, "type", None) != FLOOR_LIGHT:
            continue
        cols.extend(col for _, col in (getattr(group, "start_member", None) or ()))
    if not cols:
        return 0.0
    return (max(cols) - min(cols) + 1) / TARGET_COLS * 100.0


@pytest.mark.parametrize(("mode", "level_id", "relative_path"), list(_playlist_entries()))
def test_playlist_levels_have_scoreable_tiles_after_prepare(mode, level_id, relative_path):
    groups, game = _load_level_file(ROOT / relative_path)
    prepared_groups, prepared_game = _prepare(groups, game)
    multiplayer = relative_path.lower().endswith(".ledb")
    assert _scoreable_member_count(prepared_groups, multiplayer=multiplayer) > 0, level_id


def test_zzdk01_is_not_vacuous_after_prepare():
    groups, game = _load_level_file(ROOT / "games/source/---/---/ZZDK01.ledb")
    prepared_groups, _ = _prepare(groups, game)
    assert _scoreable_member_count(prepared_groups, multiplayer=True) > 0
    action, _next, remaining = _level_progress_action(
        prepared_groups,
        total_pass=2.0,
        multiplayer=True,
        active_goal_cells=set(),
        active_goal2_cells=set(),
    )
    assert remaining > 0
    assert action != "clear"


@pytest.mark.parametrize("relative_path", JZDS_ARCHIVES)
def test_jzds_prepared_output_matches_parent(relative_path):
    parent = _parent_scaler_module()
    groups, game = _load_level_file(ROOT / relative_path)
    parent_groups, parent_game = parent.prepare_level_for_platform(
        groups,
        game,
        target_rows=TARGET_ROWS,
        target_cols=TARGET_COLS,
        enable_wall_light=False,
        enable_screen_light=False,
    )
    new_groups, new_game = _prepare(groups, game)
    assert _digest(parent_groups, parent_game) == _digest(new_groups, new_game)


@pytest.mark.parametrize("relative_path,reason", list(PREPARE_SKIP_ARCHIVES.items()))
def test_prepare_skip_list_documents_broken_archives(relative_path, reason):
    assert "YC16" in relative_path
    groups, game = _load_level_file(ROOT / relative_path)
    with pytest.raises(ValueError, match="activity_area col range"):
        _prepare(groups, game)


def test_strip_empty_targets_match_parent_delta_set():
    parent = _parent_scaler_module()
    changed = []
    strip_targets = []
    kw = dict(
        target_rows=TARGET_ROWS,
        target_cols=TARGET_COLS,
        enable_wall_light=False,
        enable_screen_light=False,
    )
    for archive in _all_shipped_archives():
        rel = archive.relative_to(ROOT).as_posix()
        if rel in PREPARE_SKIP_ARCHIVES:
            continue
        try:
            groups, game = _load_level_file(archive)
        except Exception:
            continue
        if not groups:
            continue
        if should_strip_adapt_level(groups, game, platform_corner_line_start=0):
            strip_targets.append(rel)
        parent_groups, parent_game = parent.prepare_level_for_platform(
            groups, game, **kw
        )
        new_groups, new_game = _prepare(groups, game)
        if _digest(parent_groups, parent_game) != _digest(new_groups, new_game):
            changed.append(rel)

    assert changed, "expected at least one strip-empty stretch target"
    assert set(changed) == set(strip_targets)


def test_eight_playlist_wall_strip_targets_reach_full_column_span():
    targets = {
        "003",
        "010",
        "--/009",
        "Shoot 1",
        "005 Memory",
        "006 Memory",
        "009",
        "011",
    }
    seen = {}
    for _mode, level_id, relative_path in _playlist_entries():
        if level_id not in targets:
            continue
        groups, game = _load_level_file(ROOT / relative_path)
        prepared_groups, _ = _prepare(groups, game)
        seen[level_id] = _span_col_percent(prepared_groups)
    assert seen.keys() == targets
    for level_id, col_percent in seen.items():
        assert col_percent >= 90.0, level_id

"""Playlist coverage and strip-adapt regression guards."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from api.game_manager import _load_level_file
from api.level_scaler import prepare_level_for_platform
from scripts.validate_level_catalog import _snapshot


ROOT = Path(__file__).resolve().parents[1]
PLAYLISTS = ROOT / "api" / "mode_playlists.json"
TARGET_ROWS = 16
TARGET_COLS = 26
FLOOR_LIGHT = "floor_light"

# Authored row margins (diagnosis §4.3): art does not fill full row span by design.
ROW_MARGIN_ALLOWLIST = {
    ("games/source/---/---/JZDS001.led", "JZDS0012"),
    ("games/source/---/---/JZDS002.led", "JZDS0022"),
    ("games/source/---/---/JZDS003.led", "JZDS0032"),
    ("games/source/---/---/JZDS004.led", "JZDS0042"),
    ("games/source/---/---/JZDS005.led", "JZDS0052"),
    ("games/source/---/---/DK-001.led", "DK-0012"),
    ("games/source/---/---/DK-002.led", "DK-0022"),
}

# Corrupt movement range; not in playlists — skip during catalog preparation walks.
PREPARE_SKIP_ARCHIVES = {
    "games/source/---/---/YC16.led": (
        "corrupt activity_area col range (89, 24); not in mode_playlists.json"
    ),
}

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


def _span(groups, game):
    cells = set()
    for group in groups.values():
        if getattr(group, "type", None) != FLOOR_LIGHT:
            continue
        cells |= set(getattr(group, "start_member", None) or ())
        area = getattr(group, "activity_area", None) or []
        if len(area) == 2:
            (r0, r1), (c0, c1) = area
            for row in range(max(0, r0), min(game.row, r1)):
                for col in range(max(0, c0), min(game.col, c1)):
                    cells.add((row, col))
    if not cells:
        return 0.0, 0.0
    rows = [row for row, _ in cells]
    cols = [col for _, col in cells]
    row_span = (max(rows) - min(rows) + 1) / game.row
    col_span = (max(cols) - min(cols) + 1) / game.col
    return row_span, col_span


def _digest(groups, game):
    return hashlib.sha256(repr(_snapshot(groups, game)).encode()).hexdigest()


def _playlist_entries():
    data = json.loads(PLAYLISTS.read_text(encoding="utf-8"))
    for mode, entries in data.items():
        for entry in entries:
            yield mode, entry["id"], entry["path"]


def _old_scaler_module():
    parent_scaler = Path("/tmp/grid_parent/api/level_scaler.py")
    if not parent_scaler.is_file():
        import subprocess
        import tarfile

        parent_scaler.parent.mkdir(parents=True, exist_ok=True)
        payload = subprocess.check_output(
            ["git", "archive", "HEAD", "api/level_scaler.py"],
            cwd=ROOT,
        )
        with tarfile.open(fileobj=__import__("io").BytesIO(payload), mode="r:") as archive:
            archive.extractall("/tmp/grid_parent")
    archive = importlib.util.spec_from_file_location(
        "old_level_scaler",
        parent_scaler,
    )
    module = importlib.util.module_from_spec(archive)
    archive.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("mode", "level_id", "relative_path"), list(_playlist_entries()))
def test_playlist_levels_meet_minimum_board_coverage(mode, level_id, relative_path):
    groups, game = _load_level_file(ROOT / relative_path)
    prepared_groups, prepared_game = _prepare(groups, game)
    row_span, col_span = _span(prepared_groups, prepared_game)
    key = (relative_path, getattr(game, "name", level_id))
    if key in ROW_MARGIN_ALLOWLIST or any(
        relative_path.endswith(suffix)
        for suffix in ("JZDS001.led", "JZDS002.led", "JZDS003.led", "JZDS004.led", "JZDS005.led")
    ):
        assert row_span >= 0.62
        return
    assert row_span >= 0.9, f"{level_id} row span {row_span:.2%}"
    assert col_span >= 0.9, f"{level_id} col span {col_span:.2%}"


@pytest.mark.parametrize("relative_path,reason", list(PREPARE_SKIP_ARCHIVES.items()))
def test_prepare_skip_list_documents_broken_archives(relative_path, reason):
    assert "YC16" in relative_path
    groups, game = _load_level_file(ROOT / relative_path)
    with pytest.raises(ValueError, match="activity_area col range"):
        _prepare(groups, game)


def test_corner_zero_prepared_output_matches_parent_commit_snapshot():
    old = _old_scaler_module()
    for relative_path in (
        "games/source/effects/countdown.led",
        "games/source/effects/level_clear.led",
        "games/source/effects/level_fail.led",
    ):
        groups, game = _load_level_file(ROOT / relative_path)
        assert not getattr(game, "corner_line_start", 0)
        old_groups, old_game = old.prepare_level_for_platform(
            groups,
            game,
            target_rows=TARGET_ROWS,
            target_cols=TARGET_COLS,
            enable_wall_light=False,
            enable_screen_light=False,
        )
        new_groups, new_game = _prepare(groups, game)
        assert _digest(old_groups, old_game) == _digest(new_groups, new_game)


def test_playlist_wall_strip_levels_report_full_width_after_adapt():
    """Eight diagnosed playlist entries should reach ~100% column span after A1."""
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
    for mode, level_id, relative_path in _playlist_entries():
        if level_id not in targets:
            continue
        groups, game = _load_level_file(ROOT / relative_path)
        prepared_groups, prepared_game = _prepare(groups, game)
        row_span, col_span = _span(prepared_groups, prepared_game)
        seen[level_id] = (row_span, col_span)
    assert seen.keys() == targets
    for level_id, (row_span, col_span) in seen.items():
        assert row_span >= 0.9, level_id
        assert col_span >= 0.9, level_id

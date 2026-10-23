"""Strip-offset floor stretch (Fix A1) for wall-strip-authored levels."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from api.level_scaler import prepare_level_for_platform, scale_cells


TARGET_ROWS = 16
TARGET_COLS = 26
FLOOR_LIGHT = "floor_light"


def _game(**overrides):
    values = dict(
        name="strip-test",
        row=12,
        col=24,
        zone_row_from=0,
        zone_row_to=12,
        zone_col_from=8,
        zone_col_to=24,
        corner_line_start=8,
        wall_light=False,
        screen=False,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def _floor_group(**overrides):
    values = dict(
        name="floor",
        type=FLOOR_LIGHT,
        start_member={(4, 8), (4, 23)},
        activity_area=[(0, 12), (8, 24)],
        scale="both",
        start_area=1,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def _bbox(groups, target_rows=TARGET_ROWS, target_cols=TARGET_COLS):
    cells = set()
    for group in groups.values():
        if getattr(group, "type", None) != FLOOR_LIGHT:
            continue
        cells |= set(getattr(group, "start_member", None) or ())
        area = getattr(group, "activity_area", None) or []
        if len(area) == 2:
            (r0, r1), (c0, c1) = area
            for row in range(max(0, r0), min(target_rows, r1)):
                for col in range(max(0, c0), min(target_cols, c1)):
                    cells.add((row, col))
    if not cells:
        return None
    rows = [row for row, _ in cells]
    cols = [col for _, col in cells]
    return (
        min(rows),
        max(rows),
        min(cols),
        max(cols),
        (max(rows) - min(rows) + 1) / target_rows,
        (max(cols) - min(cols) + 1) / target_cols,
    )


def test_corner_zero_unchanged_vs_legacy_col_mapping():
    game = _game(corner_line_start=0, zone_col_from=0, zone_col_to=24)
    group = _floor_group(start_member={(4, 0), (4, 23)}, activity_area=[(0, 12), (0, 24)])
    prepared, prepared_game = prepare_level_for_platform(
        {"g": group},
        game,
        target_rows=TARGET_ROWS,
        target_cols=TARGET_COLS,
        enable_wall_light=False,
        enable_screen_light=False,
        platform_corner_line_start=0,
    )
    assert prepared_game.zone_col_from == 0
    assert prepared_game.zone_col_to == TARGET_COLS
    bbox = _bbox(prepared)
    assert bbox[4] == 1.0
    assert bbox[5] == 1.0


def test_strip_stretch_maps_authored_floor_to_full_target_width():
    prepared, prepared_game = prepare_level_for_platform(
        {"g": _floor_group()},
        _game(),
        target_rows=TARGET_ROWS,
        target_cols=TARGET_COLS,
        enable_wall_light=False,
        enable_screen_light=False,
        platform_corner_line_start=0,
    )
    assert (prepared_game.zone_col_from, prepared_game.zone_col_to) == (0, TARGET_COLS)
    bbox = _bbox(prepared)
    assert bbox[0] == 0 and bbox[1] == TARGET_ROWS - 1
    assert bbox[2] == 0 and bbox[3] == TARGET_COLS - 1
    assert bbox[4] >= 0.9 and bbox[5] >= 0.9


def test_moving_group_activity_area_col_range_stretches_to_target():
    group = _floor_group(
        start_member={(3, 10)},
        activity_area=[(0, 12), (8, 24)],
        scale="none",
    )
    prepared, _ = prepare_level_for_platform(
        {"g": group},
        _game(),
        target_rows=TARGET_ROWS,
        target_cols=TARGET_COLS,
        enable_wall_light=False,
        enable_screen_light=False,
        platform_corner_line_start=0,
    )
    col_range = prepared["g"].activity_area[1]
    assert col_range[0] == 0
    assert col_range[1] == TARGET_COLS


@pytest.mark.parametrize(
    ("mode", "source_member", "expected_col"),
    (
        ("none", {(5, 8)}, 0),
        ("none2edge", {(5, 8)}, 0),
        ("col", {(5, 8), (5, 23)}, 0),
        ("row", {(5, 8), (6, 23)}, 0),
        ("both", {(5, 8), (6, 23)}, 0),
    ),
)
def test_left_edge_floor_tile_maps_to_column_zero(mode, source_member, expected_col):
    group = _floor_group(start_member=source_member, scale=mode, activity_area=[(0, 12), (8, 24)])
    prepared, _ = prepare_level_for_platform(
        {"g": group},
        _game(),
        target_rows=TARGET_ROWS,
        target_cols=TARGET_COLS,
        enable_wall_light=False,
        enable_screen_light=False,
        platform_corner_line_start=0,
    )
    cols = {col for _, col in prepared["g"].start_member}
    assert expected_col in cols


def test_strip_only_floor_group_is_dropped():
    strip_group = _floor_group(
        name="strip",
        start_member={(2, 0), (3, 7)},
        activity_area=[(0, 12), (0, 8)],
        scale="none",
    )
    floor_group = _floor_group(name="floor")
    prepared, _ = prepare_level_for_platform(
        {"strip": strip_group, "floor": floor_group},
        _game(),
        target_rows=TARGET_ROWS,
        target_cols=TARGET_COLS,
        enable_wall_light=False,
        enable_screen_light=False,
        platform_corner_line_start=0,
    )
    assert "strip" not in prepared
    assert "floor" in prepared


def test_none_mode_keeps_single_cell_width_over_stretched_travel():
    direct = scale_cells(
        {(5, 8)},
        source_rows=12,
        source_cols=16,
        target_rows=TARGET_ROWS,
        target_cols=TARGET_COLS,
        mode="none",
    )
    assert len({col for _, col in direct}) == 1

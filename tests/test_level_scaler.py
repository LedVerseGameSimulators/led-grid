"""Executable specification for the future pure, headless level scaler."""

from __future__ import annotations

import hashlib
import importlib
import inspect
from types import SimpleNamespace

import pytest


TARGET_ROWS = 16
TARGET_COLS = 26
FLOOR_LIGHT = "floor_light"
WALL_LIGHT = "wall_light"
SCREEN_LIGHT = "screen_light"

REAL_LEVELS = (
    ("games/source/-/009.led", (12, 24)),
    ("games/source/-/008.led", (15, 26)),
    ("games/source/-/001.led", (16, 26)),
    ("games/source/--/011.led", (16, 28)),
)

# Generated once with a standalone port of game_running.zone_in_out's
# ROUND_HALF_UP cell-boundary math plus symmetric far-edge anchoring. These
# values are independent of the future api.level_scaler implementation.
REAL_LEVEL_GOLDENS = {
    "games/source/-/009.led": (
        "蓝色",
        25,
        "e5816e10bc5b0a16763412b0ca1eb175a6b19631d9f333a0b643e169c954ca88",
    ),
    "games/source/-/008.led": (
        "Group(1)",
        48,
        "80926a18fa66e664946f797bd140fb2326e23f0f93a804a947484363c70833a6",
    ),
    "games/source/-/001.led": (
        "灯组6",
        32,
        "b73ce0154ad9724a02f836322cd854eb5fed91f8bae30375a580a1d355198d10",
    ),
    "games/source/--/011.led": (
        "蓝色",
        47,
        "e603c51a22b4e9667b84fe6c9fdfc7b379365fc1cd9ec06fd38ed024a7bd494e",
    ),
}


def _level_scaler():
    """Import lazily so pytest can collect this RED-phase specification."""
    try:
        return importlib.import_module("api.level_scaler")
    except ModuleNotFoundError as exc:
        if exc.name != "api.level_scaler":
            raise
        pytest.fail(
            "TDD RED phase: required production module api.level_scaler does not exist",
            pytrace=False,
        )


def _prepare(groups, game, **options):
    scaler = _level_scaler()
    return scaler.prepare_level_for_platform(
        groups,
        game,
        target_rows=TARGET_ROWS,
        target_cols=TARGET_COLS,
        **options,
    )


def _coordinate_digest(cells) -> str:
    """SHA-256 of sorted ``row,col`` ASCII lines, with no trailing newline."""
    canonical = "\n".join(f"{row},{col}" for row, col in sorted(set(cells)))
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()


def _floor_snapshot(groups, game):
    floor_groups = {
        name: (
            tuple(sorted(getattr(group, "start_member", ()) or ())),
            tuple(tuple(axis) for axis in getattr(group, "activity_area", ()) or ()),
            getattr(group, "start_area", None),
            getattr(group, "scale", None),
        )
        for name, group in groups.items()
        if getattr(group, "type", None) == FLOOR_LIGHT
    }
    game_state = (
        game.row,
        game.col,
        game.zone_row_from,
        game.zone_row_to,
        game.zone_col_from,
        game.zone_col_to,
        game.wall_light,
        game.screen,
    )
    return floor_groups, game_state


def _game(**overrides):
    values = dict(
        name="test-level",
        row=10,
        col=10,
        zone_row_from=0,
        zone_row_to=10,
        zone_col_from=0,
        zone_col_to=10,
        wall_light=False,
        screen=False,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def _floor_group(**overrides):
    values = dict(
        name="test-group",
        type=FLOOR_LIGHT,
        start_member={(3, 3)},
        activity_area=[(0, 10), (0, 10)],
        scale="both",
        start_area=1,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.parametrize(
    ("mode", "expected"),
    (
        ("both", {(row, col) for row in range(2, 6) for col in range(2, 6)}),
        ("row", {(row, col) for row in range(2, 6) for col in (3, 4)}),
        ("col", {(row, col) for row in (3, 4) for col in range(2, 6)}),
        ("none", {(row, col) for row in (3, 4) for col in (3, 4)}),
        ("none2edge", {(row, col) for row in (3, 4) for col in (3, 4)}),
    ),
)
def test_scale_cells_honors_each_scale_mode(mode, expected):
    scaler = _level_scaler()
    source = {(1, 1), (1, 2), (2, 1), (2, 2)}

    result = scaler.scale_cells(
        source,
        source_rows=4,
        source_cols=4,
        target_rows=8,
        target_cols=8,
        mode=mode,
    )

    assert set(result) == expected


def test_none_and_none2edge_are_exact_aliases():
    scaler = _level_scaler()
    source = {(0, 1), (2, 4), (5, 7), (5, 0)}
    arguments = dict(
        source_rows=6,
        source_cols=8,
        target_rows=9,
        target_cols=11,
    )

    assert scaler.scale_cells(source, mode="none", **arguments) == scaler.scale_cells(
        source, mode="none2edge", **arguments
    )


@pytest.mark.parametrize(
    ("mode", "source", "expected"),
    (
        ("col", {(0, 3), (0, 20)}, {(0, 3), (0, 22)}),
        ("none", {(0, 3), (0, 20)}, {(0, 4), (0, 21)}),
        ("none2edge", {(0, 3), (0, 20)}, {(0, 4), (0, 21)}),
        ("col", {(11, 4), (11, 19)}, {(15, 4), (15, 21)}),
        ("none", {(11, 4), (11, 19)}, {(15, 5), (15, 20)}),
        ("none2edge", {(11, 4), (11, 19)}, {(15, 5), (15, 20)}),
        ("row", {(3, 0), (8, 0)}, {(4, 0), (11, 0)}),
        ("none", {(3, 0), (8, 0)}, {(5, 0), (10, 0)}),
        ("none2edge", {(3, 0), (8, 0)}, {(5, 0), (10, 0)}),
        ("row", {(2, 23), (9, 23)}, {(3, 25), (12, 25)}),
        ("none", {(2, 23), (9, 23)}, {(4, 25), (11, 25)}),
        ("none2edge", {(2, 23), (9, 23)}, {(4, 25), (11, 25)}),
    ),
)
def test_scale_cells_anchors_each_edge_pattern_independently(mode, source, expected):
    scaler = _level_scaler()
    result = set(
        scaler.scale_cells(
            source,
            source_rows=12,
            source_cols=24,
            target_rows=16,
            target_cols=26,
            mode=mode,
        )
    )

    assert result == expected


@pytest.mark.parametrize(
    ("start", "stop", "source_size", "target_size", "expected"),
    (
        (0, 12, 12, 16, (0, 16)),
        (0, 28, 28, 26, (0, 26)),
        (1, 5, 12, 16, (1, 7)),
        (2, 7, 12, 16, (3, 9)),
        (8, 28, 28, 26, (7, 26)),
        (-2, 8, 24, 26, (-2, 9)),
        (-3, 4, 8, 4, (-2, 2)),
        (1, 2, 2, 1, (0, 1)),    # In-bounds cell remains in target bounds
        (5, 6, 2, 1, (3, 4)),    # Outside range remains signed/outside
        (-1, 0, 2, 1, (-1, 0)),  # -0.5 -> -1
        (-3, 0, 2, 1, (-2, 0)),  # -1.5 -> -2
    ),
)
def test_scale_range_uses_half_up_rounding_for_full_interior_and_signed_ranges(
    start, stop, source_size, target_size, expected
):
    scaler = _level_scaler()

    assert scaler.scale_range(
        start, stop, source_size=source_size, target_size=target_size
    ) == expected


def test_scale_range_keeps_collapsed_nonempty_source_range_nonempty():
    scaler = _level_scaler()

    result = scaler.scale_range(1, 2, source_size=10, target_size=2)

    assert result == (0, 1)


def test_prepare_keeps_collapsed_zone_and_activity_ranges_nonempty():
    scaler = _level_scaler()
    game = _game(
        zone_row_from=3,
        zone_row_to=4,
        zone_col_from=3,
        zone_col_to=4,
    )
    group = _floor_group(activity_area=[(3, 4), (-4, -3)])

    prepared_groups, prepared_game = scaler.prepare_level_for_platform(
        {"test-group": group},
        game,
        target_rows=2,
        target_cols=2,
    )

    assert (
        prepared_game.zone_row_from,
        prepared_game.zone_row_to,
        prepared_game.zone_col_from,
        prepared_game.zone_col_to,
    ) == (1, 2, 1, 2)
    assert prepared_groups["test-group"].activity_area == [(1, 2), (-1, 0)]
    assert (1, 1) in prepared_groups["test-group"].start_member


@pytest.mark.parametrize("group_type", (None, "unknown_light", ["floor_light"]))
def test_prepare_rejects_missing_or_unknown_group_type_with_context(group_type):
    scaler = _level_scaler()
    group = _floor_group()
    if group_type is None:
        del group.type
    else:
        group.type = group_type

    with pytest.raises(ValueError) as error:
        scaler.prepare_level_for_platform(
            {"bad-key": group},
            _game(name="typed-level"),
            target_rows=2,
            target_cols=2,
        )

    message = str(error.value)
    assert "typed-level" in message
    assert "test-group" in message
    assert "type" in message


def test_prepare_rejects_empty_activity_range_but_preserves_signed_bounds():
    scaler = _level_scaler()
    group = _floor_group(activity_area=[(1, 1), (-4, -3)])

    with pytest.raises(ValueError, match=r"test-level.*test-group.*activity_area.*empty"):
        scaler.prepare_level_for_platform(
            {"test-group": group},
            _game(),
            target_rows=2,
            target_cols=2,
        )


def test_prepare_does_not_mutate_caller_objects():
    scaler = _level_scaler()
    game = _game(
        zone_row_from=3,
        zone_row_to=4,
        zone_col_from=3,
        zone_col_to=4,
    )
    group = _floor_group(activity_area=[(3, 4), (-4, -3)])
    groups = {"test-group": group}
    original_game_state = dict(vars(game))
    original_group_state = {
        **vars(group),
        "start_member": set(group.start_member),
        "activity_area": list(group.activity_area),
    }

    prepared_groups, prepared_game = scaler.prepare_level_for_platform(
        groups,
        game,
        target_rows=2,
        target_cols=2,
    )

    assert vars(game) == original_game_state
    assert vars(group) == original_group_state
    assert prepared_game is not game
    assert prepared_groups["test-group"] is not group


class _ExplodingCopy(SimpleNamespace):
    def __deepcopy__(self, memo):
        raise RuntimeError("copy exploded")


def test_prepare_contextualizes_game_deepcopy_failure():
    scaler = _level_scaler()
    game = _ExplodingCopy(**vars(_game(name="copy-fail-level")))

    with pytest.raises(ValueError, match=r"copy-fail-level.*copy.*copy exploded"):
        scaler.prepare_level_for_platform({}, game, target_rows=2, target_cols=2)


def test_prepare_contextualizes_group_deepcopy_failure():
    scaler = _level_scaler()
    group = _ExplodingCopy(**vars(_floor_group(name="copy-fail-group")))

    with pytest.raises(
        ValueError, match=r"test-level.*copy-fail-group.*copy.*copy exploded"
    ):
        scaler.prepare_level_for_platform(
            {"copy-fail-group": group},
            _game(),
            target_rows=2,
            target_cols=2,
        )


def test_public_functions_have_complete_type_hints():
    scaler = _level_scaler()

    for function_name in scaler.__all__:
        signature = inspect.signature(getattr(scaler, function_name))
        assert all(
            parameter.annotation is not inspect.Parameter.empty
            for parameter in signature.parameters.values()
        ), function_name
        assert signature.return_annotation is not inspect.Signature.empty, function_name


@pytest.mark.parametrize(("relative_path", "source_size"), REAL_LEVELS)
def test_real_archives_prepare_to_16_by_26_with_valid_floor_cells(
    load_level_archive, relative_path, source_size
):
    groups, game = load_level_archive(relative_path)
    assert (game.row, game.col) == source_size
    original_nonempty_floor = {
        name: set(getattr(group, "start_member", ()) or ())
        for name, group in groups.items()
        if getattr(group, "type", None) == FLOOR_LIGHT
        and getattr(group, "start_member", None)
    }
    assert original_nonempty_floor

    prepared_groups, prepared_game = _prepare(groups, game)

    assert (prepared_game.row, prepared_game.col) == (TARGET_ROWS, TARGET_COLS)
    assert (
        prepared_game.zone_row_from,
        prepared_game.zone_row_to,
        prepared_game.zone_col_from,
        prepared_game.zone_col_to,
    ) == (0, 16, 0, 26)
    floor_groups = [
        group
        for group in prepared_groups.values()
        if getattr(group, "type", None) == FLOOR_LIGHT
    ]
    assert floor_groups
    assert sum(
        len(getattr(group, "start_member", ()) or ()) for group in floor_groups
    ) > 0
    for name in original_nonempty_floor:
        assert name in prepared_groups
        assert getattr(prepared_groups[name], "type", None) == FLOOR_LIGHT
        assert getattr(prepared_groups[name], "start_member", None)
    for group in floor_groups:
        for row, col in getattr(group, "start_member", ()) or ():
            assert type(row) is int
            assert type(col) is int
            assert 0 <= row < TARGET_ROWS
            assert 0 <= col < TARGET_COLS
    golden_name, golden_count, golden_digest = REAL_LEVEL_GOLDENS[relative_path]
    golden_members = set(prepared_groups[golden_name].start_member)
    assert len(golden_members) == golden_count
    assert _coordinate_digest(golden_members) == golden_digest


def test_floor_groups_with_start_area_zero_are_retained(load_level_archive):
    groups, game = load_level_archive("games/source/-/008.led")
    expected_names = {
        name
        for name, group in groups.items()
        if getattr(group, "type", None) == FLOOR_LIGHT
        and getattr(group, "start_area", None) == 0
    }
    assert expected_names, "Archive fixture must exercise start_area=0 floor groups"

    prepared_groups, _ = _prepare(groups, game)

    assert expected_names <= set(prepared_groups)
    assert all(
        getattr(prepared_groups[name], "type", None) == FLOOR_LIGHT
        and getattr(prepared_groups[name], "start_area", None) == 0
        for name in expected_names
    )


@pytest.mark.parametrize(
    ("enable_wall_light", "enable_screen_light"),
    ((True, True), (True, False), (False, True), (False, False)),
)
def test_wall_and_screen_light_filtering_is_independently_optional(
    load_level_archive, enable_wall_light, enable_screen_light
):
    groups, game = load_level_archive("games/source/-/001.led")
    assert game.wall_light is True
    assert game.screen is True
    names_by_type = {
        group_type: {
            name
            for name, group in groups.items()
            if getattr(group, "type", None) == group_type
        }
        for group_type in (FLOOR_LIGHT, WALL_LIGHT, SCREEN_LIGHT)
    }
    assert all(names_by_type.values()), "Archive must contain floor, wall, and screen groups"

    prepared_groups, prepared_game = _prepare(
        groups,
        game,
        enable_wall_light=enable_wall_light,
        enable_screen_light=enable_screen_light,
    )

    prepared_names_by_type = {
        group_type: {
            name
            for name, group in prepared_groups.items()
            if getattr(group, "type", None) == group_type
        }
        for group_type in (FLOOR_LIGHT, WALL_LIGHT, SCREEN_LIGHT)
    }
    assert prepared_game.wall_light is enable_wall_light
    assert prepared_game.screen is enable_screen_light
    assert prepared_names_by_type[FLOOR_LIGHT] == names_by_type[FLOOR_LIGHT]
    assert prepared_names_by_type[WALL_LIGHT] == (
        names_by_type[WALL_LIGHT] if enable_wall_light else set()
    )
    assert prepared_names_by_type[SCREEN_LIGHT] == (
        names_by_type[SCREEN_LIGHT] if enable_screen_light else set()
    )


def test_identity_size_preserves_floor_coordinates(load_level_archive):
    groups, game = load_level_archive("games/source/-/001.led")
    original = {
        name: set(getattr(group, "start_member", ()) or ())
        for name, group in groups.items()
        if getattr(group, "type", None) == FLOOR_LIGHT
    }

    prepared_groups, _ = _prepare(groups, game)

    assert {
        name: set(getattr(group, "start_member", ()) or ())
        for name, group in prepared_groups.items()
        if getattr(group, "type", None) == FLOOR_LIGHT
    } == original


def test_repeated_preparation_is_stable_and_idempotent(load_level_archive):
    groups, game = load_level_archive("games/source/-/009.led")

    once_groups, once_game = _prepare(groups, game)
    twice_groups, twice_game = _prepare(once_groups, once_game)

    assert _floor_snapshot(twice_groups, twice_game) == _floor_snapshot(
        once_groups, once_game
    )

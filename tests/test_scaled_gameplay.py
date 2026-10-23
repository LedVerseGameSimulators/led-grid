"""End-to-end gameplay coverage for prepared (scaled) Grid levels."""

from __future__ import annotations

from pathlib import Path
import threading
from types import SimpleNamespace

import pytest

from api import game_manager
from api.level_scaler import prepare_level_for_platform
from game_play.Play import Play
from model.setting import Color, Setting


ROOT = Path(__file__).resolve().parents[1]
FLOOR_LIGHT = Setting.FLOOR_LIGHT


def _rings(rgb):
    return [rgb, rgb, rgb]


def _group(
    name,
    rgb,
    cells,
    *,
    start=0.0,
    end=100.0,
    direct=Setting.STATIC,
    speed=1.0,
    edge=Setting.BACK,
    activity_area=((0, 8), (0, 13)),
):
    return SimpleNamespace(
        name=name,
        type=FLOOR_LIGHT,
        color=_rings(rgb),
        start_member=set(cells),
        start_time_sec=start,
        end_time_sec=end,
        scale="both",
        start_area=1,
        direct=direct,
        speed=speed,
        edge_run_into=edge,
        activity_area=list(activity_area),
    )


def _level(rows=8, cols=13):
    return SimpleNamespace(
        name="scaled-gameplay",
        row=rows,
        col=cols,
        zone_row_from=0,
        zone_row_to=rows,
        zone_col_from=0,
        zone_col_to=cols,
        wall_light=False,
        screen=False,
    )


def _prepare(groups, game=None):
    return prepare_level_for_platform(
        groups,
        game or _level(),
        target_rows=16,
        target_cols=26,
        enable_wall_light=False,
        enable_screen_light=False,
    )


def _game(groups, *, multiplayer=False):
    game = game_manager.GameInstance("scaled", "card", 1, "normal")
    game.running = True
    game.led_table = game_manager.HeadlessLedTable(100, 16, 26)
    game.zone = (0, 16, 0, 26)
    game.dict_group = groups
    game.multiplayer = multiplayer
    game.accepting_input = True
    game.current_state["accepting_input"] = True
    game.play = SimpleNamespace(total_pass=2.0)
    return game


def _classify(groups, *, multiplayer=False, total_pass=2.0):
    return game_manager._classify_floor_groups(
        groups,
        total_pass=total_pass,
        multiplayer=multiplayer,
        rows=16,
        cols=26,
    )


def _frame(game, groups, *, total_pass=2.0, hardware_state=None):
    classified = _classify(
        groups, multiplayer=game.multiplayer, total_pass=total_pass
    )
    game.process_frame_input(
        goal_cells=classified["goal"],
        goal2_cells=classified["goal2"],
        red_cells=classified["red"],
        deduct_cells=classified["deduct"],
        hardware_state=hardware_state,
    )
    return classified


def test_scaled_classification_uses_transformed_cells_and_overlap_priority():
    groups, _ = _prepare(
        {
            "goal": _group(
                "goal", Color.BLUE, {(1, 1), (3, 3), (4, 4), (5, 5)}
            ),
            "p2": _group("p2", (254, 128, 0), {(2, 2)}),
            "red": _group("red", Color.RED, {(3, 3), (5, 5)}),
            "deduct": _group("deduct", Color.DEDUCT_COLOR, {(4, 4)}),
            "green": _group("green", Color.GREEN, {(5, 5)}),
        }
    )

    classified = _classify(groups, multiplayer=True)

    assert (2, 2) in classified["goal"]
    assert (4, 4) in classified["goal2"]
    assert (6, 6) in classified["red"]
    assert (8, 8) in classified["deduct"]
    assert (10, 10) in classified["green"]
    assert (6, 6) not in classified["goal"]
    assert (8, 8) not in classified["goal"]
    assert (10, 10) not in classified["goal"] | classified["red"]
    assert (1, 1) not in set().union(
        classified["goal"],
        classified["goal2"],
        classified["red"],
        classified["deduct"],
        classified["green"],
    )


def test_simulator_press_scores_once_and_consumes_only_transformed_goal():
    groups, _ = _prepare({"goal": _group("goal", Color.BLUE, {(1, 1)})})
    game = _game(groups)

    assert game.apply_input(1, 1, "press") is True
    assert game.score == 0
    assert game.led_table.state_table[1][1] is True
    assert (1, 1) in game._sim_pressed
    _frame(game, groups)
    assert game.score == 0
    game.apply_input(1, 1, "release")

    assert game.apply_input(2, 2, "press") is True
    assert game.score == 0
    frame = threading.Thread(target=_frame, args=(game, groups))
    frame.start()
    frame.join(timeout=2)
    assert not frame.is_alive()
    assert game.score == 1
    assert (2, 2) not in groups["goal"].start_member

    game.apply_input(2, 2, "release")
    game.apply_input(2, 2, "press")
    _frame(game, groups)
    assert game.score == 1


def test_hardware_state_table_uses_transformed_row_col_without_input_scaling():
    groups, _ = _prepare({"goal": _group("goal", Color.BLUE, {(1, 1)})})
    game = _game(groups)
    hardware = [[False] * 26 for _ in range(16)]
    hardware[2][3] = True

    _frame(game, groups, hardware_state=hardware)

    assert game.score == 1
    assert game.led_table.state_table[2][3] is True
    assert (2, 3) not in groups["goal"].start_member


def test_multiplayer_scaled_blue_and_orange_cells_keep_separate_scores():
    groups, _ = _prepare(
        {
            "blue": _group("blue", Color.BLUE, {(1, 1)}),
            "orange": _group("orange", (254, 128, 0), {(2, 2)}),
        }
    )
    game = _game(groups, multiplayer=True)
    game.apply_input(2, 2, "press")
    game.apply_input(4, 4, "press")

    classified = _frame(game, groups)

    assert (2, 2) in classified["goal"]
    assert (4, 4) in classified["goal2"]
    assert (2, 2) not in classified["goal2"]
    assert (4, 4) not in classified["goal"]
    assert (game.score, game.score2) == (1, 1)


def test_expanded_members_drive_remaining_completion_and_future_wave_jump():
    groups, _ = _prepare(
        {
            "active": _group("active", Color.BLUE, {(1, 1)}, start=0, end=4),
            "future": _group("future", Color.BLUE, {(2, 2)}, start=9, end=12),
            "hazard": _group("hazard", Color.RED, {(3, 3)}),
        }
    )

    assert game_manager._remaining_scoreable_members(groups, multiplayer=False) == 8
    assert game_manager._next_scoreable_wave_start(
        groups, total_pass=2, multiplayer=False
    ) == 9

    groups["active"].start_member.clear()
    assert game_manager._remaining_scoreable_members(groups, multiplayer=False) == 4
    assert _classify(groups, total_pass=2)["goal"] == set()
    assert game_manager._next_scoreable_wave_start(
        groups, total_pass=2, multiplayer=False
    ) == 9

    groups["future"].start_member.clear()
    assert game_manager._remaining_scoreable_members(groups, multiplayer=False) == 0
    assert game_manager._next_scoreable_wave_start(
        groups, total_pass=2, multiplayer=False
    ) is None


def test_level_progress_respects_grace_period_before_clear():
    groups, _ = _prepare({})

    assert game_manager._level_progress_action(
        groups,
        total_pass=1.5,
        multiplayer=False,
        active_goal_cells=set(),
        active_goal2_cells=set(),
    ) == ("continue", None, 0)


def test_level_progress_clears_after_all_scoreables_are_consumed():
    groups, _ = _prepare({})

    assert game_manager._level_progress_action(
        groups,
        total_pass=1.6,
        multiplayer=False,
        active_goal_cells=set(),
        active_goal2_cells=set(),
    ) == ("clear", None, 0)


def test_level_progress_jumps_to_future_wave_when_no_goal_is_active():
    groups, _ = _prepare(
        {"future": _group("future", Color.BLUE, {(2, 2)}, start=9, end=12)}
    )

    assert game_manager._level_progress_action(
        groups,
        total_pass=2,
        multiplayer=False,
        active_goal_cells=set(),
        active_goal2_cells=set(),
    ) == ("jump", 9, 4)


def test_level_progress_does_not_jump_while_goal_is_active():
    groups, _ = _prepare(
        {
            "active": _group("active", Color.BLUE, {(1, 1)}, start=0, end=4),
            "future": _group("future", Color.BLUE, {(2, 2)}, start=9, end=12),
        }
    )
    active = _classify(groups, total_pass=2)["goal"]

    assert game_manager._level_progress_action(
        groups,
        total_pass=2,
        multiplayer=False,
        active_goal_cells=active,
        active_goal2_cells=set(),
    ) == ("continue", None, 8)


def test_red_rate_limit_deduct_consumption_and_green_shielding(monkeypatch):
    groups, _ = _prepare(
        {
            "red": _group("red", Color.RED, {(1, 1)}),
            "deduct": _group("deduct", Color.DEDUCT_COLOR, {(2, 2)}),
            "shielded-red": _group("shielded-red", Color.RED, {(3, 3)}),
            "green": _group("green", Color.GREEN, {(3, 3)}),
        }
    )
    game = _game(groups)
    game.score = 3
    game.life = 20
    game._life_count_time = 1.2
    game.last_life_loss_time = 0
    now = [10.0]
    monkeypatch.setattr(game_manager.time, "time", lambda: now[0])
    classified = _classify(groups)
    game.goal_cells = classified["goal"]
    game.goal2_cells = classified["goal2"]
    game.red_cells = classified["red"]
    game.deduct_cells = classified["deduct"]

    game.try_score_cell(2, 2)
    assert (game.score, game.life) == (2, 19)
    now[0] = 10.5
    game.try_score_cell(2, 2)
    assert (game.score, game.life) == (2, 19)
    now[0] = 11.3
    game.try_score_cell(2, 2)
    assert (game.score, game.life) == (1, 18)

    game.try_score_cell(4, 4)
    assert (game.score, game.life) == (0, 18)
    assert (4, 4) not in groups["deduct"].start_member
    assert (6, 6) in classified["green"]
    assert (6, 6) not in classified["red"]
    game.try_score_cell(6, 6)
    assert (game.score, game.life) == (0, 18)


def test_movement_uses_transformed_activity_bounds_and_preserves_signed_bounds(
    load_level_archive,
):
    raw_groups, raw_game = load_level_archive("games/source/-/009.led")
    groups, _ = _prepare(raw_groups, raw_game)
    moving = next(
        group
        for group in groups.values()
        if getattr(group, "type", None) == FLOOR_LIGHT
        and getattr(group, "direct", None) not in (None, Setting.STATIC)
        and getattr(group, "start_member", None)
    )
    play = object.__new__(Play)
    _, moved = play.deal_all_direction(moving)
    (row_from, row_to), (col_from, col_to) = moving.activity_area
    assert moved
    assert all(
        row_from <= row < row_to and col_from <= col < col_to
        for row, col in moved
    )

    synthetic, _ = _prepare(
        {
            "bounce": _group(
                "bounce",
                Color.BLUE,
                {(0, 1)},
                direct=Setting.UP,
                edge=Setting.BACK,
                activity_area=((-2, 8), (-1, 13)),
            ),
            "vanish": _group(
                "vanish",
                Color.BLUE,
                {(0, 2)},
                direct=Setting.UP,
                edge=Setting.DISAPPEAR,
                activity_area=((-2, 8), (-1, 13)),
            ),
        }
    )
    assert synthetic["bounce"].activity_area[0][0] < 0
    row_from = synthetic["bounce"].activity_area[0][0]
    synthetic["bounce"].start_member = {(row_from, 2), (2, 2)}
    synthetic["vanish"].start_member = {(row_from, 4), (4, 4)}
    bounce_direction, bounced = play.deal_all_direction(synthetic["bounce"])
    _, vanished = play.deal_all_direction(synthetic["vanish"])
    assert bounce_direction == Setting.DOWN
    assert set(bounced) == {(row_from + 1, 2), (3, 2)}
    assert vanished == [(3, 4)]
    classified = _classify(synthetic)
    assert (row_from, 2) not in classified["goal"]
    assert (2, 2) in classified["goal"]


def test_scaling_preserves_source_movement_speed_and_direction():
    source = _group(
        "moving",
        Color.BLUE,
        {(1, 1)},
        direct=Setting.RIGHT,
        speed=2.5,
    )

    groups, _ = _prepare({"moving": source})

    # Source-compatible: one platform cell per tick; geometry scales, cadence does not.
    assert groups["moving"].speed == source.speed
    assert groups["moving"].direct == source.direct
    assert groups["moving"].start_member != source.start_member


@pytest.mark.parametrize(
    "relative_path",
    ("games/source/-/009.led", "games/source/-/001.led"),
)
def test_load_prepare_consume_reload_prepare_restores_initial_set(
    load_level_archive, relative_path
):
    raw_groups, raw_game = load_level_archive(relative_path)
    first, first_game = _prepare(raw_groups, raw_game)
    initial = {
        name: set(getattr(group, "start_member", ()) or ())
        for name, group in first.items()
        if getattr(group, "type", None) == FLOOR_LIGHT
    }
    scoreable = next(
        group
        for group in first.values()
        if getattr(group, "type", None) == FLOOR_LIGHT
        and game_manager._group_main_color(group.color) == Color.BLUE
        and group.start_member
    )
    cell = next(iter(scoreable.start_member))
    game = _game(first)
    game.goal_cells = {cell}
    game._consume_cell(*cell, total_pass=scoreable.start_time_sec)
    assert cell not in scoreable.start_member

    reloaded_groups, reloaded_game = load_level_archive(relative_path)
    second, second_game = _prepare(reloaded_groups, reloaded_game)
    restored = {
        name: set(getattr(group, "start_member", ()) or ())
        for name, group in second.items()
        if getattr(group, "type", None) == FLOOR_LIGHT
    }
    assert restored == initial
    if (raw_game.row, raw_game.col) == (16, 26):
        raw_floor = {
            name: set(getattr(group, "start_member", ()) or ())
            for name, group in raw_groups.items()
            if getattr(group, "type", None) == FLOOR_LIGHT
        }
        assert initial == raw_floor
    assert (first_game.row, first_game.col) == (16, 26)
    assert (second_game.row, second_game.col) == (16, 26)

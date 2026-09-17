"""Phase B MP: either-player wave advance + vacuous-empty latch."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from api import game_manager
from api.level_scaler import prepare_level_for_platform
from model.setting import Color, Setting


FLOOR_LIGHT = Setting.FLOOR_LIGHT


def _rings(rgb):
    return [rgb, rgb, rgb]


def _group(name, rgb, cells, *, start=0.0, end=100.0):
    return SimpleNamespace(
        name=name,
        type=FLOOR_LIGHT,
        color=_rings(rgb),
        start_member=set(cells),
        start_time_sec=start,
        end_time_sec=end,
        scale="both",
        start_area=1,
        direct=Setting.STATIC,
        speed=1.0,
        edge_run_into=Setting.BACK,
        activity_area=((0, 8), (0, 13)),
    )


def _level(rows=8, cols=13):
    return SimpleNamespace(
        name="mp-phase-b",
        row=rows,
        col=cols,
        zone_row_from=0,
        zone_row_to=rows,
        zone_col_from=0,
        zone_col_to=cols,
        wall_light=False,
        screen=False,
    )


def _prepare(groups):
    return prepare_level_for_platform(
        groups,
        _level(),
        target_rows=16,
        target_cols=26,
        enable_wall_light=False,
        enable_screen_light=False,
    )


def _game(groups, *, multiplayer=False):
    game = game_manager.GameInstance("phase-b", "card", 1, "normal")
    game.running = True
    game.multiplayer = multiplayer
    game.dict_group = groups
    game._mp_wave_had_p1 = False
    game._mp_wave_had_p2 = False
    return game


def _classify(groups, *, multiplayer=False, total_pass=2.0):
    return game_manager._classify_floor_groups(
        groups,
        total_pass=total_pass,
        multiplayer=multiplayer,
        rows=16,
        cols=26,
    )


def _progress(groups, *, multiplayer, total_pass=2.0, goal_cells=None, goal2_cells=None):
    if goal_cells is None or goal2_cells is None:
        classified = _classify(groups, multiplayer=multiplayer, total_pass=total_pass)
        goal_cells = classified["goal"] if goal_cells is None else goal_cells
        goal2_cells = classified["goal2"] if goal2_cells is None else goal2_cells
    return game_manager._level_progress_action(
        groups,
        total_pass=total_pass,
        multiplayer=multiplayer,
        active_goal_cells=goal_cells,
        active_goal2_cells=goal2_cells,
    )


def _run_mp_discard(game, groups, *, total_pass=2.0):
    classified = _classify(groups, multiplayer=True, total_pass=total_pass)
    game_manager._mp_update_wave_latch(
        game,
        groups,
        total_pass=total_pass,
        goal_cells=classified["goal"],
        goal2_cells=classified["goal2"],
    )
    discarded = game_manager._mp_either_player_discard(
        game, groups, total_pass=total_pass
    )
    if discarded:
        classified = _classify(groups, multiplayer=True, total_pass=total_pass)
    return discarded, classified


# ── Either-player advance ─────────────────────────────────────────────────


def test_mp_p1_clears_discards_p2_leftovers_and_jumps():
    groups, _ = _prepare(
        {
            "p1": _group("p1", Color.BLUE, {(1, 1)}),
            "p2": _group("p2", (254, 128, 0), {(2, 2)}),
            "p1_next": _group("p1_next", Color.BLUE, {(3, 3)}, start=50.0, end=100.0),
        }
    )
    groups["p1"].start_member.clear()
    game = _game(groups, multiplayer=True)

    discarded, classified = _run_mp_discard(game, groups, total_pass=2.0)
    assert discarded is True
    assert len(groups["p2"].start_member) == 0
    assert len(groups["p1_next"].start_member) > 0  # future wave untouched

    action, next_start, rem = _progress(
        groups,
        multiplayer=True,
        total_pass=2.0,
        goal_cells=classified["goal"],
        goal2_cells=classified["goal2"],
    )
    assert action == "jump"
    assert next_start == 50.0
    assert rem > 0


def test_mp_p2_clears_discards_p1_leftovers():
    groups, _ = _prepare(
        {
            "p1": _group("p1", Color.BLUE, {(1, 1)}),
            "p2": _group("p2", (254, 128, 0), {(2, 2)}),
        }
    )
    groups["p2"].start_member.clear()
    game = _game(groups, multiplayer=True)
    game._mp_wave_had_p1 = True
    game._mp_wave_had_p2 = True

    assert game_manager._mp_either_player_discard(game, groups, total_pass=2.0)
    assert len(groups["p1"].start_member) == 0


# ── Vacuous-empty latch ───────────────────────────────────────────────────


def test_mp_p1_only_wave_advances_when_p1_clears():
    groups, _ = _prepare({"p1": _group("p1", Color.BLUE, {(1, 1)})})
    game = _game(groups, multiplayer=True)
    game_manager._mp_update_wave_latch(
        game,
        groups,
        total_pass=2.0,
        goal_cells={(2, 2)},
        goal2_cells=set(),
    )
    groups["p1"].start_member.clear()
    game_manager._mp_update_wave_latch(
        game,
        groups,
        total_pass=2.0,
        goal_cells=set(),
        goal2_cells=set(),
    )

    assert game._mp_wave_had_p1 is True
    assert game._mp_wave_had_p2 is False
    assert not game_manager._mp_either_player_discard(game, groups, total_pass=2.0)

    action, _, rem = _progress(groups, multiplayer=True, total_pass=2.0)
    assert action == "clear"
    assert rem == 0


def test_mp_vacuous_p2_does_not_false_advance_while_p1_remains():
    groups, _ = _prepare({"p1": _group("p1", Color.BLUE, {(1, 1)})})
    game = _game(groups, multiplayer=True)
    game_manager._mp_update_wave_latch(
        game,
        groups,
        total_pass=2.0,
        goal_cells={(2, 2)},
        goal2_cells=set(),
    )

    assert game._mp_wave_had_p2 is False
    assert not game_manager._mp_either_player_discard(game, groups, total_pass=2.0)

    action, _, rem = _progress(groups, multiplayer=True, total_pass=2.0)
    assert action == "continue"
    assert rem > 0


def test_discard_helper_respects_time_window():
    groups, _ = _prepare(
        {
            "p2_now": _group("p2_now", (254, 128, 0), {(1, 1)}, start=0.0, end=10.0),
            "p2_future": _group(
                "p2_future", (254, 128, 0), {(2, 2)}, start=50.0, end=100.0
            ),
        }
    )
    assert game_manager._discard_mp_side_leftovers(
        groups, total_pass=5.0, side_color=game_manager._GRID_P2_COLOR
    )
    assert len(groups["p2_now"].start_member) == 0
    assert len(groups["p2_future"].start_member) > 0


# ── 1P regression ─────────────────────────────────────────────────────────


def test_1p_still_waits_for_all_scoreables():
    groups, _ = _prepare(
        {
            "a": _group("a", Color.BLUE, {(1, 1)}),
            "b": _group("b", Color.BLUE, {(2, 2)}),
        }
    )
    groups["a"].start_member.clear()
    action, _, rem = _progress(groups, multiplayer=False, total_pass=2.0)
    assert action == "continue"
    assert rem > 0


def test_1p_mp_helpers_are_no_ops():
    groups, _ = _prepare({"p1": _group("p1", Color.BLUE, {(1, 1)})})
    game = _game(groups, multiplayer=False)
    assert not game_manager._mp_either_player_discard(game, groups, total_pass=2.0)

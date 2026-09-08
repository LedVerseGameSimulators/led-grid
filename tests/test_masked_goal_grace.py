"""Masked-goal grace: port of Climb's unreachable-scoreable rescue.

When visible goals are empty, scoreables remain (masked), and no future wave
exists, wait MASKED_GOAL_GRACE then clear the level — instead of waiting until
board_time (~300s). Moving masks that re-expose goals within the grace window
reset the timer so normal play continues.
"""

from __future__ import annotations

import time
from types import SimpleNamespace

import pytest

from api import game_manager


def _apply_grace(game, *, total_pass, remaining, goals, goals2, next_start):
    """Mirror the frame-callback grace branch in game_manager."""
    if (
        total_pass > 1.5
        and remaining > 0
        and not goals
        and not goals2
        and next_start is None
    ):
        now_mono = time.monotonic()
        if game._no_reachable_goal_since is None:
            game._no_reachable_goal_since = now_mono
            return "waiting"
        if (
            now_mono - game._no_reachable_goal_since
            >= game_manager._MASKED_GOAL_GRACE
        ):
            game._level_cleared = True
            return "clear"
        return "waiting"
    game._no_reachable_goal_since = None
    return "reset"


def test_masked_goal_grace_clears_after_timeout(monkeypatch):
    game = game_manager.GameInstance("g", "card", 1, "normal")
    clock = {"t": 100.0}
    monkeypatch.setattr(game_manager.time, "monotonic", lambda: clock["t"])
    monkeypatch.setattr(game_manager, "_MASKED_GOAL_GRACE", 1.0)

    assert (
        _apply_grace(
            game,
            total_pass=60.0,
            remaining=2,
            goals=set(),
            goals2=set(),
            next_start=None,
        )
        == "waiting"
    )
    assert game._level_cleared is False

    clock["t"] = 100.5
    assert (
        _apply_grace(
            game,
            total_pass=60.5,
            remaining=2,
            goals=set(),
            goals2=set(),
            next_start=None,
        )
        == "waiting"
    )
    assert game._level_cleared is False

    clock["t"] = 101.0
    assert (
        _apply_grace(
            game,
            total_pass=61.0,
            remaining=2,
            goals=set(),
            goals2=set(),
            next_start=None,
        )
        == "clear"
    )
    assert game._level_cleared is True


def test_masked_goal_grace_resets_when_goals_reappear(monkeypatch):
    game = game_manager.GameInstance("g", "card", 1, "normal")
    clock = {"t": 50.0}
    monkeypatch.setattr(game_manager.time, "monotonic", lambda: clock["t"])
    monkeypatch.setattr(game_manager, "_MASKED_GOAL_GRACE", 1.0)

    _apply_grace(
        game,
        total_pass=60.0,
        remaining=2,
        goals=set(),
        goals2=set(),
        next_start=None,
    )
    assert game._no_reachable_goal_since == 50.0

    # Moving red exposes a blue again — timer must reset.
    assert (
        _apply_grace(
            game,
            total_pass=60.2,
            remaining=2,
            goals={(2, 10)},
            goals2=set(),
            next_start=None,
        )
        == "reset"
    )
    assert game._no_reachable_goal_since is None
    assert game._level_cleared is False


def test_level_progress_still_continues_on_static_orphan_snapshot():
    """`_level_progress_action` alone still returns continue; grace is the rescue."""
    groups = {
        "blue": SimpleNamespace(
            type="floor_light",
            color=[(0, 0, 254)] * 3,
            start_member={(2, 10)},
            start_time_sec=0.0,
            end_time_sec=300.0,
        ),
    }
    action, next_start, rem = game_manager._level_progress_action(
        groups,
        total_pass=60.0,
        multiplayer=False,
        active_goal_cells=set(),
        active_goal2_cells=set(),
    )
    assert (action, next_start, rem) == ("continue", None, 1)

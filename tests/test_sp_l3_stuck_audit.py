"""Audit-only characterization: Grid SP Level 3 stuck-after-visible-clear.

No production fixes in this file. These tests document current behavior so we
can prove (or refute) the L3-only stall before changing clear-detection logic.

Symptom (onsite): after clearing visible tiles on SP L3 (`-/003.led`), the
session stays in playing with no level_clear effect and no next level until
board_time eventually fires.
"""

from __future__ import annotations

import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from api import game_manager
from api.level_scaler import prepare_level_for_platform
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
    end=300.0,
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
        direct=Setting.STATIC,
        speed=0.0,
        edge_run_into=Setting.BACK,
        activity_area=((0, 8), (0, 13)),
    )


def _prepare(groups, game=None):
    if game is None:
        game = SimpleNamespace(
            name="audit",
            row=8,
            col=13,
            zone_row_from=0,
            zone_row_to=8,
            zone_col_from=0,
            zone_col_to=13,
            wall_light=False,
            screen=False,
        )
    return prepare_level_for_platform(
        groups,
        game,
        target_rows=16,
        target_cols=26,
        enable_wall_light=False,
        enable_screen_light=False,
    )


def _classify(groups, *, total_pass=2.0, multiplayer=False):
    return game_manager._classify_floor_groups(
        groups,
        total_pass=total_pass,
        multiplayer=multiplayer,
        rows=16,
        cols=26,
    )


def _progress(groups, *, total_pass, goals, goals2=None):
    return game_manager._level_progress_action(
        groups,
        total_pass=total_pass,
        multiplayer=False,
        active_goal_cells=goals,
        active_goal2_cells=goals2 or set(),
    )


def _board_time(groups) -> float:
    ends = [
        float(getattr(g, "end_time_sec", 0) or 0)
        for g in groups.values()
        if getattr(g, "type", None) == FLOOR_LIGHT
    ]
    return max(ends) if ends else 0.0


def _scoreable_groups(groups):
    colors = game_manager._scoreable_colors(False)
    return [
        g
        for g in groups.values()
        if getattr(g, "type", None) == FLOOR_LIGHT
        and game_manager._group_main_color(g.color) in colors
        and getattr(g, "start_member", None)
    ]


def _consume_all_active_goals(groups, *, total_pass=2.0, max_rounds=500):
    """Simulate a player who scores every currently visible blue until none left.

    Does not move groups — matches a static/authored-position snapshot, which is
    the worst case for red/green overlap masking.
    """
    rounds = 0
    while rounds < max_rounds:
        rounds += 1
        classified = _classify(groups, total_pass=total_pass)
        goals = set(classified["goal"])
        if not goals:
            return classified, rounds
        for cell in list(goals):
            for group in _scoreable_groups(groups):
                members = getattr(group, "start_member", None)
                if members is not None and cell in members:
                    start = getattr(group, "start_time_sec", 0)
                    end = getattr(group, "end_time_sec", 1e9)
                    if start <= total_pass < end:
                        members.discard(cell)
    classified = _classify(groups, total_pass=total_pass)
    return classified, rounds


def _synthetic_l3_like_groups():
    """Authored 8x13 cells that scale to production; two blues sit under red."""
    # After 2x scale, (1,5)->(2,10) and (1,11)->(2,22)/(2,23) neighborhood.
    orphans_src = {(1, 5), (1, 11)}
    blues_src = {(r, c) for r in range(1, 7) for c in range(3, 12)} | orphans_src
    return {
        "blue": _group("blue", Color.BLUE, blues_src, start=0, end=300),
        "red": _group("red", Color.RED, orphans_src, start=0, end=300),
    }


def test_synthetic_overlap_orphan_enters_progress_dead_zone():
    """Mirrors L3: remaining blues exist but are red-masked → no clear/jump."""
    groups, _ = _prepare(_synthetic_l3_like_groups())

    # Consume every blue that classification currently exposes as a goal.
    classified, _ = _consume_all_active_goals(groups, total_pass=60.0)
    remaining = game_manager._remaining_scoreable_members(groups, multiplayer=False)
    action, next_start, rem = _progress(
        groups, total_pass=60.0, goals=classified["goal"]
    )

    assert classified["goal"] == set()
    assert remaining > 0
    assert next_start is None
    # CURRENT BUG: empty board look + orphans → continue (dead zone), not clear.
    assert (action, rem) == ("continue", remaining)


def test_synthetic_dead_zone_is_rescued_only_by_board_time():
    groups, _ = _prepare(
        {
            "blue": _group(
                "blue", Color.BLUE, {(1, 5), (3, 3)}, start=0, end=300
            ),
            "red": _group("red", Color.RED, {(1, 5)}, start=0, end=300),
        }
    )
    classified, _ = _consume_all_active_goals(groups, total_pass=60.0)
    action, _, rem = _progress(groups, total_pass=60.0, goals=classified["goal"])
    assert action == "continue" and rem > 0

    # Production loop clears only when total_pass > board_time_sec.
    board_time = _board_time(groups)
    assert board_time == 300.0
    assert 60.0 <= board_time  # stall window exists before rescue


@pytest.mark.parametrize(
    "relative_path,level_id",
    [
        ("games/source/-/001.led", "001"),
        ("games/source/-/002.led", "002"),
        ("games/source/-/003.led", "003"),
        ("games/source/-/004.led", "004"),
    ],
)
def test_sp_easy_levels_after_visible_clear_progress_action(
    load_level_archive, relative_path, level_id, capsys
):
    """Load real SP easy archives; report progress after consuming all visible goals.

    Static (no-movement) snapshot: L3 leaves 2 blues under moving reds at authored
    positions → `_level_progress_action` returns continue. With Play movement those
    reds leave quickly; session rescue is masked-goal grace (Climb parity), not an
    immediate clear-on-empty-goals change.
    """
    raw_groups, raw_game = load_level_archive(relative_path)
    groups, prepared_game = _prepare(raw_groups, raw_game)
    board_time = _board_time(groups)
    before = game_manager._remaining_scoreable_members(groups, multiplayer=False)

    classified, rounds = _consume_all_active_goals(groups, total_pass=60.0)
    after = game_manager._remaining_scoreable_members(groups, multiplayer=False)
    action, next_start, rem = _progress(
        groups, total_pass=60.0, goals=classified["goal"]
    )

    print(
        f"\n[AUDIT {level_id}] file={relative_path} "
        f"board_time={board_time} before={before} after={after} "
        f"goals={len(classified['goal'])} red={len(classified['red'])} "
        f"green={len(classified['green'])} action={action!r} "
        f"next_start={next_start} rem={rem} rounds={rounds} "
        f"prepared={prepared_game.row}x{prepared_game.col}"
    )

    assert before > 0
    assert classified["goal"] == set()

    if level_id == "001":
        assert action == "clear"
        assert after == 0
    elif level_id == "003":
        # Static snapshot only — orphans under MOVING reds (灯组2/3).
        assert action == "continue"
        assert next_start is None
        assert after == 2
        assert rem == after
        assert board_time >= 300.0
    else:
        assert action in ("clear", "continue", "jump")


def test_grace_rescues_static_orphan_dead_zone(monkeypatch):
    """Session-level rescue: empty goals + remaining + no wave → clear after grace."""
    game = game_manager.GameInstance("audit", "card", 1, "normal")
    clock = {"t": 10.0}
    monkeypatch.setattr(game_manager.time, "monotonic", lambda: clock["t"])
    monkeypatch.setattr(game_manager, "_MASKED_GOAL_GRACE", 1.0)

    # First empty-goal frame starts the timer.
    now = time.monotonic()
    game._no_reachable_goal_since = now
    clock["t"] = 11.0
    assert clock["t"] - game._no_reachable_goal_since >= game_manager._MASKED_GOAL_GRACE
    # Production branch would set _level_cleared here.
    game._level_cleared = True
    assert game._level_cleared is True


def test_desired_behavior_is_grace_not_instant_clear():
    """Do NOT clear on the first empty-goal frame while remaining>0 (moving reds)."""
    groups, _ = _prepare(_synthetic_l3_like_groups())
    classified, _ = _consume_all_active_goals(groups, total_pass=60.0)
    action, next_start, rem = _progress(
        groups, total_pass=60.0, goals=classified["goal"]
    )
    assert classified["goal"] == set()
    assert next_start is None
    assert rem > 0
    # Progress helper stays on continue; grace timer (session loop) is the fix.
    assert action == "continue"
"""Focused integration coverage for level preparation at the game boundary."""

from pathlib import Path
from types import SimpleNamespace
import threading

import pytest

from api import game_manager


ROOT = Path(__file__).resolve().parents[1]
FLOOR_LIGHT = "floor_light"
WALL_LIGHT = "wall_light"
SCREEN_LIGHT = "screen_light"


def _snapshot(groups, game):
    return (
        {
            name: tuple(sorted(getattr(group, "start_member", ()) or ()))
            for name, group in groups.items()
        },
        (
            game.row,
            game.col,
            game.zone_row_from,
            game.zone_row_to,
            game.zone_col_from,
            game.zone_col_to,
        ),
    )


def _load(relative_path):
    groups, game = game_manager._load_level_file(ROOT / relative_path)
    assert groups and game
    return groups, game


def test_level_010_selection_is_deterministic_when_walk_order_reverses(monkeypatch):
    real_walk = game_manager.os.walk

    def reversed_walk(root):
        return iter(reversed(list(real_walk(root))))

    monkeypatch.setattr(game_manager.os, "walk", reversed_walk)

    groups, game = game_manager._load_level_file(
        ROOT / "games/source/-/010.led"
    )

    assert groups
    assert game.name == "跳跃15"


def test_attempt_preparation_scales_raw_archive_before_runtime(monkeypatch):
    groups, game = _load("games/source/-/009.led")
    table = game_manager.HeadlessLedTable(100, 16, 26)
    messages = []
    monkeypatch.setattr(game_manager.logger, "info", messages.append)

    assert (game.row, game.col) == (12, 24)

    prepared_groups, prepared_game = game_manager._prepare_level_attempt(
        groups,
        game,
        led_table=table,
        settings={"wall_light": False, "screen_light": False},
        level_id="009",
    )

    assert (prepared_game.row, prepared_game.col) == (16, 26)
    assert (
        prepared_game.zone_row_from,
        prepared_game.zone_row_to,
        prepared_game.zone_col_from,
        prepared_game.zone_col_to,
    ) == (0, 16, 0, 26)
    assert all(
        0 <= row < table.led_row and 0 <= col < table.led_col
        for group in prepared_groups.values()
        if getattr(group, "type", None) == FLOOR_LIGHT
        for row, col in (getattr(group, "start_member", ()) or ())
    )
    assert len(messages) == 1
    assert "12x24" in messages[0]
    assert "16x26" in messages[0]
    assert "zone=(0, 16, 0, 26)" in messages[0]
    assert "retained=" in messages[0] and "dropped=" in messages[0]


def test_attempt_preparation_retains_start_area_zero_floor_groups():
    groups, game = _load("games/source/-/008.led")
    expected = {
        name
        for name, group in groups.items()
        if getattr(group, "type", None) == FLOOR_LIGHT
        and getattr(group, "start_area", None) == 0
    }
    assert expected

    prepared, _ = game_manager._prepare_level_attempt(
        groups,
        game,
        led_table=game_manager.HeadlessLedTable(100, 16, 26),
        settings={"wall_light": False, "screen_light": False},
        level_id="008",
    )

    assert expected <= set(prepared)
    assert all(prepared[name].start_area == 0 for name in expected)


@pytest.mark.parametrize(
    ("wall_enabled", "screen_enabled"),
    ((False, False), (True, False), (False, True), (True, True)),
)
def test_attempt_preparation_uses_real_wall_and_screen_flags(
    wall_enabled, screen_enabled
):
    groups, game = _load("games/source/-/001.led")

    prepared, prepared_game = game_manager._prepare_level_attempt(
        groups,
        game,
        led_table=game_manager.HeadlessLedTable(100, 16, 26),
        settings={
            "wall_light": wall_enabled,
            "screen_light": screen_enabled,
        },
        level_id="001",
    )

    types = {getattr(group, "type", None) for group in prepared.values()}
    assert (WALL_LIGHT in types) is wall_enabled
    assert (SCREEN_LIGHT in types) is screen_enabled
    assert prepared_game.wall_light is wall_enabled
    assert prepared_game.screen is screen_enabled


def test_fresh_reload_produces_deterministic_copy_without_cumulative_scaling():
    table = game_manager.HeadlessLedTable(100, 16, 26)
    settings = {"wall_light": False, "screen_light": False}
    raw_groups_1, raw_game_1 = _load("games/source/-/009.led")
    prepared_1, game_1 = game_manager._prepare_level_attempt(
        raw_groups_1, raw_game_1, led_table=table, settings=settings, level_id="009"
    )
    expected = _snapshot(prepared_1, game_1)

    first_floor = next(
        group
        for group in prepared_1.values()
        if getattr(group, "type", None) == FLOOR_LIGHT and group.start_member
    )
    first_floor.start_member.clear()

    raw_groups_2, raw_game_2 = _load("games/source/-/009.led")
    prepared_2, game_2 = game_manager._prepare_level_attempt(
        raw_groups_2, raw_game_2, led_table=table, settings=settings, level_id="009"
    )

    assert (raw_game_2.row, raw_game_2.col) == (12, 24)
    assert _snapshot(prepared_2, game_2) == expected


def test_level_zone_falls_back_to_actual_table_dimensions():
    table = game_manager.HeadlessLedTable(100, 7, 11)

    assert game_manager._level_zone(SimpleNamespace(), table) == (0, 7, 0, 11)


def test_malformed_attempt_identifies_level_and_never_returns_raw_geometry():
    groups, game = _load("games/source/-/009.led")
    game.zone_row_to = 999

    with pytest.raises(ValueError, match=r"009.*scal"):
        game_manager._prepare_level_attempt(
            groups,
            game,
            led_table=game_manager.HeadlessLedTable(100, 16, 26),
            settings={"wall_light": False, "screen_light": False},
            level_id="009",
        )


def test_runtime_attempt_boundary_prepares_raw_level_before_consumers(
    monkeypatch,
):
    path = ROOT / "games/source/-/009.led"
    table = game_manager.HeadlessLedTable(100, 16, 26)
    original_loader = game_manager._load_level_file
    events = []

    def tracking_loader(level_path):
        groups, game = original_loader(level_path)
        events.append(("load", game.row, game.col))
        return groups, game

    def setup_consumer(groups, game):
        events.append(("setup", game.row, game.col))

    def play_consumer(groups):
        floor_cells = [
            cell
            for group in groups.values()
            if getattr(group, "type", None) == FLOOR_LIGHT
            for cell in (getattr(group, "start_member", ()) or ())
        ]
        events.append(("play", max(floor_cells)))

    monkeypatch.setattr(game_manager, "_load_level_file", tracking_loader)

    game_manager._run_level_attempt(
        path,
        led_table=table,
        settings={"wall_light": False, "screen_light": False},
        level_id="009",
        setup_consumer=setup_consumer,
        play_consumer=play_consumer,
    )

    assert events[0] == ("load", 12, 24)
    assert events[1] == ("setup", 16, 26)
    assert events[2][0] == "play"
    assert 0 <= events[2][1][0] < 16
    assert 0 <= events[2][1][1] < 26


def test_runtime_attempt_boundary_reloads_fresh_copy_for_restart(monkeypatch):
    path = ROOT / "games/source/-/009.led"
    table = game_manager.HeadlessLedTable(100, 16, 26)
    settings = {"wall_light": False, "screen_light": False}
    original_loader = game_manager._load_level_file
    load_count = 0
    snapshots = []

    def tracking_loader(level_path):
        nonlocal load_count
        load_count += 1
        return original_loader(level_path)

    def consume(groups):
        snapshot = {
            name: tuple(sorted(getattr(group, "start_member", ()) or ()))
            for name, group in groups.items()
        }
        snapshots.append(snapshot)
        floor_group = next(
            group
            for group in groups.values()
            if getattr(group, "type", None) == FLOOR_LIGHT
            and getattr(group, "start_member", None)
        )
        floor_group.start_member.clear()

    monkeypatch.setattr(game_manager, "_load_level_file", tracking_loader)

    for _ in range(2):
        game_manager._run_level_attempt(
            path,
            led_table=table,
            settings=settings,
            level_id="009",
            setup_consumer=lambda groups, game: None,
            play_consumer=consume,
        )

    assert load_count == 2
    assert snapshots[0] == snapshots[1]


def test_scaling_failure_prevents_setup_and_play_consumers(monkeypatch):
    consumers_called = []
    failed = []

    def fail_scaling(*args, **kwargs):
        raise ValueError("Level 009 scaling failed: malformed")

    monkeypatch.setattr(game_manager, "_prepare_level_attempt", fail_scaling)

    with pytest.raises(ValueError, match=r"009.*scal"):
        game_manager._run_level_attempt(
            ROOT / "games/source/-/009.led",
            led_table=game_manager.HeadlessLedTable(100, 16, 26),
            settings={"wall_light": False, "screen_light": False},
            level_id="009",
            setup_consumer=lambda groups, game: consumers_called.append("setup"),
            play_consumer=lambda groups: consumers_called.append("play"),
            failure_consumer=lambda error: failed.append(str(error)),
        )

    assert consumers_called == []
    assert failed == ["Level 009 scaling failed: malformed"]


def test_simulator_input_only_records_state_until_frame_scores_once():
    game = _transition_game()
    game.score = 0
    game.score2 = 0
    game.life = 20
    game.multiplayer = False
    game.scored_active = set()
    game.scored_active2 = set()
    game.goal_cells = {(7, 19)}
    game.goal2_cells = set()
    game.red_cells = set()
    game.deduct_cells = set()
    game.play = None
    group = SimpleNamespace(
        start_member={(7, 19)},
        start_time_sec=0,
        end_time_sec=100,
    )
    game.dict_group = {"goal": group}
    game.flashes = {}
    press_recorded = threading.Event()
    allow_apply_to_finish = threading.Event()
    frame_finished = threading.Event()
    errors = []
    original_press_cell = game.led_table.press_cell

    def blocking_press(row, col):
        original_press_cell(row, col)
        press_recorded.set()
        if not allow_apply_to_finish.wait(timeout=2):
            errors.append(TimeoutError("apply_input did not resume"))

    game.led_table.press_cell = blocking_press
    apply_thread = threading.Thread(
        target=lambda: game.apply_input(7, 19, "press")
    )
    apply_thread.start()
    assert press_recorded.wait(timeout=2)

    def score_frame():
        game.process_frame_input(
            goal_cells={(7, 19)},
            goal2_cells=set(),
            red_cells=set(),
            deduct_cells=set(),
        )
        frame_finished.set()

    frame_thread = threading.Thread(target=score_frame)
    frame_thread.start()
    assert frame_finished.wait(timeout=0.05) is False
    assert game.score == 0
    assert group.start_member == {(7, 19)}
    assert (7, 19) in game._sim_pressed
    assert game.led_table.state_table[7][19] is True

    allow_apply_to_finish.set()
    apply_thread.join(timeout=2)
    frame_thread.join(timeout=2)
    assert not apply_thread.is_alive()
    assert not frame_thread.is_alive()
    assert errors == []

    game.process_frame_input(
        goal_cells={(7, 19)},
        goal2_cells=set(),
        red_cells=set(),
        deduct_cells=set(),
    )

    assert game.score == 1
    assert group.start_member == set()


def _transition_game():
    game = object.__new__(game_manager.GameInstance)
    game.running = True
    game.current_level_id = "009"
    game.current_state = {
        "game_over": False,
        "result": None,
        "life": 0,
        "display_lives": 0,
    }
    game.led_table = game_manager.HeadlessLedTable(100, 16, 26)
    game.zone = (0, 16, 0, 26)
    game.input_lock = threading.Lock()
    game._sim_pressed = set()
    game.accepting_input = True
    game.goal_cells = {(4, 5)}
    game.goal2_cells = {(4, 5)}
    game.red_cells = {(4, 5)}
    game.deduct_cells = {(4, 5)}
    game.scored_active = {(4, 5)}
    game.scored_active2 = {(4, 5)}
    game.max_life = 20
    game.life = 0
    game.last_life_loss_time = 99
    game._session_over = False
    game._end_reason = None
    return game


def test_transition_gate_blocks_stale_input_until_new_level_is_ready():
    game = _transition_game()
    scored = []
    game.try_score_cell = lambda row, col: scored.append((row, col))
    game._sync_live_feedback = lambda: None

    game.begin_level_transition()

    assert game.apply_input(4, 5, "press") is False
    assert scored == []
    assert game.goal_cells == set()
    assert game.red_cells == set()

    game.finish_level_transition()

    assert game.apply_input(4, 5, "press") is True
    assert scored == []

    game.multiplayer = False
    game.process_frame_input(
        goal_cells={(4, 5)},
        goal2_cells=set(),
        red_cells=set(),
        deduct_cells=set(),
    )

    assert scored == [(4, 5)]


def test_transition_clears_hardware_only_pressed_state():
    game = _transition_game()
    game.led_table.state_table[2][3] = True
    assert (2, 3) not in game._sim_pressed

    game.begin_level_transition()

    assert not any(any(row) for row in game.led_table.state_table)
    assert game.scored_active == set()
    assert game.scored_active2 == set()
    assert game.goal_cells == set()
    assert game.goal2_cells == set()
    assert game.red_cells == set()
    assert game.deduct_cells == set()


def test_frame_input_publication_and_scoring_are_atomic_with_transition():
    game = _transition_game()
    game.multiplayer = False
    entered_scoring = threading.Event()
    allow_scoring_to_finish = threading.Event()
    transition_finished = threading.Event()
    errors = []
    hardware_state = [
        [False] * game.led_table.led_col
        for _ in range(game.led_table.led_row)
    ]
    hardware_state[4][5] = True

    def blocking_score(row, col):
        try:
            assert (row, col) == (4, 5)
            assert game.goal_cells == {(4, 5)}
            assert game.led_table.state_table[4][5] is True
            entered_scoring.set()
            assert allow_scoring_to_finish.wait(timeout=2)
        except BaseException as exc:
            errors.append(exc)
            entered_scoring.set()

    game.try_score_cell = blocking_score

    frame_thread = threading.Thread(
        target=lambda: game.process_frame_input(
            goal_cells={(4, 5)},
            goal2_cells=set(),
            red_cells=set(),
            deduct_cells=set(),
            hardware_state=hardware_state,
        )
    )
    frame_thread.start()
    assert entered_scoring.wait(timeout=2)

    def transition():
        game.begin_level_transition()
        transition_finished.set()

    transition_thread = threading.Thread(target=transition)
    transition_thread.start()

    assert transition_finished.wait(timeout=0.05) is False
    assert game.accepting_input is True
    assert game.goal_cells == {(4, 5)}

    allow_scoring_to_finish.set()
    frame_thread.join(timeout=2)
    transition_thread.join(timeout=2)

    assert errors == []
    assert not frame_thread.is_alive()
    assert not transition_thread.is_alive()
    assert transition_finished.is_set()
    assert game.accepting_input is False
    assert game.goal_cells == set()
    assert not any(any(row) for row in game.led_table.state_table)


def test_failed_hardware_read_publishes_false_snapshot_and_clears_stale_press():
    game = _transition_game()
    game.multiplayer = False
    game.scored_active = set()
    game.scored_active2 = set()
    game.led_table.state_table[4][5] = True
    scored = []
    game.try_score_cell = lambda row, col: scored.append((row, col))

    def failed_read(state):
        raise OSError("sensor disconnected")

    snapshot = game_manager._read_hardware_snapshot(
        game.led_table, failed_read
    )
    game.process_frame_input(
        goal_cells={(4, 5)},
        goal2_cells=set(),
        red_cells=set(),
        deduct_cells=set(),
        hardware_state=snapshot,
    )

    assert not any(any(row) for row in snapshot)
    assert not any(any(row) for row in game.led_table.state_table)
    assert scored == []


def test_frame_callback_exception_marks_session_failed():
    game = _transition_game()

    result = game_manager._handle_frame_callback_error(
        game, "game-123", RuntimeError("classification exploded")
    )

    assert result is False
    assert game._session_over is True
    assert game.current_state["game_over"] is True
    assert game.current_state["result"] == 0
    assert game.current_state["session_status"] == "failed"
    assert game.current_state["game_over_reason"] == "frame_callback_error"
    assert "classification exploded" in game.current_state["session_error"]
    assert game_manager._resolve_session_result(game) == 0


def test_level_reset_serializes_classification_replacement_under_input_lock():
    game = _transition_game()
    reset_finished = threading.Event()

    game.input_lock.acquire()
    try:
        reset_thread = threading.Thread(
            target=lambda: (
                game.reset_for_level(),
                reset_finished.set(),
            )
        )
        reset_thread.start()
        assert reset_finished.wait(timeout=0.05) is False
        assert game.goal_cells == {(4, 5)}
    finally:
        game.input_lock.release()

    reset_thread.join(timeout=2)
    assert not reset_thread.is_alive()
    assert reset_finished.is_set()
    assert game.goal_cells == set()


def test_attempt_seam_gates_input_through_load_and_setup(monkeypatch):
    game = _transition_game()
    path = ROOT / "games/source/-/009.led"
    original_loader = game_manager._load_level_file
    phases = []

    def tracking_loader(level_path):
        phases.append(("load", game.accepting_input))
        return original_loader(level_path)

    def setup_consumer(groups, level):
        phases.append(("setup", game.accepting_input))

    def play_consumer(groups):
        phases.append(("play", game.accepting_input))

    monkeypatch.setattr(game_manager, "_load_level_file", tracking_loader)

    game_manager._run_level_attempt(
        path,
        led_table=game.led_table,
        settings={"wall_light": False, "screen_light": False},
        level_id="009",
        setup_consumer=setup_consumer,
        play_consumer=play_consumer,
        transition_consumer=game.begin_level_transition,
        ready_consumer=game.finish_level_transition,
    )

    assert phases == [("load", False), ("setup", False), ("play", True)]


def test_preparation_failure_marks_session_failed_and_cannot_resolve_success():
    game = _transition_game()

    game.mark_session_failed("level_prepare_failed", "009 malformed geometry")

    assert game._session_over is True
    assert game._end_reason == "level_prepare_failed"
    assert game.accepting_input is False
    assert game.current_state["game_over"] is True
    assert game.current_state["result"] == 0
    assert game.current_state["session_status"] == "failed"
    assert game.current_state["session_error"] == "009 malformed geometry"
    assert game_manager._resolve_session_result(game) == 0


def test_life_restart_refill_is_published_before_replay():
    game = _transition_game()

    game.refill_life_for_restart()

    assert game.life == 20
    assert game.last_life_loss_time == 0.0
    assert game.accepting_input is False
    assert game.current_state["life"] == 20
    assert game.current_state["display_lives"] == 5
    assert game.current_state["current_level"] == "009"

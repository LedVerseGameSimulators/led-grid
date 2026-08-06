"""Run effect .led mini-levels inside the marathon session loop."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Callable, Optional

from loguru import logger

from .config import GAMES_ROOT

EFFECTS_ENV = "GRID_EFFECTS_DIR"
_PHASE_COUNTDOWN = "countdown"
_PHASE_CLEAR = "level_clear"
_PHASE_FAIL = "level_fail"


def get_effects_dir() -> Path:
    override = os.environ.get(EFFECTS_ENV)
    if override:
        return Path(override)
    return GAMES_ROOT / "source" / "effects"


def _board_time_sec(groups) -> float:
    try:
        return max(
            (getattr(g, "end_time_sec", 0.0) for g in groups.values()),
            default=0.0,
        )
    except Exception:
        return 0.0


def _countdown_digit(groups, total_pass: float) -> Optional[int]:
    """Return 3/2/1 while a green digit group is active."""
    for name, group in groups.items():
        st = getattr(group, "start_time_sec", 0.0)
        et = getattr(group, "end_time_sec", 0.0)
        if st <= total_pass < et and "digit" in str(name).lower():
            for digit in (3, 2, 1):
                if str(digit) in str(name):
                    return digit
    return None


def _effect_led_display(groups, total_pass: float, *, rows: int, cols: int):
    from .game_manager import _group_main_color

    led_display = [[0, 0, 0] for _ in range(rows * cols)]
    for group in groups.values():
        if getattr(group, "type", None) != "floor_light":
            continue
        st = getattr(group, "start_time_sec", 0.0)
        et = getattr(group, "end_time_sec", 0.0)
        if not (st <= total_pass <= et):
            continue
        rgb = _group_main_color(getattr(group, "color", (0, 0, 0)))
        for row, col in getattr(group, "start_member", ()) or ():
            row, col = int(round(row)), int(round(col))
            if 0 <= row < rows and 0 <= col < cols:
                led_display[row * cols + col] = [int(rgb[0]), int(rgb[1]), int(rgb[2])]
    return led_display


def run_effect_led(
    path: Path,
    *,
    game,
    led_table,
    settings,
    play,
    phase: str,
    effect_name: str,
    publish_frame: Callable,
    stop_flag: Callable[[], bool],
    audio=None,
    on_digit=None,
) -> None:
    """Load one effect archive and run Play.running() with a no-score callback."""
    from .game_manager import (
        LevelAttemptPreparationError,
        _load_level_file,
        _prepare_level_attempt,
        _run_level_attempt,
    )

    path = Path(path)
    if not path.is_file():
        logger.warning(f"Effect archive missing: {path}")
        game.update_state(phase=phase, accepting_input=False, effect_name=effect_name)
        return

    last_digit = {"v": None}

    def _setup(_dg, _go):
        pass

    def _play(dg):
        board_time = _board_time_sec(dg)
        last_tick = {"t": -1.0}

        def _callback(_play_self, dgroup, _time_pass, total_pass):
            if stop_flag() or game._session_over:
                return False
            if total_pass >= board_time:
                return False

            digit = _countdown_digit(dgroup, total_pass)
            if phase == _PHASE_COUNTDOWN and digit != last_digit["v"]:
                last_digit["v"] = digit
                if digit is not None and audio is not None:
                    audio.play_countdown_tick()
                if on_digit is not None:
                    on_digit(digit)

            led_display = _effect_led_display(
                dgroup,
                total_pass,
                rows=led_table.led_row,
                cols=led_table.led_col,
            )
            publish_frame(
                led_display=led_display,
                phase=phase,
                accepting_input=False,
                countdown_digit=digit,
                effect_name=effect_name,
            )
            time.sleep(0.008)
            return True

        play.callback = _callback
        play.running_state = True
        play.total_pass = 0
        play.running(dg)

    def _transition():
        game.begin_level_transition()
        game.update_state(phase=phase, accepting_input=False, effect_name=effect_name)

    try:
        _run_level_attempt(
            path,
            led_table=led_table,
            settings=settings,
            level_id=path.stem,
            setup_consumer=_setup,
            play_consumer=_play,
            transition_consumer=_transition,
        )
    except LevelAttemptPreparationError as exc:
        logger.error(f"Effect load failed {path}: {exc}")

    game.update_state(countdown_digit=None, effect_name=None)

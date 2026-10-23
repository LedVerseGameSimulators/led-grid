"""Regression: scored/consumed tiles must not white-flash on hit."""

from __future__ import annotations

import time
from types import SimpleNamespace

from api import game_manager
from api.game_manager import _FLASH_ON_COLOR
from model.setting import Color, Setting

FLOOR_LIGHT = Setting.FLOOR_LIGHT


def _game_with_group(cells, rgb):
    group = SimpleNamespace(
        type=FLOOR_LIGHT,
        color=[rgb, rgb, rgb],
        start_member=set(cells),
        start_time_sec=0,
        end_time_sec=100,
    )
    game = game_manager.GameInstance("flash", "card", 1, "normal")
    game.dict_group = {"floor": group}
    game.flashes = {}
    game.scored_active = set()
    game.scored_active2 = set()
    game.multiplayer = False
    game.score = 0
    game.life = 20
    game.goal_cells = set()
    game.goal2_cells = set()
    game.red_cells = set()
    game.deduct_cells = set()
    return game, group


def _led_display_after_flash_overlay(game, cell, cols=26):
    """What the removed 2b FLASH block would paint on top of a black cell."""
    led_display = [[0, 0, 0] for _ in range(16 * cols)]
    now = time.time()
    for flash_cell, t0 in list(game.flashes.items()):
        el = now - t0
        if el > 0.4:
            continue
        fi, fj = flash_cell
        on = int(el / 0.1) % 2 == 0
        led_display[fi * cols + fj] = list(_FLASH_ON_COLOR) if on else [0, 0, 0]
    i, j = cell
    return led_display[i * cols + j]


def test_goal_cell_score_consumes_without_hit_flash():
    cell = (3, 5)
    game, group = _game_with_group([cell], Color.BLUE)
    game.goal_cells = {cell}

    game.try_score_cell(*cell, total_pass=0)

    assert game.score == 1
    assert cell not in group.start_member
    assert game.flashes == {}
    assert _led_display_after_flash_overlay(game, cell) != list(_FLASH_ON_COLOR)


def test_deduct_tile_consume_without_hit_flash():
    cell = (4, 6)
    game, group = _game_with_group([cell], Color.DEDUCT_COLOR)
    game.deduct_cells = {cell}

    game.try_score_cell(*cell, total_pass=0)

    assert cell not in group.start_member
    assert game.flashes == {}
    assert _led_display_after_flash_overlay(game, cell) != list(_FLASH_ON_COLOR)

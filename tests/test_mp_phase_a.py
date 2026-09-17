"""Phase A MP smoke: lives-only hazards + goal color HUD (backend).

Drive GameManager / try_score_cell / update_state — no browser.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from api import game_manager
from api.level_scaler import prepare_level_for_platform
from model.setting import Color, Setting


ROOT = Path(__file__).resolve().parents[1]
LEDB_2P = ROOT / "games" / "source" / "----" / "01.ledb"
FLOOR_LIGHT = Setting.FLOOR_LIGHT

# Parked: either-player advance is Phase B — do not fail this suite on it.
PHASE_B_EITHER_PLAYER_ADVANCE = "parked Phase B"


def _rings(rgb):
    return [rgb, rgb, rgb]


def _group(
    name,
    rgb,
    cells,
    *,
    start=0.0,
    end=100.0,
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
        speed=1.0,
        edge_run_into=Setting.BACK,
        activity_area=((0, 8), (0, 13)),
    )


def _level(rows=8, cols=13):
    return SimpleNamespace(
        name="mp-phase-a",
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
    game = game_manager.GameInstance("phase-a", "card", 1, "normal")
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


def _arm_hazards(game, groups, *, multiplayer):
    classified = _classify(groups, multiplayer=multiplayer)
    game.goal_cells = classified["goal"]
    game.goal2_cells = classified["goal2"]
    game.red_cells = classified["red"]
    game.deduct_cells = classified["deduct"]
    return classified


# ── 1. Create 2P session → multiplayer True ───────────────────────────────


def test_create_game_2p_ledb_sets_multiplayer():
    assert LEDB_2P.is_file(), f"missing 2P archive: {LEDB_2P}"
    mgr = game_manager.GameManager()
    gid = mgr.create_game(card_id="mp-phase-a", level="01", difficulty="normal")
    game = mgr.get_game(gid)
    assert game is not None
    assert game.multiplayer is True
    assert "----" in game_manager._TIERS_2P
    mgr.clear_all()


# ── 2. After frames: goal_color / goal2_color published (blue/orange) ─────


@pytest.fixture()
def mp_client(monkeypatch):
    os.environ["DISABLE_AUDIO"] = "1"
    os.environ["USE_SERIAL_HD"] = "0"
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    from fastapi.testclient import TestClient
    import api.main as main_mod

    fresh = game_manager.GameManager()
    monkeypatch.setattr(game_manager, "_manager", fresh)
    monkeypatch.setattr(game_manager, "get_manager", lambda: fresh)
    main_mod.game_manager = fresh
    return TestClient(main_mod.app), fresh


def _wait_playing(client, game_id, *, timeout=60.0):
    deadline = time.time() + timeout
    seen = []
    while time.time() < deadline:
        data = client.get(f"/game-state/{game_id}").json()
        assert data.get("success"), data
        st = data["state"]
        p = st.get("phase")
        if p and p not in seen:
            seen.append(p)
        if p == "playing" and st.get("accepting_input"):
            return st
        if st.get("game_over"):
            raise AssertionError(f"game over before playing; phases={seen} state={st}")
        time.sleep(0.05)
    raise AssertionError(f"Timed out waiting for playing; phases={seen}")


def test_mp_session_publishes_goal_colors(mp_client, monkeypatch):
    """Real ----/01.ledb session: frame loop publishes P1 blue / P2 orange."""
    client, _mgr = mp_client
    assert LEDB_2P.is_file()

    monkeypatch.setattr(
        game_manager,
        "_build_level_sequence",
        lambda _start: [str(LEDB_2P)],
    )

    resp = client.post(
        "/start-game",
        json={"card_id": "mp-phase-a", "level": "01", "difficulty": "normal"},
    )
    body = resp.json()
    assert body.get("success"), body
    gid = body["game_id"]

    st = _wait_playing(client, gid, timeout=90.0)
    assert st.get("multiplayer") is True

    gc = st.get("goal_color")
    gc2 = st.get("goal2_color")
    assert gc is not None, "goal_color missing after frames"
    assert gc2 is not None, "goal2_color missing after frames"
    assert tuple(gc) == game_manager._GRID_P1_COLOR  # blue
    assert tuple(gc2) == game_manager._GRID_P2_COLOR  # orange
    assert st.get("goal_color_hex") == "#0000fe"
    assert st.get("goal2_color_hex") == "#fe8000"

    client.post(
        "/logout",
        json={"game_id": gid, "card_id": "mp-phase-a"},
    )


# ── 3–5. MP red / DEDUCT / rate-limit ─────────────────────────────────────


def test_mp_red_life_only_scores_unchanged(monkeypatch):
    groups, _ = _prepare({"red": _group("red", Color.RED, {(1, 1)})})
    game = _game(groups, multiplayer=True)
    game.score = 5
    game.score2 = 7
    game.life = 20
    game._life_count_time = 1.0
    game.last_life_loss_time = 0
    now = [100.0]
    monkeypatch.setattr(game_manager.time, "time", lambda: now[0])
    _arm_hazards(game, groups, multiplayer=True)

    # Scaled (1,1) → (2,2)
    game.try_score_cell(2, 2)
    assert game.life == 19
    assert (game.score, game.score2) == (5, 7)


def test_mp_deduct_life_only_consumes_scores_unchanged(monkeypatch):
    groups, _ = _prepare(
        {"deduct": _group("deduct", Color.DEDUCT_COLOR, {(2, 2)})}
    )
    game = _game(groups, multiplayer=True)
    game.score = 4
    game.score2 = 6
    game.life = 15
    _arm_hazards(game, groups, multiplayer=True)

    # Scaled (2,2) → (4,4)
    game.try_score_cell(4, 4)
    assert game.life == 14
    assert (game.score, game.score2) == (4, 6)
    assert (4, 4) not in groups["deduct"].start_member
    # Second hit: already consumed — no further life loss
    game.try_score_cell(4, 4)
    assert game.life == 14


def test_mp_red_rate_limit_no_spam(monkeypatch):
    groups, _ = _prepare({"red": _group("red", Color.RED, {(1, 1)})})
    game = _game(groups, multiplayer=True)
    game.score = 3
    game.score2 = 3
    game.life = 20
    game._life_count_time = 1.2
    game.last_life_loss_time = 0
    now = [50.0]
    monkeypatch.setattr(game_manager.time, "time", lambda: now[0])
    _arm_hazards(game, groups, multiplayer=True)

    game.try_score_cell(2, 2)
    assert game.life == 19
    now[0] = 50.5
    game.try_score_cell(2, 2)
    assert game.life == 19  # rate-limited
    assert (game.score, game.score2) == (3, 3)
    now[0] = 51.3
    game.try_score_cell(2, 2)
    assert game.life == 18
    assert (game.score, game.score2) == (3, 3)


# ── 6. 1P regression ─────────────────────────────────────────────────────


def test_1p_red_still_score_and_life(monkeypatch):
    groups, _ = _prepare({"red": _group("red", Color.RED, {(1, 1)})})
    game = _game(groups, multiplayer=False)
    game.score = 5
    game.life = 20
    game._life_count_time = 1.0
    game.last_life_loss_time = 0
    now = [10.0]
    monkeypatch.setattr(game_manager.time, "time", lambda: now[0])
    _arm_hazards(game, groups, multiplayer=False)

    game.try_score_cell(2, 2)
    assert (game.score, game.life) == (4, 19)


def test_1p_deduct_score_consume_no_life():
    groups, _ = _prepare(
        {"deduct": _group("deduct", Color.DEDUCT_COLOR, {(2, 2)})}
    )
    game = _game(groups, multiplayer=False)
    game.score = 5
    game.life = 20
    _arm_hazards(game, groups, multiplayer=False)

    game.try_score_cell(4, 4)
    assert (game.score, game.life) == (4, 20)
    assert (4, 4) not in groups["deduct"].start_member


# ── 7. Phase B either-player advance not implemented (note only) ──────────


def test_either_player_advance_not_implemented_yet():
    """Remaining counts BOTH P1+P2 colors — clearing only one side does not clear."""
    groups, _ = _prepare(
        {
            "p1": _group("p1", Color.BLUE, {(1, 1)}),
            "p2": _group("p2", (254, 128, 0), {(2, 2)}),
        }
    )
    # Consume only P1 cells
    groups["p1"].start_member.clear()
    remaining = game_manager._remaining_scoreable_members(
        groups, multiplayer=True
    )
    assert remaining > 0, "P2 tiles should still block clear (Phase B not shipped)"
    action, _, rem = game_manager._level_progress_action(
        groups,
        total_pass=2.0,
        multiplayer=True,
        active_goal_cells=set(),
        active_goal2_cells=_classify(groups, multiplayer=True)["goal2"],
    )
    assert action == "continue"
    assert rem > 0
    assert PHASE_B_EITHER_PLAYER_ADVANCE == "parked Phase B"

"""Layer A — effects session loop proofs (TESTING_CONTRACT T1–T8)."""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_EFFECTS = ROOT / "tests" / "fixtures" / "effects"
FIXTURE_LEVELS = ROOT / "tests" / "fixtures" / "levels"


@pytest.fixture()
def effects_client(monkeypatch):
    """TestClient with fast effects + fresh game manager."""
    os.environ["DISABLE_AUDIO"] = "1"
    os.environ["GRID_EFFECTS_DIR"] = str(FIXTURE_EFFECTS)
    os.environ["USE_SERIAL_HD"] = "0"

    import api.game_manager as gm
    import api.main as main_mod

    fresh = gm.GameManager()
    monkeypatch.setattr(gm, "_manager", fresh)
    monkeypatch.setattr(gm, "get_manager", lambda: fresh)
    main_mod.game_manager = fresh
    return TestClient(main_mod.app)


def _wait_phase(client, game_id, phase, *, timeout=15.0, poll=0.02):
    deadline = time.time() + timeout
    seen = []
    while time.time() < deadline:
        resp = client.get(f"/game-state/{game_id}")
        data = resp.json()
        assert data.get("success"), data
        st = data["state"]
        p = st.get("phase")
        if p and p not in seen:
            seen.append(p)
        if p == phase:
            return st
        if st.get("game_over") and phase in ("session_end", "level_clear"):
            return st
        time.sleep(poll)
    raise AssertionError(f"Timed out waiting for phase={phase!r}, saw {seen}")


def _wait_playing(client, game_id, *, timeout=15.0):
    return _wait_phase(client, game_id, "playing", timeout=timeout)


def _start(client, monkeypatch, *, levels, game_time_sec=300.0, max_life=20):
    import api.game_manager as gm

    seq = [str(p) for p in levels]

    def _fake_sequence(_start_level):
        return seq

    monkeypatch.setattr(gm, "_build_level_sequence", _fake_sequence)

    real = gm.load_real_settings()

    def _settings():
        s = dict(real)
        s["game_time_sec"] = game_time_sec
        s["life_value"] = max_life
        return s

    monkeypatch.setattr(gm, "load_real_settings", _settings)

    resp = client.post(
        "/start-game",
        json={"card_id": "test-card", "level": "001", "difficulty": "easy"},
    )
    body = resp.json()
    assert body.get("success"), body
    return body["game_id"]


def _press(client, game_id, row, col, action="press"):
    return client.post(
        "/game-input",
        json={"game_id": game_id, "row": row, "col": col, "type": action},
    ).json()


def _find_blue_cell(state):
    display = state.get("led_display") or []
    cols = state.get("grid_cols") or 26
    for idx, rgb in enumerate(display):
        if len(rgb) >= 3 and rgb[2] >= 200 and rgb[0] < 80 and rgb[1] < 80:
            return idx // cols, idx % cols
    return 4, 4


# ── T1 Session start: countdown → playing, accepting_input=true ──────────


def test_t1_session_start_countdown_then_playing(effects_client, monkeypatch):
    client = effects_client
    gid = _start(
        client,
        monkeypatch,
        levels=[FIXTURE_LEVELS / "quick_clear.led"],
    )
    st = _wait_playing(client, gid)
    assert st.get("accepting_input") is True
    assert st.get("phase") == "playing"


# ── T7 Input gating during effect phases ─────────────────────────────────


def test_t7_input_blocked_during_countdown(effects_client, monkeypatch):
    client = effects_client
    gid = _start(
        client,
        monkeypatch,
        levels=[FIXTURE_LEVELS / "quick_clear.led"],
    )
    _wait_phase(client, gid, "countdown", timeout=5)
    before = client.get(f"/game-state/{gid}").json()["state"]
    score_before = before.get("score", 0)
    assert before.get("accepting_input") is False
    _press(client, gid, 4, 4)
    mid = client.get(f"/game-state/{gid}").json()["state"]
    assert mid.get("score", 0) == score_before


# ── T8 Playing accepts input ─────────────────────────────────────────────


def test_t8_playing_press_changes_score(effects_client, monkeypatch):
    client = effects_client
    gid = _start(
        client,
        monkeypatch,
        levels=[FIXTURE_LEVELS / "quick_clear.led"],
    )
    st = _wait_playing(client, gid)
    row, col = _find_blue_cell(st)
    resp = _press(client, gid, row, col)
    assert resp.get("success") is True
    deadline = time.time() + 5
    while time.time() < deadline:
        after = client.get(f"/game-state/{gid}").json()["state"]
        if after.get("score", 0) > st.get("score", 0):
            break
        time.sleep(0.05)
    assert after.get("score", 0) >= 1


# ── T2 Countdown after mid-session clear ─────────────────────────────────


def test_t2_clear_advances_with_countdown_between_levels(effects_client, monkeypatch):
    client = effects_client
    gid = _start(
        client,
        monkeypatch,
        levels=[
            FIXTURE_LEVELS / "quick_clear.led",
            FIXTURE_LEVELS / "level_b.led",
        ],
    )
    st = _wait_playing(client, gid)
    row, col = _find_blue_cell(st)
    _press(client, gid, row, col)
    _wait_phase(client, gid, "level_clear", timeout=10)
    _wait_phase(client, gid, "countdown", timeout=10)
    playing = _wait_playing(client, gid, timeout=10)
    assert playing.get("accepting_input") is True


# ── T3 Level fail restart (>10 s left) ───────────────────────────────────


def test_t3_fail_restart_same_level(effects_client, monkeypatch):
    client = effects_client
    gid = _start(
        client,
        monkeypatch,
        levels=[FIXTURE_LEVELS / "hazard.led"],
        game_time_sec=300.0,
        max_life=1,
    )
    st = _wait_playing(client, gid)
    level_before = st.get("current_level")
    score_before = st.get("score", 0)
    _press(client, gid, 6, 6)
    deadline = time.time() + 8
    while time.time() < deadline:
        cur = client.get(f"/game-state/{gid}").json()["state"]
        if cur.get("phase") == "level_fail":
            break
        time.sleep(0.05)
    assert client.get(f"/game-state/{gid}").json()["state"].get("phase") == "level_fail"
    _wait_phase(client, gid, "countdown", timeout=10)
    replay = _wait_playing(client, gid, timeout=10)
    assert replay.get("current_level") == level_before
    assert replay.get("score", 0) == score_before


# ── T4 Session end on timer — no countdown after ─────────────────────────


def test_t4_timer_expire_session_end_no_countdown(effects_client, monkeypatch):
    client = effects_client
    gid = _start(
        client,
        monkeypatch,
        levels=[FIXTURE_LEVELS / "quick_clear.led"],
        game_time_sec=1.5,
    )
    _wait_playing(client, gid, timeout=8)
    deadline = time.time() + 12
    phases_after_play = []
    while time.time() < deadline:
        st = client.get(f"/game-state/{gid}").json()["state"]
        if st.get("game_over"):
            break
        p = st.get("phase")
        if p and p != "playing":
            phases_after_play.append(p)
        time.sleep(0.05)
    final = client.get(f"/game-state/{gid}").json()["state"]
    assert final.get("game_over") is True
    assert "countdown" not in phases_after_play


# ── T5 Life=0 with ≤10 s → clear path, no fail/countdown ─────────────────


def test_t5_life_zero_near_timeout_uses_clear_not_fail(effects_client, monkeypatch):
    import api.game_manager as gm

    client = effects_client
    gid = _start(
        client,
        monkeypatch,
        levels=[FIXTURE_LEVELS / "hazard.led"],
        game_time_sec=300.0,
        max_life=1,
    )
    game = gm.get_manager().get_game(gid)
    _wait_playing(client, gid)
    game.session_start = time.time() - 296.0
    _press(client, gid, 6, 6)
    deadline = time.time() + 12
    saw_fail = False
    while time.time() < deadline:
        st = client.get(f"/game-state/{gid}").json()["state"]
        if st.get("phase") == "level_fail":
            saw_fail = True
        if st.get("game_over"):
            break
        time.sleep(0.05)
    final = client.get(f"/game-state/{gid}").json()["state"]
    assert final.get("game_over") is True
    assert saw_fail is False


# ── T6 Last level cleared → session end, no countdown ────────────────────


def test_t6_last_level_cleared_session_end(effects_client, monkeypatch):
    client = effects_client
    gid = _start(
        client,
        monkeypatch,
        levels=[FIXTURE_LEVELS / "quick_clear.led"],
    )
    st = _wait_playing(client, gid)
    row, col = _find_blue_cell(st)
    _press(client, gid, row, col)
    _wait_phase(client, gid, "level_clear", timeout=10)
    deadline = time.time() + 12
    countdown_after_clear = False
    while time.time() < deadline:
        cur = client.get(f"/game-state/{gid}").json()["state"]
        if cur.get("phase") == "countdown" and cur.get("game_over") is not True:
            countdown_after_clear = True
        if cur.get("game_over"):
            break
        time.sleep(0.05)
    assert countdown_after_clear is False
    assert client.get(f"/game-state/{gid}").json()["state"].get("game_over") is True

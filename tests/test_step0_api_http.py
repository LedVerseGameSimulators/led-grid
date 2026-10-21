"""Step 0 HTTP: /save-score, /scores, /logout must not write scores."""
import sqlite3

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def step0_client(tmp_path, monkeypatch):
    import api.database as db_mod
    import api.main as main_mod
    import api.game_manager as game_manager

    path = str(tmp_path / "hex.sqlite")
    monkeypatch.setattr(db_mod, "_SCORES_DB", path)
    monkeypatch.setattr(db_mod, "DBOperation", None)
    monkeypatch.setattr(db_mod, "GAME_NAME", "grid_step0_test")

    fresh_db = db_mod.Database()
    main_mod.db = fresh_db

    fresh_mgr = game_manager.GameManager()
    monkeypatch.setattr(game_manager, "_manager", fresh_mgr)
    monkeypatch.setattr(game_manager, "get_manager", lambda: fresh_mgr)
    main_mod.game_manager = fresh_mgr

    return TestClient(main_mod.app), fresh_db, path


def _count_rows(db_path):
    con = sqlite3.connect(db_path)
    try:
        return con.execute("SELECT COUNT(*) FROM hex_scores").fetchone()[0]
    finally:
        con.close()


def test_save_score_and_scores_export_rfid_fields(step0_client):
    client, _db, _path = step0_client
    payload = {
        "card_id": "CARD-A",
        "level": "1",
        "score": 100,
        "play_mode": "quick_play",
        "session_id": 7,
        "group_id": 2,
        "roster_size_at_play": 3,
        "roster_player_ids": [10, 11, 12],
    }
    r = client.post("/save-score", json=payload)
    assert r.status_code == 200
    assert r.json().get("success") is True

    scores = client.get("/scores", params={"since": "1970-01-01T00:00:00"}).json()
    assert scores.get("success") is True
    assert len(scores["scores"]) == 1
    row = scores["scores"][0]
    assert row["play_mode"] == "quick_play"
    assert row["session_id"] == 7
    assert row["group_id"] == 2
    assert row["roster_size_at_play"] == 3
    assert row["roster_player_ids"] == "[10, 11, 12]"


def test_logout_does_not_insert_hex_scores_row(step0_client, monkeypatch):
    client, _db, db_path = step0_client
    import api.main as main_mod

    monkeypatch.setattr(
        main_mod.game_manager,
        "stop_game",
        lambda _gid: {"success": True, "state": {"score": 999}},
    )

    before = _count_rows(db_path)
    r = client.post(
        "/logout",
        json={"game_id": "fake-game", "card_id": ""},
    )
    assert r.status_code == 200
    assert r.json().get("success") is True
    after = _count_rows(db_path)
    assert after == before == 0

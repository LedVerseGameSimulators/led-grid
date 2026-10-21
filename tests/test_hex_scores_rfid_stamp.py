"""Step 0: hex_scores RFID play-fact columns and poll cursor (A1)."""
import os
import sqlite3
import tempfile

import pytest

import api.database as db_mod
from api.database import Database


@pytest.fixture
def scores_db(tmp_path, monkeypatch):
    path = str(tmp_path / "test_hex.sqlite")
    monkeypatch.setattr(db_mod, "_SCORES_DB", path)
    monkeypatch.setattr(db_mod, "DBOperation", None)
    monkeypatch.setattr(db_mod, "GAME_NAME", "grid_test")
    return Database()


def test_record_and_get_scores_since_includes_rfid_fields(scores_db):
    ok = scores_db.record_game_score({
        "card_id": "A1",
        "card_id2": "B2",
        "multiplayer": True,
        "level": "1",
        "score": 42,
        "score2": 7,
        "play_mode": "team_battle",
        "session_id": 10,
        "group_id": 3,
        "roster_size_at_play": 4,
        "roster_player_ids": [1, 2, 3, 4],
        "session_id2": 11,
        "group_id2": 5,
        "roster_size_at_play2": 2,
        "roster_player_ids2": [8, 9],
    })
    assert ok is True

    rows = scores_db.get_scores_since("1970-01-01T00:00:00")
    assert len(rows) == 1
    row = rows[0]
    assert row["play_mode"] == "team_battle"
    assert row["session_id"] == 10
    assert row["group_id"] == 3
    assert row["roster_size_at_play"] == 4
    assert row["roster_player_ids"] == '[1, 2, 3, 4]'
    assert row["session_id2"] == 11
    assert row["group_id2"] == 5
    assert row["roster_size_at_play2"] == 2
    assert row["roster_player_ids2"] == '[8, 9]'


def test_get_scores_since_uses_gte_cursor(scores_db, monkeypatch):
    """Same-second rows must not be skipped (A1)."""
    path = db_mod._SCORES_DB
    scores_db.record_game_score({"card_id": "X", "level": "1", "score": 1})
    con = sqlite3.connect(path)
    ts = con.execute("SELECT ts FROM hex_scores LIMIT 1").fetchone()[0]
    con.execute(
        "INSERT INTO hex_scores (card_id, level, score, ts, game) VALUES (?,?,?,?,?)",
        ("Y", "1", 2, ts, "grid_test"),
    )
    con.commit()
    con.close()

    rows = scores_db.get_scores_since(ts)
    card_ids = {r["card_id"] for r in rows}
    assert card_ids == {"X", "Y"}

"""
Database Wrapper - MySQL connection and queries
"""
from .config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, GAME_NAME
from loguru import logger
import sys
import os
import sqlite3
import threading
import datetime

# Try to import db_operation from game; optional for headless testing
DBOperation = None
try:
    from database.db_operation import DBOperation
except ImportError as e:
    logger.warning(f"DBOperation not available (OK for headless testing): {e}")

# Our own scores live in the same sqlite file as the game DB.
_SCORES_DB = "/Users/apple/parallel-work/ledhexagon_clone/setting/ledplaydb.sqlite"


class Database:
    """Wrapper around game's db_operation.py"""

    def __init__(self):
        self.db_op = None
        if DBOperation:
            try:
                self.db_op = DBOperation('localhost')  # Climb decompiled version needs ip_address arg
                logger.info(f"Database connected to {DB_NAME}")
            except Exception as e:
                logger.warning(f"DBOperation init failed (OK for headless testing): {e}")
        self._scores_lock = threading.Lock()
        self._ensure_scores_table()

    # ===== OUR SCORES TABLE (kiosk leaderboard) =====
    def _scores_conn(self):
        return sqlite3.connect(_SCORES_DB, timeout=5)

    def _ensure_scores_table(self):
        """Create the hex_scores table if missing (clean kiosk leaderboard)."""
        try:
            with self._scores_lock:
                con = self._scores_conn()
                con.execute("""
                    CREATE TABLE IF NOT EXISTS hex_scores (
                        id          INTEGER PRIMARY KEY AUTOINCREMENT,
                        card_id     TEXT,
                        level       TEXT,
                        score       INTEGER,
                        score2      INTEGER,
                        life        INTEGER,
                        lives_start INTEGER,
                        result      INTEGER,
                        time_used   REAL,
                        ts          TEXT
                    )
                """)
                # Add columns if upgrading an older table (ignore if present).
                for col, typ in (("lives_start", "INTEGER"), ("result", "INTEGER"),
                                 ("score2", "INTEGER"), ("game", "TEXT")):
                    try:
                        con.execute(f"ALTER TABLE hex_scores ADD COLUMN {col} {typ}")
                    except Exception:
                        pass
                con.commit()
                con.close()
        except Exception as e:
            logger.error(f"Could not ensure hex_scores table: {e}")

    # ===== PLAYER LOOKUP =====
    def get_player_by_card(self, card_id: str):
        """Lookup player by RFID card ID"""
        if not self.db_op:
            return None
        try:
            result = self.db_op.search_custom_by_field("card_id", card_id)
            if result and len(result) > 0:
                return result[0]  # Return first match
            return None
        except Exception as e:
            logger.error(f"Error getting player by card: {e}")
            return None

    def get_player_by_id(self, custom_id: int):
        """Lookup player by customer ID"""
        if not self.db_op:
            return None
        try:
            result = self.db_op.search_custom_tb_by_id(custom_id)
            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"Error getting player by ID: {e}")
            return None

    # ===== SCORE RECORDING =====
    def record_game_score(self, game_info: dict):
        """Record a finished game to hex_scores.
        game_info keys: card_id, level, score, life, time_used."""
        try:
            with self._scores_lock:
                con = self._scores_conn()
                con.execute(
                    "INSERT INTO hex_scores (card_id, level, score, score2, life, "
                    "lives_start, result, time_used, ts, game) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (
                        str(game_info.get("card_id", "")),
                        str(game_info.get("level", "")),
                        int(game_info.get("score", 0)),
                        int(game_info.get("score2", 0)),
                        int(game_info.get("life", 0)),
                        int(game_info.get("lives_start", 0)),
                        game_info.get("result"),
                        float(game_info.get("time_used", 0.0)),
                        datetime.datetime.now().isoformat(timespec="seconds"),
                        GAME_NAME,
                    ),
                )
                con.commit()
                con.close()
            logger.info(f"Recorded score: {game_info}")
            return True
        except Exception as e:
            logger.error(f"Error recording score: {e}")
            return False

    # ===== SESSION TIMER =====
    def update_session_start(self, card_id: str, session_start_time: str):
        """Update session start time for 60-min timer"""
        if not self.db_op:
            return False
        try:
            custom_id = self.get_player_by_card(card_id)[0]
            self.db_op.update_custom_value(custom_id, "session_start_time", session_start_time)
            logger.info(f"Session started for card {card_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating session start: {e}")
            return False

    def check_session_remaining(self, card_id: str):
        """Get remaining session time (seconds)"""
        try:
            player = self.get_player_by_card(card_id)
            if not player:
                return None

            time_left = player[4]  # Index varies, check db_operation.py
            return float(time_left) if time_left else 0.0
        except Exception as e:
            logger.error(f"Error checking session: {e}")
            return None

    # ===== LEADERBOARD =====
    def get_leaderboard(self, level: str = None, limit: int = 10):
        """Top scores. If level given, filter to that level."""
        try:
            with self._scores_lock:
                con = self._scores_conn()
                con.row_factory = sqlite3.Row
                if level is not None:
                    rows = con.execute(
                        "SELECT card_id, level, score, life, lives_start, result, time_used, ts "
                        "FROM hex_scores WHERE level=? "
                        "ORDER BY score DESC, time_used ASC LIMIT ?",
                        (str(level), limit),
                    ).fetchall()
                else:
                    rows = con.execute(
                        "SELECT card_id, level, score, life, lives_start, result, time_used, ts "
                        "FROM hex_scores ORDER BY score DESC, time_used ASC LIMIT ?",
                        (limit,),
                    ).fetchall()
                con.close()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

    def get_scores_since(self, since: str):
        """Return scores recorded after `since` timestamp. Used by RFID poller."""
        try:
            with self._scores_lock:
                con = self._scores_conn()
                rows = con.execute(
                    "SELECT card_id, level, score, score2, life, result, time_used, ts, game "
                    "FROM hex_scores WHERE ts > ? ORDER BY ts ASC",
                    (since,),
                ).fetchall()
                con.close()
            return [dict(zip(
                ["card_id", "level", "score", "score2", "life", "result", "time_used", "ts", "game"], r
            )) for r in rows]
        except Exception as e:
            logger.error(f"Error getting scores since {since}: {e}")
            return []

    def close(self):
        """Close database connection"""
        if not self.db_op:
            return
        try:
            self.db_op.close_db()
            logger.info("Database closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")

# Global instance
_db = None

def get_db() -> Database:
    """Get database singleton"""
    global _db
    if _db is None:
        _db = Database()
    return _db

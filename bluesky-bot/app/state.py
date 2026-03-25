"""
SQLite-backed state store. One row per posted event.
DB file path defaults to /data/state.db (override with STATE_DB env var).
"""
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.environ.get("STATE_DB", "/data/state.db")


@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS posted (
            season      INTEGER NOT NULL,
            event_type  TEXT    NOT NULL,
            game_id     TEXT    NOT NULL,
            player_id   TEXT    NOT NULL,
            PRIMARY KEY (season, event_type, game_id, player_id)
        )
    """)
    try:
        yield con
        con.commit()
    finally:
        con.close()


def already_posted(season: int, event_type: str, game_id: str, player_id: str) -> bool:
    with _conn() as con:
        row = con.execute(
            "SELECT 1 FROM posted WHERE season=? AND event_type=? AND game_id=? AND player_id=?",
            (season, event_type, game_id, player_id),
        ).fetchone()
        return row is not None


def mark_posted(season: int, event_type: str, game_id: str, player_id: str) -> None:
    with _conn() as con:
        con.execute(
            "INSERT OR IGNORE INTO posted (season, event_type, game_id, player_id) VALUES (?,?,?,?)",
            (season, event_type, game_id, player_id),
        )

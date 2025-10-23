import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.abspath(os.path.join(DB_DIR, "cab.db"))

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS cab_details (
    cab_model_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    cab_model_name TEXT NOT NULL,
    cab_reg_name   TEXT NOT NULL,
    current_lat    REAL,
    current_lan    REAL,
    is_deleted     INTEGER NOT NULL DEFAULT 0,
    created_date   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_date   TEXT
);
"""


def _ensure_db() -> None:
    os.makedirs(DB_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(SCHEMA_SQL)
        conn.commit()


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    """Yields a SQLite connection with Row factory for dict-like access."""
    _ensure_db()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

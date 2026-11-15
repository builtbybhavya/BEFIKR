"""Small SQLite persistence layer for local development and demos."""

import os
import sqlite3
from pathlib import Path

DATA_PATH = Path(os.getenv("BEFIKR_DATA_DIR", Path(__file__).resolve().parents[1] / "data"))
DB_PATH = DATA_PATH / "befikr.db"

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS auth_sessions (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 created_at TEXT NOT NULL, expires_at TEXT NOT NULL, revoked_at TEXT
);
CREATE TABLE IF NOT EXISTS user_preferences (
 owner_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 analytics_opt_in INTEGER NOT NULL DEFAULT 0, push_opt_in INTEGER NOT NULL DEFAULT 0,
 updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS consent_events (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 purpose TEXT NOT NULL, granted INTEGER NOT NULL, scope TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS contacts (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 name TEXT NOT NULL, phone TEXT NOT NULL, relationship TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reports (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 category TEXT NOT NULL, description TEXT NOT NULL, latitude REAL, longitude REAL,
 occurred_at TEXT, status TEXT NOT NULL DEFAULT 'pending_review', internal_reason TEXT,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_reports_status_created ON reports(status, created_at);
CREATE INDEX IF NOT EXISTS ix_reports_location ON reports(latitude, longitude, status);
CREATE TABLE IF NOT EXISTS report_evidence (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 report_id TEXT REFERENCES reports(id) ON DELETE CASCADE,
 filename TEXT NOT NULL, mime_type TEXT NOT NULL, size_bytes INTEGER NOT NULL,
 created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_report_evidence_report ON report_evidence(report_id);
CREATE TABLE IF NOT EXISTS report_history (
 id TEXT PRIMARY KEY, report_id TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
 actor_id TEXT REFERENCES users(id) ON DELETE SET NULL, old_status TEXT, new_status TEXT NOT NULL,
 reason TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS appeals (
 id TEXT PRIMARY KEY, report_id TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
 owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, message TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sos_events (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 status TEXT NOT NULL, delivery_state TEXT NOT NULL, latitude REAL, longitude REAL,
 created_at TEXT NOT NULL, cancelled_at TEXT
);
CREATE TABLE IF NOT EXISTS tracking_sessions (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 recipient_ids TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL, destination TEXT,
 last_latitude REAL, last_longitude REAL, location_at TEXT, created_at TEXT NOT NULL, expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS journeys (
 id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 interval_minutes INTEGER NOT NULL, grace_minutes INTEGER NOT NULL, status TEXT NOT NULL,
 destination TEXT, next_due_at TEXT NOT NULL, created_at TEXT NOT NULL, completed_at TEXT,
 duration_minutes INTEGER NOT NULL DEFAULT 120, total_checkins INTEGER NOT NULL DEFAULT 1,
 risk_score REAL NOT NULL DEFAULT 50, started_at TEXT
);
CREATE TABLE IF NOT EXISTS checkin_events (
 id TEXT PRIMARY KEY, journey_id TEXT NOT NULL REFERENCES journeys(id) ON DELETE CASCADE,
 response TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS places (
 id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL, address TEXT NOT NULL,
 latitude REAL NOT NULL, longitude REAL NOT NULL, phone TEXT NOT NULL DEFAULT '',
 source TEXT NOT NULL, source_url TEXT NOT NULL DEFAULT '', verified_at TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1,
 created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS place_candidates (
 id TEXT PRIMARY KEY, candidate_key TEXT NOT NULL UNIQUE, name TEXT NOT NULL, category TEXT NOT NULL,
 address TEXT NOT NULL, latitude REAL NOT NULL, longitude REAL NOT NULL, phone TEXT NOT NULL DEFAULT '',
 source_url TEXT NOT NULL, source_date TEXT, dataset_id TEXT, status TEXT NOT NULL DEFAULT 'pending',
 review_notes TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, reviewed_at TEXT,
 reviewed_by TEXT REFERENCES users(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS ix_place_candidates_status_created ON place_candidates(status, created_at);
CREATE TABLE IF NOT EXISTS audit_logs (
 id TEXT PRIMARY KEY, actor_id TEXT REFERENCES users(id) ON DELETE SET NULL,
 action TEXT NOT NULL, target_type TEXT NOT NULL, target_id TEXT NOT NULL,
 detail TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL
);
"""


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc, tb):
        try:
            return super().__exit__(exc_type, exc, tb)
        finally:
            self.close()


def connect() -> sqlite3.Connection:
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH, timeout=10, factory=ClosingConnection)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def initialize() -> None:
    with connect() as connection:
        connection.executescript(SCHEMA)
        report_columns = {row[1] for row in connection.execute("PRAGMA table_info(reports)")}
        for name in ("location_label", "location_place_id"):
            if name not in report_columns:
                connection.execute(f"ALTER TABLE reports ADD COLUMN {name} TEXT")
        connection.execute("UPDATE places SET category='public_space' WHERE category='public_place'")
        place_columns = {row[1] for row in connection.execute("PRAGMA table_info(places)")}
        if "source_url" not in place_columns:
            connection.execute("ALTER TABLE places ADD COLUMN source_url TEXT NOT NULL DEFAULT ''")
        existing = {row[1] for row in connection.execute("PRAGMA table_info(journeys)")}
        for name, definition in (
            ("duration_minutes", "INTEGER NOT NULL DEFAULT 120"),
            ("total_checkins", "INTEGER NOT NULL DEFAULT 1"),
            ("risk_score", "REAL NOT NULL DEFAULT 50"),
            ("started_at", "TEXT"),
        ):
            if name not in existing:
                connection.execute(f"ALTER TABLE journeys ADD COLUMN {name} {definition}")

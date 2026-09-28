"""Registro SQLite de trabajos; no almacena logs, reportes ni credenciales."""

from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path
import os
import sqlite3
import uuid


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def default_db_path():
    configured = Path(os.getenv("ANALYSIS_DB_PATH", ".local-state/analysis.sqlite3"))
    return configured if configured.is_absolute() else Path(__file__).resolve().parents[2] / configured


class JobStore:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else default_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL CHECK(kind IN ('manual', 'periodic')),
                    idempotency_key TEXT UNIQUE,
                    status TEXT NOT NULL CHECK(status IN ('queued', 'running', 'succeeded', 'failed', 'interrupted')),
                    phase TEXT NOT NULL,
                    requested_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT,
                    last_ingested_at TEXT,
                    last_analyzed_at TEXT,
                    report_id TEXT,
                    error_code TEXT
                );
                CREATE UNIQUE INDEX IF NOT EXISTS one_active_job ON jobs((1))
                    WHERE status IN ('queued', 'running');
                CREATE TABLE IF NOT EXISTS deliveries (
                    job_id TEXT NOT NULL REFERENCES jobs(id),
                    destination TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('attempting', 'sent', 'failed', 'unknown')),
                    attempted_at TEXT NOT NULL,
                    PRIMARY KEY(job_id, destination)
                );
                CREATE TABLE IF NOT EXISTS worker (
                    singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                    instance_id TEXT NOT NULL,
                    heartbeat_at TEXT NOT NULL
                );
            """)

    @contextmanager
    def _connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=5000")
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _job(row):
        return dict(row) if row is not None else None

    def get(self, job_id):
        with self._connect() as db:
            return self._job(db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone())

    def latest(self):
        with self._connect() as db:
            return self._job(db.execute("SELECT * FROM jobs ORDER BY requested_at DESC, rowid DESC LIMIT 1").fetchone())

    def enqueue(self, kind, key=None):
        if kind not in {"manual", "periodic"}:
            raise ValueError("kind inválido")
        if key is not None and (not isinstance(key, str) or not 1 <= len(key) <= 80
                                or not key.isascii() or not all(c.isalnum() or c in "-_" for c in key)):
            raise ValueError("clave de idempotencia inválida")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if key:
                previous = db.execute("SELECT * FROM jobs WHERE idempotency_key = ?", (key,)).fetchone()
                if previous:
                    return self._job(previous), "duplicate"
            active = db.execute("SELECT * FROM jobs WHERE status IN ('queued', 'running')").fetchone()
            if active:
                return self._job(active), "busy"
            job_id = uuid.uuid4().hex
            db.execute("INSERT INTO jobs(id, kind, idempotency_key, status, phase, requested_at) "
                       "VALUES (?, ?, ?, 'queued', 'waiting', ?)", (job_id, kind, key, utc_now()))
            return self._job(db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()), "created"

    def claim(self):
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE status = 'queued' ORDER BY requested_at LIMIT 1").fetchone()
            if row is None:
                return None
            db.execute("UPDATE jobs SET status = 'running', phase = 'ingesting', started_at = ? WHERE id = ?",
                       (utc_now(), row["id"]))
            return self._job(db.execute("SELECT * FROM jobs WHERE id = ?", (row["id"],)).fetchone())

    def phase(self, job_id, phase, **fields):
        allowed = {"last_ingested_at", "last_analyzed_at", "report_id"}
        if set(fields) - allowed:
            raise ValueError("campo de trabajo inválido")
        assignments = ["phase = ?"] + [f"{field} = ?" for field in fields]
        with self._connect() as db:
            db.execute(f"UPDATE jobs SET {', '.join(assignments)} WHERE id = ? AND status = 'running'",
                       (phase, *fields.values(), job_id))

    def finish(self, job_id, status, error_code=None, report_id=None):
        if status not in {"succeeded", "failed", "interrupted"}:
            raise ValueError("estado final inválido")
        with self._connect() as db:
            db.execute("UPDATE jobs SET status = ?, phase = 'finished', finished_at = ?, "
                       "error_code = ?, report_id = COALESCE(?, report_id) WHERE id = ? AND status = 'running'",
                       (status, utc_now(), error_code, report_id, job_id))

    def recover(self):
        with self._connect() as db:
            db.execute("UPDATE jobs SET status = 'interrupted', phase = 'finished', finished_at = ?, "
                       "error_code = 'worker_interrupted' WHERE status = 'running'", (utc_now(),))
            db.execute("UPDATE deliveries SET status = 'unknown' WHERE status = 'attempting'")

    def heartbeat(self, instance_id):
        with self._connect() as db:
            db.execute("INSERT INTO worker(singleton, instance_id, heartbeat_at) VALUES (1, ?, ?) "
                       "ON CONFLICT(singleton) DO UPDATE SET instance_id = excluded.instance_id, "
                       "heartbeat_at = excluded.heartbeat_at", (instance_id, utc_now()))

    def worker(self):
        with self._connect() as db:
            row = db.execute("SELECT instance_id, heartbeat_at FROM worker WHERE singleton = 1").fetchone()
            return dict(row) if row else None

    def delivery(self, job_id, destination, status=None):
        with self._connect() as db:
            if status is None:
                row = db.execute("SELECT * FROM deliveries WHERE job_id = ? AND destination = ?",
                                 (job_id, destination)).fetchone()
                return dict(row) if row else None
            if status == "attempting":
                db.execute("INSERT OR IGNORE INTO deliveries VALUES (?, ?, ?, ?)",
                           (job_id, destination, status, utc_now()))
            else:
                db.execute("UPDATE deliveries SET status = ? WHERE job_id = ? AND destination = ?",
                           (status, job_id, destination))
            row = db.execute("SELECT * FROM deliveries WHERE job_id = ? AND destination = ?",
                             (job_id, destination)).fetchone()
            return dict(row) if row else None

    def deliveries(self, job_id):
        with self._connect() as db:
            return {row["destination"]: row["status"] for row in db.execute(
                "SELECT destination, status FROM deliveries WHERE job_id = ?", (job_id,))}

    def reconcile_attempts(self, job_id):
        with self._connect() as db:
            db.execute("UPDATE deliveries SET status = 'unknown' "
                       "WHERE job_id = ? AND status = 'attempting'", (job_id,))

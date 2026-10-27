"""Explicit bounded log following inside Flask. No model, jobs or notifications.

Construction and status reads never start a thread or contact Docker. An owned
daemon thread starts only through start(); it owns the cycle lease for the whole
session (including pause), and never resumes automatically after a process exit.
"""
import atexit
from contextlib import ExitStack, closing
from datetime import datetime, timedelta, timezone
import json
import os
import re
import sqlite3
import threading
import time
import uuid

from dashboard.services.puerto_umbral_capture import (
    STATE, MODES, MAX_BYTES, _root_safe, capture_access_log, source_status,
)
from dashboard.services.read_store import atomic_write_text, capture_file
from dashboard.services.runtime_lock import AlreadyRunning, exclusive_lock, lock_is_held

CURRENT = STATE / "following" / "current.json"
LEASE = STATE / ".follow.lock"
ACTIVE = {"following", "paused", "pausing", "stopping"}
STATES = ACTIVE | {"stopped", "completed", "error", "interrupted"}


class FollowError(ValueError):
    """Fixed codes only; never expose contents, exception text or CLI stderr."""


def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read():
    _root_safe(CURRENT)
    record = capture_file(CURRENT)
    if record.status == "missing":
        return {"schema_version": 1, "status": "stopped", "session_id": None}
    if record.status != "available" or record.size > 65536:
        raise FollowError("invalid_follow_state")
    data = json.loads(record.text)
    if (not isinstance(data, dict) or data.get("schema_version") != 1
            or data.get("status") not in STATES
            or not isinstance(data.get("session_id"), str)
            or not re.fullmatch(r"[a-f0-9]{32}", data["session_id"])):
        raise FollowError("invalid_follow_state")
    return data


def _snapshot():
    """Last locally verified generation, not an observation of current Docker health."""
    metadata = source_status()
    identifier = metadata.get("snapshot_id")
    if (not identifier or metadata.get("status") in {"changing", "mode_mismatch"}
            or metadata.get("snapshot_mode") != os.getenv("PUERTO_UMBRAL_MODE", "vulnerable")):
        return None
    path = STATE / "snapshots" / identifier / "access.log"
    _root_safe(path)
    content = capture_file(path)
    if content.status != "available" or content.size > MAX_BYTES or content.digest != metadata.get("sha256"):
        return None
    return {"snapshot_id": identifier, "sha256": content.digest,
            "gateway": metadata.get("gateway"), "mode": metadata.get("snapshot_mode"),
            "lines": content.text.splitlines(), "line_count": metadata.get("line_count"),
            "scope": metadata.get("scope")}


def _transition(before, after):
    if before is None:
        return "baseline", None
    if before["mode"] != after["mode"] or before["gateway"] != after["gateway"]:
        return "source_changed", None
    if before["sha256"] == after["sha256"]:
        return "unchanged", 0
    old, new = before["lines"], after["lines"]
    for count in range(min(len(old), len(new)), 0, -1):
        if old[-count:] == new[:count]:
            return ("appended" if count == len(old) else "window_shift"), len(new) - count
    # A bounded tail cannot prove which of rotation, truncation or missed events
    # caused a discontinuity. Do not invent an event offset or a complete history.
    return "discontinuity", None


class LogFollower:
    def __init__(self):
        self._lock = threading.RLock()
        self._commands = threading.Lock()
        self._thread = None
        self._leased = False
        self._stop = threading.Event()
        self._pause = threading.Event()
        self._wake = threading.Event()
        self._idle = threading.Event()
        self._idle.set()
        self._deadline = 0
        self._state = None
        atexit.register(self.close)

    def status(self):
        with self._lock:
            try:
                owned = bool(self._leased and self._thread and self._thread.is_alive())
                data = dict(self._state) if owned else _read()
                _root_safe(LEASE)
                held = True if owned else lock_is_held(LEASE)
                if data["status"] in ACTIVE and not held:
                    data.update(status="interrupted", error_code="process_interrupted")
                if held is None:
                    data.update(status="error", error_code="follow_lock_unknown")
                return {**data, "owned_here": owned, "session_active": held is not False,
                        "analysis_requested": False, "notifications_requested": False}
            except (OSError, ValueError, TypeError, KeyError):
                return {"schema_version": 1, "status": "error", "session_id": None,
                        "error_code": "invalid_follow_state", "owned_here": False,
                        "session_active": True, "analysis_requested": False,
                        "notifications_requested": False}

    def _write(self, **updates):
        with self._lock:
            self._state.update(updates, updated_at=_now())
            _root_safe(CURRENT)
            atomic_write_text(CURRENT, json.dumps(self._state, ensure_ascii=False, indent=2))

    def _archive(self, data):
        identifier = data.get("session_id")
        if identifier and re.fullmatch(r"[a-f0-9]{32}", identifier):
            target = STATE / "following" / "sessions" / (identifier + ".json")
            _root_safe(target)
            atomic_write_text(target, json.dumps(data, ensure_ascii=False, indent=2))

    def start(self, *, mode, db_path, interval_seconds=5, duration_seconds=1800):
        if (mode not in MODES or db_path != STATE / "analysis.sqlite3"
                or type(interval_seconds) is not int or not 5 <= interval_seconds <= 60
                or type(duration_seconds) is not int or not 60 <= duration_seconds <= 1800):
            raise FollowError("invalid_follow_options")
        with self._commands, self._lock:
            if self._thread and self._thread.is_alive():
                raise FollowError("follow_active")
            for path in (CURRENT, LEASE, db_path, db_path.with_suffix(".cycle.lock"),
                         db_path.with_suffix(".engine.lock"), db_path.with_suffix(".worker.lock")):
                _root_safe(path)
            leases = ExitStack()
            try:
                leases.enter_context(exclusive_lock(LEASE))
                leases.enter_context(exclusive_lock(db_path.with_suffix(".cycle.lock")))
                leases.enter_context(exclusive_lock(db_path.with_suffix(".engine.lock")))
                if lock_is_held(db_path.with_suffix(".worker.lock")) is not False:
                    raise FollowError("executor_active_or_unknown")
                if db_path.exists():
                    with closing(sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True, timeout=1)) as db:
                        db.execute("PRAGMA query_only=ON")
                        if db.execute("SELECT count(*) FROM jobs WHERE status IN ('queued','running')").fetchone()[0]:
                            raise FollowError("analysis_pending")
                previous = _read()
                if previous.get("session_id"):
                    if previous["status"] in ACTIVE:
                        previous.update(status="interrupted", error_code="process_interrupted", finished_at=_now())
                    self._archive(previous)
                self._stop.clear()
                self._pause.clear()
                self._wake.clear()
                self._idle.set()
                self._deadline = time.monotonic() + duration_seconds
                self._state = {"schema_version": 1, "session_id": uuid.uuid4().hex,
                               "mode": mode, "status": "following", "owner_pid": os.getpid(),
                               "started_at": _now(), "finished_at": None,
                               "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)).isoformat().replace("+00:00", "Z"),
                               "interval_seconds": interval_seconds, "duration_seconds": duration_seconds,
                               "cycles": 0, "snapshots_published": 0, "unchanged_cycles": 0,
                               "last_cycle_at": None, "last_success_at": None, "last_cycle_seconds": None,
                               "last_event": None, "new_observed_lines": None, "in_flight": False,
                               "checkpoint": None, "error_code": None}
                self._write()
                self._thread = threading.Thread(target=self._run, args=(leases,),
                                                name="puerto-umbral-log-follow", daemon=True)
                self._leased = True
                self._thread.start()
            except AlreadyRunning:
                leases.close()
                self._leased = False
                raise FollowError("follow_or_cycle_busy") from None
            except (OSError, ValueError, RuntimeError, sqlite3.Error):
                leases.close()
                self._leased = False
                raise
            return self.status()

    def control(self, action):
        if action not in {"pause", "resume", "stop"}:
            raise FollowError("invalid_follow_action")
        with self._commands:
            with self._lock:
                if not self._leased or not self._thread or not self._thread.is_alive():
                    state = self.status()
                    if state["session_active"]:
                        raise FollowError("follow_owned_elsewhere")
                    return state
                if action == "resume":
                    if self._state["status"] != "paused" or time.monotonic() >= self._deadline:
                        raise FollowError("follow_not_paused")
                    self._pause.clear()
                    self._write(status="following")
                    self._wake.set()
                    return self.status()
                if action == "pause":
                    self._pause.set()
                    self._write(status="pausing")
                else:
                    self._stop.set()
                    self._write(status="stopping")
                self._wake.set()
                thread = self._thread
            if action == "stop":
                thread.join(timeout=5)
            else:
                self._idle.wait(timeout=5)
                with self._lock:
                    if (thread.is_alive() and self._idle.is_set() and not self._stop.is_set()
                            and self._state["status"] in {"following", "pausing", "paused"}
                            and time.monotonic() < self._deadline):
                        self._write(status="paused")
            return self.status()  # pausing/stopping explicitly means not yet acknowledged.

    def _cancelled(self):
        return self._stop.is_set() or self._pause.is_set() or time.monotonic() >= self._deadline

    def _run(self, leases):
        terminal, failure = "stopped", None
        try:
            while not self._stop.is_set():
                if time.monotonic() >= self._deadline:
                    terminal = "completed"
                    break
                with self._lock:
                    if self._stop.is_set():
                        break
                    self._wake.clear()
                    if self._pause.is_set():
                        self._write(status="paused", in_flight=False)
                        paused = True
                    else:
                        self._idle.clear()
                        self._write(status="following", in_flight=True, last_cycle_at=_now())
                        paused = False
                if paused:
                    self._wake.wait(timeout=min(1, max(0, self._deadline - time.monotonic())))
                    continue
                started = time.monotonic()
                before = _snapshot()
                result = capture_access_log(mode=self._state["mode"], reuse_unchanged=True,
                                            require_running=True, cancelled=self._cancelled)
                if result is None:
                    if self._cancelled():
                        self._write(in_flight=False)
                        self._idle.set()
                        continue
                    terminal, failure = "error", source_status().get("error_code") or "capture_failed"
                    break
                after = _snapshot()
                if after is None or after["snapshot_id"] != result.snapshot_id:
                    terminal, failure = "error", "capture_checkpoint_mismatch"
                    break
                event, new_lines = _transition(before, after)
                checkpoint = {key: value for key, value in after.items() if key != "lines"}
                self._write(cycles=self._state["cycles"] + 1,
                            snapshots_published=self._state["snapshots_published"] + int(before is None or before["snapshot_id"] != result.snapshot_id),
                            unchanged_cycles=self._state["unchanged_cycles"] + int(event == "unchanged"),
                            last_success_at=_now(), last_cycle_seconds=round(time.monotonic() - started, 3),
                            last_event=event, new_observed_lines=new_lines, checkpoint=checkpoint,
                            error_code=None, in_flight=False)
                self._idle.set()
                self._wake.wait(timeout=min(self._state["interval_seconds"], max(0, self._deadline - time.monotonic())))
        except Exception:
            terminal, failure = "error", "follow_cycle_failed"
        finally:
            with self._lock:
                try:
                    self._write(status=terminal, error_code=failure, finished_at=_now(), in_flight=False)
                    self._archive(self._state)
                except (OSError, ValueError):
                    # A free lease plus an unfinished persisted state is reported
                    # as interrupted, never as an acknowledged successful stop.
                    self._state.update(status="error", error_code="follow_state_write_failed", in_flight=False)
                finally:
                    leases.close()
                    self._leased = False
                    self._idle.set()

    def close(self):
        try:
            self.control("stop")
        except (OSError, ValueError, RuntimeError):
            self._stop.set()
            self._wake.set()


_instance = None
_instance_lock = threading.Lock()


def follower():
    global _instance
    with _instance_lock:
        if _instance is None:
            _instance = LogFollower()
        return _instance

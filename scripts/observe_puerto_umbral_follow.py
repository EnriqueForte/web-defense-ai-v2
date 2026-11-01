"""Observe one owner-started follow session. GET only; never starts/stops services.

No application imports, dotenv, Docker, provider, scenario or control POST.
Creates one new receipt; existing logs, snapshots and SQLite remain untouched.
"""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import sqlite3
import time
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / ".local-state/puerto-umbral"
URL = "http://127.0.0.1:3000/api/v1/fuentes/log"
SAMPLES = 20
DEADLINE_SECONDS = 180


class ObservationError(ValueError):
    """Fixed diagnostic codes, never response or database contents."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def now():
    return datetime.now(timezone.utc)


def safe(path):
    path = Path(path).absolute()
    if not path.is_relative_to(ROOT):
        raise ObservationError("path_outside_project")
    for candidate in (path, *path.parents):
        if candidate.is_symlink() or (candidate.exists() and getattr(candidate.lstat(), "st_file_attributes", 0) & 1024):
            raise ObservationError("linked_path_rejected")
        if candidate == ROOT:
            return path
    raise ObservationError("path_outside_project")


def database_state():
    path = safe(STATE / "analysis.sqlite3")
    if not path.is_file():
        raise ObservationError("database_absent")
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=1)) as db:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        result = {}
        for table, columns, order in (
            ("jobs", "id, status, phase, requested_at, started_at, finished_at", "id"),
            ("deliveries", "job_id, status, attempted_at", "job_id, status, attempted_at"),
        ):
            # Identifiers are fixed in this whitelist; no user-supplied SQL.
            rows = db.execute(f"SELECT {columns} FROM {table} ORDER BY {order} LIMIT 10001").fetchall()
            if len(rows) > 10000:
                raise ObservationError("database_review_limit")
            result[table] = {"count": len(rows), "sha256": hashlib.sha256(json.dumps(rows).encode()).hexdigest()}
        return result


def snapshot_ids():
    directory = safe(STATE / "snapshots")
    if not directory.is_dir():
        return set()
    identifiers = set()
    for index, child in enumerate(directory.iterdir()):
        if index >= 10000:
            raise ObservationError("snapshot_review_limit")
        safe(child)
        if child.is_dir() and re.fullmatch(r"[a-f0-9]{32}", child.name):
            identifiers.add(child.name)
        if len(identifiers) > 10000:
            raise ObservationError("snapshot_review_limit")
    return identifiers


def read_source(opener):
    with opener.open(URL, timeout=2) as response:
        raw = response.read(65537)
        if response.status != 200 or len(raw) > 65536:
            raise ObservationError("invalid_source_response")
    body = json.loads(raw)
    if not isinstance(body, dict) or body.get("meta", {}).get("api_version") != "1":
        raise ObservationError("invalid_api_contract")
    data = body.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("following"), dict):
        raise ObservationError("follow_not_available")
    return data


def timestamp(value):
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ObservationError("timestamp_without_timezone")
    return value


def observe():
    opener = build_opener(ProxyHandler({}), NoRedirect())
    report = {"schema": "puerto-umbral.follow-observation.v1", "started_at": now().isoformat(),
              "status": "incomplete", "samples": [], "maximum_get_requests": 181,
              "get_requests": 0, "control_requests": 0, "model_requested": False,
              "browser_paint_measured": False, "criterion_acceptance": "owner_review_required", "hardware": {
                  "system": platform.system(), "release": platform.release(),
                  "machine": platform.machine(), "logical_cpus": os.cpu_count(),
                  "load_average_before": list(os.getloadavg()) if hasattr(os, "getloadavg") else None,
              }}

    def read():
        if report["get_requests"] >= 181:
            raise ObservationError("get_request_limit")
        report["get_requests"] += 1
        return read_source(opener)

    try:
        initial = read()["following"]
        if initial.get("enabled") is not True or initial.get("session_active") is not False:
            raise ObservationError("follow_disabled_or_already_active")
        old_session = initial.get("session_id")
        report["database_before"] = database_state()
        before_ids = snapshot_ids()
        report["snapshot_count_before"] = len(before_ids)
        print("Observador preparado. Inicia en Actividad: 5 segundos / 5 minutos.", flush=True)
        deadline = time.monotonic() + DEADLINE_SECONDS
        session, last_cycle = None, 0
        while len(report["samples"]) < SAMPLES and time.monotonic() < deadline:
            data = read()
            state = data["following"]
            identifier = state.get("session_id")
            if identifier == old_session:
                time.sleep(1)
                continue
            if not isinstance(identifier, str) or not re.fullmatch(r"[a-f0-9]{32}", identifier):
                raise ObservationError("invalid_new_session")
            if session is None:
                session = identifier
                report["session_id"] = session
            if identifier != session:
                raise ObservationError("session_changed")
            if (state.get("status") != "following" or state.get("session_active") is not True
                    or state.get("mode") != "corrected" or state.get("interval_seconds") != 5
                    or state.get("duration_seconds") != 300 or state.get("error_code")):
                raise ObservationError("unexpected_session_state_or_options")
            if state.get("analysis_requested") is not False or state.get("notifications_requested") is not False:
                raise ObservationError("unexpected_operation_flags")
            cycle = state.get("cycles")
            if type(cycle) is not int or cycle < last_cycle:
                raise ObservationError("invalid_cycle_sequence")
            checkpoint = state.get("checkpoint") or {}
            if (cycle > last_cycle and state.get("in_flight") is False
                    and data.get("status") in {"available", "stale"}
                    and data.get("snapshot_id") == checkpoint.get("snapshot_id")
                    and data.get("sha256") == checkpoint.get("sha256") and checkpoint.get("snapshot_id")):
                observed = now()
                started, finished = timestamp(state["last_cycle_at"]), timestamp(state["last_success_at"])
                latency, capture = (observed - started).total_seconds(), state.get("last_cycle_seconds")
                if (not started <= finished <= observed or type(capture) not in (int, float)
                        or not math.isfinite(capture) or capture < 0):
                    raise ObservationError("invalid_clock_or_duration")
                sample = {"cycle": cycle, "cycle_started_at": started.isoformat(),
                          "cycle_finished_at": finished.isoformat(), "observed_at": observed.isoformat(),
                          "capture_seconds": capture, "api_visibility_upper_bound_seconds": round(latency, 3),
                          "snapshot_id": checkpoint["snapshot_id"], "sha256": checkpoint["sha256"],
                          "snapshots_published": state.get("snapshots_published"),
                          "unchanged_cycles": state.get("unchanged_cycles")}
                report["samples"].append(sample)
                last_cycle = cycle
                print(f"Muestra {len(report['samples']):02d}/20: ciclo {cycle}, lectura {capture:.3f}s, visible API <= {latency:.3f}s", flush=True)
            if len(report["samples"]) < SAMPLES:
                time.sleep(1)
        report["database_after"] = database_state()
        after_ids = snapshot_ids()
        report["snapshot_count_after"] = len(after_ids)
        report["new_snapshot_ids"] = sorted(after_ids - before_ids)
        report["database_unchanged"] = report["database_before"] == report["database_after"]
        report["single_checkpoint_observed"] = len({(s["snapshot_id"], s["sha256"]) for s in report["samples"]}) == 1
        report["status"] = "observed_20_cycles" if len(report["samples"]) == SAMPLES else "incomplete"
        report["all_observed_api_bounds_within_10_seconds"] = (
            len(report["samples"]) == SAMPLES and all(s["api_visibility_upper_bound_seconds"] <= 10 for s in report["samples"]))
    except (Exception, KeyboardInterrupt) as error:
        report["error_code"] = str(error) if isinstance(error, ObservationError) else type(error).__name__
    report["finished_at"] = now().isoformat()
    report["hardware"]["load_average_after"] = list(os.getloadavg()) if hasattr(os, "getloadavg") else None
    destination = safe(STATE / "operational-review")
    destination.mkdir(parents=True, exist_ok=True)
    receipt = safe(destination / ("follow-" + uuid4().hex + ".json"))
    with receipt.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({key: report.get(key) for key in (
        "status", "error_code", "session_id", "get_requests", "database_unchanged",
        "single_checkpoint_observed", "all_observed_api_bounds_within_10_seconds")}))
    print("Recibo nuevo:", receipt.relative_to(ROOT))
    print("Medición de disponibilidad por API; no mide el render del navegador ni acepta la fase automáticamente.")
    print("Si iniciaste la sesión, detenla desde Actividad y consulta su estado.")
    return 0 if report["status"] == "observed_20_cycles" else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observe", action="store_true", help="Observar una nueva sesión iniciada por el propietario; solo GET y un recibo nuevo")
    args = parser.parse_args(argv)
    if not args.observe:
        parser.print_help()
        return 0
    return observe()


if __name__ == "__main__":
    raise SystemExit(main())

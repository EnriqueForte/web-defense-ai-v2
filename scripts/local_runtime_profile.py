"""Plan or explicitly start one local component; never loads/prints dotenv or secrets."""
import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.backup_operational import PROFILES, checked_path
from scripts.check_environment import read_pins, compare
from dashboard.services.structured_publication import load_current
from agents.evidence_contracts import ContractError


def build_plan(root, profile="pilot", mode="legacy", *, python=None, enable_manual=False):
    if profile not in PROFILES or mode not in {"legacy", "structured"}:
        raise ValueError("invalid_local_profile")
    root = Path(root).absolute()
    definition = PROFILES[profile]
    paths = {name: checked_path(root, definition[name]) for name in ("log", "reports", "db")}
    interpreter = str(Path(python or sys.executable).absolute())
    environment = {"PYTHONIOENCODING": "utf-8", "ANALYSIS_ENGINE_MODE": mode,
                   "LOG_PATH": str(paths["log"]), "REPORT_PATH": str(paths["reports"]),
                   "ANALYSIS_DB_PATH": str(paths["db"]),
                   "LOG_SYNC_SOURCE": "dvwa-lab" if profile == "pilot" else "legacy-docker",
                   "ANALYSIS_MANUAL_ENABLED": "1" if enable_manual else "0", "NOTIFICATION_DESTINATIONS": ""}
    return {"profile": profile, "mode": mode, "cwd": str(root), "environment_overrides": environment,
            "commands": {"flask": [interpreter, "-B", "-m", "flask", "--app", "dashboard.app", "run",
                                     "--host", "127.0.0.1", "--port", "5000", "--no-debugger"],
                         "worker": [interpreter, "-B", str(root / "pipeline.py"), "--manual-only"]}}


def existing_lock_status(path):
    """Probe existing lock without creating a file or modifying its contents."""
    path = Path(path)
    if not path.exists():
        return "absent"
    try:
        with path.open("r+b") as handle:
            if path.stat().st_size == 0:
                return "unknown"
            if os.name == "nt":
                import msvcrt
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError:
                    return "held"
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    return "held"
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return "free"
    except OSError:
        return "unknown"


def active_jobs(path):
    if not path.exists():
        return {"status": "absent", "queued": 0, "running": 0}
    try:
        with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=1)) as db:
            db.execute("PRAGMA query_only=ON")
            counts = dict(db.execute("SELECT status, count(*) FROM jobs WHERE status IN ('queued','running') GROUP BY status"))
        return {"status": "available", "queued": counts.get("queued", 0), "running": counts.get("running", 0)}
    except sqlite3.Error:
        return {"status": "unavailable", "queued": None, "running": None}


def port_available():
    try:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 5000))
        return True
    except OSError:
        return False


def readiness(root=ROOT, profile="pilot", mode="legacy", *, component="all", pins=None, enable_manual=False):
    if component not in {"all", "flask", "worker"}:
        raise ValueError("invalid_component")
    root = Path(root).absolute()
    plan = build_plan(root, profile, mode, enable_manual=enable_manual)
    if pins is None:
        pins = read_pins(ROOT / "requirements.txt")
        for name, expected in read_pins(ROOT / "constraints-py311.txt").items():
            if name in pins and pins[name] != expected:
                raise ValueError("environment_contract_conflict")
            pins[name] = expected
    differences = compare(pins)
    db = checked_path(root, PROFILES[profile]["db"])
    locks = {name: existing_lock_status(checked_path(root, db.with_suffix(f".{name}.lock").relative_to(root)))
             for name in ("worker", "cycle", "engine")}
    jobs = active_jobs(db)
    report_root = checked_path(root, PROFILES[profile]["reports"])
    source = "legacy" if mode == "legacy" else "structured"
    current = "absent"
    if mode == "legacy":
        path = checked_path(root, Path(PROFILES[profile]["reports"]) / "reporte_seguridad.md")
        current = "available" if path.is_file() else "absent"
    else:
        pointer = checked_path(root, Path(PROFILES[profile]["reports"]) / "structured/current.json")
        if pointer.exists():
            try:
                load_current(report_root / "structured")
                current = "verified"
            except ContractError:
                current = "invalid"
    free_port = port_available() if component in {"all", "flask"} else None
    blockers = []
    if differences:
        blockers.append("environment_differences")
    if any(value in {"held", "unknown"} for value in locks.values()):
        blockers.append("runtime_lock_active_or_unknown")
    if jobs["status"] == "unavailable" or jobs["queued"] or jobs["running"]:
        blockers.append("active_jobs_or_unreadable_store")
    if free_port is False:
        blockers.append("flask_port_in_use")
    if current == "invalid":
        blockers.append("invalid_current_generation")
    return {"ready": not blockers, "plan": plan, "component": component, "blockers": blockers,
            "environment": {"pins": len(pins), "differences": [
                {"package": name, "expected": expected, "installed": installed} for name, expected, installed in differences]},
            "locks": locks, "jobs": jobs, "flask_port_available": free_port,
            "report_source": {"kind": source, "status": current},
            "notes": ["No procesos iniciados por la comprobación; no reserva el estado de forma atómica.",
                      "La fuente estructurada puede faltar hasta el primer análisis válido; no copiar fixtures a reports.",
                      "Notificaciones desactivadas; manual requiere --enable-manual; no se validan credenciales ni Docker."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=tuple(PROFILES), default="pilot")
    parser.add_argument("--mode", choices=("legacy", "structured"), default="legacy")
    parser.add_argument("--component", choices=("all", "flask", "worker"), default="all")
    parser.add_argument("--start", action="store_true", help="explicitly start one component after preflight; requires operational authorization")
    parser.add_argument("--enable-manual", action="store_true", help="admitir solicitudes de análisis; no encola ningún trabajo por sí solo")
    args = parser.parse_args()
    try:
        result = readiness(profile=args.profile, mode=args.mode, component=args.component, enable_manual=args.enable_manual)
        print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
        if not args.start:
            return 0 if result["ready"] else 1
        if args.component == "all":
            print("Selecciona un solo componente para iniciar.", file=sys.stderr)
            return 2
        if not result["ready"]:
            print("Inicio rechazado: resuelve las condiciones indicadas.", file=sys.stderr)
            return 1
        plan = result["plan"]
        return subprocess.run(plan["commands"][args.component], cwd=plan["cwd"],
                              env={**os.environ, **plan["environment_overrides"]}).returncode
    except (OSError, ValueError, ContractError):
        print("Perfil no comprobado: revisa rutas y contrato local; no se inicia nada.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

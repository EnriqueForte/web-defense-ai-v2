"""Ejecutor local único para trabajos manuales y ciclos programados de V2.

Iniciar explícitamente con ``python pipeline.py``. No se arranca desde Flask.
"""

from datetime import datetime, timezone
from pathlib import Path
import os
import subprocess
import sys
import threading
import time
import uuid

from config.settings import INTERVALO_MINUTOS, LOG_PATH, REPORT_PATH
from dashboard.services.analysis_jobs import JobStore, utc_now
from dashboard.services.read_store import atomic_write_text, capture_file, run_atomic_copy
from dashboard.services.runtime_lock import AlreadyRunning, exclusive_lock


ROOT = Path(__file__).resolve().parent


def synchronize_log():
    source = os.getenv("LOG_SYNC_SOURCE", "legacy-docker").strip().lower()
    if source == "dvwa-lab":
        from dashboard.services.dvwa_lab_capture import capture_access_log
        return capture_access_log(Path(LOG_PATH)) is not None
    if source != "legacy-docker":
        return False

    try:
        result = run_atomic_copy(["docker", "cp", "dvwa-app:/var/log/apache2/access.log"],
                                 Path(LOG_PATH), timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def run_engine():
    try:
        result = subprocess.run([sys.executable, str(ROOT / "main.py")], cwd=ROOT,
                                capture_output=True, text=True, encoding="utf-8", timeout=900,
                                env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    except (OSError, subprocess.TimeoutExpired):
        return False
    if result.returncode != 0:
        diagnostics_dir = os.getenv("ENGINE_DIAGNOSTICS_DIR")
        if diagnostics_dir and result.stderr:
            diagnostics = result.stderr
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                diagnostics = diagnostics.replace(api_key, "[REDACTED]")
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            target = Path(diagnostics_dir) / f"engine-failure-{stamp}-{uuid.uuid4().hex[:8]}.log"
            atomic_write_text(target, diagnostics[-30000:])
    return result.returncode == 0


def archive_report(report, job_id):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    target = Path(REPORT_PATH) / "historial" / f"reporte_{stamp}_ciclo{job_id}.md"
    atomic_write_text(target, report)


def send_alerts(store, job_id, report):
    # Conteos de la misma tabla que expone el dashboard; no enviamos líneas del modelo.
    from dashboard.app import parsear_amenazas
    from config.notifications import enviar_email, enviar_telegram

    severities = [item["severidad"].replace("Í", "I") for item in parsear_amenazas(report)]
    critical = severities.count("CRITICA")
    high = severities.count("ALTA")
    if not critical and not high:
        return
    message = (f"web-defense-ai V2: análisis {job_id}; "
               f"{critical} amenazas críticas, {high} altas. Consulta el reporte local.")
    configured = os.getenv("NOTIFICATION_DESTINATIONS")
    allowed = ({"telegram", "email"} if configured is None else
               {item.strip().lower() for item in configured.split(",") if item.strip()})
    senders = (("telegram", lambda: enviar_telegram(message)),
               ("email", lambda: enviar_email("[web-defense-ai V2] Alerta de seguridad", message)))
    for destination, sender in senders:
        if destination not in allowed:
            continue
        if store.delivery(job_id, destination) is not None:
            continue
        store.delivery(job_id, destination, "attempting")
        try:
            delivered = sender()
        except Exception:
            delivered = False
        store.delivery(job_id, destination, "sent" if delivered else "unknown")


def execute_job(store, job, *, sync=synchronize_log, engine=run_engine, notify=send_alerts):
    for _ in range(100):
        try:
            with exclusive_lock(store.path.with_suffix(".cycle.lock")):
                return _execute_job_locked(store, job, sync=sync, engine=engine, notify=notify)
        except AlreadyRunning:
            time.sleep(.2)
    store.finish(job["id"], "failed", "cycle_busy")


def _execute_job_locked(store, job, *, sync, engine, notify):
    job_id = job["id"]
    report_path = Path(REPORT_PATH) / "reporte_seguridad.md"
    try:
        if not sync():
            store.finish(job_id, "failed", "ingestion_failed")
            return
        store.phase(job_id, "analyzing", last_ingested_at=utc_now())
        before = capture_file(report_path)
        if not engine():
            store.finish(job_id, "failed", "analysis_failed")
            return
        after = capture_file(report_path)
        if (after.status != "available" or not after.text or
                after.file_id == before.file_id):
            store.finish(job_id, "failed", "no_new_report")
            return
        store.phase(job_id, "publishing", last_analyzed_at=utc_now(), report_id=after.file_id)
        archive_report(after.text, job_id)
        store.phase(job_id, "notifying")
        notify(store, job_id, after.text)
        store.finish(job_id, "succeeded", report_id=after.file_id)
    except Exception:
        store.reconcile_attempts(job_id)
        store.finish(job_id, "failed", "internal_error")
        raise


def _heartbeat_loop(store, instance_id, stop):
    while not stop.is_set():
        try:
            store.heartbeat(instance_id)
        except Exception:
            pass
        stop.wait(2)


def _run_single_cycle(store):
    job, disposition = store.enqueue("periodic")
    if disposition != "created":
        print(f"No se inicia el ciclo único: {disposition}.", file=sys.stderr)
        return 1
    claimed = store.claim()
    if claimed is None:
        print("No se pudo reclamar el ciclo de prueba.", file=sys.stderr)
        return 1
    try:
        execute_job(store, claimed)
    except Exception:
        print("El ciclo de prueba falló; revisa su estado local y no reenvíes entregas ambiguas.",
              file=sys.stderr)
    result = store.get(job["id"])
    print(f"Ciclo único: {result['status']} (error={result['error_code'] or 'none'}).")
    return 0 if result["status"] == "succeeded" else 1


def main(*, once=False):
    os.chdir(ROOT)
    store = JobStore()
    lock_path = store.path.with_suffix(".worker.lock")
    try:
        with exclusive_lock(lock_path):
            store.recover()
            if once:
                return _run_single_cycle(store)
            instance_id = uuid.uuid4().hex
            stop = threading.Event()
            heartbeat = threading.Thread(target=_heartbeat_loop, args=(store, instance_id, stop), daemon=True)
            heartbeat.start()
            interval = max(1, INTERVALO_MINUTOS) * 60
            next_cycle = time.monotonic()
            print("web-defense-ai V2: ejecutor coordinado activo; Ctrl+C para detener.")
            try:
                while True:
                    if time.monotonic() >= next_cycle:
                        store.enqueue("periodic")
                        next_cycle = time.monotonic() + interval
                    job = store.claim()
                    if job:
                        try:
                            execute_job(store, job)
                        except Exception:
                            print(f"Trabajo {job['id']} falló; consulta el estado sin reintentar envíos ambiguos.")
                    else:
                        time.sleep(1)
            finally:
                stop.set()
                heartbeat.join(timeout=3)
    except AlreadyRunning:
        print("Ya hay un ejecutor activo en este equipo.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true",
                        help="ejecuta un solo ciclo y termina; puede contactar el motor configurado")
    args = parser.parse_args()
    try:
        raise SystemExit(main(once=args.once))
    except KeyboardInterrupt:
        print("Ejecutor detenido. El trabajo activo se reconciliará al reiniciar.")

"""Fase 5: coordinación aislada, sin Docker, LLM ni transportes externos."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import importlib
import os

from dashboard.services.analysis_jobs import JobStore
from dashboard.services.read_store import atomic_write_text
from dashboard.services.runtime_lock import AlreadyRunning, exclusive_lock
import pipeline


class SimulatedNotificationSink:
    """Captura mensajes en memoria; nunca usa Telegram, SMTP ni red."""

    def __init__(self):
        self.messages = {"telegram": [], "email": []}

    def telegram(self, message):
        self.messages["telegram"].append(message)
        return True

    def email(self, subject, message):
        self.messages["email"].append((subject, message))
        return False


class JobStoreTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "jobs.sqlite3"
        self.store = JobStore(self.path)

    def test_idempotency_and_single_active_job_across_connections(self):
        def request(index):
            return JobStore(self.path).enqueue("manual", f"key-{index}")
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(request, range(8)))
        self.assertEqual(sum(outcome == "created" for _, outcome in results), 1)
        self.assertEqual(sum(outcome == "busy" for _, outcome in results), 7)
        first = next(job for job, outcome in results if outcome == "created")
        same, outcome = JobStore(self.path).enqueue("manual", first["idempotency_key"])
        self.assertEqual(outcome, "duplicate")
        self.assertEqual(same["id"], first["id"])
        claimed = self.store.claim()
        self.assertEqual(claimed["id"], first["id"])
        self.assertIsNone(JobStore(self.path).claim())
        self.store.finish(first["id"], "succeeded")
        second, outcome = self.store.enqueue("periodic")
        self.assertEqual(outcome, "created")
        self.assertNotEqual(second["id"], first["id"])

    def test_recovery_marks_running_interrupted_and_delivery_unknown(self):
        job, _ = self.store.enqueue("manual", "retry-key")
        self.store.claim()
        self.store.delivery(job["id"], "telegram", "attempting")
        JobStore(self.path).recover()
        self.assertEqual(self.store.get(job["id"])["status"], "interrupted")
        self.assertEqual(self.store.delivery(job["id"], "telegram")["status"], "unknown")
        previous, outcome = self.store.enqueue("manual", "retry-key")
        self.assertEqual((previous["id"], outcome), (job["id"], "duplicate"))

    def test_worker_lock_rejects_second_instance(self):
        lock = Path(self.temp.name) / "worker.lock"
        with exclusive_lock(lock):
            with self.assertRaises(AlreadyRunning):
                with exclusive_lock(lock):
                    pass

    def test_alert_destinations_are_attempted_at_most_once(self):
        from config import notifications
        job, _ = self.store.enqueue("manual", "alert-once")
        self.store.claim()
        report = ("## AMENAZAS DETECTADAS\n"
                  "| Línea | Severidad | Tipo | Estado | IP Origen |\n"
                  "| --- | --- | --- | --- | --- |\n"
                  "| 1 | CRÍTICA | SQLi | Intento | 192.0.2.1 |\n")
        sink = SimulatedNotificationSink()
        with patch.object(notifications, "enviar_telegram", side_effect=sink.telegram) as telegram, \
             patch.object(notifications, "enviar_email", side_effect=sink.email) as email:
            pipeline.send_alerts(self.store, job["id"], report)
            pipeline.send_alerts(self.store, job["id"], report)
        self.assertEqual(telegram.call_count, 1)
        self.assertEqual(email.call_count, 1)
        self.assertEqual(len(sink.messages["telegram"]), 1)
        self.assertEqual(len(sink.messages["email"]), 1)
        self.assertIn("1 amenazas críticas", sink.messages["telegram"][0])
        self.assertIn("1 amenazas críticas", sink.messages["email"][0][1])
        self.assertNotIn("192.0.2.1", sink.messages["telegram"][0])
        self.assertNotIn("192.0.2.1", sink.messages["email"][0][1])
        self.assertEqual(self.store.deliveries(job["id"]), {"telegram": "sent", "email": "unknown"})

    def test_analysis_requires_a_new_report_and_never_notifies_on_failure(self):
        report_dir = Path(self.temp.name) / "reports"
        report_dir.mkdir()
        report = report_dir / "reporte_seguridad.md"
        report.write_text("old report", encoding="utf-8")
        notified = []
        with patch.object(pipeline, "REPORT_PATH", str(report_dir)):
            job, _ = self.store.enqueue("manual", "no-report")
            self.store.claim()
            pipeline.execute_job(self.store, job, sync=lambda: True, engine=lambda: True,
                                 notify=lambda *args: notified.append(args))
            self.assertEqual(self.store.get(job["id"])["error_code"], "no_new_report")
            self.assertEqual(notified, [])
            self.assertEqual(report.read_text(encoding="utf-8"), "old report")

            next_job, _ = self.store.enqueue("manual", "new-report")
            self.store.claim()
            def fake_engine():
                atomic_write_text(report, "new synthetic report")
                return True
            pipeline.execute_job(self.store, next_job, sync=lambda: True, engine=fake_engine,
                                 notify=lambda *args: notified.append(args))
            self.assertEqual(self.store.get(next_job["id"])["status"], "succeeded")
            self.assertEqual(len(notified), 1)
            self.assertEqual(len(list((report_dir / "historial").glob("*.md"))), 1)

    def test_ten_synthetic_cycles_survive_store_reopen_without_duplicate_jobs(self):
        report_dir = Path(self.temp.name) / "soak-reports"
        report_dir.mkdir()
        report = report_dir / "reporte_seguridad.md"
        completed = []
        with patch.object(pipeline, "REPORT_PATH", str(report_dir)):
            for index in range(10):
                job, outcome = self.store.enqueue("periodic")
                self.assertEqual(outcome, "created")
                self.store.claim()

                def synthetic_engine(cycle=index):
                    atomic_write_text(report, f"synthetic cycle {cycle}")
                    return True

                pipeline.execute_job(self.store, job, sync=lambda: True, engine=synthetic_engine,
                                     notify=lambda *args: None)
                completed.append(self.store.get(job["id"]))
        reopened = JobStore(self.path)
        self.assertEqual([job["status"] for job in completed], ["succeeded"] * 10)
        self.assertEqual(len(list((report_dir / "historial").glob("*.md"))), 10)
        self.assertEqual(reopened.latest()["id"], completed[-1]["id"])


class AnalysisApiTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.environment = patch.dict(os.environ, {
            "ANALYSIS_DB_PATH": str(Path(self.temp.name) / "jobs.sqlite3"),
            "ANALYSIS_MANUAL_ENABLED": "1",
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.web = importlib.import_module("dashboard.app")
        report_dir = Path(self.temp.name) / "reports"
        history_dir = report_dir / "historial"
        history_dir.mkdir(parents=True)
        self.enterContext(patch.multiple(
            self.web, REPORT_PATH=report_dir, HISTORIAL=history_dir,
            LOG_PATH=str(Path(self.temp.name) / "access.log")))
        self.enterContext(patch.dict(self.web.app.config, TESTING=True))
        self.client = self.web.app.test_client()

    def test_guard_deduplication_conflict_and_status(self):
        with patch.object(self.web, "_executor_status", return_value="online"):
            self.assertEqual(self.client.post("/api/v1/analisis").status_code, 400)
            self.assertEqual(self.client.post("/api/v1/analisis", headers={
                "Idempotency-Key": "one", "Origin": "https://other.example"}).status_code, 403)
            headers = {"Idempotency-Key": "one", "Origin": "http://127.0.0.1:3000"}
            first = self.client.post("/api/v1/analisis", headers=headers)
            self.assertEqual(first.status_code, 202)
            job_id = first.json["data"]["id"]
            again = self.client.post("/api/v1/analisis", headers=headers)
            self.assertEqual(again.status_code, 202)
            self.assertEqual(again.json["data"]["id"], job_id)
            busy = self.client.post("/api/v1/analisis", headers={"Idempotency-Key": "two"})
            self.assertEqual(busy.status_code, 409)
            self.assertEqual(busy.json["data"]["id"], job_id)
            self.assertEqual(self.client.get(f"/api/v1/analisis/{job_id}").json["data"]["status"], "queued")
            self.assertEqual(self.client.get("/api/v1/analisis/actual").json["data"]["job"]["id"], job_id)

    def test_disabled_and_offline_do_not_enqueue(self):
        with patch.dict(os.environ, {"ANALYSIS_MANUAL_ENABLED": "0"}):
            self.assertEqual(self.client.post("/api/v1/analisis", headers={"Idempotency-Key": "one"}).status_code, 403)
        with patch.object(self.web, "_executor_status", return_value="offline"):
            self.assertEqual(self.client.post("/api/v1/analisis", headers={"Idempotency-Key": "one"}).status_code, 503)

    def test_legacy_sync_cannot_race_with_executor(self):
        with patch.object(self.web, "_executor_status", return_value="online"), \
             patch.object(self.web, "run_atomic_copy", side_effect=AssertionError("sincronización duplicada")):
            self.assertEqual(self.client.post("/api/sincronizar").status_code, 409)

    def test_legacy_sync_rejects_cycle_lock_even_before_heartbeat(self):
        lock = Path(os.environ["ANALYSIS_DB_PATH"]).with_suffix(".cycle.lock")
        with exclusive_lock(lock), \
             patch.object(self.web, "_executor_status", return_value="offline"), \
             patch.object(self.web, "run_atomic_copy", side_effect=AssertionError("sincronización duplicada")):
            self.assertEqual(self.client.post("/api/sincronizar").status_code, 409)

    def test_executor_signal_requires_live_lock_and_heartbeat(self):
        path = Path(os.environ["ANALYSIS_DB_PATH"])
        JobStore(path).heartbeat("synthetic-worker")
        lock = path.with_suffix(".worker.lock")
        with exclusive_lock(lock):
            self.assertEqual(self.web._executor_status(), "online")
        self.assertEqual(self.web._executor_status(), "offline")

    def test_dashboard_read_routes_reject_non_loopback_clients(self):
        api = self.client.get("/api/v1/estado", environ_base={"REMOTE_ADDR": "203.0.113.50"})
        self.assertEqual(api.status_code, 403)
        self.assertEqual(api.json["error"]["code"], "local_only")
        page = self.client.get("/", environ_base={"REMOTE_ADDR": "203.0.113.50"})
        self.assertEqual(page.status_code, 403)

    def test_one_five_and_ten_concurrent_read_clients_receive_consistent_contracts(self):
        for clients in (1, 5, 10):
            with self.subTest(clients=clients), ThreadPoolExecutor(max_workers=clients) as pool:
                responses = list(pool.map(
                    lambda _: self.web.app.test_client().get("/api/v1/estado"), range(clients)))
            self.assertEqual([response.status_code for response in responses], [200] * clients)
            self.assertEqual(len({response.json["meta"]["snapshot_id"] for response in responses}), 1)

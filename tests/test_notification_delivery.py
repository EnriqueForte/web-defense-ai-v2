"""Delivery deadlines and recovery with fake subprocesses and transports."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch
from config import notification_delivery as delivery, notifications
from dashboard.services.analysis_jobs import JobStore
import pipeline


class NotificationDeadlineTests(TestCase):
    def test_real_stalled_child_is_terminated_without_notification_transport(self):
        original_run = subprocess.run
        def stalled_child(_command, **kwargs):
            return original_run([sys.executable, "-c", "import time; time.sleep(10)"], **kwargs)
        started = time.monotonic()
        with patch.dict(os.environ, {"NOTIFICATION_DEADLINE_SECONDS": "1"}), \
             patch.object(delivery.subprocess, "run", side_effect=stalled_child):
            self.assertFalse(delivery.deliver_notification("email", "Synthetic"))
        self.assertLess(time.monotonic() - started, 5)

    def test_child_receives_only_aggregate_and_has_finite_total_deadline(self):
        with patch.dict(os.environ, {"NOTIFICATION_DEADLINE_SECONDS": "8"}, clear=True), \
             patch.object(delivery.subprocess, "run", return_value=Mock(returncode=0)) as run:
            self.assertTrue(delivery.deliver_notification("email", "Synthetic aggregate"))
        self.assertEqual(run.call_args.kwargs["timeout"], 8.0)
        self.assertEqual(json.loads(run.call_args.kwargs["input"]),
                         {"destination": "email", "message": "Synthetic aggregate"})
        self.assertEqual(run.call_args.kwargs["stdout"], subprocess.DEVNULL)
        self.assertEqual(run.call_args.kwargs["stderr"], subprocess.DEVNULL)
        self.assertNotIn("Synthetic aggregate", " ".join(run.call_args.args[0]))

    def test_timeout_failure_and_crash_are_unconfirmed(self):
        for error in (subprocess.TimeoutExpired("synthetic-child", 30), OSError("synthetic")):
            with patch.object(delivery.subprocess, "run", side_effect=error):
                self.assertFalse(delivery.deliver_notification("email", "Synthetic"))
        with patch.object(delivery.subprocess, "run", return_value=Mock(returncode=1)):
            self.assertFalse(delivery.deliver_notification("telegram", "Synthetic"))

    def test_deadline_invalid_values_cannot_disable_limit(self):
        for value, expected in (("nan", 30.0), ("inf", 30.0), ("0", 30.0),
                                ("invalid", 30.0), ("1000", 120.0), ("0.1", 1.0)):
            with patch.dict(os.environ, {"NOTIFICATION_DEADLINE_SECONDS": value}, clear=True), \
                 patch.object(delivery.subprocess, "run", return_value=Mock(returncode=0)) as run:
                delivery.deliver_notification("email", "Synthetic")
                self.assertEqual(run.call_args.kwargs["timeout"], expected)

    def test_child_dispatches_exactly_one_transport(self):
        with patch.object(notifications, "enviar_email", return_value=True) as email, \
             patch.object(notifications, "enviar_telegram", return_value=False) as telegram:
            self.assertEqual(delivery.execute_payload({"destination": "email", "message": "Synthetic"}), 0)
            email.assert_called_once_with("[web-defense-ai V2] Alerta de seguridad", "Synthetic")
            telegram.assert_not_called()
            self.assertEqual(delivery.execute_payload({"destination": "telegram", "message": "Synthetic"}), 1)

    def test_malformed_child_input_never_sends(self):
        payloads = (None, {}, {"destination": [], "message": "Synthetic"},
                    {"destination": "unknown", "message": "Synthetic"},
                    {"destination": "email", "message": None},
                    {"destination": "email", "message": "x" * 2049},
                    {"destination": "email", "message": "Synthetic", "key": "forbidden"})
        with patch.object(notifications, "enviar_email") as email, \
             patch.object(notifications, "enviar_telegram") as telegram:
            for payload in payloads:
                self.assertEqual(delivery.execute_payload(payload), 1)
            with patch("sys.stdin", io.StringIO("{")):
                self.assertEqual(delivery.main(), 1)
            email.assert_not_called()
            telegram.assert_not_called()

    def test_timeout_finishes_job_keeps_unknown_and_never_resends(self):
        report = ("## AMENAZAS DETECTADAS\n| Línea | Severidad | Tipo | Estado | IP Origen |\n"
                  "|---|---|---|---|---|\n|1|ALTA|SQLi|Investigar|192.0.2.1|\n")
        with TemporaryDirectory() as folder:
            root = Path(folder)
            store = JobStore(root / "jobs.sqlite3")
            job, _ = store.enqueue("manual", "synthetic-timeout")
            store.claim()
            with patch.object(pipeline, "REPORT_PATH", str(root)), \
                 patch.dict(os.environ, {"NOTIFICATION_DESTINATIONS": "email"}, clear=True), \
                 patch.object(delivery.subprocess, "run", side_effect=subprocess.TimeoutExpired("synthetic", 30)) as send:
                def engine():
                    (root / "reporte_seguridad.md").write_text(report, encoding="utf-8")
                    return True
                pipeline.execute_job(store, job, sync=lambda: True, engine=engine)
                self.assertEqual(store.get(job["id"])["status"], "succeeded")
                self.assertEqual(store.deliveries(job["id"]), {"email": "unknown"})
                pipeline.send_alerts(store, job["id"], report)
                send.assert_called_once()
            self.assertEqual(store.enqueue("manual", "next-after-timeout")[1], "created")
            JobStore(store.path).recover()
            self.assertEqual(store.deliveries(job["id"]), {"email": "unknown"})

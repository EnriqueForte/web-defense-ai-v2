import os
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import pipeline
from dashboard.services.analysis_jobs import JobStore
from dashboard.services import dvwa_lab_capture


class DvwaLabCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.destination = Path(self.temp.name) / "access.log"

    def tearDown(self):
        self.temp.cleanup()

    def test_lab_mode_captures_only_apache_access_lines_into_configured_path(self):
        output = (
            "AH00558: Apache warning\n"
            '172.19.0.2 - - [28/Sep/2026:12:00:00 +0000] "GET /vulnerabilities/sqli/?id=1 HTTP/1.1" 200 123\n'
            '172.19.0.2 - - [28/Sep/2026:12:01:00 +0000] "POST /login.php HTTP/1.1" 302 0\n'
        )
        completed = CompletedProcess(args=[], returncode=0, stdout=output, stderr="AH00558")
        with patch.dict(os.environ, {"LOG_SYNC_SOURCE": "dvwa-lab"}, clear=True), \
             patch.object(pipeline, "LOG_PATH", str(self.destination)), \
             patch.object(dvwa_lab_capture.subprocess, "run", return_value=completed) as run:
            self.assertTrue(pipeline.synchronize_log())

        self.assertIn("/vulnerabilities/sqli/", self.destination.read_text(encoding="utf-8"))
        self.assertNotIn("AH00558", self.destination.read_text(encoding="utf-8"))
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0][-1], dvwa_lab_capture.CONTAINER_NAME)

    def test_failed_capture_preserves_previous_log(self):
        self.destination.write_text("existing safe snapshot\n", encoding="utf-8")
        completed = CompletedProcess(args=[], returncode=1, stdout="", stderr="docker unavailable")
        with patch.object(dvwa_lab_capture.subprocess, "run", return_value=completed):
            self.assertIsNone(dvwa_lab_capture.capture_access_log(self.destination))
        self.assertEqual(self.destination.read_text(encoding="utf-8"), "existing safe snapshot\n")

    def test_empty_capture_preserves_previous_log(self):
        self.destination.write_text("existing safe snapshot\n", encoding="utf-8")
        completed = CompletedProcess(args=[], returncode=0, stdout="Apache started\n", stderr="")
        with patch.object(dvwa_lab_capture.subprocess, "run", return_value=completed):
            self.assertIsNone(dvwa_lab_capture.capture_access_log(self.destination))
        self.assertEqual(self.destination.read_text(encoding="utf-8"), "existing safe snapshot\n")


class SingleCycleTests(unittest.TestCase):
    def test_manual_only_worker_never_schedules_periodic_cycle(self):
        self.assertFalse(pipeline.periodic_cycle_due(
            manual_only=True, now=1000, next_cycle=0,
        ))

    def test_regular_worker_schedules_periodic_cycle_when_due(self):
        self.assertTrue(pipeline.periodic_cycle_due(
            manual_only=False, now=1000, next_cycle=0,
        ))

    def test_single_cycle_finishes_once_and_returns_success(self):
        with tempfile.TemporaryDirectory() as temp:
            store = JobStore(Path(temp) / "analysis.sqlite3")

            def fake_execute(current_store, job):
                current_store.finish(job["id"], "succeeded")

            with patch.object(pipeline, "execute_job", side_effect=fake_execute):
                self.assertEqual(pipeline._run_single_cycle(store), 0)

            self.assertEqual(store.latest()["status"], "succeeded")

    def test_single_cycle_does_not_report_failed_work_as_success(self):
        with tempfile.TemporaryDirectory() as temp:
            store = JobStore(Path(temp) / "analysis.sqlite3")

            def fake_execute(current_store, job):
                current_store.finish(job["id"], "failed", "analysis_failed")

            with patch.object(pipeline, "execute_job", side_effect=fake_execute):
                self.assertEqual(pipeline._run_single_cycle(store), 1)

    def test_failed_engine_stores_bounded_diagnostic_with_api_key_redacted(self):
        with tempfile.TemporaryDirectory() as temp:
            secret = "test-only-secret-token"
            result = CompletedProcess(args=[], returncode=1, stdout="", stderr=f"401 {secret} rejected")
            with patch.dict(os.environ, {"ENGINE_DIAGNOSTICS_DIR": temp, "GROQ_API_KEY": secret}, clear=True), \
                 patch.object(pipeline.subprocess, "run", return_value=result):
                self.assertFalse(pipeline.run_engine())

            files = list(Path(temp).glob("engine-failure-*.log"))
            self.assertEqual(len(files), 1)
            contents = files[0].read_text(encoding="utf-8")
            self.assertIn("401 [REDACTED] rejected", contents)
            self.assertNotIn(secret, contents)


if __name__ == "__main__":
    unittest.main()

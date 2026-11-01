"""Isolated launcher checks; mocked processes/HTTP, never a real worker or model."""
import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import webdefense as cli
from scripts import start_application as start


class ManualLauncherTests(TestCase):
    def test_pending_jobs_block_manual_start_before_process_creation(self):
        with patch.object(start.sys, "version_info", (3, 11, 0)), \
                patch.object(start, "require_build"), patch.object(start, "require_free_port"), \
                patch.object(start, "readiness", return_value={
                    "ready": False, "blockers": ["active_jobs_or_unreadable_store"],
                }) as readiness, patch.object(start, "ProcessOwner") as owner:
            with self.assertRaisesRegex(ValueError, "trabajos activos"):
                start.preflight(Path.cwd(), "structured", enable_manual=True)
            owner.assert_not_called()
            self.assertTrue(readiness.call_args.kwargs["enable_manual"])
            self.assertEqual(readiness.call_args.kwargs["component"], "all")

    def test_manual_flag_does_not_turn_install_or_legacy_into_an_analysis_start(self):
        for arguments in (["install", "--enable-manual"], ["start", "--enable-manual"]):
            with self.subTest(arguments=arguments), patch.object(cli.subprocess, "Popen") as spawn, \
                    patch.object(cli, "python_command") as install, \
                    contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(cli.main(arguments), 1)
                spawn.assert_not_called()
                install.assert_not_called()

    def test_worker_readiness_requires_admission_and_heartbeat_not_provider_contact(self):
        responses = [
            {"manual_enabled": False, "executor": "online"},
            {"manual_enabled": True, "executor": "offline"},
            {"manual_enabled": True, "executor": "online", "llm_ready": False},
        ]
        with patch.object(start, "build_opener") as factory, patch.object(start.time, "sleep"):
            response = factory.return_value.open.return_value.__enter__.return_value
            response.status = 200
            response.read.side_effect = [
                json.dumps({"meta": {"api_version": "1"}, "data": data}).encode()
                for data in responses
            ]
            start.wait_http("http://127.0.0.1:5000/api/v1/analisis/actual", [], manual=True)
            self.assertEqual(factory.return_value.open.call_count, 3)
            for call in factory.return_value.open.call_args_list:
                self.assertEqual(call.args[0], "http://127.0.0.1:5000/api/v1/analisis/actual")

    def test_worker_failure_closes_owned_processes_without_starting_next(self):
        with TemporaryDirectory() as folder, patch.object(start, "ProcessOwner") as factory, \
                patch.object(start, "wait_http", side_effect=[None, RuntimeError("worker unavailable")]), \
                contextlib.redirect_stdout(io.StringIO()):
            owner = factory.return_value
            owner.spawn.return_value = SimpleNamespace(poll=lambda: None)
            plan = {
                "enable_manual": True,
                "environment_overrides": {"ANALYSIS_MANUAL_ENABLED": "1", "NOTIFICATION_DESTINATIONS": ""},
                "commands": {"flask": ["flask"], "worker": ["pipeline.py", "--manual-only"]},
            }
            with self.assertRaisesRegex(RuntimeError, "worker unavailable"):
                start.serve(Path(folder), plan, "node")
            self.assertEqual(owner.spawn.call_count, 2)
            self.assertIn("--manual-only", owner.spawn.call_args.args[0])
            self.assertEqual(owner.spawn.call_args.kwargs["env"]["ANALYSIS_MANUAL_ENABLED"], "1")
            self.assertEqual(owner.spawn.call_args.kwargs["env"]["NOTIFICATION_DESTINATIONS"], "")
            owner.close.assert_called_once()
            self.assertEqual(len(list(Path(folder).glob(".local-state/launcher/*/worker.log"))), 1)

    def test_manual_check_reports_the_same_mode_without_starting_services(self):
        with patch.object(start, "preflight") as preflight, patch.object(start, "serve") as serve, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(start.main([
                "--node", "node", "--check", "--mode", "structured", "--with-puerto-umbral",
                "--lab-mode", "corrected", "--enable-manual",
            ]), 0)
            self.assertTrue(preflight.call_args.kwargs["enable_manual"])
            serve.assert_not_called()
            self.assertIn("webdefensev2.py --lab-mode corrected --enable-manual", output.getvalue())

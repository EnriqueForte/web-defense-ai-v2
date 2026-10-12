"""Local start proposal: no dotenv, engine/provider, process or transport in these tests."""
import contextlib
from contextlib import closing
import io
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from dashboard.services.runtime_lock import exclusive_lock
from scripts import local_runtime_profile as runtime


class LocalRuntimeProfileTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.environment = patch.object(runtime, "compare", return_value=[])
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.port = patch.object(runtime, "port_available", return_value=True)
        self.port.start()
        self.addCleanup(self.port.stop)

    def check(self, **kwargs):
        return runtime.readiness(self.root, pins={}, **kwargs)

    def test_common_profile_paths_match_both_components_and_children(self):
        for profile in ("legacy", "pilot"):
            plan = runtime.build_plan(self.root, profile, "structured")
            env = plan["environment_overrides"]
            self.assertEqual(env["ANALYSIS_ENGINE_MODE"], "structured")
            self.assertEqual(env["NOTIFICATION_DESTINATIONS"], "")
            self.assertEqual(env["ANALYSIS_MANUAL_ENABLED"], "0")
            self.assertIn("--manual-only", plan["commands"]["worker"])
            self.assertIn("127.0.0.1", plan["commands"]["flask"])
            self.assertTrue(Path(env["ANALYSIS_DB_PATH"]).is_absolute())
            self.assertEqual(plan["commands"]["worker"][0], plan["commands"]["flask"][0])

    def test_missing_store_and_generation_are_reported_without_creating_them(self):
        before = list(self.root.iterdir())
        result = self.check(mode="structured")
        self.assertTrue(result["ready"])
        self.assertEqual(result["jobs"]["status"], "absent")
        self.assertEqual(result["report_source"]["status"], "absent")
        self.assertEqual(list(self.root.iterdir()), before)

    def test_active_jobs_or_invalid_store_block_start_without_mutation(self):
        db = self.root / runtime.PROFILES["pilot"]["db"]
        db.parent.mkdir(parents=True)
        with closing(sqlite3.connect(db)) as connection:
            connection.execute("CREATE TABLE jobs(status TEXT)")
            connection.execute("INSERT INTO jobs VALUES('queued')")
            connection.commit()
        before = db.read_bytes()
        result = self.check(mode="structured")
        self.assertEqual(result["jobs"]["queued"], 1)
        self.assertIn("active_jobs_or_unreadable_store", result["blockers"])
        self.assertEqual(db.read_bytes(), before)
        db.write_bytes(b"synthetic invalid sqlite")
        self.assertEqual(self.check()["jobs"]["status"], "unavailable")

    def test_held_lock_is_seen_without_removing_or_rewriting_it(self):
        lock = (self.root / runtime.PROFILES["pilot"]["db"]).with_suffix(".worker.lock")
        lock.parent.mkdir(parents=True)
        lock.write_bytes(b"1")
        before = lock.read_bytes()
        with exclusive_lock(lock):
            self.assertEqual(runtime.existing_lock_status(lock), "held")
            self.assertIn("runtime_lock_active_or_unknown", self.check()["blockers"])
        self.assertEqual(lock.read_bytes(), before)
        self.assertEqual(runtime.existing_lock_status(lock), "free")

    def test_port_required_for_flask_but_not_for_worker_with_flask_already_running(self):
        for available, blocker in ((False, "flask_port_in_use"), (None, "flask_port_unverified")):
            with self.subTest(available=available), patch.object(runtime, "port_available", return_value=available):
                result = self.check(component="flask")
                self.assertIn(blocker, result["blockers"])
                self.assertFalse(result["ready"])
                self.assertTrue(self.check(component="worker")["ready"])

    def test_environment_differences_and_corrupt_pointer_block_start(self):
        with patch.object(runtime, "compare", return_value=[("mock", "2", "1")]):
            self.assertIn("environment_differences", self.check()["blockers"])
        current = self.root / runtime.PROFILES["pilot"]["reports"] / "structured/current.json"
        current.parent.mkdir(parents=True)
        current.write_text("{}", encoding="utf-8")
        self.assertIn("invalid_current_generation", self.check(mode="structured")["blockers"])

    def test_default_cli_plan_does_not_start_process_or_emit_inherited_secret(self):
        plan = runtime.build_plan(self.root)
        with patch.object(runtime, "readiness", return_value={"ready": True, "plan": plan}), \
                patch.object(runtime.sys, "argv", ["profile"]), \
                patch.dict(runtime.os.environ, {"OPENROUTER_API_KEY": "synthetic-private-key"}), \
                patch.object(runtime.subprocess, "run") as launch, contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(runtime.main(), 0)
            launch.assert_not_called()
        self.assertNotIn("synthetic-private-key", output.getvalue())
        self.assertEqual(plan["mode"], "legacy")

    def test_explicit_start_requires_ready_state_and_applies_common_overrides(self):
        plan = runtime.build_plan(self.root, "pilot", "structured")
        arguments = ["profile", "--profile", "pilot", "--mode", "structured", "--component", "worker", "--start"]
        with patch.object(runtime.sys, "argv", arguments), contextlib.redirect_stdout(io.StringIO()), \
                patch.object(runtime.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as launch:
            with patch.object(runtime, "readiness", return_value={"ready": False, "plan": plan}):
                self.assertEqual(runtime.main(), 1)
                launch.assert_not_called()
            with patch.object(runtime, "readiness", return_value={"ready": True, "plan": plan}):
                self.assertEqual(runtime.main(), 0)
            self.assertEqual(launch.call_args.kwargs["env"]["ANALYSIS_ENGINE_MODE"], "structured")
            self.assertEqual(launch.call_args.kwargs["env"]["NOTIFICATION_DESTINATIONS"], "")
            self.assertEqual(launch.call_args.args[0], plan["commands"]["worker"])

    def test_unknown_profile_or_mode_is_rejected(self):
        for profile, mode in (("invalid", "legacy"), ("pilot", "invalid")):
            with self.assertRaises(ValueError):
                runtime.build_plan(self.root, profile, mode)

    def test_legacy_return_does_not_read_structured_pointer(self):
        report = self.root / runtime.PROFILES["pilot"]["reports"] / "reporte_seguridad.md"
        report.parent.mkdir(parents=True)
        report.write_text("Legacy preserved", encoding="utf-8")
        with patch.object(Path, "is_symlink", autospec=True, side_effect=lambda path: path.name == "current.json"):
            result = self.check(mode="legacy")
        self.assertTrue(result["ready"])
        self.assertEqual(result["report_source"], {"kind": "legacy", "status": "available"})

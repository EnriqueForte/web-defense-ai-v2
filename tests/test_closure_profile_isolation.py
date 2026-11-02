"""Closure regressions: temporary profile files, mocked environment and port.

No HTTP, Docker, services, dotenv, credentials, scenarios or provider calls.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from scripts import local_runtime_profile as runtime


class ClosureProfileIsolationTests(TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name, value in (("compare", []), ("port_available", True)):
            mocked = patch.object(runtime, name, return_value=value)
            mocked.start()
            self.addCleanup(mocked.stop)

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def readiness(self, profile, mode="structured"):
        return runtime.readiness(self.root, profile, mode, pins={})

    def test_three_profiles_have_distinct_log_report_and_database_paths(self):
        sources = {"legacy": "legacy-docker", "pilot": "dvwa-lab", "puerto-umbral": "puerto-umbral"}
        plans = {profile: runtime.build_plan(self.root, profile, "structured")
                 for profile in sources}
        for key in ("LOG_PATH", "REPORT_PATH", "ANALYSIS_DB_PATH"):
            values = [Path(plan["environment_overrides"][key]) for plan in plans.values()]
            self.assertEqual(len(set(values)), 3)
            self.assertTrue(all(path.is_relative_to(self.root) for path in values))
        for profile, plan in plans.items():
            env = plan["environment_overrides"]
            self.assertEqual(env["LOG_SYNC_SOURCE"], sources[profile])
            self.assertEqual(env["ANALYSIS_MANUAL_ENABLED"], "0")
            self.assertEqual(env["NOTIFICATION_DESTINATIONS"], "")
        self.assertEqual(self.snapshot(), {})

    def test_puerto_source_mode_is_explicit_and_manual_does_not_change_paths(self):
        normal = runtime.build_plan(self.root, "puerto-umbral", "structured", lab_mode="corrected")
        manual = runtime.build_plan(self.root, "puerto-umbral", "structured", lab_mode="vulnerable", enable_manual=True)
        first, second = normal["environment_overrides"], manual["environment_overrides"]
        self.assertEqual(first["PUERTO_UMBRAL_MODE"], "corrected")
        self.assertEqual(second["PUERTO_UMBRAL_MODE"], "vulnerable")
        self.assertEqual(first["ANALYSIS_MANUAL_ENABLED"], "0")
        self.assertEqual(second["ANALYSIS_MANUAL_ENABLED"], "1")
        for key in ("LOG_PATH", "REPORT_PATH", "ANALYSIS_DB_PATH", "LOG_SYNC_SOURCE"):
            self.assertEqual(first[key], second[key])
        for env in (first, second):
            self.assertEqual(env["LOG_CAPTURE_MANUAL_ENABLED"], "1")
            self.assertEqual(env["LOG_FOLLOW_ENABLED"], "1")
        self.assertEqual(self.snapshot(), {})

    def test_incompatible_puerto_legacy_engine_is_rejected_before_writes(self):
        with self.assertRaisesRegex(ValueError, "invalid_puerto_umbral_mode"):
            runtime.build_plan(self.root, "puerto-umbral", "legacy")
        self.assertEqual(self.snapshot(), {})

    def test_corrupt_puerto_pointer_blocks_only_selected_profile_without_fallback(self):
        pointer = self.root / runtime.PROFILES["puerto-umbral"]["reports"] / "structured/current.json"
        pointer.parent.mkdir(parents=True)
        pointer.write_bytes(b"{}")
        # Existing other-profile evidence must neither become a fallback nor be
        # rewritten by the Puerto preflight. These are temporary synthetic data.
        for profile in ("legacy", "pilot"):
            directory = self.root / runtime.PROFILES[profile]["reports"]
            directory.mkdir(parents=True)
            (directory / "reporte_seguridad.md").write_bytes(b"Existing other-profile report")
        before = self.snapshot()
        result = self.readiness("puerto-umbral")
        self.assertFalse(result["ready"])
        self.assertIn("invalid_current_generation", result["blockers"])
        self.assertEqual(result["report_source"], {"kind": "structured", "status": "invalid"})
        for profile in ("legacy", "pilot"):
            legacy = self.readiness(profile, "legacy")
            self.assertTrue(legacy["ready"])
            self.assertEqual(legacy["report_source"], {"kind": "legacy", "status": "available"})
            structured = self.readiness(profile)
            self.assertTrue(structured["ready"])
            self.assertEqual(structured["report_source"]["status"], "absent")
        self.assertEqual(self.snapshot(), before)

    def test_absent_publication_is_distinct_from_corruption_without_creating_files(self):
        before = self.snapshot()
        for profile in ("legacy", "pilot", "puerto-umbral"):
            result = self.readiness(profile)
            self.assertTrue(result["ready"])
            self.assertEqual(result["jobs"]["status"], "absent")
            self.assertEqual(result["report_source"], {"kind": "structured", "status": "absent"})
            self.assertNotIn("invalid_current_generation", result["blockers"])
        self.assertEqual(self.snapshot(), before)

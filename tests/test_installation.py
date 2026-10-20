"""Installation safety and platform selection; no packages/processes installed."""
import contextlib
import io
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from scripts import setup_installation as setup
from scripts import check_environment as contract
from scripts import local_runtime_profile as runtime


class InstallationTests(TestCase):
    def test_windows_and_linux_paths_and_frozen_frontend(self):
        with TemporaryDirectory() as directory, patch.object(setup.shutil, "which", return_value="pnpm"):
            for platform, suffix in (("win32", "Scripts/python.exe"), ("linux", "bin/python")):
                plan = setup.installation_plan(directory, platform=platform, frontend=True)
                self.assertEqual(Path(plan["python"]), Path(directory).resolve() / ".p2" / suffix)
                self.assertEqual(plan["commands"][0][1:3], ["-m", "venv"])
                self.assertIn(str(Path(directory).resolve() / "requirements-bootstrap.txt"), plan["commands"][1])
                self.assertIn(str(Path(directory).resolve() / "constraints-py311.txt"), plan["commands"][2])
                self.assertEqual(plan["frontend_commands"], [["pnpm", "install", "--frozen-lockfile"]])

    def test_plan_does_not_create_environment_or_config(self):
        with TemporaryDirectory() as directory:
            setup.installation_plan(directory)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_unrecognized_platform_or_existing_directory_rejected(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                setup.installation_plan(directory, platform="darwin")
            (Path(directory) / ".p2").mkdir()
            with self.assertRaises(ValueError):
                setup.installation_plan(directory)

    def test_existing_environment_is_not_recreated(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            executable = root / ".p2/Scripts/python.exe"
            executable.parent.mkdir(parents=True)
            executable.touch()
            (root / ".p2/pyvenv.cfg").write_text("synthetic", encoding="utf-8")
            plan = setup.installation_plan(root, platform="win32")
            self.assertEqual(plan["commands"][0][1:4], ["-m", "pip", "install"])
            with patch.object(setup.subprocess, "run", return_value=SimpleNamespace(returncode=1)) as run:
                with self.assertRaises(ValueError):
                    setup.execute(plan)
                self.assertEqual(run.call_count, 1)

    def test_existing_env_preserved_without_reading_it(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_bytes(b"private synthetic config")
            self.assertEqual(setup.initialize_env(root), "existing_preserved")
            self.assertEqual((root / ".env").read_bytes(), b"private synthetic config")

    def test_config_created_from_example_only(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env.example").write_text("ANALYSIS_MANUAL_ENABLED=0\n", encoding="utf-8")
            self.assertEqual(setup.initialize_env(root), "created")
            self.assertEqual((root / ".env").read_text(encoding="utf-8"), "ANALYSIS_MANUAL_ENABLED=0\n")

    def test_cli_default_does_not_execute_installation(self):
        with patch.object(setup.sys, "argv", ["setup"]), patch.object(setup, "execute") as install, \
                patch.object(setup, "initialize_env") as configure, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup.main(), 0)
            install.assert_not_called()
            configure.assert_not_called()

    def test_shared_pins_preserve_snapshot_except_reviewed_security_updates(self):
        for platform in ("win32", "linux"):
            with patch.object(contract.sys, "platform", platform):
                shared = contract.read_pins(setup.ROOT / "constraints-py311.txt")
                historical = contract.read_pins(setup.ROOT / "constraints-windows-py311-crewai-20261012.txt")
                # Preserve the dated snapshot; only the reviewed security pair may drift.
                expected = {**historical, "aiohttp": "3.14.4", "yarl": "1.25.1"}
                if platform == "linux":
                    expected["uvloop"] = "0.23.0"
                self.assertEqual(shared, expected)
                self.assertEqual("pywin32" in shared, platform == "win32")
                self.assertEqual("uvloop" in shared, platform == "linux")

    def test_bootstrap_failure_stops_before_application_install_or_frontend(self):
        with TemporaryDirectory() as directory:
            plan = setup.installation_plan(directory, platform="win32")
            def run(command, **kwargs):
                if any(str(item).endswith('requirements-bootstrap.txt') for item in command):
                    raise setup.subprocess.CalledProcessError(1, command)
                return SimpleNamespace(returncode=0)
            with patch.object(setup.subprocess, 'run', side_effect=run) as invoked:
                with self.assertRaises(setup.subprocess.CalledProcessError):
                    setup.execute(plan)
                self.assertEqual(invoked.call_count, 2)  # venv, then bootstrap only

    def test_manual_admission_requires_explicit_flag_and_worker_stays_manual_only(self):
        with TemporaryDirectory() as directory:
            default = runtime.build_plan(directory)
            enabled = runtime.build_plan(directory, enable_manual=True)
            self.assertEqual(default["environment_overrides"]["ANALYSIS_MANUAL_ENABLED"], "0")
            self.assertEqual(enabled["environment_overrides"]["ANALYSIS_MANUAL_ENABLED"], "1")
            self.assertEqual(enabled["environment_overrides"]["NOTIFICATION_DESTINATIONS"], "")
            self.assertIn("--manual-only", enabled["commands"]["worker"])

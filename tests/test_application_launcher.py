"""User entry and lifecycle regression; synthetic children, never an analysis worker."""
import contextlib
import io
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import time
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import webdefense as cli
from scripts import setup_installation as setup
from scripts import start_application as start
from scripts.process_owner import ProcessOwner


class UserEntryTests(TestCase):
    def test_install_rejects_active_job_and_preserves_database(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            db = root / ".local-state/analysis.sqlite3"
            db.parent.mkdir()
            with sqlite3.connect(db) as connection:
                connection.execute("CREATE TABLE jobs(status TEXT)")
                connection.execute("INSERT INTO jobs VALUES ('running')")
            connection.close()
            before = db.read_bytes()
            with self.assertRaisesRegex(ValueError, "análisis"):
                with cli.installation_locks(root):
                    self.fail("installation must not proceed")
            self.assertEqual(db.read_bytes(), before)

    def test_python_discovery_rejects_wrong_version_and_accepts_311_with_modules(self):
        with patch.object(cli.shutil, "which", return_value="python3.11"), \
                patch.object(cli, "output", side_effect=["3.13", "3.11"]) as probe:
            self.assertEqual(cli.python_command(), ["python3.11"])
            self.assertIn("venv, ensurepip", probe.call_args.args[0][-1])
        with patch.object(cli.shutil, "which", return_value=None), patch.object(cli, "output", return_value="3.13"):
            with self.assertRaisesRegex(ValueError, "Python 3.11"):
                cli.python_command()

    def test_tools_reject_old_node_wrong_pnpm_and_timeout(self):
        with patch.object(cli.shutil, "which", return_value="tool"):
            with patch.object(cli, "output", return_value="v20.19.2"):
                with self.assertRaisesRegex(ValueError, "Node 24"):
                    cli.frontend_tools(installing=True)
            with patch.object(cli, "output", side_effect=["v24.21.0", "10.0.0"]):
                with self.assertRaisesRegex(ValueError, "pnpm 11.19.0"):
                    cli.frontend_tools(installing=True)
        with patch.object(cli.subprocess, "run", side_effect=subprocess.TimeoutExpired("node", 15)):
            self.assertEqual(cli.output(["node", "--version"]), "")

    def test_install_checks_all_requirements_before_mutation(self):
        with TemporaryDirectory() as folder, patch.object(cli, "ROOT", Path(folder)), \
                patch.object(cli, "python_command", return_value=["python"]), \
                patch.object(cli, "frontend_tools", side_effect=ValueError("missing node")), \
                patch.object(cli.subprocess, "call") as run, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["install"]), 1)
            run.assert_not_called()
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_install_blocks_active_server_before_installing(self):
        with TemporaryDirectory() as folder, patch.object(cli, "ROOT", Path(folder)), \
                patch.object(cli, "python_command", return_value=["python"]), \
                patch.object(cli, "frontend_tools", return_value="node"), \
                patch.object(cli, "require_stopped", side_effect=ValueError("occupied")), \
                patch.object(cli.subprocess, "call") as run, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["install"]), 1)
            run.assert_not_called()

    def test_install_includes_build_env_creation_and_propagates_failure(self):
        with TemporaryDirectory() as folder, patch.object(cli, "ROOT", Path(folder)), \
                patch.object(cli, "python_command", return_value=["python"]), \
                patch.object(cli, "frontend_tools", return_value="node"), \
                patch.object(cli, "require_stopped"), patch.object(cli.subprocess, "call", return_value=7) as run, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["install"]), 7)
            self.assertEqual(run.call_args.args[0][-4:], ["--install", "--frontend", "--build", "--init-env"])

    def test_build_plan_optional_and_requires_frontend(self):
        with TemporaryDirectory() as folder, patch.object(setup.shutil, "which", return_value="pnpm"):
            plan = setup.installation_plan(folder, frontend=True, build=True)
            self.assertEqual(plan["frontend_commands"], [["pnpm", "install", "--frozen-lockfile"], ["pnpm", "run", "build"]])
            with self.assertRaises(ValueError):
                setup.installation_plan(folder, build=True)

    def test_build_failure_preserves_config_and_does_not_report_success(self):
        with TemporaryDirectory() as folder, patch.object(setup, "ROOT", Path(folder)), \
                patch.object(setup.sys, "argv", ["setup", "--install", "--frontend", "--build", "--init-env"]), \
                patch.object(setup, "installation_plan", return_value={}), \
                patch.object(setup, "execute", side_effect=subprocess.CalledProcessError(1, ["pnpm", "run", "build"])), \
                patch.object(setup, "initialize_env") as config, \
                contextlib.redirect_stdout(io.StringIO()) as console, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(setup.main(), 1)
            config.assert_not_called()
            self.assertNotIn("Instalación completada", console.getvalue())


class LauncherTests(TestCase):
    def test_missing_build_or_wrong_proxy_rejected(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaisesRegex(ValueError, "compilar"):
                start.require_build(root)
            binary = root / "frontend/node_modules/next/dist/bin/next"
            binary.parent.mkdir(parents=True)
            binary.touch()
            build = root / "frontend/.next"
            build.mkdir()
            (build / "BUILD_ID").write_text("synthetic")
            for destination in ("http://remote:5000/api/v1/:path*", "http://127.0.0.1:5000/api/v1/:path*"):
                (build / "routes-manifest.json").write_text(json.dumps({"rewrites": {"afterFiles": [
                    {"source": "/api/v1/:path*", "destination": destination}]}}))
                if "remote" in destination:
                    with self.assertRaisesRegex(ValueError, "5000"):
                        start.require_build(root)
                else:
                    start.require_build(root)

    def test_occupied_port_is_preserved(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            port = listener.getsockname()[1]
            with self.assertRaisesRegex(ValueError, str(port)):
                start.require_free_port(port)
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                pass

    def test_preflight_explains_blocker_and_never_spawns(self):
        with patch.object(start, "require_build"), patch.object(start, "require_free_port"), \
                patch.object(start, "readiness", return_value={"ready": False, "blockers": ["environment_differences"]}), \
                patch.object(start, "ProcessOwner") as owner:
            with self.assertRaisesRegex(ValueError, "contrato"):
                start.preflight(Path.cwd(), "legacy")
            owner.assert_not_called()

    def test_check_only_does_not_create_runtime_directory_or_spawn(self):
        with patch.object(start, "preflight") as preflight, patch.object(start, "serve") as serve, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(start.main(["--node", "node", "--check"]), 0)
            preflight.assert_called_once()
            serve.assert_not_called()

    def test_early_exit_and_health_timeout_fail(self):
        process = SimpleNamespace(poll=lambda: 2)
        with self.assertRaisesRegex(RuntimeError, "Flask"):
            start.wait_http("http://127.0.0.1:1/", [("Flask", process)])
        with self.assertRaisesRegex(RuntimeError, "tiempo"):
            start.wait_http("http://127.0.0.1:1/", [], timeout=0)

    def test_http200_requires_health_contract_but_allows_missing_sources(self):
        with patch.object(start, "build_opener") as factory, patch.object(start.time, "sleep"):
            response = factory.return_value.open.return_value.__enter__.return_value
            response.status = 200
            response.read.side_effect = [b'<html>not the API</html>',
                                        b'{"meta":{"api_version":"1"},"data":{"status":"degraded"}}']
            start.wait_http("http://127.0.0.1:5000/api/v1/salud", [], health=True)
            self.assertEqual(factory.return_value.open.call_count, 2)

    def test_second_component_failure_cleans_first_and_creates_no_worker(self):
        with TemporaryDirectory() as folder, patch.object(start, "ProcessOwner") as factory, \
                patch.object(start, "wait_http"), contextlib.redirect_stdout(io.StringIO()):
            process = SimpleNamespace(poll=lambda: None)
            owner = factory.return_value
            owner.spawn.side_effect = [process, OSError("synthetic next failure")]
            plan = {"environment_overrides": {"ANALYSIS_MANUAL_ENABLED": "0", "NOTIFICATION_DESTINATIONS": ""},
                    "commands": {"flask": [sys.executable, "flask"]}}
            with self.assertRaises(OSError):
                start.serve(Path(folder), plan, "node")
            owner.close.assert_called_once()
            self.assertEqual(owner.spawn.call_count, 2)
            self.assertIn("start", owner.spawn.call_args.args[0])
            self.assertEqual(owner.spawn.call_args.kwargs["env"]["ANALYSIS_MANUAL_ENABLED"], "0")

    def test_owned_tree_stops_descendants_even_after_parent_exit(self):
        # Actual synthetic processes exercise Windows Job ownership and POSIX groups.
        with TemporaryDirectory() as folder, open(os.devnull, "wb") as log:
            marker = Path(folder) / "heartbeat"
            child = ("import pathlib,time; p=pathlib.Path(" + repr(str(marker)) + "); "
                     "exec('while True:\\n p.write_text(str(time.time()))\\n time.sleep(.02)')")
            parent = "import subprocess,sys; subprocess.Popen([sys.executable,'-c'," + repr(child) + "])"
            owner = ProcessOwner()
            try:
                process = owner.spawn([getattr(sys, "_base_executable", sys.executable), "-c", parent],
                                      cwd=folder, env=os.environ.copy(), log=log)
                deadline = time.monotonic() + 10
                while not marker.exists() and time.monotonic() < deadline:
                    time.sleep(.02)
                self.assertTrue(marker.exists(), "synthetic child failed to start")
                process.wait(timeout=5)
            finally:
                owner.close()
            before = marker.read_text()
            time.sleep(.15)
            self.assertEqual(marker.read_text(), before, "descendant survived owner cleanup")

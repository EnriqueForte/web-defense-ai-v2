"""A-05 isolated integration and rollback; no provider or transport."""
import importlib
import ast
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from agents.evidence_contracts import ContractError
from agents.evidence_preparation import prepare_evidence
from agents.structured_engine import engine_mode, read_input, run_structured
from dashboard.services.active_report import capture_current
from dashboard.services.analysis_jobs import JobStore
from dashboard.services.structured_publication import publish, load_current

ID = "a" * 32
TEXT = '192.0.2.1 - - [06/Oct/2026:12:00:00 +0000] "GET /?q=UNION+SELECT HTTP/1.1" 200 1'


def payloads(prepared):
    return (
        {"schema_version": "1", "analysis_id": prepared.bundle.analysis_id, "candidates": [
            {"candidate_id": "c_1", "evidence_ids": [prepared.bundle.items[0].evidence_id],
             "pattern": "sql_injection", "reason": "Observed token"}]},
        {"schema_version": "1", "analysis_id": prepared.bundle.analysis_id, "classifications": [
            {"candidate_id": "c_1", "severity": "high", "state": "requires_investigation", "reason": "Payload only"}]},
        {"schema_version": "1", "analysis_id": prepared.bundle.analysis_id, "summary": "Review request",
         "recommendations": [{"candidate_id": "c_1", "text": "Validate query"}]})


class IntegrationTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.legacy = self.root / "reporte_seguridad.md"
        self.legacy.write_text("Legacy preserved", encoding="utf-8")
        self.environment = patch.dict(os.environ, {"ANALYSIS_ENGINE_MODE": "structured"})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def publish(self, analysis_id=ID):
        prepared = prepare_evidence(TEXT, analysis_id)
        return publish(self.root / "structured", prepared, *payloads(prepared), model="offline", prompt_version="test")

    def test_default_mode_and_invalid_value_fail_closed(self):
        self.assertEqual(engine_mode({}), "legacy")
        with self.assertRaises(ContractError):
            engine_mode({"ANALYSIS_ENGINE_MODE": "typo"})

    def test_main_routes_structured_input_without_running_legacy_agents(self):
        import agents.structured_engine as service
        source = Path(__file__).resolve().parents[1] / "main.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_run_analysis")
        llm = SimpleNamespace(model="offline")
        from unittest.mock import Mock
        llm_factory = Mock(return_value=llm)
        namespace = {"os": os, "get_llm_con_retry": llm_factory}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(source), "exec"), namespace)
        with patch.dict(os.environ, {"LOG_PATH": "synthetic.log", "REPORT_PATH": str(self.root),
                                     "STRUCTURED_ANALYSIS_ID": ID}), \
                patch.object(service, "read_input", return_value=TEXT), \
                patch.object(service, "run_structured") as runner:
            namespace["_run_analysis"]()
            self.assertEqual(runner.call_args.args, (TEXT, llm, str(self.root)))
            self.assertEqual(runner.call_args.kwargs["analysis_id"], ID)
            llm_factory.assert_called_once_with(max_tokens=service.STRUCTURED_MAX_TOKENS,
                                                timeout=service.STRUCTURED_REQUEST_TIMEOUT_SECONDS)

    def test_engine_subprocess_receives_job_identity(self):
        import pipeline
        with patch.object(pipeline.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as process:
            self.assertTrue(pipeline.run_engine(analysis_id=ID))
        self.assertEqual(process.call_args.kwargs["env"]["STRUCTURED_ANALYSIS_ID"], ID)
        self.assertEqual(process.call_args.kwargs["env"]["ANALYSIS_ENGINE_MODE"], "structured")

    def test_switch_returns_to_untouched_legacy_and_repeated_generation_changes_id(self):
        self.publish()
        first = capture_current(self.root)
        self.publish()
        second = capture_current(self.root)
        self.assertEqual(first.digest, second.digest)
        self.assertNotEqual(first.file_id, second.file_id)
        with patch.dict(os.environ, {"ANALYSIS_ENGINE_MODE": "legacy"}):
            self.assertEqual(capture_current(self.root).text, "Legacy preserved")
        self.assertEqual(capture_current(self.root).path, second.path)

    def test_corrupt_json_or_pointer_cannot_fall_back_to_legacy(self):
        self.assertEqual(capture_current(self.root).status, "error")
        manifest = self.publish()
        result = self.root / "structured/generations" / manifest["generation"] / "result.json"
        result.write_text("{}", encoding="utf-8")
        self.assertEqual(capture_current(self.root).status, "error")

    def test_runner_publishes_only_after_all_validated_tasks(self):
        def factory(bundle, llm, preparation):
            tasks = [SimpleNamespace(output=SimpleNamespace(raw=json.dumps(value))) for value in payloads(preparation)]
            return SimpleNamespace(kickoff=lambda: None), tasks
        manifest, _ = run_structured(TEXT, SimpleNamespace(model="offline"), self.root, analysis_id=ID, factory=factory)
        self.assertEqual(manifest["analysis_id"], ID)
        self.assertEqual(load_current(self.root / "structured")[1]["counts"]["high"], 1)
        self.assertEqual(self.legacy.read_text(), "Legacy preserved")

    def test_runner_failure_keeps_current_publication(self):
        self.publish()
        previous = capture_current(self.root)
        def factory(*args, **kwargs):
            def fail():
                raise RuntimeError("synthetic failure")
            return SimpleNamespace(kickoff=fail), []
        with self.assertRaises(RuntimeError):
            run_structured(TEXT, SimpleNamespace(model="offline"), self.root, factory=factory)
        self.assertEqual(capture_current(self.root).file_id, previous.file_id)

    def test_flask_state_catalog_detail_and_legacy_link_share_generation(self):
        self.publish()
        web = importlib.import_module("dashboard.app")
        history = self.root / "historial"
        history.mkdir()
        (history / "reporte_20261006_120000.md").write_bytes(capture_current(self.root).content)
        with patch.object(web, "REPORT_PATH", self.root), patch.object(web, "HISTORIAL", self.root / "historial"), \
                patch.object(web, "LOG_PATH", str(self.root / "absent.log")):
            client = web.app.test_client()
            with patch.object(web, "capture_current_details", wraps=web.capture_current_details) as current:
                snapshot = web._snapshot_estado()
            self.assertEqual(current.call_count, 1)
            self.assertEqual(len(snapshot["threats"]), 1)
            catalog = client.get("/api/v1/reportes").get_json()["data"]
            self.assertEqual(len(catalog), 1)
            self.assertEqual(catalog[0]["id"], capture_current(self.root).file_id)
            detail = client.get("/api/v1/reportes/" + catalog[0]["id"])
            self.assertEqual(detail.status_code, 200)
            self.assertEqual(detail.get_json()["data"]["markdown"], capture_current(self.root).text)
            self.assertIn('Línea del log', detail.get_json()["data"]["display_markdown"])
            state = client.get('/api/v1/estado').get_json()['data']['threats'][0]
            self.assertIsNotNone(state['event_time_start'])
            self.assertEqual(state['event_time_start'], state['event_time_end'])
            self.assertEqual(client.get("/report/reporte_seguridad.md").status_code, 200)
            (self.root / "structured/current.json").write_text("{}", encoding="utf-8")
            remaining = client.get("/api/v1/reportes").get_json()["data"]
            self.assertEqual(len(remaining), 1)
            self.assertFalse(remaining[0]["current"])
            self.assertEqual(client.get("/report/reporte_seguridad.md").status_code, 404)

    def test_coordinator_archives_and_notifies_same_generation(self):
        import pipeline
        store = JobStore(self.root / "jobs.sqlite3")
        job, _ = store.enqueue("manual", "synthetic")
        store.claim()
        notified = []
        def engine():
            self.publish(job["id"])
            return True
        with patch.object(pipeline, "REPORT_PATH", self.root):
            pipeline.execute_job(store, job, sync=lambda: True, engine=engine,
                                 notify=lambda _store, _id, text: notified.append(text))
        current = capture_current(self.root)
        self.assertEqual(store.get(job["id"])["status"], "succeeded")
        self.assertEqual(store.get(job["id"])["report_id"], current.file_id)
        self.assertEqual(notified, [current.text])
        self.assertEqual(next((self.root / "historial").glob("*.md")).read_text(encoding="utf-8"), current.text)

    def test_bounded_input_rejects_large_and_invalid_utf8(self):
        path = self.root / "input.log"
        path.write_bytes(b"x" * (1024 * 1024 + 1))
        with self.assertRaises(ContractError):
            read_input(path)
        path.write_bytes(b"\xff")
        with self.assertRaises(ContractError):
            read_input(path)

    def test_backup_includes_generation_json_but_excludes_unrelated_files(self):
        from scripts.backup_operational import collect_sources
        reports = self.root / "reports"
        prepared = prepare_evidence(TEXT, ID)
        manifest = publish(reports / "structured", prepared, *payloads(prepared), model="offline", prompt_version="test")
        (reports / "structured/secret.json").write_text("not a report")
        paths, _ = collect_sources(self.root, ("legacy",))
        self.assertIn("reports/structured/current.json", paths)
        for name in ("manifest.json", "result.json", "report.md"):
            self.assertIn("reports/structured/generations/" + manifest["generation"] + "/" + name, paths)
        self.assertNotIn("reports/structured/secret.json", paths)

    def test_backup_restores_coherent_generation_to_isolated_directory(self):
        from scripts.backup_operational import backup
        prepared = prepare_evidence(TEXT, ID)
        publish(self.root / "reports/structured", prepared, *payloads(prepared), model="offline", prompt_version="test")
        destination, manifest = backup(self.root, ("legacy",))
        self.assertTrue(manifest["verified"])
        restored = destination / "restore-check" / "reports/structured"
        self.assertEqual(load_current(restored)[1]["counts"]["high"], 1)

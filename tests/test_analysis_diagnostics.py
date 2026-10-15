"""Metadata diagnostics redact by construction, including adversarial model/exception text."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from agents.analysis_diagnostics import AnalysisDiagnostics, safe_exception
from agents.evidence_contracts import ContractError
from agents.structured_engine import run_structured

SECRET = "synthetic-credential-never-log"


class DiagnosticsTests(TestCase):
    def test_response_contents_and_exception_messages_are_never_stored(self):
        diagnostic = AnalysisDiagnostics()
        for response in ("", SECRET, None, json.dumps({"unexpected": SECRET})):
            identifier = diagnostic.begin_call("detection")
            diagnostic.finish_call(identifier, response)
        error = ValueError(SECRET)
        error.__cause__ = RuntimeError(SECRET)
        diagnostic.failure(error)
        snapshot = diagnostic.snapshot()
        self.assertNotIn(SECRET, json.dumps(snapshot))
        statuses = [event["output_status"] for event in snapshot["events"] if event["event"] == "call_returned"]
        self.assertEqual(statuses, ["json_invalid", "json_invalid", "non_text", "json_valid"])
        self.assertEqual(snapshot["events"][-1]["error_types"], ["ValueError", "RuntimeError"])

    def test_schema_errors_exclude_values_locations_and_context(self):
        class ValidationError(Exception):
            def errors(self, **kwargs):
                self.kwargs = kwargs
                return [{"type": "missing", "loc": [SECRET], "input": SECRET},
                        {"type": SECRET, "ctx": {"secret": SECRET}}]
        error = ValidationError(SECRET)
        class Schema:
            @staticmethod
            def model_validate(_payload):
                raise error
        diagnostic = AnalysisDiagnostics()
        identifier = diagnostic.begin_call("classification")
        diagnostic.finish_call(identifier, json.dumps({"secret": SECRET}), Schema)
        event = diagnostic.snapshot()["events"][-1]
        self.assertEqual(event["output_status"], "schema_invalid")
        self.assertEqual(event["validation_types"], ["missing", "validation_error"])
        self.assertFalse(any(error.kwargs.values()))
        self.assertNotIn(SECRET, json.dumps(diagnostic.snapshot()))

    def test_contract_codes_are_whitelisted_and_unknown_stage_is_hidden(self):
        diagnostic = AnalysisDiagnostics()
        diagnostic.phase(SECRET)
        diagnostic.guard("detection", ContractError("invalid_evidence_reference"))
        diagnostic.guard("detection", ContractError("empty_detection_with_observed_indicators"))
        diagnostic.guard(SECRET, ContractError(SECRET))
        self.assertEqual(diagnostic.snapshot()["stage"], "unknown")
        self.assertEqual(diagnostic.snapshot()["events"][1]["contract_code"], "invalid_evidence_reference")
        self.assertEqual(diagnostic.snapshot()["events"][2]["contract_code"], "empty_detection_with_observed_indicators")
        self.assertNotIn(SECRET, json.dumps(diagnostic.snapshot()))

    def test_checkpoint_bounds_and_detached_snapshot(self):
        checkpoints = []
        diagnostic = AnalysisDiagnostics(checkpoint=checkpoints.append)
        for _ in range(110):
            diagnostic.phase("detection")
        snapshot = diagnostic.snapshot()
        self.assertEqual(len(snapshot["events"]), 100)
        self.assertEqual(snapshot["dropped_events"], 10)
        snapshot["events"].clear()
        self.assertEqual(len(diagnostic.snapshot()["events"]), 100)
        self.assertEqual(checkpoints[-1]["dropped_events"], 10)

    def test_exception_chain_cycles_and_unknown_types_are_bounded(self):
        class PrivateError(Exception):
            pass
        error = PrivateError(SECRET)
        error.__cause__ = error
        summary = safe_exception(error)
        self.assertEqual(summary["error_types"], ["other_exception"])
        self.assertEqual(summary["frames"], [])
        self.assertNotIn(SECRET, json.dumps(summary))

    def test_http_status_survives_wrapped_sdk_errors_without_response_content(self):
        import httpx
        import litellm
        request = httpx.Request("POST", "https://example.invalid/" + SECRET,
                                headers={"Authorization": SECRET})
        response = httpx.Response(400, request=request, json={"error": SECRET})
        cause = httpx.HTTPStatusError(SECRET, request=request, response=response)
        error = litellm.BadRequestError(message=SECRET, model="groq/synthetic", llm_provider="groq")
        error.__cause__ = cause
        wrapper = RuntimeError(SECRET)
        wrapper.__cause__ = error
        summary = safe_exception(wrapper)
        self.assertEqual(summary["error_types"], ["RuntimeError", "BadRequestError", "HTTPStatusError"])
        self.assertEqual(summary["http_status"], 400)
        diagnostic = AnalysisDiagnostics()
        diagnostic.failure(wrapper)
        self.assertEqual(diagnostic.snapshot()["events"][-1]["http_status"], 400)
        self.assertNotIn(SECRET, json.dumps(diagnostic.snapshot()))

    def test_only_numeric_error_status_is_retained_and_httpx_response_is_supported(self):
        import httpx
        request = httpx.Request("POST", "https://example.invalid/" + SECRET)
        response = httpx.Response(429, request=request, text=SECRET)
        error = httpx.HTTPStatusError(SECRET, request=request, response=response)
        self.assertEqual(safe_exception(error)["http_status"], 429)
        for status in (True, False, "401", SECRET, 200, 299, 600, 999, 400.0, None):
            with self.subTest(status=status):
                error = RuntimeError(SECRET)
                error.status_code = status
                error.response = SimpleNamespace(status_code=status, body=SECRET)
                self.assertNotIn("http_status", safe_exception(error))
                self.assertNotIn(SECRET, json.dumps(safe_exception(error)))

    def test_broken_exception_properties_do_not_hide_cause_or_mask_failure(self):
        class PrivateError(Exception):
            @property
            def status_code(self):
                raise ValueError(SECRET)
            @property
            def response(self):
                raise ValueError(SECRET)
        cause = RuntimeError(SECRET)
        cause.response = SimpleNamespace(status_code=503)
        error = PrivateError(SECRET)
        error.__cause__ = cause
        cause.__cause__ = error
        summary = safe_exception(error)
        self.assertEqual(summary["error_types"], ["other_exception", "RuntimeError"])
        self.assertEqual(summary["http_status"], 503)
        self.assertNotIn(SECRET, json.dumps(summary))

    def test_runner_distinguishes_preparation_execution_and_publication_failures(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            diagnostic = AnalysisDiagnostics()
            with self.assertRaises(ContractError):
                run_structured("", SimpleNamespace(model="offline"), root, diagnostics=diagnostic)
            self.assertEqual(diagnostic.snapshot()["stage"], "preparation")
            self.assertFalse((root / "structured/current.json").exists())
            def factory(_bundle, _llm, preparation, diagnostics):
                return SimpleNamespace(kickoff=lambda: None), []
            diagnostic = AnalysisDiagnostics()
            with patch("agents.structured_engine.publish", side_effect=OSError(SECRET)), self.assertRaises(OSError):
                run_structured('192.0.2.1 - - [06/Oct/2026:12:00:00 +0000] "GET / HTTP/1.1" 200 1',
                               SimpleNamespace(model="offline"), root, factory=factory, diagnostics=diagnostic)
            self.assertEqual(diagnostic.snapshot()["stage"], "publication")
            self.assertNotIn(SECRET, json.dumps(diagnostic.snapshot()))

    def test_evaluator_construction_failure_still_writes_safe_checkpoint(self):
        from scripts.evaluate_structured_openrouter import evaluate
        with TemporaryDirectory() as temporary:
            with patch("scripts.evaluate_structured_openrouter._evaluate", side_effect=ValueError(SECRET)):
                report = evaluate(Path(temporary))
            persisted = json.loads((Path(temporary) / "diagnostics.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "failed")
            self.assertEqual(persisted["stage"], "configuration")
            self.assertEqual(persisted["events"][-1]["error_types"], ["ValueError"])
            self.assertNotIn(SECRET, json.dumps(report))

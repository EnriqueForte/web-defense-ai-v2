"""Real CrewAI tasks with scripted responses; publication only in temporary roots."""
from copy import deepcopy
import contextlib
import io
import json
import os
import inspect
import socket
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    original_connect = socket.socket.connect
    def internal_socketpair_only(sock, address):
        caller = inspect.currentframe().f_back
        if caller.f_code.co_name == "socketpair" and caller.f_globals.get("__name__") == "socket":
            return original_connect(sock, address)
        raise AssertionError("Network prohibited")
    with patch("dotenv.load_dotenv", return_value=False), \
         patch.dict(os.environ, {"CREWAI_TRACING_ENABLED": "false", "OTEL_SDK_DISABLED": "true",
                                 "LITELLM_LOCAL_MODEL_COST_MAP": "True", "LITELLM_MODE": "PRODUCTION",
                                 "CREWAI_STORAGE_DIR": str(ROOT / ".local-state/structured-prototype"),
                                 "GROQ_API_KEY": "", "OPENROUTER_API_KEY": ""}), \
         patch("socket.socket.connect", new=internal_socketpair_only), \
         patch("socket.create_connection", side_effect=AssertionError("Network prohibited")):
        from crewai.llms.base_llm import BaseLLM
        from crewai.events.event_bus import crewai_event_bus
        from pydantic import Field
        from agents.evidence_contracts import build_evidence
        from agents.structured_prototype import build_prototype, result_from_tasks
        from agents.evidence_preparation import prepare_evidence

        class ScriptedLLM(BaseLLM):
            responses: list[str]
            calls: int = 0
            messages_seen: list = Field(default_factory=list)

            def call(self, messages, **kwargs):
                self.calls += 1
                self.messages_seen.append(messages)
                if not self.responses:
                    raise AssertionError("Unexpected additional model call")
                return "Final Answer: " + self.responses.pop(0)

            def supports_function_calling(self):
                return False

        analysis_id = "a" * 32
        bundle = build_evidence('192.0.2.1 - - [06/Oct/2026:12:00:00 +0200] '
            '"GET /?q=UNION+SELECT HTTP/1.1" 200 1', analysis_id)
        detection = {"schema_version": "1", "analysis_id": analysis_id, "candidates": [
            {"candidate_id": "c_1", "evidence_ids": [bundle.items[0].evidence_id],
             "pattern": "sql_injection", "reason": "Observed token"}]}
        classification = {"schema_version": "1", "analysis_id": analysis_id, "classifications": [
            {"candidate_id": "c_1", "severity": "high", "state": "requires_investigation", "reason": "Payload only"}]}
        narrative = {"schema_version": "1", "analysis_id": analysis_id, "summary": "Review observed request",
                     "recommendations": [{"candidate_id": "c_1", "text": "Review validation"}]}
        def execute(responses, preparation=None):
            llm = ScriptedLLM(model="scripted-offline", responses=[json.dumps(value) for value in responses])
            crew, tasks = build_prototype(bundle, llm, preparation=preparation)
            assert tasks[1].context == [tasks[0]] and tasks[2].context == [tasks[0], tasks[1]]
            assert all(task.output_file is None and task.guardrail_max_retries == 1 for task in tasks)
            assert all(not agent.allow_delegation and not agent.tools for agent in crew.agents)
            assert crew._task_output_handler.__class__.__name__ == "MemoryOutputHandler"
            return llm, crew, tasks

        # Suppress framework logs; publication below is restricted to a temporary root.
        with patch.object(crewai_event_bus, "emit", return_value=None), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            llm, crew, tasks = execute([detection, classification, narrative])
            crew.kickoff()
            result = result_from_tasks(bundle, tasks, model="scripted-offline")
            assert llm.calls == 3 and result["counts"]["high"] == 1
            assert all(task.output.pydantic is not None for task in tasks)
            assert "c_1" in json.dumps(llm.messages_seen[1])
            assert "requires_investigation" in json.dumps(llm.messages_seen[2])

            invalid = deepcopy(detection)
            invalid["candidates"][0]["evidence_ids"] = ["e_foreign"]
            repaired_llm, repaired_crew, repaired_tasks = execute([invalid, detection, classification, narrative])
            repaired_crew.kickoff()
            assert repaired_llm.calls == 4
            assert result_from_tasks(bundle, repaired_tasks, model="scripted-offline")["counts"]["high"] == 1

            failed_llm, failed_crew, failed_tasks = execute([invalid, invalid])
            try:
                failed_crew.kickoff()
            except Exception:
                assert failed_llm.calls == 2
                assert failed_tasks[1].output is None and failed_tasks[2].output is None
            else:
                raise AssertionError("Invalid references were accepted")
            prepared = prepare_evidence(bundle.items[0].raw, analysis_id)
            observed_llm, observed_crew, observed_tasks = execute([detection, classification, narrative], prepared)
            observed_crew.kickoff()
            observed_result = result_from_tasks(bundle, observed_tasks, model="scripted-offline", preparation=prepared)
            assert observed_result["preparation"]["indicators"][bundle.items[0].evidence_id] == ["sql_injection"]
            assert observed_llm.calls == 3
            critical = deepcopy(classification)
            critical["classifications"][0]["severity"] = "critical"
            unsupported_llm, unsupported_crew, unsupported_tasks = execute([detection, critical, critical], prepared)
            try:
                unsupported_crew.kickoff()
            except Exception:
                assert unsupported_llm.calls == 3 and unsupported_tasks[2].output is None
            else:
                raise AssertionError("Unsupported critical classification was accepted")
            # Exercise the real LiteLLM adapter with a synthetic credential and no network.
            from crewai import LLM
            from litellm import ModelResponse
            from pydantic import BaseModel
            from agents.analysis_diagnostics import AnalysisDiagnostics
            class Probe(BaseModel):
                summary: str
            delegate = LLM(model="openrouter/openrouter/free", is_litellm=True,
                           api_key="synthetic-test-key", base_url="https://openrouter.ai/api/v1")
            probe_diagnostic = AnalysisDiagnostics()
            probe_crew, probe_tasks = build_prototype(bundle, delegate, preparation=prepared, diagnostics=probe_diagnostic)
            response = ModelResponse(choices=[{"index": 0, "finish_reason": "stop",
                "message": {"role": "assistant", "content": '{"summary":"synthetic"}'}}],
                model="vendor/synthetic-model:free",
                usage={"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2,
                       "completion_tokens_details": {"reasoning_tokens": 0}})
            from scripts.evaluate_structured_openrouter import capture_completion_metadata
            with patch("litellm.completion", return_value=response) as completion, \
                    patch("crewai.utilities.internal_instructor.InternalInstructor.to_pydantic",
                          side_effect=AssertionError("Unconfigured conversion call prohibited")), \
                    capture_completion_metadata(probe_diagnostic, secrets=("synthetic-test-key",)):
                output = probe_crew.agents[0].llm.call([{"role": "user", "content": "Synthetic probe"}],
                                                     response_model=Probe, from_task=probe_tasks[0])
            assert output == '{"summary":"synthetic"}' and completion.call_count == 1
            assert completion.call_args.kwargs["api_key"] == "synthetic-test-key"
            assert completion.call_args.kwargs["base_url"] == "https://openrouter.ai/api/v1"
            assert probe_diagnostic.snapshot()["events"][-1]["output_status"] == "schema_valid"
            assert probe_diagnostic.snapshot()["stage"] == "detection"
            assert "synthetic-test-key" not in json.dumps(probe_diagnostic.snapshot())
            # Expose the existing identifier contract to the model; never normalize invalid IDs.
            candidate_schema = probe_tasks[0].output_pydantic.model_json_schema()["$defs"]["Candidate"]
            assert candidate_schema["properties"]["candidate_id"]["pattern"] == r"^c_[a-zA-Z0-9_-]{1,60}$"
            assert "c_1, c_2, c_3" in probe_tasks[0].description
            from pydantic import ValidationError
            wrong_id = deepcopy(detection)
            wrong_id["candidates"][0]["candidate_id"] = "1"
            try:
                probe_tasks[0].output_pydantic.model_validate(wrong_id)
            except ValidationError:
                pass
            else:
                raise AssertionError("Invalid candidate identifier was accepted by schema")
            completed = next(event for event in probe_diagnostic.snapshot()["events"] if event["event"] == "completion_returned")
            assert completed["response_model"] == "vendor/synthetic-model:free"
            assert completed["finish_reason"] == "stop" and completed["usage"]["reasoning_tokens"] == 0
            # Empty content with a length limit is visible before CrewAI converts None to ''.
            empty_response = ModelResponse(model="vendor/synthetic-model:free", choices=[{
                "index": 0, "finish_reason": "length", "message": {
                    "role": "assistant", "content": None, "reasoning_content": "synthetic-private-reasoning"}}],
                usage={"prompt_tokens": 1, "completion_tokens": 2048, "total_tokens": 2049,
                       "completion_tokens_details": {"reasoning_tokens": 2048}})
            empty_metadata = AnalysisDiagnostics()
            empty_metadata.begin_call("detection")
            with patch("litellm.completion", return_value=empty_response) as original:
                with capture_completion_metadata(empty_metadata, secrets=("synthetic-test-key",)):
                    import litellm
                    assert litellm.completion(model="openrouter/openrouter/free", max_tokens=2048,
                        api_key="synthetic-test-key", messages=[{"role": "user", "content": "synthetic-private-prompt"}]) is empty_response
                assert litellm.completion is original
            metadata = empty_metadata.snapshot()["events"][-1]
            assert metadata["finish_reason"] == "length" and metadata["reasoning_present"]
            assert metadata["usage"]["reasoning_tokens"] == 2048 and not metadata["content_present"]
            assert "synthetic-private-reasoning" not in json.dumps(empty_metadata.snapshot())
            assert "synthetic-private-prompt" not in json.dumps(empty_metadata.snapshot())
            # Restore the real callable even if the SDK raises; don't invent completion metadata.
            failure_metadata = AnalysisDiagnostics()
            with patch("litellm.completion", side_effect=ValueError("synthetic-test-key")) as original:
                try:
                    with capture_completion_metadata(failure_metadata):
                        litellm.completion()
                except ValueError:
                    pass
                else:
                    raise AssertionError("SDK exception was swallowed")
                assert litellm.completion is original and not failure_metadata.snapshot()["events"]
            from agents.structured_engine import run_structured
            from dashboard.services.active_report import capture_current
            with TemporaryDirectory() as temporary, patch.dict(os.environ, {"ANALYSIS_ENGINE_MODE": "structured"}):
                report_root = Path(temporary)
                legacy = report_root / "reporte_seguridad.md"
                legacy.write_text("Legacy preserved", encoding="utf-8")
                integrated_llm = ScriptedLLM(model="scripted-offline", responses=[
                    json.dumps(value) for value in (detection, classification, narrative)])
                manifest, _ = run_structured(bundle.items[0].raw, integrated_llm, report_root,
                                             analysis_id=analysis_id, config={})
                published = capture_current(report_root)
                assert integrated_llm.calls == 3 and published.status == "available"
                assert manifest["generation"] in str(published.path)
                from dashboard.app import parsear_amenazas
                assert len(parsear_amenazas(published.text)) == 1
                with patch.dict(os.environ, {"ANALYSIS_ENGINE_MODE": "legacy"}):
                    assert capture_current(report_root).text == "Legacy preserved"
                assert capture_current(report_root).file_id == published.file_id
                # Actual CrewAI path for an empty provider response; no live connection.
                class EmptyLLM(BaseLLM):
                    calls: int = 0
                    def call(self, messages, **kwargs):
                        self.calls += 1
                        return ""
                    def supports_function_calling(self):
                        return False
                empty_llm = EmptyLLM(model="scripted-empty")
                diagnostic = AnalysisDiagnostics()
                try:
                    run_structured(bundle.items[0].raw, empty_llm, report_root,
                                   analysis_id=analysis_id, config={}, diagnostics=diagnostic)
                except ValueError:
                    snapshot = diagnostic.snapshot()
                    assert snapshot["stage"] == "detection"
                    returned = [event for event in snapshot["events"] if event["event"] == "call_returned"]
                    assert returned and all(event["characters"] == 0 for event in returned)
                    assert any(frame["file"] == "agent_utils.py" for frame in snapshot["events"][-1]["frames"])
                    assert capture_current(report_root).file_id == published.file_id
                else:
                    raise AssertionError("Empty response was accepted")
                bad_llm = ScriptedLLM(model="scripted-invalid", responses=[json.dumps(invalid), json.dumps(invalid)])
                bad_diagnostic = AnalysisDiagnostics()
                try:
                    run_structured(bundle.items[0].raw, bad_llm, report_root, analysis_id=analysis_id,
                                   config={}, diagnostics=bad_diagnostic)
                except Exception:
                    events = bad_diagnostic.snapshot()["events"]
                    assert any(event.get("contract_code") == "invalid_evidence_reference" for event in events)
                    assert not any(event["stage"] == "classification" for event in events)
                    assert capture_current(report_root).file_id == published.file_id
                else:
                    raise AssertionError("Foreign evidence was accepted")
                duplicate = deepcopy(detection)
                duplicate["candidates"].append(deepcopy(duplicate["candidates"][0]))
                duplicate_llm = ScriptedLLM(model="scripted-duplicate", responses=[json.dumps(duplicate), json.dumps(duplicate)])
                duplicate_diagnostic = AnalysisDiagnostics()
                try:
                    run_structured(bundle.items[0].raw, duplicate_llm, report_root, analysis_id=analysis_id,
                                   config={}, diagnostics=duplicate_diagnostic)
                except Exception:
                    assert duplicate_llm.calls == 2
                    assert any(event.get("contract_code") == "duplicate_or_invalid_candidate"
                               for event in duplicate_diagnostic.snapshot()["events"])
                    assert capture_current(report_root).file_id == published.file_id
                else:
                    raise AssertionError("Duplicate candidate identifier was accepted")
                # The real false-positive shape is rejected, then a supported correction passes.
                normal_text = '192.0.2.1 - - [06/Oct/2026:12:00:01 +0200] "GET /index.html HTTP/1.1" 200 1'
                mixed_text = bundle.items[0].raw + "\n" + normal_text
                mixed_prepared = prepare_evidence(mixed_text, analysis_id)
                valid_detection = deepcopy(detection)
                valid_detection["candidates"][0]["evidence_ids"] = [mixed_prepared.bundle.items[0].evidence_id]
                false_positive = deepcopy(valid_detection)
                false_positive["candidates"].append({"candidate_id": "c_2", "pattern": "other",
                    "reason": "Unsupported normal request", "evidence_ids": [mixed_prepared.bundle.items[1].evidence_id]})
                repaired = ScriptedLLM(model="scripted-false-positive", responses=[json.dumps(value) for value in
                    (false_positive, valid_detection, classification, narrative)])
                repaired_diagnostic = AnalysisDiagnostics()
                run_structured(mixed_text, repaired, report_root, analysis_id=analysis_id, config={}, diagnostics=repaired_diagnostic)
                from dashboard.services.structured_publication import load_current
                result = load_current(report_root / "structured")[1]
                assert repaired.calls == 4 and len(result["findings"]) == 1
                assert any(event.get("contract_code") == "other_without_observation"
                           for event in repaired_diagnostic.snapshot()["events"])
                # Nonempty normal input can finish with no candidates and no invented threat.
                empty_detection = {"schema_version": "1", "analysis_id": analysis_id, "candidates": []}
                normal_llm = ScriptedLLM(model="scripted-normal", responses=[json.dumps(empty_detection)])
                normal_diagnostic = AnalysisDiagnostics()
                run_structured(normal_text, normal_llm, report_root, analysis_id=analysis_id, config={}, diagnostics=normal_diagnostic)
                result = load_current(report_root / "structured")[1]
                assert normal_llm.calls == 1 and not result["findings"] and sum(result["counts"].values()) == 0
                assert normal_diagnostic.calls == 1
                assert [event["stage"] for event in normal_diagnostic.snapshot()["events"] if event["event"] == "local_stage"] == ["classification", "narrative"]
                assert [event["stage"] for event in normal_diagnostic.snapshot()["events"] if event["event"] == "guard" and event["accepted"]] == ["detection", "classification", "narrative"]
                assert not parsear_amenazas(capture_current(report_root).text)
                assert legacy.read_text(encoding="utf-8") == "Legacy preserved"
                # SDK-level accounting has exactly one completion, even though all Tasks finish.
                from agents.usage_summary import summarize_usage
                sdk_normal = LLM(model="openrouter/openrouter/free", is_litellm=True,
                                 api_key="synthetic-test-key", base_url="https://openrouter.ai/api/v1",
                                 timeout=60, max_tokens=8192, additional_params={"max_retries": 0})
                normal_response = ModelResponse(model="vendor/synthetic-model:free", choices=[{
                    "index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": json.dumps(empty_detection)}}],
                    usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30,
                           "completion_tokens_details": {"reasoning_tokens": 0}})
                sdk_diagnostic = AnalysisDiagnostics()
                with patch("litellm.completion", return_value=normal_response) as completed, \
                        capture_completion_metadata(sdk_diagnostic, secrets=("synthetic-test-key",)):
                    _manifest, sdk_crew = run_structured(normal_text, sdk_normal, report_root,
                                                        analysis_id=analysis_id, config={}, diagnostics=sdk_diagnostic)
                usage = summarize_usage(sdk_diagnostic.snapshot(), sdk_normal.get_token_usage_summary().model_dump())
                assert completed.call_count == 1 and sdk_diagnostic.calls == 1
                assert usage["usage"]["complete"] and usage["usage"]["total_tokens"] == 30
                assert not usage["usage_discrepancies"]
                assert all(task.output.pydantic is not None for task in sdk_crew.tasks)
                assert load_current(report_root / "structured")[1]["narrative_source"] == "python_scope"
                # Incomplete evidence also keeps a scope warning, not a benign verdict.
                incomplete_llm = ScriptedLLM(model="scripted-incomplete", responses=[json.dumps(empty_detection)])
                run_structured("uninterpretable synthetic record", incomplete_llm, report_root,
                               analysis_id=analysis_id, config={})
                incomplete_result = load_current(report_root / "structured")[1]
                assert incomplete_llm.calls == 1 and "no permite descartar" in incomplete_result["narrative"]["summary"]
        print("CrewAI/LiteLLM aislados: 17 escenarios aprobados, incluida ruta sin candidatos con una sola llamada y contabilidad SDK; sin proveedor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

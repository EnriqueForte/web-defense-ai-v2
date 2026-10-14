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
            # A contract-valid but invented narrative must not reach publication.
            invented_narrative = deepcopy(narrative)
            invented_narrative['summary'] = 'SUBSTRING confirmed exploitation'
            invented_narrative['recommendations'][0]['text'] = 'Multiple requests containing SQL patterns'
            grounded_llm, grounded_crew, grounded_tasks = execute([detection, classification, invented_narrative], prepared)
            grounded_crew.kickoff()
            grounded_result = result_from_tasks(bundle, grounded_tasks, model='scripted-offline', preparation=prepared)
            assert grounded_llm.calls == 3 and all(task.output.pydantic is not None for task in grounded_tasks)
            assert grounded_result['narrative_source'] == 'python_validated_facts'
            assert 'SUBSTRING' not in grounded_result['narrative']['summary']
            assert 'consultas parametrizadas' in grounded_result['narrative']['recommendations'][0]['text']
            assert 'Multiple requests' not in grounded_result['narrative']['recommendations'][0]['text']
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
                           api_key="synthetic-test-key", base_url="https://openrouter.ai/api/v1",
                           additional_params={"max_retries": 0, "extra_body": {
                               "provider": {"order": ["synthetic-provider"]}}})
            original_parameters = delegate.additional_params
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
            assert completion.call_args.kwargs["response_format"] == {"type": "json_object"}
            assert completion.call_args.kwargs["extra_body"]["provider"]["require_parameters"] is True
            assert completion.call_args.kwargs["extra_body"]["provider"]["order"] == ["synthetic-provider"]
            assert delegate.additional_params is original_parameters
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
            with patch('litellm.completion', side_effect=RuntimeError('synthetic-transport-error')):
                try:
                    probe_crew.agents[0].llm.call([{'role': 'user', 'content': 'Synthetic JSON probe'}],
                                                response_model=Probe, from_task=probe_tasks[0])
                except Exception:
                    assert delegate.additional_params is original_parameters
                    assert original_parameters == {'max_retries': 0, 'extra_body': {
                        'provider': {'order': ['synthetic-provider']}}}
                else:
                    raise AssertionError('Transport exception was swallowed')
            # The real evaluator wraps LLM to bound calls. That wrapper must
            # expose JSON routing and forward each temporary parameter set.
            from scripts.evaluate_structured_openrouter import bounded_evaluation_llm
            bounded = bounded_evaluation_llm(delegate)
            bounded_parameters = bounded.additional_params
            bounded_crew, bounded_tasks = build_prototype(bundle, bounded, preparation=prepared)
            with patch('litellm.completion', return_value=response) as bounded_completion:
                for _ in range(6):
                    output = bounded_crew.agents[0].llm.call([{'role': 'user', 'content': 'Synthetic bounded probe'}],
                                                          response_model=Probe, from_task=bounded_tasks[0])
                    assert output == '{"summary":"synthetic"}'
                    arguments = bounded_completion.call_args.kwargs
                    assert arguments['response_format'] == {'type': 'json_object'}
                    assert arguments['extra_body']['provider']['require_parameters'] is True
                    assert arguments['extra_body']['provider']['order'] == ['synthetic-provider']
                    assert arguments['api_key'] == 'synthetic-test-key'
                    assert arguments['base_url'] == 'https://openrouter.ai/api/v1'
                    assert arguments['max_retries'] == 0
                    assert delegate.additional_params is original_parameters
                    assert bounded.additional_params is bounded_parameters
                try:
                    bounded_crew.agents[0].llm.call([{'role': 'user', 'content': 'Prohibited seventh probe'}],
                                                  from_task=bounded_tasks[0])
                except RuntimeError as error:
                    assert str(error) == 'evaluation_call_budget'
                else:
                    raise AssertionError('Evaluator exceeded its logical call budget')
                assert bounded.calls == bounded_completion.call_count == 6
            bounded_failure = bounded_evaluation_llm(delegate)
            failed_parameters = bounded_failure.additional_params
            failed_crew, failed_tasks = build_prototype(bundle, bounded_failure, preparation=prepared)
            with patch('litellm.completion', side_effect=RuntimeError('synthetic-transport-error')):
                try:
                    failed_crew.agents[0].llm.call([{'role': 'user', 'content': 'Synthetic bounded failure'}],
                                                from_task=failed_tasks[0])
                except Exception:
                    assert bounded_failure.calls == 1
                    assert bounded_failure.additional_params is failed_parameters
                    assert delegate.additional_params is original_parameters
                else:
                    raise AssertionError('Bounded transport exception was swallowed')
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
                # Invalid classification output must reach both strict guards,
                # without CrewAI extracting partial JSON or making conversion calls.
                classification_secret = 'synthetic-classification-content-never-persist'
                malformed = 'prose {"private": "' + classification_secret + '"}'
                recovered = ScriptedLLM(model='scripted-classification-retry', responses=[
                    json.dumps(detection), malformed, json.dumps(classification), json.dumps(narrative)])
                recovered_diagnostic = AnalysisDiagnostics()
                with patch('crewai.task.convert_to_model', side_effect=AssertionError('Conversion call prohibited')):
                    run_structured(bundle.items[0].raw, recovered, report_root,
                                   analysis_id=analysis_id, config={}, diagnostics=recovered_diagnostic)
                assert recovered.calls == 4
                events = recovered_diagnostic.snapshot()['events']
                assert len([event for event in events if event.get('stage') == 'classification'
                            and event.get('contract_code') == 'invalid_json']) == 1
                assert any(event.get('stage') == 'classification' and event.get('accepted') for event in events)
                previous_publication = capture_current(report_root).file_id
                for bad_classification in (malformed, json.dumps({'schema_version': '1', 'analysis_id': analysis_id,
                                                                 'classifications': [{'unexpected': 'field'}]})):
                    failed_classification = ScriptedLLM(model='scripted-classification-invalid', responses=[
                        json.dumps(detection), bad_classification, bad_classification])
                    failed_diagnostic = AnalysisDiagnostics()
                    try:
                        with patch('crewai.task.convert_to_model', side_effect=AssertionError('Conversion call prohibited')):
                            run_structured(bundle.items[0].raw, failed_classification, report_root,
                                           analysis_id=analysis_id, config={}, diagnostics=failed_diagnostic)
                    except Exception as error:
                        assert type(error).__name__ != 'ValidationError'
                        assert failed_classification.calls == 3
                        events = failed_diagnostic.snapshot()['events']
                        rejected = [event for event in events if event.get('stage') == 'classification'
                                    and event.get('event') == 'guard' and not event.get('accepted')]
                        assert len(rejected) == 2
                        assert not any(event.get('stage') in {'narrative', 'publication'} for event in events)
                        assert classification_secret not in json.dumps(failed_diagnostic.snapshot())
                        assert capture_current(report_root).file_id == previous_publication
                    else:
                        raise AssertionError('Invalid classification was published')
                # Restore the test's reference after the successful retry publication.
                published = capture_current(report_root)
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
                # Selected indicators cannot be silently published as an empty detection.
                corrected_empty = ScriptedLLM(model="scripted-empty-corrected", responses=[json.dumps(value) for value in
                    (empty_detection, valid_detection, classification, narrative)])
                corrected_diagnostic = AnalysisDiagnostics()
                run_structured(mixed_text, corrected_empty, report_root, analysis_id=analysis_id,
                               config={}, diagnostics=corrected_diagnostic)
                assert corrected_empty.calls == 4
                assert len(load_current(report_root / "structured")[1]["findings"]) == 1
                assert any(event.get("contract_code") == "empty_detection_with_observed_indicators"
                           for event in corrected_diagnostic.snapshot()["events"])
                # Real SDK + operational wrapper: two empty responses exhaust the
                # existing single guard retry, record failure, keep the prior pointer.
                from agents.operational_diagnostics import run_operational_analysis
                refusal_input = report_root / "refusal-input.log"
                refusal_input.write_text(mixed_text, encoding="utf-8")
                pointer_before = (report_root / "structured/current.json").read_bytes()
                sdk_refusal = LLM(model="openrouter/openrouter/free", is_litellm=True,
                                  api_key="synthetic-test-key", base_url="https://openrouter.ai/api/v1",
                                  timeout=60, max_tokens=8192, additional_params={"max_retries": 0})
                refused_response = ModelResponse(model="vendor/synthetic-model:free", choices=[{
                    "index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": json.dumps(empty_detection)}}],
                    usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30,
                           "completion_tokens_details": {"reasoning_tokens": 0}})
                existing_receipts = set((report_root / "analysis-diagnostics").glob("*/receipt.json"))
                with patch("litellm.completion", return_value=refused_response) as refused_completions:
                    try:
                        run_operational_analysis(refusal_input, report_root, lambda **kwargs: sdk_refusal,
                                                 analysis_id=analysis_id, config={}, secrets_factory=lambda: ("synthetic-test-key",))
                    except Exception:
                        pass
                    else:
                        raise AssertionError("Empty detection with observed indicators was published")
                new_receipts = set((report_root / "analysis-diagnostics").glob("*/receipt.json")) - existing_receipts
                assert len(new_receipts) == 1 and refused_completions.call_count == 2
                refusal_receipt = json.loads(next(iter(new_receipts)).read_text(encoding="utf-8"))
                assert refusal_receipt["status"] == "failed" and refusal_receipt["generation"] is None
                assert refusal_receipt["logical_calls"] == refusal_receipt["transport_attempts_observed"] == 2
                assert [event["contract_code"] for event in refusal_receipt["diagnostics"]["events"]
                        if event["event"] == "guard"] == ["empty_detection_with_observed_indicators"] * 2
                assert not any(event["event"] == "local_stage" for event in refusal_receipt["diagnostics"]["events"])
                assert (report_root / "structured/current.json").read_bytes() == pointer_before
                assert "synthetic-test-key" not in json.dumps(refusal_receipt)
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
                # Operational wrapper observes the real SDK lane, with all transport
                # responses scripted and network still blocked by the outer context.
                from agents.operational_diagnostics import run_operational_analysis
                operational_llm = LLM(model="openrouter/openrouter/free", is_litellm=True,
                                      api_key="synthetic-test-key", base_url="https://openrouter.ai/api/v1",
                                      timeout=60, max_tokens=8192, additional_params={"max_retries": 0})
                operational_response = ModelResponse(model="vendor/synthetic-model:free", choices=[{
                    "index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": json.dumps(empty_detection)}}],
                    usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30,
                           "completion_tokens_details": {"reasoning_tokens": 2}})
                input_path = report_root / 'synthetic-input.log'
                input_path.write_text(normal_text, encoding='utf-8')
                existing_operational_receipts = set((report_root / 'analysis-diagnostics').glob('*/receipt.json'))
                with patch('litellm.completion', return_value=operational_response) as observed:
                    operational_manifest, _ = run_operational_analysis(input_path, report_root,
                        lambda **options: operational_llm, analysis_id=analysis_id, config={},
                        secrets_factory=lambda: ('synthetic-test-key',))
                receipt_paths = list(set((report_root / 'analysis-diagnostics').glob('*/receipt.json')) - existing_operational_receipts)
                assert len(receipt_paths) == 1
                operational_receipt = json.loads(receipt_paths[0].read_text(encoding='utf-8'))
                assert observed.call_count == 1 and operational_receipt['logical_calls'] == 1
                assert operational_receipt['usage']['total_tokens'] == 30
                assert operational_receipt['usage']['reasoning_tokens'] == 2
                assert operational_receipt['generation'] == operational_manifest['generation']
                assert operational_receipt['attempts'][0]['stage'] == 'detection'
                assert operational_receipt['attempts'][0]['response_model'] == 'vendor/synthetic-model:free'
                assert 'synthetic-test-key' not in receipt_paths[0].read_text(encoding='utf-8')
                # Incomplete evidence also keeps a scope warning, not a benign verdict.
                incomplete_llm = ScriptedLLM(model="scripted-incomplete", responses=[json.dumps(empty_detection)])
                run_structured("uninterpretable synthetic record", incomplete_llm, report_root,
                               analysis_id=analysis_id, config={})
                incomplete_result = load_current(report_root / "structured")[1]
                assert incomplete_llm.calls == 1 and "no permite descartar" in incomplete_result["narrative"]["summary"]
        print("CrewAI/LiteLLM aislados: 27 escenarios aprobados, incluido formato JSON nativo, evaluador acotado y reintento de clasificación sin conversión parcial; sin proveedor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

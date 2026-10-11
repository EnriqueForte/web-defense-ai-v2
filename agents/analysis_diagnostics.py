"""Bounded metadata diagnostics; never retains prompts, responses or exception messages."""
from copy import deepcopy
from pathlib import Path
import time

from agents.evidence_contracts import ContractError, parse_payload

STAGES = {"preparation", "construction", "execution", "detection", "classification", "narrative",
          "publication", "verification", "metrics", "configuration", "unknown"}
CODES = set("invalid_fields invalid_text invalid_text_encoding invalid_list output_limit duplicate_json_key "
            "invalid_json_constant invalid_json wrong_analysis_or_version duplicate_or_invalid_candidate "
            "invalid_evidence_reference invalid_pattern duplicate_candidate_group invalid_classification "
            "incomplete_or_foreign_classification invalid_recommendation_reference invalid_preparation_config "
            "pattern_without_observation brute_without_shared_window severity_without_support "
            "inconsistent_false_positive_severity missing_previous_stage invalid_analysis_id input_limit "
            "invalid_sampling_limit sampling_limit_exceeded empty_evidence input_too_large invalid_input_encoding "
            "linked_publication_path invalid_publication_manifest invalid_generation generation_manifest_mismatch "
            "generation_digest_mismatch generation_analysis_mismatch publication_unavailable "
            "other_without_observation unobserved_other_state empty_detection_with_observed_indicators".split())
ERROR_TYPES = set("ValueError RuntimeError ValidationError ContractError InstructorRetryException RetryError "
                  "AuthenticationError OpenRouterException HTTPStatusError TimeoutError ConnectionError "
                  "APITimeoutError RateLimitError AssertionError OSError KeyError TypeError JSONDecodeError".split())
VALIDATION_TYPES = set("json_invalid missing extra_forbidden literal_error string_type list_type dict_type "
                       "string_too_long string_too_short too_long too_short int_type value_error".split())
TRACE_FILES = {"structured_engine.py", "structured_prototype.py", "evaluate_structured_openrouter.py",
               "operational_diagnostics.py", "main.py", "pipeline.py",
               "evidence_contracts.py", "evidence_preparation.py", "structured_reporting.py",
               "structured_publication.py", "crew_agent_executor.py", "agent_utils.py", "task.py",
               "converter.py", "internal_instructor.py", "llm.py"}


def safe_exception(error):
    kinds, seen, current = [], set(), error
    while current is not None and id(current) not in seen and len(kinds) < 8:
        seen.add(id(current))
        name = type(current).__name__
        kinds.append(name if name in ERROR_TYPES else "other_exception")
        current = current.__cause__ or current.__context__
    frames, trace = [], error.__traceback__
    while trace is not None:
        code = trace.tb_frame.f_code
        name = Path(code.co_filename).name
        if name in TRACE_FILES:
            frames.append({"file": name, "function": code.co_name, "line": trace.tb_lineno})
        trace = trace.tb_next
    return {"error_types": kinds, "frames": frames[-12:]}


class AnalysisDiagnostics:
    def __init__(self, checkpoint=None):
        self.stage = "unknown"
        self.events = []
        self.dropped = 0
        self.calls = 0
        self.started = time.monotonic()
        self._call_started = {}
        self.checkpoint = checkpoint

    def _append(self, event):
        if len(self.events) < 100:
            self.events.append({"seconds": round(time.monotonic() - self.started, 3), **event})
        else:
            self.dropped += 1
        if self.checkpoint is not None:
            self.checkpoint(self.snapshot())

    def phase(self, stage):
        self.stage = stage if stage in STAGES else "unknown"
        self._append({"stage": self.stage, "event": "phase"})

    def begin_call(self, stage):
        self.stage = stage if stage in STAGES else "unknown"
        self.calls += 1
        self._call_started[self.calls] = time.monotonic()
        self._append({"stage": self.stage, "event": "call_started", "call": self.calls})
        return self.calls

    def finish_call(self, identifier, response, schema=None):
        details = {"stage": self.stage, "event": "call_returned", "call": identifier,
                   "duration_seconds": round(time.monotonic() - self._call_started.pop(identifier, time.monotonic()), 3)}
        if not isinstance(response, str):
            details["output_status"] = "non_text"
        else:
            details["characters"] = len(response)
            try:
                payload = parse_payload(response)
                details["output_status"] = "json_valid"
                if schema is not None:
                    try:
                        schema.model_validate(payload)
                        details["output_status"] = "schema_valid"
                    except Exception as error:
                        details["output_status"] = "schema_invalid"
                        # Pydantic values, locations and context can contain model output.
                        if type(error).__name__ == "ValidationError":
                            details["validation_types"] = sorted({
                                item["type"] if item["type"] in VALIDATION_TYPES else "validation_error"
                                for item in error.errors(include_input=False, include_context=False, include_url=False)})[:12]
            except (ContractError, UnicodeError):
                details["output_status"] = "json_invalid"
        self._append(details)

    def guard(self, stage, error=None):
        code = str(error) if isinstance(error, ContractError) else None
        self._append({"stage": stage if stage in STAGES else "unknown", "event": "guard",
                      "accepted": error is None,
                      **({"contract_code": code if code in CODES else "contract_rejected"} if error is not None else {})})

    def local_stage(self, stage):
        self.stage = stage if stage in {"classification", "narrative"} else "unknown"
        self._append({"stage": self.stage, "event": "local_stage", "source": "python",
                      "after_provider_call": self.calls})

    def completion(self, response, *, requested_model=None, max_tokens=None, secrets=()):
        from agents.completion_metadata import completion_metadata
        self._append({"stage": self.stage, "event": "completion_returned", "call": self.calls,
                      **completion_metadata(response, requested_model=requested_model,
                                            max_tokens=max_tokens, secrets=secrets)})

    def failure(self, error):
        self._append({"stage": self.stage, "event": "failure", **safe_exception(error)})

    def snapshot(self):
        return deepcopy({"schema_version": "1", "stage": self.stage, "calls": self.calls,
                         "dropped_events": self.dropped, "events": self.events})

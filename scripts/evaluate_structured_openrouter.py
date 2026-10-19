"""One explicitly authorized synthetic analysis; free router only, no operational writes."""
import argparse
import contextlib
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# Shared structured limits; the legacy factory keeps its previous defaults.
from agents.structured_engine import STRUCTURED_MAX_TOKENS, STRUCTURED_REQUEST_TIMEOUT_SECONDS
EVALUATION_MAX_TOKENS = STRUCTURED_MAX_TOKENS
from agents.evaluation_fixtures import CASES, fixture
from agents.evaluation_scoring import score_fixture_result


def bounded_evaluation_llm(delegate):
    """Keep the call budget without hiding the structured transport parameters."""
    from crewai.llms.base_llm import BaseLLM

    class BoundedLLM(BaseLLM):
        calls: int = 0

        def call(self, messages, **kwargs):
            if self.calls >= 6:
                raise RuntimeError("evaluation_call_budget")
            self.calls += 1
            previous = delegate.additional_params
            delegate.additional_params = self.additional_params
            try:
                return delegate.call(messages, **kwargs)
            finally:
                delegate.additional_params = previous

        def supports_function_calling(self):
            return False

    return BoundedLLM(model=delegate.model, is_litellm=delegate.is_litellm,
                      additional_params=dict(delegate.additional_params or {}))


@contextlib.contextmanager
def capture_completion_metadata(diagnostics, *, secrets=()):
    """Observe only this isolated synchronous LiteLLM evaluation, never request bodies."""
    import litellm
    original = litellm.completion
    def observed(*args, **kwargs):
        response = original(*args, **kwargs)
        diagnostics.completion(response, requested_model=kwargs.get("model"),
                               max_tokens=kwargs.get("max_tokens"), secrets=secrets)
        return response
    with patch.object(litellm, "completion", new=observed):
        yield


def evaluate(destination, case="mixed"):
    from agents.analysis_diagnostics import AnalysisDiagnostics, safe_exception
    from dashboard.services.read_store import atomic_write_text
    started = time.monotonic()
    destination = Path(destination)
    diagnostics = AnalysisDiagnostics(checkpoint=lambda snapshot: atomic_write_text(
        destination / "diagnostics.json", json.dumps(snapshot, indent=2)))
    diagnostics.phase("configuration")
    try:
        report = _evaluate(destination, diagnostics, case=case)
    except Exception as error:
        diagnostics.failure(error)
        report = {"status": "failed", "reason": safe_exception(error)["error_types"][0],
                  "seconds": round(time.monotonic() - started, 3), **safe_exception(error)}
    report["diagnostics"] = diagnostics.snapshot()
    from agents.usage_summary import summarize_usage
    report.update(summarize_usage(report["diagnostics"], report.get("usage_sdk")))
    return report


def _evaluate(destination, diagnostics, *, case="mixed"):
    selected_fixture = fixture(case)
    from config.model_config import resolve_llm_settings
    settings = resolve_llm_settings()  # Runtime only; never print settings or credentials.
    if (settings["provider"] != "openrouter" or settings["pricing_mode"] != "free" or
            settings["model"] != "openrouter/openrouter/free" or
            settings["candidates"] != ["openrouter/openrouter/free"] or not settings["api_key_configured"]):
        return {"status": "blocked", "reason": "configured_free_router_required", "calls": 0}
    from crewai import LLM
    from crewai.events.event_bus import crewai_event_bus
    from agents.structured_engine import run_structured
    from dashboard.services.structured_publication import load_current
    # No paid fallback; no retries inside the SDK; at most six task attempts.
    diagnostics.phase("construction")
    delegate = LLM(model=settings["model"], api_key=settings["api_key"],
                   base_url=settings["base_url"], is_litellm=True, temperature=0.1,
                   timeout=STRUCTURED_REQUEST_TIMEOUT_SECONDS, max_tokens=EVALUATION_MAX_TOKENS,
                   additional_params={"max_retries": 0})

    llm = bounded_evaluation_llm(delegate)
    text = selected_fixture["text"]
    started = time.monotonic()
    try:
        with patch.object(crewai_event_bus, "emit", return_value=None), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()), \
                capture_completion_metadata(diagnostics, secrets=(settings["api_key"],)):
            manifest, crew = run_structured(text, llm, destination, analysis_id="e" * 32, config={}, diagnostics=diagnostics)
        diagnostics.phase("verification")
        _, result, _ = load_current(destination / "structured")
        diagnostics.phase("metrics")
        scores = score_fixture_result(result["findings"], result["evidence"], case)
        return {"status": "succeeded", "calls": llm.calls, "seconds": round(time.monotonic() - started, 3),
                "model": settings["model"], "generation": manifest["generation"],
                **scores,
                "counts": result["counts"], "usage_sdk": delegate.get_token_usage_summary().model_dump(),
                "scope": "one_synthetic_fixture_not_semantic_acceptance"}
    except Exception as error:
        from agents.analysis_diagnostics import safe_exception
        diagnostics.failure(error)
        summary = safe_exception(error)
        return {"status": "failed", "case": case, "reason": summary["error_types"][0], "calls": llm.calls,
                **summary, "seconds": round(time.monotonic() - started, 3),
                "usage_sdk": delegate.get_token_usage_summary().model_dump()}


def failed_child_report(destination, reason):
    from agents.usage_summary import summarize_usage
    report = {"status": "failed", "reason": reason}
    checkpoint = Path(destination) / "diagnostics.json"
    if checkpoint.exists():
        report["diagnostics"] = json.loads(checkpoint.read_text(encoding="utf-8"))
    report.update(summarize_usage(report.get("diagnostics", {})))
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorized-free-analysis", action="store_true", required=True)
    parser.add_argument("--case", choices=CASES, default="mixed", help="one labeled synthetic case; does not run a batch")
    parser.add_argument("--child-destination", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.child_destination:
        destination = args.child_destination.resolve()
        if not destination.is_relative_to((ROOT / ".local-state/a05-evaluation").resolve()):
            raise ValueError("isolated_destination_required")
        with patch("dotenv.load_dotenv", return_value=False):
            report = evaluate(destination, case=args.case)
        (destination / "evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return 0 if report["status"] == "succeeded" else 1
    destination = ROOT / ".local-state/a05-evaluation" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination.mkdir(parents=True, exist_ok=False)
    environment = {**os.environ, "CREWAI_TRACING_ENABLED": "false", "OTEL_SDK_DISABLED": "true",
                   "LITELLM_LOCAL_MODEL_COST_MAP": "True", "LITELLM_MODE": "PRODUCTION",
                   "NOTIFICATION_DESTINATIONS": "", "CREWAI_STORAGE_DIR": str(destination / "framework")}
    try:
        completed = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                    "--authorized-free-analysis", "--case", args.case,
                                    "--child-destination", str(destination)],
                                   env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
        if not (destination / "evaluation.json").exists():
            report = failed_child_report(destination, "child_failed")
            (destination / "evaluation.json").write_text(json.dumps(report))
    except subprocess.TimeoutExpired:
        report = failed_child_report(destination, "deadline_600_seconds")
        (destination / "evaluation.json").write_text(json.dumps(report))
    print((destination / "evaluation.json").read_text(encoding="utf-8"))
    print("Evidence: " + str(destination / "evaluation.json"))
    return 0 if json.loads((destination / "evaluation.json").read_text())["status"] == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())

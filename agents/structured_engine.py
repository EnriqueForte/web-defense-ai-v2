"""Explicit structured execution lane; no provider is created on import."""
import os
from pathlib import Path
import uuid

from agents.evidence_contracts import ContractError
from agents.evidence_preparation import prepare_evidence
from agents.structured_prototype import build_prototype, stage_payload, PROMPT_VERSION
from dashboard.services.structured_publication import publish

STRUCTURED_MAX_TOKENS = 8192
STRUCTURED_REQUEST_TIMEOUT_SECONDS = 60


def engine_mode(environ=None):
    value = (os.environ if environ is None else environ).get("ANALYSIS_ENGINE_MODE", "legacy").strip().lower()
    if value not in {"legacy", "structured"}:
        raise ContractError("invalid_engine_mode")
    return value


def run_structured(text, llm, report_root, *, analysis_id=None, config=None, factory=build_prototype, diagnostics=None):
    def phase(value):
        if diagnostics is not None:
            diagnostics.phase(value)
    try:
        phase("preparation")
        prepared = prepare_evidence(text, analysis_id or uuid.uuid4().hex, config=config)
        if not prepared.bundle.items:
            raise ContractError("empty_evidence")
        phase("construction")
        crew, tasks = factory(prepared.bundle, llm, preparation=prepared,
                              **({"diagnostics": diagnostics} if diagnostics is not None else {}))
        phase("execution")
        crew.kickoff()
        phase("publication")
        manifest = publish(Path(report_root) / "structured", prepared,
                           *(stage_payload(task) for task in tasks),
                           model=str(llm.model), prompt_version=PROMPT_VERSION)
        return manifest, crew
    except Exception as error:
        if diagnostics is not None:
            diagnostics.failure(error)
        raise


def read_input(path):
    # Read a bounded amount even if the file grows concurrently.
    with Path(path).open("rb") as stream:
        content = stream.read(1024 * 1024 + 1)
    if len(content) > 1024 * 1024:
        raise ContractError("input_too_large")
    try:
        return content.decode("utf-8")
    except UnicodeError:
        raise ContractError("invalid_input_encoding") from None

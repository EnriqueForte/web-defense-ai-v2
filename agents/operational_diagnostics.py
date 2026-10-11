"""Safe process-local structured-engine receipts; never serializes LLM content."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
import uuid

from agents.analysis_diagnostics import AnalysisDiagnostics, safe_exception
from agents.evidence_contracts import ContractError
from agents.completion_metadata import completion_metadata
from agents.structured_engine import read_input, run_structured, STRUCTURED_MAX_TOKENS, STRUCTURED_REQUEST_TIMEOUT_SECONDS
from agents.usage_summary import summarize_usage
from config.model_config import configured_provider_keys
from dashboard.services.read_store import atomic_write_text
from dashboard.services.structured_publication import _directory


def diagnostic_destination(report_root, analysis_id):
    if not isinstance(analysis_id, str) or not re.fullmatch(r'[a-f0-9]{32}', analysis_id):
        raise ValueError('invalid_analysis_id')
    return _directory(Path(report_root) / 'analysis-diagnostics' / f'{analysis_id}-{uuid.uuid4().hex}')


class OperationalReceipt:
    def __init__(self, destination, analysis_id):
        self.destination = _directory(destination)
        if not re.fullmatch(r'[a-f0-9]{32}', analysis_id):
            raise ValueError('invalid_analysis_id')
        self.destination.mkdir(parents=True, exist_ok=False)
        self.analysis_id = analysis_id
        self.started = time.monotonic()
        self.attempts = []
        self.attempts_started = 0
        self.dropped = 0
        self.write_failed = False
        self.diagnostics = AnalysisDiagnostics(checkpoint=self.checkpoint)

    def write(self, name, data):
        try:
            atomic_write_text(_directory(self.destination / name), json.dumps(data, indent=2))
        except (OSError, ContractError):
            # An unavailable diagnostics disk must not replace the engine outcome.
            self.write_failed = True

    def checkpoint(self, snapshot):
        self.write('checkpoint.json', {'schema_version': '1', 'analysis_id': self.analysis_id,
                   'diagnostics': snapshot, 'transport_attempts_observed': self.attempts_started,
                   'dropped_transport_attempts': self.dropped, 'attempts': self.attempts})

    @contextmanager
    def capture(self, *, secrets=()):
        import litellm
        original = litellm.completion
        def observed(*args, **kwargs):
            self.attempts_started += 1
            row = {'attempt': self.attempts_started, 'logical_call': self.diagnostics.calls,
                   'stage': self.diagnostics.stage, 'status': 'started'}
            retained = len(self.attempts) < 100
            if retained:
                self.attempts.append(row)
            else:
                self.dropped += 1
            self.checkpoint(self.diagnostics.snapshot())
            started = time.monotonic()
            try:
                response = original(*args, **kwargs)
            except Exception as error:
                row.update(status='failed', **safe_exception(error))
                raise
            else:
                row.update(status='returned', **completion_metadata(response, requested_model=kwargs.get('model'),
                           max_tokens=kwargs.get('max_tokens'), secrets=secrets))
                return response
            finally:
                row['duration_seconds'] = round(time.monotonic() - started, 3)
                self.checkpoint(self.diagnostics.snapshot())
        litellm.completion = observed
        try:
            yield
        finally:
            litellm.completion = original

    def finish(self, status, *, sdk=None, generation=None):
        snapshot = self.diagnostics.snapshot()
        completions = [{'event': 'completion_returned', 'call': row['attempt'], 'usage': row.get('usage')}
                       for row in self.attempts if row['status'] == 'returned']
        reconciled = summarize_usage({'calls': self.attempts_started or None, 'events': completions,
                                     'dropped_events': self.dropped}, sdk)
        durations = {}
        elapsed = round(time.monotonic() - self.started, 3)
        events = snapshot['events']
        for index, event in enumerate(events):
            stop = events[index + 1]['seconds'] if index + 1 < len(events) else elapsed
            stage = event['stage']
            durations[stage] = round(durations.get(stage, 0) + max(0, stop - event['seconds']), 3)
        body = {'schema_version': '1', 'analysis_id': self.analysis_id, 'status': status,
                'finished_at': datetime.now(timezone.utc).isoformat(), 'seconds': elapsed,
                'generation': generation, 'logical_calls': snapshot['calls'],
                'transport_attempts_observed': self.attempts_started, 'attempts': self.attempts,
                'dropped_transport_attempts': self.dropped, 'checkpoint_write_failed': self.write_failed,
                'stage_durations_seconds': durations, 'stage_duration_coverage_complete': bool(events) and not snapshot['dropped_events'],
                'diagnostics': snapshot, **reconciled,
                'transport_observer': 'litellm.completion; native SDK metadata unavailable'}
        body['completion_metadata_status'] = ('unavailable' if not self.attempts_started else
            'partial' if self.dropped or any(row.get('metadata_status') != 'captured' for row in self.attempts)
            else 'captured')
        self.write('receipt.json', body)
        body['checkpoint_write_failed'] = self.write_failed
        return body


def run_operational_analysis(input_path, report_root, llm_factory, *, analysis_id=None, config=None,
                             destination=None, runner=run_structured, secrets_factory=configured_provider_keys):
    analysis_id = analysis_id or uuid.uuid4().hex
    receipt = OperationalReceipt(destination or diagnostic_destination(report_root, analysis_id), analysis_id)
    llm = None
    def sdk_usage():
        try:
            value = llm.get_token_usage_summary()
            return value.model_dump() if hasattr(value, 'model_dump') else value
        except Exception:
            return None
    try:
        receipt.diagnostics.phase('preparation')
        text = read_input(input_path)
        receipt.diagnostics.phase('construction')
        llm = llm_factory(max_tokens=STRUCTURED_MAX_TOKENS, timeout=STRUCTURED_REQUEST_TIMEOUT_SECONDS)
        with receipt.capture(secrets=secrets_factory()):
            manifest, crew = runner(text, llm, report_root, analysis_id=analysis_id,
                                    config=config, diagnostics=receipt.diagnostics)
    except Exception as error:
        receipt.diagnostics.failure(error)
        receipt.finish('failed', sdk=sdk_usage())
        raise
    receipt.finish('succeeded', sdk=sdk_usage(), generation=manifest['generation'])
    return manifest, crew

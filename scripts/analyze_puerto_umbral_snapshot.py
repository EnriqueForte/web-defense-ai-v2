"""One authorized saved-snapshot analysis in Parrot; no capture, worker or scenarios.

--check only reads metadata. Execution requires a confirmed Groq Free account;
the local catalog cannot verify billing. Never upgrades a plan or changes .env.
"""
import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
STATE = ROOT / '.local-state/puerto-umbral'
REPORTS = STATE / 'reports'
DB = STATE / 'analysis.sqlite3'
ATTEMPT = STATE / 'manual-validation.json'
MODEL = 'groq/openai/gpt-oss-120b'
CALLS = 6
TOKENS = 8192
DEADLINE = 600


def plan(mode, identifier=None, digest=None):
    from config.model_config import resolve_llm_settings
    from dashboard.services.puerto_umbral_capture import source_status
    from dashboard.services.structured_publication import _directory
    from dashboard.services.runtime_lock import lock_is_held
    from scripts.local_runtime_profile import active_jobs
    _directory(STATE)
    _directory(REPORTS)
    for path in (ATTEMPT, DB, STATE / '.follow.lock',
                 *(DB.with_suffix(f'.{name}.lock') for name in ('worker', 'cycle', 'engine'))):
        _directory(path)
    settings = resolve_llm_settings()
    source = source_status(mode=mode)
    blockers = []
    if settings['provider'] != 'groq' or settings['model'] != MODEL or settings['pricing_mode'] != 'free':
        blockers.append('configured_groq_120b_free_required')
    if not settings['api_key_configured']:
        blockers.append('configured_key_required')
    if source['status'] not in {'available', 'stale'} or not source.get('line_count'):
        blockers.append('valid_nonempty_saved_snapshot_required')
    if identifier is not None and source.get('snapshot_id') != identifier:
        blockers.append('snapshot_changed')
    if digest is not None and source.get('sha256') != digest:
        blockers.append('snapshot_digest_changed')
    if ATTEMPT.exists():
        blockers.append('authorization_already_consumed_do_not_retry')
    for name, path in [('follow', STATE / '.follow.lock'),
                       *((name, DB.with_suffix(f'.{name}.lock')) for name in ('worker', 'cycle', 'engine'))]:
        if lock_is_held(path) is not False:
            blockers.append(name + '_active_or_unknown')
    jobs = active_jobs(DB)
    if jobs['status'] == 'unavailable' or jobs['queued'] or jobs['running']:
        blockers.append('active_jobs_or_unreadable_store')
    return {'ready': not blockers, 'blockers': blockers, 'mode': mode,
            'snapshot_id': source.get('snapshot_id'), 'sha256': source.get('sha256'),
            'line_count': source.get('line_count'), 'model': MODEL,
            'maximum_transport_requests': CALLS, 'maximum_output_tokens_per_request': TOKENS,
            'deadline_seconds': DEADLINE, 'network_retries': 0, 'model_fallback': False,
            'paid_budget_eur': 0, 'billing_verification': 'owner_confirmed_free_account_required',
            'scope': 'one_saved_snapshot_not_full_detector_acceptance'}


def native_llm(key, receipt):
    """Direct Groq SDK, exact endpoint/model, no network retries or tools."""
    from crewai.llms.base_llm import BaseLLM
    from groq import Groq
    import httpx
    from agents.analysis_diagnostics import safe_exception
    from agents.completion_metadata import completion_metadata

    def guard(request):
        if (request.method != 'POST' or str(request.url) != 'https://api.groq.com/openai/v1/chat/completions'
                or receipt.attempts_started >= CALLS or time.monotonic() - receipt.started >= DEADLINE):
            raise RuntimeError('authorized_request_budget_or_endpoint')
        body = json.loads(request.content)
        if body.get('model') != MODEL.removeprefix('groq/') or body.get('max_completion_tokens') != TOKENS:
            raise RuntimeError('authorized_model_or_tokens_changed')
        receipt.attempts_started += 1
        receipt.attempts.append({'attempt': receipt.attempts_started,
            'logical_call': receipt.diagnostics.calls, 'stage': receipt.diagnostics.stage, 'status': 'started'})
        receipt.checkpoint(receipt.diagnostics.snapshot())

    transport = httpx.Client(timeout=60, trust_env=False, follow_redirects=False,
                             event_hooks={'request': [guard]})
    client = Groq(api_key=key, base_url='https://api.groq.com', max_retries=0,
                  timeout=60, http_client=transport)

    class SavedSnapshotLLM(BaseLLM):
        def supports_function_calling(self):
            return False

        def call(self, messages, **kwargs):
            if isinstance(messages, str):
                messages = [{'role': 'user', 'content': messages}]
            # Only role/content are transported: no CrewAI cache markers or tools.
            if not isinstance(messages, list) or any(not isinstance(item, dict)
                    or item.get('role') not in {'system', 'user', 'assistant'}
                    or not isinstance(item.get('content'), str) for item in messages):
                raise ValueError('unsupported_message_shape')
            cleaned = [{name: item[name] for name in ('role', 'content')} for item in messages]
            previous = receipt.attempts_started
            started = time.monotonic()
            try:
                response = client.chat.completions.create(model=MODEL.removeprefix('groq/'),
                    messages=cleaned, temperature=0.1, max_completion_tokens=TOKENS,
                    reasoning_effort='low', response_format={'type': 'json_object'})
                row = receipt.attempts[-1]
                row.update(status='returned', **completion_metadata(response, requested_model=MODEL,
                                                                   max_tokens=TOKENS, secrets=(key,)))
                message = response.choices[0].message
                if response.choices[0].finish_reason != 'stop' or not isinstance(message.content, str):
                    raise RuntimeError('incomplete_completion')
                return message.content
            except Exception as error:
                if receipt.attempts_started > previous:
                    row = receipt.attempts[-1]
                    if row['status'] != 'returned':
                        row.update(status='failed', **safe_exception(error))
                raise
            finally:
                if receipt.attempts_started > previous:
                    receipt.attempts[-1]['duration_seconds'] = round(time.monotonic() - started, 3)
                receipt.checkpoint(receipt.diagnostics.snapshot())

    return SavedSnapshotLLM(model=MODEL), client


def execute(args):
    from config.model_config import resolve_llm_settings
    from dashboard.services.analysis_jobs import JobStore, utc_now
    from dashboard.services.read_store import atomic_write_text, capture_file
    from dashboard.services.runtime_lock import exclusive_lock
    from dashboard.services.structured_publication import load_current, _directory
    from dashboard.services.puerto_umbral_capture import CapturedLog, record_analysis_input
    from agents.operational_diagnostics import OperationalReceipt, diagnostic_destination
    from agents.structured_engine import run_structured
    from crewai.events.event_bus import crewai_event_bus
    from unittest.mock import patch

    # The normal worker and following cannot run alongside this single execution.
    with ExitStack() as locks:
        for path in (STATE / '.follow.lock', DB.with_suffix('.worker.lock'),
                     DB.with_suffix('.cycle.lock'), DB.with_suffix('.engine.lock')):
            locks.enter_context(exclusive_lock(_directory(path)))
        # Repeat content/config checks under the leases; our own locks are expected.
        check = plan(args.mode, args.snapshot_id, args.sha256)
        check['blockers'] = [code for code in check['blockers'] if not code.endswith('_active_or_unknown')]
        if check['blockers']:
            raise ValueError('preconditions_changed')
        snapshot = STATE / 'snapshots' / args.snapshot_id / 'access.log'
        _directory(snapshot)
        captured = capture_file(snapshot)
        if captured.status != 'available' or captured.digest != args.sha256:
            raise ValueError('snapshot_integrity_error')
        text = captured.content.decode('utf-8')
        if not text.strip() or len(captured.content) > 1024 * 1024:
            raise ValueError('invalid_snapshot_size')
        settings = resolve_llm_settings()
        store = JobStore(DB)
        job, outcome = store.enqueue('manual', 'puerto-umbral-one-authorized-validation')
        if outcome != 'created':
            raise ValueError('authorization_already_consumed')
        job = store.claim()
        summary = {**check, 'ready': True, 'blockers': [], 'analysis_id': job['id'],
                   'status': 'started', 'actual_provider_charge_eur': None}
        atomic_write_text(ATTEMPT, json.dumps(summary, indent=2))
        receipt = None
        client = None
        generation = None
        try:
            frozen = CapturedLog(snapshot, captured.digest, check['line_count'], args.snapshot_id, False)
            record_analysis_input(frozen, job['id'])
            receipt = OperationalReceipt(diagnostic_destination(REPORTS, job['id']), job['id'])
            receipt.diagnostics.phase('construction')
            llm, client = native_llm(settings['api_key'], receipt)
            store.phase(job['id'], 'analyzing', last_ingested_at=utc_now())
            # Disable framework event emission; no remote tracing or persisted prompts.
            with patch.object(crewai_event_bus, 'emit', return_value=None):
                manifest, _ = run_structured(text, llm, REPORTS, analysis_id=job['id'],
                                             config={}, diagnostics=receipt.diagnostics)
            generation = manifest['generation']
            verified, result, markdown = load_current(REPORTS / 'structured')
            if verified['analysis_id'] != job['id'] or result['evidence']['source_digest'] != captured.digest:
                raise ValueError('published_input_mismatch')
            current = capture_file(REPORTS / 'structured/generations' / generation / 'report.md')
            store.phase(job['id'], 'publishing', last_analyzed_at=utc_now(), report_id=current.file_id)
            from datetime import datetime, timezone
            stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            atomic_write_text(REPORTS / 'historial' / ('reporte_' + stamp + '_ciclo' + job['id'] + '.md'), markdown)
            store.finish(job['id'], 'succeeded', report_id=current.file_id)
            summary.update(status='succeeded', generation=generation, counts=result['counts'])
        except BaseException as error:
            from agents.analysis_diagnostics import safe_exception
            if receipt is not None:
                receipt.diagnostics.failure(error)
            store.finish(job['id'], 'interrupted' if isinstance(error, KeyboardInterrupt) else 'failed',
                         'saved_snapshot_analysis_failed')
            summary.update(status='failed', **safe_exception(error))
        finally:
            if client is not None:
                client.close()
            if receipt is not None:
                details = receipt.finish(summary['status'], generation=generation)
                details['transport_observer'] = 'groq SDK; httpx request hook; retries disabled'
                receipt.write('receipt.json', details)
                summary.update(transport_requests=receipt.attempts_started, usage=details['usage'])
            summary['input_unchanged'] = hashlib.sha256(snapshot.read_bytes()).hexdigest() == captured.digest
            atomic_write_text(ATTEMPT, json.dumps(summary, indent=2))
        return 0 if summary['status'] == 'succeeded' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--check', action='store_true')
    actions.add_argument('--authorized-free-analysis', action='store_true')
    parser.add_argument('--groq-free-account', action='store_true',
                        help='owner confirms actual Groq billing account is Free, not just V2 catalog')
    parser.add_argument('--mode', choices=('corrected', 'vulnerable'), default='corrected')
    parser.add_argument('--snapshot-id')
    parser.add_argument('--sha256')
    parser.add_argument('--child', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not args.check and (not args.groq_free_account or not re.fullmatch('[a-f0-9]{32}', args.snapshot_id or '')
                          or not re.fullmatch('[a-f0-9]{64}', args.sha256 or '')):
        parser.error('execution requires --groq-free-account --snapshot-id ID --sha256 HASH')
    os.environ.update(ANALYSIS_ENGINE_MODE='structured', ANALYSIS_DB_PATH=str(DB),
                      REPORT_PATH=str(REPORTS), LOG_PATH=str(STATE / 'access.log'),
                      NOTIFICATION_DESTINATIONS='', CREWAI_TRACING_ENABLED='false', OTEL_SDK_DISABLED='true',
                      LITELLM_LOCAL_MODEL_COST_MAP='True', LITELLM_MODE='PRODUCTION',
                      CREWAI_STORAGE_DIR=str(STATE / 'validation-framework'))
    os.chdir(ROOT)
    try:
        check = plan(args.mode, args.snapshot_id, args.sha256)
        if args.check or not check['ready']:
            print(json.dumps(check, indent=2))
            return 0 if check['ready'] else 1
        if args.child:
            return execute(args)
        command = [sys.executable, '-B', str(Path(__file__).resolve()), *sys.argv[1:], '--child']
        try:
            child = subprocess.run(command, cwd=ROOT, env=os.environ.copy(),
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=DEADLINE)
        except subprocess.TimeoutExpired:
            print('Tiempo agotado. No repetir: revisar manual-validation.json y el checkpoint conservado.')
            return 1
        except KeyboardInterrupt:
            print('Interrumpido. No repetir: revisar el recibo conservado antes de cualquier otra ejecución.')
            return 1
        if ATTEMPT.is_file():
            print(ATTEMPT.read_text(encoding='utf-8'))
        else:
            print('No se completó la preparación; no se autoriza un reintento automático.')
        return child.returncode
    except Exception:
        print('Comprobación bloqueada: revisar rutas, snapshot, configuración y bloqueos locales; no se reintenta.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

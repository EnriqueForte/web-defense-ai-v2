"""Read one captured application audit; no Docker, network, jobs or model calls.

The source is the trusted controller's saved capture, not its corpus expectations
or functional verdict. Rules describe observations and never merge into an LLM
report or claim browser execution from a raw rendering event.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from dashboard.services.structured_publication import _directory
from labs.puerto_umbral.lab.audit_contract import validate_batch

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / 'labs/puerto_umbral/.local-state/f2/runs'
VERSION = 'puerto-umbral-audit-observer-1'


def read_json_capture(path, limit):
    """Bound bytes before parsing, including files growing during a read."""
    path = _directory(path)
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0)
    with os.fdopen(os.open(path, flags), 'rb') as handle:
        initial = os.fstat(handle.fileno())
        if not stat.S_ISREG(initial.st_mode) or initial.st_size > limit:
            raise ValueError('invalid_application_capture_size')
        raw = handle.read(limit + 1)
        final = os.fstat(handle.fileno())
    current = _directory(path).stat()
    identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
    if len(raw) > limit or len(raw) != initial.st_size or identity(initial) != identity(final) or identity(final) != identity(current):
        raise ValueError('application_capture_changing')
    return json.loads(raw.decode('utf-8', 'strict')), hashlib.sha256(raw).hexdigest()


def observations(events):
    rows = []
    for event in events:
        kind = None
        effect = 'requires_investigation'
        component = event['component']
        if component == 'cargo' and event['owner'] not in {'none', event['actor']}:
            kind = 'foreign_resource_served' if event['decision'] == 'allow' else 'object_access_denied'
            effect = 'resource_returned' if event['decision'] == 'allow' else 'request_denied'
        elif component == 'docking' and event['action'] == 'execute' and event['state_before'] != 'approved':
            executed = event['decision'] == 'allow' and event['outcome'] == 'executed'
            kind = ('permit_reused' if executed else 'permit_reuse_denied') if event['state_before'] == 'consumed' else ('docking_without_approval' if executed else 'approval_required')
            effect = 'operation_executed' if executed else 'request_denied'
        elif component == 'beacon':
            if event['canary_scope'] == 'internal' and event['outcome'] == 'canary_read':
                kind, effect = 'internal_canary_read', 'canary_resource_returned'
            elif event['decision'] == 'deny':
                kind, effect = 'canary_fetch_denied', 'request_denied'
        elif component == 'preferences' and event['origin_relation'] == 'cross':
            if event['outcome'] == 'updated':
                kind = 'cross_origin_cookie_state_change' if event['auth_source'] == 'cookie' else 'http_origin_control_probe'
                effect = 'cookie_state_changed_client_not_independently_verified' if event['auth_source'] == 'cookie' else 'http_probe_state_changed_not_browser_proof'
            elif event['csrf_check'] == 'rejected':
                kind, effect = 'cross_origin_request_denied', 'request_denied'
        elif component == 'notice_board' and event['action'] == 'read' and event['render_context'] == 'raw_markup':
            kind, effect = 'stored_markup_rendered', 'browser_execution_not_inferred'
        if kind:
            ref = hashlib.sha256((event['run_id'] + ':' + str(event['sequence'])).encode()).hexdigest()[:24]
            rows.append({'id': ref, 'sequence': event['sequence'], 'component': component,
                         'observed_at': event['observed_at'], 'actor': event['actor'], 'resource': event['resource'],
                         'observation': kind, 'effect': effect, 'http_status': event['http_status']})
    return rows


def source_status(mode='corrected', run_id=None, *, _include_batch=False):
    result = {'source': 'puerto-umbral-application', 'status': 'missing', 'mode': mode,
              'run_id': None, 'sha256': None, 'events': 0, 'observations': [],
              'observer_version': VERSION, 'llm_consulted': False,
              'scope': 'captured_target_events_rule_observations_not_model_report'}
    if mode not in {'vulnerable', 'corrected'} or (run_id is not None and not re.fullmatch('[a-f0-9]{32}', run_id)):
        result.update(status='error', error_code='invalid_application_source_selection')
        return result
    try:
        _directory(RUNS)
        if not RUNS.exists():
            return result
        if run_id:
            candidates = [RUNS / run_id]
        else:
            candidates = []
            for index, directory in enumerate(RUNS.iterdir()):
                if index >= 1000:
                    raise ValueError('application_source_inventory_limit')
                if re.fullmatch('[a-f0-9]{32}', directory.name):
                    _directory(directory)
                    if directory.is_dir():
                        candidates.append(directory)
                if len(candidates) > 1000:
                    raise ValueError('application_source_inventory_limit')
            candidates.sort(key=lambda path: path.stat().st_mtime_ns, reverse=True)
        for directory in candidates:
            receipt_path = _directory(directory / 'receipt.json')
            if not receipt_path.is_file() or receipt_path.stat().st_size > 2 * 1024 * 1024:
                if run_id:
                    raise ValueError('invalid_application_receipt')
                continue
            receipt, _ = read_json_capture(receipt_path, 2 * 1024 * 1024)
            if type(receipt) is not dict:
                raise ValueError('invalid_application_receipt')
            audit = receipt.get('application_audit')
            if receipt.get('mode') != mode:
                continue
            if receipt.get('application_audit_error'):
                raise ValueError('latest_application_capture_failed')
            if audit is None:
                continue
            if receipt.get('schema_version') != 2 or receipt.get('version') != 'puerto-umbral-extensions-1':
                raise ValueError('unsupported_application_receipt')
            if (receipt.get('id') != directory.name or type(audit) is not dict
                    or receipt.get('status') not in {'running', 'completed', 'failed', 'stopped', 'interrupted'}
                    or not re.fullmatch('application-[a-f0-9]{16}\\.json', audit.get('file', ''))
                    or not re.fullmatch('[a-f0-9]{64}', audit.get('sha256', ''))):
                raise ValueError('invalid_application_receipt')
            audit_path = _directory(directory / audit['file'])
            if not audit_path.is_file() or audit_path.stat().st_size > 256 * 1024:
                raise ValueError('invalid_application_capture')
            value, digest = read_json_capture(audit_path, 256 * 1024)
            if digest != audit['sha256']:
                raise ValueError('application_capture_integrity_error')
            batch = validate_batch(value, directory.name)
            if (not batch['events'] or type(audit.get('events')) is not int
                    or len(batch['events']) != audit['events'] or batch['schema'] != audit.get('schema')
                    or any(event['mode'] != mode for event in batch['events'])):
                raise ValueError('application_capture_mode_mismatch')
            result.update(status='available', run_id=directory.name, sha256=digest,
                          events=len(batch['events']), observations=observations(batch['events']),
                          execution_status=receipt.get('status'),
                          evidence_kind=receipt.get('evidence_kind'),
                          trust='target_observations_saved_outside_target_by_controller')
            if _include_batch:
                result['_batch'] = batch
            return result
        return result
    except (OSError, ValueError, TypeError, KeyError):
        result.update(status='error', error_code='application_source_unavailable_or_invalid')
        return result


def preserve_capture(mode, run_id, digest):
    """Explicit copy of validated events into V2's backup profile. No model."""
    from datetime import datetime, timezone
    from dashboard.services.read_store import atomic_write_text
    value = source_status(mode, run_id, _include_batch=True)
    if value['status'] != 'available':
        raise ValueError('application_source_not_available')
    if value['sha256'] != digest:
        raise ValueError('application_snapshot_changed')
    batch = value.pop('_batch')
    state = _directory(ROOT / '.local-state/puerto-umbral/application-audit')
    identifier = hashlib.sha256((mode + ':' + run_id + ':' + digest).encode()).hexdigest()[:32]
    destination = _directory(state / 'snapshots' / identifier)
    body = json.dumps(batch, ensure_ascii=False, sort_keys=True, indent=2)
    body_digest = hashlib.sha256(body.encode()).hexdigest()
    if destination.exists():
        # Repeated explicit requests for the same evidence reuse a complete
        # immutable snapshot; a partial or different copy is never overwritten.
        existing, _ = read_json_capture(destination / 'receipt.json', 8192)
        saved, saved_digest = read_json_capture(destination / 'events.json', 256 * 1024)
        if (type(existing) is not dict or existing.get('snapshot_id') != identifier
                or existing.get('source') != value['source'] or existing.get('schema_version') != 1
                or existing.get('run_id') != run_id or existing.get('mode') != mode
                or existing.get('original_sha256') != digest or existing.get('sha256') != body_digest
                or existing.get('analysis_requested') is not False or existing.get('notifications_requested') is not False
                or existing.get('events') != value['events'] or saved_digest != body_digest or saved != batch):
            raise ValueError('application_saved_capture_mismatch')
        atomic_write_text(_directory(state / 'current.json'), json.dumps(existing, sort_keys=True))
        return existing
    destination.mkdir(parents=True, exist_ok=False)
    receipt = {'schema_version': 1, 'source': value['source'], 'snapshot_id': identifier,
               'run_id': value['run_id'], 'mode': mode, 'events': value['events'],
               'sha256': body_digest, 'original_sha256': value['sha256'],
               'observer_version': VERSION, 'captured_at': datetime.now(timezone.utc).isoformat(),
               'execution_status_at_capture': value['execution_status'], 'evidence_kind': value['evidence_kind'],
               'analysis_requested': False, 'notifications_requested': False}
    atomic_write_text(destination / 'events.json', body)
    encoded = json.dumps(receipt, sort_keys=True)
    atomic_write_text(destination / 'receipt.json', encoded)
    atomic_write_text(_directory(state / 'current.json'), encoded)
    return receipt

"""Structured operational diagnostics with synthetic SDK/subprocesses only."""
from contextlib import nullcontext
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

from agents.operational_diagnostics import OperationalReceipt, diagnostic_destination, run_operational_analysis
from agents.evidence_contracts import ContractError

ID = 'a' * 32
SECRET = 'SYNTHETIC-secret-that-must-never-be-retained'

def response():
    return {'model': 'vendor/model:free', 'choices': [{'finish_reason': 'stop', 'message': {
        'content': SECRET, 'reasoning_content': SECRET}}], 'usage': {'prompt_tokens': 2,
        'completion_tokens': 3, 'total_tokens': 5, 'completion_tokens_details': {'reasoning_tokens': 2}}}

class OperationalDiagnosticsTests(TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory()))

    def receipt(self):
        return OperationalReceipt(diagnostic_destination(self.root, ID), ID)

    def test_completion_metadata_and_sdk_discrepancy_without_content_or_secrets(self):
        tracker = self.receipt()
        sdk = SimpleNamespace(completion=lambda **kwargs: response())
        original = sdk.completion
        tracker.diagnostics.begin_call('detection')
        with patch.dict(sys.modules, {'litellm': sdk}), tracker.capture(secrets=(SECRET,)):
            self.assertEqual(sdk.completion(model='vendor/requested', max_tokens=8192, api_key=SECRET), response())
        self.assertIs(sdk.completion, original)
        record = tracker.finish('succeeded', sdk={'reasoning_tokens':0, 'total_tokens':5})
        self.assertEqual(record['logical_calls'], 1)
        self.assertEqual(record['usage']['reasoning_tokens'], 2)
        self.assertEqual(record['usage_discrepancies'][0]['field'], 'reasoning_tokens')
        self.assertNotIn(SECRET, ''.join(p.read_text() for p in tracker.destination.glob('*.json')))
        self.assertTrue(record['usage']['complete'])

    def test_retry_attempts_do_not_claim_complete_usage_after_unknown_failed_response(self):
        tracker = self.receipt()
        delegate = Mock(side_effect=[ValueError(SECRET), response()])
        sdk = SimpleNamespace(completion=delegate)
        tracker.diagnostics.begin_call('detection')
        with patch.dict(sys.modules, {'litellm':sdk}), tracker.capture():
            with self.assertRaises(ValueError): sdk.completion()
            sdk.completion()
        record = tracker.finish('succeeded', sdk={'total_tokens':5})
        self.assertEqual(record['logical_calls'], 1)
        self.assertEqual(record['transport_attempts_observed'], 2)
        self.assertIsNone(record['usage']['total_tokens'])
        self.assertFalse(record['usage']['complete'])
        self.assertNotIn(SECRET, json.dumps(record))
        self.assertIs(sdk.completion, delegate)

    def test_http_failure_persists_safe_status_in_checkpoint_and_receipt_and_restores_hook(self):
        import httpx
        request = httpx.Request('POST', 'https://example.invalid/' + SECRET,
                                headers={'Authorization':SECRET})
        response = httpx.Response(401, request=request, json={'error':SECRET})
        error = httpx.HTTPStatusError(SECRET, request=request, response=response)
        delegate = Mock(side_effect=error)
        sdk = SimpleNamespace(completion=delegate)
        tracker = self.receipt()
        tracker.diagnostics.begin_call('detection')
        with patch.dict(sys.modules, {'litellm':sdk}), tracker.capture():
            with self.assertRaises(httpx.HTTPStatusError) as raised:
                sdk.completion(api_key=SECRET)
        self.assertIs(raised.exception,error)
        self.assertIs(sdk.completion,delegate)
        tracker.diagnostics.failure(error)
        tracker.finish('failed')
        for filename in ('checkpoint.json','receipt.json'):
            saved = json.loads((tracker.destination/filename).read_text())
            self.assertEqual(saved['attempts'][0]['http_status'],401)
            self.assertEqual(saved['diagnostics']['events'][-1]['http_status'],401)
            self.assertNotIn(SECRET,json.dumps(saved))
        self.assertEqual(saved['logical_calls'],1)
        self.assertEqual(saved['transport_attempts_observed'],1)
        self.assertIsNone(saved['usage']['total_tokens'])

    def test_native_or_absent_metadata_is_unknown_not_zero_sdk_fallback(self):
        tracker = self.receipt()
        tracker.diagnostics.begin_call('detection')
        record = tracker.finish('failed', sdk={'reasoning_tokens':0})
        self.assertEqual(record['transport_attempts_observed'], 0)
        self.assertIsNone(record['usage']['reasoning_tokens'])
        self.assertFalse(record['usage']['complete'])

    def test_two_returned_attempts_for_one_logical_call_are_aggregated_independently(self):
        tracker = self.receipt()
        sdk = SimpleNamespace(completion=lambda: response())
        tracker.diagnostics.begin_call('detection')
        with patch.dict(sys.modules, {'litellm': sdk}), tracker.capture():
            sdk.completion(); sdk.completion()
        record = tracker.finish('succeeded', sdk={'total_tokens':10})
        self.assertEqual(record['logical_calls'], 1)
        self.assertEqual(record['usage']['total_tokens'], 10)
        self.assertEqual(record['usage']['reasoning_tokens'], 4)
        self.assertTrue(record['usage']['complete'])

    def test_repeated_job_identity_has_distinct_receipts_and_restores_hook_on_error(self):
        first, second = self.receipt(), self.receipt()
        self.assertNotEqual(first.destination, second.destination)
        delegate = Mock(side_effect=ValueError(SECRET))
        sdk = SimpleNamespace(completion=delegate)
        with patch.dict(sys.modules, {'litellm':sdk}):
            with self.assertRaises(ValueError), first.capture(): sdk.completion()
        self.assertIs(sdk.completion,delegate)
        first.finish('failed')
        self.assertFalse((second.destination/'receipt.json').exists())

    def test_structured_failure_does_not_persist_raw_subprocess_output(self):
        import pipeline
        result=SimpleNamespace(returncode=1,stdout=SECRET,stderr=SECRET)
        with patch.dict(os.environ,{'ANALYSIS_ENGINE_MODE':'structured','ENGINE_DIAGNOSTICS_DIR':str(self.root)}), \
                patch.object(pipeline,'REPORT_PATH',self.root),patch.object(pipeline.subprocess,'run',return_value=result):
            self.assertFalse(pipeline.run_engine(analysis_id=ID))
        self.assertEqual(len(list(self.root.rglob('process.json'))),1)
        self.assertFalse(list(self.root.glob('*.log')))
        self.assertNotIn(SECRET,''.join(p.read_text() for p in self.root.rglob('*.json')))

    def test_constructor_error_is_recorded_before_any_provider_invocation(self):
        path = self.root/'input.log'; path.write_text('synthetic')
        factory = Mock(side_effect=ValueError(SECRET))
        destination = diagnostic_destination(self.root, ID)
        with self.assertRaises(ValueError):
            run_operational_analysis(path, self.root, factory, analysis_id=ID, destination=destination, secrets_factory=lambda:())
        record = json.loads((destination/'receipt.json').read_text())
        self.assertEqual(record['status'],'failed')
        self.assertEqual(record['logical_calls'],0)
        self.assertNotIn(SECRET,json.dumps(record))
        factory.assert_called_once_with(max_tokens=8192,timeout=60)

    def test_runner_success_records_receipt_without_changing_factory_or_payload(self):
        path=self.root/'input.log'; path.write_text('synthetic')
        fake_llm=SimpleNamespace(get_token_usage_summary=lambda:{'total_tokens':0})
        factory=Mock(return_value=fake_llm)
        destination=diagnostic_destination(self.root,ID)
        def runner(text,llm,root,**kwargs):
            self.assertEqual((text,llm,root),('synthetic',fake_llm,self.root))
            kwargs['diagnostics'].phase('publication')
            return {'generation':ID+'-'+'b'*32}, object()
        with patch.object(OperationalReceipt,'capture',return_value=nullcontext()):
            run_operational_analysis(path,self.root,factory,analysis_id=ID,destination=destination,runner=runner,secrets_factory=lambda:())
        record=json.loads((destination/'receipt.json').read_text())
        self.assertEqual(record['status'],'succeeded')
        self.assertEqual(record['generation'],ID+'-'+'b'*32)
        self.assertIsNone(record['usage']['total_tokens'])

    def test_write_failure_does_not_replace_analysis_error_or_receipt_result(self):
        tracker=self.receipt()
        with patch('agents.operational_diagnostics.atomic_write_text',side_effect=OSError(SECRET)):
            tracker.diagnostics.phase('detection')
            record=tracker.finish('failed')
        self.assertTrue(record['checkpoint_write_failed'])
        self.assertNotIn(SECRET,json.dumps(record))

    def test_identifiers_and_linked_directories_rejected_and_attempts_bounded(self):
        with self.assertRaises(ValueError): diagnostic_destination(self.root,'../outside')
        tracker=self.receipt()
        sdk=SimpleNamespace(completion=lambda:response())
        with patch.dict(sys.modules,{'litellm':sdk}),tracker.capture():
            for _ in range(105):sdk.completion()
        record=tracker.finish('succeeded')
        self.assertEqual(len(record['attempts']),100)
        self.assertEqual(record['dropped_transport_attempts'],5)
        self.assertFalse(record['usage']['complete'])
        with patch('pathlib.Path.is_symlink',return_value=True), self.assertRaises(ContractError):self.receipt()

    def test_process_timeout_preserves_checkpoint_and_omits_stderr(self):
        import pipeline
        def timeout(*args,**kwargs):
            destination=Path(kwargs['env']['STRUCTURED_DIAGNOSTICS_DIR'])
            destination.mkdir(parents=True)
            (destination/'checkpoint.json').write_text('{"partial":true}')
            raise subprocess.TimeoutExpired(args[0],900,output=SECRET,stderr=SECRET)
        with patch.dict(os.environ,{'ANALYSIS_ENGINE_MODE':'structured','ENGINE_DIAGNOSTICS_DIR':str(self.root)}), \
                patch.object(pipeline,'REPORT_PATH',self.root),patch.object(pipeline.subprocess,'run',side_effect=timeout):
            self.assertFalse(pipeline.run_engine(analysis_id=ID))
        destination=next((self.root/'analysis-diagnostics').iterdir())
        self.assertEqual((destination/'checkpoint.json').read_text(),'{"partial":true}')
        self.assertEqual(json.loads((destination/'process.json').read_text())['process_status'],'process_timeout')
        self.assertFalse((destination/'receipt.json').exists())
        self.assertNotIn(SECRET,''.join(p.read_text() for p in destination.iterdir()))

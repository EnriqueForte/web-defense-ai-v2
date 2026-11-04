"""Unified workflow regressions; temporary stores and mocks, no live services."""
import contextlib
import importlib
import io
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch

import webdefensev2
from dashboard.services.runtime_lock import exclusive_lock


class UnifiedLauncherTests(TestCase):
    def test_default_starts_idle_manual_executor(self):
        with patch('webdefense.main', return_value=0) as launch, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(webdefensev2.main([]), 0)
        self.assertIn('--enable-manual', launch.call_args.args[0])
        self.assertIn('--with-puerto-umbral', launch.call_args.args[0])

    def test_read_only_is_explicit(self):
        with patch('webdefense.main', return_value=0) as launch, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(webdefensev2.main(['--read-only']), 0)
        self.assertNotIn('--enable-manual', launch.call_args.args[0])


class UnifiedApiTests(TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / 'analysis.sqlite3'
        self.enterContext(patch.dict(os.environ, {
            'ANALYSIS_DB_PATH': str(self.db), 'ANALYSIS_MANUAL_ENABLED': '1',
            'LOG_SYNC_SOURCE': 'puerto-umbral', 'LOG_CAPTURE_MANUAL_ENABLED': '1',
        }))
        with patch('dotenv.load_dotenv', return_value=False):
            self.web = importlib.import_module('dashboard.app')
        self.enterContext(patch.dict(self.web.app.config, TESTING=True))
        self.enterContext(patch.object(self.web, '_executor_status', return_value='online'))
        self.enterContext(patch.object(self.web, '_job_response', side_effect=lambda job: {'data': job}))
        self.client = self.web.app.test_client()
        self.headers = {'Origin': 'http://127.0.0.1:3000', 'Idempotency-Key': 'unified-one'}

    def test_capture_allowed_with_idle_executor(self):
        with patch('dashboard.services.puerto_umbral_capture.capture_access_log', return_value=object()) as capture, \
             patch('dashboard.services.puerto_umbral_capture.source_status', return_value={'status': 'available'}):
            response = self.client.post('/api/v1/fuentes/log/capturar', json={}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        capture.assert_called_once()

    def test_analysis_stops_owned_follow_before_enqueue(self):
        follow = Mock()
        follow.status.return_value = {'session_active': True, 'owned_here': True}
        follow.control.return_value = {'session_active': False}
        with patch('dashboard.services.puerto_umbral_follow.follower', return_value=follow):
            response = self.client.post('/api/v1/analisis', headers=self.headers)
        self.assertEqual(response.status_code, 202)
        follow.control.assert_called_once_with('stop')
        self.assertEqual(self.web.JobStore().latest()['status'], 'queued')

    def test_unconfirmed_stop_does_not_enqueue(self):
        follow = Mock()
        follow.status.return_value = {'session_active': True, 'owned_here': True}
        follow.control.return_value = {'session_active': True}
        with patch('dashboard.services.puerto_umbral_follow.follower', return_value=follow):
            response = self.client.post('/api/v1/analisis', headers=self.headers)
        self.assertEqual(response.status_code, 409)
        self.assertFalse(self.db.exists())

    def test_busy_cycle_prevents_admission(self):
        follow = Mock()
        follow.status.return_value = {'session_active': False}
        with patch('dashboard.services.puerto_umbral_follow.follower', return_value=follow), \
             exclusive_lock(self.db.with_suffix('.cycle.lock')):
            response = self.client.post('/api/v1/analisis', headers=self.headers)
        self.assertEqual(response.status_code, 409)
        self.assertFalse(self.db.exists())

    def test_source_selection_is_local_and_does_not_capture(self):
        with patch.object(self.web, 'select_mode') as select, \
             patch.object(self.web, '_log_source_data', return_value={'mode': 'vulnerable'}), \
             patch('dashboard.services.puerto_umbral_capture.capture_access_log') as capture:
            response = self.client.put('/api/v1/fuentes/log/modo', json={'mode': 'vulnerable'}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        select.assert_called_once_with('vulnerable')
        capture.assert_not_called()

    def test_pending_analysis_blocks_source_selection(self):
        self.web.JobStore().enqueue('manual', 'pending')
        with patch.object(self.web, 'select_mode') as select:
            response = self.client.put('/api/v1/fuentes/log/modo', json={'mode': 'vulnerable'}, headers=self.headers)
        self.assertEqual(response.status_code, 409)
        select.assert_not_called()

    def test_unknown_source_is_rejected(self):
        with patch.object(self.web, 'select_mode') as select:
            response = self.client.put('/api/v1/fuentes/log/modo', json={'mode': 'other'}, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        select.assert_not_called()

    def test_idle_executor_does_not_block_follow_api(self):
        follow = Mock()
        with patch.dict(os.environ, {'LOG_FOLLOW_ENABLED': '1'}), \
             patch('dashboard.services.puerto_umbral_follow.follower', return_value=follow), \
             patch.object(self.web, 'selected_mode', return_value='vulnerable'), \
             patch.object(self.web, '_log_source_data', return_value={'mode': 'vulnerable'}):
            response = self.client.post('/api/v1/fuentes/log/seguimiento/iniciar',
                                        json={'interval_seconds': 5, 'duration_seconds': 300}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        follow.start.assert_called_once_with(mode='vulnerable', db_path=self.db,
                                            interval_seconds=5, duration_seconds=300)


class SharedSourceTests(TestCase):
    def setUp(self):
        from dashboard.services import puerto_umbral_mode
        self.subject = puerto_umbral_mode
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.path = root / '.local-state/launcher/session/source-mode.json'
        self.path.parent.mkdir(parents=True)
        self.enterContext(patch.object(self.subject, 'ROOT', root))
        self.enterContext(patch.dict(os.environ, {
            'PUERTO_UMBRAL_MODE_FILE': str(self.path), 'PUERTO_UMBRAL_MODE': 'corrected',
        }))

    def test_each_read_observes_shared_selection(self):
        self.subject.select_mode('corrected')
        self.assertEqual(self.subject.selected_mode(), 'corrected')
        self.subject.select_mode('vulnerable')
        self.assertEqual(self.subject.selected_mode(), 'vulnerable')

    def test_corrupt_selection_never_falls_back_to_environment(self):
        self.path.write_text('{}', encoding='utf-8')
        with self.assertRaises(ValueError):
            self.subject.selected_mode()

    def test_path_outside_session_state_is_rejected(self):
        with patch.dict(os.environ, {'PUERTO_UMBRAL_MODE_FILE': str(Path(self.temp.name) / 'source-mode.json')}):
            with self.assertRaises(ValueError):
                self.subject.select_mode('vulnerable')

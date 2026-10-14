"""Recovery preserves synthetic rows/publications and rejects unsafe archives."""
from contextlib import closing
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import stat
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from zipfile import ZipFile, ZipInfo

from agents.evidence_preparation import prepare_evidence
from dashboard.services.analysis_jobs import JobStore
from dashboard.services.structured_publication import publish, load_current
from scripts.backup_operational import PROFILES, backup
from scripts import restore_operational as recovery


class OperationalRestoreTests(TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory()))
        definition = PROFILES['pilot']
        log = self.root / definition['log']
        log.parent.mkdir(parents=True)
        log.write_text('synthetic log', encoding='utf-8')
        self.db = self.root / definition['db']
        store = JobStore(self.db)
        job, _ = store.enqueue('manual', 'synthetic-idempotency-key')
        store.claim()
        store.delivery(job['id'], 'email', 'attempting')
        store.delivery(job['id'], 'email', 'unknown')
        store.finish(job['id'], 'succeeded')
        normal = prepare_evidence('192.0.2.1 - - [14/Oct/2026:12:00:00 +0000] "GET / HTTP/1.1" 200 1', 'a' * 32)
        envelope = {'schema_version': '1', 'analysis_id': 'a' * 32}
        publish(self.root / definition['reports'] / 'structured', normal,
                {**envelope, 'candidates': []}, {**envelope, 'classifications': []},
                {**envelope, 'summary': 'synthetic', 'recommendations': []}, model='offline', prompt_version='test')
        diagnostics = self.root / definition['reports'] / 'analysis-diagnostics' / ('a' * 32 + '-' + 'b' * 32)
        diagnostics.mkdir(parents=True)
        for name in ('checkpoint.json', 'receipt.json', 'process.json'):
            (diagnostics / name).write_text('{"synthetic_metadata":true}', encoding='utf-8')
        (diagnostics / 'private.json').write_text('SYNTHETIC-PRIVATE-EXCLUDED', encoding='utf-8')
        self.source, self.manifest = backup(self.root, ('pilot',))

    def write_manifest(self, manifest):
        (self.source / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    def test_restores_all_job_and_delivery_fields_and_valid_publication_without_live_changes(self):
        before = {p: p.read_bytes() for p in (self.db, self.source / 'operational.zip', self.source / 'manifest.json')}
        def rows(path, table, order):
            with closing(sqlite3.connect(path)) as db:
                return db.execute(f'SELECT * FROM {table} ORDER BY {order}').fetchall()
        original_jobs = rows(self.db, 'jobs', 'id')
        original_deliveries = rows(self.db, 'deliveries', 'job_id,destination')
        destination, review = recovery.restore(self.source, root=self.root)
        restored_db = destination / PROFILES['pilot']['db']
        self.assertEqual(rows(restored_db, 'jobs', 'id'), original_jobs)
        self.assertEqual(rows(restored_db, 'deliveries', 'job_id,destination'), original_deliveries)
        self.assertEqual(review['profiles']['pilot']['deliveries'], {'unknown': 1})
        original = load_current(self.root / PROFILES['pilot']['reports'] / 'structured')
        self.assertEqual(load_current(destination / PROFILES['pilot']['reports'] / 'structured'), original)
        self.assertTrue(review['verified'])
        self.assertTrue((destination / 'recovery-review.json').is_file())
        restored_diagnostics = destination / PROFILES['pilot']['reports'] / 'analysis-diagnostics'
        self.assertEqual({p.name for p in restored_diagnostics.rglob('*.json')},
                         {'checkpoint.json', 'receipt.json', 'process.json'})
        for path in restored_diagnostics.rglob('*.json'):
            self.assertEqual(path.read_text(encoding='utf-8'), '{"synthetic_metadata":true}')
        for path, body in before.items():
            self.assertEqual(path.read_bytes(), body)
        second, _ = recovery.restore(self.source, root=self.root)
        self.assertNotEqual(destination, second)

    def test_rejects_unverified_manifest_wrong_kinds_and_private_paths_before_creating_destination(self):
        variations = []
        manifest = deepcopy(self.manifest); manifest['verified'] = False; variations.append(manifest)
        manifest = deepcopy(self.manifest); next(iter(manifest['files'].values()))['kind'] = 'directory'; variations.append(manifest)
        for name in ('.env', 'reports/.env.md', '../outside.md', 'reports/CON.md', 'reports/A.md '):
            manifest = deepcopy(self.manifest)
            manifest['files'][name] = {'bytes': 1, 'sha256': '0' * 64, 'kind': 'file'}
            variations.append(manifest)
        for manifest in variations:
            with self.subTest(manifest_files=list(manifest['files'])):
                self.write_manifest(manifest)
                with self.assertRaises(ValueError): recovery.restore(self.source, root=self.root)
                self.assertFalse((self.root / '.local-state/recovery').exists())

    def test_duplicate_manifest_keys_windows_aliases_and_size_limits_are_rejected(self):
        (self.source / 'manifest.json').write_text('{"verified":true,"verified":false}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'duplicate_manifest_key'):
            recovery.restore(self.source, root=self.root)
        manifest = deepcopy(self.manifest)
        name = next(name for name in manifest['files'] if name.endswith('.md'))
        prefix, leaf = name.rsplit('/', 1)
        manifest['files'][prefix + '/' + leaf[:-3].upper() + '.md'] = deepcopy(manifest['files'][name])
        # Case-insensitive aliases are invalid on both platforms.
        with self.assertRaisesRegex(ValueError, 'duplicate_backup_path'): recovery.validate_manifest(manifest)
        manifest = deepcopy(self.manifest)
        next(iter(manifest['files'].values()))['bytes'] = recovery.MAX_FILE_BYTES + 1
        with self.assertRaisesRegex(ValueError, 'invalid_backup_entry'):
            recovery.validate_manifest(manifest)

    def test_tampered_archive_and_corrupt_publication_never_publish_verified_recovery(self):
        with ZipFile(self.source / 'operational.zip') as archive:
            bodies = {name: archive.read(name) for name in archive.namelist()}
        pointer_name = PROFILES['pilot']['reports'] + '/structured/current.json'
        bodies[pointer_name] = b'{}'
        with ZipFile(self.source / 'operational.zip', 'w') as archive:
            for name, body in bodies.items(): archive.writestr(name, body)
        with self.assertRaises(ValueError): recovery.restore(self.source, root=self.root)
        self.assertFalse(any((self.root / '.local-state/recovery').glob('*/recovery-review.json')))
        manifest = deepcopy(self.manifest)
        manifest['files'][pointer_name].update(bytes=2, sha256=hashlib.sha256(b'{}').hexdigest())
        self.write_manifest(manifest)
        with self.assertRaises(ValueError): recovery.restore(self.source, root=self.root)
        self.assertFalse(any((self.root / '.local-state/recovery').glob('*/recovery-review.json')))

    def test_linked_recovery_root_is_rejected_without_following_it(self):
        linked = self.root / '.local-state/recovery'
        linked.mkdir()
        original = Path.is_symlink
        with patch.object(Path, 'is_symlink', lambda path: path == linked or original(path)):
            with self.assertRaises(ValueError): recovery.restore(self.source, root=self.root)
        self.assertEqual(list(linked.iterdir()), [])

    def test_archived_active_jobs_are_refused_without_reconciling_or_replaying_deliveries(self):
        with ZipFile(self.source / 'operational.zip') as archive:
            bodies = {name: archive.read(name) for name in archive.namelist()}
        name = PROFILES['pilot']['db']
        changed_db = self.root / 'modified-copy.sqlite3'
        changed_db.write_bytes(bodies[name])
        with closing(sqlite3.connect(changed_db)) as db:
            db.execute("UPDATE jobs SET status='queued'")
            db.commit()
        bodies[name] = changed_db.read_bytes()
        manifest = deepcopy(self.manifest)
        manifest['files'][name].update(bytes=len(bodies[name]), sha256=hashlib.sha256(bodies[name]).hexdigest())
        self.write_manifest(manifest)
        with ZipFile(self.source / 'operational.zip', 'w') as archive:
            for name, body in bodies.items(): archive.writestr(name, body)
        with self.assertRaisesRegex(ValueError, 'restored_active_jobs'):
            recovery.restore(self.source, root=self.root)
        self.assertFalse(any((self.root / '.local-state/recovery').glob('*/recovery-review.json')))
        with closing(sqlite3.connect(self.db)) as db:
            self.assertEqual(db.execute('SELECT status FROM jobs').fetchone()[0], 'succeeded')
            self.assertEqual(db.execute('SELECT status FROM deliveries').fetchone()[0], 'unknown')

    def test_symlink_zip_entry_is_rejected_before_extraction(self):
        with ZipFile(self.source / 'operational.zip') as archive:
            bodies = {name: archive.read(name) for name in archive.namelist()}
        linked = next(name for name in bodies if name.endswith('.md'))
        with ZipFile(self.source / 'operational.zip', 'w') as archive:
            for name, body in bodies.items():
                info = ZipInfo(name)
                info.external_attr = (stat.S_IFLNK | 0o777) << 16 if name == linked else 0
                archive.writestr(info, body)
        with self.assertRaisesRegex(ValueError, 'invalid_archive_member'):
            recovery.restore(self.source, root=self.root)
        self.assertFalse((self.root / '.local-state/recovery').exists())

    def test_cli_failure_does_not_log_archive_contents_or_traceback(self):
        with patch.object(recovery, 'restore', side_effect=ValueError('SYNTHETIC-PRIVATE-CONTENT')), \
                patch('sys.argv', ['restore_operational.py', '--backup', str(self.source)]), \
                patch('sys.stderr', new_callable=io.StringIO) as output:
            self.assertEqual(recovery.main(), 1)
        self.assertNotIn('SYNTHETIC-PRIVATE-CONTENT', output.getvalue())
        self.assertNotIn('Traceback', output.getvalue())

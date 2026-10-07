"""Backup/restore of synthetic sources including SQLite WAL and ambiguous delivery."""
from pathlib import Path
from contextlib import closing
import hashlib
import json
import io
import sqlite3
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from zipfile import ZipFile

from dashboard.services.analysis_jobs import JobStore
from dashboard.services.read_store import CapturedFile
from dashboard.services.runtime_lock import AlreadyRunning, exclusive_lock
from scripts import backup_operational as recovery


class OperationalBackupTests(TestCase):
    def test_cli_reports_busy_lock_without_traceback_or_accessing_real_sources(self):
        with patch.object(recovery, "backup", side_effect=AlreadyRunning("synthetic busy")), \
             patch("sys.argv", ["backup_operational.py", "--profile", "pilot"]), \
             patch("sys.stderr", new_callable=io.StringIO) as error:
            self.assertEqual(recovery.main(), 1)
        self.assertIn("AlreadyRunning", error.getvalue())
        self.assertNotIn("Traceback", error.getvalue())

    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory()))
        self.definition = recovery.PROFILES["pilot"]
        self.log = self.root / self.definition["log"]
        self.log.parent.mkdir(parents=True)
        self.log.write_text("synthetic-access-only", encoding="utf-8")
        self.reports = self.root / self.definition["reports"]
        (self.reports / "historial").mkdir(parents=True)
        (self.reports / "reporte_seguridad.md").write_text("synthetic current", encoding="utf-8")
        (self.reports / "historial/reporte_test.md").write_text("synthetic historical", encoding="utf-8")
        (self.reports / ".env").write_text("synthetic-secret-never-copy", encoding="utf-8")
        (self.root / ".env").write_text("synthetic-root-secret", encoding="utf-8")
        self.db_path = self.root / self.definition["db"]
        self.store = JobStore(self.db_path)
        self.job, _ = self.store.enqueue("manual", "synthetic")
        self.store.claim()
        self.store.delivery(self.job["id"], "email", "attempting")
        self.store.delivery(self.job["id"], "email", "unknown")
        self.store.finish(self.job["id"], "succeeded")

    def test_full_roundtrip_and_source_preservation(self):
        before = {p: p.read_bytes() for p in (self.log, self.db_path, self.reports / "reporte_seguridad.md")}
        destination, manifest = recovery.backup(self.root, ("pilot",))
        self.assertTrue(manifest["verified"])
        self.assertEqual(len(manifest["files"]), 4)
        self.assertEqual(json.loads((destination / "manifest.json").read_text())["verified"], True)
        with ZipFile(destination / "operational.zip") as zipped:
            self.assertNotIn(".env", zipped.namelist())
            self.assertNotIn(self.definition["reports"] + "/.env", zipped.namelist())
            self.assertFalse(any(name.endswith((".lock", "-wal", "-shm")) for name in zipped.namelist()))
        restored_db = destination / "restore-check" / self.definition["db"]
        with closing(sqlite3.connect(restored_db)) as connection:
            self.assertEqual(connection.execute("SELECT status FROM deliveries").fetchone()[0], "unknown")
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)
        second, _ = recovery.backup(self.root, ("pilot",))
        self.assertNotEqual(destination, second)

    def test_wal_changes_are_included_without_copying_live_wal_files(self):
        connection = sqlite3.connect(self.db_path)
        self.addCleanup(connection.close)
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("UPDATE worker SET heartbeat_at='unused' WHERE singleton=1")
        connection.execute("INSERT INTO worker VALUES (1,'synthetic-worker','2026-10-06T00:00:00Z')")
        connection.commit()
        self.assertTrue(Path(str(self.db_path) + "-wal").exists())
        destination, _ = recovery.backup(self.root, ("pilot",))
        restored = sqlite3.connect(destination / "restore-check" / self.definition["db"])
        self.addCleanup(restored.close)
        self.assertEqual(restored.execute("SELECT instance_id FROM worker").fetchone()[0], "synthetic-worker")

    def test_active_job_is_not_changed_or_reconciled(self):
        active, _ = self.store.enqueue("manual", "active")
        with self.assertRaises(ValueError):
            recovery.backup(self.root, ("pilot",))
        self.assertEqual(self.store.get(active["id"])["status"], "queued")
        manifests = list((self.root / ".local-backups").glob("*/manifest.json"))
        self.assertEqual(len(manifests), 1)
        self.assertFalse(json.loads(manifests[0].read_text())["verified"])

    def test_busy_cycle_refuses_before_creating_archive(self):
        with exclusive_lock(self.db_path.with_suffix(".cycle.lock")), self.assertRaises(AlreadyRunning):
            recovery.backup(self.root, ("pilot",))
        self.assertFalse((self.root / ".local-backups").exists())

    def test_changed_source_never_becomes_verified_archive(self):
        original = recovery.capture_file
        def changing(path):
            capture = original(path)
            if path == self.log:
                return CapturedFile(path, None, "changing")
            return capture
        # The injected failure occurs before publication and leaves originals intact.
        with patch.object(recovery, "capture_file", side_effect=changing), self.assertRaises(ValueError):
            recovery.backup(self.root, ("pilot",))
        manifest = next((self.root / ".local-backups").glob("*/manifest.json"))
        self.assertFalse(json.loads(manifest.read_text())["verified"])
        self.assertFalse((manifest.parent / "operational.zip").exists())

    def test_restore_refuses_existing_destination_and_tampered_content(self):
        destination, manifest = recovery.backup(self.root, ("pilot",))
        with self.assertRaises(ValueError):
            recovery.verify_restore(destination / "operational.zip", manifest, self.reports)
        tampered = self.root / "tampered.zip"
        with ZipFile(tampered, "w") as zipped:
            for name in manifest["files"]:
                zipped.writestr(name, "tampered")
        with self.assertRaises(ValueError):
            recovery.verify_restore(tampered, manifest, self.root / "isolated-tamper-check")

    def test_restore_path_escape_is_rejected(self):
        archive = self.root / "unsafe.zip"
        content = b"synthetic"
        with ZipFile(archive, "w") as zipped:
            zipped.writestr("../escaped.md", content)
        manifest = {"files": {"../escaped.md": {"bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(), "kind": "file"}}}
        with self.assertRaises(ValueError):
            recovery.verify_restore(archive, manifest, self.root / "isolated-unsafe-check")
        self.assertFalse((self.root / "escaped.md").exists())

    def test_linked_source_or_external_path_is_rejected(self):
        original = Path.is_symlink
        with patch.object(Path, "is_symlink", lambda path: True if path == self.log else original(path)):
            with self.assertRaises(ValueError):
                recovery.collect_sources(self.root, ("pilot",))
        with self.assertRaises(ValueError):
            recovery.checked_path(self.root, "../outside")

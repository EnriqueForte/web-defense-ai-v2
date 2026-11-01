"""Isolated observer checks: synthetic API states/temp SQLite, no app or transport."""
import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from scripts import observe_puerto_umbral_follow as observer


def state(cycle):
    return {"status": "available", "snapshot_id": "b" * 32, "sha256": "c" * 64,
            "following": {"enabled": True, "session_active": True, "session_id": "a" * 32,
                          "status": "following", "mode": "corrected", "interval_seconds": 5,
                          "duration_seconds": 300, "error_code": None, "cycles": cycle,
                          "analysis_requested": False, "notifications_requested": False,
                          "in_flight": False, "last_cycle_at": "2026-11-02T12:00:00Z",
                          "last_success_at": "2026-11-02T12:00:00.050Z", "last_cycle_seconds": .05,
                          "checkpoint": {"snapshot_id": "b" * 32, "sha256": "c" * 64},
                          "snapshots_published": 0, "unchanged_cycles": cycle}}


INITIAL = {"following": {"enabled": True, "session_active": False, "session_id": "d" * 32}}
DB = {"jobs": {"count": 1, "sha256": "e" * 64}, "deliveries": {"count": 0, "sha256": "f" * 64}}


class FollowObserverTests(TestCase):
    def test_default_help_never_observes_or_reads_operational_state(self):
        with patch.object(observer, "observe") as run, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(observer.main([]), 0)
        run.assert_not_called()

    def test_transport_is_fixed_get_with_redirects_and_oversized_input_rejected(self):
        self.assertIsNone(observer.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.invalid"))
        with patch.object(observer, "build_opener") as factory:
            opener = factory.return_value
            response = opener.open.return_value.__enter__.return_value
            response.status = 200
            response.read.return_value = b"x" * 65537
            with self.assertRaisesRegex(observer.ObservationError, "invalid_source_response"):
                observer.read_source(opener)
            opener.open.assert_called_once_with(observer.URL, timeout=2)
            response.read.assert_called_once_with(65537)

    def test_database_fingerprint_preserves_original_bytes_and_excludes_private_fields(self):
        with TemporaryDirectory() as folder, patch.object(observer, "ROOT", Path(folder)), \
                patch.object(observer, "STATE", Path(folder) / "state"):
            observer.STATE.mkdir()
            path = observer.STATE / "analysis.sqlite3"
            with contextlib.closing(sqlite3.connect(path)) as db:
                db.executescript("CREATE TABLE jobs(id,status,phase,requested_at,started_at,finished_at);"
                                 "INSERT INTO jobs VALUES('j','succeeded','finished','t','t','t');"
                                 "CREATE TABLE deliveries(job_id,status,attempted_at,destination);"
                                 "INSERT INTO deliveries VALUES('j','sent','t','private-fixture-destination');")
                db.commit()
            before = path.read_bytes()
            result = observer.database_state()
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(result["jobs"]["count"], 1)
            self.assertEqual(result["deliveries"]["count"], 1)
            self.assertNotIn("private-fixture-destination", json.dumps(result))

    def observe_fixture(self, folder, responses):
        with patch.object(observer, "ROOT", Path(folder)), patch.object(observer, "STATE", Path(folder) / "state"), \
                patch.object(observer, "build_opener"), patch.object(observer, "read_source", side_effect=responses) as read, \
                patch.object(observer, "database_state", return_value=DB), \
                patch.object(observer, "snapshot_ids", return_value={"b" * 32}), \
                patch.object(observer.time, "sleep"), patch.object(observer.time, "monotonic", return_value=0), \
                patch.object(observer, "now", return_value=datetime(2026, 11, 2, 12, 0, 10, tzinfo=timezone.utc)), \
                contextlib.redirect_stdout(io.StringIO()):
            code = observer.observe()
        receipts = list((Path(folder) / "state/operational-review").glob("follow-*.json"))
        self.assertEqual(len(receipts), 1)
        return code, json.loads(receipts[0].read_text()), read.call_count

    def test_twenty_distinct_cycles_ignore_duplicate_polls_and_keep_originals(self):
        with TemporaryDirectory() as folder:
            sentinel = Path(folder) / "source.log"
            sentinel.write_bytes(b"original fixture\n")
            responses = [INITIAL, state(1), state(1), *(state(cycle) for cycle in range(2, 21))]
            code, result, calls = self.observe_fixture(folder, responses)
            self.assertEqual(code, 0)
            self.assertEqual([s["cycle"] for s in result["samples"]], list(range(1, 21)))
            self.assertEqual(calls, 22)
            self.assertTrue(result["database_unchanged"])
            self.assertTrue(result["single_checkpoint_observed"])
            self.assertTrue(result["all_observed_api_bounds_within_10_seconds"])
            self.assertFalse(result["browser_paint_measured"])
            self.assertEqual(result["control_requests"], 0)
            self.assertEqual(sentinel.read_bytes(), b"original fixture\n")

    def test_read_failure_preserves_partial_measurements_without_inventing_success(self):
        with TemporaryDirectory() as folder:
            code, result, calls = self.observe_fixture(folder, [INITIAL, state(1), RuntimeError("synthetic-private-detail")])
            self.assertEqual(code, 1)
            self.assertEqual(result["status"], "incomplete")
            self.assertEqual(len(result["samples"]), 1)
            self.assertEqual(calls, 3)
            self.assertEqual(result["error_code"], "RuntimeError")
            self.assertNotIn("synthetic-private-detail", json.dumps(result))
            self.assertIsNot(result.get("all_observed_api_bounds_within_10_seconds"), True)

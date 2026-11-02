"""Isolated synthetic packaging tests. Never use them as detector evidence."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import prepare_puerto_umbral_evaluation as subject


class EvaluationPackTests(unittest.TestCase):
    def index(self):
        return json.loads(subject.INDEX.read_text(encoding="utf-8"))

    def fixture(self, root):
        index = copy.deepcopy(self.index())
        archive = root / "archive"
        archive.mkdir()
        corpus = root / "corpus.json"
        corpus.write_bytes(b"{}")
        (archive / "suite.json").write_bytes(b"{}")
        inputs = {"corpus.json": b"{}", "suite.json": b"{}"}
        for ordinal, row in enumerate(index["cases"], 1):
            count = row["correlated_access_line_count"]
            lines = [f'172.20.0.{ordinal} - - [26/Oct/2026:18:00:{n:02d} +0000] "GET /normal?marker={ordinal}-{n} HTTP/1.1" 200 2' for n in range(count)]
            raw = ("\n".join(lines) + "\n").encode()
            snapshot = {"file": "access-0000000000000000.log", "sha256": subject.digest(raw),
                        "bytes": len(raw), "matches": [{"line": n, "sha256": subject.digest(line.encode())}
                                                        for n, line in enumerate(lines, 1)]}
            receipt_raw = json.dumps({"access_snapshot": snapshot}).encode()
            directory = archive / "runs" / row["execution_id"]
            directory.mkdir(parents=True)
            (directory / snapshot["file"]).write_bytes(raw)
            (directory / "receipt.json").write_bytes(receipt_raw)
            inputs[f"runs/{row['execution_id']}/{snapshot['file']}"] = raw
            inputs[f"runs/{row['execution_id']}/receipt.json"] = receipt_raw
        index["inputs"] = {name: {"sha256": subject.digest(raw), "bytes": len(raw)} for name, raw in inputs.items()}
        return index, archive, corpus

    def test_plan_has_fixed_denominators_and_no_metrics(self):
        result = subject.plan(self.index())
        self.assertEqual(sum(row["lines"] for row in result["batches"]), 75)
        self.assertEqual(sum(row["cases"] for row in result["batches"]), 45)
        self.assertIsNone(result["detector_metrics"])
        self.assertFalse(result["model_contacted"])

    def test_changed_balance_is_rejected(self):
        index = self.index()
        index["cases"][0]["kind"] = "benign"
        with self.assertRaises(ValueError):
            subject.plan(index)

    def test_pack_separates_labels_and_maps_every_case(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            index, archive, corpus = self.fixture(root)
            with patch("scripts.review_puerto_umbral_evidence.review", return_value=index):
                result = subject.package(archive, corpus, root / "output", index, b"synthetic index")
            self.assertEqual(result["status"], "prepared_not_evaluated")
            manifest = json.loads((root / "output/evaluator/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(sum(len(row["cases"]) for row in manifest["batches"]), 45)
            for batch in manifest["batches"]:
                raw = (root / f"output/detector/{batch['batch']}.log").read_bytes()
                self.assertEqual(subject.digest(raw), batch["input_sha256"])
                self.assertEqual(len(raw.splitlines()), 25)
                for case in batch["cases"]:
                    self.assertTrue(case["line_numbers"])
                    self.assertNotIn(case["case_id"].encode(), raw)
            with patch("scripts.review_puerto_umbral_evidence.review", return_value=index):
                with self.assertRaises(FileExistsError):
                    subject.package(archive, corpus, root / "output", index, b"synthetic index")

    def test_changed_archive_fails_before_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            index, archive, corpus = self.fixture(root)
            (archive / "suite.json").write_bytes(b"changed")
            with patch("scripts.review_puerto_umbral_evidence.review", return_value=index):
                with self.assertRaises(ValueError):
                    subject.package(archive, corpus, root / "output", index, b"synthetic index")
            self.assertFalse((root / "output").exists())

    def test_missing_archive_is_not_reconstructed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            corpus = root / "corpus.json"
            corpus.write_bytes(b"{}")
            with self.assertRaises((OSError, ValueError, KeyError)):
                subject.package(root / "absent", corpus, root / "output", self.index(), b"index")
            self.assertFalse((root / "output").exists())


if __name__ == "__main__":
    unittest.main()

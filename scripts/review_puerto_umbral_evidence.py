"""Review an existing F2 archive offline; never run scenarios, Docker or models.

Only suite.json, its referenced receipts/access snapshots and the selected
corpus are read. Output contains identifiers, counts and digests, never URLs,
request bodies, response bodies, credentials or absolute source paths.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]


class EvidenceError(ValueError):
    pass


def review(state_root, corpus_path):
    state_root = Path(state_root).absolute()
    corpus_path = Path(corpus_path).absolute()
    inputs = {}

    def read(path, label, limit):
        path = Path(path).absolute()
        for candidate in (path, *path.parents):
            info = candidate.lstat()
            if candidate.is_symlink() or getattr(info, "st_file_attributes", 0) & 1024:
                raise EvidenceError("linked_input_rejected")
        before = path.stat()
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise EvidenceError("input_size_or_type_rejected")
        raw = path.read_bytes()
        after = path.stat()
        if (before.st_size != after.st_size or len(raw) != after.st_size
                or before.st_mtime_ns != after.st_mtime_ns or before.st_ino != after.st_ino):
            raise EvidenceError("input_changed_during_read")
        fingerprint = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        if label in inputs and inputs[label][1] != fingerprint:
            raise EvidenceError("input_changed_during_review")
        inputs[label] = (path, fingerprint, limit)
        return raw

    corpus_raw = read(corpus_path, "corpus.json", 1024 * 1024)
    corpus = json.loads(corpus_raw)
    suite_raw = read(state_root / "suite.json", "suite.json", 1024 * 1024)
    suite = json.loads(suite_raw)
    canonical = {case["case_id"]: case for case in corpus["cases"]}
    saved = {case["case_id"]: case for case in suite["cases"]}
    if (len(canonical) != len(corpus["cases"]) or len(saved) != len(suite["cases"])
            or set(canonical) != set(saved) or suite["total"] != len(canonical)
            or suite["version"] != corpus["version"]
            or suite.get("kind") != "functional_http_not_v2_evaluation"
            or suite["corpus_sha256"] != hashlib.sha256(corpus_raw).hexdigest()):
        raise EvidenceError("suite_corpus_mismatch")
    results = []
    for identifier, case in canonical.items():
        entry = saved[identifier]
        for key in ("scenario", "variant", "mode", "kind", "expected_effect"):
            if entry[key] != case[key]:
                raise EvidenceError("case_definition_mismatch")
        run_id = entry["run_id"]
        if not isinstance(run_id, str) or not re.fullmatch(r"[a-f0-9]{32}", run_id):
            raise EvidenceError("invalid_saved_execution_id")
        receipt_name = f"runs/{run_id}/receipt.json"
        receipt = json.loads(read(state_root / receipt_name, receipt_name, 1024 * 1024))
        if (receipt["id"] != run_id or receipt["version"] != corpus["version"]
                or receipt["seed"] != corpus["seed"] or receipt.get("v2_consulted") is not False
                or any(receipt[key] != case[key] for key in ("scenario", "variant", "mode", "kind"))):
            raise EvidenceError("receipt_identity_mismatch")
        snapshot = receipt["access_snapshot"]
        if not re.fullmatch(r"access-[a-f0-9]{16}\.log", snapshot["file"]):
            raise EvidenceError("invalid_snapshot_name")
        snapshot_name = f"runs/{run_id}/{snapshot['file']}"
        access_raw = read(state_root / snapshot_name, snapshot_name, 4 * 1024 * 1024)
        if hashlib.sha256(access_raw).hexdigest() != snapshot["sha256"] or len(access_raw) != snapshot["bytes"]:
            raise EvidenceError("snapshot_digest_mismatch")
        lines = access_raw.decode("utf-8").splitlines()
        seen = set()
        for match in snapshot["matches"]:
            position = match["line"]
            if (type(position) is not int or not 1 <= position <= len(lines) or position in seen
                    or hashlib.sha256(lines[position - 1].encode()).hexdigest() != match["sha256"]):
                raise EvidenceError("snapshot_line_mismatch")
            seen.add(position)
        requests = receipt["requests"]
        for item in requests:
            if hashlib.sha256(item["body_text"].encode("utf-8")).hexdigest() != item["body_sha256"]:
                raise EvidenceError("saved_response_digest_mismatch")
        passed = entry["passed"]
        if type(passed) is not bool:
            raise EvidenceError("invalid_saved_verdict")
        results.append({
            **case, "expected_attempt_indicator": case["kind"] == "attempt",
            "execution_id": run_id, "execution_status": receipt["status"],
            "historical_http_conformant": passed,
            "browser_confirmation_pending": bool(entry.get("browser_confirmation_pending")),
            "browser_execution_confirmed": bool(receipt.get("browser_execution_confirmed")),
            "functional_effect_confirmed_in_receipt": bool(receipt.get("functional_effect_confirmed")),
            "saved_diagnostic": "cannot_fork_in_saved_output" if any("Cannot fork" in item["body_text"] for item in requests) else None,
            "executor_request_count": len(requests), "correlated_access_line_count": len(seen),
            "receipt_sha256": inputs[receipt_name][1]["sha256"],
            "access_snapshot_sha256": inputs[snapshot_name][1]["sha256"],
            "receipt_and_snapshot_reviewed": True,
            "detector_evaluation": "not_evaluated",
        })
    conformant = sum(item["historical_http_conformant"] for item in results)
    if suite["passed"] != conformant:
        raise EvidenceError("saved_summary_mismatch")
    # Read the exact same whitelist again, checking bytes rather than trusting
    # timestamps alone. Never rewrite or repair the original archive.
    for label, (path, _, limit) in list(inputs.items()):
        read(path, label, limit)
    by_family = {}
    for family in sorted({item["scenario"] for item in results}):
        rows = [item for item in results if item["scenario"] == family]
        by_family[family] = {"cases": len(rows), "historical_http_conformant": sum(row["historical_http_conformant"] for row in rows)}
    return {
        "schema": "puerto-umbral.archived-evidence-review.v1",
        "operation": "read_existing_evidence_only", "new_scenarios_executed": 0,
        "docker_contacted": False, "model_contacted": False,
        "historical_kind": suite["kind"], "historical_checked_at": suite["checked_at"],
        "historical_source_revision": None,
        "source_revision_limit": "Original execution predates current code; the corrected version was not rerun.",
        "corpus_version": corpus["version"], "seed": corpus["seed"],
        "corpus_sha256": inputs["corpus.json"][1]["sha256"],
        "suite_sha256": inputs["suite.json"][1]["sha256"],
        "summary": {"cases": len(results), "historical_http_conformant": conformant,
                    "historical_http_nonconformant": len(results) - conformant,
                    "kinds": dict(Counter(item["kind"] for item in results)), "by_family": by_family,
                    "executor_requests_recorded": sum(item["executor_request_count"] for item in results),
                    "correlated_access_lines_in_selected_snapshots": sum(item["correlated_access_line_count"] for item in results),
                    "browser_confirmation_pending_cases": sum(item["browser_confirmation_pending"] for item in results)},
        "integrity": {"status": "verified_for_listed_local_inputs", "input_files": len(inputs),
                      "unchanged_on_second_read": True, "scope": "Local historical files only; not VM captures or confinement verification."},
        "inputs": {label: fingerprint for label, (_, fingerprint, _) in sorted(inputs.items())},
        "cases": results,
        "detector_metrics": {"precision": None, "recall": None, "false_positive_rate": None,
                             "analysis_latency_seconds": None, "provider_cost": None,
                             "reason": "No V2 detector output or provider receipt evaluated in this review."},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", type=Path, required=True, help="Existing directory containing suite.json and runs/")
    parser.add_argument("--corpus", type=Path, default=ROOT / "labs/puerto_umbral/lab/corpus.json")
    parser.add_argument("--output", type=Path, help="New JSON file only; existing files are never overwritten")
    args = parser.parse_args()
    try:
        report = review(args.state_root, args.corpus)
        encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            if args.output.suffix.lower() != ".json":
                raise EvidenceError("json_output_required")
            with args.output.open("x", encoding="utf-8", newline="\n") as destination:
                destination.write(encoded)
            print(json.dumps({"status": "reviewed", "cases": report["summary"]["cases"],
                              "historical_http_conformant": report["summary"]["historical_http_conformant"],
                              "input_files": report["integrity"]["input_files"], "new_executions": 0}))
        else:
            print(encoded)
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError):
        print("Archived evidence review not completed; originals preserved. Check input schema, completeness and output path.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

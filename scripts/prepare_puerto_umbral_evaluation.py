"""Plan or package frozen F5 evidence offline. No network, model or scenarios.

Only --prepare creates a new directory. Expected labels stay under evaluator/;
detector/ contains only the selected historical access lines and opaque IDs.
This tool does not execute, score or accept a detector evaluation.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs/PUERTO_UMBRAL_F5_CORPUS_2026_10_27.json"
FAMILIES = {"sqli", "xss", "traversal", "command", "brute"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def plain_path(path):
    path = Path(path).absolute()
    for part in (path, *path.parents):
        if part.is_symlink() or (part.exists() and getattr(part.lstat(), "st_file_attributes", 0) & 1024):
            raise ValueError("linked_path_rejected")
    return path


def read_bytes(path, limit=4 * 1024 * 1024):
    path = plain_path(path)
    before = path.stat()
    if not path.is_file() or before.st_size > limit:
        raise ValueError("input_size_or_type_rejected")
    raw = path.read_bytes()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise ValueError("input_changed")
    return raw


def plan(index):
    if index["schema"] != "puerto-umbral.archived-evidence-review.v1":
        raise ValueError("unsupported_index")
    cases = index["cases"]
    if len(cases) != 45 or len({row["case_id"] for row in cases}) != 45:
        raise ValueError("expected_45_unique_cases")
    batches = []
    for variant in range(3):
        rows = [row for row in cases if type(row["variant"]) is int and row["variant"] == variant]
        if (len(rows) != 15 or {row["scenario"] for row in rows} != FAMILIES
                or Counter(row["kind"] for row in rows) != {"attempt": 10, "benign": 5}
                or sum(row["correlated_access_line_count"] for row in rows) != 25):
            raise ValueError("unexpected_batch_shape")
        for family in FAMILIES:
            if Counter(row["kind"] for row in rows if row["scenario"] == family) != {"attempt": 2, "benign": 1}:
                raise ValueError("unexpected_family_balance")
        batches.append({"batch": variant + 1, "cases": 15, "attempts": 10, "benign": 5, "lines": 25})
    return {"schema": "puerto-umbral.evaluation-plan.v1", "model_contacted": False,
            "new_scenarios_executed": 0, "status": "planned_not_evaluated", "batches": batches,
            "acceptance": {"attempts_detected_minimum": 27, "attempts_total": 30,
                           "per_family_detected_minimum": 5, "per_family_attempts": 6,
                           "benign_false_positives_maximum": 0, "benign_total": 15},
            "proposed_budget_not_authorized": {"maximum_transport_requests": 18,
                                              "maximum_output_tokens_per_request": 8192,
                                              "maximum_seconds_per_batch": 600,
                                              "network_retries": 0, "model_fallback": False},
            "detector_metrics": None}


def package(state_root, corpus_path, destination, index, index_raw):
    # Reuse the existing integrity reviewer, never its historical HTTP verdict as
    # detector ground truth. Lazy imports keep --help and planning stdlib-only.
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from scripts.review_puerto_umbral_evidence import review
    from agents.evidence_contracts import parse_evidence
    from agents.evidence_preparation import prepare_evidence

    result = plan(index)
    state_root, corpus_path = plain_path(state_root), plain_path(corpus_path)
    checked = review(state_root, corpus_path)
    if (checked["inputs"] != index["inputs"] or checked["cases"] != index["cases"]
            or checked["corpus_sha256"] != index["corpus_sha256"]
            or checked["suite_sha256"] != index["suite_sha256"]):
        raise ValueError("archive_differs_from_frozen_review")
    loaded = {}

    def archived(label):
        if label not in loaded:
            raw = read_bytes(corpus_path if label == "corpus.json" else state_root / label)
            if {"sha256": digest(raw), "bytes": len(raw)} != checked["inputs"][label]:
                raise ValueError("archive_changed_after_review")
            loaded[label] = raw
        return loaded[label]

    payloads, manifest_rows = {}, []
    for variant in range(3):
        identifier = uuid.uuid4().hex
        rows = [row for row in checked["cases"] if row["variant"] == variant]
        selected = []
        for row in rows:
            receipt = json.loads(archived(f"runs/{row['execution_id']}/receipt.json"))
            snapshot = receipt["access_snapshot"]
            lines = archived(f"runs/{row['execution_id']}/{snapshot['file']}").decode("utf-8").splitlines()
            for match in snapshot["matches"]:
                raw = lines[match["line"] - 1]
                if digest(raw.encode()) != match["sha256"]:
                    raise ValueError("matched_line_changed")
                parsed = parse_evidence(raw, 1, identifier, "")
                if not parsed.observed_at or not parsed.method or parsed.http_status is None:
                    raise ValueError("unparsed_historical_line")
                selected.append((parsed.observed_at, digest(raw.encode()), row["case_id"], raw))
        # Observed chronology, then raw digest. Expected labels never select or
        # order model input. Reject ambiguity rather than silently deduplicating.
        selected.sort(key=lambda item: (item[0], item[1]))
        if len(selected) != 25 or len({item[1] for item in selected}) != 25:
            raise ValueError("ambiguous_or_incomplete_batch")
        text = "\n".join(item[3] for item in selected) + "\n"
        prepared = prepare_evidence(text, identifier)
        if (prepared.bundle.omitted_lines or len(prepared.bundle.items) != 25
                or {item.line_number for item in prepared.bundle.items} != set(range(1, 26))):
            raise ValueError("production_selection_omits_evidence")
        batch_name = f"batch-{variant + 1}"
        payloads[f"detector/{batch_name}.log"] = text.encode()
        mapping = []
        for row in rows:
            mapping.append({"case_id": row["case_id"], "scenario": row["scenario"],
                            "kind": row["kind"], "mode": row["mode"],
                            "line_numbers": [n for n, item in enumerate(selected, 1) if item[2] == row["case_id"]],
                            "historical_http_conformant": row["historical_http_conformant"],
                            "saved_diagnostic": row["saved_diagnostic"]})
        manifest_rows.append({"batch": batch_name, "analysis_id": identifier,
                              "input_sha256": digest(text.encode()), "cases": mapping,
                              "preparation_scope": prepared.scope})
    # Revalidate all originals after packaging in memory, before any output.
    for label, fingerprint in checked["inputs"].items():
        raw = read_bytes(corpus_path if label == "corpus.json" else state_root / label)
        if {"sha256": digest(raw), "bytes": len(raw)} != fingerprint:
            raise ValueError("archive_changed_during_packaging")
    destination = plain_path(destination)
    if destination == state_root or state_root in destination.parents:
        raise ValueError("output_must_be_outside_archive")
    manifest = {**result, "status": "prepared_not_evaluated", "index_sha256": digest(index_raw),
                "corpus_sha256": checked["corpus_sha256"], "suite_sha256": checked["suite_sha256"],
                "batches": manifest_rows, "input_files": checked["inputs"]}
    payloads["evaluator/manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    # Exclusive directory creation: a partial failed write must never be reused.
    destination.mkdir(parents=True, exist_ok=False)
    for relative, raw in payloads.items():
        target = destination / relative
        target.parent.mkdir(exist_ok=True)
        with target.open("xb") as handle:
            handle.write(raw)
    return {"status": "prepared_not_evaluated", "batches": 3, "cases": 45,
            "model_contacted": False, "new_scenarios_executed": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=INDEX)
    parser.add_argument("--state-root", type=Path, help="Existing suite.json and runs/ archive")
    parser.add_argument("--corpus", type=Path, help="Original physical corpus.json, including its line endings")
    parser.add_argument("--prepare", type=Path, metavar="NEW_DIRECTORY", help="Create three input batches; never call a model")
    args = parser.parse_args()
    if bool(args.prepare) != bool(args.state_root) or bool(args.prepare) != bool(args.corpus):
        parser.error("--prepare, --state-root and --corpus must be supplied together")
    try:
        raw = read_bytes(args.index)
        index = json.loads(raw)
        result = package(args.state_root, args.corpus, args.prepare, index, raw) if args.prepare else plan(index)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError):
        print("F5 preparation incomplete: check original archive, digests and new output directory. No model called.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

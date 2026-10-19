"""Reproducible synthetic A-05 review; no provider, settings, jobs or lab access."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import socket
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.evaluation_fixtures import CASES, FIXTURE_VERSION, fixture, expected_evidence_groups
from agents.evaluation_scoring import METRICS_VERSION, score_fixture_result
from agents.evidence_contracts import ContractError
from agents.evidence_preparation import prepare_evidence
from dashboard.services.structured_publication import publish, load_current

ID = "e" * 32
MODEL_TEXT = "SYNTHETIC_UNSUPPORTED_EXPLOITATION_CLAIM"


def authored_payloads(prepared, case):
    """Simulated responses use authored labels, never detector output as oracle."""
    candidates = []
    for group in expected_evidence_groups(case):
        refs = [item.evidence_id for item in prepared.bundle.items if item.line_number in group["line_numbers"]]
        if refs:
            candidates.append({"candidate_id": f"c_{len(candidates) + 1}", "pattern": group["pattern"],
                               "evidence_ids": refs, "reason": MODEL_TEXT})
    detection = {"schema_version": "1", "analysis_id": ID, "candidates": candidates}
    classification = {"schema_version": "1", "analysis_id": ID, "classifications": [
        {"candidate_id": item["candidate_id"], "severity": "unknown", "state": "requires_investigation",
         "reason": MODEL_TEXT} for item in candidates]}
    narrative = {"schema_version": "1", "analysis_id": ID, "summary": MODEL_TEXT,
                 "recommendations": [{"candidate_id": item["candidate_id"], "text": MODEL_TEXT}
                                     for item in candidates]}
    return detection, classification, narrative


def fingerprints(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in root.rglob("*") if path.is_file()}


def review_matrix(destination):
    destination = Path(destination)
    reviews = []
    specifications = [(case, case, {}) for case in CASES]
    specifications += [("incomplete_other", "incomplete", {}), ("false_positive", "same_family", {}),
                       ("partial_same_family", "same_family", {}),
                       ("selection_limit", "same_family", {"max_items": 1}),
                       ("split_dvwa_burst", "dvwa_post_burst", {}),
                       ("overlapping_dvwa_burst", "dvwa_post_burst", {})]
    for name, case, selection in specifications:
        prepared = prepare_evidence(fixture(case)["text"], ID, config={}, **selection)
        payloads = authored_payloads(prepared, case)
        detection, classification, narrative = payloads
        if name == "incomplete_other":
            detection["candidates"] = [{"candidate_id": "c_1", "pattern": "other", "reason": MODEL_TEXT,
                                        "evidence_ids": [prepared.bundle.items[0].evidence_id]}]
            classification["classifications"] = [{"candidate_id": "c_1", "severity": "unknown",
                                                   "state": "requires_investigation", "reason": MODEL_TEXT}]
        elif name == "false_positive":
            classification["classifications"][0].update(state="probable_false_positive", severity="low")
        elif name == "partial_same_family":
            detection["candidates"][0]["evidence_ids"] = detection["candidates"][0]["evidence_ids"][:1]
        elif name in {"split_dvwa_burst", "overlapping_dvwa_burst"}:
            burst = detection["candidates"][1]
            refs = burst["evidence_ids"]
            burst["evidence_ids"] = refs[:4] if name == "split_dvwa_burst" else refs[:5]
            detection["candidates"].append({**burst, "candidate_id": "c_3",
                "evidence_ids": refs[4:] if name == "split_dvwa_burst" else refs[3:]})
            classification["classifications"].append({**classification["classifications"][1], "candidate_id": "c_3"})
        publication = destination / name
        publish(publication, prepared, *payloads, model="offline-authored-responses", prompt_version="a05-review-1")
        manifest, result, markdown = load_current(publication)  # verifies artifact hashes
        scores = score_fixture_result(result["findings"], result["evidence"], case)
        group_mismatch = name in {"partial_same_family", "split_dvwa_burst", "overlapping_dvwa_burst"}
        checks = {"families": scores["pattern_expectations_met"],
                  "evidence_verdict": scores["evidence_expectations_met"] == (name != "partial_same_family"),
                  "selection_verdict": scores["fixture_fully_selected"] == (name != "selection_limit"),
                  "group_verdict": scores["group_expectations_met"] == (not group_mismatch),
                  "fixture_verdict": scores["fixture_expectations_met"] == (not group_mismatch and name != "selection_limit"),
                  "counts": sum(result["counts"].values()) == len(result["findings"]),
                  "quality_pending": result["quality"] == "semantic_evaluation_pending",
                  "grounded_text": MODEL_TEXT not in markdown and MODEL_TEXT not in json.dumps(result["narrative"]),
                  "narrative_source": result["narrative_source"] == (
                      "python_validated_facts" if result["findings"] else "python_scope"),
                  "recommendation_refs": {item["candidate_id"] for item in result["narrative"]["recommendations"]}
                      == {item["candidate_id"] for item in result["findings"]}}
        if name == "partial_same_family":
            checks["omission_warning"] = "Queda 1 referencia" in result["narrative"]["summary"]
        if name == "false_positive":
            checks["cautious_false_positive"] = "antes de cambiar controles" in result["narrative"]["recommendations"][0]["text"]
        reviews.append({"name": name, "fixture_case": case, "checks": checks, "passed": all(checks.values()),
                        "generation": manifest["generation"], "sha256": manifest["sha256"], **scores})

    prepared = prepare_evidence(fixture("mixed")["text"], ID, config={})
    valid = authored_payloads(prepared, "mixed")
    publication = destination / "guard_controls"
    guard_manifest = publish(publication, prepared, *valid,
                             model="offline-authored-responses", prompt_version="a05-review-1")
    baseline = fingerprints(publication)
    controls = []
    for name, code in (("empty_detection", "empty_detection_with_observed_indicators"),
                       ("foreign_reference", "invalid_evidence_reference"),
                       ("normal_reference", "pattern_without_observation"),
                       ("unsupported_severity", "severity_without_support"),
                       ("false_positive_severity", "inconsistent_false_positive_severity"),
                       ("missing_classification", "incomplete_or_foreign_classification"),
                       ("invalid_narrative", "invalid_text"),
                       ("cross_ip_burst", "brute_without_shared_window")):
        detection, classification, narrative = deepcopy(valid)
        control_prepared = prepared
        if name == "empty_detection":
            detection["candidates"] = []
        elif name in {"foreign_reference", "normal_reference"}:
            detection["candidates"][0]["evidence_ids"] = [
                "e_foreign" if name == "foreign_reference" else prepared.bundle.items[-1].evidence_id]
        elif name == "unsupported_severity":
            classification["classifications"][0]["severity"] = "critical"
        elif name == "false_positive_severity":
            classification["classifications"][0].update(state="probable_false_positive", severity="medium")
        elif name == "missing_classification":
            classification["classifications"] = []
        elif name == "invalid_narrative":
            narrative["summary"] = ""
        else:
            control_prepared = prepare_evidence(fixture("login_multi_ip_bursts")["text"], ID, config={})
            detection, classification, narrative = authored_payloads(control_prepared, "login_multi_ip_bursts")
            detection["candidates"][0]["evidence_ids"].append(detection["candidates"][1]["evidence_ids"][0])
        observed_code = None
        try:
            publish(publication, control_prepared, detection, classification, narrative,
                    model="offline-authored-responses", prompt_version="a05-review-1")
        except ContractError as error:
            observed_code = str(error)
        preserved = baseline == fingerprints(publication)
        controls.append({"name": name, "expected_code": code, "observed_code": observed_code,
                         "publication_preserved": preserved, "passed": code == observed_code and preserved})
    return {"schema_version": "1", "fixture_version": FIXTURE_VERSION, "metrics_version": METRICS_VERSION,
            "scope": "offline_authored_responses_not_provider_semantic_acceptance",
            "provider_calls": 0, "cases": reviews, "guard_controls": controls,
            "guard_publication": {"name": "guard_controls", "generation": guard_manifest["generation"],
                                  "sha256": guard_manifest["sha256"]},
            "passed": all(item["passed"] for item in (*reviews, *controls))}


def main():
    destination = ROOT / ".local-state/a05-offline-review" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    destination.mkdir(parents=True, exist_ok=False)
    # Any accidental network addition must fail, including framework telemetry.
    with patch.object(socket.socket, "connect", side_effect=RuntimeError("offline_network_forbidden")), \
            patch.object(socket, "create_connection", side_effect=RuntimeError("offline_network_forbidden")):
        report = review_matrix(destination)
    (destination / "review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"A-05 offline: {len(report['cases'])} casos; {len(report['guard_controls'])} controles; "
          f"passed={report['passed']}; llamadas proveedor=0")
    print(f"Evidence: {destination / 'review.json'}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

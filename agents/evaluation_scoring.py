"""Fixture-bound evaluation metrics; never a provider or operational quality gate."""
from collections import Counter

from agents.evidence_contracts import TYPES
from agents.evaluation_fixtures import (expected_evidence_groups, expected_evidence_pairs,
                                      score_patterns, score_evidence)

METRICS_VERSION = "a05-metrics-2"


def score_groups(findings, bundle, case):
    """Match authored partitions one-to-one, keeping duplicate findings visible.

    A split or overlapping group can cover every indicator/line pair while
    changing the report count. Exact partition conformance is a fixture policy,
    not proof that one grouping is universally correct for real incidents.
    """
    score_evidence(findings, bundle, case)  # Bind digest, raw lines and references first.
    evidence = bundle.to_dict() if hasattr(bundle, "to_dict") else bundle
    references = {item["evidence_id"]: item["line_number"] for item in evidence["items"]}
    selected = set(references.values())
    required = Counter((group["pattern"], tuple(sorted(set(group["line_numbers"]) & selected)))
                       for group in expected_evidence_groups(case)
                       if set(group["line_numbers"]) & selected)
    _, optional_pairs = expected_evidence_pairs(case)
    optional = Counter((pattern, tuple(sorted(number for family, number in optional_pairs
                                              if family == pattern and number in selected)))
                       for pattern in sorted({family for family, number in optional_pairs if number in selected}))
    actual = Counter()
    for finding in findings:
        refs = finding["evidence_ids"]
        if (finding["pattern"] not in TYPES or type(refs) is not list or not refs
                or len(refs) != len(set(refs))):
            raise ValueError("evaluation_invalid_group")
        actual[(finding["pattern"], tuple(sorted(references[ref] for ref in refs)))] += 1
    required_matches = actual & required
    optional_matches = (actual - required_matches) & optional
    missing = required - required_matches
    unexpected = actual - required_matches - optional_matches

    def groups(counter):
        return [{"pattern": pattern, "line_numbers": list(numbers)}
                for (pattern, numbers), count in sorted(counter.items()) for _ in range(count)]

    return {"group_metrics_scope": "exact_authored_indicator_groups_not_incident_accuracy",
            "expected_selected_groups": groups(required), "optional_selected_groups": groups(optional),
            "actual_groups": groups(actual), "missing_groups": groups(missing),
            "unexpected_groups": groups(unexpected), "actual_group_count": sum(actual.values()),
            "expected_selected_group_count": sum(required.values()),
            "group_recall": sum(required_matches.values()) / sum(required.values()) if required else None,
            "group_precision": (sum(required_matches.values()) + sum(optional_matches.values())) / sum(actual.values())
                if actual else None,
            "group_expectations_met": not (missing or unexpected)}


def score_fixture_result(findings, bundle, case):
    """Keep execution success, input coverage and fixture conformance distinct."""
    scores = {**score_patterns(findings, case), **score_evidence(findings, bundle, case),
              **score_groups(findings, bundle, case)}
    scores.update(metrics_version=METRICS_VERSION, semantic_acceptance=False,
                  fixture_expectations_met=all(scores[key] for key in
                    ("pattern_expectations_met", "evidence_expectations_met",
                     "group_expectations_met", "fixture_fully_selected")))
    return scores

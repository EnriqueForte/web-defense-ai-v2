"""Labeled synthetic A-05 cases; no logs, configuration, provider or transport reads."""
from datetime import datetime, timedelta, timezone
import hashlib

CASES = ("mixed", "normal", "missing_body", "encoded", "login_window", "login_spread", "timezone_split", "incomplete", "same_family")
CANONICAL_TARGETS = ('/?q=UNION+SELECT', '/?q=%3Cimg+onerror=confirm(1)%3E',
                     '/?file=../../etc/passwd', '/?host=x%3Bwhoami')
CANONICAL_PATTERNS = ("sql_injection", "xss", "path_traversal", "command_injection")


def fixture(case="mixed"):
    """Return text plus authored expectations; neither is derived from the detector."""
    if case not in CASES:
        raise ValueError("invalid_evaluation_case")
    required, optional = set(), set()
    requests = []
    if case == "mixed":
        targets = (*CANONICAL_TARGETS, *(['/login'] * 5), '/index.html')
        requests = [(target, "POST" if target == "/login" else "GET", index, "+0000")
                    for index, target in enumerate(targets)]
        required = {*CANONICAL_PATTERNS, "brute_force"}
    elif case == "normal":
        requests = [(target, "GET", index, "+0000") for index, target in enumerate(
            ('/index.html', '/health', '/assets/app.css', '/search?q=hello'))]
    elif case == "missing_body":
        requests = [('/vulnerabilities/exec/', 'POST', 0, '+0000'), ('/login.php', 'POST', 1, '+0000')]
    elif case == "encoded":
        requests = [(target, "GET", index, "+0000") for index, target in enumerate((
            '/?q=%55NION%20SELECT', '/?q=%253Cimg%2520onerror%253Dconfirm(1)%253E',
            '/?file=%252e%252e%252fetc/passwd', '/?host=x%253Bwhoami'))]
        required = set(CANONICAL_PATTERNS)
    elif case == "same_family":
        requests = [(target, "GET", index, "+0000") for index, target in enumerate(
            ('/?q=UNION+SELECT', '/?q=1+OR+1=1', '/index.html'))]
        required = {"sql_injection"}
    elif case in {"login_window", "login_spread", "timezone_split"}:
        for index in range(5):
            seconds = index * (120 if case == "login_spread" else 10)
            offset = "+0900" if case == "timezone_split" and index % 2 else "+0000"
            requests.append(('/login', 'POST', seconds, offset))
        if case == "login_window":
            required = {"brute_force"}
    else:
        optional = {"other"}
        return {"case": case, "text": "synthetic uninterpretable request record", "required_patterns": [],
                "optional_patterns": sorted(optional), "expected_input_lines": 1}
    base = datetime(2026, 10, 6, 12, tzinfo=timezone.utc)
    lines = []
    for target, method, seconds, offset in requests:
        stamp = (base + timedelta(seconds=seconds)).strftime("%d/Oct/%Y:%H:%M:%S")
        lines.append(f'192.0.2.1 - - [{stamp} {offset}] "{method} {target} HTTP/1.1" 200 1')
    return {"case": case, "text": "\n".join(lines), "required_patterns": sorted(required),
            "optional_patterns": sorted(optional), "expected_input_lines": len(lines)}


def score_patterns(findings, case):
    expected = fixture(case)
    required = set(expected["required_patterns"])
    allowed = required | set(expected["optional_patterns"])
    actual = {finding["pattern"] for finding in findings}
    return {"case": case, "metrics_scope": "pattern_families_not_event_accuracy",
            "expected_patterns": sorted(required), "optional_patterns": sorted(allowed - required),
            "actual_patterns": sorted(actual), "missing_patterns": sorted(required - actual),
            "unexpected_patterns": sorted(actual - allowed),
            "pattern_recall": len(required & actual) / len(required) if required else None,
            "pattern_precision": len(allowed & actual) / len(actual) if actual else None,
            "pattern_expectations_met": not (required - actual or actual - allowed)}


def expected_evidence_pairs(case):
    """Authored (pattern, input line) labels, independent of preparation rules.

    These label visible indicators, not successful attacks or model severity.
    An uncertain finding on the incomplete record is optional.
    """
    fixture(case)  # Reject unknown cases even when they have no required labels.
    required = set()
    if case in {"mixed", "encoded"}:
        required = {(pattern, number) for number, pattern in enumerate(CANONICAL_PATTERNS, 1)}
    if case == "mixed":
        required |= {("brute_force", number) for number in range(5, 10)}
    elif case == "login_window":
        required = {("brute_force", number) for number in range(1, 6)}
    elif case == "same_family":
        required = {("sql_injection", 1), ("sql_injection", 2)}
    optional = {("other", 1)} if case == "incomplete" else set()
    return required, optional


def score_evidence(findings, bundle, case):
    """Score unique indicator/line pairs against a bound synthetic fixture.

    Missing labels outside the selection are reported separately from model
    omissions. Foreign references fail closed rather than disappear from scores.
    """
    source = fixture(case)
    evidence = bundle.to_dict() if hasattr(bundle, "to_dict") else bundle
    if (evidence["source_digest"] != hashlib.sha256(source["text"].encode()).hexdigest()
            or evidence["total_lines"] != source["expected_input_lines"]):
        raise ValueError("evaluation_fixture_mismatch")
    lines = source["text"].splitlines()
    references = {}
    selected = set()
    for item in evidence["items"]:
        number = item["line_number"]
        if (type(number) is not int or not 1 <= number <= len(lines)
                or item["raw"] != lines[number - 1]
                or number in selected or item["evidence_id"] in references):
            raise ValueError("evaluation_fixture_mismatch")
        references[item["evidence_id"]] = number
        selected.add(number)
    required, optional = expected_evidence_pairs(case)
    selected_required = {pair for pair in required if pair[1] in selected}
    allowed = selected_required | {pair for pair in optional if pair[1] in selected}
    actual = set()
    for finding in findings:
        for identifier in finding["evidence_ids"]:
            if identifier not in references:
                raise ValueError("evaluation_foreign_reference")
            actual.add((finding["pattern"], references[identifier]))
    def labels(pairs):
        return [{"pattern": pattern, "line_number": number} for pattern, number in sorted(pairs)]
    missing = selected_required - actual
    unexpected = actual - allowed
    unselected = required - selected_required
    return {"evidence_metrics_scope": "synthetic_indicator_line_pairs_not_attack_accuracy",
            "expected_evidence_pairs": labels(selected_required),
            "actual_evidence_pairs": labels(actual), "missing_evidence_pairs": labels(missing),
            "unexpected_evidence_pairs": labels(unexpected), "unselected_evidence_pairs": labels(unselected),
            "evidence_recall": len(selected_required & actual) / len(selected_required) if selected_required else None,
            "evidence_precision": len(allowed & actual) / len(actual) if actual else None,
            "evidence_expectations_met": not (missing or unexpected),
            "expected_evidence_fully_selected": not unselected,
            "selected_input_lines": len(selected), "fixture_input_lines": len(lines),
            "fixture_fully_selected": len(selected) == len(lines)}

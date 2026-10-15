"""Bounded balanced selection and observed indicators for the optional structured lane."""
from dataclasses import asdict, dataclass
from datetime import datetime
import json
import re
from urllib.parse import unquote_plus, urlsplit, parse_qs
from agents.evidence_contracts import (ContractError, EvidenceBundle, build_evidence, parse_evidence,
                                      validate_detection, validate_classification)

RULE_VERSION = "observed-access-4"
PATTERNS = {
    "sql_injection": re.compile(r"\bunion\s+(?:all\s+)?select\b|(?:\bor\b|\band\b)\s+['\"]?1['\"]?\s*=\s*['\"]?1|(?:\bsleep|\bbenchmark)\s*\(", re.I),
    "xss": re.compile(r"<\s*(?:script|svg|img)\b|\bon(?:error|load)\s*=|javascript\s*:", re.I),
    "path_traversal": re.compile(r"(?:\.\.[/\\])|(?:etc/(?:passwd|shadow))|windows/system32", re.I),
    "command_injection": re.compile(r"(?:;|&&|\|)\s*(?:whoami|cat|ls|id|pwd|curl|wget)\b", re.I),
}


@dataclass(frozen=True)
class Preparation:
    bundle: EvidenceBundle
    indicators: dict
    bursts: tuple
    scope: dict

    def context(self):
        return json.loads(json.dumps({"rule_version": RULE_VERSION, "scope": self.scope,
                                      "indicators": self.indicators, "bursts": self.bursts,
                                      "uncertainty_evidence_ids": [item.evidence_id for item in self.bundle.items
                                          if _supports_uncertainty(item, self.indicators[item.evidence_id])]}))


def _supports_uncertainty(item, patterns):
    # No indicator is not proof of benign traffic. It is insufficient support
    # for inventing a finding on a fully parsed request in this bounded policy.
    return bool(patterns) or item.method is None or item.target is None or item.http_status is None


def _integer(values, name, default, maximum):
    try:
        raw = values.get(name, str(default))
        if type(raw) not in (str, int):
            raise ValueError
        value = int(raw)
    except (TypeError, ValueError):
        raise ContractError("invalid_preparation_config") from None
    if not 1 <= value <= maximum:
        raise ContractError("invalid_preparation_config")
    return value


def decoded_target(item):
    value = item.target or ""
    for _ in range(2):
        updated = unquote_plus(value)
        if updated == value:
            break
        value = updated
    return value


def observed_patterns(item):
    return tuple(name for name, pattern in PATTERNS.items() if pattern.search(decoded_target(item)))


def is_login_submission(item):
    try:
        target = urlsplit(decoded_target(item))
        path = target.path.lower().rstrip("/")
        fields = parse_qs(target.query, keep_blank_values=True)
    except ValueError:
        return False
    endpoint = path.rsplit("/", 1)[-1]
    # A POST to this exact DVWA form is observable even when Apache does not
    # record its body. Count submissions, without inferring credentials or
    # authentication outcomes. A plain GET remains only a page visit.
    return (item.method == "POST" and (
        endpoint in {"login", "login.php", "signin", "signin.php"}
        or path == "/vulnerabilities/brute")) or (
        item.method == "GET" and path == "/vulnerabilities/brute"
        and "username" in fields and "password" in fields)


def prepare_evidence(text, analysis_id, *, config=None, max_items=30, max_selected_bytes=65536):
    values = {} if config is None else config
    window = _integer(values, "MAX_LINEAS_LOG", 100, 1000)
    threshold = _integer(values, "UMBRAL_FUERZA_BRUTA", 5, 100)
    seconds = _integer(values, "VENTANA_FUERZA_BRUTA_SEGUNDOS", 60, 3600)
    # Reuse input/ID/byte limits without changing the original tail helper.
    seed = build_evidence(text, analysis_id, max_items=max_items, max_selected_bytes=max_selected_bytes)
    lines = [(number, raw) for number, raw in enumerate(text.splitlines(), 1) if raw.strip()]
    scoped = lines[-window:]
    eligible = [parse_evidence(raw, number, analysis_id, seed.source_digest)
                for number, raw in scoped if len(raw.encode()) <= 16384]
    observed = {item.evidence_id: observed_patterns(item) for item in eligible}
    groups = {}
    for item in eligible:
        if is_login_submission(item) and item.source_ip and item.observed_at:
            groups.setdefault(item.source_ip, []).append(item)
    windows = []
    for ip, items in sorted(groups.items()):
        items.sort(key=lambda item: (item.observed_at, item.line_number))
        start = 0
        for end in range(len(items)):
            while (datetime.fromisoformat(items[end].observed_at.replace("Z", "+00:00")) -
                   datetime.fromisoformat(items[start].observed_at.replace("Z", "+00:00"))).total_seconds() > seconds:
                start += 1
            if end - start + 1 >= threshold:
                refs = items[start:end + 1]
                # Merge overlapping windows so long bursts include all attempts.
                union_span = ((datetime.fromisoformat(refs[-1].observed_at.replace("Z", "+00:00")) -
                               datetime.fromisoformat(windows[-1]["items"][0].observed_at.replace("Z", "+00:00"))).total_seconds()
                              if windows and windows[-1]["source_ip"] == ip else seconds + 1)
                if windows and windows[-1]["source_ip"] == ip and union_span <= seconds:
                    previous = windows.pop()
                    refs = sorted({item.evidence_id: item for item in (*previous["items"], *refs)}.values(),
                                  key=lambda item: (item.observed_at, item.line_number))
                windows.append({"source_ip": ip, "items": refs, "all_ids": [item.evidence_id for item in refs]})
    window_count = len(windows)
    windows = sorted(windows, key=lambda group: group["items"][-1].observed_at)[-100:]
    brute_ids = {identifier for group in windows for identifier in group["all_ids"]}
    for identifier in brute_ids:
        observed[identifier] = (*observed[identifier], "brute_force")
    # One recent representative of each observed family, then round-robin fill.
    families = (*PATTERNS, "brute_force")
    buckets = {family: [item for item in reversed(eligible) if family in observed[item.evidence_id]] for family in families}
    selected, used, size = [], set(), 0
    while any(buckets.values()) and len(selected) < max_items:
        for family in families:
            if not buckets[family]:
                continue
            item = buckets[family].pop(0)
            length = len(item.raw.encode())
            if item.evidence_id not in used and size + length <= max_selected_bytes and len(selected) < max_items:
                selected.append(item)
                used.add(item.evidence_id)
                size += length
    for item in reversed(eligible):
        length = len(item.raw.encode())
        if item.evidence_id not in used and len(selected) < max_items and size + length <= max_selected_bytes:
            selected.append(item)
            used.add(item.evidence_id)
            size += length
    selected.sort(key=lambda item: item.line_number)
    bundle = EvidenceBundle(seed.schema_version, analysis_id, seed.source, seed.source_digest,
                            len(lines), len(lines) - len(selected), size, tuple(selected))
    bursts = tuple({"source_ip": group["source_ip"], "count": len(group["items"]),
                    "first_at": group["items"][0].observed_at, "last_at": group["items"][-1].observed_at,
                    "window_seconds": seconds, "threshold": threshold,
                    "line_numbers": [item.line_number for item in group["items"]],
                    "selected_evidence_ids": [identifier for identifier in group["all_ids"] if identifier in used]}
                   for group in windows)
    scope = {"input_nonempty_lines": len(lines), "scanned_lines": len(scoped),
             "outside_window": len(lines) - len(scoped), "oversized_lines": len(scoped) - len(eligible),
             "selected_lines": len(selected), "omitted_lines": len(lines) - len(selected),
             "incomplete": len(lines) != len(selected), "selected_bytes": size}
    scope["omitted_burst_windows"] = window_count - len(windows)
    return Preparation(bundle, {item.evidence_id: observed[item.evidence_id] for item in selected}, bursts, scope)


def validate_observed_detection(payload, prepared):
    validate_detection(payload, prepared.bundle)
    # Pattern matches require explicit review; never silently publish zero findings
    # over selected indicators. Candidates can retain uncertainty/false positives.
    if not payload["candidates"] and any(prepared.indicators.values()):
        raise ContractError("empty_detection_with_observed_indicators")
    evidence = {item.evidence_id: item for item in prepared.bundle.items}
    for candidate in payload["candidates"]:
        pattern = candidate["pattern"]
        refs = candidate["evidence_ids"]
        if pattern == "other" and not all(_supports_uncertainty(evidence[ref], prepared.indicators[ref]) for ref in refs):
            raise ContractError("other_without_observation")
        if pattern != "other" and not all(pattern in prepared.indicators[ref] for ref in refs):
            raise ContractError("pattern_without_observation")
        if pattern == "brute_force" and not any(set(refs).issubset(group["selected_evidence_ids"]) for group in prepared.bursts):
            raise ContractError("brute_without_shared_window")
    return payload


def validate_observed_classification(payload, prepared, detection):
    validate_observed_detection(detection, prepared)
    validate_classification(payload, prepared.bundle, detection)
    patterns = {item["candidate_id"]: item["pattern"] for item in detection["candidates"]}
    rank = {"unknown": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    ceilings = {"sql_injection": 3, "xss": 2, "path_traversal": 3,
                "command_injection": 3, "brute_force": 3, "other": 1}
    for item in payload["classifications"]:
        if patterns[item["candidate_id"]] == "other" and item["state"] == "observed_indicator":
            raise ContractError("unobserved_other_state")
        if rank[item["severity"]] > ceilings[patterns[item["candidate_id"]]]:
            raise ContractError("severity_without_support")
        if item["state"] == "probable_false_positive" and rank[item["severity"]] > 1:
            raise ContractError("inconsistent_false_positive_severity")
    return payload

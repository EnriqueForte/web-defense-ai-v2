"""Versioned evidence/result contracts. No CrewAI, I/O, providers or publication."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import re

VERSION = "1"
TYPES = ("sql_injection", "xss", "path_traversal", "command_injection", "brute_force", "other")
SEVERITIES = ("critical", "high", "medium", "low", "unknown")
STATES = ("observed_indicator", "requires_investigation", "probable_false_positive")


class ContractError(ValueError):
    """Safe diagnostic code; never include raw evidence/model output."""


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    line_number: int
    raw: str
    observed_at: str | None
    source_ip: str | None
    method: str | None
    target: str | None
    http_status: int | None


@dataclass(frozen=True)
class EvidenceBundle:
    schema_version: str
    analysis_id: str
    source: str
    source_digest: str
    total_lines: int
    omitted_lines: int
    selected_bytes: int
    items: tuple[Evidence, ...]

    def to_dict(self):
        return asdict(self)


def parse_evidence(raw, number, analysis_id, digest):
    match = re.match(r'^(\S+) \S+ \S+ \[([^\]]+)\] "([A-Z]+) ([^ ]+) HTTP/[^" ]+" ([0-9]{3})(?: |$)', raw)
    ip, date, method, target, status = None, None, None, None, None
    if match:
        try:
            ip = str(ipaddress.ip_address(match[1]))
        except ValueError:
            pass
        date = utc_timestamp(match[2])
        method, target = match[3], match[4]
        code = int(match[5])
        status = code if 100 <= code <= 599 else None
    identity = f"{analysis_id}:{digest}:{number}:".encode() + raw.encode("utf-8")
    return Evidence("e_" + hashlib.sha256(identity).hexdigest()[:24], number, raw,
                    date, ip, method, target, status)


def utc_timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        date = datetime.strptime(value, "%d/%b/%Y:%H:%M:%S %z")
    except ValueError:
        try:
            date = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    try:
        return date.astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if date.tzinfo else None
    except (ValueError, OverflowError):
        return None


def build_evidence(text, analysis_id, *, max_items=100, max_line_bytes=16384, max_selected_bytes=65536):
    if not isinstance(analysis_id, str) or not re.fullmatch(r"[a-f0-9]{32}", analysis_id):
        raise ContractError("invalid_analysis_id")
    if not isinstance(text, str) or len(text.encode("utf-8")) > 1048576:
        raise ContractError("input_limit")
    if any(type(limit) is not int or limit < 1 for limit in (max_items, max_line_bytes, max_selected_bytes)):
        raise ContractError("invalid_sampling_limit")
    if max_items > 1000 or max_line_bytes > 16384 or max_selected_bytes > 262144:
        raise ContractError("sampling_limit_exceeded")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    lines = [(number, raw) for number, raw in enumerate(text.splitlines(), 1) if raw.strip()]
    selected, size = [], 0
    # Isolated bounded tail sample. No production selection policy is changed.
    for number, raw in reversed(lines):
        length = len(raw.encode("utf-8"))
        if length > max_line_bytes or size + length > max_selected_bytes:
            continue
        if len(selected) >= max_items:
            break
        selected.append((number, raw))
        size += length
    items = []
    for number, raw in reversed(selected):
        items.append(parse_evidence(raw, number, analysis_id, digest))
    return EvidenceBundle(VERSION, analysis_id, "access.log", digest, len(lines), len(lines) - len(items), size, tuple(items))


def _object(value, fields):
    if type(value) is not dict or set(value) != set(fields):
        raise ContractError("invalid_fields")


def _text(value, maximum=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ContractError("invalid_text")
    try:
        value.encode("utf-8")
    except UnicodeError:
        raise ContractError("invalid_text_encoding") from None
    return value


def _list(value, maximum=100):
    if type(value) is not list or len(value) > maximum:
        raise ContractError("invalid_list")


def parse_payload(raw):
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > 262144:
        raise ContractError("output_limit")
    def pairs(values):
        result = {}
        for name, value in values:
            if name in result:
                raise ContractError("duplicate_json_key")
            result[name] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _value: (_ for _ in ()).throw(ContractError("invalid_json_constant")))
    except (ValueError, RecursionError) as error:
        if isinstance(error, ContractError):
            raise
        raise ContractError("invalid_json") from None


def _envelope(payload, bundle, field):
    _object(payload, ("schema_version", "analysis_id", field))
    if payload["schema_version"] != VERSION or payload["analysis_id"] != bundle.analysis_id:
        raise ContractError("wrong_analysis_or_version")
    _list(payload[field])


def validate_detection(payload, bundle):
    _envelope(payload, bundle, "candidates")
    allowed = {item.evidence_id for item in bundle.items}
    ids, groups = set(), set()
    for item in payload["candidates"]:
        _object(item, ("candidate_id", "evidence_ids", "pattern", "reason"))
        identifier = _text(item["candidate_id"], 64)
        if not re.fullmatch(r"c_[a-zA-Z0-9_-]{1,60}", identifier) or identifier in ids:
            raise ContractError("duplicate_or_invalid_candidate")
        ids.add(identifier)
        _list(item["evidence_ids"])
        refs = item["evidence_ids"]
        if not refs or any(not isinstance(ref, str) or ref not in allowed for ref in refs) or len(refs) != len(set(refs)):
            raise ContractError("invalid_evidence_reference")
        if item["pattern"] not in TYPES:
            raise ContractError("invalid_pattern")
        key = (item["pattern"], tuple(sorted(refs)))
        if key in groups:
            raise ContractError("duplicate_candidate_group")
        groups.add(key)
        _text(item["reason"])
    return payload


def validate_classification(payload, bundle, detection):
    validate_detection(detection, bundle)
    _envelope(payload, bundle, "classifications")
    ids = []
    for item in payload["classifications"]:
        _object(item, ("candidate_id", "severity", "state", "reason"))
        ids.append(_text(item["candidate_id"], 64))
        if item["severity"] not in SEVERITIES or item["state"] not in STATES:
            raise ContractError("invalid_classification")
        _text(item["reason"])
    if len(ids) != len(set(ids)) or set(ids) != {item["candidate_id"] for item in detection["candidates"]}:
        raise ContractError("incomplete_or_foreign_classification")
    return payload


def validate_narrative(payload, bundle, detection, classification):
    validate_classification(classification, bundle, detection)
    _object(payload, ("schema_version", "analysis_id", "summary", "recommendations"))
    if payload["schema_version"] != VERSION or payload["analysis_id"] != bundle.analysis_id:
        raise ContractError("wrong_analysis_or_version")
    _text(payload["summary"], 4000)
    _list(payload["recommendations"])
    allowed = {item["candidate_id"] for item in detection["candidates"]}
    for item in payload["recommendations"]:
        _object(item, ("candidate_id", "text"))
        if not isinstance(item["candidate_id"], str) or item["candidate_id"] not in allowed:
            raise ContractError("invalid_recommendation_reference")
        _text(item["text"])
    return payload


def assemble_result(bundle, detection, classification, narrative, *, model, prompt_version):
    validate_narrative(narrative, bundle, detection, classification)
    by_id = {item["candidate_id"]: item for item in classification["classifications"]}
    evidence = {item.evidence_id: item for item in bundle.items}
    counts = {severity: 0 for severity in SEVERITIES}
    findings = []
    for candidate in detection["candidates"]:
        classified = by_id[candidate["candidate_id"]]
        counts[classified["severity"]] += 1
        findings.append({**candidate, **classified,
                         "observations": [asdict(evidence[ref]) for ref in candidate["evidence_ids"]]})
    # Copy containers so later mutation of model payloads cannot change this result.
    result = {"schema_version": VERSION, "analysis_id": bundle.analysis_id,
              "provenance": "validated_references", "model": _text(model, 256),
              "prompt_version": _text(prompt_version, 128), "evidence": bundle.to_dict(),
              "findings": findings, "counts": counts, "narrative": narrative,
              "quality": "semantic_evaluation_pending"}
    return json.loads(json.dumps(result))

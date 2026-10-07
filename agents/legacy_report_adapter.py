"""Historical Markdown adapter; reported facts never become verified evidence."""
import hashlib
import ipaddress
import re
import unicodedata
from agents.evidence_contracts import ContractError, VERSION, utc_timestamp


def clean(value):
    return value.strip().strip("*_` ")


def header(value):
    return "".join(char for char in unicodedata.normalize("NFD", clean(value).lower())
                   if unicodedata.category(char) != "Mn")


def cells(line):
    return [value.strip().replace(r"\|", "|") for value in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def adapt_legacy(markdown):
    if not isinstance(markdown, str) or len(markdown.encode("utf-8")) > 1048576:
        raise ContractError("legacy_input_limit")
    rows, warnings, columns = [], [], None
    in_section, found = False, False
    for line_number, line in enumerate(markdown.splitlines(), 1):
        if re.match(r"^\s*#{1,6}\s+.*AMENAZAS DETECTADAS", line, re.IGNORECASE):
            in_section, columns = True, None
            continue
        if in_section and re.match(r"^\s*#{1,6}\s", line):
            in_section = False
        if not in_section or not line.strip().startswith("|") or not line.strip().endswith("|"):
            continue
        values = cells(line)
        if columns is None:
            columns = [header(value) for value in values]
            if len(columns) != len(set(columns)):
                warnings.append("duplicate_headers")
            if not any(name == "severidad" for name in columns) or not any(name.startswith("tipo") for name in columns):
                warnings.append("missing_required_headers")
            found = True
            continue
        if values and all(re.fullmatch(r":?-{3,}:?", value) for value in values):
            continue
        if len(values) != len(columns):
            warnings.append("misaligned_row")
            continue
        def value(*names):
            return next((clean(values[index]) for index, name in enumerate(columns)
                         if name in names), "-")
        raw_ip = value("ip", "ip origen", "origen")
        try:
            reported_ip = str(ipaddress.ip_address(raw_ip))
        except ValueError:
            reported_ip = None
            if raw_ip not in {"-", "", "—"}:
                warnings.append("invalid_reported_ip")
        raw_date = value("fecha/hora del evento", "fecha del evento", "timestamp", "fecha hora")
        reported_date = utc_timestamp(raw_date)
        if raw_date not in {"-", "", "—"} and reported_date is None:
            warnings.append("invalid_reported_time")
        raw_severity = header(value("severidad"))
        severity = {"critica": "critical", "alta": "high", "media": "medium", "baja": "low"}.get(raw_severity)
        if severity is None:
            warnings.append("unknown_reported_severity")
        rows.append({"row_number": line_number, "reported_line": value("linea", "numero", "#"),
                     "reported_severity_text": value("severidad"), "reported_ip_text": raw_ip,
                     "reported_time_text": raw_date,
                     "reported_type": value("tipo", "tipo de ataque"), "reported_severity": severity,
                     "reported_state": value("estado"), "reported_ip": reported_ip,
                     "reported_time": reported_date, "evidence_ids": [], "provenance": "legacy_unverified"})
        if len(rows) > 1000:
            raise ContractError("legacy_row_limit")
    if not found:
        warnings.append("missing_threat_table")
    return {"schema_version": VERSION, "source_report_digest": hashlib.sha256(markdown.encode()).hexdigest(),
            "provenance": "legacy_unverified", "status": "degraded" if warnings else "adapted_unverified",
            "findings": rows, "warnings": sorted(set(warnings))}

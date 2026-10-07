"""Deterministic facts/table and scoped no-finding summary for the optional lane."""
import html
from agents.evidence_contracts import assemble_result
from agents.evidence_preparation import validate_observed_classification, RULE_VERSION
REPORT_FORMAT_VERSION = "structured-report-3"

SEVERITY_LABELS = {"critical": "CRITICA", "high": "ALTA", "medium": "MEDIA", "low": "BAJA", "unknown": "DESCONOCIDA"}
TYPE_LABELS = {"sql_injection": "SQLi", "xss": "XSS", "path_traversal": "Path Traversal",
               "command_injection": "Command Injection", "brute_force": "Fuerza Bruta", "other": "Otro"}
STATE_LABELS = {"observed_indicator": "Indicador observado", "requires_investigation": "Requiere investigación",
               "probable_false_positive": "Posible falso positivo"}


def no_findings_narrative(bundle, *, preparation=None):
    selected = len(bundle.items)
    unknown = sum(item.method is None or item.target is None or item.http_status is None for item in bundle.items)
    selection = f"{selected} línea seleccionada" if selected == 1 else f"{selected} líneas seleccionadas"
    summary = (f"No se obtuvieron hallazgos que cumplan los criterios en {selection} "
               f"de {bundle.total_lines}; se omitieron {bundle.omitted_lines}. ")
    if unknown:
        records = "1 registro" if unknown == 1 else f"{unknown} registros"
        summary += (f"Hay {records} cuya petición no se pudo interpretar completamente. "
                    "La evidencia incompleta no permite descartar actividad sospechosa. ")
    if preparation is not None:
        indicators = sum(bool(value) for value in preparation.indicators.values())
        if indicators:
            indicator_lines = "1 línea" if indicators == 1 else f"{indicators} líneas"
            summary += (f"La preparación observó indicadores en {indicator_lines}, pero la detección "
                        "validada no produjo candidatos; revisar posibles omisiones. ")
    summary += "Este resultado limitado no demuestra tráfico benigno ni seguridad global."
    return {"schema_version": bundle.schema_version, "analysis_id": bundle.analysis_id,
            "summary": summary, "recommendations": []}


def safe_text(value):
    # Narrative is text, not a second Markdown document or a model-authored table.
    value = " ".join(value.split())
    value = html.escape(value, quote=True)
    for char in "\\|#*`[]":
        value = value.replace(char, "\\" + char)
    return value


def compose(prepared, detection, classification, narrative, *, model, prompt_version):
    validate_observed_classification(classification, prepared, detection)
    result = assemble_result(prepared.bundle, detection, classification, narrative, model=model, prompt_version=prompt_version)
    result["report_format_version"] = REPORT_FORMAT_VERSION
    # Validate the model's contract first; don't turn malformed JSON into a report.
    # For no candidates, only Python may describe the evidence scope and limits.
    if not result["findings"]:
        narrative = no_findings_narrative(prepared.bundle, preparation=prepared)
        result["narrative"] = narrative
        result["narrative_source"] = "python_scope"
    else:
        result["narrative_source"] = "llm_contract_validated_semantics_pending"
    result["preparation"] = prepared.context()
    result["rule_version"] = RULE_VERSION
    return result, render_markdown(result)


def event_period(observations):
    dates = sorted({item["observed_at"] for item in observations if item["observed_at"]})
    return {"event_time_start": dates[0] if dates else None,
            "event_time_end": dates[-1] if dates else None,
            "event_time_missing_count": sum(item["observed_at"] is None for item in observations)}


def render_markdown(result):
    narrative = result["narrative"]
    evidence = result["evidence"]
    lines = ["# Reporte de seguridad", "", "## RESUMEN EJECUTIVO", safe_text(narrative["summary"]), "",
             "## ALCANCE", f"Análisis: {result['analysis_id']}",
             f"Líneas seleccionadas: {len(evidence['items'])}; omitidas: {evidence['omitted_lines']}.",
             "Las referencias son números de línea del log, no puntuaciones de severidad.",
             "Fechas de las peticiones en UTC; un intervalo agrupa varias horas observadas.",
             "Observaciones del access.log; no confirman éxito de explotación.", "",
             "## AMENAZAS DETECTADAS",
             "| Fecha/hora del evento (UTC) | Línea del log | Severidad | Tipo de Ataque | Estado | IP Origen |",
             "| --- | --- | --- | --- | --- | --- |"]
    for finding in result["findings"]:
        observations = finding["observations"]
        period = event_period(observations)
        ips = {item["source_ip"] for item in observations}
        date = period['event_time_start']
        if date and date != period['event_time_end']:
            date += ' a ' + period['event_time_end']
        if period['event_time_missing_count']:
            date = (date or 'Sin fecha conocida') + f"; {period['event_time_missing_count']} sin fecha"
        ip = next(iter(ips)) if len(ips) == 1 else None
        positions = ",".join(str(item["line_number"]) for item in observations)
        lines.append(f"| {date or '-'} | {positions} | {SEVERITY_LABELS[finding['severity']]} | "
                     f"{TYPE_LABELS[finding['pattern']]} | {STATE_LABELS[finding['state']]} | {ip or '-'} |")
    lines += ["", "## CONTEOS", *[f"{SEVERITY_LABELS[key]}: {value}" for key, value in result["counts"].items()],
              "", "## REFERENCIAS"]
    for finding in result["findings"]:
        lines.append(f"{finding['candidate_id']}: " + ", ".join(finding["evidence_ids"]))
    lines += ["", "## RECOMENDACIONES DE MITIGACIÓN"]
    for item in narrative["recommendations"]:
        lines.append(f"- {item['candidate_id']}: {safe_text(item['text'])}")
    lines += ["", "## ACCIONES INMEDIATAS", "Revisar las evidencias y recomendaciones antes de actuar.", ""]
    return "\n".join(lines)

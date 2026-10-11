"""Deterministic facts, scope and reviewed mitigations for the structured lane."""
from collections import Counter
import html
from agents.evidence_contracts import assemble_result
from agents.evidence_preparation import validate_observed_classification, RULE_VERSION
REPORT_FORMAT_VERSION = "structured-report-4"
NARRATIVE_POLICY_VERSION = "grounded-narrative-1"

SEVERITY_LABELS = {"critical": "CRITICA", "high": "ALTA", "medium": "MEDIA", "low": "BAJA", "unknown": "DESCONOCIDA"}
TYPE_LABELS = {"sql_injection": "SQLi", "xss": "XSS", "path_traversal": "Path Traversal",
               "command_injection": "Command Injection", "brute_force": "Fuerza Bruta", "other": "Otro"}
STATE_LABELS = {"observed_indicator": "Indicador observado", "requires_investigation": "Requiere investigación",
               "probable_false_positive": "Posible falso positivo"}

# Reviewed against OWASP; advice is conditional, never a claim of a deployed fix.
# Source links and review scope are recorded in docs/NARRATIVA_VALIDADA_A05_2026_10_10.md.
MITIGATIONS = {
    "sql_injection": "Revisar las consultas asociadas a estas peticiones y usar consultas parametrizadas "
                     "para los valores, evitando concatenar entradas en SQL.",
    "xss": "Revisar dónde se reflejan los datos y aplicar codificación de salida según el contexto. "
           "Si la aplicación acepta HTML, sanearlo con una biblioteca mantenida.",
    "path_traversal": "Limitar la selección de archivos a identificadores permitidos y comprobar que "
                      "la ruta resuelta permanezca dentro del directorio autorizado.",
    "command_injection": "Preferir APIs que no invoquen comandos del sistema. Si un proceso es imprescindible, "
                         "separar comando y argumentos y validar las entradas con una lista permitida.",
    "brute_force": "Revisar los intentos por cuenta y aplicar limitación de intentos de autenticación; "
                   "valorar autenticación multifactor y evitar bloqueos indiscriminados.",
    "other": "Verificar formato, fecha y solicitud de estas referencias y contrastarlas con eventos de "
             "aplicación antes de clasificar la actividad o elegir una mitigación específica.",
}


def findings_narrative(result, prepared):
    """Use only validated enumerations/counts; never raw targets or model reasons."""
    findings = result["findings"]
    bundle = prepared.bundle
    families = Counter(finding["pattern"] for finding in findings)
    states = Counter(finding["state"] for finding in findings)
    total = len(findings)
    groups = "1 grupo de hallazgos" if total == 1 else f"{total} grupos de hallazgos"
    verb = "Se clasificó" if total == 1 else "Se clasificaron"
    summary = (f"{verb} {groups} con referencias en {len(bundle.items)} líneas seleccionadas "
               f"de {bundle.total_lines}; se omitieron {bundle.omitted_lines}. ")
    summary += "Patrones: " + "; ".join(f"{TYPE_LABELS[pattern]}: {families[pattern]}"
                                       for pattern in TYPE_LABELS if families[pattern]) + ". "
    summary += "Severidades: " + "; ".join(f"{SEVERITY_LABELS[severity]}: {count}"
                                          for severity, count in result["counts"].items() if count) + ". "
    summary += "Estados: " + "; ".join(f"{STATE_LABELS[state]}: {states[state]}"
                                      for state in STATE_LABELS if states[state]) + ". "
    observed = {(pattern, identifier) for identifier, patterns in prepared.indicators.items() for pattern in patterns}
    covered = {(finding["pattern"], identifier) for finding in findings for identifier in finding["evidence_ids"]}
    missing = len(observed - covered)
    if missing:
        remaining = "Queda 1 referencia" if missing == 1 else f"Quedan {missing} referencias"
        summary += (f"{remaining} de patrón observado sin representar en estos grupos; "
                    "revisar posibles omisiones. ")
    summary += ("Este alcance no confirma explotación exitosa ni permite descartar actividad fuera de la selección. "
                "Las medidas propuestas deben revisarse según la aplicación antes de aplicarlas.")
    recommendations = []
    for finding in findings:
        prefix = ("Verificar el contexto y documentar el posible falso positivo antes de cambiar controles. "
                  if finding["state"] == "probable_false_positive" else
                  "Correlacionar las referencias con eventos de aplicación para determinar su alcance. ")
        recommendations.append({"candidate_id": finding["candidate_id"],
                                "text": prefix + MITIGATIONS[finding["pattern"]]})
    return {"schema_version": bundle.schema_version, "analysis_id": bundle.analysis_id,
            "summary": summary, "recommendations": recommendations}


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
    # Only Python publishes facts and reviewed advice. The model's narrative
    # still has to pass its original contract; it is never silently repaired.
    if not result["findings"]:
        narrative = no_findings_narrative(prepared.bundle, preparation=prepared)
        result["narrative"] = narrative
        result["narrative_source"] = "python_scope"
    else:
        result["narrative"] = findings_narrative(result, prepared)
        result["narrative_source"] = "python_validated_facts"
    result["narrative_policy_version"] = NARRATIVE_POLICY_VERSION
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

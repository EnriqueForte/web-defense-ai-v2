"""F6/F7 catalog, separate from the immutable 45-case F2 corpus.

Definitions are instructional expectations, never the detector input.
"""
VERSION = "puerto-umbral-extensions-1"
SEED = "umbral-extensions-20261029-1"
CATEGORIES = {
    "A01:2025": "Control de acceso", "A02:2025": "Configuración de seguridad",
    "A03:2025": "Cadena de suministro", "A04:2025": "Criptografía",
    "A05:2025": "Inyección", "A06:2025": "Diseño inseguro", "A07:2025": "Autenticación",
    "A08:2025": "Integridad de software o datos", "A09:2025": "Registro y alertas",
    "A10:2025": "Condiciones excepcionales",
}
SCENARIOS = {
    "stored_xss": {"name": "Bitácora · XSS almacenado", "phase": "F6", "owasp": "A05:2025",
                   "evidence_kind": "http_and_browser", "path": "/avanzado/tablon",
                   "effect": "stored_browser_marker", "corrected_status": 200},
    "idor": {"name": "Cargas · autorización por objeto", "phase": "F6", "owasp": "A01:2025",
             "evidence_kind": "application_state", "path": "/avanzado/carga",
             "effect": "foreign_fixture_read", "corrected_status": 403},
    "csrf": {"name": "Preferencias · protección CSRF", "phase": "F6", "owasp": "A01:2025",
             "evidence_kind": "http_control_browser_pending", "path": "/avanzado/preferencias",
             "effect": "cross_origin_state_change", "corrected_status": 403},
    "ssrf": {"name": "Baliza · señuelo interno", "phase": "F6", "owasp": "A01:2025",
             "evidence_kind": "unix_http_canary", "path": "/avanzado/baliza",
             "effect": "internal_canary_read", "corrected_status": 403},
    "workflow": {"name": "Atraque · flujo de aprobación", "phase": "F6", "owasp": "A06:2025",
                 "evidence_kind": "application_state", "path": "/avanzado/atraque",
                 "effect": "unapproved_docking", "corrected_status": 409},
    "configuration": {"name": "Configuración · réplica de diagnóstico", "phase": "F7", "owasp": "A02:2025",
                      "evidence_kind": "fixture_review", "path": "/avanzado/revision",
                      "effect": "debug_fixture_exposed", "corrected_status": 200},
    "supply_chain": {"name": "Suministro · procedencia del artefacto", "phase": "F7", "owasp": "A03:2025",
                     "evidence_kind": "fixture_review", "path": "/avanzado/revision",
                     "effect": "changed_artifact_accepted", "corrected_status": 422},
    "cryptography": {"name": "Criptografía · codificar o proteger", "phase": "F7", "owasp": "A04:2025",
                     "evidence_kind": "fixture_review", "path": "/avanzado/revision",
                     "effect": "reversible_fixture_storage", "corrected_status": 200},
    "integrity": {"name": "Integridad · manifiesto de carga", "phase": "F7", "owasp": "A08:2025",
                  "evidence_kind": "fixture_review", "path": "/avanzado/revision",
                  "effect": "changed_manifest_accepted", "corrected_status": 422},
    "logging": {"name": "Registro · huecos y avisos", "phase": "F7", "owasp": "A09:2025",
                "evidence_kind": "fixture_review", "path": "/avanzado/revision",
                "effect": "fixture_gap_unnoticed", "corrected_status": 200},
    "exceptions": {"name": "Excepciones · respuesta controlada", "phase": "F7", "owasp": "A10:2025",
                   "evidence_kind": "fixture_review", "path": "/avanzado/revision",
                   "effect": "fictional_error_details_exposed", "corrected_status": 400},
}


def cases():
    """99 fixed extension cases, distinct from F2; constructing this sends nothing."""
    return [{"case_id": f"ext-{scenario}-{'a' if kind == 'attempt' else 'b'}{variant + 1}-{mode}",
             "scenario": scenario, "phase": definition["phase"], "mode": mode,
             "variant": variant, "kind": kind, "evidence_kind": definition["evidence_kind"],
             "expected_effect": kind == "attempt" and mode == "vulnerable"}
            for scenario, definition in SCENARIOS.items() for variant in range(3)
            for kind, modes in (("attempt", ("vulnerable", "corrected")), ("benign", ("corrected",)))
            for mode in modes]


def coverage(base_scenarios):
    definitions = {**base_scenarios, **SCENARIOS}
    return [{"category": key, "name": name, "source": "https://top10.owasp.org/2025/",
             "scenarios": [value["name"] for value in definitions.values() if value["owasp"] == key],
             "evidence": sorted({value.get("evidence_kind", "local_http") for value in definitions.values() if value["owasp"] == key}),
             "acceptance": "pending", "full_category_detection_verified": False}
            for key, name in CATEGORIES.items()]

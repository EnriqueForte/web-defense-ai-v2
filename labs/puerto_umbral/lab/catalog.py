"""Versioned cases fixed before execution; never sent to V2 as expected labels."""
VERSION = "puerto-umbral-f2-1"
SEED = "umbral-cargo-20261026-1"
SCENARIOS = {
    "sqli": {"name": "Inyección SQL", "path": "/mercancias", "field": "q", "owasp": "A05:2025",
             "attacks": ["%' OR 1=1 --", "%' OR 2>1 --", "%' UNION SELECT id,name FROM cargo WHERE visible=0 --"],
             "benign": ["navegación", "energía", "Asteria"], "effect": "private_cargo_read"},
    "xss": {"name": "XSS reflejado", "path": "/comunicaciones", "field": "q", "owasp": "A05:2025",
            "attacks": ["<svg onload=\"parent.postMessage({kind:'umbral-xss',nonce:'__NONCE__'},'*')\"></svg>",
                        "<img src='data:,' onerror=\"parent.postMessage({kind:'umbral-xss',nonce:'__NONCE__'},'*')\">",
                        "<script>parent.postMessage({kind:'umbral-xss',nonce:'__NONCE__'},'*')</script>"],
            "benign": ["Revisión de baliza", "Llegada de Asteria", "Turno de ingeniería"], "effect": "browser_script_executed"},
    "traversal": {"name": "Path traversal", "path": "/archivo", "field": "documento", "owasp": "A01:2025",
                  "attacks": ["../private/manifiesto.txt", "./../private/manifiesto.txt", "a/../../private/manifiesto.txt"],
                  "benign": ["atraque.txt", "baliza.txt", "tripulacion.txt"], "effect": "reserved_fixture_read"},
    "command": {"name": "Inyección de comandos", "path": "/mantenimiento", "field": "equipo", "owasp": "A05:2025",
                "attacks": ["baliza-07; id", "baliza-07 && whoami", "baliza-07 | pwd"],
                "benign": ["baliza-07", "esclusa-02", "enlace-comms"], "effect": "sandbox_command_executed"},
    "brute": {"name": "Fuerza bruta", "path": "/login", "field": "username", "owasp": "A07:2025",
              "attacks": ["operador.demo", "ingenieria.demo", "control.demo"],
              "benign": ["operador.demo", "ingenieria.demo", "control.demo"], "effect": "login_after_failed_burst"},
}
MODES = ("vulnerable", "corrected")
PASSWORD = "umbral-demo"


def cases():
    result = []
    for scenario, definition in SCENARIOS.items():
        for variant in range(3):
            for mode in MODES:
                result.append({"case_id": f"{scenario}-a{variant + 1}-{mode}", "scenario": scenario,
                               "variant": variant, "mode": mode, "kind": "attempt",
                               "expected_effect": mode == "vulnerable"})
        for variant in range(3):
            result.append({"case_id": f"{scenario}-b{variant + 1}", "scenario": scenario,
                           "variant": variant, "mode": "corrected", "kind": "benign",
                           "expected_effect": False})
    return result

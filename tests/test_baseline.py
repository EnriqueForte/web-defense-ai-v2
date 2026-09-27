"""Línea base sin Docker, credenciales, llamadas IA ni datos operativos.

expectedFailure documenta defectos pendientes: NO equivale a prueba aprobada.
Un arreglo inesperado hace fallar la suite hasta retirar esa marca.
"""
import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from agents.log_analyst import (
    analizar_fuerza_bruta, leer_log, pre_filtrar_lineas, preparar_log_para_agente,
)

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "tests/fixtures/traffic.json").read_text(encoding="utf-8"))


def line(target="/index.php", date="30/Apr/2026:23:00:00", method="GET"):
    return f'192.0.2.10 - - [{date} +0000] "{method} {target} HTTP/1.1" 200 42'


def report(ip="192.0.2.10", severity="ALTA", state="Desconocido"):
    return ("## AMENAZAS DETECTADAS\n"
            "| Línea | Severidad | Tipo | Estado | IP Origen |\n"
            "| --- | --- | --- | --- | --- |\n"
            f"| 1 | {severity} | SQLi | {state} | {ip} |\n")


class IsolatedCase(unittest.TestCase):
    def setUp(self):
        stack = self.enterContext(contextlib.ExitStack())
        self.base = Path(stack.enter_context(tempfile.TemporaryDirectory()))
        stack.enter_context(patch.dict(os.environ, {}, clear=True))
        stack.enter_context(patch("dotenv.load_dotenv", return_value=False))
        stack.enter_context(patch("socket.socket.connect", side_effect=AssertionError("Red prohibida")))
        stack.enter_context(patch("socket.create_connection", side_effect=AssertionError("Red prohibida")))
        self.process = stack.enter_context(patch("subprocess.run", side_effect=AssertionError("Proceso externo prohibido")))
        stack.enter_context(patch("subprocess.Popen", side_effect=AssertionError("Proceso externo prohibido")))
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self.log = self.base / "access.log"


class PreprocessingTests(IsolatedCase):
    def test_reference_dataset(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                entry = case.get("raw") or line(case["target"], method=case.get("method", "GET"))
                self.assertEqual(bool(pre_filtrar_lineas([entry])["sospechosas"]), case["suspicious"])

    def test_missing_log(self):
        with self.assertRaises(FileNotFoundError):
            leer_log(str(self.log))

    def test_empty_log(self):
        self.log.write_text("", encoding="utf-8")
        self.assertIn("error", preparar_log_para_agente(str(self.log)))

    def test_burst_threshold_and_window(self):
        burst = [line("/login.php", f"30/Apr/2026:23:00:{i:02d}", "POST") for i in range(5)]
        self.assertEqual(set(analizar_fuerza_bruta(burst)), set(burst))
        self.assertEqual(analizar_fuerza_bruta(burst[:4]), [])
        spread = [line("/login.php", f"30/Apr/2026:23:{i:02d}:00", "POST") for i in range(5)]
        self.assertEqual(analizar_fuerza_bruta(spread), [])
        self.assertEqual(analizar_fuerza_bruta(["POST login sin fecha"]), [])

    def test_current_selection_limit_is_observable(self):
        # Caracterización, no garantía de calidad: solo últimas 100, cinco altas.
        rows = [line(f"/item?id=%27&sample={i}") for i in range(120)]
        self.log.write_text("\n".join(rows), encoding="utf-8")
        prepared = preparar_log_para_agente(str(self.log))
        self.assertEqual(prepared["estadisticas"]["total_lineas"], 100)
        self.assertEqual(prepared["contenido"].splitlines(), rows[20:25])

    def test_critical_patterns_survive_high_volume(self):
        critical = line("/vulnerabilities/exec/?ip=127.0.0.1%3Bwhoami")
        rows = [critical] + [line(f"/vulnerabilities/brute/?n={i}") for i in range(99)]
        self.log.write_text("\n".join(rows), encoding="utf-8")
        selected = preparar_log_para_agente(str(self.log))["contenido"].splitlines()
        self.assertIn(critical, selected)
        self.assertEqual(len(selected), 6)


class DashboardTests(IsolatedCase):
    def setUp(self):
        super().setUp()
        self.web = importlib.import_module("dashboard.app")
        self.enterContext(patch.multiple(self.web, REPORT_PATH=self.base,
                                        HISTORIAL=self.base / "historial", LOG_PATH=str(self.log)))
        self.enterContext(patch.dict(self.web.app.config, TESTING=True))
        self.client = self.web.app.test_client()
        self.log.write_text(line("/item?id=%27"), encoding="utf-8")

    def test_valid_report_and_dashboard(self):
        (self.base / "reporte_seguridad.md").write_text(report(), encoding="utf-8")
        self.assertEqual(self.web.parsear_amenazas(report())[0]["ip"], "192.0.2.10")
        self.assertEqual(self.client.get("/").status_code, 200)
        self.process.assert_not_called()

    def test_legacy_state_contract_with_simulated_copy(self):
        self.process.side_effect = None
        self.process.return_value = subprocess.CompletedProcess([], 0)
        data = self.client.get("/api/estado").get_json()
        self.assertEqual(set(data), {"stats", "amenazas", "historial", "log", "ips_log", "timeline", "timestamp"})

    def test_report_routes_reject_invalid_and_missing_names(self):
        self.assertEqual(self.client.get("/report/no.txt").status_code, 400)
        self.assertEqual(self.client.get("/report/reporte_20260430.md").status_code, 404)

    def test_sync_failure_is_reported(self):
        self.process.side_effect = None
        self.process.return_value = subprocess.CompletedProcess([], 1)
        response = self.client.post("/api/sincronizar")
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.get_json()["ok"])

    @unittest.expectedFailure
    def test_h01_sync_does_not_claim_new_analysis(self):
        self.process.side_effect = None
        self.process.return_value = subprocess.CompletedProcess([], 0)
        result = self.client.post("/api/sincronizar").get_json()
        self.assertNotIn("analisis completado", result["mensaje"].lower())

    @unittest.expectedFailure
    def test_h02_empty_dashboard_renders(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    @unittest.expectedFailure
    def test_h05_state_read_does_not_call_docker(self):
        self.process.side_effect = None
        self.process.return_value = subprocess.CompletedProcess([], 0)
        self.client.get("/api/estado")
        self.process.assert_not_called()

    @unittest.expectedFailure
    def test_h05_state_available_without_docker(self):
        self.process.side_effect = FileNotFoundError("Docker simulado no disponible")
        self.assertEqual(self.client.get("/api/estado").status_code, 200)

    @unittest.expectedFailure
    def test_h06_low_is_not_medium(self):
        stats = self.web.obtener_estadisticas(self.web.parsear_amenazas(report(severity="BAJA")))
        self.assertEqual(stats["medias"], 0)

    @unittest.expectedFailure
    def test_h07_empty_cell_preserves_columns(self):
        threat = self.web.parsear_amenazas(report(ip="198.51.100.7", state=""))[0]
        self.assertEqual(threat["ip"], "198.51.100.7")
        self.assertIn(threat["estado"], (None, "", "-", "Desconocido"))

    @unittest.expectedFailure
    def test_h08_missing_ip_not_attributed_to_busy_host(self):
        self.assertIn(self.web.parsear_amenazas(report(ip="Desconocido"))[0]["ip"], (None, "-", "Desconocido"))

    @unittest.expectedFailure
    def test_h09_timeline_chronological_across_months(self):
        self.log.write_text(line("/item?id=%27") + "\n" + line("/item?id=%27", "01/May/2026:00:00:00"), encoding="utf-8")
        self.assertEqual(self.web.obtener_timeline_ataques()["horas"], ["30/Apr/2026 23h", "01/May/2026 00h"])

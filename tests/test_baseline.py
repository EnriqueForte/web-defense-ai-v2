"""Línea base sin Docker, credenciales, llamadas IA ni datos operativos.

La suite verifica comportamientos corregidos de fase 1 con datos sintéticos.
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
import ast

from agents.log_analyst import (
    analizar_fuerza_bruta, leer_log, pre_filtrar_lineas, preparar_log_para_agente,
)
from dashboard.services.read_store import atomic_write_text, capture_file, inspect_file, run_atomic_copy

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

    @staticmethod
    def successful_copy(command, **_kwargs):
        Path(command[-1]).write_text("synthetic atomic log", encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")


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


class ReadStoreTests(IsolatedCase):
    def test_capture_reports_missing_and_stable_files(self):
        missing = capture_file(self.base / "missing.md")
        self.assertEqual(missing.status, "missing")
        path = self.base / "reporte.md"
        path.write_text("reporte sintético", encoding="utf-8")
        captured = capture_file(path)
        self.assertEqual(captured.status, "available")
        self.assertEqual(captured.text, "reporte sintético")
        self.assertEqual(len(captured.file_id), 64)
        self.assertEqual(len(captured.digest), 64)

    def test_atomic_write_replaces_complete_file(self):
        path = self.base / "reports" / "current.md"
        path.parent.mkdir()
        path.write_text("anterior", encoding="utf-8")
        atomic_write_text(path, "reporte completo\n")
        self.assertEqual(path.read_text(encoding="utf-8"), "reporte completo\n")
        self.assertEqual(list(path.parent.glob("*.tmp")), [])

    def test_failed_atomic_replace_preserves_previous_report_and_cleans_temp(self):
        path = self.base / "current.md"
        path.write_text("último reporte válido", encoding="utf-8")
        with patch("dashboard.services.read_store.os.replace", side_effect=OSError("reemplazo simulado")):
            with self.assertRaises(OSError):
                atomic_write_text(path, "contenido parcial")
        self.assertEqual(path.read_text(encoding="utf-8"), "último reporte válido")
        self.assertEqual(list(self.base.glob("*.tmp")), [])

    def test_health_metadata_does_not_read_file_content(self):
        path = self.base / "status.log"
        path.write_text("synthetic", encoding="utf-8")
        with patch.object(Path, "read_bytes", side_effect=AssertionError("health no debe leer el archivo")):
            self.assertEqual(inspect_file(path)["status"], "available")

    def test_external_copy_publishes_atomically_after_success(self):
        target = self.base / "access.log"
        target.write_text("last complete log", encoding="utf-8")
        self.process.side_effect = self.successful_copy
        result = run_atomic_copy(["synthetic-copy", "source"], target)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(target.read_text(encoding="utf-8"), "synthetic atomic log")
        self.assertEqual(list(self.base.glob("*.tmp")), [])

    def test_failed_external_copy_keeps_previous_log(self):
        target = self.base / "access.log"
        target.write_text("last complete log", encoding="utf-8")
        self.process.side_effect = None
        self.process.return_value = subprocess.CompletedProcess([], 1, "", "synthetic failure")
        result = run_atomic_copy(["synthetic-copy", "source"], target)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(target.read_text(encoding="utf-8"), "last complete log")
        self.assertEqual(list(self.base.glob("*.tmp")), [])

    def test_all_existing_report_writers_use_atomic_publication(self):
        for filename in ("main.py", "pipeline.py"):
            source = (ROOT / filename).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=filename)
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
            self.assertTrue(any(isinstance(call.func, ast.Name) and call.func.id == "atomic_write_text"
                                for call in calls), filename)
        reporter = ast.parse((ROOT / "agents/report_generator.py").read_text(encoding="utf-8"))
        task_calls = [node for node in ast.walk(reporter)
                      if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Task"]
        self.assertTrue(task_calls)
        self.assertFalse(any(keyword.arg == "output_file" for call in task_calls for keyword in call.keywords))


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
        self.assertEqual(self.web.parsear_amenazas(report())[0]["timestamp"], "-")
        self.assertEqual(self.client.get("/").status_code, 200)
        self.process.assert_not_called()

    def test_report_content_is_server_escaped_before_client_render(self):
        history = self.base / "historial"
        history.mkdir()
        (history / "reporte_sintetico.md").write_text("<script>alert(1)</script>", encoding="utf-8")
        response = self.client.get("/report/reporte_sintetico.md")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"&lt;script&gt;", response.data)
        self.assertNotIn(b"<script>alert(1)</script>", response.data)

    def test_report_routes_reject_invalid_and_missing_names(self):
        self.assertEqual(self.client.get("/report/no.txt").status_code, 400)
        self.assertEqual(self.client.get("/report/reporte_20260430.md").status_code, 404)

    def test_sync_failure_is_reported(self):
        self.process.side_effect = None
        self.process.return_value = subprocess.CompletedProcess([], 1)
        response = self.client.post("/api/sincronizar")
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.get_json()["ok"])

    def test_sync_timeout_has_gateway_timeout_status(self):
        self.process.side_effect = subprocess.TimeoutExpired("docker cp", 15)
        response = self.client.post("/api/sincronizar")
        self.assertEqual(response.status_code, 504)
        self.assertFalse(response.get_json()["ok"])

    def test_sync_without_docker_has_service_unavailable_status(self):
        self.process.side_effect = FileNotFoundError("docker")
        response = self.client.post("/api/sincronizar")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("FileNotFoundError", response.get_json()["error"])

    def test_h01_sync_does_not_claim_new_analysis(self):
        self.process.side_effect = self.successful_copy
        result = self.client.post("/api/sincronizar").get_json()
        self.assertNotIn("analisis completado", result["mensaje"].lower())
        self.assertFalse(result["analisis_ejecutado"])
        self.assertIn("no se ha ejecutado", result["mensaje"].lower())

    def test_h01_sync_does_not_archive_or_notify_from_old_report(self):
        (self.base / "reporte_seguridad.md").write_text(report("192.0.2.9", "CRÍTICA"), encoding="utf-8")
        history = self.base / "historial"
        self.process.side_effect = self.successful_copy
        response = self.client.post("/api/sincronizar")
        self.assertTrue(response.get_json()["ok"])
        self.assertFalse(history.exists())
        self.assertTrue((self.base / "reporte_seguridad.md").exists())

    def test_h02_empty_dashboard_renders(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_h05_state_read_does_not_call_docker(self):
        self.client.get("/api/estado")
        self.process.assert_not_called()

    def test_h05_state_available_without_docker(self):
        self.process.side_effect = FileNotFoundError("Docker simulado no disponible")
        self.assertEqual(self.client.get("/api/estado").status_code, 200)

    def test_h06_low_is_not_medium(self):
        stats = self.web.obtener_estadisticas(self.web.parsear_amenazas(report(severity="BAJA")))
        self.assertEqual(stats["medias"], 0)
        self.assertEqual(stats["bajas"], 1)

    def test_h06_unknown_severity_is_not_counted_as_a_level(self):
        stats = self.web.obtener_estadisticas(self.web.parsear_amenazas(report(severity="INDEFINIDA")))
        self.assertEqual(stats["desconocidas"], 1)
        self.assertEqual(stats["medias"], 0)

    def test_h07_empty_cell_preserves_columns(self):
        threat = self.web.parsear_amenazas(report(ip="198.51.100.7", state=""))[0]
        self.assertEqual(threat["ip"], "198.51.100.7")
        self.assertEqual(threat["estado"], "-")

    def test_h07_reordered_columns_remain_aligned(self):
        reordered = ("## AMENAZAS DETECTADAS\n"
                     "| Tipo de Ataque | IP Origen | Estado | Severidad | Línea |\n"
                     "| --- | --- | --- | --- | --- |\n"
                     "| SQLi | 198.51.100.7 | | BAJA | 2 |\n")
        threat = self.web.parsear_amenazas(reordered)[0]
        self.assertEqual((threat["tipo"], threat["ip"], threat["estado"], threat["severidad"], threat["numero"]),
                         ("SQLi", "198.51.100.7", "-", "BAJA", "2"))

    def test_h08_missing_ip_not_attributed_to_busy_host(self):
        self.assertIn(self.web.parsear_amenazas(report(ip="Desconocido"))[0]["ip"], (None, "-", "Desconocido"))

    def test_h09_timeline_chronological_across_months(self):
        self.log.write_text(line("/item?id=%27") + "\n" + line("/item?id=%27", "01/May/2026:00:00:00"), encoding="utf-8")
        self.assertEqual(self.web.obtener_timeline_ataques()["horas"], ["30/Apr/2026 23h", "01/May/2026 00h"])

    def test_h08_invalid_ipv4_is_unknown(self):
        self.assertEqual(self.web.parsear_amenazas(report(ip="999.1.1.1"))[0]["ip"], "-")

    def test_h08_ipv6_origin_is_preserved(self):
        self.assertEqual(self.web.parsear_amenazas(report(ip="2001:db8::7"))[0]["ip"], "2001:db8::7")

    def test_api_v1_state_has_versioned_snapshot_and_private_cache_headers(self):
        report_path = self.base / "reporte_seguridad.md"
        report_path.write_text(report(), encoding="utf-8")
        self.log.unlink()
        response = self.client.get("/api/v1/estado")
        payload = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["meta"]["api_version"], "1")
        self.assertEqual(payload["meta"]["schema"], "web-defense-ai.estado.v1")
        self.assertEqual(len(payload["meta"]["snapshot_id"]), 64)
        self.assertEqual(payload["meta"]["health"], "degraded")
        self.assertIsNone(payload["data"]["threats"][0]["event_time"])
        self.assertEqual(payload["data"]["threats"][0]["source_report_id"], payload["meta"]["report_id"])
        self.assertEqual(response.headers["Cache-Control"], "no-store, max-age=0")
        self.assertTrue(response.headers["X-Request-ID"])
        self.process.assert_not_called()

    def test_api_v1_snapshot_is_stable_and_changes_with_source_content(self):
        report_path = self.base / "reporte_seguridad.md"
        report_path.write_text(report(), encoding="utf-8")
        first = self.client.get("/api/v1/estado").get_json()["meta"]["snapshot_id"]
        again = self.client.get("/api/v1/estado").get_json()["meta"]["snapshot_id"]
        self.assertEqual(first, again)
        report_path.write_text(report(severity="CRÍTICA"), encoding="utf-8")
        changed = self.client.get("/api/v1/estado").get_json()["meta"]["snapshot_id"]
        self.assertNotEqual(first, changed)

    def test_api_v1_captures_each_state_source_once(self):
        capture = self.web.capture_file
        with patch.object(self.web, "capture_file", wraps=capture) as wrapped:
            self.client.get("/api/v1/estado")
        requested = [call.args[0] for call in wrapped.call_args_list]
        self.assertEqual(requested.count(self.base / "reporte_seguridad.md"), 1)
        self.assertEqual(requested.count(Path(self.log)), 1)

    def test_api_v1_threat_filtering_and_pagination(self):
        rows = ("## AMENAZAS DETECTADAS\n| Línea | Severidad | Tipo | Estado | IP Origen |\n"
                "| --- | --- | --- | --- | --- |\n"
                "| 1 | ALTA | SQLi | Revisar | 192.0.2.10 |\n"
                "| 2 | BAJA | XSS | Desconocido | 198.51.100.4 |\n")
        (self.base / "reporte_seguridad.md").write_text(rows, encoding="utf-8")
        response = self.client.get("/api/v1/amenazas?severidad=ALTA&per_page=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["meta"]["total"], 1)
        self.assertEqual(response.get_json()["data"][0]["type"], "SQLi")
        bad = self.client.get("/api/v1/amenazas?page=0")
        self.assertEqual(bad.status_code, 400)
        self.assertEqual(bad.get_json()["error"]["code"], "invalid_pagination")
        self.assertEqual(bad.get_json()["error"]["request_id"], bad.headers["X-Request-ID"])

    def test_api_v1_reports_are_fully_paginated_and_resolved_by_id(self):
        history = self.base / "historial"
        history.mkdir()
        archive = history / "reporte_20260430_120000.md"
        archive.write_text("## REPORTE SINTÉTICO\nContenido de fixture\n", encoding="utf-8")
        listing = self.client.get("/api/v1/reportes?per_page=1").get_json()
        self.assertEqual(listing["meta"]["total"], 1)
        report_id = listing["data"][0]["id"]
        self.assertEqual(len(report_id), 64)
        detail = self.client.get(f"/api/v1/reportes/{report_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertIn("Contenido de fixture", detail.get_json()["data"]["markdown"])
        self.assertEqual(detail.headers["Cache-Control"], "no-store, max-age=0")
        self.assertEqual(self.client.get("/api/v1/reportes/../secret").status_code, 404)

    def test_api_v1_health_openapi_and_errors(self):
        with patch.object(self.web, "capture_file", side_effect=AssertionError("salud no lee contenidos")):
            health = self.client.get("/api/v1/salud").get_json()
        self.assertEqual(health["data"]["status"], "degraded")
        spec = self.client.get("/api/v1/openapi.json")
        self.assertEqual(spec.status_code, 200)
        contract = spec.get_json()
        self.assertEqual(contract["openapi"], "3.0.3")
        self.assertEqual(set(contract["paths"]), {
            "/estado", "/salud", "/amenazas", "/reportes", "/reportes/{report_id}"
        })
        def collect_refs(node):
            refs = []
            if isinstance(node, dict):
                if "$ref" in node:
                    refs.append(node["$ref"])
                for value in node.values():
                    refs.extend(collect_refs(value))
            elif isinstance(node, list):
                for value in node:
                    refs.extend(collect_refs(value))
            return refs

        references = collect_refs(contract)
        self.assertTrue(references)
        for reference in references:
            self.assertTrue(reference.startswith("#/"), reference)
            target = contract
            for segment in reference[2:].split("/"):
                segment = segment.replace("~1", "/").replace("~0", "~")
                self.assertIn(segment, target, reference)
                target = target[segment]
        missing = self.client.get("/api/v1/no-existe")
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.get_json()["error"]["code"], "not_found")

    def test_legacy_state_contract_remains_unchanged(self):
        data = self.client.get("/api/estado").get_json()
        self.assertEqual(set(data), {"stats", "amenazas", "historial", "log", "ips_log", "timeline", "timestamp"})
        self.process.assert_not_called()

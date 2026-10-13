"""Global configuration failures must stop before worker state or services exist."""

import os
from pathlib import Path
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from config.global_settings import InvalidGlobalSettings, resolve_global_numbers

ROOT = Path(__file__).resolve().parents[1]


class GlobalSettingsTests(TestCase):
    def test_defaults_and_valid_boundaries(self):
        self.assertEqual(resolve_global_numbers({}), {
            "INTERVALO_MINUTOS": 3, "MAX_LINEAS_LOG": 100,
            "UMBRAL_FUERZA_BRUTA": 5, "LLM_TEMPERATURE": 0.1,
        })
        for temperature in ("0", "2"):
            result = resolve_global_numbers({"LLM_TEMPERATURE": temperature,
                "INTERVALO_MINUTOS": " 2 ", "MAX_LINEAS_LOG": "1000",
                "UMBRAL_FUERZA_BRUTA": "100"})
            self.assertEqual(result["LLM_TEMPERATURE"], float(temperature))
            self.assertEqual(result["INTERVALO_MINUTOS"], 2)
            self.assertEqual(result["MAX_LINEAS_LOG"], 1000)
            self.assertEqual(result["UMBRAL_FUERZA_BRUTA"], 100)

    def test_invalid_values_identify_fields_without_echoing_input(self):
        cases = {
            "INTERVALO_MINUTOS": ("", "0", "-1", "1.5", True, None, 1.5, 10 ** 400),
            "MAX_LINEAS_LOG": ("", "0", "1001", "2.5", False, None),
            "UMBRAL_FUERZA_BRUTA": ("", "0", "101", "3.5", True, None),
            "LLM_TEMPERATURE": ("", "nan", "inf", "-inf", "1e309", "-0.1", "2.1", True, None),
        }
        for name, invalid in cases.items():
            for value in (*invalid, "synthetic-private-value"):
                with self.subTest(name=name, value=value):
                    with self.assertRaises(InvalidGlobalSettings) as caught:
                        resolve_global_numbers({name: value})
                    self.assertIn(name, str(caught.exception))
                    self.assertNotIn("synthetic-private-value", str(caught.exception))

    def test_all_errors_are_reported_together(self):
        names = ("INTERVALO_MINUTOS", "MAX_LINEAS_LOG", "UMBRAL_FUERZA_BRUTA", "LLM_TEMPERATURE")
        with self.assertRaises(InvalidGlobalSettings) as caught:
            resolve_global_numbers(dict.fromkeys(names, "invalid"))
        for name in names:
            self.assertIn(name, str(caught.exception))

    def test_settings_import_uses_validation_without_loading_dotenv(self):
        with patch.dict(os.environ, {"INTERVALO_MINUTOS": "2"}, clear=True), \
             patch("dotenv.load_dotenv", return_value=False):
            namespace = runpy.run_path(str(ROOT / "config/settings.py"))
            self.assertEqual(namespace["INTERVALO_MINUTOS"], 2)
            self.assertEqual(namespace["LLM_TEMPERATURE"], 0.1)
            os.environ["MAX_LINEAS_LOG"] = "synthetic-private-value"
            with self.assertRaises(InvalidGlobalSettings):
                runpy.run_path(str(ROOT / "config/settings.py"))

    def test_worker_rejects_invalid_config_before_creating_any_state(self):
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            # A fresh interpreter exercises the actual CLI/import boundary.
            environment = {**os.environ, "PYTHON_DOTENV_DISABLED": "1", "PYTHONIOENCODING": "utf-8",
                "INTERVALO_MINUTOS": "synthetic-private-value",
                "MAX_LINEAS_LOG": "100", "UMBRAL_FUERZA_BRUTA": "5",
                "LLM_TEMPERATURE": "0.1", "ANALYSIS_DB_PATH": str(base / "jobs.sqlite3"),
                "LOG_PATH": str(base / "access.log"), "REPORT_PATH": str(base / "reports")}
            result = subprocess.run([sys.executable, "-B", str(ROOT / "pipeline.py"), "--manual-only"],
                                    cwd=base, env=environment, capture_output=True,
                                    text=True, encoding="utf-8", timeout=10)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn("INTERVALO_MINUTOS", result.stderr)
            self.assertNotIn("synthetic-private-value", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(list(base.iterdir()), [])

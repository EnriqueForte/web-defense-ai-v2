"""Servidor Flask local con datos sintéticos para comprobar la interfaz de fase 4.

No lee .env, logs ni reportes operativos; crea fuentes efímeras en un directorio
temporal y escucha solamente en 127.0.0.1:5000.
"""

import os
import argparse
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--empty", action="store_true", help="Servir fuentes ausentes para comprobar la vista vacía")
    parser.add_argument("--port", type=int, default=5051, help="Puerto local aislado (predeterminado: 5051)")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("el puerto debe estar entre 1024 y 65535")
    with tempfile.TemporaryDirectory(prefix="web-defense-ai-v2-phase4-") as directory:
        base = Path(directory)
        history = base / "historial"
        history.mkdir()
        rows = [
            "## AMENAZAS DETECTADAS",
            "| Línea | Severidad | Tipo | Estado | IP Origen |",
            "| --- | --- | --- | --- | --- |",
        ]
        if not args.empty:
            for index in range(1, 29):
                severity = "ALTA" if index % 2 else "BAJA"
                rows.append(f"| {index} | {severity} | SQLi | Intento observado | 192.0.2.{index} |")
            (base / "reporte_seguridad.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
            for index in range(1, 23):
                (history / f"reporte_sintetico_{index:02d}.md").write_text(
                    f"# Reporte sintético {index}\n\n<script>alert('no ejecutar')</script>\n",
                    encoding="utf-8",
                )
        log = base / "access.log"
        if not args.empty:
            log.write_text(
                '\n'.join(f'192.0.2.{index} - - [30/Apr/2026:23:{index:02d}:00 +0000] '
                          '"GET /item?id=%27 HTTP/1.1" 200 42' for index in range(1, 12)) + "\n",
                encoding="utf-8",
            )
        os.environ["REPORT_PATH"] = str(base)
        os.environ["LOG_PATH"] = str(log)
        os.environ["ANALYSIS_DB_PATH"] = str(base / "jobs.sqlite3")
        os.environ["ANALYSIS_MANUAL_ENABLED"] = "0"
        with patch("dotenv.load_dotenv", return_value=False):
            import dashboard.app as web
        # Fijar las fuentes explícitamente evita depender del momento en que
        # config.settings haya sido importado o de un módulo ya almacenado.
        with patch.multiple(web, REPORT_PATH=base, HISTORIAL=history, LOG_PATH=str(log)), \
             patch("config.model_config.load_local_env", return_value={}), \
             patch.dict(os.environ, {"LLM_PROVIDER": "groq", "LLM_MODEL": "groq/openai/gpt-oss-120b",
                                     "LLM_CONFIG_SOURCE": "", "LLM_PRICING_MODE": "free",
                                     "LLM_FALLBACK_MODELS": "", "GROQ_API_KEY": "", "OPENROUTER_API_KEY": ""}):
            web.app.run(host="127.0.0.1", port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()

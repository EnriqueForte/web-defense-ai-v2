"""Ejecuta la regresión Python y los diagnósticos JS; rechaza cero pruebas."""
from pathlib import Path
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    # Block both dotenv entry points, including the runtime LLM resolver.
    # Individual configuration tests override this with their temporary files.
    with patch("dotenv.load_dotenv", return_value=False), \
         patch("config.model_config.load_local_env", return_value={}), \
         patch.dict(os.environ, {"GROQ_API_KEY": "", "OPENROUTER_API_KEY": "",
                                 "LLM_PROVIDER": "groq", "LLM_MODEL": "groq/openai/gpt-oss-120b",
                                 "LLM_CONFIG_SOURCE": "", "LLM_PRICING_MODE": "free",
                                 "LLM_FALLBACK_MODELS": "", "ANALYSIS_ENGINE_MODE": "legacy"}):
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
        if not suite.countTestCases():
            print("ERROR: no se encontraron pruebas", file=sys.stderr)
            return 1
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    try:
        browser = subprocess.run(["node", "tests/browser_baseline.cjs"], cwd=ROOT, timeout=20)
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"ERROR al comprobar JavaScript: {error}", file=sys.stderr)
        return 1
    print(f"Python: {result.testsRun} casos; {len(result.expectedFailures)} fallos conocidos pendientes.")
    return 0 if result.wasSuccessful() and browser.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Construct the OpenRouter retry adapter offline, without importing main.py."""
import ast
import os
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    with patch("dotenv.load_dotenv", return_value=False), \
         patch.dict(os.environ, {"CREWAI_TRACING_ENABLED": "false", "OTEL_SDK_DISABLED": "true",
                                 "LITELLM_LOCAL_MODEL_COST_MAP": "True", "LITELLM_MODE": "PRODUCTION",
                                 "GROQ_API_KEY": "", "OPENROUTER_API_KEY": ""}), \
         patch("socket.socket.connect", side_effect=AssertionError("Network prohibited")), \
         patch("socket.create_connection", side_effect=AssertionError("Network prohibited")):
        from crewai import LLM
        from pydantic import Field
        from config.model_config import resolve_llm_settings
        from config.llm_resilience import call_with_model_fallback
        source = ROOT / "main.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        definitions = [node for node in tree.body
                       if isinstance(node, (ast.ClassDef, ast.FunctionDef))
                       and node.name in {"RateLimitResilientLLM", "get_llm_con_retry"}]
        settings = resolve_llm_settings(environ={"LLM_PROVIDER": "openrouter",
            "LLM_MODEL": "openrouter/openrouter/free", "OPENROUTER_API_KEY": "synthetic-offline-key"})
        namespace = {"LLM": LLM, "Field": Field,
                     "call_with_model_fallback": call_with_model_fallback,
                     "resolve_llm_settings": lambda: settings}
        exec(compile(ast.Module(body=definitions, type_ignores=[]), str(source), "exec"), namespace)
        adapter = namespace["get_llm_con_retry"]()
        if not isinstance(adapter, namespace["RateLimitResilientLLM"]) or not adapter.is_litellm:
            raise RuntimeError("No se construyó el adaptador LiteLLM de reintentos")
        if adapter.candidate_models != settings["candidates"]:
            raise RuntimeError("Los candidatos no se conservaron")
        from agents.structured_engine import STRUCTURED_MAX_TOKENS, STRUCTURED_REQUEST_TIMEOUT_SECONDS
        structured = namespace["get_llm_con_retry"](max_tokens=STRUCTURED_MAX_TOKENS,
                                                   timeout=STRUCTURED_REQUEST_TIMEOUT_SECONDS)
        if structured.max_tokens != 8192 or structured.timeout != 60:
            raise RuntimeError("No se conservaron los límites estructurados")
        if adapter.max_tokens is not None or adapter.timeout is not None:
            raise RuntimeError("Se alteraron los valores de la ruta anterior")
    print("OpenRouter: adaptadores legacy/estructurado construidos; límites 8192/60 verificados sin call/kickoff, red ni .env operativo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

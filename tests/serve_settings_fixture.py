"""Real Flask configuration routes with only synthetic temporary credentials."""

from contextlib import ExitStack
import argparse
import os
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def serve(base, port, ui_port):
    from dotenv import dotenv_values
    from flask import jsonify, request
    from dashboard.services.runtime_lock import exclusive_lock

    env_file = base / ".env"
    original = "# synthetic E2E configuration\nUNRELATED=synthetic-kept\n"
    env_file.write_text(original, encoding="utf-8")
    mode = {"value": "normal"}
    env = {"PYTHON_DOTENV_DISABLED": "1", "ANALYSIS_MANUAL_ENABLED": "0",
           "NOTIFICATION_DESTINATIONS": "", "REPORT_PATH": str(base / "reports"),
           "LOG_PATH": str(base / "access.log"), "ANALYSIS_DB_PATH": str(base / "jobs.sqlite3")}
    # Clear inherited credentials/settings; never read the operational .env.
    with ExitStack() as stack:
        stack.enter_context(patch.dict(os.environ, env, clear=True))
        stack.enter_context(patch("dotenv.load_dotenv", return_value=False))
        stack.enter_context(patch("socket.socket.connect", side_effect=AssertionError("Outbound network prohibited")))
        stack.enter_context(patch("socket.create_connection", side_effect=AssertionError("Outbound network prohibited")))
        import dashboard.app as web
        from dashboard.services import llm_settings
        stack.enter_context(patch.object(llm_settings, "ENV_FILE", env_file))
        stack.enter_context(patch("config.model_config.load_local_env", side_effect=lambda *args, **kwargs: {
            key: value for key, value in dotenv_values(env_file, interpolate=False).items() if value is not None}))
        stack.enter_context(patch.object(web, "LOCAL_BROWSER_ORIGINS", {f"http://127.0.0.1:{ui_port}"}))
        save = web.save_llm_settings

        def controlled_save(payload):
            if mode["value"] == "locked":
                with exclusive_lock((base / "jobs.sqlite3").with_suffix(".engine.lock")):
                    return save(payload)
            if mode["value"] == "write_error":
                with patch.object(llm_settings, "_atomic_write_env", side_effect=OSError("synthetic write failure")):
                    return save(payload)
            return save(payload)

        stack.enter_context(patch.object(web, "save_llm_settings", controlled_save))

        @web.app.post("/__e2e__/control")
        def control():
            payload = request.get_json()
            if payload.get("reset"):
                env_file.write_text(original, encoding="utf-8")
            mode["value"] = payload.get("mode", "normal")
            return jsonify({"ok": True})

        @web.app.get("/__e2e__/receipt")
        def receipt():
            values = dotenv_values(env_file, interpolate=False)
            return jsonify({"provider": values.get("LLM_PROVIDER"), "model": values.get("LLM_MODEL"),
                "mode": values.get("LLM_PRICING_MODE"), "unrelated": values.get("UNRELATED"),
                "openrouter_key_retained": values.get("OPENROUTER_API_KEY") == "synthetic-e2e-openrouter-key",
                "groq_key_retained": values.get("GROQ_API_KEY") == "synthetic-e2e-groq-key",
                "managed_blocks": env_file.read_text(encoding="utf-8").count(llm_settings.BEGIN_MARKER),
                "jobs_db_exists": (base / "jobs.sqlite3").exists()})

        web.app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--ui-port", type=int, required=True)
    args = parser.parse_args()
    base = args.base.resolve()
    expected = (ROOT / ".local-state/settings-e2e").resolve()
    if not base.is_relative_to(expected) or base == expected or base.is_symlink():
        parser.error("base debe ser un directorio nuevo de pruebas bajo .local-state/settings-e2e")
    if not all(1024 <= port <= 65535 and port not in (3000, 5000) for port in (args.port, args.ui_port)):
        parser.error("usa puertos aislados")
    base.mkdir(exist_ok=False)
    serve(base, args.port, args.ui_port)

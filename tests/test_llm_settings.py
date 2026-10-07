"""LLM configuration regression using temporary dotenv files and no providers."""

import ast
import importlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import Mock, patch

from dotenv import dotenv_values
from config import model_config
from dashboard.services import llm_settings
from dashboard.services.runtime_lock import exclusive_lock


class LocalLLMSettingsTests(TestCase):
    def setUp(self):
        temporary = self.enterContext(TemporaryDirectory())
        self.base = Path(temporary)
        self.env_file = self.base / ".env"
        self.db_path = self.base / "jobs.sqlite3"
        self.enterContext(patch.dict(os.environ, {}, clear=True))
        self.enterContext(patch("dotenv.load_dotenv", return_value=False))
        self.enterContext(patch.object(llm_settings, "ENV_FILE", self.env_file))
        self.enterContext(patch.object(llm_settings, "default_db_path", return_value=self.db_path))
        self.enterContext(patch.object(model_config, "load_local_env", side_effect=lambda *args, **kwargs: {
            key: value for key, value in dotenv_values(self.env_file, interpolate=False).items()
            if value is not None
        }))
        self.enterContext(patch("socket.create_connection", side_effect=AssertionError("Network prohibited")))
        self.enterContext(patch("socket.socket.connect", side_effect=AssertionError("Network prohibited")))
        self.web = importlib.import_module("dashboard.app")
        self.enterContext(patch.dict(self.web.app.config, TESTING=True))
        self.client = self.web.app.test_client()
        self.payload = {"provider": "openrouter", "model": "openrouter/openrouter/free",
                        "pricing_mode": "free", "api_key": "synthetic-openrouter-key"}
        self.headers = {"Origin": "http://127.0.0.1:3000"}

    def save(self, payload=None, headers=None):
        return self.client.put("/api/v1/configuracion/llm", json=self.payload if payload is None else payload,
                               headers=self.headers if headers is None else headers)

    def test_new_installation_defaults_and_never_returns_credentials(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "synthetic-groq-key"}):
            response = self.client.get("/api/v1/configuracion/llm")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"]["provider"], "groq")
        self.assertTrue(response.json["data"]["api_key_configured"])
        self.assertNotIn("synthetic-groq-key", response.get_data(as_text=True))
        self.assertNotIn('"api_key":', response.get_data(as_text=True))
        self.assertFalse(self.env_file.exists())

    def test_save_preserves_unmanaged_text_and_other_provider_key(self):
        original = '# keep this comment\nUNRELATED="literal-${VALUE}"\nGROQ_API_KEY="synthetic-groq-key"\n'
        self.env_file.write_text(original, encoding="utf-8")
        response = self.save()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.env_file.read_text(encoding="utf-8").startswith(original))
        values = dotenv_values(self.env_file, interpolate=False)
        self.assertEqual(values["GROQ_API_KEY"], "synthetic-groq-key")
        self.assertEqual(values["OPENROUTER_API_KEY"], self.payload["api_key"])
        self.assertEqual(values["UNRELATED"], "literal-${VALUE}")
        for key in ("synthetic-groq-key", self.payload["api_key"]):
            self.assertNotIn(key, json.dumps(response.json))

    def test_empty_or_omitted_key_retains_existing_and_replaces_one_block(self):
        self.assertEqual(self.save().status_code, 200)
        for omit in (False, True):
            payload = {**self.payload, "api_key": "", "model": "openrouter/example/custom", "pricing_mode": "paid"}
            if omit:
                payload.pop("api_key")
            self.assertEqual(self.save(payload).status_code, 200)
        content = self.env_file.read_text(encoding="utf-8")
        self.assertEqual(content.count(llm_settings.BEGIN_MARKER), 1)
        self.assertEqual(content.count(llm_settings.END_MARKER), 1)
        self.assertEqual(dotenv_values(self.env_file)["OPENROUTER_API_KEY"], self.payload["api_key"])

    def test_saved_settings_override_stale_worker_environment(self):
        self.assertEqual(self.save().status_code, 200)
        with patch.dict(os.environ, {"LLM_PROVIDER": "groq", "LLM_MODEL": "groq/openai/gpt-oss-20b",
                                     "OPENROUTER_API_KEY": "synthetic-stale-key"}):
            resolved = model_config.resolve_llm_settings()
        self.assertEqual(resolved["provider"], "openrouter")
        self.assertEqual(resolved["model"], self.payload["model"])
        self.assertEqual(resolved["api_key"], self.payload["api_key"])

    def test_custom_paid_selection_has_no_automatic_fallback(self):
        payload = {**self.payload, "model": "openrouter/example/custom", "pricing_mode": "paid"}
        self.assertEqual(self.save(payload).status_code, 200)
        self.assertEqual(model_config.resolve_llm_settings()["candidates"], [payload["model"]])

    def test_invalid_payloads_leave_configuration_unchanged(self):
        original = "UNRELATED=preserve\n"
        self.env_file.write_text(original, encoding="utf-8")
        invalid = [None, [], {}, {**self.payload, "provider": "unknown"},
                   {**self.payload, "model": "groq/wrong-provider"},
                   {**self.payload, "model": "openrouter/example/paid"},
                   {**self.payload, "model": "openrouter/bad model"},
                   {**self.payload, "model": "openrouter/" + "a" * 256},
                   {**self.payload, "pricing_mode": "unknown"},
                   {**self.payload, "api_key": "bad\nkey"},
                   {**self.payload, "api_key": "x" * 4097},
                   {**self.payload, "api_key": "your_api_key_here"},
                   {**self.payload, "api_key": 123},
                   {**self.payload, "base_url": "https://untrusted.example"}]
        for payload in invalid:
            with self.subTest(payload=type(payload).__name__):
                response = self.client.put("/api/v1/configuracion/llm", json=payload, headers=self.headers)
                self.assertIn(response.status_code, (400, 415))
                self.assertEqual(self.env_file.read_text(encoding="utf-8"), original)

    def test_missing_key_cannot_enable_new_provider(self):
        response = self.save({**self.payload, "api_key": ""})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.env_file.exists())

    def test_origin_and_content_type_guards_never_write(self):
        for origin in (None, "", "null", "https://untrusted.example", "http://127.0.0.1:3000.evil.example"):
            headers = {} if origin is None else {"Origin": origin}
            self.assertEqual(self.save(headers=headers).status_code, 403)
        self.assertEqual(self.client.put("/api/v1/configuracion/llm", data="text", headers=self.headers).status_code, 415)
        self.assertFalse(self.env_file.exists())

    def test_each_local_origin_is_accepted(self):
        for origin in self.web.LOCAL_BROWSER_ORIGINS:
            with self.subTest(origin=origin):
                self.assertEqual(self.save(headers={"Origin": origin}).status_code, 200)

    def test_malformed_json_is_rejected_without_creating_configuration(self):
        response = self.client.put("/api/v1/configuracion/llm", data='{"provider":',
                                   content_type="application/json", headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.env_file.exists())

    def test_remote_client_cannot_read_or_save(self):
        for method in ("GET", "PUT"):
            response = self.client.open("/api/v1/configuracion/llm", method=method,
                                        json=self.payload if method == "PUT" else None,
                                        headers=self.headers, environ_overrides={"REMOTE_ADDR": "192.0.2.1"})
            self.assertEqual(response.status_code, 403)
        self.assertFalse(self.env_file.exists())

    def test_active_engine_cycle_or_config_lock_preserves_file(self):
        original = "UNRELATED=preserve\n"
        self.env_file.write_text(original, encoding="utf-8")
        for lock in (self.db_path.with_suffix(".engine.lock"), self.db_path.with_suffix(".cycle.lock"),
                     self.db_path.with_name("llm-config.lock")):
            with self.subTest(lock=lock.name), exclusive_lock(lock):
                response = self.save()
                self.assertEqual(response.status_code, 409)
                self.assertEqual(self.env_file.read_text(encoding="utf-8"), original)

    def test_atomic_replace_failure_preserves_file_and_removes_temporary(self):
        original = "UNRELATED=preserve\n"
        self.env_file.write_text(original, encoding="utf-8")
        with patch.object(llm_settings.os, "replace", side_effect=OSError("synthetic write failure")):
            response = self.save()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json["error"]["code"], "llm_config_save_failed")
        self.assertEqual(self.env_file.read_text(encoding="utf-8"), original)
        self.assertEqual(list(self.base.glob(".env.llm-*.tmp")), [])
        self.assertNotIn(self.payload["api_key"], response.get_data(as_text=True))

    def test_malformed_managed_sections_are_not_overwritten(self):
        for original in (llm_settings.BEGIN_MARKER, llm_settings.END_MARKER,
                         llm_settings.END_MARKER + "\n" + llm_settings.BEGIN_MARKER,
                         (llm_settings.BEGIN_MARKER + "\n" + llm_settings.END_MARKER + "\n") * 2):
            with self.subTest(section=original):
                self.env_file.write_text(original, encoding="utf-8")
                self.assertEqual(self.save().status_code, 400)
                self.assertEqual(self.env_file.read_text(encoding="utf-8"), original)

    def test_analysis_status_reads_only_synthetic_provider_configuration(self):
        self.assertEqual(self.save().status_code, 200)
        with patch.object(self.web, "default_db_path", return_value=self.db_path):
            response = self.client.get("/api/v1/analisis/actual")
        self.assertTrue(response.json["data"]["llm_ready"])
        self.assertEqual(response.json["data"]["llm_provider"], "openrouter")
        self.assertNotIn(self.payload["api_key"], response.get_data(as_text=True))


class LLMConstructionRegressionTests(TestCase):
    def test_openrouter_uses_litellm_route_without_importing_or_running_engine(self):
        # Extract only the factory: main.py replaces stdout on import and builds
        # real CrewAI objects. A double records adapter arguments without network.
        source = Path(__file__).resolve().parents[1] / "main.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        factory = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                       and node.name == "get_llm_con_retry")
        for provider, model in (("openrouter", "openrouter/openrouter/free"), ("groq", "groq/openai/gpt-oss-120b")):
            settings = model_config.resolve_llm_settings(environ={"LLM_PROVIDER": provider, "LLM_MODEL": model,
                                                                  "GROQ_API_KEY": "synthetic", "OPENROUTER_API_KEY": "synthetic"})
            constructor = Mock(return_value=object())
            namespace = {"resolve_llm_settings": lambda: settings, "RateLimitResilientLLM": constructor}
            exec(compile(ast.Module(body=[factory], type_ignores=[]), str(source), "exec"), namespace)
            namespace["get_llm_con_retry"]()
            options = constructor.call_args.kwargs
            self.assertNotIn("max_tokens", options)
            self.assertNotIn("timeout", options)
            self.assertEqual(options["candidate_models"][0], model)
            self.assertEqual(options["additional_params"], {"max_retries": 0})
            if provider == "openrouter":
                self.assertTrue(options["is_litellm"])
                self.assertEqual(options["base_url"], "https://openrouter.ai/api/v1")
            else:
                self.assertNotIn("is_litellm", options)
            namespace["get_llm_con_retry"](max_tokens=8192, timeout=60)
            structured_options = constructor.call_args.kwargs
            self.assertEqual(structured_options["max_tokens"], 8192)
            self.assertEqual(structured_options["timeout"], 60)
            self.assertEqual(structured_options["candidate_models"], options["candidate_models"])

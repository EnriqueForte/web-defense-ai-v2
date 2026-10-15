"""Real CrewAI/LiteLLM HTTP serialization with synthetic responses and no network."""
import ast
from copy import deepcopy
import inspect
import json
import os
from pathlib import Path
import socket
from tempfile import TemporaryDirectory
import time
from unittest import TestCase
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
KEY = "synthetic-groq-transport-key"
ID = "d" * 32


class GroqCacheTransportTests(TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, {
            "LITELLM_LOCAL_MODEL_COST_MAP": "True", "LITELLM_MODE": "PRODUCTION",
            "CREWAI_TRACING_ENABLED": "false", "OTEL_SDK_DISABLED": "true",
            "GROQ_API_KEY": "", "OPENROUTER_API_KEY": ""}))
        self.enterContext(patch("dotenv.load_dotenv", return_value=False))
        original_connect = socket.socket.connect
        def only_internal_socketpair(sock, address):
            caller = inspect.currentframe().f_back
            if caller.f_code.co_name == "socketpair" and caller.f_globals.get("__name__") == "socket":
                return original_connect(sock, address)
            raise AssertionError("Network prohibited")
        self.enterContext(patch("socket.socket.connect", new=only_internal_socketpair))
        self.enterContext(patch("socket.create_connection", side_effect=AssertionError("Network prohibited")))
        from crewai import LLM
        from pydantic import Field
        from config.llm_resilience import call_with_model_fallback
        from crewai.events.event_bus import crewai_event_bus
        self.enterContext(patch.object(crewai_event_bus, "emit", return_value=None))
        tree = ast.parse((ROOT / "main.py").read_text(encoding="utf-8"))
        definitions = [item for item in tree.body if isinstance(item, ast.ClassDef)
                       and item.name == "RateLimitResilientLLM"]
        namespace = {"LLM": LLM, "Field": Field, "time": time,
                     "call_with_model_fallback": call_with_model_fallback}
        exec(compile(ast.Module(body=definitions, type_ignores=[]), str(ROOT / "main.py"), "exec"), namespace)
        self.adapter = namespace["RateLimitResilientLLM"]
        self.requests = []

    def llm(self, model="groq/openai/gpt-oss-120b", **options):
        return self.adapter(model=model, api_key=KEY, max_tokens=8192, timeout=60,
                            additional_params={"max_retries": 0}, rate_limit_retries=0,
                            **options)

    def intercept(self, decide=None):
        import httpx
        def send(_client, request, **_kwargs):
            self.assertIn(request.url.host, {"api.groq.com", "openrouter.ai"})
            self.assertEqual(request.url.path, "/openai/v1/chat/completions"
                             if request.url.host == "api.groq.com" else "/api/v1/chat/completions")
            self.assertEqual(request.headers["authorization"], "Bearer " + KEY)
            body = json.loads(request.content)
            self.requests.append(body)
            if decide is not None:
                status, content = decide(body)
                if status != 200:
                    return httpx.Response(status, request=request, json={"error": {
                        "message": "synthetic rejection", "type": "invalid_request_error"}})
            else:
                # Reproduce Groq's rejection of the internal CrewAI marker.
                if any("cache_breakpoint" in message for message in body["messages"]):
                    return httpx.Response(400, request=request, json={"error": {
                        "message": "cache_breakpoint is unsupported", "type": "invalid_request_error"}})
                content = '{"synthetic":true}'
            return httpx.Response(200, request=request, json={
                "id": "synthetic-response", "object": "chat.completion", "created": 1,
                "model": body["model"], "service_tier": "on_demand",
                "choices": [{"index": 0, "finish_reason": "stop",
                    "message": {"role": "assistant", "content": content}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}})
        return patch("httpx.Client.send", new=send)

    def messages(self):
        from crewai.llms.cache import mark_cache_breakpoint
        return [mark_cache_breakpoint({"role": "system", "content": "Keep literal cache_breakpoint text."}),
                mark_cache_breakpoint({"role": "user", "content": "Synthetic input"})]

    def test_http_rejects_unadapted_marker_but_adapter_preserves_messages_and_limits(self):
        from crewai import LLM
        import litellm
        messages = self.messages()
        before = deepcopy(messages)
        unadapted = LLM(model="groq/openai/gpt-oss-120b", is_litellm=True, api_key=KEY,
                        max_tokens=8192, timeout=60, additional_params={"max_retries": 0})
        with self.intercept():
            with self.assertRaises(litellm.BadRequestError):
                unadapted.call(deepcopy(messages))
            self.assertEqual(self.llm().call(messages), '{"synthetic":true}')
        self.assertEqual(len(self.requests), 2)
        self.assertEqual(messages, before)
        expected = [{k:v for k,v in message.items() if k != "cache_breakpoint"} for message in before]
        self.assertEqual(self.requests[-1]["messages"], expected)
        self.assertEqual(self.requests[-1]["model"], "openai/gpt-oss-120b")
        self.assertEqual(self.requests[-1].get("max_tokens", self.requests[-1].get("max_completion_tokens")), 8192)

    def test_real_structured_crew_generates_markers_and_publishes_with_mock_http(self):
        from agents.structured_engine import run_structured
        from dashboard.services.structured_publication import load_current
        def decide(body):
            self.assertFalse(any("cache_breakpoint" in message for message in body["messages"]))
            return 200, json.dumps({"schema_version":"1", "analysis_id":ID, "candidates":[]})
        with TemporaryDirectory() as temporary, self.intercept(decide):
            root = Path(temporary)
            manifest, _crew = run_structured(
                '192.0.2.1 - - [15/Oct/2026:16:00:00 +0000] "GET / HTTP/1.1" 200 10',
                self.llm(), root, analysis_id=ID, config={})
            self.assertEqual(load_current(root / "structured")[0]["generation"], manifest["generation"])
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(self.requests[0]["messages"][0]["role"], "system")

    def test_other_provider_http_messages_are_unchanged(self):
        from crewai import LLM
        messages = self.messages()
        before = deepcopy(messages)
        def decide(_body):
            return 200, '{"synthetic":true}'
        plain = LLM(model="openrouter/openrouter/free", is_litellm=True, api_key=KEY,
                    base_url="https://openrouter.ai/api/v1", max_tokens=8192, timeout=60,
                    additional_params={"max_retries":0})
        adapted = self.llm("openrouter/openrouter/free", is_litellm=True,
                           base_url="https://openrouter.ai/api/v1")
        with self.intercept(decide):
            plain.call(deepcopy(messages))
            adapted.call(messages)
        self.assertEqual(self.requests[0], self.requests[1])
        self.assertEqual(messages, before)

    def test_fallback_strips_markers_on_each_attempt_and_failure_does_not_mutate_input(self):
        import litellm
        messages = self.messages()
        before = deepcopy(messages)
        def decide(body):
            self.assertFalse(any("cache_breakpoint" in message for message in body["messages"]))
            return (429, "") if body["model"].endswith("120b") else (200, '{"synthetic":true}')
        with self.intercept(decide):
            self.assertEqual(self.llm(candidate_models=["groq/openai/gpt-oss-120b", "groq/openai/gpt-oss-20b"]).call(messages), '{"synthetic":true}')
        self.assertEqual([body["model"] for body in self.requests], ["openai/gpt-oss-120b", "openai/gpt-oss-20b"])
        self.requests.clear()
        with self.intercept(lambda _body: (400,"")):
            with self.assertRaises(litellm.BadRequestError):
                self.llm().call(messages)
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(messages, before)

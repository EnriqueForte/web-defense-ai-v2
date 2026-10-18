"""Real CrewAI/LiteLLM HTTP serialization with synthetic responses and no network."""
import ast
from copy import deepcopy
import hashlib
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
TOKENIZER_CACHE_KEY = "9b5ad71b2ce5302211f9c61530b329a4922fc6a4"
TOKENIZER_SHA256 = "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7"


def tokenizer_fixture_bytes(data):
    # The Windows wheel records CRLF bytes, while tiktoken verifies LF bytes.
    # Use a private temporary fixture; never rewrite package/global caches.
    canonical = data.replace(b"\r\n", b"\n")
    if hashlib.sha256(canonical).hexdigest() != TOKENIZER_SHA256:
        raise ValueError("Unexpected bundled tokenizer asset")
    return canonical


class GroqCacheTransportTests(TestCase):
    def setUp(self):
        self.enterContext(patch.dict(os.environ, {
            "LITELLM_LOCAL_MODEL_COST_MAP": "True", "LITELLM_MODE": "PRODUCTION",
            "LITELLM_RUST": "false",
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
        from importlib import resources
        bundled = resources.files("litellm").joinpath("litellm_core_utils", "tokenizers", TOKENIZER_CACHE_KEY)
        self.tokenizer_bytes = tokenizer_fixture_bytes(bundled.read_bytes())
        cache = Path(self.enterContext(TemporaryDirectory()))
        from config.tokenizer_cache import ASSET_HASHES, verified_bytes
        for key in ASSET_HASHES:
            resource = resources.files("litellm").joinpath("litellm_core_utils", "tokenizers", key)
            (cache / key).write_bytes(verified_bytes(resource.read_bytes(), key))
        self.enterContext(patch.dict(os.environ, {"CUSTOM_TIKTOKEN_CACHE_DIR":str(cache),
                                                 "TIKTOKEN_CACHE_DIR":str(cache)}))
        tree = ast.parse((ROOT / "main.py").read_text(encoding="utf-8"))
        definitions = [item for item in tree.body if isinstance(item, ast.ClassDef)
                       and item.name == "RateLimitResilientLLM"]
        namespace = {"LLM": LLM, "Field": Field, "time": time,
                     "call_with_model_fallback": call_with_model_fallback}
        exec(compile(ast.Module(body=definitions, type_ignores=[]), str(ROOT / "main.py"), "exec"), namespace)
        self.adapter = namespace["RateLimitResilientLLM"]
        self.requests = []

    def llm(self, model="groq/openai/gpt-oss-120b", **options):
        options.setdefault("rate_limit_retries", 0)
        return self.adapter(model=model, api_key=KEY, max_tokens=8192, timeout=60,
                            additional_params={"max_retries": 0},
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
                    error = content if isinstance(content, dict) else {
                        "message": "synthetic rejection", "type": "invalid_request_error"}
                    return httpx.Response(status, request=request, json={"error": error})
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

    def test_private_tokenizer_fixture_accepts_only_verified_lf_or_crlf_asset(self):
        crlf = self.tokenizer_bytes.replace(b"\n", b"\r\n")
        self.assertEqual(tokenizer_fixture_bytes(crlf), self.tokenizer_bytes)
        self.assertEqual(tokenizer_fixture_bytes(self.tokenizer_bytes), self.tokenizer_bytes)
        with self.assertRaisesRegex(ValueError, "Unexpected bundled tokenizer asset"):
            tokenizer_fixture_bytes(self.tokenizer_bytes[:-1])

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

    def test_structured_413_rate_limit_body_is_one_http_without_fallback_or_publication(self):
        from config.llm_resilience import ProviderRequestTooLargeError
        from agents.analysis_diagnostics import safe_exception
        from agents.structured_engine import run_structured
        from agents.evidence_preparation import prepare_evidence
        from dashboard.services.structured_publication import publish
        text = '192.0.2.1 - - [15/Oct/2026:18:00:00 +0000] "GET / HTTP/1.1" 200 10'
        prepared = prepare_evidence(text, ID)
        detection = {"schema_version":"1", "analysis_id":ID, "candidates":[]}
        classification = {"schema_version":"1", "analysis_id":ID, "classifications":[]}
        narrative = {"schema_version":"1", "analysis_id":ID, "summary":"Synthetic scope", "recommendations":[]}
        error = {"message":"Request too large for model; TPM: Limit 8000, Requested 8103",
                 "type":"tokens", "code":"rate_limit_exceeded"}
        llm = self.llm(candidate_models=["groq/openai/gpt-oss-120b", "groq/openai/gpt-oss-20b"],
                       rate_limit_retries=2)
        with TemporaryDirectory() as temporary, self.intercept(lambda _body: (413, error)), \
                patch("config.llm_resilience.time.sleep") as sleep:
            root = Path(temporary)
            publish(root / "structured", prepared, detection, classification, narrative,
                    model="synthetic", prompt_version="test")
            before = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            with self.assertRaises(ProviderRequestTooLargeError) as caught:
                run_structured(text, llm, root, analysis_id=ID, config={})
            metadata = safe_exception(caught.exception)
            self.assertEqual(metadata["http_status"], 413)
            self.assertIn("ProviderRequestTooLargeError", metadata["error_types"])
            after = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(after, before)
            self.assertEqual(len(self.requests), 1)
            self.assertEqual(llm.model, "groq/openai/gpt-oss-120b")
            sleep.assert_not_called()

    def test_compact_lab_prompt_preserves_all_raw_lines_and_eight_post_references(self):
        from datetime import datetime, timedelta
        import tiktoken
        from agents.evidence_preparation import prepare_evidence
        from agents.structured_prototype import compact_json, prompt_evidence
        from agents.structured_engine import run_structured
        from dashboard.services.structured_publication import load_current
        # Explicit synthetic CSRF placeholder, never a captured session value.
        suffix = (' "http://127.0.0.1:4280/vulnerabilities/xss_r/?name=%3Cscript%3Ealert(1)%3C/script%3E'
                  '&user_token=00000000000000000000000000000000" '
                  '"Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"')
        rows = []
        for number in range(1, 39):
            stamp = (datetime(2026, 10, 15, 18, 28) + timedelta(seconds=number)).strftime('%d/Oct/%Y:%H:%M:%S')
            target = '/?name=%3Cscript%3Ealert(1)%3C/script%3E' if number == 31 else '/index.php'
            rows.append(f'192.0.2.1 - - [{stamp} +0000] "GET {target} HTTP/1.1" 200 2000' + suffix)
        for stamp in ('18:29:46','18:29:52','18:29:59','18:30:04','18:30:12','18:30:19','18:30:26','18:30:31'):
            rows.append(f'192.0.2.1 - - [15/Oct/2026:{stamp} +0000] "POST /vulnerabilities/brute/ HTTP/1.1" 200 2148' + suffix)
        text = '\n'.join(rows)
        prepared = prepare_evidence(text, ID)
        original = deepcopy(prepared.bundle.to_dict())
        view = json.loads(compact_json(prompt_evidence(prepared.bundle)))
        self.assertEqual([(dict(zip(view["columns"], row))) for row in view["items"]], [
            {"evidence_id":item.evidence_id, "line_number":item.line_number, "raw":item.raw}
            for item in prepared.bundle.items])
        self.assertEqual(prepared.bundle.to_dict(), original)
        self.assertEqual(prepared.bursts[0]["count"], 8)
        self.assertEqual(len(prepared.bursts[0]["selected_evidence_ids"]), 8)
        refs = {item.line_number: item.evidence_id for item in prepared.bundle.items}
        payloads = [
            {"schema_version":"1", "analysis_id":ID, "candidates":[
                {"candidate_id":"c_xss", "pattern":"xss", "evidence_ids":[refs[31]], "reason":"Synthetic URL"},
                {"candidate_id":"c_brute", "pattern":"brute_force", "evidence_ids":[refs[n] for n in range(39,47)], "reason":"Synthetic frequency"}]},
            {"schema_version":"1", "analysis_id":ID, "classifications":[
                {"candidate_id":candidate, "severity":"unknown", "state":"requires_investigation", "reason":"Outcome unknown"}
                for candidate in ("c_xss","c_brute")]},
            {"schema_version":"1", "analysis_id":ID, "summary":"Synthetic review", "recommendations":[
                {"candidate_id":candidate, "text":"Review application events"} for candidate in ("c_xss","c_brute")]},
        ]
        def decide(_body):
            return 200, json.dumps(payloads[len(self.requests) - 1])
        with TemporaryDirectory() as temporary, self.intercept(decide):
            root = Path(temporary)
            run_structured(text, self.llm(), root, analysis_id=ID, config={})
            _, result, _ = load_current(root / "structured")
        brute = next(f for f in result["findings"] if f["pattern"] == "brute_force")
        self.assertEqual(set(brute["evidence_ids"]), {refs[n] for n in range(39,47)})
        self.assertEqual(result["evidence"], json.loads(json.dumps(original)))
        self.assertEqual(len(self.requests), 3)
        first = self.requests[0]["messages"]
        contents = '\n'.join(message["content"] for message in first)
        self.assertIn(compact_json(view), contents)
        encoding = tiktoken.get_encoding("cl100k_base")
        previous = contents.replace(compact_json(view), json.dumps(original, ensure_ascii=False))
        old_count, new_count = len(encoding.encode(previous)), len(encoding.encode(contents))
        self.assertLess(new_count, old_count * .8)
        self.assertLess(new_count, 7000)  # Local fixture estimate, not the provider's tokenizer/TPM guarantee.

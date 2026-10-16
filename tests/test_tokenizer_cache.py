"""Cold SDK checks use fresh processes, real tokenization and intercepted HTTP."""
import hashlib
from importlib.metadata import distribution
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from config import tokenizer_cache as cache


class TokenizerCacheTests(TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory())).resolve()
        self.enterContext(patch.object(cache, "ROOT", self.root))
        self.enterContext(patch.dict(os.environ, {"CUSTOM_TIKTOKEN_CACHE_DIR": "", "TIKTOKEN_CACHE_DIR": ""}))
        self.package = self.root / "package"
        self.package.mkdir()
        self.assets = {}
        installed = distribution("litellm")
        for key in cache.ASSET_HASHES:
            source = installed.locate_file(cache.RESOURCE_DIR + key)
            self.assets[key] = cache.verified_bytes(Path(source).read_bytes(), key)
            (self.package / key).write_bytes(self.assets[key].replace(b"\n", b"\r\n"))
        self.data = self.assets[cache.CACHE_KEY]
        self.asset = self.package / cache.CACHE_KEY
        self.enterContext(patch.object(cache, "distribution", return_value=SimpleNamespace(
            locate_file=lambda resource: self.package / Path(resource).name)))

    def test_verified_copy_preserves_package_and_reuses_exact_cache(self):
        original = {path.name: path.read_bytes() for path in self.package.iterdir()}
        directory = cache.prepare_tokenizer_cache()
        target = directory / cache.CACHE_KEY
        self.assertEqual(target.read_bytes(), self.data)
        self.assertEqual({path.name: path.read_bytes() for path in directory.iterdir()}, self.assets)
        self.assertEqual({path.name: path.read_bytes() for path in self.package.iterdir()}, original)
        before = target.stat().st_mtime_ns
        with patch.object(cache, "distribution", side_effect=AssertionError("Must reuse cache")):
            self.assertEqual(cache.prepare_tokenizer_cache(), directory)
        self.assertEqual(target.stat().st_mtime_ns, before)
        self.assertEqual(os.environ["CUSTOM_TIKTOKEN_CACHE_DIR"], str(directory))
        self.assertEqual(os.environ["TIKTOKEN_CACHE_DIR"], str(directory))
        self.assertEqual({path.name for path in directory.iterdir()}, set(cache.ASSET_HASHES))

    def test_invalid_asset_does_not_create_cache_or_select_environment(self):
        # A corrupt last resource must not publish the valid earlier resources.
        (self.package / list(cache.ASSET_HASHES)[-1]).write_bytes(b"untrusted or truncated asset")
        with self.assertRaisesRegex(cache.TokenizerResourceError, "tokenizer_asset_invalid"):
            cache.prepare_tokenizer_cache()
        self.assertFalse((self.root / ".local-state").exists())
        self.assertEqual(os.environ["CUSTOM_TIKTOKEN_CACHE_DIR"], "")

    def test_failed_atomic_repair_preserves_previous_file_and_cleans_temporary(self):
        directory = cache.prepare_tokenizer_cache()
        target = directory / cache.CACHE_KEY
        target.write_bytes(b"broken previous cache")
        with patch.object(cache.os, "replace", side_effect=PermissionError("synthetic")):
            with self.assertRaisesRegex(cache.TokenizerResourceError, "tokenizer_cache_unavailable"):
                cache.prepare_tokenizer_cache()
        self.assertEqual(target.read_bytes(), b"broken previous cache")
        self.assertEqual({path.name for path in directory.iterdir()}, set(cache.ASSET_HASHES))
        cache.prepare_tokenizer_cache()
        self.assertEqual(target.read_bytes(), self.data)

    def test_explicit_custom_cache_is_validated_without_writes(self):
        external = self.root / "custom"
        external.mkdir()
        target = external / cache.CACHE_KEY
        for key, data in self.assets.items():
            (external / key).write_bytes(data)
        os.environ["CUSTOM_TIKTOKEN_CACHE_DIR"] = str(external)
        self.assertEqual(cache.prepare_tokenizer_cache(), external)
        self.assertFalse((self.root / ".local-state").exists())
        target.write_bytes(b"user-owned invalid cache")
        with self.assertRaisesRegex(cache.TokenizerResourceError, "tokenizer_custom_cache_invalid"):
            cache.prepare_tokenizer_cache()
        self.assertEqual(target.read_bytes(), b"user-owned invalid cache")

    def test_partial_custom_cache_is_rejected_without_repair_or_selection(self):
        external = self.root / "partial"
        external.mkdir()
        (external / cache.CACHE_KEY).write_bytes(self.data)
        os.environ["CUSTOM_TIKTOKEN_CACHE_DIR"] = str(external)
        with self.assertRaisesRegex(cache.TokenizerResourceError, "tokenizer_custom_cache_invalid"):
            cache.prepare_tokenizer_cache()
        self.assertEqual(os.environ["TIKTOKEN_CACHE_DIR"], "")
        self.assertEqual([path.name for path in external.iterdir()], [cache.CACHE_KEY])
        self.assertFalse((self.root / ".local-state").exists())

    def test_concurrent_valid_publication_can_win_atomic_replacement(self):
        directory = cache.prepare_tokenizer_cache()
        target = directory / cache.CACHE_KEY
        target.write_bytes(b"broken cache")
        def published_elsewhere(_temporary, destination):
            destination.write_bytes(self.data)
            raise PermissionError("synthetic sharing violation")
        with patch.object(cache.os, "replace", side_effect=published_elsewhere):
            self.assertEqual(cache.prepare_tokenizer_cache(), directory)
        self.assertEqual(target.read_bytes(), self.data)
        self.assertEqual({path.name for path in directory.iterdir()}, set(cache.ASSET_HASHES))

    def test_cache_links_are_rejected_before_writes(self):
        directory = self.root / ".local-state"
        directory.mkdir()
        original = Path.is_symlink
        with patch.object(Path, "is_symlink", new=lambda path: path == directory or original(path)):
            with self.assertRaisesRegex(cache.TokenizerResourceError, "tokenizer_cache_link"):
                cache.prepare_tokenizer_cache()
        self.assertEqual(list(directory.iterdir()), [])

    def test_equivalent_root_spelling_uses_canonical_cache_and_link_checks(self):
        # Windows temporary paths can use short names; the product resolves its
        # root. A '..' alias reproduces the lexical mismatch on both platforms.
        inner = self.root / "inner"
        inner.mkdir()
        alias = inner / ".."
        directory = self.root / ".local-state"
        with patch.object(cache, "ROOT", alias):
            selected = cache.prepare_tokenizer_cache()
            self.assertTrue(selected.is_relative_to(alias.resolve()))
            self.assertFalse(selected.is_relative_to(alias))
            self.assertEqual({path.name for path in selected.iterdir()}, set(cache.ASSET_HASHES))
            original = Path.is_symlink
            with patch.object(Path, "is_symlink", new=lambda path: path == directory or original(path)):
                with self.assertRaisesRegex(cache.TokenizerResourceError, "tokenizer_cache_link"):
                    cache.prepare_tokenizer_cache()

    def test_cold_installed_lf_crlf_and_invalid_assets_through_real_adapter(self):
        for style in ("installed", "lf", "crlf", "invalid"):
            with self.subTest(style=style):
                result = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), style],
                                        cwd=ROOT, capture_output=True, text=True, timeout=90)
                self.assertEqual(result.returncode, 0, result.stdout[-3000:] + result.stderr[-3000:])
                self.assertIn('"cold_tokenizer": "' + style + '"', result.stdout)


def cold_check(style):
    import ast
    import inspect
    import socket
    import time
    from contextlib import ExitStack
    with TemporaryDirectory() as directory, ExitStack() as context:
        root = Path(directory).resolve()
        context.enter_context(patch.object(cache, "ROOT", root))
        context.enter_context(patch.dict(os.environ, {
            "CUSTOM_TIKTOKEN_CACHE_DIR": "", "TIKTOKEN_CACHE_DIR": str(root / "empty"),
            "LITELLM_RUST": "false", "LITELLM_LOCAL_MODEL_COST_MAP": "True",
            "LITELLM_MODE": "PRODUCTION", "CREWAI_TRACING_ENABLED": "false",
            "OTEL_SDK_DISABLED": "true", "GROQ_API_KEY": "", "OPENROUTER_API_KEY": ""}))
        context.enter_context(patch("dotenv.load_dotenv", return_value=False))
        connect = socket.socket.connect
        def offline(sock, address):
            caller = inspect.currentframe().f_back
            if caller.f_code.co_name == "socketpair" and caller.f_globals.get("__name__") == "socket":
                return connect(sock, address)
            raise AssertionError("Network prohibited")
        context.enter_context(patch("socket.socket.connect", new=offline))
        context.enter_context(patch("socket.create_connection", side_effect=AssertionError("Network prohibited")))
        # Only replace the bundled resource location; use the production loader,
        # real cl100k parsing, CrewAI/LiteLLM serialization and retry adapter.
        package = root / "package"
        package.mkdir()
        original = {}
        installed = distribution("litellm")
        for key in cache.ASSET_HASHES:
            raw = Path(installed.locate_file(cache.RESOURCE_DIR + key)).read_bytes()
            data = raw if style == "installed" else cache.verified_bytes(raw, key)
            if style == "crlf":
                data = data.replace(b"\n", b"\r\n")
            elif style == "invalid" and key == list(cache.ASSET_HASHES)[-1]:
                data = data[:-1]
            original[key] = data
            (package / key).write_bytes(data)
        context.enter_context(patch.object(cache, "distribution", return_value=SimpleNamespace(
            locate_file=lambda resource: package / Path(resource).name)))
        assert "litellm.litellm_core_utils.default_encoding" not in sys.modules
        import httpx
        requests = []
        def send(_client, request, **_kwargs):
            assert request.url.host == "api.groq.com"
            body = json.loads(request.content)
            requests.append(body)
            return httpx.Response(200, request=request, json={
                "id": "synthetic", "object": "chat.completion", "created": 1,
                "model": body["model"], "service_tier": "on_demand",
                "choices": [{"index": 0, "finish_reason": "stop",
                    "message": {"role": "assistant", "content": "synthetic result"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}})
        context.enter_context(patch("httpx.Client.send", new=send))
        from crewai import LLM
        from crewai.events.event_bus import crewai_event_bus
        from pydantic import Field
        from config.llm_resilience import call_with_model_fallback
        context.enter_context(patch.object(crewai_event_bus, "emit", return_value=None))
        tree = ast.parse((ROOT / "main.py").read_text(encoding="utf-8"))
        definitions = [node for node in tree.body if isinstance(node, ast.ClassDef)
                       and node.name == "RateLimitResilientLLM"]
        namespace = {"LLM": LLM, "Field": Field, "time": time,
                     "call_with_model_fallback": call_with_model_fallback}
        exec(compile(ast.Module(body=definitions, type_ignores=[]), str(ROOT / "main.py"), "exec"), namespace)
        llm = namespace["RateLimitResilientLLM"](model="groq/openai/gpt-oss-120b",
            api_key="synthetic-cold-key", max_tokens=8192, timeout=60,
            additional_params={"max_retries": 0}, rate_limit_retries=0)
        if style == "invalid":
            try:
                llm.call([{"role": "user", "content": "Synthetic input"}])
            except cache.TokenizerResourceError:
                pass
            else:
                raise AssertionError("Invalid asset accepted")
            assert requests == []
            assert not (root / ".local-state").exists()
        else:
            assert llm.call([{"role": "user", "content": "Synthetic input"}]) == "synthetic result"
            assert len(requests) == 1
            # Exercise the second SDK tokenizer from a cold registry. Previously
            # the cl100k-only directory hid o200k and triggered a download here.
            import litellm
            assert litellm.token_counter(model="gpt-4o", text="Synthetic input") > 0
            import tiktoken
            for name in ("cl100k_base", "o200k_base", "p50k_base", "o200k_harmony", "p50k_edit"):
                encoding = tiktoken.get_encoding(name)
                assert encoding.decode(encoding.encode("Comprobación real sin red")) == "Comprobación real sin red"
            target = Path(os.environ["TIKTOKEN_CACHE_DIR"]) / cache.CACHE_KEY
            assert target.is_relative_to(root)
            assert {path.name for path in target.parent.iterdir()} == set(cache.ASSET_HASHES)
            for key, expected in cache.ASSET_HASHES.items():
                assert hashlib.sha256((target.parent / key).read_bytes()).hexdigest() == expected
        assert {path.name: path.read_bytes() for path in package.iterdir()} == original
        print(json.dumps({"cold_tokenizer": style, "http_requests": len(requests)}))


if __name__ == "__main__":
    cold_check(sys.argv[1])

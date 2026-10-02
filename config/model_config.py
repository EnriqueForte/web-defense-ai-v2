"""Model catalog and environment resolution for supported LLM providers."""

import os
import re
from pathlib import Path

from dotenv import dotenv_values


DEFAULT_LLM_MODEL = "groq/openai/gpt-oss-120b"
DEFAULT_LLM_FALLBACKS = ("groq/openai/gpt-oss-20b",)
RETIRED_LLM_MODELS = {
    "groq/meta-llama/llama-4-scout-17b-16e-instruct",
    "groq/llama-3.3-70b-versatile",
    "groq/llama-3.1-8b-instant",
}
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"

PROVIDER_CATALOG = {
    "groq": {
        "label": "Groq",
        "key_env": "GROQ_API_KEY",
        "base_url": None,
        "default_model": DEFAULT_LLM_MODEL,
        "free_models": (DEFAULT_LLM_MODEL, "groq/openai/gpt-oss-20b"),
        "fallbacks": DEFAULT_LLM_FALLBACKS,
        "prefix": "groq/",
    },
    "openrouter": {
        "label": "OpenRouter",
        "key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "openrouter/openrouter/free",
        "free_models": ("openrouter/openrouter/free",),
        "fallbacks": (),
        "prefix": "openrouter/",
    },
}

_PLACEHOLDER_KEYS = {
    "your_groq_api_key_here",
    "your_openrouter_api_key_here",
    "your_api_key_here",
}
_MODEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")


def _clean_key(value):
    value = (value or "").strip()
    return "" if value.casefold() in _PLACEHOLDER_KEYS else value


def load_local_env(env_file=ENV_FILE):
    """Read local dotenv values for runtime use; callers must never expose them."""
    try:
        return {key: value for key, value in dotenv_values(env_file, interpolate=False).items()
                if key and value is not None}
    except OSError:
        return {}


def _active_values(environ=None, env_file=ENV_FILE):
    environment = os.environ if environ is None else environ
    local = load_local_env(env_file) if environ is None else {}
    managed = local.get("LLM_CONFIG_SOURCE") == "dashboard"
    values = dict(local)
    values.update(environment)
    if managed:
        # Dashboard-owned model selection must take effect for a long-running worker
        # that launches a fresh engine process with its original inherited environment.
        for name in ("LLM_CONFIG_SOURCE", "LLM_PROVIDER", "LLM_MODEL", "LLM_PRICING_MODE", "LLM_FALLBACK_MODELS"):
            if name in local:
                values[name] = local[name]
        values["LLM_CONFIG_SOURCE"] = "dashboard"
    # Dashboard-saved credentials take priority over a worker's stale environment;
    # other credentials can still come from an existing environment source.
    for provider in PROVIDER_CATALOG.values():
        name = provider["key_env"]
        if managed and _clean_key(local.get(name)):
            values[name] = local[name]
        elif not _clean_key(values.get(name)):
            values[name] = environment.get(name, local.get(name, ""))
    return values


def resolve_llm_settings(environ=None, env_file=ENV_FILE):
    """Resolve runtime settings, keeping credentials out of public responses."""
    values = _active_values(environ=environ, env_file=env_file)
    provider_id = (values.get("LLM_PROVIDER") or "").strip().lower()
    model = (values.get("LLM_MODEL") or "").strip()
    if provider_id not in PROVIDER_CATALOG:
        provider_id = next((name for name, item in PROVIDER_CATALOG.items()
                            if model.startswith(item["prefix"])), "groq")
    provider = PROVIDER_CATALOG[provider_id]
    if not model:
        model = provider["default_model"]
    if model in RETIRED_LLM_MODELS:
        model = provider["default_model"]
    if not model.startswith(provider["prefix"]) or not _MODEL_ID.fullmatch(model):
        model = provider["default_model"]
    pricing_mode = (values.get("LLM_PRICING_MODE") or "").strip().lower()
    if pricing_mode not in {"free", "paid"}:
        pricing_mode = "free" if model in provider["free_models"] else "paid"
    key = _clean_key(values.get(provider["key_env"]))
    try:
        temperature = float(values.get("LLM_TEMPERATURE", "0.1"))
    except (TypeError, ValueError):
        temperature = 0.1
    try:
        retries = max(0, min(10, int(values.get("LLM_RATE_LIMIT_RETRIES", "2"))))
        backoff = max(0.0, min(120.0, float(values.get("LLM_RATE_LIMIT_BACKOFF_SECONDS", "10"))))
        max_wait = max(0.0, min(900.0, float(values.get("LLM_RATE_LIMIT_MAX_WAIT_SECONDS", "45"))))
    except (TypeError, ValueError):
        retries, backoff, max_wait = 2, 10.0, 45.0
    explicit_paid_selection = (
        (values.get("LLM_PRICING_MODE") or "").strip().lower() == "paid"
    )
    if explicit_paid_selection:
        candidates = [model]
    else:
        configured = values.get("LLM_FALLBACK_MODELS")
        fallbacks = (configured.split(",") if configured is not None
                     else tuple(candidate for candidate in provider["free_models"] if candidate != model))
        dashboard_free_selection = (
            values.get("LLM_CONFIG_SOURCE") == "dashboard" and pricing_mode == "free"
        )
        candidates = [model]
        candidates.extend(candidate.strip() for candidate in fallbacks
                          if candidate.strip().startswith(provider["prefix"])
                          and candidate.strip() not in RETIRED_LLM_MODELS
                          and (not dashboard_free_selection or candidate.strip() in provider["free_models"])
                          and _MODEL_ID.fullmatch(candidate.strip()))
    candidates = list(dict.fromkeys(candidates))
    return {
        "provider": provider_id,
        "provider_label": provider["label"],
        "model": model,
        "pricing_mode": pricing_mode,
        "api_key": key,
        "api_key_configured": bool(key),
        "base_url": provider["base_url"],
        "candidates": candidates,
        "temperature": temperature,
        "rate_limit_retries": retries,
        "rate_limit_backoff_seconds": backoff,
        "rate_limit_max_wait_seconds": max_wait,
    }


def configured_model_candidates(environ=None):
    """Return unique preferred/fallback model IDs without making network calls."""
    return resolve_llm_settings(environ=environ)["candidates"]


def configured_provider_keys(environ=None, env_file=ENV_FILE):
    """Return configured credential values for internal redaction only."""
    values = _active_values(environ=environ, env_file=env_file)
    environment = os.environ if environ is None else environ
    local = load_local_env(env_file) if environ is None else {}
    keys = []
    for provider in PROVIDER_CATALOG.values():
        name = provider["key_env"]
        keys.extend((_clean_key(values.get(name)), _clean_key(local.get(name)), _clean_key(environment.get(name))))
    return list(dict.fromkeys(key for key in keys if key))


def resolve_provider_key(provider_id, environ=None, env_file=ENV_FILE):
    """Resolve a provider credential for internal use without exposing it to clients."""
    provider = PROVIDER_CATALOG.get(provider_id)
    if provider is None:
        return ""
    return _clean_key(_active_values(environ=environ, env_file=env_file).get(provider["key_env"]))

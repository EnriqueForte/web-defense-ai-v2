"""Model selection shared by the CrewAI entry points."""

import os


DEFAULT_LLM_MODEL = "groq/openai/gpt-oss-120b"
DEFAULT_LLM_FALLBACKS = ("groq/openai/gpt-oss-20b",)
RETIRED_LLM_MODELS = {
    "groq/meta-llama/llama-4-scout-17b-16e-instruct",
    "groq/llama-3.3-70b-versatile",
    "groq/llama-3.1-8b-instant",
}


def configured_model_candidates(environ=None):
    """Return unique preferred/fallback model IDs without making network calls."""
    environ = os.environ if environ is None else environ
    primary = environ.get("LLM_MODEL", DEFAULT_LLM_MODEL).strip() or DEFAULT_LLM_MODEL
    if primary in RETIRED_LLM_MODELS:
        primary = DEFAULT_LLM_MODEL
    configured_fallbacks = environ.get("LLM_FALLBACK_MODELS")
    fallback_values = (
        configured_fallbacks.split(",")
        if configured_fallbacks is not None
        else DEFAULT_LLM_FALLBACKS
    )
    candidates = [primary]
    candidates.extend(
        value.strip() for value in fallback_values
        if value.strip() and value.strip() not in RETIRED_LLM_MODELS
    )
    return list(dict.fromkeys(candidates))

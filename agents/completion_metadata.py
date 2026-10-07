"""Allowlisted completion metadata, independent of the SDK and response content."""
import re

MODEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*/[A-Za-z0-9][A-Za-z0-9._:/-]{0,254}$")
FINISH_REASONS = {"stop", "length", "tool_calls", "function_call", "content_filter", "error"}


def _field(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name, None) if value is not None else None


def _number(value):
    return value if type(value) is int and 0 <= value <= 1_000_000_000 else None


def safe_model(value, secrets=()):
    if not isinstance(value, str) or len(value) > 256 or not MODEL_ID.fullmatch(value):
        return None
    if any(secret and secret in value for secret in secrets):
        return None
    return value


def completion_metadata(response, *, requested_model=None, max_tokens=None, secrets=()):
    """Never serializes the response, headers, IDs, messages, reasoning or kwargs."""
    try:
        choices = _field(response, "choices")
        first = choices[0] if isinstance(choices, (list, tuple)) and choices else None
        message = _field(first, "message")
        content = _field(message, "content")
        reasoning = _field(message, "reasoning_content")
        if reasoning is None:
            reasoning = _field(message, "reasoning")
        details = _field(message, "reasoning_details")
        usage = _field(response, "usage")
        completion_details = _field(usage, "completion_tokens_details")
        reason = _field(first, "finish_reason")
        return {
            "metadata_status": "captured",
            "requested_model": safe_model(requested_model, secrets),
            "response_model": safe_model(_field(response, "model"), secrets),
            "max_tokens": _number(max_tokens),
            "finish_reason": reason if isinstance(reason, str) and reason in FINISH_REASONS else None,
            "choice_count": _number(len(choices)) if isinstance(choices, (list, tuple)) else None,
            "content_characters": len(content) if isinstance(content, str) else None,
            "content_present": bool(content) if isinstance(content, str) else False,
            "reasoning_present": bool(reasoning) or bool(details),
            "usage": {
                "prompt_tokens": _number(_field(usage, "prompt_tokens")),
                "completion_tokens": _number(_field(usage, "completion_tokens")),
                "total_tokens": _number(_field(usage, "total_tokens")),
                "reasoning_tokens": _number(_field(completion_details, "reasoning_tokens")),
            },
        }
    except Exception:
        # Unexpected SDK shapes must not alter the completion's behavior.
        return {"metadata_status": "unavailable"}

"""Rate-limit recognition and bounded model-call retries."""

import re
import time


def is_rate_limit_error(error: Exception) -> bool:
    status = getattr(error, "status_code", None) or getattr(error, "status", None)
    if status == 429 or "ratelimit" in type(error).__name__.replace("_", "").lower():
        return True
    message = str(error).lower()
    return any(token in message for token in ("rate_limit", "rate limit", "too many requests"))


def retry_after_seconds(error: Exception) -> float | None:
    for owner in (error, getattr(error, "response", None)):
        headers = getattr(owner, "headers", None)
        if headers:
            value = headers.get("retry-after") or headers.get("Retry-After")
            if value:
                try:
                    return max(0.0, float(value))
                except (TypeError, ValueError):
                    pass
    match = re.search(r"try again in\s*([0-9]+(?:\.[0-9]+)?)\s*s", str(error), re.IGNORECASE)
    return float(match.group(1)) if match else None


def call_with_model_fallback(
    invoke,
    models,
    select_model,
    *,
    retries=2,
    backoff_seconds=10.0,
    max_wait_seconds=45.0,
    sleep=time.sleep,
):
    """Retry only rate limits, then try configured fallback models within a wait budget."""
    candidates = list(dict.fromkeys(models))
    if not candidates:
        raise ValueError("Se requiere al menos un modelo para llamar al proveedor.")
    retries = max(0, min(int(retries), 5))
    backoff_seconds = max(0.1, float(backoff_seconds))
    wait_budget = max(0.0, float(max_wait_seconds))
    waited = 0.0
    last_rate_limit = None

    for model in candidates:
        select_model(model)
        for attempt in range(retries + 1):
            try:
                return invoke()
            except Exception as error:
                if not is_rate_limit_error(error):
                    raise
                last_rate_limit = error
                if attempt >= retries or waited >= wait_budget:
                    break
                server_delay = retry_after_seconds(error)
                delay = server_delay if server_delay is not None else backoff_seconds * (2 ** attempt)
                remaining = wait_budget - waited
                if delay > remaining:
                    break
                if delay > 0:
                    sleep(delay)
                    waited += delay

    if last_rate_limit is not None:
        raise last_rate_limit
    raise RuntimeError("No se pudo invocar ningún modelo configurado.")

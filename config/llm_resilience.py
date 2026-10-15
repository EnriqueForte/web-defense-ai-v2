"""Rate-limit recognition and bounded model-call retries."""

import re
import time


class ProviderRequestTooLargeError(RuntimeError):
    """Terminal HTTP 413 without SDK text/causes that trigger nested retries."""

    status_code = 413


def _error_details(error):
    # An SDK may label an HTTP 413 body rate_limit_exceeded. Its numeric
    # status takes precedence over message/class heuristics: waiting cannot
    # make that same oversized request smaller. Inspect bounded wrappers too.
    pending, seen, statuses, inferred = [error], set(), [], False
    while pending and len(seen) < 8:
        current = pending.pop(0)
        if current is None or id(current) in seen:
            continue
        seen.add(id(current))
        for name in ("status_code", "status"):
            try:
                status = getattr(current, name, None)
                if type(status) is int and 300 <= status <= 599:
                    statuses.append(status)
            except Exception:
                pass
        try:
            status = getattr(getattr(current, "response", None), "status_code", None)
            if type(status) is int and 300 <= status <= 599:
                statuses.append(status)
        except Exception:
            pass
        inferred |= "ratelimit" in type(current).__name__.replace("_", "").lower()
        try:
            message = str(current).lower()
            inferred |= any(token in message for token in ("rate_limit", "rate limit", "too many requests"))
        except Exception:
            pass
        for name in ("__cause__", "__context__"):
            try:
                pending.append(getattr(current, name, None))
            except Exception:
                pass
    return statuses, inferred


def is_rate_limit_error(error: Exception) -> bool:
    statuses, inferred = _error_details(error)
    return all(status == 429 for status in statuses) if statuses else inferred


def _invoke_with_terminal_http_errors(invoke):
    try:
        return invoke()
    except Exception as error:
        if 413 not in _error_details(error)[0]:
            raise
    # Raise outside the except block. CrewAI inspects implicit contexts even
    # with "from None"; retaining an SDK RateLimitError would repeat the call.
    raise ProviderRequestTooLargeError("provider_request_too_large") from None


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
                return _invoke_with_terminal_http_errors(invoke)
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

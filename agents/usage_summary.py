"""Reconcile allowlisted SDK usage with recorded completion metadata; no inferred tokens."""
FIELDS = ("prompt_tokens", "completion_tokens", "total_tokens", "reasoning_tokens")
SDK_FIELDS = (*FIELDS, "cached_prompt_tokens", "cache_creation_tokens", "successful_requests")


def _number(value):
    return value if type(value) is int and 0 <= value <= 1_000_000_000 else None


def summarize_usage(diagnostics, sdk=None):
    sdk = sdk if isinstance(sdk, dict) else {}
    safe_sdk = {name: _number(sdk.get(name)) for name in SDK_FIELDS}
    completed = [event for event in diagnostics.get("events", [])
                 if event.get("event") == "completion_returned"]
    calls = _number(diagnostics.get("calls"))
    identifiers = [event.get("call") for event in completed]
    coverage = (calls is not None and calls > 0 and not diagnostics.get("dropped_events")
                and len(completed) == calls and all(type(identifier) is int for identifier in identifiers)
                and set(identifiers) == set(range(1, calls + 1)))
    totals = {}
    warnings = []
    for name in FIELDS:
        values = [_number(event.get("usage", {}).get(name)) if isinstance(event.get("usage"), dict) else None
                  for event in completed]
        totals[name] = sum(values) if coverage and all(value is not None for value in values) else None
    for event in completed:
        values = event.get("usage", {})
        if not isinstance(values, dict):
            continue
        prompt, output, total, reasoning = (_number(values.get(name)) for name in FIELDS)
        if output is not None and reasoning is not None and reasoning > output:
            warnings.append({"call": _number(event.get("call")), "code": "reasoning_exceeds_completion"})
        if prompt is not None and output is not None and total is not None and prompt + output != total:
            warnings.append({"call": _number(event.get("call")), "code": "total_token_mismatch"})
    discrepancies = [{"field": name, "sdk": safe_sdk[name], "completion_metadata": totals[name]}
                     for name in FIELDS if safe_sdk[name] is not None and totals[name] is not None
                     and safe_sdk[name] != totals[name]]
    return {"usage": {"source": "completion_metadata", "complete": coverage and all(value is not None for value in totals.values()),
                      "observed_completions": len(completed), **totals},
            "usage_sdk": safe_sdk, "usage_discrepancies": discrepancies, "usage_warnings": warnings}

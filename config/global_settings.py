"""Validate global numeric settings without reading files or contacting services."""

import math


class InvalidGlobalSettings(ValueError):
    """A configuration error safe to display without the supplied values."""


def resolve_global_numbers(values):
    """Reject invalid supplied values; use defaults only when a key is absent."""
    resolved = {}
    errors = []
    for name, default, maximum in (
        ("INTERVALO_MINUTOS", 3, None),
        ("MAX_LINEAS_LOG", 100, 1000),
        ("UMBRAL_FUERZA_BRUTA", 5, 100),
    ):
        requirement = (f"un entero entre 1 y {maximum}" if maximum is not None
                       else "un entero mayor o igual que 1 con un intervalo en segundos finito")
        try:
            raw = values.get(name, str(default))
            if type(raw) not in (str, int):
                raise ValueError
            value = int(raw)
            if value < 1 or (maximum is not None and value > maximum):
                raise ValueError
            if maximum is None and not math.isfinite(value * 60):
                raise ValueError
        except (TypeError, ValueError, OverflowError):
            errors.append(f"{name}: debe ser {requirement}.")
        else:
            resolved[name] = value

    try:
        raw = values.get("LLM_TEMPERATURE", "0.1")
        if type(raw) not in (str, int, float):
            raise ValueError
        temperature = float(raw)
        if not math.isfinite(temperature) or not 0 <= temperature <= 2:
            raise ValueError
    except (TypeError, ValueError, OverflowError):
        errors.append("LLM_TEMPERATURE: debe ser un número finito entre 0 y 2.")
    else:
        resolved["LLM_TEMPERATURE"] = temperature

    if errors:
        raise InvalidGlobalSettings("Configuración inválida. " + " ".join(errors)) from None
    return resolved

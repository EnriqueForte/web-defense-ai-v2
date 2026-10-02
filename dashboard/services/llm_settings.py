"""Local dashboard-managed LLM settings stored in the ignored project .env."""

import os
import json
import re
import tempfile

from config.model_config import (
    ENV_FILE,
    PROVIDER_CATALOG,
    resolve_llm_settings,
    resolve_provider_key,
)
from dashboard.services.analysis_jobs import default_db_path
from dashboard.services.runtime_lock import AlreadyRunning, exclusive_lock
from dotenv import dotenv_values


BEGIN_MARKER = "# BEGIN web-defense-ai V2 LLM settings"
END_MARKER = "# END web-defense-ai V2 LLM settings"
MODEL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")
ALLOWED_FIELDS = {"provider", "model", "pricing_mode", "api_key"}


class InvalidLLMSettings(ValueError):
    pass


def public_llm_settings():
    """Return provider/model choices and key-presence flags, never secret values."""
    resolved = resolve_llm_settings()
    providers = []
    for provider_id, provider in PROVIDER_CATALOG.items():
        providers.append({
            "id": provider_id,
            "label": provider["label"],
            "default_model": provider["default_model"],
            "free_models": list(provider["free_models"]),
            "api_key_configured": bool(resolve_provider_key(provider_id)),
        })
    return {
        "provider": resolved["provider"],
        "model": resolved["model"],
        "pricing_mode": resolved["pricing_mode"],
        "api_key_configured": resolved["api_key_configured"],
        "providers": providers,
    }


def _read_local_env():
    try:
        return {key: value for key, value in dotenv_values(ENV_FILE, interpolate=False).items()
                if key and value is not None}
    except OSError:
        return {}


def _validate_payload(payload):
    if not isinstance(payload, dict) or set(payload) - ALLOWED_FIELDS:
        raise InvalidLLMSettings("La configuración contiene campos no admitidos.")
    provider_id = payload.get("provider")
    mode = payload.get("pricing_mode")
    model = payload.get("model")
    api_key = payload.get("api_key", "")
    if not isinstance(provider_id, str) or provider_id not in PROVIDER_CATALOG:
        raise InvalidLLMSettings("Selecciona un proveedor disponible.")
    if not isinstance(mode, str) or mode not in {"free", "paid"}:
        raise InvalidLLMSettings("Selecciona un modo de modelo disponible.")
    if not isinstance(model, str) or not model or len(model) > 256 or not MODEL_ID.fullmatch(model):
        raise InvalidLLMSettings("El identificador del modelo no tiene un formato válido.")
    provider = PROVIDER_CATALOG[provider_id]
    if not model.startswith(provider["prefix"]):
        raise InvalidLLMSettings(f"El identificador del modelo debe comenzar por {provider['prefix']}.")
    if mode == "free" and model not in provider["free_models"]:
        raise InvalidLLMSettings("El modelo no pertenece a las opciones gratuitas disponibles.")
    if not isinstance(api_key, str) or len(api_key) > 4096 or any(ord(char) < 32 or ord(char) == 127 for char in api_key):
        raise InvalidLLMSettings("La clave API no tiene un formato válido.")
    api_key = api_key.strip()
    if api_key.casefold() in {"your_groq_api_key_here", "your_openrouter_api_key_here", "your_api_key_here"}:
        raise InvalidLLMSettings("Introduce una clave API real del proveedor seleccionado.")
    return provider_id, model, mode, api_key


def _merge_managed_block(original, values):
    starts = [match.start() for match in re.finditer(re.escape(BEGIN_MARKER), original)]
    ends = [match.start() for match in re.finditer(re.escape(END_MARKER), original)]
    if len(starts) != len(ends) or len(starts) > 1 or (starts and starts[0] > ends[0]):
        raise InvalidLLMSettings("No se pudo actualizar la sección LLM del archivo local de configuración.")
    block = "\n".join([BEGIN_MARKER] + [f"{key}={json.dumps(value, ensure_ascii=False)}" for key, value in values.items()] + [END_MARKER])
    if starts:
        end_match = re.search(re.escape(END_MARKER), original[starts[0]:])
        end = starts[0] + end_match.end()
        merged = original[:starts[0]] + block + original[end:]
    else:
        separator = "" if not original or original.endswith(("\n", "\r")) else "\n"
        merged = original + separator + block + "\n"
    return merged


def _atomic_write_env(content):
    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".env.llm-", suffix=".tmp", dir=ENV_FILE.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if os.name != "nt":
            os.chmod(temporary_name, 0o600)
        os.replace(temporary_name, ENV_FILE)
    finally:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass


def save_llm_settings(payload):
    """Validate and atomically update .env when no analysis holds engine locks."""
    provider_id, model, mode, supplied_key = _validate_payload(payload)
    provider = PROVIDER_CATALOG[provider_id]
    lock_path = default_db_path()
    config_lock = lock_path.with_name("llm-config.lock")
    cycle_lock = lock_path.with_suffix(".cycle.lock")
    engine_lock = lock_path.with_suffix(".engine.lock")
    with exclusive_lock(config_lock):
        with exclusive_lock(cycle_lock):
            with exclusive_lock(engine_lock):
                local_values = _read_local_env()
                existing_key = resolve_provider_key(provider_id)
                selected_key = supplied_key or existing_key
                if not selected_key:
                    raise InvalidLLMSettings("Añade la clave API del proveedor seleccionado antes de guardar.")
                managed = {
                    "LLM_CONFIG_SOURCE": "dashboard",
                    "LLM_PROVIDER": provider_id,
                    "LLM_MODEL": model,
                    "LLM_PRICING_MODE": mode,
                }
                # Retain locally stored keys; save this provider's selected key.
                # Environment-only keys for other providers stay in their source.
                for item in PROVIDER_CATALOG.values():
                    key_name = item["key_env"]
                    if local_values.get(key_name):
                        managed[key_name] = local_values[key_name]
                managed[provider["key_env"]] = selected_key
                try:
                    if ENV_FILE.exists():
                        with ENV_FILE.open("r", encoding="utf-8", newline="") as handle:
                            original = handle.read()
                    else:
                        original = ""
                    updated = _merge_managed_block(original, managed)
                    _atomic_write_env(updated)
                except InvalidLLMSettings:
                    raise
                except OSError as error:
                    raise RuntimeError("No se pudo guardar la configuración local del proveedor.") from error
    return public_llm_settings()

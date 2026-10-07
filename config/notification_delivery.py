"""Bounded notification subprocess; invoked only by an explicit analysis job."""

import json
import math
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def bounded_seconds(name, default, maximum):
    try:
        value = float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return float(default)
    if not math.isfinite(value) or value <= 0:
        return float(default)
    return min(maximum, max(1.0, value))


def deliver_notification(destination, message):
    """Kill a stalled sender, including DNS/protocol waits; never retry here."""
    if destination not in {"telegram", "email"}:
        raise ValueError("Destino de notificación inválido")
    deadline = bounded_seconds("NOTIFICATION_DEADLINE_SECONDS", 30, 120)
    try:
        result = subprocess.run(
            [sys.executable, "-B", "-m", "config.notification_delivery"],
            cwd=ROOT,
            input=json.dumps({"destination": destination, "message": message}),
            text=True, encoding="utf-8", timeout=deadline,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
    except (OSError, subprocess.TimeoutExpired):
        # It may have been accepted before the timeout. The store marks unknown.
        return False
    return result.returncode == 0


def execute_payload(payload):
    """Internal child entry point, also testable with mocked transports."""
    if (not isinstance(payload, dict) or set(payload) != {"destination", "message"}
            or not isinstance(payload["destination"], str)
            or payload["destination"] not in {"telegram", "email"}
            or not isinstance(payload["message"], str) or len(payload["message"]) > 2048):
        return 1
    from config.notifications import enviar_email, enviar_telegram
    try:
        if payload["destination"] == "email":
            sent = enviar_email("[web-defense-ai V2] Alerta de seguridad", payload["message"])
        else:
            sent = enviar_telegram(payload["message"])
    except Exception:
        return 1
    return 0 if sent else 1


def main():
    try:
        # The only caller sends a short aggregate, never logs or credentials.
        payload = json.loads(sys.stdin.read(8193))
        return execute_payload(payload)
    except (ValueError, TypeError):
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

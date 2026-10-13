# config/settings.py
# ============================================================
# Configuración global del Sistema de Defensa Web
# ============================================================

import os
from dotenv import load_dotenv
from config.global_settings import resolve_global_numbers

load_dotenv()
_numbers = resolve_global_numbers(os.environ)

# --- Rutas ---
LOG_PATH        = os.getenv("LOG_PATH", "./logs/access.log")
REPORT_PATH     = os.getenv("REPORT_PATH", "./reports/")

# --- LLM ---
GROQ_API_KEY    = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "groq/openai/gpt-oss-120b")
LLM_TEMPERATURE = _numbers["LLM_TEMPERATURE"]

# --- Pipeline ---
INTERVALO_MINUTOS   = _numbers["INTERVALO_MINUTOS"]
MAX_LINEAS_LOG      = _numbers["MAX_LINEAS_LOG"]
UMBRAL_FUERZA_BRUTA = _numbers["UMBRAL_FUERZA_BRUTA"]

# --- Alertas ---
# Severidades que disparan alerta inmediata en consola
SEVERIDADES_CRITICAS = ["CRÍTICA", "ALTA"]

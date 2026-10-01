# main.py
# ============================================================
# web-defense-ai V2 — Sistema de defensa web con agentes de IA
# Segunda version de la aplicacion
# ============================================================

import os
import sys
import time
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import Field
from config.prompts import PROMPT_ANALISTA
from config.model_config import configured_model_candidates
from config.llm_resilience import call_with_model_fallback
from dashboard.services.read_store import atomic_write_text


# Cargar variables de entorno desde .env
load_dotenv()

# ============================================================
# CONFIGURACIÓN DEL MODELO DE LENGUAJE
# ============================================================
class RateLimitResilientLLM(LLM):
    """CrewAI LLM with bounded rate-limit retries and configured model fallback."""

    candidate_models: list[str] = Field(default_factory=list, exclude=True)
    rate_limit_retries: int = Field(default=2, exclude=True)
    rate_limit_backoff_seconds: float = Field(default=10.0, exclude=True)
    rate_limit_max_wait_seconds: float = Field(default=45.0, exclude=True)

    def call(self, messages, tools=None, callbacks=None, available_functions=None,
             from_task=None, from_agent=None, response_model=None):
        def invoke():
            return super(RateLimitResilientLLM, self).call(
                messages, tools=tools, callbacks=callbacks,
                available_functions=available_functions, from_task=from_task,
                from_agent=from_agent, response_model=response_model,
            )

        def select_model(model):
            if self.model != model:
                print(f"   Cambiando al modelo alternativo configurado: {model}")
                self.model = model

        return call_with_model_fallback(
            invoke, self.candidate_models or [self.model], select_model,
            retries=self.rate_limit_retries,
            backoff_seconds=self.rate_limit_backoff_seconds,
            max_wait_seconds=self.rate_limit_max_wait_seconds,
        )


def get_llm_con_retry():
    """
    Construye el LLM con reintentos de rate limit limitados por llamada.
    """
    modelos = configured_model_candidates()
    try:
        retries = int(os.getenv("LLM_RATE_LIMIT_RETRIES", "2"))
        backoff = float(os.getenv("LLM_RATE_LIMIT_BACKOFF_SECONDS", "10"))
        max_wait = float(os.getenv("LLM_RATE_LIMIT_MAX_WAIT_SECONDS", "45"))
    except ValueError as error:
        raise ValueError("La política de reintentos LLM debe usar valores numéricos.") from error
    for index, modelo in enumerate(modelos):
        try:
            return RateLimitResilientLLM(
                model=modelo,
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0.1,
                additional_params={"max_retries": 0},
                candidate_models=modelos[index:],
                rate_limit_retries=retries,
                rate_limit_backoff_seconds=backoff,
                rate_limit_max_wait_seconds=max_wait,
            )
        except Exception:
            print(f"   Modelo {modelo} no disponible al inicializar; probando el siguiente.")
            time.sleep(2)
            continue
    raise RuntimeError("Ningún modelo configurado pudo inicializarse.")


def get_llm():
    """
    Inicializa y retorna el modelo de lenguaje (LLM).
    Usa el modelo indicado por LLM_MODEL y los fallbacks configurados.
    """
    return get_llm_con_retry()

# ============================================================
# DEFINICIÓN DE AGENTES
# Cada agente tiene un rol, objetivo y backstory específico.
# Esto guía al LLM para comportarse como un experto en ese dominio.
# ============================================================
def crear_agentes(llm):
    from agents.threat_detector  import crear_agente_detective
    from agents.report_generator import crear_agente_reporter

    agente_analista  = Agent(
        role="Analista de Logs de Seguridad",
        goal=(
            "Analizar logs de acceso web e identificar patrones "
            "sospechosos que puedan indicar ataques como SQLi, XSS, "
            "Path Traversal o fuerza bruta."
        ),
        backstory=PROMPT_ANALISTA,
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )

    agente_detective = crear_agente_detective(llm)
    agente_reporter  = crear_agente_reporter(llm)

    return agente_analista, agente_detective, agente_reporter


# ============================================================
# DEFINICIÓN DE TAREAS
# Cada tarea asigna trabajo concreto a un agente específico.
# ============================================================
def crear_tareas(agente_analista, agente_detective,
                 agente_reporter, contenido_log):
    from agents.threat_detector  import crear_tarea_clasificacion
    from agents.report_generator import crear_tarea_reporte

    tarea_analisis = Task(
        description=(
            f"Analiza el siguiente fragmento de access.log de Apache "
            f"e identifica TODAS las líneas que contengan patrones de ataque.\n\n"
            f"LOG A ANALIZAR:\n{contenido_log}\n\n"
            f"Para cada línea sospechosa indica:\n"
            f"1. La línea exacta del log\n"
            f"2. El tipo de ataque detectado\n"
            f"3. El indicador específico que te llevó a esa conclusión"
        ),
        expected_output=(
            "Lista estructurada de todas las líneas sospechosas con "
            "tipo de ataque e indicador de compromiso de cada una."
        ),
        agent=agente_analista,
    )

    tarea_clasificacion = crear_tarea_clasificacion(
        agente_detective, tarea_analisis
    )

    tarea_reporte = crear_tarea_reporte(
        agente_reporter, tarea_analisis, tarea_clasificacion
    )

    return tarea_analisis, tarea_clasificacion, tarea_reporte

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def main():
    from dashboard.services.analysis_jobs import default_db_path
    from dashboard.services.runtime_lock import exclusive_lock
    with exclusive_lock(default_db_path().with_suffix(".engine.lock")):
        return _run_analysis()


def _run_analysis():
    sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 60)
    print("  🛡️  web-defense-ai V2 — T3r0S3c")
    print("=" * 60)

    # ----------------------------------------------------------
    # PASO 1: Leer el log REAL de Apache desde el volumen Docker
    # ----------------------------------------------------------
    from agents.log_analyst import preparar_log_para_agente

    ruta_log = os.getenv("LOG_PATH", "./logs/access.log")
    
    resultado_lectura = preparar_log_para_agente(ruta_log)
    
    if "error" in resultado_lectura:
        raise RuntimeError("No se pudo leer el log de entrada")
    
    stats = resultado_lectura["estadisticas"]
    contenido_log = resultado_lectura["contenido"]
    
    print(f"📊 Estadísticas del log:")
    print(f"   Total líneas analizadas : {stats['total_lineas']}")
    print(f"   Líneas sospechosas      : {stats['lineas_sospechosas']}")
    print(f"   Porcentaje sospechoso   : {stats['porcentaje_sospechoso']}%")
    print(f"   Fuerza bruta detectada  : {stats['fuerza_bruta_detectada']}")
    print()

    # ----------------------------------------------------------
    # PASO 2: Inicializar LLM y crear agentes
    # ----------------------------------------------------------
    llm = get_llm_con_retry()
    agente_analista, agente_detective, agente_reporter = crear_agentes(llm)

    # ----------------------------------------------------------
    # PASO 3: Crear tareas
    # ----------------------------------------------------------
    tarea_analisis, tarea_clasificacion, tarea_reporte = crear_tareas(
        agente_analista,
        agente_detective,
        agente_reporter,
        contenido_log
    )

    # ----------------------------------------------------------
    # PASO 4: Crear y ejecutar el Crew (equipo de agentes)
    # Process.sequential = los agentes trabajan en orden, uno tras otro
    # ----------------------------------------------------------
    crew = Crew(
        agents=[agente_analista, agente_detective, agente_reporter],
        tasks=[tarea_analisis, tarea_clasificacion, tarea_reporte],
        process=Process.sequential,  # Analista → Detective → Reporter
        verbose=True,
    )

    # ----------------------------------------------------------
    # PASO 5: Ejecutar el análisis
    # ----------------------------------------------------------
    print("🚀 Ejecutando análisis de seguridad...\n")
    resultado = crew.kickoff()

    # ----------------------------------------------------------
    # PASO 6: Guardar el reporte
    # ----------------------------------------------------------
    ruta_reporte = Path(os.getenv("REPORT_PATH", "./reports/")) / "reporte_seguridad.md"
    contenido_reporte = str(resultado).strip()
    if not contenido_reporte:
        raise RuntimeError("El análisis no produjo un reporte")
    atomic_write_text(ruta_reporte, contenido_reporte)

    print("\n" + "=" * 60)
    print(f"  ✅ Reporte guardado en: {ruta_reporte}")
    print("=" * 60)


# ============================================================
# PUNTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    main()

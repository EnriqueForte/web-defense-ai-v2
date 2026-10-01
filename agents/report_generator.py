# agents/report_generator.py
# ============================================================
# Agente 3: Generador de Reportes
# Responsabilidad: Crear reporte ejecutivo con recomendaciones
# ============================================================

from crewai import Agent, Task
from config.prompts import PROMPT_REPORTER


def crear_agente_reporter(llm) -> Agent:
    """
    Crea el agente Generador de Reportes.
    Recibe el análisis y clasificación de los Agentes 1 y 2
    y genera un reporte ejecutivo en Markdown.
    """
    return Agent(
        role="Generador de Reportes de Seguridad",
        goal=(
            "Generar un reporte ejecutivo claro con las amenazas detectadas "
            "y recomendaciones de mitigación específicas y accionables "
            "para cada tipo de ataque identificado."
        ),
        backstory=PROMPT_REPORTER,
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )


def crear_tarea_reporte(agente_reporter, tarea_analisis,
                        tarea_clasificacion) -> Task:
    """
    Crea la tarea de generación del reporte ejecutivo.
    Recibe el output de los Agentes 1 y 2 como contexto.
    """
    return Task(
        description=(
            "Con base en el análisis y clasificación anteriores, genera un "
            "reporte ejecutivo de seguridad en formato Markdown que incluya:\n"
            "1. RESUMEN EJECUTIVO (2-3 líneas)\n"
            "2. AMENAZAS DETECTADAS — tabla con columnas exactas:\n"
            "   Fecha/hora del evento | Línea | Severidad | Tipo de Ataque | Estado | IP Origen\n"
            "   Copia la fecha/hora de la línea de access.log correspondiente, incluyendo su zona horaria. "
            "Si no puedes vincular la amenaza con una línea concreta o la línea no tiene fecha válida, escribe '-'; nunca estimes ni inventes una fecha.\n"
            "3. RECOMENDACIONES DE MITIGACIÓN (específicas por tipo)\n"
            "4. ACCIONES INMEDIATAS (pasos concretos)\n\n"
            "IMPORTANTE: La tabla AMENAZAS DETECTADAS debe usar "
            "EXACTAMENTE esas 6 columnas en ese orden. "
            "No añadas columnas extra ni cambies los nombres."
        ),
        expected_output=(
            "Reporte completo en formato Markdown con las 4 secciones "
            "indicadas. La tabla de amenazas debe tener exactamente "
            "las columnas: Fecha/hora del evento | Línea | Severidad | Tipo de Ataque | Estado | IP Origen."
        ),
        agent=agente_reporter,
        context=[tarea_analisis, tarea_clasificacion],
    )

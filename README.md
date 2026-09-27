# 🛡️ web-defense-ai V2

Segunda versión de la aplicación de ciberseguridad defensiva de **T3r0S3c**. Analiza logs de Apache de un laboratorio DVWA mediante tres agentes CrewAI y presenta resultados en un dashboard.

**Desarrollo en Codex; seguimiento continuo de los archivos en VSCode.** Ambos utilizan la misma carpeta local. La denominación oficial de la aplicación es **web-defense-ai V2**; T3r0S3c se conserva como autor.

El repositorio de esta versión es [EnriqueForte/web-defense-ai-v2](https://github.com/EnriqueForte/web-defense-ai-v2), privado y configurado como `origin`. El [repositorio original](https://github.com/EnriqueForte/web-defense-ai) se conserva independiente y sin modificaciones. Véase [la separación de repositorios](docs/REPOSITORIOS.md).

## Estado de esta versión

La aplicación actual utiliza Python, Flask, Jinja2 y Chart.js. La migración a React + Next.js está planificada y todavía no se ha iniciado. El nombre V2 identifica esta segunda versión del proyecto, no una migración ya terminada.

La fase 0 dejó fixtures sintéticos, regresión aislada y respaldo restaurado. La fase 1 corrigió los fallos prioritarios de la interfaz Flask; Next.js y la API versionada siguen pendientes. Consultar el alcance en [el plan de migración](docs/PLAN_MIGRACION_INTERFAZ.md) y [la línea base](docs/FASE_0_LINEA_BASE.md).

| Documento | Contenido |
|---|---|
| [Guía de VSCode](docs/GUIA_VSCODE.md) | Apertura, seguimiento de cambios, tareas y depuración |
| [Plan de migración](docs/PLAN_MIGRACION_INTERFAZ.md) | Arquitectura, riesgos, fases, pruebas y reversión |
| [Plan de agentes y tareas](docs/PLAN_AGENTES_TAREAS.md) | Revisión de CrewAI, responsabilidades y backlog |
| [Contexto de desarrollo](AGENTS.md) | Instrucciones compartidas para trabajar desde Codex |
| [Repositorios y recuperación](docs/REPOSITORIOS.md) | Separación entre original y V2, remotos y copias locales |

## Abrir el proyecto en VSCode

Abrir **web-defense-ai V2.code-workspace** desde Archivo → Abrir área de trabajo desde archivo. Si el comando de VSCode está disponible, también puede abrirse desde la raíz:

```powershell
code "web-defense-ai V2.code-workspace"
```

El explorador y Control de código fuente permiten seguir los cambios guardados por Codex. No es necesario trasladar archivos. Evitar cambios sin guardar sobre un archivo que se esté modificando desde Codex.

Se recomiendan extensiones de Python, Pylance, depuración, Black y YAML. Seleccionar `.venv/Scripts/python.exe` con **Python: Select Interpreter**. Las recomendaciones no instalan extensiones automáticamente.

| Acción | Acceso en VSCode |
|---|---|
| Revisar sintaxis sin ejecutar el motor | Ctrl+Shift+B |
| Ver dashboard con recarga local | Terminal → Ejecutar tarea → web-defense-ai V2: dashboard con recarga local |
| Depurar el dashboard | Ejecutar y depurar → web-defense-ai V2: dashboard local → F5 |
| Leer documentación renderizada | Abrir Markdown y pulsar Ctrl+Shift+V |

Abrir [el dashboard local](http://127.0.0.1:5000) después de iniciar su tarea. Las modificaciones de archivos se reflejan en VSCode; la página web debe actualizarse al cambiar HTML o CSS. El proceso Flask se recarga ante cambios Python en la tarea de visualización. El perfil de depuración usa reinicio manual.

## Arquitectura actual

```text
DVWA / Apache → volumen Docker → sincronización → logs/access.log
                                                       ↓
                                           pipeline.py / main.py
                                                       ↓
                                    Analista → Detective → Reporter
                                                       ↓
                                      Markdown actual e históricos
                                                       ↓
                                              Dashboard Flask

El pipeline y determinadas acciones del dashboard pueden enviar
notificaciones mediante Telegram y SMTP.
```

| Área | Tecnología actual |
|---|---|
| Motor | Python 3.11 y CrewAI 1.14.2 declarado |
| Modelos | Proveedor Groq; modelos configurados en el código actual |
| Dashboard | Flask + Jinja2 + JavaScript |
| Gráficos | Chart.js |
| Laboratorio | Docker Compose, DVWA y MySQL para DVWA |
| Alertas | Telegram Bot API y correo SMTP |
| Interfaz prevista | React + Next.js + TypeScript |

El contenedor `ai-engine` declarado en Compose permanece inactivo con `tail -f /dev/null`; no arranca automáticamente el motor o el dashboard. La base MySQL pertenece al laboratorio DVWA.

## Entorno y ejecución

El entorno local revisado utiliza Python 3.11.9. `requirements.txt` incluye ahora Flask y limita pywin32 a Windows. Para las pruebas aisladas basta instalar `requirements-test.txt` y disponer de Node; ejecutar `python -B scripts/check_baseline.py`. No requiere `.env`, Docker ni claves. La [línea base](docs/FASE_0_LINEA_BASE.md) detalla la verificación de instalación y sus límites.

Para copiar la plantilla sin sobrescribir una configuración existente:

```powershell
if (-not (Test-Path -LiteralPath .env)) {
    Copy-Item -LiteralPath .env.example -Destination .env
}
```

Configurar localmente `GROQ_API_KEY`, rutas, intervalo y, si se usan, destinos de Telegram/SMTP. No versionar secretos. Algunos valores del motor aún están fijados en código; el plan recoge su consolidación.

Las tareas de VSCode no ejecutan automáticamente análisis al abrir la carpeta. Cuando se quiera usar el laboratorio real, estas operaciones se realizan de forma explícita:

```powershell
# Laboratorio Docker
docker compose up -d

# Copiar el log y ejecutar un análisis real con el proveedor IA
.\sync_logs.ps1
.\.venv\Scripts\python.exe main.py

# Alternativa: pipeline periódico real, que puede enviar notificaciones
.\.venv\Scripts\python.exe pipeline.py
```

No ejecutar análisis manual y pipeline simultáneamente sobre los mismos reportes mientras no exista coordinación de trabajos. Para visualizar cambios de interfaz basta con la tarea del dashboard; no hace falta iniciar otro motor.

## Funciones y límites conocidos

El dashboard presenta métricas del reporte, tabla de amenazas, coincidencias de patrones por hora, cinco reportes históricos recientes y ocho líneas del log. El motor contempla SQLi, XSS, traversal, fuerza bruta e inyección de comandos, con las limitaciones de evidencia y muestreo descritas en los planes.

La revisión detectó fallos previos que siguen pendientes: pantalla sin reporte, actualización del timeline, severidades, representación de contenido no confiable y consultas que sincronizan Docker. El botón actual de análisis reutiliza un reporte existente y puede notificar; no ejecuta un análisis nuevo. La configuración del IDE y el cambio de nombre no corrigen estos comportamientos.

## Estructura

```text
web-defense-ai V2/
├── .vscode/
│   ├── settings.json                 # Ajustes del proyecto
│   ├── extensions.json               # Extensiones recomendadas
│   ├── tasks.json                    # Sintaxis y visualización local
│   └── launch.json                   # Depuración y operaciones reales
├── docs/
│   ├── GUIA_VSCODE.md
│   ├── PLAN_MIGRACION_INTERFAZ.md
│   └── PLAN_AGENTES_TAREAS.md
├── agents/                           # Preprocesamiento, detective y reporter
├── config/                           # Configuración, prompts y alertas
├── dashboard/
│   ├── app.py                        # Flask
│   ├── templates/                    # Dashboard y reporte
│   └── static/                       # CSS y favicon
├── logs/                             # Datos operativos excluidos de Git
├── reports/                          # Reporte actual e históricos
├── screenshots/                      # Capturas de referencia anteriores
├── scripts/check_syntax.py           # Comprobación sin ejecutar módulos
├── tests/                            # Suite de regresión pendiente
├── AGENTS.md
├── web-defense-ai V2.code-workspace
├── main.py                           # Crew y agente analista
├── pipeline.py                       # Ejecución periódica
├── sync_logs.ps1
├── requirements.txt
└── docker-compose.yml
```

Se conservan los nombres de módulos, rutas de datos y contenedores para mantener su compatibilidad. No se ha renombrado el repositorio remoto ni creado una aplicación frontend que todavía no existe.

## Capturas de referencia

Estas imágenes corresponden al estado anterior del dashboard y pueden mostrar la denominación previa. No representan todavía el diseño previsto para V2; se actualizarán al validar la nueva interfaz.

![Dashboard anterior](screenshots/screenshot-1-dashboard.png)

- [Dashboard con inyección de comandos](screenshots/screenshot-1a-dashboard.png)
- [Arquitectura del laboratorio](screenshots/screenshot-2-architecture.png)
- [Timeline](screenshots/screenshot-5-timeline.png) y [timeline con varias categorías](screenshots/screenshot-5a-timeline.png)
- [Reporte](screenshots/screenshot-3-report.png) y [otro reporte](screenshots/screenshot-3a-report.png)
- [Notificación Telegram](screenshots/screenshot-4-telegram.png) y [detalle de otra notificación](screenshots/screenshot-4a-telegram.png)

## Autor y ámbito de uso

**T3r0S3c** — Proyecto de portfolio en ciberseguridad.

[Repositorio de origen](https://github.com/EnriqueForte/web-defense-ai) · [GitHub del autor](https://github.com/EnriqueForte) · [LinkedIn](https://linkedin.com/in/enriqueforte)

Proyecto para laboratorio y aprendizaje. DVWA es intencionadamente vulnerable: mantener el laboratorio aislado y trabajar únicamente sobre sistemas autorizados.

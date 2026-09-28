# 🛡️ web-defense-ai V2

Segunda versión de la aplicación de ciberseguridad defensiva de **T3r0S3c**. Analiza logs de Apache de un laboratorio DVWA mediante tres agentes CrewAI y presenta resultados en un dashboard.

**Desarrollo en Codex; seguimiento continuo de los archivos en VSCode.** Ambos utilizan la misma carpeta local. La denominación oficial de la aplicación es **web-defense-ai V2**; T3r0S3c se conserva como autor.

El repositorio de esta versión es [EnriqueForte/web-defense-ai-v2](https://github.com/EnriqueForte/web-defense-ai-v2), privado y configurado como `origin`. El [repositorio original](https://github.com/EnriqueForte/web-defense-ai) se conserva independiente y sin modificaciones. Véase [la separación de repositorios](docs/REPOSITORIOS.md).

## Estado de esta versión

El motor continúa en Python/CrewAI y Flask conserva su dashboard anterior. La nueva interfaz en `frontend/` usa Next.js 16, React 19 y TypeScript; ya consulta `/api/v1` en modo lectura para mostrar el resumen, las amenazas, la actividad y los reportes. El análisis manual coordinado aún no está implementado.

Las fases 0–4 completaron la línea base, estabilización de Flask, API versionada, base visual y lectura conectada. Consultar [el plan de migración](docs/PLAN_MIGRACION_INTERFAZ.md), [el contrato de fase 2](docs/FASE_2_API_LECTURA.md) y [la entrega de fase 4](docs/FASE_4_LECTURA_CONECTADA.md).

| Documento | Contenido |
|---|---|
| [Guía de VSCode](docs/GUIA_VSCODE.md) | Apertura, seguimiento de cambios, tareas y depuración |
| [Plan de migración](docs/PLAN_MIGRACION_INTERFAZ.md) | Arquitectura, riesgos, fases, pruebas y reversión |
| [Fase 3 — Base visual](docs/FASE_3_BASE_VISUAL.md) | Pantalla Next.js, datos sintéticos, validación y reversión |
| [Fase 4 — Lectura conectada](docs/FASE_4_LECTURA_CONECTADA.md) | Integración con Flask, filtros, reportes, validación y reversión |
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
| Ver consola Next.js conectada | Terminal → Ejecutar tarea → web-defense-ai V2: lectura conectada (Flask + Next.js) |
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
| Nueva interfaz de lectura | React + Next.js + TypeScript; consume `/api/v1` de Flask |

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

No ejecutar análisis manual y pipeline simultáneamente sobre los mismos reportes mientras no exista coordinación de trabajos. Para visualizar Next.js con lectura de Flask, usar la tarea conjunta de ambos servidores; no hace falta iniciar CrewAI.

## Funciones y límites conocidos

El dashboard presenta métricas del reporte, tabla de amenazas, coincidencias de patrones por hora, cinco reportes históricos recientes y ocho líneas del log. El motor contempla SQLi, XSS, traversal, fuerza bruta e inyección de comandos, con las limitaciones de evidencia y muestreo descritas en los planes.

La fase 1 corrigió la pantalla sin reporte, la recursión del timeline, el recuento de severidades y la representación insegura de logs y reportes. La fase 2 separó las consultas de estado de la sincronización con Docker y añadió `/api/v1` solo de lectura. La fase 4 conectó Next.js a esa API. El botón anterior sincroniza el log y comunica que no inicia un análisis nuevo; la coordinación del análisis manual y periódico corresponde a la fase 5.

## Estructura

```text
web-defense-ai V2/
├── .vscode/
│   ├── settings.json                 # Ajustes del proyecto
│   ├── extensions.json               # Extensiones recomendadas
│   ├── tasks.json                    # Sintaxis y visualización local
│   ├── run-frontend.ps1              # Tareas Next.js sin pnpm en PATH
│   └── launch.json                   # Depuración y operaciones reales
├── docs/
│   ├── GUIA_VSCODE.md
│   ├── PLAN_MIGRACION_INTERFAZ.md
│   ├── PLAN_AGENTES_TAREAS.md
│   ├── FASE_0_LINEA_BASE.md
│   ├── FASE_2_API_LECTURA.md
│   ├── FASE_3_BASE_VISUAL.md
│   └── FASE_4_LECTURA_CONECTADA.md
├── frontend/                         # Next.js: lectura conectada a Flask
├── agents/                           # Preprocesamiento, detective y reporter
├── config/                           # Configuración, prompts y alertas
├── dashboard/
│   ├── app.py                        # Flask
│   ├── templates/                    # Dashboard y reporte
│   └── static/                       # CSS y favicon
├── logs/                             # Datos operativos excluidos de Git
├── reports/                          # Reporte actual e históricos
├── screenshots/                      # Capturas de referencia anteriores
├── scripts/                          # Sintaxis y regresión aislada
├── tests/                            # 39 casos Python y 3 comprobaciones JS
├── AGENTS.md
├── web-defense-ai V2.code-workspace
├── main.py                           # Crew y agente analista
├── pipeline.py                       # Ejecución periódica
├── sync_logs.ps1
├── requirements.txt
└── docker-compose.yml
```

Se conservan los nombres de módulos, rutas de datos y contenedores para mantener su compatibilidad. La interfaz Next.js vive en `frontend/` y consulta Flask mediante `/api/v1`; no accede a Docker, secretos ni archivos brutos.

## Capturas de referencia

Estas imágenes corresponden al dashboard Flask anterior y pueden mostrar la denominación previa. La nueva base visual V2 está en `frontend/`; las capturas se actualizarán cuando la interfaz conectada quede validada.

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

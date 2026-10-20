# 🛡️ web-defense-ai V2

Aplicación local de ciberseguridad defensiva de **T3r0S3c**. Analiza registros
de Apache mediante tres agentes CrewAI y muestra indicadores, evidencias e
informes en una consola SOC con Next.js y Flask.

El código se distribuye en [EnriqueForte/web-defense-ai-v2](https://github.com/EnriqueForte/web-defense-ai-v2)
con licencia [MIT](LICENSE). Cada instalación conserva sus datos y configura
su proveedor. El [repositorio original](https://github.com/EnriqueForte/web-defense-ai)
permanece independiente; véase [la separación de repositorios](docs/REPOSITORIOS.md).

## Estado de esta versión

Revisión documental: **20/10/2026**. El [resumen vigente](docs/ESTADO_FINAL_2026_10_12.md)
es la referencia de estado; el [análisis de cierre](docs/ANALISIS_CIERRE_2026_10_20.md)
explica el trabajo restante.

| Área | Estado comprobado |
| --- | --- |
| Aplicación local | Interfaz SOC, API `/api/v1`, configuración, trabajos, instalación y arranque/cierre implementados. Flask se conserva como interfaz alternativa. |
| Windows y Ubuntu | Código `0d73ec2`, [CI 39466610699](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/39466610699) aprobada: Ubuntu 376 Python; Windows 375 y una prueba exclusiva Linux omitida; nueve E2E por OS. Instalación limpia, build, API/proxy y cierre comprobados; artefactos completos revisados. |
| Parche de seguridad | aiohttp 3.14.4 y yarl 1.25.1 instalados y probados en ambos OS, incluidos dos casos de cookies Secure. Inventarios 172/0/0; solo cambian esos dos paquetes frente al contrato anterior. |
| Evaluación A-05 | Aceptada por el usuario el 20/10 para la primera versión local de apoyo a la revisión, con límites explícitos y comparación legacy diferida. [Matriz y evidencias](docs/MATRIZ_ACEPTACION_A05_2026_10_20.md). |
| Parrot 7.3/VMware | Instalación/lectura e inventario 172/0/0 comprobados; recorrido DVWA XSS/fuerza bruta aceptado el 15/10 para esa muestra. La actualización de la VM a los pins posteriores y su recuperación Docker no están acreditadas. |
| Seguridad y entrega | [Tratamiento residual C3](docs/TRATAMIENTO_RIESGOS_C3_2026_10_20.md) aceptado para uso local aislado, conservando vulnerabilidades y límites. [Entrega C4](docs/ENTREGA_LOCAL_C4_2026_10_20.md) identificada como [v0.1.0](https://github.com/EnriqueForte/web-defense-ai-v2/releases/tag/v0.1.0); sin certificación global de seguridad. |

Las fases de migración 0–7 y las del rediseño SOC están cerradas en su alcance
local aceptado. Los [estados anteriores del README](docs/HISTORIAL_README_2026_10_20.md)
se conservan como historia; sus pendientes no describen la instalación actual.

## Entorno y ejecución

Requiere Git, Python **3.11** con venv, Node.js **24 o posterior** y
pnpm **11.19.0** disponibles. Desde el directorio donde quieras clonar:

```bash
git clone https://github.com/EnriqueForte/web-defense-ai-v2.git
cd web-defense-ai-v2
python3 webdefense.py install
python3 webdefense.py start
```

En Windows usa `py webdefense.py install` y `py webdefense.py start`.
Abre [la consola local](http://127.0.0.1:3000) cuando aparezca «Consola lista».
Mantén la terminal abierta; **Ctrl+C detiene Flask y Next** creados por el
lanzador. En VMware abre la dirección desde el navegador de la VM.

La instalación prepara `.p2`, comprueba el contrato de paquetes y compila el
frontend. Crea `.env` si falta y conserva uno existente. El arranque habitual
inicia lectura, con análisis manual deshabilitado y notificaciones vacías;
no inicia el worker ni Docker. El modo de informes predeterminado es legacy.
Para leer publicaciones structured existentes:

```bash
python3 webdefense.py start --mode structured
```

Este cambio de modo no solicita un análisis. Una clonación nueva puede mostrar
«Fuentes incompletas» porque no incluye los logs o informes del mantenedor.
Actualizar relee la copia local; no genera tráfico ni inicia un análisis.

| Necesidad | Guía |
| --- | --- |
| Primera instalación y comprobación de arranque | [Inicio rápido](docs/INICIO_RAPIDO.md) |
| Configuración, captura y análisis manual por terminales | [Instalación y operación](docs/INSTALACION_AUTOALOJADA.md) |
| Proveedor, modelo y credenciales propios | [Configuración LLM](docs/CONFIGURACION_PROVEEDOR_LLM.md) |
| Laboratorio Docker aislado | [DVWA y Mailpit](docs/LABORATORIO_DVWA_FASE_6.md) |
| Copias, actualización y restauración de aplicación | [Operación y recuperación](docs/OPERACION_RECUPERACION_2026_10_14.md) |
| Desarrollo, responsabilidades y pendientes | [Plan vigente](docs/PLAN_AGENTES_TAREAS.md) |
| Entrega local v0.1.0 | [Estado C4](docs/ENTREGA_LOCAL_C4_2026_10_20.md) · [Notas de versión](docs/NOTAS_VERSION_LOCAL_2026_10_20.md) |

## Arquitectura actual

```text
DVWA/Apache → captura Docker → copia local del access.log
                                      ↓
                           ejecutor Python (opcional)
                                      ↓
                   Analista → Detective → Reporter
                                      ↓
                validación y publicación de informes
                                      ↓
                       API Flask /api/v1 → Next.js
                                      └→ interfaz Flask alternativa
```

En modo **structured**, Python prepara evidencia, valida referencias y
clasificación, calcula tabla/conteos y publica JSON/Markdown mediante generaciones
y un puntero coherente. El modo **legacy** conserva el flujo y los informes
anteriores. Ambos se seleccionan explícitamente; no se mezclan sus fuentes.

| Área | Implementación del código revisado |
| --- | --- |
| Motor | Python 3.11, CrewAI 1.15.27 y contrato de 172 paquetes por plataforma |
| Proveedores | Groq predeterminado; OpenRouter opcional; credenciales locales |
| Interfaz | Next.js 16, React 19 y TypeScript; Flask conserva API e interfaz alternativa |
| Laboratorio recomendado | `compose.lab.yaml`: DVWA, MariaDB y Mailpit fijados por digest; puertos publicados solo en loopback |
| Análisis/avisos | Worker separado; manual y notificaciones desactivados en el arranque de lectura; Telegram/SMTP opcionales |

`docker-compose.yml` es legacy, con exposición diferente, y no es la instalación
recomendada. Antes de recrear un laboratorio existente con los pins nuevos,
seguir el respaldo y recuperación de su base descritos en la guía del laboratorio.
El respaldo de aplicación no incluye el volumen DVWA ni el buzón Mailpit.

## Funciones y límites conocidos

La consola muestra grupos del informe actual, severidades, referencias, actividad
reciente y reportes. Las coincidencias de patrones del log son distintas de los
hallazgos clasificados; ocho POST pueden formar una sola ráfaga. El log de la
API muestra una ventana de ocho líneas, no el historial completo.

Se contemplan SQLi, XSS, traversal, fuerza bruta e inyección de comandos con
límites de evidencia y selección. Un HTTP 200 o una petición a un avatar no
demuestran un inicio de sesión exitoso. Las guardas verifican forma y referencias;
la aceptación local no garantiza detección general. El resultado conserva
`quality=semantic_evaluation_pending` porque no se certifica la calidad general
del proveedor; la aceptación del alcance se registra en la matriz enlazada.

La pantalla Configuración guarda la clave en `.env` local, en texto sin cifrar
y excluido de Git. El dashboard debe permanecer en localhost. Un análisis puede
enviar datos del log al proveedor elegido; cada instalación asume sus límites
y costes. Guardar configuración no valida la clave ni inicia análisis.

Los avisos de [dependencias, secretos y su tratamiento](docs/TRATAMIENTO_RIESGOS_C3_2026_10_20.md)
y de [imágenes](docs/FIJACION_IMAGENES_LAB_2026_10_19.md) siguen documentados.
Los pins fijan contenido; no eliminan vulnerabilidades. No se declara soporte
general de todas las distribuciones, macOS/ARM, uso público multiusuario o
remediación automática.

## Abrir el proyecto en VSCode

Abre `web-defense-ai V2.code-workspace`. Codex y VSCode utilizan la misma carpeta;
Control de código fuente permite revisar los cambios y Ctrl+Shift+V muestra
Markdown. Véase [la guía de VSCode](docs/GUIA_VSCODE.md).

El instalador actual utiliza `.p2`. Las tareas Python heredadas del IDE invocan
`.venv/Scripts/python.exe` mediante PowerShell: seleccionar otro intérprete en
el editor no cambia esos comandos. Para una clonación nueva usa las órdenes
del inicio rápido; no necesitas crear otro entorno para arrancar la aplicación.

## Estructura

```text
web-defense-ai V2/
├── frontend/             # Consola Next.js
├── agents/               # Agentes, evidencia, contratos y evaluación
├── config/               # Configuración y adaptadores
├── dashboard/            # Flask, API, trabajos y publicación
├── scripts/              # Instalación, verificaciones y operación local
├── tests/                # Pruebas aisladas
├── docs/                 # Guías vigentes y actas fechadas
├── .vscode/              # Herramientas de desarrollo
├── webdefense.py          # Instalador y lanzador de lectura
├── main.py               # Motor
├── pipeline.py           # Ejecutor separado
├── requirements.txt
├── constraints-py311.txt
├── compose.lab.yaml      # Laboratorio recomendado
└── docker-compose.yml    # Laboratorio legacy
```

Los datos locales y entornos se crean por instalación y no se distribuyen.
El perfil `pilot` utiliza `.local-state/dvwa-lab/access.log` y
`.local-state/phase6-pilot/`; el nombre se conserva por compatibilidad.

## Capturas de referencia

Estas imágenes corresponden al dashboard Flask anterior y pueden mostrar la
denominación previa. Son referencias históricas; no acreditan el aspecto de la
consola Next.js actual.

![Dashboard anterior](screenshots/screenshot-1-dashboard.png)

- [Reporte anterior](screenshots/screenshot-3-report.png)
- [Timeline anterior](screenshots/screenshot-5-timeline.png)
- [Arquitectura anterior](screenshots/screenshot-2-architecture.png)

## Autor y ámbito de uso

**T3r0S3c** — Proyecto de portfolio en ciberseguridad.

[GitHub del autor](https://github.com/EnriqueForte) · [LinkedIn](https://linkedin.com/in/enriqueforte)

Proyecto para laboratorio y aprendizaje. DVWA es intencionalmente vulnerable:
mantén el laboratorio aislado y trabaja únicamente sobre sistemas autorizados.

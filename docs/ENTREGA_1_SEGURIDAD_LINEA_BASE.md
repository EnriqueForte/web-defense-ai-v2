# Entrega 1 — Seguridad y línea base

Estado: completada el 06/10/2026 como primera entrega de
[la revisión integral](REVISION_INTEGRAL_2026_10_06.md). Responsable: Codex
principal, sin delegación. No inicia otras fases del plan.

## Cambios y aceptación

| Hallazgo | Cambio | Evidencia |
|---|---|---|
| R-01 | Errores de reportes con mensaje constante y `text/plain` | Nombre con HTML hostil no se refleja; rutas válidas y contenido escapado conservados |
| R-02 | Allowlist común de Origin para mutaciones locales; sincronización exige Origin | Origen ausente, vacío, null o ajeno rechazado antes de I/O; cuatro orígenes locales aceptados; bloqueos de coordinación conservados |
| R-09 | Telegram registra código HTTP o fallo genérico de transporte | Token, chat, mensaje y cuerpo de respuesta sintéticos no aparecen en diagnósticos; transporte exitoso conserva contrato |
| Regresión OpenAPI | Prueba incluye `/configuracion/llm` | Especificación y referencias internas pasan sin modificar el contrato publicado |
| R-15, parte backend | Regresión de rutas, archivo administrado, precedencia y factory LLM | Archivos y claves ficticios; casos de validación, bloqueos y fallo atómico |
| R-17 | Tarea local ejecuta ESLint sobre todo el frontend | Verificación por el mismo script usado en VSCode aprobada |
| R-22, resumen operativo | README, AGENTS y seguimiento del backlog reflejan UI 8 y zoom confirmados | Estado alineado con acta SOC; evidencia histórica conservada |
| Aislamiento de pruebas | Runner bloquea ambas lecturas dotenv y sustituye selección/credenciales heredadas; fixture visual bloquea resolver runtime | La suite no carga el `.env` real; las pruebas LLM usan su propio archivo temporal |

## Política de origen y compatibilidad

Los orígenes permitidos son `http://127.0.0.1:3000`,
`http://127.0.0.1:5000`, `http://localhost:3000` y
`http://localhost:5000`. La comprobación por conexión loopback sigue vigente
y es independiente de Origin. No se habilita CORS ni se permite un destino
arbitrario para el proxy o los proveedores.

`PUT /api/v1/configuracion/llm` y `POST /api/sincronizar` requieren uno de esos
orígenes. La sincronización responde `403` si falta o no se permite Origin;
una herramienta local que invoque esa ruta debe incluir explícitamente
`Origin: http://127.0.0.1:5000`. El botón Flask utiliza fetch POST del mismo
origen. Sus respuestas JSON conservan `ok/error`, y los bloqueos, copia
atómica y ausencia de ejecución IA permanecen intactos.

`POST /api/v1/analisis` acepta esos mismos orígenes y conserva clientes locales
sin Origin que aporten `Idempotency-Key`, además de los conmutadores y guardas
existentes. Un Origin explícito vacío, null o ajeno se rechaza. La excepción
CLI no se extiende a sincronización ni guardado de configuración.

Los errores de la ruta HTML de reportes mantienen HTTP 400/404, con mensaje
constante y tipo de contenido texto plano. No se cambia `/api/v1`, el parsing
del Markdown ni el contenido de reportes válidos.

## Pruebas LLM añadidas

`tests/test_llm_settings.py` utiliza un `.env` temporal, claves ficticias,
entorno controlado y conexiones de red prohibidas. Cubre valores iniciales,
ausencia de secretos en GET/PUT/estado del análisis, proveedor/modelo/mode
inválidos, prefijo y formato, claves vacías/inválidas, orígenes, cliente remoto,
JSON malformado y tipo de contenido, guardado y sustitución de bloque,
conservación de líneas ajenas y claves de otros proveedores, precedencia frente
al entorno heredado del worker, bloqueo engine/cycle/config y fallo de replace
sin pérdida del archivo ni temporales sobrantes.

La prueba del factory extrae solo `get_llm_con_retry` mediante AST y emplea un
constructor doble para comprobar que OpenRouter recibe `is_litellm=True`,
base URL fija y opciones de reintento, mientras Groq mantiene su configuración.
No importa `main.py`, no construye el cliente real CrewAI y no llama a proveedores.
La instalación limpia y la dependencia LiteLLM explícita pertenecen a entrega 2.

## Validación

- `.venv/Scripts/python.exe -B scripts/check_syntax.py`: 32 archivos, 0 errores.
- `.venv/Scripts/python.exe -B scripts/check_baseline.py`: 111 pruebas Python
  aprobadas, 0 expected failures, y 3 diagnósticos JavaScript aprobados.
- `.vscode/run-frontend.ps1 -Action lint`: aprobado, alcance completo.
- `node scripts/test_ui_regression.mjs` desde frontend: 6 grupos aprobados.
- `git diff --check`: sin errores de espacios; Git avisa de normalización
  LF/CRLF de archivos Windows, sin cambio de comportamiento.

La revisión inicial tenía 88 pruebas Python con un fallo. Esta entrega corrige
ese fallo y añade 23 casos, incluidos subcasos de payloads y orígenes.

No se ejecutaron motor, pipeline real, Docker, Telegram o SMTP reales ni se
contactaron proveedores. No se escribió el `.env` operativo, logs, reportes o
SQLite del usuario. No cambian prompts, muestreo, modelos, dependencias,
conmutadores ni componentes React. No se repitieron build/tipos/audit porque
esta entrega no modifica fuentes TypeScript o dependencias; su verificación
anterior queda registrada en la revisión, sin presentarla como nueva.

## Límites y próximos trabajos

No se verificó aquí la interacción en navegador ni una integración LLM real.
La regresión de efectos del componente `LLMSettings` y polling sigue pendiente;
R-15 queda cubierto en backend/factory, no cerrado íntegramente. La fixture
visual se ajustó para no leer configuración real al utilizar las nuevas rutas;
no se volvió a iniciar un servidor visual en esta entrega.

Los avisos de dependencias, declaración LiteLLM, discrepancias de instalación
y timeout SMTP siguen abiertos para entrega 2. La validación estructural del
resultado, selección, prompts, trazabilidad y publicación corresponden a
A-01–A-05 y no quedan resueltos por recuperar la suite. Fase 7 sigue abierta
hasta disponer de evidencia de uso y decisión de cierre.

## Reversión

Revertir únicamente los cambios de esta entrega en rutas, diagnósticos,
verificación, fixture, pruebas y documentación, preservando cambios posteriores.
No requiere modificar `.env`, datos, históricos, SQLite ni volúmenes Docker.
Revertir las guardas reintroduciría los hallazgos R-01/R-02/R-09; no se recomienda
como solución operativa. El retorno a Flask mediante `NEXT_PRIMARY_ENABLED=0`
sigue disponible y es independiente de estos cambios. No se realizó publicación.

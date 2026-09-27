# Fase 2 — API de lectura y capturas

Estado: **completada el 27/09/2026**. Esta entrega añade la primera
superficie versionada de lectura en Flask y los servicios locales de captura y
publicación. No inicia Next.js, no cambia prompts y no lanza análisis.

## Rutas

La especificación navegable en máquina está en
[`dashboard/openapi-v1.json`](../dashboard/openapi-v1.json) y se sirve en
`GET /api/v1/openapi.json`.

| Ruta | Respuesta |
|---|---|
| `GET /api/v1/estado` | Métricas globales, diez amenazas recientes como máximo, terminal limitado, cinco IP observadas, timeline etiquetado como coincidencias de patrones y cinco reportes recientes |
| `GET /api/v1/amenazas` | Amenazas del reporte actual con filtros `tipo`, `severidad`, `ip` y paginación (`page`, `per_page`, máximo 100) |
| `GET /api/v1/reportes` | Reporte actual e históricos completos como lista paginada de metadatos |
| `GET /api/v1/reportes/{report_id}` | Markdown de un reporte identificado por ID opaco; no recibe ni resuelve rutas del sistema |
| `GET /api/v1/salud` | Metadatos ligeros de existencia, última modificación y tamaño; no lee el log, no conecta con Docker ni afirma salud del ejecutor |

Los errores tienen `error.code`, `error.message` seguro y `error.request_id`; la
misma petición devuelve el ID en `X-Request-ID`. Las respuestas de API llevan
`Cache-Control: no-store`. Los filtros desconocidos y los límites inválidos
responden 400. Si una lista de reportes queda obsoleta antes de abrir su detalle,
la ruta devuelve 409 para recargar la lista.

La amenaza tiene ID estable dentro del reporte, referencia al reporte e IP opcional.
`event_time` siempre es `null` con el formato Markdown actual, porque no contiene
una fecha individual verificable. Las IP mostradas son orígenes observados; no se
les atribuye que sean atacantes. Las estadísticas cuentan severidades reconocidas
y separan BAJA y DESCONOCIDA.

## Captura y escritura

`GET /api/estado` conserva los siete campos superiores anteriores. Tanto esa ruta
como `/` y la ruta nueva de estado leen una vez el reporte actual, una vez el log
y una vez cada uno de los cinco históricos incluidos. El ID de captura cambia si
cambia el contenido de las fuentes. Se comparan tamaño, modificación, creación e
identidad del archivo antes y después de leer; si el archivo sigue cambiando, la
fuente se declara `changing` y no se usa como contenido válido.

La captura une los archivos disponibles, pero el formato histórico no lleva un
`run_id` compartido. Por eso, aunque `snapshot_id` identifica exactamente los
bytes leídos, no demuestra que log y reporte se generaron en el mismo análisis.
`meta.sources` expone su disponibilidad y hora de modificación. Las fechas del
reporte se refieren al archivo, no a un evento de seguridad.

`main.py` publica el reporte actual con archivo temporal y reemplazo; el agente
reporter ya no escribe por su cuenta. El pipeline publica históricos del mismo
modo. La sincronización desde el dashboard, el pipeline y `sync_logs.ps1` copia
primero a un temporal junto al destino y reemplaza el log solo si Docker termina
bien. Ante un fallo se conserva el último log válido.

No hay base de incidentes, registro de trabajos, bloqueo compartido de análisis,
autenticación ni prueba de despliegue multiusuario en esta fase. La consola sigue
siendo local: no publicar el servidor Flask actual directamente en una red. Las
rutas anteriores siguen disponibles y `/api/sincronizar` conserva su propósito
de copiar logs sin afirmar que ejecuta IA.

## Verificación y reversión

Resultado: **39 casos Python y 3 comprobaciones JavaScript aprobados**; sintaxis
Python, análisis sintáctico de PowerShell y JSON OpenAPI válidos. `git diff --check`
no reporta errores. La suite crea archivos temporales y sustituye procesos externos. No usa Docker,
CrewAI, API del modelo ni notificaciones. Incluye contrato legado, IDs de captura,
filtros, paginación, resolución segura de reportes, errores, cabeceras, lectura
única por fuente y reemplazo atómico correcto/fallido. El reemplazo de Docker se
verifica con un doble; no equivale a una integración con un contenedor activo.

La reversión de código es volver al commit anterior de fase 2 y conservar logs,
reportes, secretos e históricos locales. Desactivar `/api/v1` no requiere migrar
ni transformar los archivos Markdown.

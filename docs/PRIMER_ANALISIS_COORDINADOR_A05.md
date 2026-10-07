# A-05 — Primer análisis autorizado del coordinador

Fecha: 07/10/2026. Resultado: **succeeded**, publicación y lectura verificadas.
A-05 permanece abierta por observación operativa y aceptación final de calidad.

## Operación y evidencia

El usuario autorizó expresamente un primer análisis tras aceptar el arranque
piloto estructurado. Se mantuvo `.p2`, profile=pilot, ANALYSIS_ENGINE_MODE=structured,
worker --manual-only, ANALYSIS_MANUAL_ENABLED=0 y NOTIFICATION_DESTINATIONS vacío.
No se modificó `.env` ni se habilitó el botón de análisis del dashboard.

Docker Desktop estaba detenido. Se inició y se verificaron los contenedores
existentes DVWA, MariaDB y Mailpit, conservando sus datos. El aislamiento de
Codex bloqueaba el acceso al pipe de Docker. Se reinició exclusivamente el
ejecutor propio y sin trabajos activos con permisos aprobados; el lanzador
vigente es PID 37076. El primer intento de reinicio fue rechazado correctamente
por el bloqueo del ejecutor anterior; no creó un segundo worker efectivo.
Los PID son históricos de esta sesión: comprobar identidad antes de detenerlos.
Flask no se reinició.

Antes del envío se comprobó mediante el resolvedor privado que el proveedor era
OpenRouter, el modelo openrouter/openrouter/free, pricing_mode=free y la lista
de candidatos contenía únicamente ese router gratuito. No se imprimieron claves.
Se capturaron 112 líneas del laboratorio (29384 bytes) y se envió un único job
manual directamente al JobStore con clave de idempotencia
`a05-first-coordinator-20261007`; la API de creación manual siguió desactivada.
El worker ejecutó la ingesta real, el motor estructurado, publicación,
archivo histórico y finalización; no se sustituyeron por dobles de prueba.

| Dato | Resultado |
| --- | --- |
| Job | 8c8efc240655459cb72d590e47233173 |
| Inicio UTC | 2026-10-07T13:09:52Z |
| Ingesta UTC | 2026-10-07T13:09:53Z |
| Finalización UTC | 2026-10-07T13:12:29Z |
| Duración del job | 157 s; incluye coordinación, no solo llamadas LLM |
| Estado/error | succeeded / null |
| Entregas de notificación | ninguna, deliveries={} |
| Generación | 8c8efc240655459cb72d590e47233173-80537e9a8a64441da5eec20ca1b4db94 |
| Report ID API | 9a1cb9c93f87edc645daf7f6e39734594753a8d228aca86dc635a5d43947a9e7 |
| Versiones | structured-prototype-5 / observed-access-2 / structured-report-2 |

Los recibos locales están en
`.local-state/a05-activation/first-analysis-20261007/`: submission.json,
worker-restart.json y result.json. Las generaciones y el histórico permanecen
en `.local-state/phase6-pilot/reports`. El respaldo previo verificado de 17
archivos sigue en `.local-backups/operational-20261007T130119779538Z`.

## Verificación del resultado

Se cargó la generación con load_current y se comprobaron SHA-256, manifiestos,
ID de análisis, referencias y observaciones. La evidencia serializada coincide
con la preparación reconstruida a partir del log capturado; las guardas de
clasificación observada y de narrativa volvieron a pasar offline. Se verificó
que los conteos coinciden con los hallazgos y que el informe de la API coincide
con report.md y con la copia histórica de este job. El Markdown legacy conserva
su hash del respaldo previo. La comprobación inicial del bundle comparaba
tuplas con listas JSON; se corrigió el comprobador local mediante normalización
JSON, sin modificar resultados ni guardas del motor.

Se seleccionaron 30 de 112 líneas y se omitieron 82. Hay cinco grupos: uno de
SQLi, tres de ráfagas compatibles con fuerza bruta y uno de XSS; cuatro altos
y uno medio, cero críticos. Son indicadores del access.log del laboratorio,
no cinco ataques confirmados ni prueba de explotación exitosa. La revisión
del resumen y recomendaciones no encontró afirmaciones de éxito de explotación;
las recomendaciones de autenticación son medidas propuestas, no evidencia
de fallos de contraseña o de acceso conseguido.

Después de publicar, `/api/v1/salud` indica status=ok, report/log disponibles
y executor=online. `ingestion=unobserved` sigue siendo el valor de ese contrato
de salud: el job sí registra last_ingested_at, pero el endpoint no certifica
observación continua. El análisis manual continúa desactivado. La operación
no midió Next.js, navegación del usuario ni disponibilidad tras reiniciar Windows.

## Límites y continuación

Un job puede incluir múltiples llamadas y reintentos internos. El motor operativo
no capturó en esta ejecución el número de llamadas, modelo informado por cada
respuesta ni uso reconciliado de tokens: son datos no disponibles, no cero.
No reutilizar las métricas del evaluador aislado para este job. El router gratuito
puede seleccionar modelos diferentes; esta ejecución no demuestra p95 ni mejora
causal. El resultado conserva quality=semantic_evaluation_pending y
narrative_source=llm_contract_validated_semantics_pending; esta revisión puntual
no altera retroactivamente esos metadatos.

La activación y el primer análisis real del coordinador están comprobados.
Quedan observación operativa, revisión de la experiencia del usuario y decisión
explícita sobre habilitar nuevos análisis manuales o ciclos. No se programaron
nuevos trabajos ni observación automática; la autorización usada era un primer
análisis, no una campaña abierta. El retorno sigue siendo el modo legacy del
mismo piloto, conservando generaciones, SQLite y logs; véase
[activación y retorno](ACTIVACION_LOCAL_A05.md).

# A-05 — Revisión de vistas con el primer informe operativo

Fecha: 07/10/2026. Revisión local en navegador de la generación
8c8efc240655459cb72d590e47233173-80537e9a8a64441da5eec20ca1b4db94.
Sin nuevos análisis, llamadas al proveedor, cambios en `.env` o notificaciones.

Next.js no estaba iniciado. Se arrancó en 127.0.0.1:3000 con la API existente
en 127.0.0.1:5000. El proceso Next de esta sesión es PID 10616; Flask se recargó
para aplicar la corrección descrita abajo y su lanzador vigente es PID 24560.
Worker PID 37076 permaneció activo. Verificar identidad de procesos antes de
operarlos; los PID pueden reutilizarse. La entrada Flask y los conmutadores de
migración no se cambiaron. La consola Next queda disponible para revisión local.

## Recorrido y resultados

| Vista | Comprobación real en navegador |
| --- | --- |
| Resumen | Cinco grupos, cuatro críticas/altas (cero críticas), una IP observada; executor activo, último job succeeded y botón Iniciar análisis desactivado |
| Amenazas | Cinco filas; filtro Alta devuelve cuatro, filtro XSS devuelve una, limpiar recupera cinco; paginación y referencias visibles |
| Reportes | Catálogo con actual y 14 históricos; actual report.md abre como texto y muestra alcance 30 seleccionadas/82 omitidas, tabla y referencias |
| Actividad | Fuente available, fecha de modificación del log, ventana reciente acotada; no se presenta como histórico completo |

La fecha visible del archivo actual es 07/10/2026, mientras que el evento XSS
es del 02/10/2026; no se sustituyó fecha de evento por la de publicación.
Las filas agrupadas con múltiples horas conservan «Sin dato en el reporte».
Los históricos excluyen la copia idéntica del actual para evitar duplicación,
por eso la lista de históricos recientes empieza por el informe anterior.
Se revisó visualmente Resumen en el viewport normal del navegador; no equivale
a repetir la auditoría de zoom/responsive/accesibilidad de las fases UI.

## Corrección encontrada durante la revisión

La tabla de eventos observados etiquetaba el payload XSS codificado como
SQL injection: la regla genérica tomaba cualquier %27 como señal SQL antes
de comprobar XSS. Se retiró esa condición en obtener_eventos_recientes;
una comilla aislada no basta. Las expresiones SQL explícitas siguen admitidas.
No se cambiaron prompts, detección del motor, clasificación o artefactos
publicados. Los gráficos de coincidencias siguen usando sus heurísticas
históricas independientes; sus conteos no son hallazgos validados del motor.

Tres regresiones sintéticas comprueban XSS codificado con comillas, nombre
ordinario con apóstrofo y tautología SQL. La prueba anterior que usaba solo una
comilla como SQL se ajustó a UNION SELECT para exigir soporte real. Pasaron
226 pruebas Python en `.p2` y `.venv`, más tres diagnósticos JS por ejecución.
Después de recargar únicamente Flask, la fila /vulnerabilities/xss_r/ muestra
XSS en el navegador. El worker siguió online y el informe conserva cinco grupos.

El lanzador inicial rechaza deliberadamente otro worker activo. Para esta
recarga controlada del mismo Flask/perfil, el script local restart_flask.py
exigió worker bloqueado y cycle/engine libres, cero trabajos activos,
entorno fijado y puerto libre tras detener exclusivamente el Flask propio.
No se relajó el helper de arranque general ni se inició otro worker.

## Evidencia y aceptación pendiente

Recibos en `.local-state/a05-activation/ui-review-20261007/`: startup.json,
flask-restart.json, flask-preflight.json y observation.json. La observación
consiste en cinco consultas de lectura separadas 15 s, comparando snapshot
Flask/Next, salud, último job y ausencia de entregas. Del 13:22:30 al 13:23:30 UTC,
las cinco muestras dieron salud ok, executor online, snapshots iguales, cinco
grupos y XSS correctamente observado; cero errores, job sin cambios y entregas
vacías. Es un minuto de observación muestreada, no horas/días ni monitor continuo.

Se solicitó al usuario revisar las cuatro vistas con **este** informe. La
confirmación histórica de fase 7 no sustituye la aceptación de A-05. A-05 sigue
abierta hasta esa aceptación y la decisión sobre el alcance de observación.
Nuevos trabajos, habilitación manual o ciclos requieren un alcance autorizado;
esta revisión no los activa. El retorno documentado conserva Flask, modo
legacy del piloto y generaciones existentes.

# A-05 — Fechas agrupadas, referencias y antigüedad del log

El 07/10/2026 el usuario señaló que las vistas mostraban eventos del 2 de
octubre, números poco claros y fechas ausentes en cuatro filas del informe.
Se confirmó y corrigió la presentación; A-05 sigue abierta por aceptación.

## Diagnóstico y corrección

Se recapturó una vez el Docker DVWA existente, bajo bloqueos cycle/engine y
sin trabajos activos. La captura tiene 112 líneas: desde 01/10/2026 18:05:05 UTC
hasta 02/10/2026 18:31:54 UTC. No hay peticiones del 07/10/2026 en esa fuente.
El análisis del día 7 había utilizado esas peticiones anteriores; su fecha de
ejecución/publicación no cambia la fecha de los eventos. No se generó tráfico
artificial para hacer aparecer actividad del día actual.

El informe agrupaba varias peticiones y solo imprimía una fecha cuando todas
coincidían. Aunque las horas por evidencia estaban conservadas en result.json,
los grupos con horas distintas se mostraban como «Sin dato en el reporte».
Ahora las amenazas muestran primera y última hora observadas, con segundos,
en Europe/Madrid. Los grupos se ordenan por su última hora conocida. El intervalo
no implica actividad continua entre extremos; si faltan fechas, se informa su
número, sin inventarlas.

Los números 26,28,41… son posiciones de las peticiones en el log usado por el
análisis. La UI los identifica como «Líneas del log» y explica que son evidencias,
no puntuaciones de severidad. Todas las vistas distinguen última petición
fechada de última copia del log; Actualizar vuelve a leer la copia local, sin
capturar Docker, generar tráfico ni ejecutar un análisis.

## Compatibilidad y artefactos

La captura de informe/metadatos se hace desde una misma generación validada;
no se mezclan intervalos de una generación distinta del Markdown leído.
La API conserva event_time y añade opcionalmente event_time_start,
event_time_end y event_time_missing_count para grupos estructurados. El estado
añade log_period; su cálculo reutiliza la caché por digest del log.

El detalle conserva markdown idéntico al archivo y añade display_markdown,
una vista determinista derivada de las mismas evidencias, con intervalos UTC y
leyenda de referencias. Next muestra esa vista y lo indica expresamente.
No se alteraron current.json, result.json, report.md, hashes, generación,
histórico o recibos anteriores. Los próximos informes utilizarán
structured-report-3; el actual conserva structured-report-2. Los históricos
legacy sin evidencias siguen mostrando únicamente las fechas realmente disponibles.
No se cambiaron prompts, familias, severidades, modelos o configuración operativa.

Flask propio se recargó conservando el worker piloto; lanzador vigente PID 23412,
Next PID 10616 y worker PID 37076 en esta sesión. Comprobar identidad antes de
operar los PID. Manual y notificaciones continúan desactivados. No hubo llamadas
al proveedor ni nuevos jobs. La API conserva salud ok y el job anterior succeeded.

## Validación y límites

227 pruebas Python pasan en `.p2` y `.venv`, tres diagnósticos JS por ejecución,
siete grupos de regresión UI, TypeScript y lint aprobados; 17 escenarios
CrewAI/LiteLLM offline aprobados. Las comprobaciones cubren intervalos, fechas
parcialmente ausentes, lectura única de generación, Markdown original preservado,
compatibilidad legacy y referencias escapadas. El navegador mostró intervalos
en las cinco filas y en el informe actual, junto a la explicación del log antiguo.

Recibos nuevos en `.local-state/a05-activation/ui-review-20261007/`:
log-refresh.json, dates-verification.json y flask-dates-final-restart.json.
Se verificaron los hashes originales y los cinco intervalos contra observaciones.
Esta comprobación no sustituye observación prolongada ni acredita nuevos eventos.
Para ver peticiones del día actual deben existir en el laboratorio y capturarse;
para incorporarlas al informe hará falta otro análisis con alcance autorizado.

La reversión de presentación consiste en retirar los campos opcionales y la
vista derivada, conservando markdown original; las generaciones no requieren
restauración. El retorno operativo al piloto legacy permanece documentado en
[activación local](ACTIVACION_LOCAL_A05.md).

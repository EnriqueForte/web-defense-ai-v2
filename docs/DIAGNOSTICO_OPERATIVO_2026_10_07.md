# A-05 — Diagnóstico operativo seguro

Entrega del 07/10/2026. Implementación en el código del motor estructurado y
coordinador, verificada offline. No se reinició el worker ni se autorizó/ejecutó
otra llamada real. A-05 sigue abierta por aceptación y observación.

## Archivos y correlación

Cada ejecución structured usa una carpeta nueva bajo
`REPORT_PATH/analysis-diagnostics/<analysis_id>-<uuid>/`. El coordinador pasa la
identidad del job y esa carpeta al hijo mediante STRUCTURED_ANALYSIS_ID y
STRUCTURED_DIAGNOSTICS_DIR. Una ejecución directa genera su identidad si falta.
Se rechazan IDs inválidos y enlaces/junctions en el destino; no se reutilizan
recibos de otra ejecución ni se modifican generaciones o informes anteriores.

| Archivo | Alcance |
| --- | --- |
| checkpoint.json | Etapas, guardas, resultados JSON/esquema, tipos/ubicaciones permitidas de errores y últimos intentos observados; actualizado durante la ejecución |
| receipt.json | Resultado del motor, generación, duración, llamadas lógicas, metadatos por intento y uso reconciliado; solo se escribe al finalizar el wrapper |
| process.json | Resultado observado por el coordinador: succeeded, failed, process_timeout o process_error; independiente del resultado del job completo |

Un timeout del coordinador conserva el checkpoint y añade process_timeout.
No crea un recibo de motor exitoso ni sobrescribe su checkpoint. No demuestra
por sí solo que todos los procesos descendientes hayan terminado. Tampoco
permite considerar una publicación verificada como un job completamente
finalizado: archivo histórico/notificación/finalización siguen siendo etapas
del coordinador posteriores al motor.

## Métricas y límites

El diagnóstico de tareas conserva llamadas lógicas y etapas locales Python.
El observador de transporte mide invocaciones a litellm.completion dentro del
proceso exclusivo de análisis; cada intento tiene número propio, vínculo a la
llamada lógica, etapa y duración. Así varios reintentos pueden pertenecer a una
misma llamada lógica. No es un contador de peticiones HTTP internas del SDK.

El observador registra únicamente modelo solicitado/informado, finish_reason,
límites, presencia/longitud de contenido y uso numérico acotado. La ruta native
de otros SDK no está instrumentada por este hook: metadata queda no disponible,
incluso si hay llamadas lógicas o un resumen SDK. Cero intentos **observados**
no demuestra cero peticiones. completion_metadata_status distingue captured,
partial y unavailable. Tokens ausentes quedan null.

Los totales reconciliados se calculan solo con cobertura completa del registro
de intentos y todos los campos disponibles. Un intento fallido con uso desconocido
impide afirmar el total completo, aunque un intento posterior termine bien.
El resumen SDK se guarda aparte como usage_sdk; discrepancias y alertas de
razonamiento/total siguen explícitas. No se suman tokens de razonamiento a
completion_tokens ni se estiman cargos o coste cero.

Se retienen hasta 100 eventos de etapa y 100 intentos; los descartados se cuentan.
Las duraciones por etapa se estiman de las marcas de eventos, con cobertura
indicada separadamente. Un diagnóstico incompleto no acredita latencia por etapa
completa. La instrumentación no cambia modelos, límites 8192/60, reintentos,
prompts, guardas, contratos API o publicación.

## Privacidad y fallos

No se serializan mensajes, prompts, logs, contenido/reasoning del modelo,
credenciales, headers, kwargs completos o mensajes de excepción. Los modelos
que contienen una credencial conocida se rechazan como metadata. Los frames
solo incluyen módulos permitidos, función y línea, sin variables locales.

El motor structured devuelve un error constante al terminal tras registrar los
metadatos seguros del error original. El coordinador structured no guarda
stdout/stderr crudos, incluso si ENGINE_DIAGNOSTICS_DIR estuviera configurado.
La ruta legacy conserva su comportamiento anterior y no recibe estos recibos.
Los errores de escritura de checkpoints se marcan cuando puede registrarse el
fallo; no sustituyen el resultado del motor. Si falta el recibo final, el consumo
no puede considerarse conocido. Un destino enlazado inicial se rechaza antes
de construir el LLM. Los datos son locales e ignorados por Git bajo reports/ o
el perfil piloto; no se publican como parte del código.

El hook se instala/restaura solo durante el runner del hijo estructurado.
Su uso presupone ese proceso exclusivo y Crew secuencial; no se ofrece como
observador global para una aplicación con múltiples análisis concurrentes.

## Verificación y carga pendiente

243 pruebas Python pasan en `.p2` y `.venv`, tres diagnósticos JS por ejecución,
66 archivos Python sin errores de sintaxis y diff limpio. Los casos nuevos
comprueban metadatos/secretos ficticios, discrepancia SDK, dos intentos de una
llamada, intento fallido con uso desconocido, native sin metadata, fallo temprano,
destinos únicos/enlazados, acotación, error de escritura, timeout con checkpoint
y supresión de stderr estructurado. Los efectos del motor se prueban con dobles.

18 escenarios CrewAI/LiteLLM offline aprobados, incluido el wrapper operativo
con SDK real y completado sintético. Se bloquean conexiones a proveedores y
se publica únicamente en un directorio temporal. El recibo coincide con la
generación, observa una detección y conserva dos tokens de razonamiento desde
metadatos; no confundir este ensayo con una llamada real al proveedor.

En Windows el sandbox rechazó os.replace en temporales; la suite pasó al ejecutarla
fuera del sandbox con permiso, manteniendo aislamiento por fixtures/dobles.
No se obtuvo un recibo retroactivo del primer job real: sus métricas siguen no
disponibles. No se reescribe la evidencia previa con datos de simulaciones.

El worker ya activo mantiene su código cargado. Para cargar la parte coordinadora
hay que comprobar ausencia de jobs activos, detener únicamente el worker propio
y reiniciarlo con el mismo perfil piloto/.p2/structured/--manual-only, manual y
notificaciones apagados. El nuevo main se carga al lanzar un hijo; no hay un
nuevo hijo activo en esta entrega. Una prueba con proveedor requiere alcance
autorizado nuevo. No usar el saldo de evaluaciones anteriores.

Reversión: retirar la llamada al wrapper/observador y el paso del destino desde
coordinador, recargar el worker si se había activado y conservar los recibos.
No necesita restaurar informes o SQLite ni cambiar .env o modo de análisis.

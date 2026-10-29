# Puerto Umbral: preparación de un análisis autorizado

El propietario autoriza el 27/10/2026 un análisis manual del snapshot guardado
en Parrot, con Groq `groq/openai/gpt-oss-120b`, exclusivamente cuota gratuita,
presupuesto de pago de 0 €, sin nuevos escenarios ni notificaciones.
La ejecución todavía no se ha realizado. No hay resultado de detección ni
aceptación del MVP atribuible a esta preparación.

## Estado observado

Las capturas del propietario muestran selección del modelo indicado y clave
guardada, no validación de la clave. La API de salud muestra ejecutor offline,
log disponible de 2060 bytes, modificado `2026-10-26T19:08:38Z`, e informe con
estado `error`. Una comprobación posterior en la raíz del proyecto devuelve
`SIN_PRIMER_INFORME` para el puntero estructurado de este perfil.

El selector actual también utiliza `error` cuando falta la primera publicación;
ese estado no acredita corrupción. La preparación no crea un informe ficticio
ni modifica el selector para ocultar errores de publicaciones existentes.

## Preparación local

Se incorpora [un ejecutor independiente](../scripts/analyze_puerto_umbral_snapshot.py).
No inicia servicios, seguimiento, worker, capturas Docker ni escenarios. Lee la
selección actual del perfil y exige fijar snapshot y SHA-256 en la orden de
ejecución, rechazando una selección diferente. El modo predeterminado es
`corrected`, como en el último arranque de la VM.

`--check` consulta configuración, metadatos, hashes, jobs y bloqueos locales;
no construye un cliente Groq ni escribe artefactos operativos. No imprime
credenciales, cuerpos de peticiones ni contenidos del log.

La ejecución explícita reserva seguimiento/worker/ciclo/motor, registra un solo
job manual y vínculo de entrada, y utiliza el motor estructurado y publicador
existentes. Conserva informes previos si falla antes de publicar. La publicación
y el registro final de SQLite no son una transacción conjunta: si se interrumpe
después de publicar, debe revisarse el recibo antes de cualquier actuación.

Se usa un adaptador directo del SDK Groq para esta orden. No modifica el motor
normal ni las preferencias persistidas. Envía solo mensajes de texto,
sin herramientas ni los marcadores de caché internos de CrewAI. Modelo y URL
están fijados, sin fallback. El transporte desactiva proxies del entorno,
redirecciones y reintentos SDK. Un hook de peticiones limita el proceso a seis
solicitudes HTTP. Cada respuesta admite hasta 8192 tokens de salida, con
razonamiento bajo y JSON validado por los contratos existentes. Los intentos
de reparación de contratos, si se producen, consumen ese mismo máximo de seis.
Una respuesta truncada, un error 429 o un fallo de conexión no provoca un
reintento de red. El proceso supervisor impone 600 segundos de duración.

La autorización se consume una vez mediante la clave idempotente del job y
`.local-state/puerto-umbral/manual-validation.json`. Repetir la orden no inicia
otro análisis. Un cierre forzado puede conservar estado `started`/job activo;
no borrar el recibo ni recuperar automáticamente para volver a ejecutar.
Un fallo posterior a la reserva requiere revisión, no reintento automático.

## Condición económica

El selector gratuito de V2 no consulta el plan de facturación de la cuenta.
La ejecución requiere `--groq-free-account`, declaración del propietario de
que la cuenta real está en Free. No cambia planes ni crea medios de pago.
No existe comprobación local automática de facturación: si la cuenta estuviera
en Developer, este modelo puede generar cargos y no debe ejecutarse esta orden.
El coste real se conserva como `null`, no como un cero medido.

Groq indica que el plan Free no genera cargos y que, al superar su cuota,
devuelve 429: [FAQ del plan Free](https://community.groq.com/t/do-i-get-charged-for-anything-on-the-groq-free-plan/832).
La [FAQ de facturación](https://console.groq.com/docs/billing-faqs) distingue
Developer con pago por uso. La [referencia API](https://console.groq.com/docs/api-reference)
documenta JSON y límites de salida. Consultadas el 27/10/2026.

## Recorrido manual en Parrot, tras distribuir el archivo

Mantener V2 abierto en el perfil Puerto Umbral/corrected, con seguimiento
detenido. No activar el ejecutor normal ni el botón de análisis.
No se requiere recompilar el frontend ni reinstalar dependencias.

Desde la raíz del proyecto:

```bash
.p2/bin/python -B scripts/analyze_puerto_umbral_snapshot.py --check
```

Revisar `ready`, `blockers`, `snapshot_id`, `sha256` y `line_count`. Esto no
ejecuta el modelo. Si hay bloqueadores, detener el recorrido y revisarlos.
Si el resultado es válido y la cuenta real es Free, ejecutar una sola vez
con los valores completos que devolvió la comprobación:

```bash
.p2/bin/python -B scripts/analyze_puerto_umbral_snapshot.py \
  --authorized-free-analysis --groq-free-account \
  --snapshot-id ID_COMPLETO --sha256 SHA256_COMPLETO
```

Los marcadores se sustituyen por los valores del check; no son valores reales.
La orden lee la clave guardada localmente sin mostrarla ni pedir copiarla.
Al terminar conserva el resultado de la orden en `manual-validation.json`,
el vínculo en `analysis-inputs`, diagnósticos seguros y, solo si el motor valida
el resultado, una generación de informe en `reports/structured` y su histórico.
La salud puede leerse sin ejecutar análisis para revisar la disponibilidad del
informe. El ejecutor normal puede seguir indicando offline: esta orden termina
al finalizar su único trabajo.

Un error no se resuelve repitiendo el análisis ni borrando el registro.
Una ejecución válida permitirá comprobar el recorrido del snapshot concreto;
no constituye evaluación de los 45 casos ni aceptación completa de F2–F5.
En la versión publicada `1403f8d`, el resumen `manual-validation.json` no
pertenece a la lista del backup general: conservarlo aparte al utilizar esa
versión. El job idempotente en SQLite y los diagnósticos sí utilizan rutas ya
respaldables. La ampliación local del 29/10, descrita al final, corrige esa
omisión sin modificar los archivos históricos.

## Verificación y publicación

AST y compilación en memoria del ejecutor correctos, sin importarlo ni
ejecutarlo. Enlaces locales comprobados y `git diff --check` correcto.
No se ha ejecutado el check en la VM ni se ha construido o llamado a Groq
desde Windows. No se han iniciado escenarios, servicios, suites automáticas
o capturas nuevas.

El propietario autoriza después publicar el ejecutor, esta guía y las notas
de contexto/recepción mediante commit/push con `[skip ci]`. La revisión remota
se realizará tras el push; el commit de esta entrega se identifica en el
historial Git, sin afirmar una ejecución del modelo por distribuir el archivo.
La actualización de Parrot y el check del snapshot son pasos posteriores.

## Resultado aportado por el propietario en Parrot

El ejecutor se publicó en `1403f8d3be1896a8055e71fabb0e18b96dbc5b58`, con
`[skip ci]`; se comprobó la coincidencia de main remoto/local y el árbol limpio
tras publicar. Las capturas posteriores muestran el archivo disponible en la
VM, el check con `ready: true`/sin bloqueadores y la ejecución autorizada.
No muestran por sí mismas el HEAD completo de la VM.

La salida final aportada registra:

| Campo | Valor observado |
| --- | --- |
| Estado | `succeeded` |
| Análisis | `f5b674c867994aeba3beeb4a638d7a33` |
| Snapshot corregido | `df39623de3684fa7932edf6b688b2f04`, 17 líneas |
| SHA-256 | `2f891446d512be3a31ee858db5f3318156f74b3d2348b40a7ee41dd8c59f2b4a` |
| Modelo | `groq/openai/gpt-oss-120b` |
| Solicitudes de transporte | 3 |
| Metadatos de uso | Completos, 3 completions observadas |
| Tokens de entrada / salida / total | 6889 / 1261 / 8150 |
| Tokens de razonamiento reportados | 372, no se suman otra vez al total |
| Grupos clasificados | 3 altos, 1 medio, 0 críticos/bajos/desconocidos |
| Integridad al finalizar | `input_unchanged: true` |
| Coste real del proveedor | `null`: no medido por este recibo |

El resumen contiene una generación y éxito tras la comprobación de publicación
del ejecutor. Es evidencia aportada en pantalla, sin acceso independiente del
agente a los bytes originales, al panel de facturación o a la VM. El agente
no ha ejecutado el modelo en Windows.

Queda comprobar visualmente que V2 carga ese mismo análisis y sus conteos,
abrir su informe actual y revisar el contenido. Todavía no se acredita esa
visualización ni la calidad semántica de cada grupo. No se deducen cuatro
explotaciones confirmadas ni precisión/recall del corpus completo.

La autorización de una ejecución ya se consumió. No repetir la orden ni borrar
el registro para permitir otro análisis. Esta nota posterior es local, sin
nuevo commit/push. La aceptación global del MVP permanece pendiente.

## Confirmación visual del informe en V2

Una captura posterior del propietario muestra `report.md` publicado el
27/10/2026 a las 22:38:42 (Madrid), con el análisis
`f5b674c867994aeba3beeb4a638d7a33`. El resumen y el alcance indican 17 líneas
seleccionadas de 17, sin omisiones, y cuatro grupos que requieren investigación.

| Patrón mostrado | Líneas del log | Severidad | Estado |
| --- | --- | --- | --- |
| SQLi | 7 | Alta | Requiere investigación |
| XSS | 13, 14 | Media | Requiere investigación |
| Path Traversal | 15 | Alta | Requiere investigación |
| Command Injection | 17 | Alta | Requiere investigación |

La IP mostrada en los cuatro grupos es `172.20.0.1`. Los conteos coinciden con
el recibo de ejecución: tres altos y uno medio. Se acredita así, por las
capturas del propietario, el recorrido básico **snapshot guardado → análisis
Groq → publicación → informe visible en V2** para este snapshot concreto.

Esta comprobación operativa limitada queda completada, sin solicitar nuevas
ejecuciones. El recorte no incluye las recomendaciones inferiores ni el estado
global de fuentes, y no sustituye revisión de bytes originales o facturación.
Las líneas de access.log no acreditan éxito de explotación. No se acepta por
ello el corpus de 45 casos, las métricas globales del detector ni el MVP completo.
Esta recepción visual queda registrada localmente, posterior a `1403f8d`, sin
nueva publicación ni llamadas adicionales al modelo.

## Corrección de la fuente mostrada en Amenazas y Reportes

El propietario observa una referencia fija a DVWA en el texto de eventos de
ambas vistas. Se corrige el componente compartido para utilizar el identificador
opcional de fuente que Flask incluye en `meta.sources.log.source`.
Con `puerto-umbral` muestra Puerto Umbral; conserva DVWA para los perfiles de
ese laboratorio y usa un texto neutro si falta el metadato. No añade consultas
de captura ni cambia el informe guardado.

TypeScript sin emisión, ESLint de los tres archivos TypeScript modificados,
sintaxis Python, JSON OpenAPI y `git diff --check` correctos. Sin suites,
escenarios, servicios o nuevas llamadas al modelo. El propietario autoriza
publicar la corrección junto con estas actas pendientes mediante commit/push
con `[skip ci]`. El commit se identifica en el historial Git y su verificación
remota se realiza tras publicar.

Para recibir la corrección en Parrot se debe cerrar la consola propia,
actualizar el checkout, recompilar el frontend con Webpack y volver a arrancar
el mismo perfil. No reinstalar dependencias ni repetir el análisis autorizado:
el informe ya publicado permanece en el estado local de la VM. La recepción
visual de esta corrección en Parrot todavía no se ha observado.

## Continuación del 29/10/2026

La corrección de nombres y las actas se publicaron en
`9e71c0cdac60fba70c037dc7c04405cbd5a18b35`, con main remoto verificado y árbol
local limpio tras el push. El propietario declara ahora comprobada la corrección
en Parrot y solicita continuar los pendientes. No se infiere de esa declaración
una nueva inspección del HEAD o de los archivos originales de la VM.

Se preparan localmente dos ajustes de conservación y estado: el recibo del
análisis único pasa a ser un nombre permitido en el respaldo de Puerto Umbral
y, a través de la misma lista, en la restauración aislada; el selector distingue
un puntero ausente (`missing`) de una publicación existente inválida (`error`).
No se ejecutan respaldos/restauraciones, servicios, suites o modelos para este
bloque. El informe observado se conserva; los cambios no autorizan repetir el
análisis ni consideran cerrado el MVP.

El propietario autoriza después el commit/push de esos dos ajustes y sus actas
con `[skip ci]`. La actualización de Parrot solo requiere recibir la fuente y
reiniciar V2 en el mismo perfil, sin recompilar el frontend o reinstalar.
Publicar o arrancar no ejecuta un respaldo, restauración o análisis nuevo.
La revisión remota se realiza al terminar la publicación; la identidad de esta
entrega queda en el commit que incorpora la presente nota.

## Recepción de las mejoras y selección del respaldo

Las mejoras se publican en `c8abcafadf07569d7e0d866bcc64faae8711f569`, con
main remoto verificado y árbol local limpio tras el push. En capturas
posteriores del propietario, el listado de `backup_operational.py --profile
puerto-umbral --list` incluye
`.local-state/puerto-umbral/manual-validation.json` como `file`, junto al SQLite,
la publicación estructurada y sus diagnósticos. El recorte no muestra todo el
listado o el campo `missing`; no se infieren un total de archivos o ausencia
de faltantes. El listado acredita selección, todavía no copia o restauración.

La vista de Amenazas muestra «Lectura conectada», archivos disponibles y el
texto de Puerto Umbral; la tabla anuncia cuatro coincidencias. El informe
sigue mostrando el análisis `f5b674c867994aeba3beeb4a638d7a33`, su fecha de
publicación del 27/10 a las 22:38:42 (Madrid), 17 líneas sin omisiones y los
mismos cuatro grupos, tres altos y uno medio. Esta evidencia confirma la
conservación visible del informe después de la actualización, sin una nueva
llamada al modelo ni verificación independiente de los bytes de la VM.

El caso de puntero ausente no se ensaya borrando el informe existente. El
siguiente paso es crear una copia del perfil, con operaciones detenidas,
y revisar `verified`, `missing` y el destino generado antes de seleccionar
ese directorio exacto para una recuperación aislada. No se atribuye todavía
un resultado a esos pasos. Esta recepción se registra localmente después de
`c8abcaf`, sin otra publicación.

## Copia real del perfil, 29/10/2026

La siguiente captura del propietario muestra la ejecución de
`backup_operational.py --profile puerto-umbral` con esta salida:

| Campo | Valor observado |
| --- | --- |
| Directorio de copia, relativo a la raíz del proyecto | `.local-backups/operational-20261029T185605963239Z` |
| Archivos | 66 |
| Verificación | `true` |
| Faltantes | `[]` |

Según el funcionamiento de la herramienta, `verified: true` se escribe tras
crear el ZIP y comprobar extracción aislada, hashes y SQLite en `restore-check`.
La captura acredita esa salida, sin una inspección independiente por el agente
del archivo o manifiesto de Parrot. No acredita una recuperación completa de
Docker, `.env`, volúmenes o recibos del laboratorio bajo `labs/`.

Queda como siguiente paso ejecutar el restaurador independiente contra ese
directorio exacto y revisar su salida. Solo crea un árbol nuevo bajo
`.local-state/recovery/`; no promueve esa copia al estado vivo, arranca servicios
o repite análisis. Aún no se atribuye éxito a ese paso posterior. La copia y los
datos originales deben conservarse. Acta local posterior a `c8abcaf`.

## Restauración aislada observada, 29/10/2026

La captura posterior del propietario muestra el restaurador independiente
aplicado a `.local-backups/operational-20261029T185605963239Z`:

| Campo | Valor observado |
| --- | --- |
| Directorio nuevo, relativo a la raíz | `.local-state/recovery/restore-20261029T185830160239Z` |
| Esquema | `web-defense-ai.restore.v1` |
| Verificación / archivos / faltantes | `true` / 66 / `[]` |
| Base de datos del perfil Puerto Umbral | `verified` |
| Publicación estructurada | `verified` |
| Trabajos | Un `succeeded` |
| Entregas | `{}` |
| Generación | `f5b674c867994aeba3beeb4a638d7a33-a1e812cf5d974f1995a78966e9181d50` |
| Hash del manifiesto reportado | `f3eb92c5386ce73da937a3c46b67ebb7c21719a557aa266505a0d11a577e96c1` |
| Alcance | `isolated_application_data_no_live_replacement_no_delivery_replay` |

La generación coincide con la del análisis único y el informe ya observado.
El recorrido básico de creación de copia y recuperación independiente de los
datos del perfil queda completado dentro del alcance de estas capturas. El
agente no accedió a Parrot, recalculó los hashes originales o ejecutó modelos.
La salida no acredita sustitución del estado vivo, arranque desde el árbol
recuperado, restauración de Docker o recuperación completa de la VM.

Conservar tanto la copia como el árbol recuperado y los originales. No hace
falta repetir esta comprobación o el análisis para cerrar este recorrido.
Permanecen pendientes la calidad del detector sobre el corpus completo, los
fallos históricos, las condiciones ampliadas de F4 y la aceptación global del
MVP. Esta acta posterior a `c8abcaf` permanece local, sin nuevo commit/push.

Nota de distribución posterior, 29/10: el propietario autoriza incorporar estas
actas pendientes al commit/push del paquete de código revisado F6/F7. El estado
local descrito arriba corresponde a su registro inicial; esta publicación no
repite el análisis, respaldo o restauración ni amplía lo acreditado por las
capturas originales. La identidad de entrega queda en el historial de este archivo.

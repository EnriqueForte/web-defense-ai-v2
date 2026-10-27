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
El nuevo resumen `manual-validation.json` no pertenece a la lista actual del
backup general: conservarlo aparte si se respalda este recorrido. El job
idempotente en SQLite y los diagnósticos sí utilizan rutas ya respaldables.

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

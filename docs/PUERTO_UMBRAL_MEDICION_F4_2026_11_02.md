# Puerto Umbral — medición operativa acotada F4

Preparado el 02/11/2026. **Observador desarrollado; cinco comprobaciones
aisladas correctas; ensayo real, parada y lectura del recibo completados en
Parrot. Desviación acotada de F4-AC1 aceptada expresamente; F4 global abierta.**
La sesión antigua está interrumpida e inactiva según la respuesta actual de V2.
No se modifican el servicio de seguimiento, la interfaz o los logs para medir.

## Recepción en Parrot y sesión acordada

Entrega publicada `586f050a85f21e0d4014a8d571453acdb58627fd`, con HEAD remoto
coincidente y árbol limpio verificados al terminar Git. El propietario aporta
captura en Parrot: `git status --short` vacío, `git pull --ff-only` ya actualizado
y `586f050` en HEAD/main/origin. Recepción completada, sin repetir actualización,
build, instalación o reinicio de servicios por estas actas.

El propietario autoriza expresamente una única sesión manual en modo corregido,
intervalo cinco segundos/duración cinco minutos, observador de veinte ciclos
con GET locales, lectura SQLite antes/después y un recibo nuevo. Quedan fuera
nuevos escenarios, llamadas al modelo, suites, cambios de logs y contenedores.
**Autorizada, ejecutada y recibida por capturas/salida del propietario**,
según los resultados siguientes; no se vuelve a ejecutar por este documento.

Preparar primero Actividad con intervalo/duración indicados sin pulsar inicio.
En otra terminal desde la raíz, ejecutar el observador con `--observe`.
Solo al ver «Observador preparado» se pulsa Iniciar seguimiento una vez.
Al obtener veinte muestras y resumen/recibo, detener desde Actividad y esperar
confirmación Detenido. Si falla antes de estar preparado, no iniciar; si falla
después, detener la sesión iniciada y conservar salida/recibo sin reintentar.
Se solicita salida final del observador y estado detenido, no veinte capturas.

## Resultado recibido de la medición

Captura del propietario: sesión `a3c05482a81a4b2894da55ad53f30583`,
`status: observed_20_cycles`, `error_code: null`, 114 GET realizados,
`database_unchanged: true`, `single_checkpoint_observed: true` y
`all_observed_api_bounds_within_10_seconds: true`. El resumen corrobora las
veinte muestras aunque el recorte solo incluye las filas 6–20; no se piden
otra vez las cinco primeras por esa razón.

Recibo creado según salida del observador:
`.local-state/puerto-umbral/operational-review/follow-4bb2c1c519524ab5b68ed82d3ea116d0.json`.

Lectura posterior del recibo, aportada por el propietario, confirma:

| Magnitud / comprobación | Resultado del ensayo |
| --- | --- |
| Muestras distintas | 20 |
| Lectura, mínimo / máximo | 0,057 / 0,096 s |
| Cota de disponibilidad por API, mínimo / máximo | 0,086 / 1,054 s; las veinte dentro de diez segundos |
| Trabajos antes / después | 1 / 1; metadatos sin cambios según observador |
| Entregas antes / después | 0 / 0 |
| Directorios de snapshots antes / después | 25 / 26 |
| Único snapshot nuevo | `b41656aab6e548e9bac5458c69e41637` |
| Checkpoint de las veinte muestras | Uno único según observador |

Condiciones registradas: Linux `7.0.9+parrot7-amd64`, arquitectura `x86_64`,
16 CPU lógicas visibles. Carga media antes (1/5/15 minutos):
`[1.28466796875, 0.603515625, 0.26904296875]`; después:
`[0.26318359375, 0.4521484375, 0.25341796875]`.
No se inventaría hardware adicional o carga de otras condiciones de uso.

**Completado el ensayo acotado de disponibilidad API, reutilización y ausencia
de nuevos trabajos/entregas en la ventana observada**, según herramientas y
capturas del propietario, sin acceso independiente del agente a la VM. Un
solo directorio nuevo y un checkpoint estable son coherentes con la referencia
inicial y los contadores del panel; no hay duplicaciones adicionales observadas
en este ensayo. No se generaliza a todo el historial o tráfico nuevo.

Captura posterior de Actividad confirma **Detenido**, inicio disponible y
pausa/reanudación/parada deshabilitados: 21 ciclos válidos, un snapshot nuevo,
20 sin cambios, intervalo cinco segundos/duración cinco minutos. Última lectura
visible: 02/11/2026 a las 17:40:13 de Madrid, 0,073 s; el fin de duración
programado es 17:43:32. Son última lectura y vencimiento previsto, no una hora
exacta de parada. El ciclo adicional hasta la acción de detener no invalida
las veinte muestras del recibo ni se añade a ellas como muestra medida.
**Parada y lectura del recibo completadas**; no repetir botón, sesión,
arranque, observador, lectura del recibo o captura por estas actas.

## Dictamen del alcance medido

La disponibilidad API queda medida en veinte ciclos y cumple la cota de diez
segundos en este ensayo. El observador también corrobora que el seguimiento
no añadió trabajos/entregas y reutilizó la referencia dentro de esa ventana.
No se mide el pintado del navegador, tiempo desde una petición nueva del portal,
rotación o desconexión de la fuente. No se declara F4 global aceptada.

F4-AC1 permite medición conforme o una desviación documentada y revisada.
El propietario **acepta expresamente el 02/11 la desviación acotada**: admitir
para esta entrega la evidencia de disponibilidad API de veinte muestras con
máximo 1,054 s, dejando sin verificar renderizado y visibilidad extremo a
extremo de RNF-09. F4-AC1 se trata por esa vía de desviación revisada, **no como
cumplimiento medido del objetivo original de interfaz**. No se modifica el PRD
ni se acepta toda F4 o el proyecto. Fallo/rotación de fuente y demás criterios
abiertos mantienen su tratamiento separado.

## Recorrido completado: desconexión y reinicio de fuente

**Autorizado expresamente y completado por capturas/salida del propietario,
incluida la integridad puntual del snapshot anterior.** El
propietario acepta este único recorrido de fallo/recuperación, incluyendo
seguimiento, parada/arranque de la pasarela corregida, una captura manual
posterior y lectura de conservación. La sesión anterior excluía intervenir
contenedores; este permiso es distinto y no amplía escenarios, suites o modelo.
Alcance: una interrupción de `puerto-umbral-f2-gateway-corrected` y recuperación
del mismo contenedor, sin tocar targets, red, imágenes, volúmenes o logs.

1. Mantener V2 en lectura/corregido, sin ejecutor manual. La sesión previa ya
   está detenida; no repetir el observador o sus veinte muestras.
2. Iniciar desde Actividad una sesión de seguimiento a 5 s/5 min, una vez,
   para observar su respuesta a un fallo; no es otra medición de latencia.
3. En otra terminal, detener únicamente la pasarela corregida con
   `docker stop --time 3 puerto-umbral-f2-gateway-corrected`.
4. Esperar el estado de error de seguimiento/fuente y conservar captura. El
   código usa `require_running=True`: se espera `source_stopped` y que se
   conserve el snapshot anterior. Si aparece otro resultado, revisar salida
   antes de ampliar acciones; no borrar locks, estados o evidencia.
5. Volver a arrancar el mismo contenedor con
   `docker start puerto-umbral-f2-gateway-corrected`. El seguimiento no debe
   reanudarse por sí solo. Si siguiera activo, detenerlo desde la interfaz.
6. Con la pasarela disponible y sin seguimiento activo, pulsar una vez
   Capturar log de Puerto Umbral para obtener una referencia actual. Conservar
   resultado y comprobar en lectura que el snapshot anterior
   `b41656aab6e548e9bac5458c69e41637` sigue existiendo y coincide con su hash
   guardado en el recibo del ensayo; no repetir el ensayo, copias o respaldos.

Guía inicial entregada: iniciar seguimiento y esperar Siguiendo logs; detener
la pasarela, observar/guardar el error y después restaurar el mismo contenedor.
Se da el comando de restauración desde el principio para no dejar la fuente
detenida esperando una respuesta del chat. Conservar también la salida de
`docker start`. El recorrido se detiene ante resultados inesperados, restaurando
la fuente si llegó a pararse; no se reintenta seguimiento automáticamente.

Recepción posterior del propietario: Actividad muestra **Seguimiento con error**
y «La pasarela está detenida. Se conserva la última evidencia válida; un error
no significa ausencia de eventos». Conserva tres ciclos válidos, cero snapshots
nuevos y tres sin cambios; última lectura 02/11 a las 18:00:15 de Madrid,
0,117 s. El fin de duración previsto es 18:05:05, no una hora de error/parada.
Inicio está habilitado y pausa/reanudación/parada deshabilitados en la captura.

La terminal muestra ambos comandos sobre la pasarela exacta, con su nombre de
contenedor devuelto tanto por `docker stop` como por `docker start`, sin error
visible. Parada/arranque del contenedor y error de fuente observados según
salidas del propietario; todavía no se acredita recuperación de captura o
integridad de bytes del snapshot conservado con el mensaje de la interfaz.
No se repiten los comandos ni se inicia otro seguimiento.

Siguiente dentro del mismo permiso: Actualizar seguimiento (solo lectura) y,
si no está activo, una pulsación de Capturar log de Puerto Umbral. Conservar
fuente y estado de seguimiento después. El estado de error del último intento
puede permanecer mientras la captura nueva pasa a disponible: no es una orden
de reanudar seguimiento ni prueba de que la fuente siga caída. Si se observa
actividad o falla la captura, guardar salida antes de repetir o corregir.

Captura posterior del propietario: **Captura disponible · Modo corregido**,
94 líneas, obtención/última lectura válida 02/11/2026 a las 18:03:42 de Madrid,
snapshot `a0c4aafab7a645f986a11f7164ef316a`, SHA-256
`40354503f19a91d865a41bbe353a088a1571ad461eecfeaf0a4c154273113d7d`.
El estado del origen se refiere a cuando se capturó, no a salud continua.

El seguimiento conserva error, tres ciclos y última lectura 18:00:15; inicio
habilitado, pausa/reanudación/parada deshabilitados. Fuente nueva disponible
y ausencia de auto-reanudación observadas por captura. El mensaje rojo pertenece
al intento anterior del seguimiento, no invalida la captura nueva. No se
repiten captura, start/stop o seguimiento. Sigue únicamente la lectura de
integridad del snapshot `b41656aab6e548e9bac5458c69e41637`, comparando sus bytes
con el hash registrado en la primera muestra del recibo del ensayo; no se
confunde con el nuevo ID/hash ni se recalcula un veredicto del modelo.

La lectura final del propietario devuelve
`snapshot_anterior: b41656aab6e548e9bac5458c69e41637`, `existe: true` y
`sha256_coincide: true`. El bloque leído comprueba antes el ID esperado y
compara el SHA-256 de los bytes actuales con el guardado en `samples[0]` del
recibo del ensayo. **Conservación e integridad puntual comprobadas según salida
de la herramienta del propietario**, sin acceso independiente del agente a VM.
No se solicita repetir la lectura, crear otro respaldo o recapturar.

Queda completado el recorrido acordado: fallo real visible de la fuente,
parada/arranque de la pasarela prevista, recuperación manual de captura,
ausencia de auto-reanudación y snapshot previo intacto. La captura recuperada
de 94 líneas no reemplaza ni borra la referencia anterior. No se acredita
integridad de todos los snapshots, recuperación de toda la VM o rotación del
log. Las instrucciones de preparación anteriores conservan el protocolo del
ensayo realizado, no una orden para repetirlo.

El agente solo guía: no opera Docker/VM ni envía control por su cuenta. Quedan
fuera escenarios, modelo, suites, borrado/truncado o rotación de logs. Este
recorrido puede acreditar desconexión y reinicio, **no rotación real**; ese
pendiente no se transforma en aprobado por reiniciar un contenedor.

## Entrega versionada

El propietario autoriza commit/push del observador, sus cinco pruebas y la
documentación acumulada: trece archivos, once Markdown y dos Python, con
`[skip ci]`. Base `91a101e` coincidente con `origin/main` tras fetch y staging
inicial vacío. La entrega se identifica por el commit que incorpora esta nota;
su publicación se verifica contra HEAD remoto al terminar Git, sin anticiparla.
No se crea una release ni se autoriza una sesión real por publicar la fuente.

En Parrot se conserva cualquier cambio local y se actualiza con
`git pull --ff-only`. Solo se añaden el observador/pruebas y actas; no requiere
recompilar frontend, reinstalar dependencias o reiniciar los servicios ya
abiertos. Antes de la medición se confirma que el archivo ya está recibido y
se acuerda la sesión manual acotada; las pruebas simuladas no la sustituyen.

## Acción preparada para revisar

El [observador](../scripts/observe_puerto_umbral_follow.py) recoge veinte ciclos
distintos de **una sesión nueva que inicia el propietario desde Actividad**:
intervalo de cinco segundos, duración de cinco minutos y modo corregido.
Debe iniciarse el observador antes del seguimiento para fijar la referencia.

Su ayuda y el inicio explícito son:

```bash
.p2/bin/python -B scripts/observe_puerto_umbral_follow.py --help
.p2/bin/python -B scripts/observe_puerto_umbral_follow.py --observe
```

Esta receta queda preparada; no solicita ejecutarla antes de recibir el archivo
en Parrot y acordar la sesión. Sin `--observe` solo muestra ayuda. No importa
Flask, el pipeline o la configuración del proveedor, ni carga `.env`.

| Límite | Comportamiento |
| --- | --- |
| Transporte | Solo GET a `http://127.0.0.1:3000/api/v1/fuentes/log`, sin proxy del sistema ni redirecciones; respuestas de hasta 64 KiB y timeout de dos segundos |
| Duración/cantidad | Espera hasta 180 segundos desde que anuncia estar preparado; como máximo 181 GET contando el inicial; objetivo de veinte ciclos distintos, no veinte sondeos repetidos |
| Control | No envía POST, no inicia/pausa/detiene seguimiento, no contacta Docker, portales, proveedores o notificaciones |
| Base de datos | SQLite `mode=ro`/`query_only`, transacción de lectura antes y después; cantidades y hashes de metadatos de trabajos/entregas, sin destinos o contenido de logs |
| Capturas | Cuenta directorios de snapshots antes/después; conserva los IDs/digests de los checkpoints observados; no escribe en ellos |
| Escritura | Un recibo nuevo con nombre aleatorio y apertura exclusiva en `.local-state/puerto-umbral/operational-review/`; no sobrescribe evidencias anteriores |
| Fallo/interrupción | Conserva muestras parciales, estado incompleto y causa acotada; no inventa veinte ciclos, reintenta sesiones o cambia fuentes automáticamente |

Al terminar o fallar, si inició la sesión, el propietario la detiene desde
Actividad y consulta el estado. La sesión tiene además su duración finita de
cinco minutos. El observador nunca altera el proceso para detenerla.

## Qué mide y cómo se interpreta

Cada muestra relaciona un ciclo con su inicio, fin, duración de lectura,
checkpoint y el momento en que se observa coherente por la API que usa V2.
Se registra la cota `observed_at - last_cycle_at`, que incluye el sondeo y
transporte local. Se rechaza reloj incoherente; se registran sistema/kernel,
arquitectura, CPU lógicas y carga disponible antes/después.

**Es disponibilidad observada por API, no tiempo de renderizado/pintado del
navegador.** RNF-09 exige captura visible en diez segundos con condiciones del
ensayo; no se cambia ese requisito ni se declara satisfecho automáticamente.
El recibo marca `browser_paint_measured: false` y requiere revisión del
propietario. La medición contribuye a F4-AC1; cualquier desviación debe quedar
expresamente revisada, como permite el PRD.

El resultado `observed_20_cycles` significa que se recogieron veinte muestras,
**no que toda F4 haya pasado**. Las banderas separan la cota de diez segundos,
igualdad de metadatos SQLite y estabilidad de checkpoint. Un cambio de base,
origen o condición se conserva en el resultado; no se oculta para aprobarlo.
El primer ciclo puede renovar la referencia del origen sin duplicación por
cambios de identidad/procedencia; los directorios nuevos se informan aparte.

No se generan solicitudes nuevas en los portales durante la medición. Esto
permite estudiar reutilización sin cambios, sin acreditar ingestión de tráfico
nuevo, rotación o continuidad completa del historial. La interrupción de
contenedores y modificación de logs quedan fuera de esta sesión propuesta.
El recibo nuevo tampoco amplía retroactivamente el respaldo de 113 archivos.

## Verificación del observador

Se preparan cinco pruebas en
[test_follow_observer.py](../tests/test_follow_observer.py):

- La ayuda predeterminada no inicia observación ni lee datos operativos.
- URL GET fija, redirecciones deshabilitadas y entrada excesiva rechazada.
- Lectura de SQLite temporal conserva bytes y omite campos privados.
- Veinte ciclos distintos con sondeos duplicados no inflan la muestra.
- Un fallo de lectura conserva el recibo parcial sin inventar éxito o exponer
  el detalle de una excepción.

Usan respuestas simuladas y archivos temporales, sin servicios o transporte
real. El propietario autoriza después expresamente estas cinco pruebas;
se ejecuta una vez en Windows con `.p2`, Python **3.11.9**:

```powershell
.p2/Scripts/python.exe -B -m unittest tests.test_follow_observer -v
```

Resultado **5/5 correctas, 0,085 s según unittest, exit 0**. Sintaxis de ambos
archivos revisada y ayuda ejecutada sin iniciar observación. No se amplía la
suite después de este resultado. La ejecución con datos y HTTP reales en
Parrot sigue pendiente; las pruebas simuladas no acreditan latencias de la VM,
consumo real del proveedor o aceptación F4. Publicación Git y sesión Parrot
no se presuponen por aprobar las cinco comprobaciones.

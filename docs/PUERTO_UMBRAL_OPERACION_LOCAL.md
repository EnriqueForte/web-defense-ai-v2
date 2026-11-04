# Puerto Umbral y V2 — manual de operación local

## Arranque unificado — cambio preparado el 04/11

La entrada habitual `python3 webdefensev2.py` (Windows: `py webdefensev2.py`)
habilita el ejecutor manual junto a captura y seguimiento. No solicita análisis
ni inicia seguimiento automáticamente. Ya no es necesario cerrar y arrancar
con `--enable-manual` para pasar de logs a análisis; esa opción se conserva
como compatibilidad. `--read-only` permite omitir el ejecutor explícitamente.

El ejecutor inactivo puede convivir con la captura y el seguimiento. Un análisis
solicitado desde V2 detiene primero el seguimiento propio y solo se admite
cuando su parada está confirmada. Una sesión de otro proceso o una parada
pendiente produce un conflicto sin encolar el análisis. Los bloqueos de ciclo
y motor mantienen la exclusión entre operaciones reales; un trabajo pendiente
impide iniciar seguimiento o capturar manualmente. El seguimiento no se reinicia
automáticamente después de analizar: se inicia desde su botón cuando se desee.

Los dos portales arrancan juntos: vulnerable en 4380 y corregido en 4382.
La fuente de V2 se cambia en Actividad mediante el selector Corregido/Vulnerable,
sin reiniciar. Flask y el ejecutor leen una selección compartida, acotada a la
sesión del lanzador. El cambio exige seguimiento detenido y ningún análisis
pendiente/activo; no ejecuta escenarios ni captura automáticamente. Después
de cambiar, capturar el log o iniciar seguimiento para esa fuente. Auditoría
de aplicación usa también la selección nueva. Snapshots e informe anteriores
se conservan y el desajuste de modo queda visible hasta capturar. Un arranque
nuevo comienza en corregido salvo `--lab-mode` inicial explícito.
Las recetas inferiores de cerrar/reabrir para habilitar el análisis
describen el comportamiento anterior. Implementación local preparada, con trece
regresiones aisladas nuevas escritas y no ejecutadas; no hay build ni validación
de este cambio en Parrot todavía. Las actas anteriores conservan su versión.

Estado de cierre acordado el 03/11: F4/F5 cerradas por decisión expresa del
propietario sin sus pruebas restantes; F6 conserva su cierre previo y la matriz
F7 está aceptada en su alcance educativo. Rotación real y métricas del detector
no acreditadas se mantienen como límites. Las recetas siguientes son referencia
de uso, no tareas pendientes de cierre ni solicitudes de ejecución. Véase el
[registro vigente](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md).

Referencia inicial de entrega: código operativo `02d2638`, revisión del 27/10/2026.
Actualización de estado del 29/10: ejecutor acotado publicado en `1403f8d`,
corrección de nombres de fuente en `9e71c0c` y un análisis/informe de 17 líneas
observado en Parrot. Los ajustes de ausencia de informe y cobertura del recibo
descritos aquí forman parte de la revisión del 29/10, cuya publicación autoriza
el propietario. La identidad de la entrega se obtiene del commit que incorpora
esta revisión. Los ajustes se publicaron después en `c8abcaf`; el propietario
aportó capturas de selección, creación de copia y restauración aislada del perfil.
La [evaluación F5](PUERTO_UMBRAL_F5_2026_10_27.md) registra alcance, evidencias y
pendientes. Este manual conserva las recetas de uso; no solicita ejecutarlas
de nuevo durante el bloque documental F5.

## Preparación y direcciones

Se utiliza el checkout de V2 con `labs/puerto_umbral`, Python 3.11 en `.p2`,
Node 24 o posterior, las dependencias del frontend, Docker y el cliente Compose
disponible. Las instrucciones de instalación están en
[Instalación autoalojada](INSTALACION_AUTOALOJADA.md) y la
[guía específica de Parrot](PUERTO_UMBRAL_PARROT_2026_10_26.md).
La revisión actual acredita una actualización de la instalación del propietario;
no se ha repetido una instalación limpia o recuperación completa en F5.

| Dirección | Función |
| --- | --- |
| `http://127.0.0.1:3000` | Interfaz V2, Actividad y seguimiento |
| `http://127.0.0.1:5000` | API local de V2 |
| `http://127.0.0.1:4381` | Panel de Puerto Umbral |
| `http://127.0.0.1:4380` | Portal vulnerable del laboratorio |
| `http://127.0.0.1:4382` | Portal corregido del laboratorio |

El [prototipo privado F1](PUERTO_UMBRAL_F1_2026_10_26.md) permanece separado.
Publicar el repositorio en GitHub no sirve el backend local en Internet ni
conecta el prototipo alojado con la VM.

## Actualizar y compilar

Cerrar primero la sesión propia desde su terminal y esperar la salida de cierre.
Revisar `git status --short`; conservar y revisar cualquier cambio antes de
actualizar. El recorrido observado utilizó `git pull --ff-only` y comprobación
del commit efectivo. No requiere forzar el árbol o borrar evidencias.

Cuando cambie el frontend, la compilación observada en Parrot fue, desde la raíz:

```bash
cd frontend
node node_modules/next/dist/bin/next build --webpack
```

Esperar la salida final, incluidas TypeScript y las rutas generadas. Para F4 no
fue necesario reinstalar Python, cambiar dependencias o modificar `.env`.

## Comprobar y arrancar

La entrada simplificada incorporada el 01/11 utiliza el mismo supervisor:

```bash
python3 webdefensev2.py
```

Equivale al arranque conjunto `structured`, con fuente V2 `corrected`.
Admite `start` explícito, `check`, `install` y `--help`; el comando sin acción
ejecuta `start`. `python3 webdefensev2.py --lab-mode vulnerable` cambia solo
la fuente del laboratorio elegida para V2. En Windows sustituir `python3`
por `py`. No hace falta activar `.p2`, abrir varios procesos manualmente o
volver a instalar por usar esta entrada en una instalación ya preparada.

Para comprobar sin iniciar: `python3 webdefensev2.py check`.
`install` delega en el instalador existente; Docker/Compose se prepara aparte.
Se conservan puertos, logs, bloqueos, comprobaciones y cierre con `Ctrl+C` del
supervisor original. Sin `--enable-manual` no inicia worker; ninguna de estas
entradas ejecuta escenarios, seguimiento o análisis por el mero arranque.

### Activación manual integrada

```bash
python3 webdefensev2.py --enable-manual
```

Esta opción habilita admisión de solicitudes e inicia el ejecutor existente
`pipeline.py --manual-only` en el mismo perfil, modo, origen, rutas y entorno
que Flask. El supervisor espera una respuesta GET local de análisis con
`manual_enabled: true` y `executor: online` antes de dar la consola por lista.
No exige contactar al proveedor para comprobar disponibilidad; si falta la
configuración del proveedor, el botón sigue deshabilitado hasta configurarlo.
No se crean trabajos ni ciclos programados al arrancar. Usar el botón sí
solicita un análisis al proveedor configurado. Las notificaciones siguen apagadas.

`python3 webdefensev2.py check --enable-manual` comprueba ese plan sin iniciar
el ejecutor. `install --enable-manual` se rechaza; la activación corresponde
al arranque. El modo manual del lanzador requiere informes `structured`.

Los logs del ejecutor se guardan en `worker.log`, junto a `flask.log` y
`next.log` en `.local-state/launcher/<ejecución>/`. Su proceso y descendientes
quedan bajo el mismo propietario de procesos: si un componente termina,
se cierra el conjunto propio; `Ctrl+C` también incluye al ejecutor.
Espera al fin del trabajo antes de cerrar. Si se interrumpe un trabajo, se
conservan su estado y recibos para revisión; el preflight no lo reintenta ni
elimina automáticamente para desbloquear el arranque.

Para seguimiento o captura independiente de logs, vuelve a iniciar sin
`--enable-manual`: esas operaciones requieren ejecutor detenido. Para el
análisis manual, la captura la coordina el ejecutor al recibir la solicitud.

Desarrollo revisado con sintaxis/ayuda; las regresiones aisladas preparadas
no se han ejecutado. Después, el propietario aporta dos capturas de la entrega
`91a101e`: Consola lista y ejecutor esperando solicitudes, con V2 mostrando
Ejecutor activo, solicitudes manuales habilitadas, Groq configurado y botón
disponible. El último trabajo visible sigue siendo el previo
`f5b674c86799…`, succeeded/finished. Primer arranque del modo manual y
disponibilidad del botón completados según capturas, sin resultado de un
análisis nuevo. No se atribuye por ello validación del proveedor o una parada
del nuevo ejecutor; no se repite el arranque solo para actualizar el acta.

Recepción posterior del 01/11: el propietario aporta Ctrl+C y «Consola detenida»
en la sesión manual. El navegador conserva la última lectura y muestra que no
puede consultar el estado del ejecutor: tras cerrar el backend, esos campos
no son una comprobación en vivo de su actividad. No hace falta repetir la
parada. Para completar el retorno, iniciar `python3 webdefensev2.py` sin la
opción y recargar Resumen; se esperan solicitudes manuales desactivadas,
ejecutor no disponible y botón inactivo. Esa recepción aún está pendiente.

La captura siguiente completa ese retorno: Ejecutor no disponible, solicitudes
manuales desactivadas y botón inactivo, conservando Groq configurado y el
último trabajo anterior. El recorrido básico lectura → manual → parada →
lectura queda completado por capturas en `91a101e`; no se repite para el acta.
No constituye análisis nuevo, inspección exhaustiva de procesos del host o
ejecución de las regresiones aisladas preparadas.

### Arranque de lectura ya observado

La revisión inicial del nuevo archivo fue estática y de ayuda CLI. Después,
el propietario aporta captura del primer arranque en Parrot con fuente
corregida, direcciones 4381/4380/4382 y Consola lista en 3000; confirma que
ambas apps responden en el navegador. Recorrido de arranque completado a ese
alcance para la entrega `8f65bc7`, sin repetir escenarios o modelo. No se
extrapola a un nuevo cierre con Ctrl+C o al análisis manual.
Los comandos detallados anteriores siguen disponibles:

Desde la raíz, el modo corregido revisado utiliza:

```bash
python3 webdefense.py check --mode structured --with-puerto-umbral --lab-mode corrected
```

`check` comprueba build, entorno, bloqueos/trabajos, puertos y preparación de
los contenedores propios. No inicia servicios. «Preparado» significa que no
encontró los bloqueadores previstos, dentro del alcance de ese preflight.

El arranque conjunto es:

```bash
python3 webdefense.py start --mode structured --with-puerto-umbral --lab-mode corrected
```

La terminal supervisa Flask, Next, el panel y los servicios propios del
laboratorio. Debe quedar abierta. Construye las dos imágenes con Docker y utiliza
el Compose instalado para su ciclo de vida. No ejecuta escenarios, corpus,
worker (sin `--enable-manual`), análisis, notificaciones o seguimiento por el mero arranque.

`--lab-mode` elige la pasarela que lee V2. Cambiar el selector vulnerable/corregido
en el panel 4381 no cambia esa fuente. El perfil `puerto-umbral` mantiene sus
logs, snapshots, informes y SQLite separados de pilot/legacy y de DVWA.

## Lectura, captura y seguimiento

### Por qué «Iniciar análisis» puede estar desactivado

El arranque conjunto sin `--enable-manual` mantiene lectura: el plan usa
`ANALYSIS_MANUAL_ENABLED=0` y el supervisor no inicia el worker. Configurar el
proveedor no cambia esas dos condiciones. El botón solo se habilita cuando
la admisión manual está habilitada, el proveedor está listo, el ejecutor
figura online y no hay un trabajo en cola o ejecución. No se activa por esperar.

La activación explícita de componentes de análisis tiene su
[procedimiento separado](INSTALACION_AUTOALOJADA.md#pasar-de-lectura-a-análisis-manual).
Esa receta histórica usa el perfil `pilot`; no se debe copiar como si fuera
la activación integrada de Puerto Umbral. La opción conjunta desarrollada el
01/11 es `python3 webdefensev2.py --enable-manual`, descrita arriba. Su
comprobación operativa aún está pendiente; no se ejecuta un análisis por esta
explicación. Se conserva el análisis único anterior y no se repite para
comprobar el botón.

### Fuente local y seguimiento

En Actividad, **Actualizar estado de fuente** lee los metadatos locales.
**Capturar log de Puerto Umbral** solicita una captura manual del gateway
seleccionado, sin analizarla. La captura manual requiere seguimiento detenido
y ausencia de operaciones incompatibles.

| Campo o estado | Lectura correcta |
| --- | --- |
| Fecha de captura | Momento de creación del snapshot mostrado |
| Última lectura válida | Última consulta correcta del origen; puede avanzar sin crear snapshot |
| Snapshot y SHA-256 | Referencia de evidencia; mostrar el hash no verifica por sí solo todos sus bytes |
| Captura antigua | Evidencia conservada con antigüedad; no implica fuente vacía |
| Modo cambiado | El snapshot anterior pertenece a otra selección; no se presenta como una captura nueva |
| Error o desajuste | Revisar la fuente; conservar la evidencia anterior, sin interpretar ausencia de eventos |

El estado de salud del informe es independiente de la clave del proveedor.
El selector actualizado devuelve `missing` cuando no hay puntero de informe
actual: no equivale a un fallo de Groq. Un puntero existente que no se puede
validar, contenido incompleto, hashes distintos o rutas enlazadas siguen siendo
`error`. Este ajuste no crea informes ni utiliza una publicación antigua como
sustituto. La consola puede seguir mostrando fuentes incompletas hasta disponer
tanto del log como del informe; `missing` es distinto de `error` en la API.

Los textos de eventos de Amenazas y Reportes identifican la fuente de arranque.
El propietario confirma el 29/10 la corrección de Puerto Umbral en esas vistas.

El seguimiento necesita **Iniciar seguimiento**. El intervalo permitido es de
5–60 segundos y la duración de 1–30 minutos; la interfaz ofrece sesiones de
5, 15 y 30 minutos. La ronda F4 utilizó cinco segundos y cinco minutos.
Sin cambios de bytes/procedencia se conserva el snapshot, con última lectura
y contadores actualizados. No se crea un análisis por cada lectura.

**Pausar** requiere esperar a «Pausado». Conserva los bloqueos y la duración
total sigue contando. **Reanudar** continúa la sesión sin ampliar su fin.
**Detener seguimiento** requiere esperar a «Detenido». Un estado de pausa o
parada solicitada todavía no confirma su finalización. Después de detener, el
botón **Actualizar seguimiento** permite revisar nuevamente los valores.

La sesión continúa al cambiar de vista o cerrar la pestaña hasta su parada,
vencimiento, error o cierre del proceso propietario. Para capturar manualmente,
analizar, respaldar o cambiar la configuración del motor, detener el seguimiento;
una pausa conserva los bloqueos de ciclo y motor.

## Cierre y reapertura

Ctrl+C en la terminal del lanzador solicita cerrar sus procesos y servicios
propios. Esperar a que regrese el prompt y revisar cualquier aviso de parada
no confirmada. Se conservan evidencias y volúmenes; DVWA/Mailpit siguen siendo
servicios independientes. La ronda F4 observó «Consola detenida» y un preflight
posterior correcto.

Al cerrar la API, el navegador puede mostrar un error de red junto con el último
estado recibido. Esa pantalla no es una observación actual del hilo. Al volver
a abrir V2, una sesión cortada puede aparecer como **Interrumpida**. No se
reanuda automáticamente; el recorrido F4 comprobó contadores y lectura estables.

No se requiere iniciar otra sesión para eliminar ese estado histórico. Una nueva
sesión necesita una acción explícita. La comprobación de todos los procesos o
interrupciones posibles queda fuera de lo demostrado por esas capturas.

## Conservación y recuperación

| Ubicación | Contenido |
| --- | --- |
| `.local-state/puerto-umbral/` en la raíz | Capturas V2, snapshots/recibos, seguimiento, publicaciones y SQLite del perfil |
| `.local-state/puerto-umbral/manual-validation.json` | Resumen de la autorización única y su resultado; no borrar para permitir otro análisis |
| `labs/puerto_umbral/.local-state/f2/` | Recibos funcionales, snapshots del laboratorio y registros de preparación |
| `.local-state/launcher/` | Salidas del lanzador, compilación de preparación y parada |
| Volúmenes/imágenes Docker | Estado y artefactos propios del laboratorio; conservación separada |
| `.env` y configuración local | Gestión separada; no publicar o incluir en informes |

Los datos operativos quedan fuera de Git. El límite de captura es una ventana
de las últimas 1.000 líneas, con publicación de hasta 1 MiB. La cuota de estado
y el espacio disponible pueden detener nuevas capturas; no se borran originales
automáticamente para continuar. El historial completo no está garantizado.

El script [backup_operational](../scripts/backup_operational.py) admite
`--profile puerto-umbral`, incorpora los nombres permitidos de snapshots,
seguimiento y, con el ajuste local del 29/10, `manual-validation.json`. Produce
un manifiesto, ZIP y comprobación de restauración. El restaurador utiliza la
misma lista permitida, por lo que reconoce ese recibo sin admitir otros JSON
arbitrarios. Requiere
detener las operaciones activas; comprobar `verified` y `missing` antes de
atribuir cobertura. En la revisión documental inicial F5 no se ejecutó; el
recorrido posterior del 29/10 se describe a continuación.

La ampliación no añade lecturas de `.env` ni claves. Conserva el recibo como
archivo de evidencia, sin reutilizarlo para arrancar sesiones o repetir el
análisis. Copias antiguas no ganan ese archivo retroactivamente. La cobertura
solo puede atribuirse a archivos incluidos en un manifiesto concreto.

Ese respaldo de aplicación **no incluye** los recibos del laboratorio bajo
`labs/`, los logs completos del lanzador, `.env`, imágenes Docker o sus volúmenes.
Esas piezas requieren conservación separada antes de cambiarlas. Una copia de
aplicación no constituye una recuperación completa de la VM.

El script [restore_operational](../scripts/restore_operational.py) recibe el
directorio exacto de copia mediante `--backup` y recupera en un árbol nuevo de
`.local-state/recovery/`. No reemplaza el estado vivo ni reactiva sesiones. Su
resultado debe revisarse antes de una promoción posterior con alcance propio.
Esta guía no ordena una restauración o sustitución de datos ahora.

El 29/10, el propietario aportó una copia de 66 archivos con `verified: true`
y `missing: []`, y una recuperación independiente de los mismos 66 archivos
en un directorio nuevo. La salida de recuperación verifica la base de datos,
un trabajo exitoso, ninguna entrega y la publicación estructurada del análisis
único observado. La comprobación básica de recuperación aislada del perfil
queda completada dentro del alcance de esas capturas. Se conservan la copia,
el árbol recuperado y los originales; no se requiere repetirla. El
[acta](PUERTO_UMBRAL_ANALISIS_ACOTADO_2026_10_27.md) registra los destinos y
límites: no se promovió el estado recuperado a los datos vivos ni se validó una
recuperación completa de la VM.

Si una operación no completa su salida, conservar los archivos y revisar su
estado; no forzar reintentos con borrado de volúmenes, recibos o snapshots.

## Alcance de los resultados

El panel funcional, la captura y el detector tienen evidencias distintas.
Un HTTP 200 puede acompañar un efecto o una respuesta normal. Un HTTP 400/403
puede rechazar una entrada y seguir dejando un indicador observable. La lectura
de una petición en V2 acredita recepción del registro; la clasificación y el
informe requieren un análisis separado. Después de la revisión documental F5
se autorizó y observó [un análisis acotado](PUERTO_UMBRAL_ANALISIS_ACOTADO_2026_10_27.md):
17 líneas, tres llamadas a Groq y publicación visible de cuatro grupos. No se
ha evaluado por ello el corpus completo ni se ha aceptado el MVP.

La ronda básica F4 está completada. La [evaluación F5](PUERTO_UMBRAL_F5_2026_10_27.md)
mantiene los tres fallos históricos, las variantes aplazadas, las métricas del
detector sin medir y la aceptación ampliada pendiente. Los comandos `check-*`
del corpus siguen fuera del recorrido acordado; no se ejecutan automáticamente.

# Puerto Umbral y V2 — preparación de actualización y revisión manual en Parrot

Fecha: 26/10/2026. El propietario autoriza compilación, commit/push del proyecto
y revisión manual posterior desde la VM. Se mantiene la restricción de no
ejecutar suites de escenarios o análisis LLM automáticamente.

## Recepción vigente F6/F7 — 29/10/2026

El propietario autoriza el paso 3 tras publicar `cc363af`. Sus capturas muestran
`HEAD -> main`, `origin/main` y `origin/HEAD` en ese commit, y compilación del
frontend con `next build --webpack`: Next.js 16.3.8, compilación/TypeScript
correctos, 4/4 páginas estáticas, trazas y optimización finalizadas. El paso 3
queda completado según las capturas; el agente no ejecutó comandos en la VM.

La actualización se hizo sin solicitar reinstalar dependencias. Los comandos
de instalación y pruebas de la cronología inferior pertenecen a su preparación
histórica: no son pasos pendientes que deban repetirse ahora. La siguiente área
es arranque y disponibilidad de V2/laboratorio; todavía no se atribuye arranque
de los 14 servicios, ejecución de casos o aceptación funcional F6/F7. Véase el
[acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md). Esta recepción es local posterior
a `cc363af`, sin commit/push adicional todavía.

Recepción posterior: el lanzador informa «Consola lista» y las cuatro URLs;
el panel se muestra accesible e informa perímetro de 14 contenedores. Este
envío no contiene Actividad V2 ni resultados de escenarios nuevos. El modo
vulnerable seleccionado en el panel no modifica la fuente V2 `corrected`.
La petición posterior de autoría en cabecera se prepara en HTML/CSS local,
con los datos y enlaces de V2; todavía requiere distribución a la VM y revisión
visual. No se atribuye ese cambio a las capturas previas a su implementación.

El propietario autoriza después publicar esta autoría y las actas pendientes.
Esta entrega solo cambia HTML/CSS del panel y documentación: tras el commit/push,
actualizar desde la raíz con `git pull --ff-only` y recargar 4381 con
Ctrl+Shift+R. El controlador lee esos archivos directamente; no hace falta
recompilar Next o recrear imágenes por este cambio. Si `git status --short`
muestra cambios locales, conservarlos y revisarlos antes de actualizar, sin
usar reset. La recepción visual actualizada queda pendiente.

Las capturas siguientes confirman autoría visible y Actividad V2 accesible.
La fuente muestra el snapshot corregido histórico de 17 líneas como antiguo;
la auditoría avanzada indica que aún no hay datos, sin error visible. Con ello
finaliza el bloque básico de disponibilidad y pantallas; no se solicita una
captura nueva, ejecución de escenarios o repetición del análisis por ese estado.
Las pruebas funcionales y la evaluación del detector continúan pendientes.
Posteriormente se autoriza un control normal manual F6: Cargas, corregido,
variante 1. Las capturas muestran HTTP 200 para `own-1`, propietario correcto,
3 peticiones y 3 líneas correlacionadas. La auditoría del panel y V2 comparten
ejecución `10fea5f6cbef9d88320ca767cc11e0b4` y 2 eventos; V2 muestra cero
coincidencias de esas reglas. Ese caso y su lectura quedan completados, sin
extender el resultado a los demás casos o a evaluación LLM. La copia de esa
auditoría en V2 todavía no está acreditada; no se pide repetir el caso.
El propietario autoriza después conservar la auditoría y consultar su recibo.
Las capturas muestran confirmación de copia y `current.json` con la misma
ejecución, 2 eventos, modo corregido, estado completado e identificador
`ed70066797f1f68f7df55b7ecb18247d`; análisis y notificaciones están en `false`.
Ese paso queda completado según las capturas, sin una nueva ejecución del caso,
modelo o respaldo/restauración. El acta F6/F7 conserva ambos hashes reportados;
su lectura no equivale a recalcular los bytes de los archivos de la VM.

## Recepción del bloque normal F6 del 30/10

El propietario retoma manualmente Bitácora, Preferencias, Baliza y Atraque,
corregido/Uso normal/variante 1, aportando resultado y auditoría de V2 para cada
uno. Los cuatro muestran uso normal completado, HTTP 200, mismo identificador
en panel/V2 y mensaje de copia conservada sin análisis. Se observan 3, 2, 2 y
4 eventos respectivamente. El bloque queda completado a ese alcance; Cargas
del 29/10 y su copia ya estaban completados y no se repitieron.

El [acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md) conserva identidades, hashes
mostrados, conteos y límites. No se han ejecutado suites, llamadas LLM o acciones
de VM por el agente. Las otras variantes/tipos, pruebas de navegador,
aislamiento/regresión y recuperación de auditorías nuevas siguen pendientes;
no es aceptación de F6/F7 completas. Las actas de recepción siguen locales,
posteriores a `5bf154a`, sin nuevo commit/push.

El propietario autoriza posteriormente publicar esas cinco actas con
`[skip ci]`. La entrega documental se identifica por el commit que incorpora
esta nota; no cambia el runtime. Para recibirla en Parrot, desde la raíz:

```bash
git status --short
git pull --ff-only
git log -1 --oneline
```

Si hay cambios locales, conservarlos y revisarlos antes del pull. Esta entrega
no requiere reinstalar, recompilar el frontend o reiniciar la aplicación, ni
repetir escenarios, capturas o análisis. La recepción de actas en la VM no se
presume hasta su confirmación; publicar no cierra F6/F7 o el MVP.

## Contexto y preparación anteriores

**Estado posterior:** la ronda manual se da por finalizada por decisión del
propietario. Los pasos no ejecutados que aparecen en esta cronología quedan
aplazados; no son nuevas solicitudes de prueba. El [estado consolidado](PUERTO_UMBRAL_ESTADO_ACTUAL_2026_10_26.md)
resume lo observado y los pendientes, sin cerrar F2/F3 ni acreditar detección
del analizador. No se requieren más capturas para este cierre.

El [desarrollo F4 del 27/10](PUERTO_UMBRAL_F4_2026_10_27.md) añade controles de
seguimiento. El propietario autoriza después publicar y revisar F4 de forma
guiada, usando solo los logs existentes. La actualización efectiva de la VM y
sus ciclos se acreditarán por separado; no cambia la cronología anterior ni
reabre sus escenarios aplazados.

## Qué cambia al actualizar

La distribución portable en [labs/puerto_umbral](../labs/puerto_umbral/README.md)
permite obtener las dos aplicaciones con un único `git pull`. El Site privado
F1 sigue separado y conserva su publicación. No se crea otro repositorio ni se
copian al código credenciales, historial Git, imágenes, entornos o datos locales.

El nuevo comando explícito es:

```bash
python3 webdefense.py start --mode structured --with-puerto-umbral
```

Arranca Flask, Next, el panel de Puerto Umbral y sus servicios Docker propios,
con los cinco puertos solo en loopback. Prepara y comprueba disponibilidad; no
inicia escenarios, corpus, worker, análisis del modelo, avisos o monitorización
periódica. El arranque anterior sin esa opción conserva su alcance de V2/pilot.

El laboratorio admite el Compose realmente instalado: `docker compose` cuando
está disponible o el ejecutable `docker-compose` usado anteriormente en Parrot.
No instala otro cliente ni cambia el contexto de Docker por sí solo.
La preparación construye las imágenes con `docker build` y reserva Compose para
configuración y arranque con `--no-build`; no invoca `compose build`.

Ctrl+C debe cerrar los procesos iniciados por la terminal y solicitar la parada
de los servicios propios Puerto Umbral. Se conservan sus evidencias y volúmenes.
No se ejecuta `down --volumes` ni se detienen servicios DVWA/Mailpit existentes.
Una sesión Puerto Umbral previa debe cerrarse antes de asumir una nueva.

## Compilación de preparación

El frontend se compiló localmente en Windows con Webpack y terminó la comprobación
de tipos TypeScript. Turbopack falló al iniciar su proceso PostCSS incluso fuera
del sandbox; ese intento no se cuenta como compilación correcta. No se cambiaron
dependencias para resolverlo. La compilación local no acredita compilación ni
arranque en Parrot. El lanzador conjunto y el backend siguen pendientes de esa
revisión manual en la VM.
La sintaxis de los 16 archivos Python nuevos/modificados se compiló en memoria
con el intérprete de `.p2`, sin importar ni ejecutar los módulos de aplicación;
los dos JSON del bloque se leyeron correctamente. No se ejecutaron suites ni escenarios.

## Pasos en la VM: no ejecutados por el agente

Desde el clon V2 en Parrot, primero cerrar sus consolas/worker propios si quedan
abiertos y comprobar que `git status --short` no muestre cambios que puedan
perderse. Si aparecen cambios, conservarlos antes de actualizar; no usar reset.

Antes del `pull`, crear una copia nueva de los datos operativos con el intérprete
de la instalación existente:

```bash
.p2/bin/python -B scripts/backup_operational.py --profile all
```

Conservar la ruta devuelta y confirmar `verified: true`. Es un respaldo de la
aplicación y su recuperación aislada; no copia el volumen DB ni correo de DVWA.
El laboratorio existente no se recrea como parte de este procedimiento.

Después de que el commit autorizado esté publicado y la copia esté verificada:

```bash
git pull --ff-only
python3 webdefense.py install
python3 webdefense.py start --mode structured --with-puerto-umbral
```

El instalador conserva un `.env` existente. No es necesario mostrar su contenido,
copiar claves al chat ni abrir el analizador para comprobar las pantallas.

Si la compilación del frontend en ese equipo presenta el mismo fallo de
Turbopack, conservar el diagnóstico y compilar solo la interfaz con la alternativa
que se usó en Windows, desde `frontend`:

```bash
node node_modules/next/dist/bin/next build --webpack
```

No se presupone que vaya a fallar en Linux. Un error de instalación previo a la
compilación requiere revisar su causa antes de continuar.

## Revisión manual de las páginas

Abrir estas direcciones en el navegador **dentro de Parrot**:

| Dirección | Revisión |
| --- | --- |
| `http://127.0.0.1:3000` | Consola V2 y vista Actividad |
| `http://127.0.0.1:4381` | Panel local de Puerto Umbral |
| `http://127.0.0.1:4380` | Portal del modo vulnerable |
| `http://127.0.0.1:4382` | Portal del modo corregido |

Primero revisar navegación normal y estado de los servicios. Cambiar una
selección no inicia un escenario. La captura solo se solicita desde el botón de
Actividad; esa acción no llama al modelo. Los escenarios se revisarán después
mediante acciones manuales explícitas del propietario, conservando cada recibo.

La primera revisión debe confirmar puertos y pantallas antes de extraer
conclusiones sobre efectos de escenarios o detección. Los resultados iniciales
42/45 y los pendientes F2/F3 se conservan en
[su registro](PUERTO_UMBRAL_F2_F3_2026_10_26.md).

No marcar Parrot actualizado ni los servicios arrancados hasta recibir su salida
real. La accesibilidad desde otro equipo no se habilita por este procedimiento.

## Evidencia a recoger al terminar

- Commit efectivo mostrado por `git rev-parse --short HEAD` en la VM.
- Resultado de instalación/compilación y mensajes de consola lista.
- Confirmación de acceso a V2 y al panel Puerto Umbral en el navegador de la VM.
- Estado de fuente y, solo si se solicita, recibo de captura manual.
- Salida de cierre con Ctrl+C y cualquier aviso de parada no confirmada.

No se atribuyen a esta publicación pruebas de CI, cierre de F2/F3 ni seguridad
general. El commit de desarrollo se prepara con exclusión de CI para respetar
la revisión manual acordada. El estado final de publicación se informará tras
comprobar el push; esta guía no lo presume.

## Diagnóstico de la primera preparación en Parrot

La captura del propietario acredita `existing_preserved` e instalación completada.
El arranque conjunto se detuvo durante la construcción con el error
`compose build requires buildx 0.17.0 or later`. La carpeta del laboratorio sí
está presente: el traceback ejecuta `labs/puerto_umbral/labctl.py` y su controlador.
No se atribuye el fallo a una actualización incompleta ni se acredita el arranque
de Flask, Next o del laboratorio por esa salida.

Se sustituye la compilación mediante Compose por dos invocaciones secuenciales
de Docker, una por imagen compartida. Se conservan Dockerfiles, digests, puertos,
restricciones y `up --no-build`. No se instala ni actualiza Buildx automáticamente,
ni se fuerza un constructor alternativo por variables de entorno. La operación
real sigue pendiente de repetir el arranque manual en Parrot.

Los resultados completos de cada construcción quedan en
`labs/puerto_umbral/.local-state/f2/setup-history/build-*.json`, separados del
código versionado. El log del lanzador indica su ruta si la construcción falla.
El identificador del primer log se localizó por búsqueda, evitando volver a
transcribirlo desde una captura. No hace falta repetir el instalador para aplicar
esta corrección Python: tras el `pull`, volver a ejecutar solo el arranque conjunto.

## Confirmación posterior y siguiente revisión

El propietario confirma que tiene todos los servicios abiertos en sus direcciones
correspondientes dentro de Parrot. Se registra como confirmación de arranque y
acceso del usuario, sin captura adicional de IDs, versión efectiva o estado de
contenedores. No acredita todavía captura V2, efectos de escenarios ni análisis.

El siguiente paso será una solicitud normal de mercancías y su captura manual:

1. En el panel 4381, seleccionar el escenario de mercancías/SQL, modo vulnerable,
   y pulsar «Restablecer escenario». Esto prepara esa ejecución sin lanzar un intento.
2. Dentro de los siguientes 30 segundos, en el portal 4380, buscar `Asteria` en
   Mercancías mediante «Consultar». Es una búsqueda normal sobre datos ficticios.
3. En Actividad de V2, pulsar «Capturar log de Puerto Umbral» y luego el control
   general «Actualizar» para releer la actividad.
4. Comprobar modo vulnerable, fecha de captura reciente, líneas disponibles,
   referencia/hash y la petición de mercancías con HTTP 200. Conservar el resultado.

Esta comprobación se realizará manualmente por el propietario. No se ejecutó
por el agente al redactar estas instrucciones. Si el portal responde 410 por
expiración, restablecer solo ese escenario antes de repetir la búsqueda normal.
La evaluación de escenarios educativos y cualquier uso del modelo siguen siendo
pasos separados; no se declaran cerradas F2/F3 por tener las páginas abiertas.

## Primera lectura de actividad acreditada

La captura de Actividad aportada por el propietario muestra la línea Apache
`GET /mercancias?q=Asteria HTTP/1.1` con HTTP 200, 125 bytes y fecha del registro
26/10/2026 18:31:24 +0000. Acredita la recepción y visualización en V2 de esa
solicitud normal realizada en Puerto Umbral. La IP que figura es la observada
en el registro; no se atribuye a un atacante.

La imagen no muestra el panel de metadatos, el hash o el identificador del
snapshot, ni resultados del analizador. Por tanto, no acredita todavía la
integridad completa de una generación, detección de un escenario o un análisis
del modelo. La vista sigue siendo una ventana limitada del log.

La siguiente revisión propuesta al propietario es una única ejecución manual
del escenario SQL, modo vulnerable, tipo intento y variante 1, desde el panel
4381. Se revisarán respuesta real y recibo antes de comparar con el modo
corregido. Esa acción no se ha ejecutado por el agente ni se presume realizada.
La selección del modo en Puerto Umbral no cambia el modo de captura del perfil
V2: mientras el lanzador use su valor predeterminado, capturará la pasarela
vulnerable. La comparación posterior debe conservar esa distinción.

## Caso SQL vulnerable observado en Parrot

Dos capturas posteriores del propietario muestran el escenario SQL en modo
`vulnerable`, tipo `attempt`, variante 1, con estado `COMPLETED`. El panel informa
una petición HTTP local real y una línea Apache correlacionada. La respuesta
HTTP 200 incluye el registro ficticio reservado `UM-9000`, con nombre
`SEÑUELO-RESERVADO-UMBRAL`: se acredita el efecto funcional de este caso.

La segunda imagen muestra en Actividad de V2 la misma ruta de mercancías y
consulta codificada, registrada el 26/10/2026 a las 18:36:15 +0000, con HTTP 200,
230 bytes y un identificador `rid` presente. La fuente figura como `available`,
con modificación a las 19:36:40 de Madrid. Acredita la recepción y visualización
de esa petición en V2. El panel del ejecutor indica «V2 consultado: no», coherente
con una ejecución y una captura independientes.

Las imágenes no contienen un resultado del analizador ni los bytes del recibo
JSON exportado o del snapshot de captura para verificar sus hashes. No se
atribuye detección por el modelo ni cierre de F2/F3. El agente solo documentó la
evidencia aportada, sin ejecutar escenarios, suites o llamadas al modelo.

El siguiente paso manual es exportar el recibo vulnerable y comparar el mismo
escenario, tipo y variante en modo **Corregido** desde el panel 4381. Se espera
que la respuesta no incluya `UM-9000`; HTTP 200 por sí solo no determina el
resultado. Conservar también el recibo corregido. Cambiar ese selector no cambia
la fuente configurada en V2: la captura del gateway corregido requiere seleccionar
ese modo en el perfil del lanzador, como paso separado posterior.

## Comparación SQL corregida observada en Parrot

La siguiente captura del propietario muestra el mismo caso, modo `corrected`,
tipo `attempt`, variante 1, estado `COMPLETED`, una petición HTTP local real y
una línea Apache correlacionada. La respuesta HTTP 200 contiene `{"cargo": []}`,
sin `UM-9000`, y el panel indica que el control impidió el efecto en esta prueba.
Se acredita la diferencia funcional entre ambos modos para esta variante SQL.
No se generaliza el resultado al resto del corpus o a todas las protecciones.

«V2 consultado: no» sigue siendo coherente con la separación del ejecutor y
el consumidor del log. Esta imagen no acredita la recepción del log corregido
en V2 ni un análisis del modelo. Tampoco acredita la exportación del recibo;
conviene descargarlo antes de cerrar el panel y su proceso.

Para revisar manualmente esa fuente en V2, cerrar el lanzador con Ctrl+C y
esperar a que confirme su parada. Desde la raíz del repositorio en Parrot:

```bash
python3 webdefense.py start --mode structured --with-puerto-umbral --lab-mode corrected
```

En Actividad, pulsar «Capturar log de Puerto Umbral» y después «Actualizar».
Comprobar que el panel de fuente identifica el modo corregido y revisar su
snapshot/hash/fecha junto con la línea del caso. El gateway conserva normalmente
su log al detenerse y arrancar; la preparación además guarda los logs previos
en `setup-history`. Si la línea no está en la ventana actual, no presumir su
presencia ni repetir el caso automáticamente: revisar primero la captura y
sus metadatos. El cambio de perfil no ejecuta escenarios ni llama al modelo.

Esta transición queda propuesta para ejecución manual del propietario; el agente
solo revisó el código del lanzador y actualizó la documentación local. F2/F3
siguen abiertas para las comprobaciones pendientes.

## Fuente corregida visible en V2

La captura posterior del propietario muestra «Captura disponible · Modo
corregido», siete líneas y última captura del 26/10/2026 a las 19:44:21 de Madrid.
El panel presenta un identificador de snapshot y un SHA-256. Su estado indica
que el origen estaba en ejecución cuando se capturó; no comprueba su estado
actual.

Actividad incluye la petición SQL del modo corregido a las 18:40:42 +0000,
HTTP 200, 13 bytes y `rid` presente, coherente con la respuesta `cargo` vacía
observada en el panel. Queda acreditada visualmente la recepción del log de
este caso en V2, además de la lectura anterior del modo vulnerable. No se han
recibido los archivos de la VM para recalcular el hash, ni resultados del
analizador. Las fases completas F2/F3 mantienen sus pendientes.

El siguiente control manual propuesto es restablecer únicamente el escenario
SQL en modo corregido desde el panel 4381 y, dentro de los siguientes 30 segundos,
buscar `Asteria` en Mercancías del portal 4382. Se esperan las mercancías públicas
`UM-1284` y `UM-1287`, sin `UM-9000`. Esto comprobará que el modo corregido
conserva la búsqueda normal, además de impedir el efecto de la variante revisada.
Después se podrá capturar y actualizar Actividad para ver la solicitud normal.
No se presume realizado este control por proponerlo; el agente no ha ejecutado
pruebas automáticas, escenarios ni llamadas al modelo.

## Búsqueda normal conservada en el modo corregido

Las dos capturas siguientes del propietario muestran el portal 4382 en
`/mercancias?q=Asteria`, con los registros públicos `UM-1284` y `UM-1287`, sin
el señuelo reservado `UM-9000`. La búsqueda normal sigue funcionando en el modo
corregido para esta entrada.

V2 muestra modo corregido, doce líneas, snapshot y SHA-256 visibles, con captura
del 26/10/2026 a las 19:49:23 de Madrid. Actividad contiene la búsqueda `Asteria`
a las 18:49:00 +0000, HTTP 200 y 125 bytes. Quedan observados la diferencia
funcional SQL de la variante 1, el control de uso normal y la recepción de esos
logs. No equivalen a una validación de todo el corpus ni a detección del modelo.

El siguiente caso manual propuesto es **XSS reflejado → Corregido → Intento de
ataque → Variante 1** en el panel 4381. Una sola pulsación de «Ejecutar prueba
real» prepara y ejecuta ese caso; revisar tanto «Resultado observado» como
«Comprobación XSS en navegador». Se espera entrada codificada como texto y
ausencia de confirmación de ejecución. La ausencia de marcador por sí sola no
acredita una protección general: se comparará después con el modo vulnerable.
Exportar el recibo y capturar/actualizar Actividad en V2, cuya fuente permanece
corregida. Esta propuesta no se declara ejecutada. No se han realizado suites,
escenarios ni llamadas al modelo por el agente.

## Recepción del caso XSS y observación de navegador pendiente

La siguiente captura de Actividad muestra dos solicitudes a `/comunicaciones`
el 26/10/2026 a las 18:51:16 y 18:51:17 +0000, ambas con HTTP 200 y 431 bytes.
Comparten la referencia `_request`; la primera tiene `rid` y la segunda muestra
`rid:-`. Es coherente con la petición del ejecutor seguida de la carga del iframe:
el controlador asigna un encabezado de correlación a su petición y el navegador
carga después la misma URL en el iframe. No se atribuyen dos ejecuciones manuales
por observar dos solicitudes. La fuente estaba configurada previamente como
corregida, pero esta imagen no muestra de nuevo sus metadatos de modo.

El log acredita que V2 recibió las solicitudes, sin mostrar el cuerpo de respuesta
ni la observación del navegador. HTTP 200 no confirma codificación o ejecución
de JavaScript. Falta revisar «Resultado observado» y «Comprobación XSS en
navegador» del caso existente en el panel 4381. Puede recuperarse mediante
«Consultar» en el historial, sin volver a ejecutar la prueba. No declarar bloqueo,
ejecución confirmada, detección del analizador o cierre del caso con esta imagen.
El agente solo revisó código y registró la evidencia; no ejecutó escenarios,
suites o llamadas al modelo.

## Respuesta XSS corregida codificada

La imagen posterior del resultado muestra modo `corrected`, tipo `attempt`,
variante 1, estado `COMPLETED`, HTTP 200, una petición del ejecutor y una línea
Apache correlacionada. La referencia de ejecución coincide con `_request`
en las dos solicitudes mostradas anteriormente en Actividad. El panel indica
«Entrada codificada como texto en la respuesta» y el cuerpo HTML presenta
entidades en el contenido reflejado. Se acredita visualmente esa codificación
en la respuesta del caso corregido y su recepción previa en V2.

La imagen termina antes de «Comprobación XSS en navegador», por lo que sigue
pendiente revisar esa sección del mismo caso, sin repetirlo. No se declara una
observación de ejecución o ausencia de ejecución en el iframe basándose solo
en el cuerpo presentado como texto. La exportación del recibo y el análisis
de V2 tampoco quedan acreditados por esta imagen. No se ejecutaron escenarios,
suites o llamadas al modelo por el agente; solo se actualizó el registro local.

La siguiente imagen muestra ya el iframe «Comprobación XSS en navegador»:
«Comunicaciones · escenario local» presenta la entrada literalmente como texto.
Es coherente con la codificación observada en la respuesta corregida. El recorte
no incluye el mensaje final `browser-result`; no se afirma un valor de esa
bandera ni protección general. Esta observación visual permite avanzar a la
comparación sin repetir el caso corregido ni solicitar otro recorte del mismo.

El siguiente paso propuesto es conservar el recibo corregido y ejecutar una vez,
manualmente en el panel 4381, **XSS reflejado → Vulnerable → Intento de ataque
→ Variante 1**. Revisar «Resultado observado» y el mensaje de comprobación del
navegador: solo el marcador confirmado del iframe acredita ejecución, no la
mera reflexión HTTP. Exportar después el recibo vulnerable. La fuente V2 sigue
configurada como corregida; la captura del log vulnerable se revisará después
de cambiar el perfil. No se presupone realizada esa comparación ni se han
ejecutado escenarios, suites o llamadas al modelo por el agente.

## Ejecución XSS vulnerable confirmada en navegador

Las dos capturas posteriores muestran modo `vulnerable`, tipo `attempt`,
variante 1, estado `COMPLETED` y el mensaje «Ejecución de JavaScript confirmada
en el navegador». El panel informa HTTP 200, una petición del ejecutor y dos
líneas Apache correlacionadas. El cuerpo presenta la entrada sin codificar;
el iframe muestra la página de Comunicaciones sin la entrada literal que era
visible en el modo corregido. La confirmación del marcador en el panel es la
evidencia de ejecución, no el aspecto vacío del iframe.

Queda observada la diferencia funcional de esta variante XSS: codificación y
representación literal en el modo corregido, frente a ejecución confirmada en
el vulnerable. No se generaliza al resto de variantes ni se cierra F2/F3.
«V2 consultado: no» continúa separando el ejecutor de la captura y el análisis.
Estas imágenes no acreditan todavía recepción de este caso vulnerable en V2
ni resultados del analizador o exportación del recibo.

El siguiente paso manual es exportar el recibo antes de cerrar el panel y detener
el lanzador con Ctrl+C, esperando confirmación. Arrancar desde la raíz de V2:

```bash
python3 webdefense.py start --mode structured --with-puerto-umbral --lab-mode vulnerable
```

En Actividad, capturar el log de Puerto Umbral y actualizar la vista. Revisar
modo vulnerable, snapshot/fecha/hash y las solicitudes a `/comunicaciones` del
caso ya realizado. No es necesario volver a ejecutar el escenario. Si la línea
no figura en la ventana disponible, revisar primero la fuente y sus metadatos.
Esta captura queda pendiente del propietario; el agente solo registra las
imágenes, sin suites, escenarios, operaciones de VM o llamadas al modelo.

## Recepción XSS vulnerable visible en V2

La captura posterior de Actividad muestra las dos solicitudes a `/comunicaciones`
del 26/10/2026 a las 18:54:58 y 18:54:59 +0000, ambas con HTTP 200 y 379 bytes.
La referencia `_request` coincide con la ejecución del panel que confirmó
JavaScript en el navegador. La primera línea contiene `rid`; la segunda indica
`rid:-`, coherente con la petición del ejecutor y la carga del iframe. La fuente
figura como `available`, con modificación a las 19:57:15 de Madrid. Este recorte
no muestra los metadatos superiores de modo/snapshot/hash.

Queda observada la recepción en V2 de este caso vulnerable, además del corregido
anterior. Se han comparado manualmente la variante 1 de SQL y XSS, con sus
límites registrados; no todo el corpus ni las fases completas. El log no
constituye un resultado de detección del analizador.

El siguiente caso manual propuesto, manteniendo la fuente vulnerable actual,
es **Path traversal → Vulnerable → Intento de ataque → Variante 1** desde el
panel 4381. Ejecutar una sola vez y revisar si la respuesta contiene el marcador
ficticio `PU_RESERVED_FIXTURE_20261026`, correspondiente al documento señuelo
del laboratorio. Exportar el recibo y capturar/actualizar Actividad para revisar
la solicitud a `/archivo`. Después se comparará el modo corregido. Esta revisión
queda pendiente del propietario; el agente solo consultó código y registró las
capturas, sin ejecutar escenarios, suites o llamadas al modelo.

## Lectura del documento señuelo en el modo vulnerable

La siguiente captura de Actividad muestra una solicitud a `/archivo` del
26/10/2026 a las 18:59:07 +0000, HTTP 200, 125 bytes y `rid` presente. La fuente
figura como `available`, con modificación a las 19:59:41 de Madrid. Esa imagen
por sí sola acredita recepción del log, no el contenido devuelto.

La imagen posterior del resultado completa la observación: **Path traversal**,
modo `vulnerable`, tipo `attempt`, variante 1, estado `COMPLETED`, una petición
HTTP local real y una línea Apache correlacionada. La respuesta HTTP 200 muestra
`PU_RESERVED_FIXTURE_20261026` y el texto del documento señuelo ficticio fuera
de la carpeta pública. Quedan observados el efecto funcional de esta variante
y su recepción en V2. No se atribuye detección del analizador, exportación del
recibo o cierre de las fases completas.

El siguiente paso propuesto es exportar el recibo vulnerable y comparar una vez
el mismo escenario, tipo y variante en modo **Corregido** desde el panel 4381.
Según el código actual se espera HTTP 403 con `document_not_authorized`, sin el
marcador reservado. La fuente V2 permanece vulnerable; la recepción del modo
corregido requiere cambiar el perfil como paso separado posterior. No se declara
ejecutada esa comparación. El agente solo consultó el código y registró las
capturas, sin escenarios, suites, operaciones de VM o llamadas al modelo.

## Path traversal rechazado en el modo corregido

La captura posterior muestra modo `corrected`, tipo `attempt`, variante 1,
estado `COMPLETED`, una petición del ejecutor y una línea Apache correlacionada.
La respuesta es HTTP 403 con `{"error": "document_not_authorized"}`, sin el
marcador reservado. El panel indica que el control impidió el efecto en esta
prueba. Queda observada la diferencia funcional de esta variante: el modo
vulnerable devuelve el documento señuelo y el corregido rechaza la solicitud.
No se generaliza a todo el corpus ni a la seguridad global del laboratorio.

Esta imagen aún no acredita la recepción de ese caso corregido en V2, que estaba
configurado para capturar el gateway vulnerable. El siguiente paso manual es
exportar el recibo corregido, detener el lanzador con Ctrl+C y esperar su parada.
Desde la raíz del repositorio, arrancar con:

```bash
python3 webdefense.py start --mode structured --with-puerto-umbral --lab-mode corrected
```

Después, capturar el log de Puerto Umbral en Actividad y actualizar la vista.
Revisar el modo de fuente y la línea de `/archivo` con HTTP 403 del caso ya
ejecutado, sin repetir el escenario. Si no aparece en la ventana, revisar antes
fuente y metadatos. No se presupone realizada esta captura, exportado el recibo
ni ejecutado un análisis. F2/F3 mantienen sus pendientes; el agente solo registra
la evidencia, sin suites, escenarios, operaciones de VM o llamadas al modelo.

## Recepción del rechazo Path traversal en V2

La captura posterior de Actividad muestra la solicitud a `/archivo` del
26/10/2026 a las 19:01:28 +0000, con HTTP 403, 36 bytes y `rid` presente. La fuente
figura como `available`, con modificación a las 20:02:57 de Madrid. La línea es
coherente con el rechazo corregido observado en el panel. El recorte no incluye
los metadatos superiores de modo/snapshot/hash, ni un resultado del analizador.
Queda observada la recepción del caso corregido en V2, además del vulnerable.

Se han comparado manualmente la variante 1 de SQL, XSS y Path traversal en
ambos modos y observado sus solicitudes en V2; no todo el corpus o las fases
completas. El siguiente control manual propuesto es **Path traversal → Corregido
→ Uso normal → Variante 1** en el panel 4381. Corresponde al documento público
`atraque.txt`: se espera HTTP 200 y el texto «PUERTO UMBRAL / PROTOCOLO FICTICIO».
Conservar el recibo y capturar/actualizar Actividad, manteniendo la fuente
corregida actual. Esto comprobará que la restricción no impide leer ese documento
público. No se declara ejecutado el control; el agente solo registra evidencia
y consulta el archivo ficticio del código, sin suites, escenarios o llamadas
al modelo.

## Lectura pública conservada tras corregir Path traversal

Las dos capturas siguientes muestran el control `corrected`, tipo `benign`,
variante 1, estado `COMPLETED` y «Uso normal completado correctamente».
La respuesta HTTP 200 de `/archivo?documento=atraque.txt` contiene el protocolo
ficticio público. El panel informa una petición y una línea Apache correlacionada.
Actividad de V2 muestra la misma solicitud el 26/10/2026 a las 19:05:22 +0000,
HTTP 200, 88 bytes y `rid` presente. Quedan observados el uso normal conservado
y su recepción en V2, además de la comparación del intento en ambos modos.
Las imágenes no acreditan exportación de recibos o resultados del analizador.

El siguiente caso manual propuesto es **Inyección de comandos → Corregido →
Intento de ataque → Variante 1** en el panel 4381. Según el código, esa entrada
se rechaza con HTTP 400 y `invalid_component`. Revisar el resultado de una sola
ejecución, exportar el recibo y capturar/actualizar Actividad para localizar la
solicitud a `/mantenimiento`. La fuente actual ya es corregida. La comparación
vulnerable y la validación de los fallos previos de creación de procesos quedan
pendientes; no se presupone que hayan pasado. El agente solo consultó código
y registró capturas, sin escenarios, suites, operaciones de VM o llamadas al
modelo. No se cierra F2/F3 ni se generaliza al corpus completo.

## Entrada de comandos rechazada en el modo corregido

Las capturas posteriores muestran modo `corrected`, tipo `attempt`, variante 1,
estado `COMPLETED`, una petición del ejecutor y una línea Apache correlacionada.
La respuesta HTTP 400 contiene `{"error": "invalid_component"}`. Actividad de V2
muestra la misma solicitud a `/mantenimiento` el 26/10/2026 a las 19:07:52 +0000,
HTTP 400, 30 bytes y `rid` presente. Se acreditan visualmente el rechazo de esta
entrada y su recepción en V2, no ejecución de comandos o detección del analizador.

El siguiente paso manual propuesto es conservar el recibo corregido y comparar
**Inyección de comandos → Vulnerable → Intento de ataque → Variante 1** desde
el panel 4381, una sola vez. Se espera una salida de identidad con `uid=10001`
del contenedor confinado. La revisión permitirá comprobar también el fallo
anterior `Cannot fork`: si vuelve a aparecer, conservar el resultado en lugar
de presumir que la corrección funciona o repetir la ejecución. Exportar el
recibo y revisar primero el resultado del panel. La fuente V2 sigue corregida;
la recepción vulnerable se comprobará después de cambiar el perfil. El agente
no ejecutó esta comparación, suites, operaciones de VM o llamadas al modelo;
solo registró las imágenes. F2/F3 mantienen sus pendientes.

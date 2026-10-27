# Puerto Umbral — F4: seguimiento local de logs

Fecha: 27/10/2026. Estado: **implementado; ronda operativa básica completada en
Parrot; aceptación ampliada pendiente**.

El propietario autoriza desarrollar F4 después de finalizar la ronda manual.
Se mantiene la restricción de no ejecutar escenarios, suites, capturas reales,
ciclos de seguimiento ni llamadas al modelo. No se solicitan nuevas pruebas o
capturas al propietario por este documento. F2/F3/F5 conservan sus pendientes.

**Autorización posterior del mismo día:** el propietario acepta publicar la
implementación y realizar una validación operativa guiada mediante capturas de
pantalla. Esta autorización permite seguimiento de los logs existentes y sus
controles, sin ejecutar nuevos escenarios, corpus, suites o llamadas al modelo.
La restricción de la ronda anterior se mantiene para esas operaciones. Los pasos
propuestos a continuación no se declaran ejecutados ni aprobados por anticipado.

## Comportamiento implementado

La vista Actividad incorpora **Iniciar seguimiento**, **Pausar**, **Reanudar** y
**Detener seguimiento**, además de la captura manual existente. El perfil
`puerto-umbral` habilita los controles con `LOG_FOLLOW_ENABLED=1`, pero no inicia
la sesión. Abrir una página, leer el estado o arrancar V2 no captura por sí solo.

La sesión admite intervalos entre 5 y 60 segundos y duración entre 60 y 1.800
segundos. Sus valores predeterminados son cinco segundos y treinta minutos;
la interfaz ofrece duraciones de cinco, quince y treinta minutos. Cada intervalo
se espera después de terminar la lectura anterior: no se superponen ciclos ni
se recuperan de golpe los ciclos atrasados. Las pausas cuentan para la duración
total; reanudar no la amplía. El límite se mide con reloj monotónico.

El seguimiento vive en un hilo del proceso Flask, no en la pestaña del navegador.
Cambiar de vista o cerrar la pestaña no lo detiene. Termina mediante parada
explícita, duración agotada, fallo o cierre de su proceso. Nunca se reanuda
automáticamente tras reiniciar Flask o restaurar los archivos de estado.

Los estados son detenido, siguiendo, pausa solicitada, pausado, parada solicitada,
finalizado, error e interrumpido. La interfaz presenta último ciclo válido,
duración de su lectura, fin de sesión, contadores y tipo de cambio observado.
Una pausa o parada solicitada no equivale a una operación ya confirmada.

## Procedencia, idempotencia y límites

- Se utiliza una sola pasarela del modo configurado en el perfil. El selector
  del panel Puerto Umbral no cambia la fuente de V2.
- El capturador comprueba la identidad/configuración y el estado de la pasarela
  antes y después de leer los logs. El seguimiento rechaza una fuente detenida
  o cambiada durante la captura, conservando la evidencia anterior.
- La procedencia incluye ID de contenedor, imagen e instante de arranque.
  Una identidad o reinicio diferente se señala como nueva referencia, aunque
  los bytes del log coincidan.
- Si los bytes y la procedencia no cambian, se reutiliza el snapshot verificado.
  No se crea otra generación ni se modifica su recibo. Solo se actualizan la
  última lectura válida y el checkpoint de seguimiento.
- El estado distingue fecha del snapshot y fecha de última lectura válida.
  Un snapshot antiguo puede seguir siendo la ventana actual sin cambios.
- Una fuente válida vacía puede producir una referencia de cero líneas durante
  el seguimiento. Esto no equivale a «sin incidentes» o un resultado del detector.
- Se conservan las últimas 1.000 líneas solicitadas y el límite de publicación
  de 1 MiB. Se mantienen la cuota de 128 MiB de estado y la comprobación de
  espacio libre; no se borran generaciones para seguir capturando.

Para describir cambios se comparan las ventanas con solapamiento de líneas.
Se distinguen referencia inicial, sin cambios, líneas añadidas, desplazamiento
de ventana, cambio de origen y discontinuidad. Una discontinuidad puede deberse
a rotación, truncado o datos que ya salieron de la ventana; **no se inventa un
offset completo ni el número de eventos perdidos**. El contador de líneas nuevas
es una observación del solapamiento, no una garantía de historial completo ni
identificación única de eventos. Una última línea incompleta detiene la captura.

Los snapshots siguen siendo la evidencia. Los checkpoints y contadores no se
inyectan como etiquetas esperadas en el analizador. No se crea ningún trabajo
de análisis o entrega de notificaciones desde el servicio de seguimiento.

## Exclusión, cancelación y cierre

La sesión posee `.follow.lock`, el bloqueo de ciclo y el bloqueo de motor durante
toda su duración, incluida la pausa. El inicio rechaza un ejecutor activo o
desconocido y trabajos pendientes/en curso. Capturar manualmente, analizar,
guardar configuración del motor o respaldar puede resultar bloqueado hasta
detener la sesión. La API de análisis rechaza expresamente un seguimiento activo.

Pausar o detener señala cancelación y despierta el hilo. El capturador comprueba
la señal antes de los comandos y antes de publicar; el cliente Docker propio se
cancela durante su espera. Si una publicación ya comenzó puede terminar antes
de confirmar la pausa o parada. El control espera hasta cinco segundos y, si
todavía no finalizó, mantiene el estado «solicitada», sin confirmar por anticipado.

El capturador mantiene la limitación previa: puntero y copia visible se publican
como archivos separados. Una interrupción entre ambos se indica como desajuste;
no se promete una transacción entre archivos. Las generaciones anteriores se
conservan, incluso cuando una captura cancelada dejó una generación sin publicar.

El cierre normal del proceso intenta detener su hilo. El lanzador conjunto ya
posee sus grupos de procesos en POSIX o Job Object en Windows, incluido el cliente
Docker hijo; no se crea otro proceso independiente de monitorización. Un cierre
forzado puede dejar el último estado escrito como activo. La lectura posterior
lo identifica como interrumpido cuando el bloqueo está libre, sin reanudarlo.
Los controles de una sesión de otro proceso no se apropian de ella ni matan PIDs.
Estas rutas de cierre están implementadas, pero no se han ejercitado en esta fase.

## API y archivos

| Ruta | Operación |
| --- | --- |
| `GET /api/v1/fuentes/log` | Estado de fuente con `following`, modo, snapshot y última lectura válida |
| `GET /api/v1/fuentes/log/seguimiento` | Estado local de sesión y checkpoint; sin Docker o nuevas capturas |
| `POST /api/v1/fuentes/log/seguimiento/iniciar` | Inicio explícito con `interval_seconds` y `duration_seconds`, opcionales |
| `POST /api/v1/fuentes/log/seguimiento/pausar` | Solicitud de pausa con objeto JSON vacío |
| `POST /api/v1/fuentes/log/seguimiento/reanudar` | Reanudación de la misma sesión, sin prolongar su duración |
| `POST /api/v1/fuentes/log/seguimiento/detener` | Solicitud de parada y liberación posterior de los bloqueos |

Las escrituras requieren conexión local, origen permitido y habilitación del
perfil. No se admiten destinos, comandos o modos arbitrarios en estas opciones.
El [OpenAPI](../dashboard/openapi-v1.json) recoge límites y respuestas de control.

```text
.local-state/puerto-umbral/
  .follow.lock
  following/current.json
  following/sessions/<session_id>.json
```

El estado persiste modo, sesión, duración, último ciclo y checkpoint con referencia
al snapshot, hash y procedencia. Al terminar se conserva un recibo de sesión;
si hubo interrupción, el siguiente inicio conserva el estado previo con esa causa.
No se guardan claves ni cuerpos de petición en estos archivos. Los nombres de
estado y recibos de sesión se añaden a la lista permitida de respaldo/restauración.
Restaurarlos no activa el seguimiento. Los bloqueos no se respaldan como sesiones
vivas. Los datos operativos siguen fuera de Git.

La UI consulta metadatos cada dos segundos mientras observa una sesión activa.
Esas lecturas no contactan con Docker. Al cambiar el snapshot actualiza la vista
Actividad, sin solicitar un análisis. Los controles mantienen la separación entre
modo del perfil, modo del snapshot conservado y selección del laboratorio.

## Comprobaciones de desarrollo realizadas

- Sintaxis de seis archivos Python compilada en memoria, sin importar ni ejecutar
  módulos de aplicación.
- JSON de OpenAPI leído correctamente.
- TypeScript sin emisión y ESLint de los dos componentes modificados, correctos.
- Compilación de producción Next con Webpack y TypeScript, correcta. El primer
  intento quedó bloqueado por permisos de escritura del sandbox en `.next`;
  la repetición autorizada fuera del sandbox terminó con salida 0.

No se iniciaron Flask, Next, Docker, sesiones de seguimiento, capturas, escenarios,
suites ni llamadas al modelo durante estas comprobaciones. La compilación no
acredita comportamiento en ejecución ni revisión visual de las nuevas pantallas.

## Aceptación pendiente

| Criterio PRD | Implementación preparada | Evidencia operativa y pendientes |
| --- | --- | --- |
| F4-AC1 | Frecuencia y duración acotadas; medición del último ciclo | Se observan 26 ciclos; faltan medidas de latencia individuales para acreditar el objetivo completo |
| F4-AC2 | Reutilización por bytes/procedencia; sin creación de trabajos | Reutilización entre ciclos/sesiones y contadores estables al reabrir observados; archivos, trabajos y captura después de reinicio pendientes |
| F4-AC3 | Estados de error, cambio de origen y discontinuidad; conservación | Desconexión, rotación/truncado, errores de almacenamiento y recuperación |
| F4-AC4 | Señales de cancelación, espera de confirmación y cierre propietario | Recorrido básico observado: pausa/reanudación/parada/vencimiento, cierre informado, preflight correcto y reapertura sin auto-resume; no inspección exhaustiva de procesos ni todas las interrupciones posibles |
| F4-AC5 | Servicio sin acceso a pipeline/modelo/notificaciones | Revisión operativa posterior del recorrido completo |

No se ejecutan esos pendientes por escribirlos. Se mantiene finalizada la ronda
anterior de escenarios. F4 queda desarrollada, sin cerrar su aceptación ni
F2/F3/F5. La publicación autorizada se identifica mediante el historial Git;
la evidencia posterior de actualización en Parrot se recoge al final de este
registro. La ronda operativa básica queda completada y la aceptación ampliada
sigue pendiente. No se crea una release o
atribuye nueva CI. El Site privado F1
permanece intacto.

## Validación operativa guiada autorizada

El agente prepara y verifica la publicación; el propietario opera la VM. Cada
paso se revisa antes de avanzar al siguiente. No se incluyen escenarios nuevos
ni tráfico preparado para evaluar el detector.

1. Cerrar el lanzador anterior con Ctrl+C y esperar la confirmación. Revisar el
   árbol de trabajo antes de actualizar; si hay cambios locales, conservarlos
   y revisar su alcance antes de continuar. Actualizar con `git pull --ff-only`
   y confirmar el commit obtenido. No usar reset o borrar archivos para forzar.
2. Compilar solo el frontend actualizado con las dependencias ya instaladas.
   No hace falta reinstalar Python o modificar `.env` para este cambio.
3. Arrancar el perfil conjunto con la fuente corregida y confirmar que Actividad
   presenta los controles de seguimiento inicialmente detenidos. No activarlos
   hasta revisar esa pantalla.
4. Iniciar una sesión de cinco minutos con intervalo de cinco segundos sobre
   los logs existentes. Conservar la primera referencia observada y comparar los
   siguientes ciclos. Una captura F3 antigua sin el instante de arranque puede
   producir una nueva referencia inicial de procedencia; a partir de ella, sin
   cambios de bytes/origen, debe mantenerse el mismo snapshot.
5. Revisar pausa y reanudación con contadores/fechas antes y después; detener y
   confirmar que no comienzan ciclos nuevos. «Pausa/parada solicitada» no basta
   como confirmación de que hayan terminado.
6. Cerrar V2 desde su lanzador y abrir de nuevo para comprobar ausencia de
   reanudación automática. Una sesión que se cierre abruptamente puede aparecer
   como interrumpida, con la última evidencia conservada.

Las capturas de pantalla respaldarán
únicamente los estados que muestren; no se atribuyen integridad de todos los
archivos, cobertura de rotación/errores o rendimiento general por ese recorrido.

## Publicación y actualización de Parrot observadas

El commit `02d26388b67fc51591eaede9bf2056f28cadbea1` publica los 18 archivos de
F4 y actas acumuladas con `[skip ci]`. La consulta remota de `refs/heads/main`
coincidió con HEAD y el árbol local quedó limpio después del push. No se
publicaron logs, recibos de la VM, archivos `.env` o una nueva release.

La captura siguiente del propietario muestra un fast-forward de `abab01d` a
`02d2638` y `git log -1 --oneline` con HEAD en `main`, coincidiendo con
`origin/main`. Acredita la actualización del checkout en Parrot. La imagen no
incluye el cierre anterior, el estado previo del árbol o una compilación nueva.

El siguiente paso guiado es compilar únicamente el frontend actualizado, desde
la raíz del checkout de Parrot:

```bash
cd frontend
node node_modules/next/dist/bin/next build --webpack
```

Esta operación utiliza las dependencias ya instaladas y no inicia servicios,
seguimiento, escenarios o análisis. Se espera su salida final antes de arrancar
la aplicación. El agente no ha ejecutado esta compilación en la VM; la evidencia
de compilación Windows anterior se mantiene separada.

## Compilación del frontend observada en Parrot

La siguiente captura del propietario muestra Next.js 16.3.8 con Webpack,
compilación correcta en 8,1 segundos, TypeScript terminado en 3,6 segundos,
generación de cuatro de cuatro páginas y finalización de trazas/optimización.
La salida termina con las rutas estáticas `/` y `/_not-found`. Se acredita la
compilación del frontend actualizado en la VM por su salida final; el recorte
no incluye el código de salida o el prompt. No acredita arranque o seguimiento.

El siguiente paso guiado, desde el directorio `frontend` mostrado, es volver
a la raíz y arrancar el perfil conjunto con la fuente corregida:

```bash
cd ..
python3 webdefense.py start --mode structured --with-puerto-umbral --lab-mode corrected
```

Una vez aparezca «Consola lista», abrir Actividad en V2 y revisar los controles
de seguimiento inicialmente detenidos, sin iniciar todavía una sesión. La
evidencia del arranque y de esa pantalla sigue pendiente del propietario.
El agente solo registra la captura y prepara las indicaciones, sin operar la VM,
ejecutar escenarios o llamar al modelo.

## Pantalla inicial F4 observada en Parrot

La siguiente imagen del propietario muestra Actividad con los nuevos controles
de seguimiento: estado «Detenido», inicio habilitado y pausa, reanudación y parada
deshabilitados. La fuente indica modo corregido y conserva una captura antigua
del 26/10/2026 a las 20:08:38 de Madrid, con 17 líneas, snapshot y SHA-256 visibles.
El intervalo seleccionado es de cinco segundos y la duración predeterminada de
treinta minutos. Se acredita el acceso a la interfaz y su estado inicial, no la
salud actual del contenedor ni la ausencia de reanudación tras una sesión previa.

«Captura antigua» es coherente con la antigüedad del snapshot conservado. No se
interpreta por sí solo como fallo de arranque o ausencia de actividad. La fecha
y el estado del contenedor indicados en esa captura pertenecen a su obtención.

El siguiente paso guiado es elegir duración de cinco minutos, mantener intervalo
de cinco segundos y pulsar «Iniciar seguimiento» una vez. Esperar entre quince
y veinte segundos sin generar tráfico nuevo en el portal y aportar una imagen
que incluya fuente, snapshot, estado y contadores. La primera referencia puede
renovarse para registrar la procedencia/arranque actuales; la comprobación sin
cambios comparará ciclos posteriores a esa primera referencia. Este inicio aún
no se declara ejecutado; el agente solo registra la imagen del estado detenido.

## Primera sesión de seguimiento observada

La captura posterior del propietario muestra «Siguiendo logs», intervalo de
cinco segundos y duración de cinco minutos. Los contadores indican diez ciclos
válidos, un snapshot nuevo y nueve ciclos sin cambios. El último ciclo válido
figura el 27/10/2026 a las 17:51:37 de Madrid, con 0,058 segundos de lectura,
y el fin de duración a las 17:55:51. El estado de ventana indica «Sin cambios».

Se acredita la ejecución de ciclos de F4 en Parrot y la reutilización indicada
por sus contadores. El recorte no incluye snapshot/hash superiores ni los
archivos de estado. La duración mostrada corresponde únicamente al último
ciclo, no a todos los anteriores ni al objetivo completo de latencia F4-AC1.

El siguiente paso guiado es alcanzar al menos veinte ciclos válidos, si la sesión
sigue activa, y pulsar «Pausar». Revisar que el estado llegue a «Pausado», conservar
una captura y compararla con otra después de quince segundos: ciclos y fecha del
último ciclo no deben avanzar mientras la pausa está confirmada. Una pausa
solicitada todavía no basta. Si la duración se agota antes, registrar ese estado
en lugar de presumir que la pausa se ejecutó. Esta comprobación sigue pendiente;
el agente no opera la VM ni genera nuevas solicitudes al portal.

## Pausa estable y fin de duración observados

Las tres imágenes siguientes del propietario muestran dos estados «Pausado»
y después «Sesión finalizada por duración». En las tres se conservan 26 ciclos
válidos, un snapshot nuevo, 25 ciclos sin cambios y último ciclo válido del
27/10/2026 a las 17:52:58 de Madrid, con 0,057 segundos de lectura. El fin de
duración permanece a las 17:55:51. La fuente sigue corregida, con 17 líneas y
el mismo identificador de snapshot y SHA-256 visibles; su fecha de captura
permanece a las 17:50:51, separada de la última lectura válida.

Se observa estabilidad entre las dos pantallas de pausa y vencimiento posterior
sin avanzar contadores o última lectura. Es coherente con que la pausa no amplía
la duración. Las imágenes no aportan una medida independiente del intervalo
entre capturas, ni los archivos completos para recalcular el hash. Los 26 ciclos
no acreditan la latencia de cada uno, ausencia de trabajos en SQLite o cierre
completo de F4.

La sesión anterior ya finalizó, por lo que la reanudación debe revisarse en una
nueva sesión corta, con cinco minutos y cinco segundos de intervalo. El siguiente
paso guiado es iniciar, alcanzar al menos dos ciclos, pausar y conservar una
captura del estado confirmado. Después reanudar y, tras diez o quince segundos,
conservar otra imagen que muestre «Siguiendo logs» y avance de contadores/última
lectura. Mantener el portal sin acciones nuevas. Este paso no se declara realizado;
parada manual y cierre quedan para después de revisar la reanudación.

## Reanudación y reutilización entre sesiones observadas

Las siguientes dos imágenes muestran una nueva sesión de cinco minutos, con
intervalo de cinco segundos. La primera está «Pausado», con tres ciclos válidos,
cero snapshots nuevos, tres ciclos sin cambios y última lectura del 27/10/2026
a las 17:58:59 de Madrid, de 0,064 segundos. La segunda está «Siguiendo logs»,
con siete ciclos válidos, cero snapshots nuevos y siete ciclos sin cambios;
la última lectura avanza a las 17:59:35, de 0,060 segundos.

La fuente corregida mantiene 17 líneas, el mismo identificador de snapshot y
SHA-256, con fecha de snapshot a las 17:50:51. El fin de duración conserva las
18:03:48 en ambas imágenes. Se observa reanudación, avance de lecturas y
reutilización del snapshot de la sesión anterior sin ampliar la duración. No
se infiere un reinicio del proceso Flask, verificación independiente del hash,
ausencia de trabajos o métricas de latencia de todos los ciclos.

El siguiente paso guiado es pulsar «Detener seguimiento», esperar «Detenido»
y conservar una captura con contadores y última lectura. Después de quince
segundos, pulsar «Actualizar seguimiento» y tomar una segunda captura para
comparar esos valores. Esta actualización explícita evita confundir una pantalla
sin refrescar con ausencia de ciclos: el sondeo automático de seguimiento se
desactiva al quedar detenido. La parada manual y el cierre de V2 siguen pendientes
de observación; el agente solo registra las imágenes del propietario.

## Parada manual estable observada

Las dos imágenes siguientes muestran «Detenido», con 31 ciclos válidos,
cero snapshots nuevos y 31 ciclos sin cambios. La última lectura permanece
el 27/10/2026 a las 18:01:37 de Madrid, con 0,065 segundos; el fin de duración
conserva las 18:03:48. Los controles de pausa, reanudación y parada aparecen
deshabilitados y el inicio vuelve a estar disponible.

La comparación es consistente con la parada manual y estabilidad de contadores
tras la actualización solicitada. No aporta una medida independiente del tiempo
entre imágenes, ni inspección de procesos o puertos. No se acredita todavía
el cierre del lanzador o la ausencia de reanudación al abrir V2 de nuevo.

El siguiente paso guiado es iniciar otra sesión de cinco minutos/cinco segundos,
esperar al menos dos ciclos y conservar una captura «Siguiendo logs». Después,
cerrar V2 con Ctrl+C en su terminal propietaria y esperar a que vuelva el prompt,
conservando la salida de cierre. Revisar esa evidencia antes de volver a arrancar.
Se hará con logs existentes y sin acciones sobre el portal. No se declara
realizado el cierre por proponerlo; el agente solo actualiza el registro local.

## Cierre del lanzador durante una sesión activa

El propietario aporta tres imágenes. La primera muestra «Siguiendo logs» con
dos ciclos válidos, cero snapshots nuevos y dos sin cambios, último ciclo del
27/10/2026 a las 18:04:37 de Madrid, de 0,076 segundos. La segunda conserva
la última respuesta recibida, ahora con cinco ciclos y última lectura a las
18:04:52, de 0,058 segundos, junto con un error de red al consultar el recurso.
El fin de duración permanece a las 18:09:32 en ambas.

La terminal muestra el arranque conjunto en modo corregido, Ctrl+C,
«Consola detenida» y vuelta al prompt. Se acredita que el lanzador informó
el cierre mientras la sesión estaba activa. El error de red es coherente con
el cierre de la API; «Siguiendo logs» permanece como estado de la última
respuesta válida, no como observación actual de un hilo que continúe activo.
Estas imágenes no inspeccionan por sí mismas puertos o procesos supervivientes.

El siguiente paso guiado, antes de volver a abrir, es:

```bash
python3 webdefense.py check --mode structured --with-puerto-umbral --lab-mode corrected
```

La revisión del código confirma que `check` realiza el preflight: build, entorno,
bloqueos/trabajos, disponibilidad de puertos 3000/5000/4380/4381/4382 y estado
de los contenedores propios mediante Compose config e inspect. No inicia
servicios, seguimiento, escenarios o análisis. Se espera su resultado real antes
de la reapertura; el agente solo revisó código y registró las imágenes.

## Preflight posterior al cierre acreditado

La captura del propietario muestra el comando `webdefense.py check` con modo
structured, arranque conjunto y fuente corregida, seguido de «Preparado:
entorno, build y puertos comprobados» y vuelta al prompt. Acredita que el
preflight terminó sin los bloqueadores previstos. No sustituye una inspección
exhaustiva de todos los procesos o una prueba de reanudación automática.

El siguiente paso guiado es volver a arrancar con el mismo perfil:

```bash
python3 webdefense.py start --mode structured --with-puerto-umbral --lab-mode corrected
```

Una vez lista la consola, abrir Actividad sin iniciar seguimiento y conservar
una captura. Se espera estado detenido o interrumpido: el segundo es coherente
con haber cerrado el proceso con una sesión activa y no implica reanudación.
Después de quince segundos, pulsar «Actualizar seguimiento» y comparar otra
captura. No deben avanzar los ciclos ni la fecha de última lectura por el mero
arranque de V2. Esta reapertura sigue pendiente de evidencia del propietario;
el agente no ejecutó el comando en la VM ni generó escenarios o análisis.

## Reapertura sin reanudación automática observada

Las dos capturas posteriores muestran «Sesión interrumpida; no se reanuda
automáticamente». En ambas se mantienen cinco ciclos válidos, cero snapshots
nuevos, cinco ciclos sin cambios y última lectura del 27/10/2026 a las 18:04:52
de Madrid, de 0,058 segundos. El fin de la sesión anterior permanece a las
18:09:32. El inicio está disponible y pausa/reanudación/parada deshabilitados.

Es coherente con el último estado recibido antes del cierre activo y con que
reabrir V2 no inició nuevas lecturas. Las imágenes no incorporan una medida
independiente del intervalo entre ellas o archivos completos de la VM. El estado
interrumpido informa del cierre anterior; no representa una sesión nueva activa.

## Cierre de la ronda operativa básica

El recorrido guiado acordado queda completado con la evidencia del propietario:

| Revisión | Resultado observado |
| --- | --- |
| Actualización de Parrot | Fast-forward a `02d2638` |
| Compilación VM | Webpack/TypeScript y salida final de rutas correctos |
| Estado inicial | Fuente corregida, seguimiento detenido |
| Inicio y ciclos | Sesiones explícitas; una alcanza 26 ciclos y otra 31 |
| Sin cambios | Snapshot conservado; sesiones posteriores sin snapshots nuevos |
| Pausa | Estado confirmado y contadores/última lectura estables |
| Reanudación | Avance de tres a siete ciclos sin ampliar duración |
| Parada manual | Estado detenido estable tras la revisión solicitada |
| Vencimiento | Fin por duración mientras estaba pausado |
| Cierre con sesión activa | Ctrl+C, consola detenida y vuelta al prompt |
| Preflight posterior | Entorno, build y puertos comprobados sin bloqueadores |
| Reapertura | Sesión interrumpida, sin avance de contadores o última lectura |

No se solicitan más capturas o ejercicios para cerrar este recorrido. El agente
ha registrado la evidencia sin operar la VM. No se solicitaron nuevos escenarios,
corpus, análisis del modelo o notificaciones durante esta ronda de seguimiento.

**Alcance del cierre:** validación operativa básica de F4 con logs existentes,
no aceptación de todos los criterios del PRD. Permanecen pendientes métricas
individuales de latencia, variación real del log, desconexión de la fuente durante
el seguimiento, rotación/truncado, fallos de almacenamiento, cotejo independiente
de archivos/hashes y trabajos. No se atribuye detección al analizador ni cierre
de F2/F3/F5. La continuación puede preparar la evaluación y documentación F5 con
la evidencia disponible, manteniendo explícitos esos límites.

El código operativo de referencia permanece en `02d2638`. Estas observaciones
posteriores se incorporan al paquete documental F4/F5 cuya publicación autoriza
el propietario el 27/10, sin nueva release. La reapertura observada dejó el
seguimiento interrumpido, a la espera
de una futura acción explícita del operador.

La [evaluación F5](PUERTO_UMBRAL_F5_2026_10_27.md) utiliza después este cierre
como evidencia operativa parcial y prepara el [manual de operación](PUERTO_UMBRAL_OPERACION_LOCAL.md).
No convierte las capturas en mediciones de todos los ciclos o en aceptación
ampliada de F4, ni solicita nuevas revisiones al propietario.

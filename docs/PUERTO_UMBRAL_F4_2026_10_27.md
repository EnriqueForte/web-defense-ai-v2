# Puerto Umbral — F4: seguimiento local de logs

Fecha: 27/10/2026. Estado: **implementado; validación operativa pendiente**.

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

| Criterio PRD | Implementación preparada | Evidencia pendiente |
| --- | --- | --- |
| F4-AC1 | Frecuencia y duración acotadas; medición del último ciclo | Veinte ciclos y objetivo de latencia en plataforma real |
| F4-AC2 | Reutilización por bytes/procedencia; sin creación de trabajos | Comportamiento real sin cambios y entre reinicios |
| F4-AC3 | Estados de error, cambio de origen y discontinuidad; conservación | Desconexión, rotación/truncado, errores de almacenamiento y recuperación |
| F4-AC4 | Señales de cancelación, espera de confirmación y cierre propietario | Pausa, parada, vencimiento y cierre de procesos observados |
| F4-AC5 | Servicio sin acceso a pipeline/modelo/notificaciones | Revisión operativa posterior del recorrido completo |

No se ejecutan esos pendientes por escribirlos. Se mantiene finalizada la ronda
anterior de escenarios. F4 queda desarrollada, sin cerrar su aceptación ni
F2/F3/F5. La publicación autorizada se identifica mediante el historial Git;
actualización y validación en Parrot quedan pendientes de la evidencia del
propietario. No se crea una release o atribuye nueva CI. El Site privado F1
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

El primer paso aún no está acreditado. Las capturas de pantalla respaldarán
únicamente los estados que muestren; no se atribuyen integridad de todos los
archivos, cobertura de rotación/errores o rendimiento general por ese recorrido.

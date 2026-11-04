# Estado y plan de cierre de Web Defense AI V2 y Puerto Umbral

## Recorrido funcional posterior — 04/11/2026

El propietario solicita y realiza un nuevo recorrido guiado: captura,
seguimiento con una petición normal nueva, dos análisis manuales y retorno a
lectura. El primero selecciona 30/95 líneas y no publica hallazgos; el segundo
selecciona 26/26 de la fuente vulnerable y publica SQLi en la línea 26 del
intento recién recibido y Command Injection en línea 7 del historial.
La vista Amenazas refleja ambos y el ejecutor vuelve a lectura conservando
el resultado. **Recorrido representativo completado a su alcance observado.**

El [acta del 04/11](PUERTO_UMBRAL_RECORRIDO_MANUAL_2026_11_04.md) distingue
seguimiento de la consulta normal, captura manual del intento vulnerable,
evidencia de pantalla y límites. La pausa no tiene captura específica de
estabilidad de contadores; no se repite por el acta. Esta autorización nueva
no cambia las decisiones de cierre por alcance inferiores ni aporta métricas
globales F5, rotación real o aceptación final. No se ejecuta nada adicional
para registrar los resultados y no se publica Git por documentarlos.

## Estado vigente — 03/11/2026

El propietario mantiene el jueves **5 de noviembre** como objetivo de cierre
del desarrollo y comunica el 03/11: «Procedo a aceptar la matrix actualizada»,
y sobre F4/F5: «si hay que ejecutar pruebas dalas por cerradas tambien».
Se registra esa decisión expresa después de la revisión documental F7 y de
la explicación de los pendientes. No se ejecutan nuevas pruebas para cerrar.

| Fase | Decisión vigente del propietario | Alcance y limitación conservada |
| --- | --- | --- |
| F4 | Cerrada por decisión expresa de alcance, sin las pruebas restantes | Medición API con desviación F4-AC1 ya aceptada, seguimiento y fallo/recuperación observados. Rotación/discontinuidad real restante y otras condiciones no observadas quedan sin verificar; no se declaran aprobadas |
| F5 | Cerrada por decisión expresa de alcance, sin evaluación adicional | Se conserva registro histórico, revisión documental, consumo y respaldos a sus fechas. No hay métricas propias del detector sobre los 45 casos; originales aún sin localizar. Se omiten del trabajo de cierre la evaluación, pruebas del empaquetador y desarrollo/validación pendiente de su ejecutor/puntuador |
| F6 | Cerrada por decisión expresa anterior, sin las pruebas restantes | Cargas/Atraque y controles corregidos conservan sus resultados. Bitácora/Preferencias vulnerables, resultado vulnerable de Baliza y regresión F6 restante omitidos/no verificados |
| F7 | Matriz actualizada aceptada expresamente en su alcance educativo documentado | Diez categorías con objetivos/tipos de evidencia y once recorridos representativos identificados; no 54/54, detección completa OWASP o seguridad de producción |

**Las decisiones de alcance F4/F5 y aceptación de la matriz F7 están resueltas.**
Los criterios originales del PRD se conservan como referencia: el cierre
acordado incorpora omisiones explícitas y no equivale a haber superado todas
sus verificaciones originales. La falta de evaluación F5 se conserva como tal;
27/30, 5/6 por familia y cero falsas alarmas son objetivos no acreditados.

No se reabren las búsquedas de originales, pruebas, casos, capturas, copias,
hashes, sesiones de seguimiento, servicios, VM o modelo para este cierre. Los
resultados recibidos de lanzador, interfaces, comandos, observador, perfiles,
auditoría y conservación mantienen su alcance. La cobertura F2/F3 no observada
sigue declarada como limitación, sin añadir nuevas pruebas.

Queda la consolidación y aceptación final del conjunto de entrega con esos
límites; esta aceptación de fases no publica Git, crea una release o autoriza
LinkedIn. V2 v0.1.0 mantiene su identidad y aceptación local anterior. La
[revisión integral](REVISION_INTEGRAL_2026_11_03.md), el
[estado de entrega](PUERTO_UMBRAL_ENTREGA_2026_11_02.md) y la
[matriz aceptada](PUERTO_UMBRAL_F7_CIERRE_EDUCATIVO_2026_10_31.md)
conservan el detalle. Los pendientes de las cronologías inferiores quedan
resueltos o retirados según esta decisión, sin cambiar resultados históricos.

## Antecedentes de planificación y entrega — 02/11

Estado al 02/11/2026, Europe/Madrid: **desarrollo en curso; cierre F0–F7 solicitado,
todavía no aceptado**. En ese momento el propietario quería terminar antes del martes 3 de
noviembre para preparar su publicación en LinkedIn. Confirmaba expresamente que
incluía F6 y F7, además del MVP F0–F5. El objetivo de revisión final era el lunes
2 de noviembre. Este calendario histórico queda sustituido por el objetivo
del 5 de noviembre indicado arriba; no es una validación anticipada.

## Estado de entrega registrado — 02/11

Publicación autorizada después de comprobar el observador: trece archivos
(observador independiente, cinco pruebas y once Markdown acumulados), con
`[skip ci]`. Base `91a101e` coincide con remoto tras fetch y staging inicial
vacío. La identidad será el commit que incluye esta nota y su HEAD remoto se
verifica al terminar. Se entrega código/actas; medición real F4 no realizada.

El propietario pide priorizar lo realmente necesario y autoriza expresamente
las cinco pruebas aisladas del lanzador. Resultado local: **5/5 correctas,
exit 0**, Python 3.11.9/Windows, sin servicios o HTTP reales, Docker, VM o
modelo. No cambia el código ni se amplía la ejecución después. Acta y propuesta
manual siguiente: [verificación prioritaria](CIERRE_VERIFICACION_PRIORITARIA_2026_11_02.md).
Se reciben después los dos recorridos manuales de comandos y la identificación
previa de imagen/fuente: normal corregido y vulnerable variante 1 con identidad
del usuario del contenedor, ambos sin timeout y retorno 0. La incidencia
`Cannot fork` queda corregida y verificada a ese alcance; se conservan los tres
fallos históricos y no se puntúan variantes 2/3 nuevas. No repetir ese bloque.
Los demás criterios globales siguen abiertos; operación F3/F4 es la siguiente
prioridad recomendada, todavía sin ejecutar.

Recepción operativa posterior: [ensayo F4 de veinte ciclos](PUERTO_UMBRAL_MEDICION_F4_2026_11_02.md)
completado con parada y lectura de condiciones. Lecturas 0,057–0,096 s,
cotas API 0,086–1,054 s, trabajos 1→1/entregas 0→0 y un snapshot nuevo con
checkpoint único; Linux Parrot/x86_64/16 CPU lógicas/carga registradas.
No repetirlo. El propietario acepta después la desviación acotada de F4-AC1:
disponibilidad API, sin paint/visibilidad extremo a extremo RNF-09 verificados.
Condiciones de fallo/rotación de fuente y aceptación global siguen pendientes;
no se autoriza una nueva operación por aceptar esa desviación.

Tras autorización separada se completa el recorrido de fallo/recuperación de
la pasarela corregida: error visible, stop/start previstos, captura nueva de
94 líneas y ausencia de auto-resume; lectura del snapshot anterior confirma
existencia e igualdad de hash contra el recibo. No repetir comandos/captura/
lecturas o respaldo por documentarlo. Rotación real no observada y demás
criterios abiertos siguen explícitos. Siguiente prioridad recomendada:
preparación de evaluación F5 acotada, sin reutilizar el permiso Groq consumido.

El [resumen de entrega](PUERTO_UMBRAL_ENTREGA_2026_11_02.md) es la entrada
actual para continuar: lanzador conjunto y revisión básica de ambas interfaces
completados a su alcance; tres bloques técnicos abiertos (funcionamiento y
regresión, operación ampliada, evaluación F5) más decisión final de aceptación.
La guía de producto y la auditoría incorporan las recepciones posteriores.
No se repiten pantallas, arranques o lecturas de conservación ya completados.

Zoom 200 %, exportación y controles exhaustivos quedan sin observar como
cobertura adicional, sin convertirse automáticamente en cuotas del PRD.
Baliza tiene fila de historial pero resultado funcional sin recibir; no se
cuenta como superado ni se pide reejecución. El respaldo de 113 archivos
mantiene su fecha/selección, anterior a Cargas vulnerable recibido después.
La consolidación es documental local, sin suites, modelos, servicios o Git.

## Cronología del punto de partida

Las entradas siguientes registran qué se sabía y proponía en cada momento.
Los pendientes de una entrada antigua se resuelven por sus recepciones
posteriores; no son instrucciones vigentes de repetición. El resumen del
02/11 y la tabla de trabajo actualizada al final prevalecen para continuar.

### Revisión básica de ambas interfaces recibida — 01/11

Las capturas de Puerto Umbral muestran cabecera, autoría, controles y lista de
evidencias legibles en vista estrecha. La indicación «sí se distingue» del
propietario se interpreta como confirmación del foco solicitado. Con las
recepciones V2 anteriores se completa el bloque básico de navegación/vista
estrecha/foco de ambas interfaces a ese alcance. No se repite por el acta.
No constituye revisión de todos los controles, accesibilidad global, zoom
200 %, exportación o consulta móvil de recibos individuales. Una fila del
historial no acredita el resultado funcional del caso; no se añade otro
resultado F6 por la fila Baliza visible. Siguiente trabajo propuesto:
consolidación documental y revisión de los pendientes esenciales de entrega,
sin aceptar automáticamente F0–F7 ni activar pruebas o modelos.

### Revisión básica V2 completada; Puerto Umbral siguiente — 01/11

Cuatro capturas completan el recorrido V2: informe anterior abierto, Amenazas,
Actividad y Configuración en vista estrecha, con bloques mostrados legibles y
sin error visible. Se mantienen informe/fechas/origen/antigüedad; no se genera
evidencia nueva. Con Resumen y la confirmación previa de foco/Escape, se
completa navegación básica de cinco vistas y ese recorrido de teclado.
No se atribuyen todos los controles, accesibilidad global, zoom 200 % o
exportación. Siguiente dentro del bloque acordado: panel Puerto Umbral en
vista adaptable, cabecera y lista de evidencias, sin ejecutar, restablecer,
abrir recibos o activar comprobaciones de navegador. Resultado aún pendiente.
Detalle en [revisión de producto](PUERTO_UMBRAL_REVISION_PRODUCTO_2026_10_31.md).

### Revisión de producto V2, recepción parcial — 01/11

Firefox Responsive permitió observar el menú a 390 × 844/DPR 1 pese a la
restricción de redimensionar la ventana en Parrot. El propietario confirma
foco visible con Tab/Mayús+Tab y cierre con Escape/devolución al botón de menú.
Otra captura muestra Reportes con menú cerrado: cabecera/autoría legibles,
catálogo y lectura apilados. El informe aún no está seleccionado; no se
atribuye lectura de su contenido. Resumen/Reportes observados; navegación de
las otras tres vistas y revisión de Puerto Umbral pendientes. No repetir
menú/teclado ya confirmados. Estado detallado en la
[revisión de producto](PUERTO_UMBRAL_REVISION_PRODUCTO_2026_10_31.md).

### Retorno a lectura completado por captura — 01/11

La captura posterior muestra Ejecutor no disponible, solicitudes manuales
desactivadas y botón Iniciar análisis inactivo. Groq sigue configurado y el
último trabajo visible sigue siendo el previo `f5b674c86799…`, manual,
succeeded/finished. Queda completado el retorno solicitado a lectura.

Con las recepciones de arranque manual/disponibilidad y Ctrl+C/Consola detenida,
se completa el recorrido básico **lectura → manual → parada → lectura** de
`91a101e` dentro del alcance observado. No se repite por documentarlo. No se
aporta análisis nuevo ni ejecución de las cinco regresiones aisladas, ni se
atribuye una inspección exhaustiva de procesos del host o aceptación global.
Las actas nuevas siguen locales; siguiente bloque de producto propuesto:
navegación, móvil y teclado, sin modelos o escenarios.

### Parada manual informada; retorno a lectura pendiente — 01/11

El propietario sigue la propuesta y aporta `Ctrl+C` en la sesión manual
`20261101T164618Z-9953ad47`, con salida «Consola detenida». Se recibe la parada
informada por el supervisor propio, sin solicitar repetirla por un prompt no
visible ni atribuir una inspección exhaustiva de procesos del host.

La segunda captura del navegador conserva la lectura anterior de ejecutor
activo/admisión habilitada, pero añade «No se pudo consultar el estado del
ejecutor». Es coherente con el backend cerrado: no acredita ejecutor activo
actual ni un arranque nuevo de lectura. La continuación es iniciar
`python3 webdefensev2.py` sin la opción manual y recargar Resumen. Se esperan
ejecutor no disponible, solicitudes manuales desactivadas y botón inactivo,
sin solicitar un análisis. Resultado de ese retorno todavía pendiente.

### Disponibilidad del modo manual observada — 01/11

Dos capturas del propietario muestran la entrega `91a101e` en HEAD/main/origin
y el inicio con `python3 webdefensev2.py --enable-manual`, fuente corregida,
direcciones del panel/portales y Consola lista en 3000. Logs mostrados:
`.local-state/launcher/20261101T164618Z-9953ad47`. La consola indica que el
ejecutor espera solicitudes, sin ciclos programados. V2 muestra Ejecutor
activo, solicitudes manuales habilitadas, Groq configurado y botón disponible.
El último trabajo visible conserva el prefijo `f5b674c86799`, manual,
succeeded/finished, correspondiente al análisis previo.

La comprobación acordada de disponibilidad queda completada por capturas;
no se repite el arranque o la revisión del botón por documentarlos. No se
aporta resultado de un análisis nuevo, autenticación del proveedor, coste,
parada del nuevo ejecutor o ejecución de las cinco regresiones preparadas.
Publicación Git verificada; no hay publicación adicional por esta recepción.
Siguiente comprobación propuesta: cierre propio con Ctrl+C y retorno a lectura
sin la opción, observando admisión apagada y ejecutor inactivo, sin llamar al
modelo; aún no realizada. Resto de criterios globales pendientes.

### Publicación y comprobación de disponibilidad manual autorizadas — 01/11

El propietario pide commit/push y comprobar la integración manual. Entrega:
tres lanzadores Python, cinco comprobaciones aisladas en un archivo todavía
sin ejecutar y ocho documentos/actas. Base `8f65bc7`, coincidente con
`origin/main` tras fetch; staging inicial vacío. Se publica con `[skip ci]`;
la identidad será el commit que incluye esta nota, verificando remoto y árbol
al finalizar. No se repiten suites, frontend build o llamadas al modelo.

El recorrido acordado en Parrot es detener la consola anterior, revisar cambios
locales, actualizar con `git pull --ff-only`, comprobar el commit y ejecutar
`python3 webdefensev2.py --enable-manual`. Recoger Consola lista, ejecutor activo,
admisión manual y disponibilidad del botón con el proveedor ya configurado,
**sin pulsar Iniciar análisis**. Esta comprobación no autoriza otra llamada al
modelo, escenario o suite. No necesita reinstalar o recompilar el frontend.
La disponibilidad real sigue pendiente de capturas; no se acredita por Git.

### Activación manual del lanzador desarrollada — 01/11

El propietario acepta integrar la opción `--enable-manual`. Se implementa
en ambas entradas Python y el supervisor: el inicio sin opción mantiene lectura;
el inicio manual habilita admisión y supervisa el worker existente
`pipeline.py --manual-only` en el mismo perfil/env/rutas que Flask.
Se conserva el bloqueo por trabajos activos/pendientes y locks incompatibles.
El supervisor espera, mediante GET local de estado, admisión habilitada y
ejecutor online antes de confirmar disponibilidad; no necesita contactar al
proveedor para ello. El botón también necesita proveedor configurado.

No se encolan trabajos ni ciclos programados por arrancar; notificaciones
apagadas. `worker.log` y el proceso del ejecutor forman parte del supervisor
y su cierre propio. Antes de cerrar se espera al fin del trabajo; un trabajo
interrumpido conserva estado/recibos para revisión y no se reintenta por
eludir el bloqueo del preflight. `check --enable-manual` no inicia el ejecutor;
instalación/legacy no admiten esa opción.

Sintaxis AST Python 3.11 revisada en cuatro archivos y ayuda CLI exit 0.
Cinco regresiones aisladas preparadas, **no ejecutadas**; tampoco se inicia
servicio, preflight, instalación, suite, frontend build o modelo por el agente.
Validación operativa del modo manual/botón en Parrot pendiente tras publicar;
la primera revisión será disponibilidad, sin pulsar Iniciar análisis. Cambios
locales sin nuevo commit/push. Los demás criterios abiertos se mantienen.

### Entrada conjunta observada en Parrot — 01/11

Entrega `8f65bc747e87e3bbd7318e2146e453869b1728f3` publicada y verificada
contra `origin/main`. La captura muestra `python3 webdefensev2.py`, fuente V2
corregida, preparación de servicios propios, direcciones 4381/4380/4382 y
«Consola lista» en 3000. Directorio de logs mostrado:
`.local-state/launcher/20261101T162651Z-b93ea780`. El propietario confirma que
ambas apps funcionan en el navegador. Primer arranque de la entrada conjunta
completado a ese alcance; no repetirlo para documentar. No implica una nueva
comprobación de cierre, instalación o flujo de análisis.

El propietario señala que «Iniciar análisis» sigue desactivado. Es coherente
con el arranque de lectura: no habilita admisión manual ni inicia el worker.
El botón requiere admisión manual, proveedor listo, ejecutor online y ausencia
de trabajo en cola/ejecución. No se habilita automáticamente al esperar o
guardar una clave. Integrar una activación manual explícita en el lanzador
queda como pendiente propuesto, sin cambiarlo por esta recepción. La
autorización anterior de Groq está consumida; no se solicitan análisis nuevos.

### Publicación del lanzador autorizada — 01/11

El propietario solicita commit/push de la entrada conjunta y documentación
pendiente para actualizar Parrot. Alcance: dos archivos Python y nueve
documentos; sin frontend o datos operativos nuevos. Base `cd6b34d`, coincidente
con `origin/main` tras fetch. La entrega se identifica por el commit que
contiene esta nota, con `[skip ci]`; se verifican remoto y árbol al terminar.
No se repiten ayuda/AST ni se inician servicios o suites por publicar.

En Parrot: cerrar la consola propia anterior, revisar cambios locales,
`git pull --ff-only`, comprobar el commit e iniciar desde raíz con
`python3 webdefensev2.py`. La fuente elegida por defecto será `corrected`;
`--lab-mode vulnerable` conserva esa otra selección explícita si se desea.
No requiere recompilar Next o reinstalar por esta entrega. Primer arranque
real mediante la entrada nueva pendiente de captura, no acreditado por Git.

### Entrada conjunta simplificada desarrollada — 01/11

El propietario solicita un comando genérico para iniciar ambas aplicaciones.
Se implementa `webdefensev2.py`: sin argumentos delega en el lanzador existente
con `start --mode structured --with-puerto-umbral --lab-mode corrected`.
Admite `start` explícito, `check`, `install`, `--help` y selección
`--lab-mode vulnerable`. La instalación delega sin opciones del laboratorio;
no instala Docker por sí sola. Ambas pasarelas se preparan, y `--lab-mode`
elige la fuente que lee V2, no una ejecución de casos.

La nueva entrada conserva el supervisor y el cierre conjunto originales,
sin introducir otro gestor de procesos. El mensaje final de `check` recomienda
el comando conjunto con la fuente seleccionada, o el modo elegido para solo V2.
Sintaxis Python 3.11 revisada con AST y ayuda CLI con exit 0. No se ejecutaron
inicio, instalación, preflight, suites o modelos; no hubo build nuevo de Next.
El primer arranque mediante la entrada nueva sigue pendiente de observación
manual en Parrot. Cambios locales sin commit/push nuevo. La redistribución del
Resumen se mantiene y Baliza continúa aplazada.

### Nueva distribución recibida en Parrot — legibilidad prioritaria

La entrega `cd6b34d` se publicó en `origin/main` y su HEAD remoto/árbol limpio
se verificaron. El propietario aporta captura de Resumen a zoom 60 % y confirma
que a 100 % todavía requiere desplazamiento vertical. Se observa el ancho
aprovechado y las tarjetas en paralelo; no se acredita encaje sin scroll a
100 %, móvil o teclado. Pide preservar visibilidad y admite mantenerlo así.
Se recomienda conservar la distribución y trabajar a 100 % con desplazamiento
natural, sin compactar más, reducir texto o fijar la altura de la página.
No se modifica de nuevo el frontend por esta recepción. Acta visual en la
[revisión de producto](PUERTO_UMBRAL_REVISION_PRODUCTO_2026_10_31.md).

### Publicación autorizada y revisión en Parrot siguiente

El propietario solicita commit/push de los cambios acumulados y revisión
posterior en Parrot. La entrega incluye dos archivos de interfaz y trece de
documentación, sin datos operativos. Base `main`/`origin/main` comprobada tras
fetch: `1fdfed1`, sin divergencia. Se publica con `[skip ci]`; build de
producción/TypeScript/rutas y ESLint del archivo modificado ya completados.
La identidad será el commit que contiene esta nota; el resultado Git se
verifica al terminar, no se presupone por la autorización.

Después de publicarla: detener la consola propia en Parrot, actualizar con
`git pull --ff-only`, compilar desde `frontend` con
`node node_modules/next/dist/bin/next build --webpack`, volver a la raíz e iniciar
la consola habitual. Se conserva `--lab-mode vulnerable`, la última selección
usada, sin ejecutar casos. Recoger Resumen en escritorio y ventana estrecha;
móvil, teclado y resultado visual del nuevo diseño siguen pendientes.

### Resumen redistribuido — implementación y compilación completadas

Tras recibir tres capturas del Resumen, el propietario autoriza optimizar la
distribución. Se implementa ancho fluido solo en esa vista, cabecera y tarjetas
compactas, y cuadrícula adaptable con gráficas/reportes en paralelo y
amenazas/terminal debajo en escritorio amplio. Vistas previas: hasta cuatro
amenazas, seis líneas de log y dos reportes históricos; cantidades y enlaces a
vistas completas disponibles. Se mantienen tipografía base y desplazamiento
natural si la ventana o el contenido lo requieren.

Build webpack de producción, TypeScript y generación de rutas completados;
ESLint de `page.tsx` correcto. No suites, escenarios, servicios o modelos.
Las capturas corresponden al diseño anterior: revisión visual de la nueva
distribución en Parrot pendiente tras publicar/compilar el frontend allí.
Cambios locales, sin commit/push nuevo. Véase la
[revisión de producto](PUERTO_UMBRAL_REVISION_PRODUCTO_2026_10_31.md).

### Prioridad actual — producto y documentación

El propietario indica que no puede continuar Baliza por bloqueo del chat y
pide otro trabajo. Baliza vulnerable queda pendiente, sin ejecución ni
resultado; no se reformula el recorrido para eludir ese bloqueo. La prioridad
actual es la [revisión de producto](PUERTO_UMBRAL_REVISION_PRODUCTO_2026_10_31.md):
documentación, navegación, presentación móvil y teclado. No requiere nuevos
escenarios ni llamadas al modelo. La preparación documental no acredita por sí
sola el recorrido manual y no cierra las dependencias funcionales pendientes.
Las propuestas inferiores conservan su carácter histórico.

### Cargas vulnerable completado por capturas — 31/10

El recorrido `ext-idor-a1-vulnerable` queda completado en ejecución, lectura y
conservación informada en V2. Run `176266c5fd701ecdfa637ba14f0d6a34`:
COMPLETED, HTTP 200, `foreign-1`, propietario `supervisor.demo` y señuelo
`UMBRAL_FOREIGN_CARGO`; 3 peticiones/3 líneas Apache/2 eventos/2 referencias.
V2 muestra el mismo run y modo vulnerable, 2 eventos y la observación
«Recurso de otro propietario devuelto» para actor `estibador.demo` y recurso
`foreign-1`, con mensaje de copia conservada sin análisis. SHA de auditoría
mostrado: `2956f103989b75c515c0320b871eb2558cb5b93f425bd6d4b3b2db4cbc6d38d2`.
La comparación de esta variante con el rechazo corregido previo queda observada;
no repetir ninguno. No implica hash de bytes verificado de esta copia, nuevo
respaldo, métricas del modelo o aceptación F6 global. Próximo candidato
propuesto: Baliza vulnerable/Intento/variante 1, todavía sin autorizar o ejecutar.

### Siguiente recorrido aceptado — Cargas vulnerable, pendiente de resultado

El propietario acepta un caso manual `ext-idor-a1-vulnerable`: Cargas F6,
Intento de ataque, variante 1, con lectura y conservación de auditoría en V2,
sin suites ni llamadas al modelo. El arranque manual debe seleccionar
`--lab-mode vulnerable` para que V2 lea esa fuente. La expectativa revisada es
HTTP 200 para `foreign-1`, propietario `supervisor.demo` y señuelo
`UMBRAL_FOREIGN_CARGO`; 3 peticiones y 2 eventos/2 referencias. La regla V2
esperada es «Recurso de otro propietario devuelto». Ejecución, lectura y copia
siguen pendientes de las capturas; no se acredita ningún resultado por aceptar
el recorrido. No repetir el rechazo corregido ni las comprobaciones de cierre.

### Preflight de cierre actual completado — bloque terminado a su alcance

El propietario aporta `webdefense.py check` structured/with-puerto/corrected
con salida «Preparado: entorno, build y puertos comprobados». La rama revisada
lo imprime tras pasar las comprobaciones; lectura actual completada sin
bloqueadores visibles. No pedir repetir por prompt o exitcode fuera del recorte,
ni atribuir inspección exhaustiva de procesos del host o arranque de servicios.

Quedan completados a su alcance perímetro, recibo/hash puntual de auditoría,
selección de respaldo, copia del perfil de 113 archivos verificada internamente
y este preflight. No se repiten casos F7, copias o lecturas; la restauración
independiente adicional sigue aplazada. F4 ampliada, positivos/regresión F6,
evaluación/decisión de alcance F5 y UX/aceptación siguen pendientes.
Siguiente candidato funcional propuesto: un caso Cargas F6/vulnerable/Intento/
variante 1 con lectura/copia V2, sin suites o modelo, todavía sin autorizar o
ejecutar. Actas locales posteriores a `1fdfed1`, sin publicación Git.

### Respaldo actualizado completado; comprobar cierre sin arrancar

Captura del propietario: `.local-backups/operational-20261031T201154664036Z`,
113 archivos, `verified: true`, `missing: []`. Conservación básica del perfil
actual con verificación interna completada a ese alcance; no repetir el
respaldo. La restauración independiente adicional sigue aplazada y los
originales bajo `labs/` no se atribuyen a este perfil. No supone cierre F6/MVP.

Se revisa y guía el preflight existente `webdefense.py check --mode structured
--with-puerto-umbral --lab-mode corrected`, que comprueba entorno/build/puertos,
locks/trabajos y contenedores propios detenidos sin arrancar servicios,
recompilar o ejecutar casos/modelos. Resultado pendiente de captura; no se
deduce cierre del host a partir de la salida de backup. Procedimiento en la
[auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md).

### Respaldo actualizado autorizado, restauración independiente aplazada

El propietario acepta crear solo una copia nueva del perfil Puerto Umbral
con su verificación interna. Se guía cerrar la consola propia y ejecutar
`backup_operational.py --profile puerto-umbral` una vez, sin `--list`.
La herramienta crea ZIP/manifiesto, instantánea SQLite y `restore-check`
interno; se esperan `verified: true`, `missing: []` y ruta/conteo reales.
Resultado pendiente de captura. La restauración independiente con
`restore_operational.py` queda expresamente aplazada; no se ejecuta ni se
considera validada por esta decisión. No repetir casos/LLM o crear Git nuevo.

### Selección de auditorías confirmada; respaldo nuevo propuesto

El listado filtrado aportado muestra las tres rutas de la última auditoría
como `file`, 47 archivos de auditoría seleccionados y `faltantes: []`.
**Ronda de lectura completada**: perímetro, recibo, hash puntual y selección.
No repetirla. No hay todavía ZIP o recuperación nuevos ni inclusión acreditada
de los originales bajo `labs/`. Se prepara en la
[auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md) una propuesta conjunta:
cerrar consola propia, crear respaldo nuevo del perfil, comprobarlo con el
restaurador aislado y revisar la última auditoría recuperada. Genera archivos,
mientras que el alcance acordado era de solo lectura: autorización y ejecución
siguen pendientes. No se repite la recuperación antigua de 66 archivos.

### Integridad de la última copia recibida; listado de respaldo siguiente

El propietario aporta `sha256sum` de `events.json` del snapshot
`891a00db10ca4bcda8a73f5d33fb10a0`: resultado
`bf41223489600b2429eab07b2cd9d08e589372ed9fefa4cd70900e330b1177fa`,
idéntico al SHA de copia del recibo. Integridad puntual comprobada según la
salida aportada; no repetir caso/copia/hash. No acredita todos los snapshots,
un respaldo nuevo o recuperación. Sigue consulta de selección con
`backup_operational.py --profile puerto-umbral --list`, resumida para tres
rutas de esta auditoría y faltantes. Resultado pendiente de captura, sin crear
ZIP, snapshots SQLite o locks. Procedimiento en la
[auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md).

### Recibo V2 leído; comparación de bytes siguiente

La captura de `current.json` confirma el último run Excepciones
`a8a228ff56fc61649041b9740731cc86`, modo corregido, 2 eventos,
`fixture_review`, estado completado y solicitudes de análisis/notificaciones
falsas. `original_sha256` coincide con V2; snapshot
`891a00db10ca4bcda8a73f5d33fb10a0`, SHA de copia
`bf41223489600b2429eab07b2cd9d08e589372ed9fefa4cd70900e330b1177fa`.
Lectura de metadatos completada según captura, sin repetir caso/copia/lectura.
Todavía no demuestra integridad de bytes o respaldo. Se guía `sha256sum` del
`events.json` de ese snapshot; comparar con SHA de copia, no original. Resultado
pendiente de captura, sin escribir archivos o ejecutar aplicación/modelos.
Detalle en la [auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md).

### Inspección de perímetro recibida; siguiente lectura del recibo V2

El propietario acepta continuar con la lectura de estado/perímetro propuesta.
Se revisa y guía el comando existente `labs/puerto_umbral/labctl.py inspect`,
con un filtro JSON de presentación en una segunda terminal. Consulta Docker y
el manifiesto sin iniciar/detener servicios, escribir estado, ejecutar casos,
sondas HTTP o modelo. Se esperan 14 contenedores, targets sin red IP,
pasarelas en loopback, permisos/montajes/límites conformes y red frontal
exclusiva. Procedimiento y límites en la
[auditoría de cierre](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md).
Resultado pendiente de captura; no se declara el perímetro actual validado por
revisar código. Si falla se recoge el error antes de arrancar o corregir nada.
La captura posterior muestra `valid=True`, 14 contenedores, targets sin red IP
y masquerade/ICC desactivados. Once filas visibles son activas, de solo lectura
y usuario `10001:10001`; el inspector revisado emite el resultado agregado tras
comprobar los catorce y la red frontal. **Lectura actual de perímetro completada
según la salida aportada**, sin pedir repetir para filas recortadas o atribuir
inspección independiente del agente. No cierra aún efectos vulnerables F6,
regresión o procesos host. Se guía después la lectura del `current.json` ya
conservado en V2 con `python -m json.tool`, sin escribir o importar la aplicación.
Recibo pendiente de captura; no se repite ningún caso, copia o análisis.

### Auditoría de pendientes reales y documentación vigente — 31/10

Completada la [auditoría de cierre F6/MVP](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md)
con evidencia existente. Distingue requisito del PRD, observación, cobertura
adicional y decisión de alcance; no ejecuta casos o modelos ni acepta fases.
Hay cinco grupos finitos: funcionamiento/límites/regresión, operación,
evaluación/alcance F5, conservación nueva y producto/documentación/aceptación.
No son cinco pruebas ni una orden de ejecutarlas.

Los 45 registros históricos cubren la obligación de registro de F5-AC1, sin
convertir 42/45 en éxito funcional o pedir otra ejecución de 45 por ese criterio.
La incidencia de comandos sigue en F2/regresión. El recorrido único hasta
informe, la recuperación aislada básica y las rondas manuales ya completadas
no se repiten. F4-AC1 admite medir veinte muestras o revisar una desviación;
no hay desviación aceptada. F5-AC2 sigue sin métricas y requiere evaluación
autorizada o decisión expresa de alcance; no se cambia a piloto por defecto.

README, inicio, instalación y repositorios se sincronizan con los recorridos
F6/F7 observados; las actas F4/F5 remiten a esta auditoría sin alterar JSON
históricos. Siguiente paso propuesto: acordar lectura manual de estado/perímetro
y recibos existentes en Parrot, sin nuevos casos, seguimiento o modelo. Aún no
se ha autorizado o realizado esa lectura. Documentación local, sin Git nuevo.

### Ronda representativa F7 terminada — matriz preparada para revisar

Excepciones/corregido/Intento/variante 1 completada según capturas:
`a8a228ff56fc61649041b9740731cc86`, HTTP 400, `controlled_response`, error solo
`code: invalid_fixture`, sin traza en el cuerpo mostrado; 3 peticiones/3 líneas/
2 eventos/2 referencias HTTP. V2 muestra mismo identificador y 2 eventos, sin
coincidencias, con copia conservada sin análisis. No repetir este recorrido.

Los cuatro comportamientos nuevos propuestos están observados. **No faltan más
ejecuciones del bloque representativo F7 propuesto.** Se prepara la
[matriz de cierre educativo](PUERTO_UMBRAL_F7_CIERRE_EDUCATIVO_2026_10_31.md),
revisada contra F7-AC1/2/3 con las evidencias existentes: once ejecuciones,
objetivos y tipo de evidencia para diez categorías, límites de simulación y
ausencia de afirmación de detección F7 completa. Propuesta de aceptación del
alcance educativo lista para revisión del propietario; F7 global y dependencias
F6/MVP siguen pendientes. No convertir las variantes no observadas en una cuota
nueva ni contar Criptografía/Intento/corregido como ejecutado.

Siguiente trabajo: revisar matriz y bloqueadores reales del proyecto (F6,
regresión/operación/recuperación, evaluación o decisión expresa de alcance F5,
documentación V2). Esta revisión no autoriza nuevos casos, suites o LLM.

### Último control del bloque en curso: Excepciones corregida

El propietario acepta un caso manual Excepciones/corregido/Intento/variante 1,
con lectura y conservación V2, sin suites o modelo. Esperado HTTP 400,
`controlled_response`, error solo `code: invalid_fixture`, sin `fictional_trace`;
2 eventos. Resultado y copia pendientes de capturas. Después se revisará la
matriz de evidencias/límites para proponer cierre educativo, sin añadir pruebas
o aceptar F7/proyecto automáticamente. No se repiten los casos anteriores.

### Última recepción: Registro con hueco corregido

El propietario acepta un caso manual Registro/corregido/Intento/variante 1,
con lectura y conservación V2, sin suites o modelo. Esperado HTTP 200,
secuencia ficticia `[1,2,4,5]`, hueco `[3]`, advertencia registrada y
`gap_identified`; 2 eventos. No comprueba continuidad de Apache, rotación o
entrega de notificaciones. Resultado y copia pendientes de capturas. Quedan
dos controles del bloque propuesto incluido este; después quedaría Excepciones.
No repetir anteriores o aceptar F7 global por guiar el caso.
Las capturas posteriores muestran `6a0648c2fed5d6b50f5d08e1a7db6db1`, HTTP
200, secuencia `[1,2,4,5]`, hueco `[3]`, advertencia registrada y
`gap_identified`; 3 peticiones, 3 líneas y 2 eventos / 2 referencias HTTP.
V2 muestra la misma ejecución y 2 eventos, sin coincidencias, con copia
conservada sin análisis. **Recorrido completado según capturas**; no repetir
ni pedir más capturas de este recorrido. Queda únicamente Excepciones del
bloque representativo propuesto, aún sin autorizar o ejecutar. F7 global abierta.

### Última recepción: Integridad modificada corregida

El propietario acepta Integridad/corregido/Intento/variante 1, un caso manual
con lectura y conservación V2, sin suites o modelo. Se guía una revisión del
manifiesto ficticio modificado: esperado HTTP 422, `accepted: false`,
`hmac_sha256` y `manifest_checked`; 2 eventos. Resultado y copia pendientes de
capturas, sin ejecución desde Windows. Quedan tres casos del bloque propuesto
incluido este; después de completarlo quedarían Registro y Excepciones.
No repetir anteriores, alterar el corpus o aceptar F7 global por guiar el caso.
Las capturas posteriores muestran `cc7cdd171465527bc6cd31497755c38a`, HTTP
422, `accepted: false`, `hmac_sha256` y `manifest_checked`; 3 peticiones,
3 líneas y 2 eventos / 2 referencias HTTP. V2 muestra misma ejecución y
2 eventos sin coincidencias; una captura adicional confirma copia conservada
sin análisis. **Recorrido completado según capturas**; no repetir ni pedir
más capturas de este recorrido. Quedan Registro y Excepciones del bloque
representativo propuesto, todavía sin autorizar o ejecutar. F7 global abierta.

### Alcance necesario frente a cobertura exhaustiva — 31/10

El propietario pregunta por el número y necesidad real de pruebas. Actualizado
tras Excepciones: en F7 hay 11 entradas distintas observadas de un catálogo de 54:
6 normales más Configuración, Suministro, Integridad, Registro y Excepciones/
Intento, corregido/variante 1. **Las 43 no observadas no son una cuota obligatoria
de salida del PRD.** El bloque representativo propuesto está terminado.
Criptografía corregida sigue la misma rama de derivación que el control normal:
se propone documentar esa equivalencia por código y conservar el intento como
no ejecutado, sin puntuarlo como superado.

Propuesta para decidir el cierre educativo F7: observar esos cuatro controles
y revisar la matriz final frente a F7-AC1/2/3 (objetivo/evidencia, límites de
simulación y afirmaciones de detección respaldadas). No es aceptación anticipada
ni cambio del corpus. No elimina dependencias F6/MVP, positivos/negativos y
regresión, pendientes operativos o evaluación del detector. La cobertura de
otros modos/variantes se distingue de estos criterios; no se declara 54/54.

Suministro/corregido/Intento/variante 1 queda completado según capturas:
`3708b145de707ced3497dbb37883f07d`, HTTP 422, hashes distintos y `accepted:
false`; 3 peticiones/3 líneas/2 eventos/2 referencias HTTP. V2 muestra misma
ejecución y 2 eventos, sin coincidencias, con copia conservada sin análisis.
No repetir. Después se completaron Integridad, Registro y Excepciones,
registrados al inicio; no quedan controles del bloque representativo propuesto.
Sigue revisión de matriz educativa y pendientes F6/MVP. La revisión final
documental V2 y la decisión explícita de cierre del proyecto siguen pendientes.

### Reanudación del 31/10 — primer caso adverso F7 corregido

El propietario retoma y se levanta la pausa para guiar Configuración/corregido/
Intento de ataque/variante 1, manual una vez, lectura y conservación en V2, sin
suites o modelo. Los seis normales anteriores siguen completados y no se
repiten. La entrega previa `1fdfed1` se publicó y verificó al cerrar; HEAD local
coincide y el árbol estaba limpio al retomar. No se asumen servicios VM abiertos;
se facilita el arranque manual existente si están detenidos, sin instalaciones,
builds o arranque desde Windows.

Expectativa: HTTP 200, depuración desactivada y configuración mínima sin
`debug_trace`; 2 eventos. El caso `attempt` corregido devuelve el mismo contenido
mínimo que el normal, sin afirmar rechazo HTTP o configuración real segura.
Resultado y conservación pendientes de capturas. F7 global continúa abierta;
notas nuevas locales posteriores a `1fdfed1`, sin publicación adicional.
Las capturas posteriores confirman `9370f0028216a9926d2ca38ef0c2b1ee`, HTTP
200 y configuración mínima sin depuración ni `debug_trace`; 3 peticiones,
3 líneas y 2 eventos / 2 referencias HTTP. V2 muestra la misma ejecución y
2 eventos, sin coincidencias, con copia conservada sin análisis. **Configuración
corregida/Intento/variante 1 completada según capturas**. No repetir. Siguiente
candidato Suministro/corregido/Intento/variante 1, todavía sin autorizar o
ejecutar. El resultado no verifica configuración real; F7 global sigue abierta.

### Punto de reanudación guardado — cierre del 30/10 y pausa

**Ronda de seis controles normales F7 completada según capturas**, todos
corregido/Uso normal/variante 1: Configuración, Suministro, Criptografía,
Integridad, Registro y Excepciones. Los seis tienen respuesta esperada,
lectura en V2 y mensaje de copia conservada sin análisis. No repetirlos.
Último caso: `b4ca524b483be65d9549d6b132f25fe7`, HTTP 200,
`controlled_response`, `error: null`, 3 peticiones/3 líneas, 2 eventos /
2 referencias HTTP; misma ejecución y 2 eventos en V2, con copia conservada.
Detalle e identificadores en el [acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md).

El propietario autoriza commit/push documental con `[skip ci]` y pide seguir
mañana. Se completa esa publicación y se verifica remoto/árbol limpio antes
de parar. La identidad de la entrega es la del commit que contiene este punto.
**Después de publicar, pausa hasta que el propietario retome.** No hay tareas
programadas; no se inician servicios, casos, suites o modelos durante la pausa.

Al retomar, revisar este punto y la situación de la VM comunicada por el
propietario. No asumir servicios abiertos ni arrancarlos desde Windows. El
siguiente bloque propuesto es revisar condiciones adversas de artefactos F7,
modo corregido, variante 1, manualmente y con alcance por acordar; todavía sin
ejecutar o autorizar. F6/F7 globales, validaciones ampliadas del MVP y evaluación
del detector siguen pendientes. La autorización Groq anterior sigue consumida.
La entrega actual solo modifica documentación: Parrot puede actualizarse con
`git pull --ff-only`, sin build, reinstalación o reinicio por estos cambios.
Las notas inferiores recogen la secuencia histórica y sus pendientes de entonces.

### Último caso de esta sesión y pausa solicitada

El propietario autoriza Excepciones/corregido/Uso normal/variante 1, con
lectura y conservación en V2, sin suites o modelo. Expectativa por código:
HTTP 200, `controlled_response`, `error: null` y 2 eventos. Resultado y copia
pendientes de capturas. Después autoriza commit/push de las cuatro actas
pendientes con `[skip ci]` y pide seguir mañana. Primero se documentará el
resultado, luego se publicará y verificará el remoto/árbol limpio; finalmente
se guardará el punto de reanudación y se detendrá el trabajo. No se inician
otros casos o recordatorios por esa petición. Los cinco normales anteriores
no se repiten; F7 global y demás validaciones continúan pendientes.

### Siguiente revisión manual F7: Registro normal corregido

El propietario acepta un caso Registro/corregido/Uso normal/variante 1,
con lectura y conservación V2, sin suites o modelo. Se guía la revisión de
una secuencia ficticia completa: expectativa HTTP 200, `[1,2,3,4,5]`, lista
de huecos vacía, `warning_recorded: false` y `no_warning`. No comprueba
continuidad real de Apache o entrega de avisos. Se esperan 2 eventos y puede
no haber coincidencias F6. Resultado y conservación pendientes de capturas;
los cuatro controles normales anteriores no se repiten. F7 sigue abierta.
Las capturas posteriores muestran `2c26ab55cda7b3e95eccfbf5080580b2`, HTTP
200, secuencia ficticia completa, sin huecos o aviso; 3 peticiones, 3 líneas y
2 eventos / 2 referencias HTTP. V2 muestra misma ejecución y 2 eventos, sin
coincidencias, con copia conservada sin análisis. **Registro normal corregido,
variante 1, completado a ese alcance**. No repetir. Siguiente candidato
Excepciones/corregido/Uso normal/variante 1, todavía propuesto sin ejecutar.
F7 global y comprobaciones de continuidad real o entrega de avisos siguen abiertas.

### Siguiente revisión manual F7: Integridad normal corregida

El propietario acepta un caso Integridad/corregido/Uso normal/variante 1,
con lectura y conservación V2, sin suites o modelo. Se guía una revisión del
manifiesto ficticio: expectativa HTTP 200, `accepted: true`, `hmac_sha256` y
`manifest_checked`; no verifica manifiestos reales. Se esperan 2 eventos y
puede no haber coincidencias de reglas F6. Resultado y conservación pendientes
de capturas. Los tres casos normales anteriores no se repiten; F7 sigue abierta.
Las capturas posteriores muestran `38d690cd4161439e73f4d38df256e0d1`, HTTP
200, manifiesto ficticio aceptado, `hmac_sha256` y `manifest_checked`; 3
peticiones, 3 líneas y 2 eventos / 2 referencias HTTP. V2 muestra misma
ejecución y 2 eventos, sin coincidencias, con copia conservada sin análisis.
**Integridad normal corregida, variante 1, completada a ese alcance**. No se
repite. Siguiente candidato Registro/corregido/Uso normal/variante 1, todavía
propuesto sin ejecutar. F7 global y evaluación del contenido siguen pendientes.

### Siguiente revisión manual F7: Criptografía normal corregida

El propietario acepta un caso Criptografía/corregido/Uso normal/variante 1,
con lectura y conservación V2, sin suites o modelo. Se guía una revisión del
artefacto ficticio: expectativa HTTP 200, `scrypt`, sal y derivación con valor,
`salted_password_derivation`; la sal aleatoria impide fijar una respuesta
idéntica entre casos. No repetir para comparar hashes. Se esperan 2 eventos;
las reglas F6 no evalúan el contenido F7. Resultado y conservación pendientes
de capturas; no acepta F7 global o criptografía de producción.
Recepción posterior: `8fa4ffafefc52573988c36dd75fbcbb5`, HTTP 200, `scrypt`,
sal y derivación con valor, `salted_password_derivation`; 3 peticiones, 3 líneas
y 2 eventos / 2 referencias HTTP. V2 muestra misma ejecución y 2 eventos, sin
coincidencias. Ejecución y lectura observadas; conservación pendiente de
confirmación visual, sin banner de copia en la captura. Se guía solo conservar
esa auditoría, sin repetir caso o comparar hashes con ejecuciones nuevas.
La captura posterior confirma copia conservada sin análisis, con la misma
ejecución, 2 eventos y SHA. **Recorrido normal de Criptografía corregida,
variante 1, completado según capturas**. No repetir. Configuración, Suministro
y Criptografía normales tienen lectura y conservación informada en V2;
resto de cobertura y aceptación F7 pendientes. Siguiente candidato Integridad/
corregido/Uso normal/variante 1, todavía propuesto sin ejecutar.

### Siguiente revisión manual F7: Suministro normal corregido

El propietario acepta continuar con un único caso Suministro/corregido/Uso
normal/variante 1 y su lectura/conservación en V2, sin suites o modelo. Se guía
«Revisar artefacto ficticio» una vez; expectativa HTTP 200, hashes esperado y
recibido iguales y `accepted: true`, sobre referencia local ficticia. No se
verifican paquetes o proveedores reales. Se esperan 2 eventos; la ausencia de
coincidencias de reglas F6 no evalúa el artefacto F7. Resultado y conservación
pendientes de capturas. Configuración normal anterior no se repite.
Las capturas posteriores confirman HTTP 200 con hashes iguales y artefacto
aceptado, ejecución `d34aba7e1dfae17f750c1ac7c8722be1`; 3 peticiones, 3 líneas
y 2 eventos / 2 referencias HTTP. V2 muestra la misma ejecución y 2 eventos,
sin coincidencias, con copia conservada sin análisis. **Suministro normal
corregido, variante 1, completado a ese alcance**. No se repite. El siguiente
candidato es Criptografía/corregido/Uso normal/variante 1, todavía propuesto
sin iniciar. F7 global y evaluación del contenido siguen pendientes.

### Siguiente revisión manual F7: Configuración normal corregida

La entrega de actas se publicó en `dc9fb17`, con remoto coincidente y árbol
limpio. El propietario solicita continuar: se guía un único caso manual
Configuración/corregido/Uso normal/variante 1, lectura y conservación en V2,
sin suites o modelo. Se espera HTTP 200, `debug_enabled: false` y
`minimal_configuration` en un artefacto ficticio; no una auditoría real del
despliegue. La ausencia de observaciones en V2 no evalúa el contenido F7.
Resultado pendiente de capturas y copia informada, sin ejecución desde Windows.
Los recorridos completados de F6 no se repiten; aceptación global pendiente.
Las capturas siguientes muestran Configuración normal corregida completada:
`608700e1fe2c6d7d91f4f275a770a56a`, HTTP 200, depuración desactivada y
configuración mínima; 3 peticiones/3 líneas y 2 eventos. V2 muestra la misma
ejecución y 2 eventos, sin coincidencias. Ejecución y lectura observadas;
**conservación pendiente de confirmación visual**, pues el recorte no incluye
su mensaje. Se guía solo conservar esta copia, sin repetir caso o análisis.
La captura posterior confirma copia conservada sin análisis, con la misma
ejecución, 2 eventos y SHA. **Recorrido normal de Configuración corregida
completado según capturas**, sin recibo local o verificación independiente
nuevos. No repetir. El siguiente candidato es Suministro/corregido/Uso normal/
variante 1; todavía propuesto, sin ejecutar. F7 global sigue abierta.

### Siguiente validación manual: rechazos corregidos

Las cinco actas se publicaron en `d3e0b14`, con remoto verificado y árbol
limpio. El propietario solicita continuar con lo siguiente: se guía primero
Cargas/corregido/Intento de ataque/variante 1, seguido de lectura y conservación
de auditoría en V2, sin suites o modelo. El resultado esperado es HTTP 403 y
observación por reglas de acceso rechazado. Todavía no hay captura de ese
caso; no modifica las aceptaciones pendientes ni repite los controles normales.
Las capturas posteriores muestran Cargas rechazado con HTTP 403 y dos eventos
en V2, con «Acceso al objeto rechazado» para `foreign-1`. Una captura adicional
confirma copia conservada sin análisis. Se completa ese recorrido de variante 1
corregida; sigue Preferencias como control HTTP de rechazo. No se repite Cargas
ni se atribuyen métricas LLM o protección universal.
Después se observa Preferencias rechazado en la prueba HTTP de origen/token:
403, `changed: false`, misma ejecución y 2 eventos en V2, con la regla de
solicitud de otro origen rechazada y copia conservada. La comprobación de
navegador sigue pendiente; continúa Baliza, rechazo corregido de variante 1.
La siguiente recepción muestra Baliza rechazado con 403 para diagnóstico,
misma ejecución y 2 eventos en V2, regla «Lectura del señuelo rechazada» y
copia conservada sin análisis. Sigue Atraque sin aprobación, variante 1
corregida; los demás criterios y comprobaciones de navegador siguen pendientes.
Las capturas siguientes confirman Atraque sin aprobación rechazado con 409 y
permiso pendiente, dos eventos y «Aprobación exigida» en V2, con copia
conservada. Se observan así los cuatro rechazos HTTP corregidos de variante 1.
Sigue Bitácora, control de codificación con HTTP 200 esperado y revisión del
iframe; no es aceptación de F6 ni prueba de navegador CSRF.
La recepción de Bitácora confirma HTTP 200 con entrada codificada, iframe
mostrando el texto literal sin ejecución confirmada y 3 eventos en V2, con
copia conservada. Termina la ronda corregida de variante 1: cuatro rechazos
HTTP y un control de codificación, todos con lectura y conservación informada.
Sigue pendiente F6 completa, en particular navegador CSRF, reutilización de
permiso, otros modos/variantes, aislamiento/regresión y evaluación del detector.
El candidato siguiente es una sesión nueva para comprobar el formulario CSRF
en navegador; su alcance debe acordarse antes de prepararla.
El propietario autoriza expresamente ese recorrido manual corregido: una
preparación nueva, sesión ficticia, formulario normal y formulario del otro
origen, confirmación en el panel y lectura/conservación en V2, sin suites o
modelo. Se guían los pasos dentro de su ventana de cinco minutos; los
resultados nuevos siguen pendientes de capturas y no se declaran aceptados.

Recepción posterior: las cuatro capturas de la ejecución
`fe73eb53a5030885bb395eeb7613ac5c` muestran formulario normal con
`changed: true`, formulario cruzado con `changed: false`, confirmación de
rechazo en navegador y cinco eventos coincidentes en V2, con copia conservada
sin análisis. **Recorrido CSRF corregido en navegador completado a ese alcance**;
no repetirlo. El panel informa 4 peticiones del ejecutor y 7 líneas Apache
correlacionadas. Las dos observaciones de rechazo son coherentes con la sonda
HTTP y el formulario, sin inspección de eventos crudos o recibo local nuevo.
El detalle y el SHA mostrado están en el [acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md).
El siguiente candidato manual es reutilización de permiso en Atraque corregido,
intento variante 3; todavía sin ejecutar ni acordar ese nuevo alcance. F6/F7 y
el cierre global siguen abiertos. Sin llamadas al modelo o publicación Git.
El propietario acepta después continuar con ese único caso manual y su lectura/
conservación en V2. Se guía una pulsación de ejecutar, ya que la variante 3
incluye aprobación, consumo y segundo uso de `dock-3`. Se espera 409 con el
permiso todavía consumido y observación «Reutilización del permiso rechazada».
Resultado pendiente de capturas, sin ejecutar el caso desde Windows ni iniciar
suites o modelo. El recorrido CSRF anterior no se repite.
Recepción posterior: Atraque variante 3 corregida se muestra completado,
ejecución `b1aa23bd017b47ec814fe8d3c52ecd2e`, HTTP 409 y permiso consumido
antes y después; 6 peticiones, 6 líneas correlacionadas y 5 eventos. V2 muestra
la misma ejecución y conteo, «Reutilización del permiso rechazada» para `dock-3`
y copia conservada sin análisis. **Recorrido de reutilización corregida
completado según capturas**, sin recibo local o hash independiente nuevo.
No se repite este caso ni CSRF. F6 global continúa abierta por cobertura,
aislamiento/regresión y evaluación. El siguiente bloque propuesto es revisión
manual F7, comenzando Configuración/corregido/Uso normal/variante 1; todavía
sin ejecutar ni acordar ese nuevo alcance. Detalle en el acta F6/F7.

### Reanudación del 30/10

El propietario vuelve y solicita continuar desde el punto guardado, reiniciando
la aplicación en Parrot y siguiendo las pruebas. Se levanta la pausa para el
bloque manual descrito: Bitácora, Preferencias, Baliza y Atraque, todos en modo
corregido, Uso normal y variante 1, uno a uno, con lectura y conservación de sus
auditorías en V2. No se incluyen suites, otros casos, modelo o notificaciones.

Primero se guía el arranque conjunto desde la instalación existente; su éxito
todavía no se atribuye sin salida real. No se presupone que los servicios
siguieran abiertos ni se ejecuta la VM desde Windows. No hay cambios de código
operativo desde `5bf154a` que requieran reinstalar o recompilar por estas actas.
El primer caso pendiente será Bitácora. Cargas y su copia/recibo anteriores
permanecen completados, sin repetición. Los cuatro casos y el nuevo arranque
están pendientes de evidencia del propietario.
Primera recepción del bloque: Bitácora/corregido/Uso normal/variante 1 se
muestra completada con HTTP 200 y «Revisión de baliza»; 4 peticiones, 4 líneas
Apache y 3 eventos capturados. Su lectura/conservación en V2 aún están
pendientes. Preferencias, Baliza y Atraque no se declaran ejecutados.
La captura siguiente confirma lectura de Bitácora en V2, misma ejecución y
3 eventos, y mensaje de copia conservada sin análisis. Se completa ese
recorrido normal con conservación informada en pantalla. El siguiente control
es Preferencias; Baliza y Atraque continúan después, todos con la misma
selección corregido/Uso normal/variante 1. No se repite Cargas o Bitácora.
Después se observa Preferencias completado, HTTP 200 con `demo-1` y
`changed: true`; mismo identificador y 2 eventos en V2, con copia conservada
sin análisis. Este control normal HTTP queda completado a ese alcance;
Baliza y Atraque son los dos controles pendientes del bloque reanudado.
La recepción siguiente completa Baliza normal: HTTP 200 para `/public` con
`UMBRAL_PUBLIC_BEACON`, misma ejecución y 2 eventos en V2, copia conservada
sin análisis. Atraque es el único control pendiente de este bloque normal.
La última recepción completa Atraque: HTTP 200, permiso aprobado y después
consumido; misma ejecución y 4 eventos en V2 con copia conservada. Queda
**completado el bloque de cuatro controles normales del 30/10**, con lectura
y conservación informada en V2. Son 15 peticiones/15 líneas informadas/11
eventos; incluido Cargas del 29/10, cinco controles, 18/18/13. No se considera
una suite nueva o evaluación del detector. No se repiten los casos normales.
El propietario acepta después publicar las cinco actas pendientes mediante
commit/push `[skip ci]`, sobre `5bf154a` comprobado con el remoto. La identidad
se obtiene del commit que incorpora la nota de distribución del acta F6/F7;
el resultado de Git se verifica al terminar. Es una entrega documental sin
ejecuciones nuevas o aceptación de criterios pendientes; en Parrot basta
actualizar por Git, sin reinstalar, recompilar o reiniciar servicios.

### Punto de reanudación guardado — pausa del 29/10

El propietario indica que continuará mañana (30/10 según la fecha de esta
sesión) y pide guardar el siguiente paso. Se detiene el trabajo tras registrar
este punto, sin ejecutar nuevos casos, servicios, modelos o publicaciones.
No se ha solicitado ni creado un recordatorio automático.

- **Completado:** un control normal Cargas, modo corregido, variante 1;
  auditoría de 2 eventos visible en V2, copia conservada y recibo local observado.
  Ejecución `10fea5f6cbef9d88320ca767cc11e0b4`; copia
  `ed70066797f1f68f7df55b7ecb18247d`. No repetir este recorrido.
- **Siguiente bloque propuesto, todavía sin ejecutar:** Bitácora, Preferencias,
  Baliza y Atraque; los cuatro en modo corregido, **Uso normal**, variante 1,
  manualmente uno a uno, con lectura y conservación de sus auditorías en V2.
  No incluye suites ni llamadas al modelo. La respuesta recibida aplaza el
  bloque; no autoriza iniciarlo durante la pausa.
- **Al retomar:** revisar este punto y el [acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md),
  acordar la continuación y comprobar el estado que comunique el propietario.
  No se presupone que la VM o sus servicios sigan abiertos.
- **Distribución:** último commit publicado `5bf154a`; las cinco actas actuales
  siguen guardadas localmente, sin commit/push posterior. El código no cambia
  por este registro. La configuración Groq y su análisis anterior se conservan.

### Resumen de evidencia disponible, actualizado al 31/10

| Área | Evidencia disponible | Límite |
| --- | --- | --- |
| Distribución V2 | Repositorio público y entrega base v0.1.0; código F6/F7 en `cc363af`, actas normales posteriores publicadas hasta `1fdfed1` con remoto verificado al cerrar el 30/10; revisión actual local | No nueva release o CI atribuida a los commits `[skip ci]`; no se presume HEAD actual de la VM |
| Puerto Umbral F1/F2 | Prototipo privado, cinco familias locales y dos modos | Corpus histórico 42/45; tres fallos de comandos preservados |
| F3, recorrido de integración | Un snapshot de 17 líneas, análisis Groq, publicación y lectura en V2 | No evaluación de los 45 casos |
| F4 | Inicio, pausa, reanudación, parada, vencimiento y reapertura sin auto-resume | Condiciones ampliadas y latencias individuales pendientes |
| F5, conservación | Copia y recuperación aislada de 66 archivos, SQLite e informe verificados en Parrot | Sin promover datos recuperados ni restaurar la VM completa |
| Interfaz | Autoría visible en cabecera y vistas Fuente/Auditoría de Actividad V2 observadas por capturas | No revisión actual completa de móvil/teclado o enlaces abiertos |
| F6/F7 | [Acta de ampliación](PUERTO_UMBRAL_F6_F7_2026_10_29.md): normales e intentos F6 corregidos, CSRF corregido en navegador y reutilización de permiso observados; once recorridos F7 corregidos con lectura/copia V2 | Ronda educativa representativa F7 terminada; aceptación global y positivos/aislamiento/regresión F6, conservación de auditorías nuevas y evaluación pendientes |

El [estado consolidado](PUERTO_UMBRAL_ESTADO_ACTUAL_2026_10_26.md), el
[acta del análisis y recuperación](PUERTO_UMBRAL_ANALISIS_ACOTADO_2026_10_27.md)
y la [evaluación histórica F5](PUERTO_UMBRAL_F5_2026_10_27.md) contienen los
resultados originales. Este documento no reemplaza sus denominadores ni
reescribe los JSON históricos.

## Trabajo de cierre, en orden

| ID | Trabajo | Evidencia necesaria para cerrarlo | Estado |
| --- | --- | --- | --- |
| DOC-01 | Sincronizar README, arquitectura, inicio y plan V2 | Enlaces válidos y distinción entre estado actual e historia | Consolidación del 02/11 enlazada desde README/estado/plan/auditoría; revisión básica de producto recibida y guía actualizada; nueve Markdown/120 referencias locales sin ausencias; revisión final conjunta pendiente |
| F6-01 | Contrato de auditoría de aplicación y correlación | Actor, recurso, acción, decisión y secuencia; sin claves, tokens o etiquetas esperadas del corpus | Cinco normales, cinco intentos de variante 1 corregida, CSRF de navegador corregido y reutilización corregida leídos y conservados en V2 según capturas; recibo local del normal Cargas observado; criterios ampliados pendientes |
| F6-02 | XSS almacenado, IDOR, CSRF, SSRF y permisos de atraque | Modos vulnerable/corregido, controles normales, reset, evidencia HTTP/negocio y prueba de navegador cuando corresponda | Corregidos normales/negativos, CSRF en navegador, reutilización de permiso y comparación Cargas observados; perímetro configurado válido; otros efectos representativos y regresión pendientes; Baliza vulnerable solo tiene fila sin resultado recibido |
| F7-01 | Ejercicios para configuración, suministro, criptografía, integridad, registro y excepciones | Catálogo con tipo de ejercicio explícito y artefactos ficticios verificables | Once recorridos corregidos/variante 1 con lectura y copias conservadas según capturas; ronda representativa terminada y matriz educativa revisada documentalmente; propuesta de aceptación de ese alcance lista; resto de cobertura/dependencias y aceptación global pendientes |
| EVAL-01 | Resolver o conservar con causa los fallos del corpus actual | Resultados actuales trazables; el histórico 42/45 permanece intacto | Los 45 históricos tienen evidencia/causa; corrección de comandos verificada en normal corregido y vulnerable variante 1 del 02/11; variantes 2/3 históricas preservadas sin nueva ejecución; regresión global F2/F6 pendiente; no repetir45 por F5-AC1 |
| EVAL-02 | Evaluar detección y falsas alarmas del corpus definido | Expectativas fijadas antes de puntuar, resultados por caso, presupuesto, modelo y uso | Métricas sin medir: bloqueo F5-AC2, requiere evaluación autorizada o decisión expresa que cambie alcance; permiso Groq anterior consumido |
| OPS-01 | Condiciones ampliadas F4 y regresión de aislamiento | Observaciones reproducibles de rotación, truncado, fallo, cuotas y ausencia de actividad automática | Perímetro actual válido/14 contenedores y preflight de cierre posterior al respaldo recibidos; cierre básico acreditado a ese alcance, discontinuidad/latencia y regresión ampliadas pendientes |
| UX-01 | Lectura final, móvil, teclado y exportación de evidencias | Comprobación del producto actual y ausencia de contenido sin fuente | Bloque básico de ambas interfaces completado a su alcance; zoom 200 %, exportación y consultas adicionales sin observar como cobertura adicional, no nuevas cuotas de salida |
| DOC-02 | Revisar documentación completa de V2 con el propietario | README/manual/estado/catálogo/actas coherentes y enlaces comprobados | Consolidación documental del 02/11 preparada; revisión final conjunta pendiente, sin dar por aceptados criterios técnicos abiertos |
| ACC-01 | Decisión de cierre y alcance de comunicación | Criterios F0–F7 revisados expresamente, limitaciones pendientes visibles | No aceptado |

F6 y F7 pueden prepararse en código sin declarar superado su requisito de
aceptación del MVP. Las dependencias del PRD siguen vigentes para el cierre.
La fecha objetivo no autoriza declarar completado un criterio no observado.

El propietario elige después mantener solo desarrollo y revisión de código;
decidirá las pruebas más adelante. No se interpretará la petición de todas las
fases o la fecha de LinkedIn como permiso para iniciar suites o llamadas LLM.
La primera preparación de F6/F7 y la sincronización documental pasan revisión
estática de sintaxis, tipos, configuración y enlaces; no se confunde esa revisión
con los recorridos de aceptación que aún deben decidirse.
El propietario autoriza a continuación el paso 1 de revisión de código. Se
completa localmente con correcciones de concurrencia, ventana manual,
validación/lectura acotada y conservación de evidencias, registradas en el
[acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md). Los criterios operativos siguen
pendientes. Después el propietario autoriza commit/push del paquete revisado
con `[skip ci]`; su identidad queda en el commit que incorpora la nota de
distribución del acta F6/F7. Publicar no ejecuta la validación ni actualiza la VM.
La publicación se completa en `cc363af`, con remoto coincidente y árbol limpio.
El propietario autoriza después el paso 3 y sus capturas confirman ese commit
en Parrot y la compilación completa del frontend con Webpack y TypeScript.
**Paso 3 completado**; no acredita todavía arranque de V2, construcción o
disponibilidad de la topología nueva, escenarios o métricas del detector.
El siguiente bloque de arranque y revisión de pantallas queda autorizado por
el propietario, limitado a disponibilidad y navegación en el perfil corregido;
su resultado permanece pendiente. No autoriza recorrer casos ni repetir LLM.
Las capturas siguientes acreditan salida «Consola lista» y acceso al panel de
Puerto Umbral, que informa 14 contenedores. El alcance de disponibilidad del
panel queda observado; falta la captura de Actividad V2 y no se validan casos.
La petición adicional de autoría en cabecera se implementa en HTML/CSS local;
su recepción en Parrot y revisión visual quedan pendientes de distribución.
Recepciones posteriores: autoría visible y vistas de Actividad V2 acreditadas
por capturas. La fuente conserva el snapshot corregido histórico de 17 líneas
y se muestra antigua; la auditoría avanzada se muestra sin datos, sin error.
El bloque de disponibilidad y revisión básica de pantallas queda completado.
No cambia la aceptación de escenarios, F4 ampliada o métricas de detección.

## Calendario histórico propuesto, sustituido por el objetivo del 05/11

| Fecha | Prioridad de trabajo |
| --- | --- |
| Jueves 29/10 | Documentación V2 al día y contrato de ampliación F6 |
| Viernes 30/10 | Escenarios F6 y recibos de estado/identidad |
| Sábado 31/10 | Ejercicios F7 y matriz de categorías/evidencias |
| Domingo 01/11 | Validación acotada, correcciones y métricas si su ejecución se autoriza |
| Lunes 02/11 | Congelación de alcance, revisión del laboratorio y documentación V2 con el propietario |
| Martes 03/11 | Publicación del propietario en LinkedIn con afirmaciones respaldadas |

Si una validación no está disponible a tiempo, se registrará como pendiente y
se revisará la fecha o el alcance con el propietario; no se omitirá para dar
el proyecto por terminado. Este plan no configura tareas programadas ni
publica mensajes en LinkedIn.

## Límites de ejecución que siguen vigentes

La única autorización de análisis Groq ya se consumió. No se inician llamadas,
escenarios, suites o recorridos automáticos nuevos por este documento. Antes
de ejecutar el siguiente bloque se necesita concretar su alcance y, si usa
modelo, número máximo de solicitudes, proveedor/modelo y presupuesto. No
solicitar ni publicar claves; utilizar la configuración propia de Parrot.

Los escenarios permanecen locales y confinados. El prototipo privado de Sites
mantiene su identidad y audiencia; no se despliega el backend vulnerable allí.
F7 distinguirá ejercicio HTTP real, demostración con datos ficticios y revisión
de artefactos. Un mapa educativo de diez categorías no acredita detección de
todas ellas por V2 ni explotación real de todos los ejemplos.

## Qué respaldará la comunicación final

Podrán describirse las funciones implementadas y los recorridos observados,
con sus versiones y límites. Los porcentajes de detección solo procederán de
la evaluación identificada del detector; no del corpus funcional 42/45.
La nueva ampliación no será una actualización de la release v0.1.0 hasta que
se decida expresamente una entrega identificada. El texto de LinkedIn y la
revisión documental final se prepararán tras cerrar el laboratorio, como
solicita el propietario.

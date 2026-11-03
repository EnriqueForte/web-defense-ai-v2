# Web Defense AI V2 y Puerto Umbral — estado de entrega

Publicación solicitada por el propietario el 03/11: entrega de 21 rutas,
16 Markdown y eliminación de cinco SVG de plantilla sin uso, con `[skip ci]`.
Base comprobada tras fetch: `7d4d10f1d3a0c26f04fdb14f7766a57a01e23ba2`,
`main` igual a `origin/main`, divergencia 0/0 y staging inicial vacío. La
identidad de esta entrega es el commit que incorpora esta nota; la publicación
se verifica después del push, sin atribuirle pruebas o aceptación adicionales.
En Parrot, conservar cambios locales y actualizar con `git pull --ff-only`
cuando corresponda. No requiere recompilar frontend, reinstalar o reiniciar
por defecto: solo cambia documentación y assets de plantilla no utilizados.

Actualizado el 03/11/2026, Europe/Madrid. **Aplicaciones desarrolladas y
recorridos básicos observados en Parrot; decisiones de alcance F4/F5/F6
resueltas y matriz educativa F7 aceptada.** Resta la consolidación/aceptación
final del conjunto de entrega. Este resumen conserva las omisiones y no
declara superadas verificaciones no realizadas.

## Decisión más reciente del propietario — 03/11

El propietario acepta expresamente la matriz F7 actualizada y decide cerrar
también F4/F5 si requieren pruebas. **F4 y F5 quedan cerradas por decisión
expresa de alcance, sin ejecutar las verificaciones restantes.** F6 conserva
su cierre previo. F7 queda aceptada en el alcance educativo de la matriz.

La rotación/discontinuidad real restante no está verificada; las métricas del
detector F5 no están medidas y los originales siguen sin localizar. Evaluación,
pruebas del empaquetador y ejecutor/puntuador F5 pendientes se retiran del
trabajo de esta entrega. No se reabren pruebas, búsquedas o ensayos para cerrar.
Los límites F2/F3 y resultados ya recibidos se conservan. El
[registro vigente de decisiones](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md)
prevalece sobre propuestas y pendientes históricos inferiores.

## Antecedentes de decisiones y recepciones

**Decisión posterior del 03/11: F6 cerrada.** El propietario decide no realizar
las pruebas restantes porque bloquean la conversación. Se cierra la fase por
decisión expresa de alcance, conservando la evidencia recibida y registrando
como omitidas/no verificadas Bitácora/Preferencias vulnerables, resultado
vulnerable de Baliza y regresión F6 restante. No se reabren esos recorridos ni
se consideran pruebas aprobadas. Se continúa trabajo documental sin ejecución
de pruebas. F4/F5/F7 y la aceptación final mantienen sus estados propios.
Las propuestas F6 inferiores describen el estado previo a esta decisión.

**Revisión documental F7 posterior, 03/11: completada.** PRD, catálogos,
presentación y once identificadores de evidencia cotejados por lectura;
matriz de diez categorías y dictamen F7-AC1/2/3 listos para decisión final
del propietario. El intento Criptografía no observado y las 43 entradas sin
resultado conservan su estado; no se declara detección completa. No se
ejecutan pruebas, programas de validación, casos, modelos o servicios. El
[dictamen F7](PUERTO_UMBRAL_F7_CIERRE_EDUCATIVO_2026_10_31.md) sustituye su
antigua revisión documental pendiente, sin aceptar automáticamente la fase.

**Actualización vigente, 03/11:** entrega
`7d4d10f1d3a0c26f04fdb14f7766a57a01e23ba2` publicada y verificada en
`origin/main`; actualización Parrot confirmada por el propietario. Se fija el
jueves 5 de noviembre como objetivo de cierre del desarrollo. El
[plan mínimo F6 y operación](PUERTO_UMBRAL_CIERRE_MINIMO_2026_11_03.md)
concreta tres candidatos funcionales, revisión del contrato
por código y la decisión pendiente sobre rotación de la fuente Docker. F5
conserva el pendiente de originales/evaluación. No se reduce el alcance F0–F7
por la fecha ni se repiten pruebas o arranques completados. Las notas de
preparación/publicación inferiores son antecedentes, no órdenes nuevas.
La [revisión integral del 03/11](REVISION_INTEGRAL_2026_11_03.md) reúne el dictamen
actual y la organización documental. La recepción siguiente resuelve Atraque;
los otros dos candidatos quedan después omitidos por decisión de cierre F6.

Recepción posterior del 03/11: Atraque vulnerable/Intento/variante 1 completado
por capturas de resultado y auditoría V2 conservada: HTTP 200, permiso
`pending → consumed`, mismo run con prefijo `b2df9053`, dos eventos y observación
«Atraque ejecutado sin aprobación» para `estibador.demo`/`dock-1`. Comparación
puntual con rechazo corregido previo; no repetir caso/copia. Bitácora y
Preferencias del plan mínimo quedan omitidas tras el cierre expreso F6,
igual que el resultado vulnerable de Baliza; demás criterios mantienen su estado.

Publicación solicitada después el 02/11: entrega acumulada de once archivos,
con actas F4, preparación F5 y regresiones de perfiles. Se identifica por el
commit que contiene esta nota, con `[skip ci]`; la coincidencia remota se
comprueba al terminar el push. Los cinco tests de perfiles ya pasaron; los
cinco del empaquetador F5 siguen sin ejecutar y la evaluación sigue pendiente
de localizar sus originales. En Parrot basta actualizar Git conservando cambios
locales: no requiere recompilar frontend ni reinstalar o reiniciar servicios.
La referencia verificada anterior indicada debajo se conserva como antecedente.

Actualización posterior del 02/11: observador F4 y cinco pruebas aisladas
correctas preparados junto a las actas; el propietario autoriza su commit/push
en una entrega de trece archivos con `[skip ci]`. Se identifica por el commit
que incorpora esta nota y se verifica al finalizar Git. `91a101e` sigue siendo
la referencia de los servicios ya observados en Parrot; el observador nuevo
es independiente y no requiere otro build de interfaz. Las indicaciones
«local/publicación pendiente» de las recepciones anteriores describen su
momento de preparación, sin sustituir la verificación final de publicación.

Entrega anterior publicada y verificada al cerrar su publicación:
`586f050a85f21e0d4014a8d571453acdb58627fd`, observador independiente y actas.
`91a101e3831009da1ba25589798dc733b0222ce0` conserva la referencia de los
servicios y opción manual del lanzador. Este párrafo conserva el estado anterior
a la publicación `7d4d10f1d3a0c26f04fdb14f7766a57a01e23ba2` indicada arriba;
las nuevas actas posteriores a esa entrega siguen locales hasta otra publicación.

## Uso disponible

Desde la raíz del proyecto en Parrot:

```bash
python3 webdefensev2.py
```

Inicia V2 y Puerto Umbral, con fuente V2 corregida y lectura por defecto.
V2: `http://127.0.0.1:3000`; panel: `http://127.0.0.1:4381`; portales
vulnerable/corregido: `http://127.0.0.1:4380` y `http://127.0.0.1:4382`.
`--lab-mode vulnerable` selecciona esa fuente para V2; cambiar el selector del
panel por sí solo no cambia la fuente de V2.

La opción `--enable-manual` habilita el ejecutor y las solicitudes manuales.
Arrancar con ella no encola un análisis. Pulsar Iniciar análisis sí usa el
proveedor configurado. Se espera al fin del trabajo antes de cerrar con
Ctrl+C; para volver a lectura se inicia sin la opción. Procedimiento completo:
[operación local](PUERTO_UMBRAL_OPERACION_LOCAL.md).

## Qué ya está acreditado y no se necesita repetir

| Bloque | Evidencia disponible | Límite |
| --- | --- | --- |
| Arranque conjunto y modo manual | Ambas apps accesibles; ejecutor manual disponible; Ctrl+C informado y retorno a lectura con botón deshabilitado; cinco regresiones aisladas del lanzador correctas el 02/11 | Ciclo básico observado y pruebas simuladas acotadas; no nuevo análisis ni inspección exhaustiva del host |
| Interfaz | Nueva distribución de escritorio; navegación básica de cinco vistas V2; informe anterior legible; ambas interfaces en vista estrecha y foco confirmado a su alcance | No encaje sin scroll a 100 %, accesibilidad global o dispositivo físico |
| Corpus base | 45 registros históricos con evidencia o causa; 42 conformes HTTP y tres comandos con `Cannot fork` | Registro completo no equivale a funcionamiento 45/45 ni métricas del detector |
| Integración y seguimiento | Snapshot de 17 líneas → un análisis Groq → informe visible; seguimiento básico recibido; veinte muestras API con desviación F4-AC1 aceptada; fallo/recuperación y snapshot anterior conservado recibidos | No evaluación del corpus, rotación real ni latencia de renderizado extremo a extremo |
| F6, cerrada por decisión expresa del 03/11 | Cinco normales y cinco intentos corregidos de variante 1; CSRF corregido en navegador y reutilización corregida de permiso; comparaciones Cargas y Atraque vulnerable/corregido con auditoría conservada | Restantes verificaciones F6 omitidas/no acreditadas por decisión del propietario; no cuentan como superadas |
| F7 educativa | Once recorridos corregidos de variante 1; revisión documental finalizada el 03/11 con objetivos, evidencia y límites por categoría y dictamen F7-AC1/2/3 | Lista para aceptación final del propietario; no 54/54, explotación real de artefactos ficticios ni detección completa OWASP |
| Conservación y perímetro | Restauración aislada previa de 66 archivos; respaldo posterior de 113 verificado internamente; hash puntual de auditoría; inspector agregado válido de 14 contenedores y preflight recibido | Cada comprobación conserva su fecha y selección; no cubre automáticamente evidencias posteriores o toda la VM |

El respaldo de 113 archivos es del 31/10 y anterior al recorrido Cargas
vulnerable recibido después. No se presenta como copia de toda la evidencia
posterior. La restauración independiente adicional sigue aplazada. Los
originales del laboratorio bajo `labs/puerto_umbral/.local-state/f2` están fuera
del perfil de respaldo V2 señalado; no se confunden con sus copias de auditoría.

## Estado de los bloques tras el ajuste expreso de alcance

Los tres bloques técnicos conservan sus evidencias y límites; F4/F5/F6 ya
tienen decisión expresa y la matriz F7 está aceptada. El detalle está en la
[auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md).

| Prioridad | Pendiente | Criterios relacionados | Evidencia o decisión que falta |
| --- | --- | --- | --- |
| 1 | Alcance de funcionamiento y regresión existente | F2-AC1/2/3/4, F3-AC4 | Comandos ya tiene verificación representativa y separación de perfiles cuenta con preflight probado; documentar límites restantes sin nuevas pruebas. F6 está cerrada por decisión expresa, con sus omisiones registradas |
| 2 | Operación ampliada, F4 cerrada por alcance | F3-AC3, F4-AC1/2/3/4/5 | Ensayos previos conservados; propietario cierra F4 sin pruebas restantes. Rotación/discontinuidad y condiciones no observadas permanecen sin verificar, sin más ensayos de cierre |
| 3 | Evaluación del detector, F5 cerrada por alcance | F5-AC2 | Propietario cierra F5 sin evaluación adicional: objetivos de detección no medidos. Se conservan registro histórico y límites, sin ejecutar pruebas o modelo ni presentar objetivos como resultados |
| Final | Consolidación y aceptación de entrega | Conjunto de entrega | Matriz F7 aceptada y decisiones F4/F5/F6 registradas; consolidar y aceptar el conjunto con límites F2/F3 y omisiones. Publicación únicamente cuando se solicite |

La fuente corregida de comandos se identificó en la imagen de Parrot y pasaron
el uso normal corregido y el recorrido vulnerable representativo de variante 1,
con salida real, sin timeout y retorno 0. La incidencia `Cannot fork` queda
verificada como corregida en ese alcance, sin repetirlo ni puntuar variantes
2/3 no reejecutadas. Las cinco regresiones aisladas del nuevo lanzador se
ejecutaron después con autorización expresa: **5/5 correctas, exit 0**, Windows
y Python 3.11.9, sin procesos/HTTP reales o modelo. Su
[acta de verificación prioritaria](CIERRE_VERIFICACION_PRIORITARIA_2026_11_02.md)
delimita ambos resultados y los recorridos manuales recibidos.
Esto no completa toda la regresión del MVP o la aceptación F6.

Baliza vulnerable conserva un resultado funcional no recibido y queda omitida
por el cierre expreso de F6. Una fila de
historial con prefijo `525a2076b8ae` no permite evaluarlo. El recorrido se
aplazó a petición del propietario y se retira del trabajo pendiente al cerrar F6;
no se reejecuta ni se reformula para eludir
el bloqueo comunicado. Permanece explícito donde afecte al cierre F6.

F5-AC1 ya permite registrar los 45 casos con su evidencia o causa de fallo;
no exige repetirlos solo para documentarlos. Su registro histórico y la
verificación representativa posterior se mantienen separados; no se cambia
el histórico a 45/45. El informe único de 17 líneas tampoco mide precisión o falsas
alarmas. El permiso del análisis Groq anterior está consumido: no se inicia
otra evaluación por esta consolidación ni se acepta un alcance reducido por
silencio. Se mantiene el objetivo completo solicitado.

## Cobertura adicional que no se convierte en cuota nueva

No se impone ejecutar todas las 99 entradas de ampliación ni las 43 F7 sin
observar para cerrar su matriz educativa. La equivalencia de Criptografía
corregida por código no cuenta como ejecución del intento. Se mantienen sus
estados y el corpus original, sin reescribir resultados históricos.

Zoom 200 %, exportación, recorrido exhaustivo de tablas y teléfono físico
siguen sin observarse. Son cobertura adicional del plan UX, sin incidencia
concreta pendiente que obligue ahora a repetir la revisión básica. Una nueva
instalación completa, otro análisis del mismo snapshot y una restauración de
toda la VM tampoco se añaden como requisitos de cierre.

## Antecedentes del siguiente trabajo propuesto antes del cierre F4/F5

Las propuestas de evaluación, búsquedas o verificaciones de esta sección
quedan retiradas por la decisión más reciente; no son acciones pendientes.

Las regresiones aisladas, el bloque representativo de comandos y el ensayo
operativo de veinte ciclos están completados a sus alcances. No se repiten.
La lectura de historial/SQLite ya corrobora la relación temporal de dos
sesiones cerradas con el único trabajo posterior y cero entregas; la API
actual confirma inactividad/interrupción de la tercera sesión antigua.
El [ensayo F4](PUERTO_UMBRAL_MEDICION_F4_2026_11_02.md), tras recibir `586f050`
en Parrot, registra veinte lecturas de 0,057–0,096 s y cotas API de 0,086–1,054 s,
trabajos 1→1, entregas 0→0 y snapshots 25→26 con un único checkpoint. Parada
recibida y condiciones del recibo leídas: Linux Parrot/x86_64/16 CPU lógicas,
carga registrada. El panel termina Detenido con 21 ciclos; el adicional hasta
detener no se suma a las veinte muestras. No mide renderizado del navegador.
El propietario acepta expresamente la desviación acotada de F4-AC1:
disponibilidad API como evidencia, sin renderizado o visibilidad extremo a
extremo RNF-09 verificados. No equivale a aceptar toda F4/proyecto. Siguiente
recorrido de desconexión/reinicio también completado después: error visible,
captura recuperada de 94 líneas, sin auto-resume y snapshot previo existente
con hash coincidente según lectura del propietario. No repetirlo. Rotación
real y criterios F6/F5 siguen separados. La [preparación F5](PUERTO_UMBRAL_EVALUACION_F5_2026_11_02.md)
ya incluye empaquetador offline, protocolo de puntuación por caso y presupuesto
propuesto: tres lotes de quince casos/veinticinco líneas, con etiquetas separadas.
Sintaxis y ayuda correctas; cinco pruebas nuevas preparadas pero no ejecutadas.
Falta localizar el archivo original `suite.json`/`runs/` y su corpus físico;
no está en este checkout. No se ha creado un paquete real ni ejecutado evaluación.
Ejecutor con presupuesto y puntuador quedan pendientes; tope propuesto de
dieciocho llamadas, sin autorización nueva de modelo. El informe de metadatos
histórico no sustituye sus originales ni el log actual sustituye los 45 casos.
Al no localizar la copia, el propietario acepta avanzar con otros pendientes:
cinco regresiones aisladas de separación de perfiles y preflight con publicación
ausente/corrupta, en `tests/test_closure_profile_isolation.py`, se ejecutan después
con autorización específica: **5/5 correctas, 0,178 s, exit 0**, sin bloqueo,
archivos temporales y comprobaciones de entorno/puerto simuladas. Su alcance figura en la
[verificación prioritaria](CIERRE_VERIFICACION_PRIORITARIA_2026_11_02.md).
No se cambia el runtime ni se acepta toda la regresión por este bloque.
Cada comprobación reutiliza evidencia previa.
La evaluación F5 se trata como una decisión separada de ejecución y presupuesto.
El número final de comprobaciones se fija al revisar ese plan; no se deduce
del número de entradas del catálogo.

Hasta que se acuerde esa ejecución, se continúa con código/documentación.
El agente no inicia suites, escenarios, servicios, VM o modelos. Esta revisión
no crea una release, despliegue público, publicación de LinkedIn o commit/push.

Referencias vigentes: [PRD](PRD_PUERTO_UMBRAL_2026_10_26.md),
[matriz F7](PUERTO_UMBRAL_F7_CIERRE_EDUCATIVO_2026_10_31.md),
[producto](PUERTO_UMBRAL_REVISION_PRODUCTO_2026_10_31.md),
[plan y cronología](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md).

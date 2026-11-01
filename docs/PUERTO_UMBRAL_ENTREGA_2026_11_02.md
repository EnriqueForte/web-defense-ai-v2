# Web Defense AI V2 y Puerto Umbral — estado de entrega

Actualizado el 02/11/2026, Europe/Madrid. **Aplicaciones desarrolladas y
recorridos básicos observados en Parrot; aceptación completa F0–F7 todavía
abierta.** El objetivo del propietario sigue siendo todas las fases. Este
resumen consolida evidencias existentes; no cambia el PRD ni autoriza pruebas.

Actualización posterior del 02/11: observador F4 y cinco pruebas aisladas
correctas preparados junto a las actas; el propietario autoriza su commit/push
en una entrega de trece archivos con `[skip ci]`. Se identifica por el commit
que incorpora esta nota y se verifica al finalizar Git. `91a101e` sigue siendo
la referencia de los servicios ya observados en Parrot; el observador nuevo
es independiente y no requiere otro build de interfaz. Las indicaciones
«local/publicación pendiente» de las recepciones anteriores describen su
momento de preparación, sin sustituir la verificación final de publicación.

Última entrega de código publicada y verificada al cerrar su publicación:
`91a101e3831009da1ba25589798dc733b0222ce0`, opción de análisis manual en el
lanzador conjunto. Las recepciones y esta consolidación documental son cambios
locales posteriores; no se han publicado por redactar este documento.

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
| Arranque conjunto y modo manual | Ambas apps accesibles; ejecutor manual disponible; Ctrl+C informado y retorno a lectura con botón deshabilitado | Ciclo básico observado por propietario; no nuevo análisis ni suite del lanzador ejecutada |
| Interfaz | Nueva distribución de escritorio; navegación básica de cinco vistas V2; informe anterior legible; ambas interfaces en vista estrecha y foco confirmado a su alcance | No encaje sin scroll a 100 %, accesibilidad global o dispositivo físico |
| Corpus base | 45 registros históricos con evidencia o causa; 42 conformes HTTP y tres comandos con `Cannot fork` | Registro completo no equivale a funcionamiento 45/45 ni métricas del detector |
| Integración y seguimiento | Snapshot de 17 líneas → un análisis Groq → informe visible; seguimiento básico con pausa/reanudación/parada/vencimiento y reapertura sin auto-resume | No evaluación del corpus ni prueba de rotación o veinte latencias individuales |
| F6 | Cinco normales y cinco intentos corregidos de variante 1; CSRF corregido en navegador y reutilización corregida de permiso; comparación Cargas vulnerable/corregida con auditoría conservada | Otros efectos representativos y regresión pendientes |
| F7 educativa | Once recorridos corregidos de variante 1; objetivos, evidencia y límites por categoría en la matriz | No 54/54, explotación real de artefactos ficticios ni detección completa OWASP |
| Conservación y perímetro | Restauración aislada previa de 66 archivos; respaldo posterior de 113 verificado internamente; hash puntual de auditoría; inspector agregado válido de 14 contenedores y preflight recibido | Cada comprobación conserva su fecha y selección; no cubre automáticamente evidencias posteriores o toda la VM |

El respaldo de 113 archivos es del 31/10 y anterior al recorrido Cargas
vulnerable recibido después. No se presenta como copia de toda la evidencia
posterior. La restauración independiente adicional sigue aplazada. Los
originales del laboratorio bajo `labs/puerto_umbral/.local-state/f2` están fuera
del perfil de respaldo V2 señalado; no se confunden con sus copias de auditoría.

## Pendientes esenciales para aceptar el alcance completo

Son **tres bloques técnicos y una decisión final**, no cuatro pruebas ni una
orden de ejecución. El detalle por criterio está en la
[auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md).

| Prioridad | Pendiente | Criterios relacionados | Evidencia o decisión que falta |
| --- | --- | --- | --- |
| 1 | Funcionamiento y regresión | F2-AC1/2/3/4, F3-AC4, F6-AC1/2/3/4/5 | Comandos ya tiene verificación representativa de la corrección; completar conductas avanzadas distintas aún no observadas y regresión acotada por cambios; revisar separación de perfiles y contrato real sin etiquetas esperadas |
| 2 | Operación ampliada | F3-AC3, F4-AC1/2/3/4/5 | Completar discontinuidad/rotación de fuente y conservación, cotejo de deduplicación/trabajos y latencias; el PRD admite una desviación temporal documentada y revisada, todavía no aceptada |
| 3 | Evaluación del detector | F5-AC2 | Medir los objetivos del corpus: 27/30 intentos, al menos 5/6 por familia y cero falsas alarmas entre 15 benignos; o decisión expresa de alcance sobre resultados inferiores, conforme al PRD |
| Final | Revisión y aceptación de entrega | F5 y F7, con sus dependencias | Revisar resultados/limitaciones, matriz educativa F7 y documentación V2 con el propietario; registrar la decisión sin convertir criterios pendientes en aprobados |

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

Baliza vulnerable conserva un resultado funcional no recibido. Una fila de
historial con prefijo `525a2076b8ae` no permite evaluarlo. El recorrido se
aplazó a petición del propietario; no se reejecuta ni se reformula para eludir
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

## Siguiente trabajo y límites vigentes

Las cinco regresiones aisladas y el bloque representativo de comandos están
completados a su alcance. Siguiente prioridad recomendada: concretar la
validación de operación F3/F4 (lectura, latencias, deduplicación, ausencia de
trabajos nuevos y conservación ante discontinuidad), sin otros escenarios
de seguridad o modelo. Todavía no se ha autorizado o ejecutado ese bloque.
La lectura de historial/SQLite ya corrobora la relación temporal de dos
sesiones cerradas con el único trabajo posterior y cero entregas; la API
actual confirma inactividad/interrupción de la tercera sesión antigua.
Se prepara el [observador F4](PUERTO_UMBRAL_MEDICION_F4_2026_11_02.md), con cinco
pruebas aisladas autorizadas y correctas, para conservar veinte muestras de
disponibilidad por API y cotejar metadatos antes/después. No mide paint del
navegador ni acepta el criterio automáticamente. Archivo aún local, medición
Parrot y publicación pendientes. Cada comprobación reutiliza evidencia previa.
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

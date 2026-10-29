# Puerto Umbral — F5: evaluación de evidencias y preparación de entrega

Fecha: 27/10/2026. Estado: **revisión de evidencias existentes y documentación
preparadas; aceptación del MVP pendiente**.

Actualización del 29/10: las tablas y JSON de esta revisión conservan el estado
del archivo histórico al crear la entrega F5. Después se autorizó y observó
[un análisis acotado de 17 líneas](PUERTO_UMBRAL_ANALISIS_ACOTADO_2026_10_27.md),
incluida su publicación y visualización en V2. Su autorización ya se consumió.
No se transforma esa muestra en métricas de los 45 casos ni se reescriben los
resultados históricos. El [estado consolidado vigente](PUERTO_UMBRAL_ESTADO_ACTUAL_2026_10_26.md)
recoge esta evidencia posterior y los pendientes que continúan abiertos.

El propietario autoriza continuar con F5 después de completar el recorrido
operativo básico F4. Este bloque conserva el alcance acordado: leer evidencias
ya guardadas, organizar resultados y preparar la entrega, sin nuevos escenarios,
suites, ciclos de seguimiento, servicios o llamadas al modelo. No se solicitan
más capturas para las rondas finalizadas. Las condiciones originales permanecen
en el [PRD](PRD_PUERTO_UMBRAL_2026_10_26.md).

## Entregables de este bloque

| Entregable | Contenido |
| --- | --- |
| [Resumen estructurado F5](PUERTO_UMBRAL_F5_2026_10_27.json) | Observaciones manuales, criterios, métricas sin medir, pendientes e inventario de fuente |
| [Revisión del corpus histórico](PUERTO_UMBRAL_F5_CORPUS_2026_10_27.json) | 45 entradas, referencias de ejecución, hashes y resultados guardados |
| [Revisor offline](../scripts/review_puerto_umbral_evidence.py) | Lee el archivo conservado y contrasta recibos/snapshots sin ejecutar la aplicación |
| [Manual de operación](PUERTO_UMBRAL_OPERACION_LOCAL.md) | Preparación, lectura, seguimiento, cierre, conservación y recuperación |
| Este informe | Evaluación consolidada, matriz de aceptación y lista de entrega |

La versión operativa publicada y observada en Parrot es
`02d26388b67fc51591eaede9bf2056f28cadbea1`. El nuevo revisor se ejecuta de forma
independiente; no se incorpora al arranque de V2, al pipeline o al seguimiento.
Este bloque no cambia el código operativo de esa versión. El propietario autoriza
después publicar las nuevas actas, el revisor y los informes mediante commit/push
del paquete F4/F5. Su identificación queda en el historial Git y la referencia
remota se comprueba tras publicar. No se crea una release o etiqueta nueva.

## Fuentes y alcance de la revisión

| Fuente | Procedencia | Uso permitido en la conclusión |
| --- | --- | --- |
| Suite F2 del 26/10 | Archivo local original de la primera ejecución en Docker Desktop/Linux, Windows | Conformidad HTTP y correlación de los casos históricos |
| Capturas de Parrot del 26/10 | Propietario, [cronología](PUERTO_UMBRAL_PARROT_2026_10_26.md) | Respuestas funcionales y recepción visible en V2 de los casos mostrados |
| Capturas F4 del 27/10 | Propietario, [acta F4](PUERTO_UMBRAL_F4_2026_10_27.md) | Compilación y recorrido operativo básico observado |
| Fuente Git publicada | 28 archivos seleccionados del commit operativo | Identidad de los bytes de fuente entregados, independiente de finales de línea del checkout |

Los originales de la VM, sus snapshots completos y recibos JSON exportados no
se han recibido. Las capturas de pantalla acreditan los campos visibles. El
agente no dispone de shell de Parrot ni atribuye operaciones propias a la VM.
La revisión de 92 archivos locales históricos no se extiende a los archivos de
Parrot, imágenes Docker, paquetes instalados o el confinamiento del host.

## Resultado del corpus histórico

El recibo de suite está fechado `2026-10-26T17:15:05.684368Z`, versión
`puerto-umbral-f2-1`, semilla `umbral-cargo-20261026-1` y tipo
`functional_http_not_v2_evaluation`. Se conservan sus resultados:

| Familia | Casos históricos | Conformes HTTP | No conformes HTTP |
| --- | ---: | ---: | ---: |
| SQL | 9 | 9 | 0 |
| XSS | 9 | 9 | 0 |
| Path traversal | 9 | 9 | 0 |
| Comandos | 9 | 6 | 3 |
| Autenticación | 9 | 9 | 0 |
| **Total** | **45** | **42** | **3** |

Se revisaron 45 recibos y sus 45 snapshots Apache, además de suite y corpus:
**92 archivos**. Se contrastaron identidad, definición del caso, hashes de
snapshot, bytes, referencias de líneas y hashes de respuestas guardadas. Una
segunda lectura confirmó los mismos bytes de esos archivos durante la revisión.
El informe contiene sus fingerprints y no copia cuerpos, URLs o credenciales.

Los recibos registran **75 peticiones del ejecutor** y los snapshots seleccionados
suman **75 líneas correlacionadas**. Son denominadores del archivo revisado;
no se deduce cobertura de todo el historial o de peticiones no registradas.

Los tres casos no conformes son `command-a1-vulnerable`,
`command-a2-vulnerable` y `command-a3-vulnerable`. Sus recibos están completados,
pero la salida guardada contiene `Cannot fork` y no demuestra el efecto esperado.
La corrección posterior del límite de procesos permanece sin repetir esos casos.

Los seis intentos XSS del archivo histórico conservan pendiente la confirmación
de navegador. La conformidad de esa suite se basa en reflexión/codificación HTTP
y captura. La confirmación posterior de una variante en Parrot se registra
separadamente; no modifica el recibo original ni convierte el corpus en 45/45.

### Integridad y finales de línea

El SHA-256 de `suite.json` conservado es
`60e045f1cf9214d05771b35e42f872d2573c69dcc9355430af1c29a995462cbb`.
El corpus físico que esa suite identifica tiene SHA-256
`cb95ce3004a4ec02ecfb019be787e13b29427618143dfd2ad25ad859ef8bbae6`.
El revisor exige coincidencia exacta con ese corpus y no normaliza sus bytes.

Git guarda el corpus con LF y el archivo local de esta revisión utiliza CRLF;
por ello el blob publicado tiene un SHA-256 diferente, registrado por separado
en el resumen F5. El inventario de los 28 archivos usa bytes de los blobs Git
del commit indicado. Esta distinción evita presentar una conversión de finales
de línea como verificación idéntica de un archivo histórico. Para reproducir la
revisión se necesita conservar el corpus físico original junto con su suite.

## Matriz de 45 entradas

La variante se presenta como 1–3, aunque el archivo usa índices 0–2. «Conforme»
es el veredicto HTTP histórico guardado. La observación Parrot se ha relacionado
por selección/entrada y respuesta visible, sin recibo completo de la VM.
Una búsqueda normal realizada desde el navegador no se presenta como ejecución
del runner del corpus. Los detalles están en los JSON enlazados.

| Caso | Tipo | Modo | Histórico HTTP | Observación posterior en Parrot | Detector V2 |
| --- | --- | --- | --- | --- | --- |
| sqli-a1-vulnerable | Intento | Vulnerable | Conforme | Señuelo visible | Sin evaluar |
| sqli-a1-corrected | Intento | Corregido | Conforme | Lista vacía, sin señuelo | Sin evaluar |
| sqli-a2-vulnerable | Intento | Vulnerable | Conforme | Sin nueva observación | Sin evaluar |
| sqli-a2-corrected | Intento | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| sqli-a3-vulnerable | Intento | Vulnerable | Conforme | Sin nueva observación | Sin evaluar |
| sqli-a3-corrected | Intento | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| sqli-b1 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| sqli-b2 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| sqli-b3 | Normal | Corregido | Conforme | Asteria normal desde navegador | Sin evaluar |
| xss-a1-vulnerable | Intento | Vulnerable | Conforme | Ejecución de navegador confirmada | Sin evaluar |
| xss-a1-corrected | Intento | Corregido | Conforme | Codificación y texto literal; estado final incompleto | Sin evaluar |
| xss-a2-vulnerable | Intento | Vulnerable | Conforme | Sin nueva observación | Sin evaluar |
| xss-a2-corrected | Intento | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| xss-a3-vulnerable | Intento | Vulnerable | Conforme | Sin nueva observación | Sin evaluar |
| xss-a3-corrected | Intento | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| xss-b1 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| xss-b2 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| xss-b3 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| traversal-a1-vulnerable | Intento | Vulnerable | Conforme | Documento señuelo visible | Sin evaluar |
| traversal-a1-corrected | Intento | Corregido | Conforme | Rechazo 403 | Sin evaluar |
| traversal-a2-vulnerable | Intento | Vulnerable | Conforme | Sin nueva observación | Sin evaluar |
| traversal-a2-corrected | Intento | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| traversal-a3-vulnerable | Intento | Vulnerable | Conforme | Sin nueva observación | Sin evaluar |
| traversal-a3-corrected | Intento | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| traversal-b1 | Normal | Corregido | Conforme | Documento público normal | Sin evaluar |
| traversal-b2 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| traversal-b3 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| command-a1-vulnerable | Intento | Vulnerable | No conforme | Sin nueva observación | Sin evaluar |
| command-a1-corrected | Intento | Corregido | Conforme | Rechazo 400 | Sin evaluar |
| command-a2-vulnerable | Intento | Vulnerable | No conforme | Sin nueva observación | Sin evaluar |
| command-a2-corrected | Intento | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| command-a3-vulnerable | Intento | Vulnerable | No conforme | Sin nueva observación | Sin evaluar |
| command-a3-corrected | Intento | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| command-b1 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| command-b2 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| command-b3 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| brute-a1-vulnerable | Intento | Vulnerable | Conforme | Sin nueva observación | Sin evaluar |
| brute-a1-corrected | Intento | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| brute-a2-vulnerable | Intento | Vulnerable | Conforme | Sin nueva observación | Sin evaluar |
| brute-a2-corrected | Intento | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| brute-a3-vulnerable | Intento | Vulnerable | Conforme | Sin nueva observación | Sin evaluar |
| brute-a3-corrected | Intento | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| brute-b1 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| brute-b2 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |
| brute-b3 | Normal | Corregido | Conforme | Sin nueva observación | Sin evaluar |

La búsqueda normal vulnerable de `Asteria`, visible en Actividad, es una
observación adicional fuera de los 15 controles benignos del corpus, que están
definidos en modo corregido. No se añade al denominador de 45.

## Evaluación del detector y métricas

El corpus contiene **30 intentos** y **15 controles benignos**. Un intento
rechazado en modo corregido mantiene su condición positiva para reconocer
intentos; `expected_effect=false` describe su efecto funcional esperado.
El JSON histórico añade `expected_attempt_indicator` para conservar esa
distinción. Las expectativas no se ajustan a los resultados del detector.

| Métrica | Resultado disponible |
| --- | --- |
| Conformidad HTTP histórica | 42/45, con tres fallos conservados |
| Observaciones manuales relacionadas con el corpus | 9 entradas; muestra dirigida, sin puntuación de calidad |
| Recepción manual visible | Solicitudes mostradas en Actividad; ventana limitada |
| Precisión/recuperación del detector | Sin medir; valores `null` |
| Falsas alarmas | Sin medir; no se declara cero |
| Omisiones o duplicados de todo el historial | Sin medir |
| Latencia de seguimiento | Últimas lecturas de algunas pantallas; no veinte medidas individuales |
| Cola, modelo y publicación de análisis | Sin medir |
| Coste del proveedor | Sin recibo evaluado; `null` |
| Nuevas ejecuciones / llamadas del modelo en este bloque | 0 / 0 |

Los objetivos del PRD permanecen sin evaluar: al menos 27 de 30 intentos,
al menos cinco de seis por familia y cero falsas alarmas entre 15 controles
benignos. No se equipara la lectura de logs o el valor 42/45 con esos objetivos.
La ausencia de resultados del modelo no constituye una puntuación cero ni una
garantía de detección. No se solicita un presupuesto o clave en este bloque.

## Estado de aceptación F5

| Criterio | Evidencia preparada | Estado y pendiente |
| --- | --- | --- |
| F5-AC1 — 45 casos con resultado/evidencia o causa | Matriz completa, 45 recibos históricos, fallos preservados y nueve observaciones manuales relacionadas | Parcial: el código corregido/actual no tiene un nuevo corpus completo |
| F5-AC2 — Objetivos del detector o aceptación expresa de alcance | Objetivos y denominadores conservados; métricas ausentes identificadas | Pendiente: sin evaluación del detector ni aceptación implícita de su ausencia |
| F5-AC3 — Separar intento, efecto y evidencia insuficiente | Campos separados en informe/JSON, XSS HTTP/navegador diferenciados | Documentado en el alcance de esta revisión |
| F5-AC4 — Instalación/cierre en plataforma objetivo | Actualización, build, arranque, preflight, cierre y reapertura en Parrot observados | Recorrido sobre instalación existente; no nueva instalación limpia o certificación multiplataforma |
| F5-AC5 — Conservar originales, presupuesto y límites | Fingerprints y doble lectura de 92 archivos locales; originales intactos y límites explícitos | Parcial: originales VM, recuperación del perfil y recibos del proveedor pendientes |

**F5 no se declara cerrada ni se acepta el MVP completo.** Quedan preparados
la evaluación de las evidencias accesibles, sus datos estructurados y el manual.
La entrega identificable es una versión educativa local con captura/seguimiento
y verificación parcial de escenarios. F2/F3 conservan sus pendientes y F4 su
aceptación ampliada. Una futura decisión de alcance debe expresar qué criterios
se aceptan o aplazan; seguir desarrollando no los da por cumplidos.

## Lista de entrega y pendientes finitos

| Elemento | Estado |
| --- | --- |
| Fuente operativa identificada y checkout Parrot | Publicada/observada en `02d2638` |
| Prototipo Sites | F1 privado; sin cambios o despliegue nuevo |
| Frontend local | Build Parrot y Windows documentados; sin nueva revisión móvil/teclado F4 |
| Conector y seguimiento | Lectura manual y ronda básica F4 observadas |
| Datos de evaluación | Históricos y manuales separados; todos los casos indexados |
| Manual de inicio/parada/conservación | Preparado y enlazado |
| Manifiesto de fuente | 28 blobs identificados; no inventario de imágenes o entorno instalado |
| Corpus corregido y autenticación manual | Aplazados; tres fallos históricos no descartados |
| Snapshot → trabajo → informe y evaluación del detector | Pendientes; sin nuevas llamadas al modelo |
| Rotación, truncado, desconexión, cuota y métricas F4 | Aplazados |
| Recuperación Puerto, regresión y verificaciones negativas | Aplazadas |
| Publicación del paquete F4/F5 | Commit/push autorizado después de preparar la entrega; identificado en el historial Git |
| Aceptación del MVP / release | Pendientes; publicar documentación no las da por realizadas |

Los siete pendientes identificados `PU-P01`–`PU-P07` del resumen JSON agrupan
estos límites. No generan automáticamente un plan de ejecución: el alcance de
una futura revisión se decide expresamente. No se solicitan más imágenes,
escenarios o comprobaciones al propietario para completar este bloque documental.

## Reproducción de la revisión offline

El [revisor](../scripts/review_puerto_umbral_evidence.py) solo lee la lista concreta
de archivos referenciados en el archivo histórico. Rechaza identidades/corpus
incompatibles, enlaces, archivos excesivos y cambios durante la lectura. Genera
un JSON nuevo; rechaza sobrescribir un destino existente. Su ejecución no
contacta con Docker, el sitio, la VM o el modelo.

Para otra revisión se requiere una copia conservada de `suite.json`, sus
directorios `runs/` y el corpus físico original. Los parámetros son `--state-root`,
`--corpus` y, opcionalmente, `--output` para un archivo JSON nuevo. Los archivos
históricos de esta sesión permanecen fuera de Git; el informe no los hace
portables por sí solo. No se solicita repetir la revisión ahora.

Las comprobaciones de este bloque se limitan a sintaxis del revisor, lectura
de los archivos existentes, consistencia de los informes y enlaces locales.
No se inicia una nueva CI, release, aplicación, seguimiento o evaluación de
seguridad. La fuente operativa, las dependencias, `.env`, DVWA y los datos
de Parrot permanecen sin modificaciones por el agente.

### Comprobación final del paquete documental

- Sintaxis Python del revisor compilada sin importar módulos de aplicación.
- Dos JSON leídos y coherentes: 45 entradas únicas, 30 indicadores esperados
  de intento y nueve observaciones manuales relacionadas.
- Los 92 archivos de entrada mantienen al final del bloque los hashes y tamaños
  inventariados. Los 28 blobs de fuente coinciden con el commit operativo.
- La matriz Markdown tiene sus 45 filas y los 87 enlaces locales revisados
  existen. La revisión de diferencias no muestra errores de espacios.
- El código operativo sigue sin diferencias respecto de `02d2638`. Solo se
  añade la herramienta independiente de lectura y los artefactos/documentos F5.

Estas son comprobaciones de datos y documentación. No se ejecutaron pruebas
del sitio o del detector, ni se inició la aplicación para obtener esos resultados.

## Publicación y actualización del paquete documental

El propietario autoriza el commit/push y se publica
`ff1691845900204afd1a84fbc59274a3ad316395`, con 13 archivos del paquete F4/F5 y
`[skip ci]`. La consulta remota de `main` coincide con el commit local y el árbol
queda limpio tras el push. El código operativo de la aplicación sigue siendo
el de referencia `02d2638`; la nueva herramienta es un revisor offline separado.

La captura posterior del propietario muestra `git pull --ff-only` en Parrot,
fast-forward de `02d2638` a `ff16918` y los 13 archivos actualizados. Queda
observada la recepción del paquete en la VM. Esta actualización documental no
requiere recompilar, reinstalar dependencias o reiniciar los servicios.

Los JSON entregados permiten consultar la evaluación ya realizada. No se
solicita ejecutar el revisor en Parrot, donde no se han recibido los archivos
históricos originales de esta revisión. El recorrido snapshot → análisis →
informe sigue pendiente de alcance de ejecución y presupuesto propios; la
publicación no lo activa ni acepta el MVP completo. Esta nota de recepción es
posterior al commit citado y queda local hasta otra publicación autorizada.

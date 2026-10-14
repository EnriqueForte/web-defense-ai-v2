# A-05 — Ensayo real acotado, 14/10/2026

**Resultado parcial:** `mixed` y `normal` satisfacen sus expectativas de soporte
y publicación; `same_family` falló antes de corregir un defecto del evaluador y
no se repitió. A-05 permanece abierta. No se presenta este lote como tres casos
aprobados ni como aceptación semántica general del modelo.

## Autorización y aislamiento

El usuario autorizó expresamente los casos `same_family`, `mixed` y `normal`,
en ese orden, una vez cada uno, con máximo seis intentos lógicos y 600 segundos
externos por caso: 18 intentos como límite del lote. Sin repetir fallos,
datos/servicios operativos, Docker o notificaciones. Se usó el evaluador existente
con el router configurado `openrouter/openrouter/free`, modo gratuito y sin
fallback pagado. La configuración/credencial local se resolvió internamente
para este uso autorizado, sin imprimirla ni modificar `.env`.

El entorno `.p4` comprobó 172 pines, cero diferencias y cero extras. No se activó
como entorno operativo. Cada resultado se publicó únicamente en una carpeta
nueva de `.local-state/a05-evaluation/`; el lanzador local guarda un marcador
exclusivo por caso para impedir repetir un intento comenzado.

Versiones del producto: `observed-access-3`, `structured-prototype-8`,
`structured-report-4` y `grounded-narrative-1`. HEAD inicial
`b5649929cecfc5bf05231d0bad7df4c6a4af8d59`, documentación del código CI `c7df36a`.
Durante el lote se corrigió únicamente el envoltorio del evaluador, con pruebas
offline antes de los dos casos restantes; las fuentes del motor/adaptador no
cambiaron. Cada marcador guarda el hash del evaluador usado.

## Resultados reales

| Caso | Resultado | Intentos lógicos | Segundos informados | Evidencia |
| --- | --- | --- | --- | --- |
| `same_family` | Falló detección: dos `invalid_json`; sin clasificación, narrativa o publicación | 2 | 21,438 | `20261014T094305947708Z` |
| `mixed` | Publicación verificada, cinco familias y nueve pares patrón–línea esperados, sin omisiones ni atribuciones inesperadas | 3 | 83,125 | `20261014T094752213939Z` |
| `normal` | Publicación verificada, cero hallazgos; clasificación/narrativa locales tras detección válida | 1 | 5,000 | `20261014T095000222953Z` |

Las tres carpetas pertenecen a `.local-state/a05-evaluation/` y contienen
`evaluation.json` y diagnósticos; los dos casos positivos contienen además
publicaciones sintéticas con manifiesto, resultado y Markdown. Se consumieron
**seis de 18 intentos lógicos**. Los 12 restantes no son autorización para
repetir casos o ampliar el lote. Las solicitudes internas del transporte no
se equiparan automáticamente a estos intentos/completions observados.
Los tiempos de la tabla son los informados por el motor, no incluyen toda la
construcción/importación del proceso ni acreditan un p95 o una respuesta rápida.

### Fallo del primer caso y defecto del evaluador

Las dos respuestas del primer caso eran JSON inválido según ambas guardas.
El diagnóstico conserva longitudes, estados y metadatos, sin las respuestas
crudas rechazadas. Se comprobó ausencia de puntero y de generaciones para este
caso; no se transformó el fallo en cero hallazgos.

La revisión identificó que el `BoundedLLM` del evaluador heredaba
`is_litellm=False` y parámetros vacíos, mientras su delegado real era LiteLLM.
El adaptador structured comprueba esas propiedades antes de solicitar
`response_format=json_object` y `provider.require_parameters=true`. El
envoltorio ocultaba ese camino: **este caso no probó la corrección de formato
con los parámetros que usa el producto**.

`bounded_evaluation_llm` conserva ahora `is_litellm` y los parámetros del delegado,
traslada el conjunto temporal por llamada y restaura el original en `finally`.
Mantiene el mismo límite de seis intentos, claves, URL, modelo y presupuesto;
el séptimo se rechaza antes de llamar al delegado. El cambio se hizo antes de
`mixed` y `normal`, tras verificación offline. No se repitió `same_family`.

Hashes SHA-256 de los bytes del evaluador usados en este Windows:

- Primer caso: `9330ddde292e8155aad318c0bcc1e54556f9a50eb4565b2ee00381efbaa2d18d`.
- Dos restantes: `798c1edc767dd07210c44ddcbab3eb32641c5d9cac9850cc8c318220d3b94231`.

Modelos de respuesta observados: `nvidia/nemotron-3.5-content-safety:free` en el
primer caso; `dots-studio/dots-3-note-preview:free` y `liquid/lfm-2.5-2.6b:free`
en el mixto; `liquid/lfm-2.5-2.6b:free` en el normal. Son identificadores de
metadatos, no una explicación de la causa. Al variar los modelos y las entradas,
el éxito posterior no se atribuye únicamente a la corrección del evaluador.

### Revisión de los informes positivos

Se cargaron los manifiestos y verificaron los bytes/hash de resultado y Markdown.
La evidencia coincide con cada fixture, las guardas de referencias y
clasificación se volvieron a validar y las dos métricas se recalcularon.

En `mixed`, las diez líneas de entrada están seleccionadas: SQLi en línea 1,
XSS en 2, traversal en 3, comandos en 4 y frecuencia de login en 5–9. La petición
normal en línea 10 no recibe hallazgo. Los cinco grupos mantienen
`requires_investigation`; cuatro son altos y XSS medio, dentro de los techos
de la política. Los motivos describen los indicadores y requieren investigación,
sin confirmar explotación o resultado de autenticación. Son motivos libres
del modelo en inglés; no son la narrativa publicada ni garantizan clasificación
correcta en otros logs.

La narrativa publicada usa `python_validated_facts`, está en español y contiene
conteos, alcance y cinco medidas concretas por patrón con referencias válidas.
Advierte que el alcance no confirma explotación ni permite descartar actividad
fuera de la selección. En `normal`, las cuatro solicitudes no producen
hallazgos; el resumen `python_scope` explica el alcance y no declara tráfico
benigno o seguridad global. Las recomendaciones quedan vacías y no se inventan
porcentajes precision/recall sin denominador. Ambas publicaciones mantienen
`quality=semantic_evaluation_pending`.

| Informe | SHA-256 Markdown | SHA-256 resultado |
| --- | --- | --- |
| `mixed` | `bcd6f2cef76dbefea8307c6c4f13eb68c410161adea3345258ebc9a7c63a8ad1` | `aeea8a3e52a9b0559d35a85bc674229880060cba4246d2adf0b129aa85928f41` |
| `normal` | `ba7aa5e3c65b8d792d7b2bb0ea6b99bf0c9dcb5cd1c5eb317dc9262a3723ac85` | `5d6c8d15421bd705aff93a1f54eb142944a7eb975ee27491a227a431a22fa56a` |

## Consumo y discrepancias

Los metadatos de seis completions informan 14.823 tokens de entrada,
10.735 de salida y 25.558 totales; 9.530 de razonamiento informado. No se suma
razonamiento a esos totales ni se afirma coste facturado. El SDK informa cero
razonamiento en los tres casos; la discrepancia se conserva por caso. Hay dos
avisos `reasoning_exceeds_completion`, en el segundo intento de `same_family`
y en la segunda llamada de `mixed`; no se normalizan ni se ocultan.

## Comprobaciones y conservación

Tras la corrección, 314 casos Python locales (.p4: 313 aprobados y uno Linux
omitido), tres comprobaciones JS y 89 archivos de sintaxis pasaron. El verificador
SDK amplió su cobertura de 25 a **27 escenarios offline**: el adaptador recibe
JSON mode/requisito de parámetros a través del envoltorio real del evaluador,
conserva preferencias, clave/URL sintéticas y `max_retries=0`, restaura los dos
objetos de parámetros y bloquea la séptima llamada incluso tras un fallo de
transporte. Red bloqueada; no se consumen llamadas reales en esas pruebas.

Lecturas antes/después: 29 trabajos, 14 entregas y cero activos; filas consultadas
y hashes de log/puntero/informe/resultado operativo iguales. `.env` conserva
tamaño/mtime. No hubo nuevos jobs, admisión manual, servicios operativos,
captura Docker o envíos. Los informes reales de estas fixtures no sustituyeron
el informe del dashboard. Recibos consolidados y comprobaciones en
`.local-state/a05-real-20261014/review.json` y archivos de la misma carpeta,
ignorados por Git. No se repiten llamadas para generar documentación.

La corrección del evaluador necesita publicación y CI Windows/Ubuntu propias;
la CI `38411563805` anterior no la cubre. Los resultados locales y reales de
este ensayo no se presentan como ejecución remota de la corrección.

## Pendientes y siguiente paso

Queda comprobar `same_family` con el evaluador corregido mediante **un nuevo
ensayo expresamente autorizado**, con máximo seis intentos lógicos y 600 segundos,
sin repetición automática. El lote actual ya terminó y no se reutiliza su saldo.
Una publicación correcta en ese caso aún requeriría revisión y aceptación con
límites. La semántica general y el recorrido manual/ingesta Parrot, incluida la
causa histórica de `ingestion_failed`, permanecen abiertos. Seguridad residual,
historial, recuperación y entrega final siguen siendo bloques independientes.

# Evaluación A-05 de grupos y revisión sin proveedor — 19/10/2026

Estado: implementación y pruebas locales completadas; publicación y CI pendientes.

La evaluación distingue ahora cobertura de referencias y agrupación del informe.
También permite revisar una publicación sintética existente sin ejecutar otra
vez el motor, cargar configuración LLM o modificar el informe.

## Problema reproducido

En la fixture `dvwa_post_burst` hay un XSS y una ráfaga de ocho POST. Dividir la
ráfaga en dos candidatos producía **tres hallazgos en vez de los dos grupos
escritos en la fixture**, pero las métricas anteriores seguían dando precisión
y recall 1: cada par patrón–línea estaba representado. Las guardas permiten
subconjuntos de una misma ventana; la cobertura por pares no evalúa particiones.
Esto acredita una carencia del evaluador, no que el proveedor la haya cometido
en el ensayo de Parrot aceptado.

`agents/evaluation_scoring.py` añade `a05-metrics-2`. Compara los grupos por
patrón y conjunto de líneas, sin depender del ID del candidato o del orden.
Cada grupo esperado puede coincidir una sola vez. Conserva duplicados como
grupos sobrantes en la métrica; una división, un solapamiento o la unión de las
dos ráfagas de distintas IP no desaparecen al deduplicar pares.

| Resultado sobre la fixture XSS + ocho POST | Cobertura por pares | Grupos exactos |
| --- | --- | --- |
| Un XSS y una ráfaga completa | Precisión/recall 1 | Precisión/recall 1; dos grupos |
| Un XSS y la ráfaga dividida en dos | Precisión/recall 1 | Precisión 1/3, recall 1/2; tres grupos |
| Un XSS y dos subconjuntos solapados que cubren la ráfaga | Precisión/recall 1 | Precisión 1/3, recall 1/2; tres grupos |

La selección parcial proyecta los grupos esperados sobre las líneas disponibles.
Puede cumplir la agrupación seleccionada, pero `fixture_expectations_met` queda
false cuando no se seleccionó toda la entrada. Los negativos y la incertidumbre
opcional conservan métricas indefinidas donde no hay denominador; no se inventa
recall 1 para un caso sin positivos.

El veredicto de fixture exige familias, pares, grupos y selección completa.
`semantic_acceptance=false` conserva explícitamente que estas métricas no
constituyen aceptación semántica general. El evaluador de proveedor reutiliza
el mismo cálculo después de ejecutar; `status=succeeded` sigue describiendo
la ejecución, y el nuevo veredicto informa por separado de las expectativas.
No se altera su presupuesto de seis intentos/600 s ni se inicia un ensayo.

## Revisar una publicación existente

Desde la raíz, con el intérprete instalado y sustituyendo la ruta por la carpeta
del caso que contiene `current.json`:

```bash
.p2/bin/python -B scripts/score_structured_fixture.py --case dvwa_post_burst --publication "RUTA_PUBLICACION/dvwa_post_burst"
```

En Windows usar `.p2/Scripts/python.exe`. El comando lee puntero/manifiesto,
verifica hashes y liga la evidencia al texto de la fixture elegida. Emite JSON
con métricas y referencias numéricas, sin líneas crudas, razones del modelo,
credenciales o mensajes de excepción. No acepta un log arbitrario como verdad
etiquetada: otra entrada, referencias ajenas o un informe corrupto se rechazan.

| Salida | Código |
| --- | ---: |
| `reviewed`, expectativas de la fixture cumplidas | 0 |
| `reviewed`, alguna expectativa o selección completa no cumplida | 2 |
| `rejected`, publicación no verificable o fixture incorrecta | 1 |

Los errores de argumentos conservan el código estándar 2 de argparse. Un
`reviewed` no es aceptación del proveedor. El comando no modifica manifiestos,
generaciones, trabajos o configuración y bloquea conexiones de red. Se comprobó
también en proceso Python frío, sin importar CrewAI, LiteLLM, motor, pipeline o
resolver de configuración. Una publicación sintética del bloque anterior se
volvió a puntuar satisfactoriamente sin regenerarla.

## Pruebas y evidencia local

La matriz añade dos salidas deliberadamente divididas/solapadas: **24 casos y
ocho controles**. En ambos casos nuevos, el checker pasa porque detecta la
agrupación incorrecta; `fixture_expectations_met=false` permanece visible. No
se presentan esas salidas como conformes ni se añade un rechazo al publicador.
Las 25 publicaciones completas siguen usando la selección del artefacto CI ya
existente, que incluye 101 archivos sin locks de publicación.

- 17 pruebas enfocadas aprobadas, incluidas nueve nuevas: división/solapamiento,
  identidad sin orden, duplicados, unión de IP, selección parcial, opcionales,
  entrada ajena, códigos del CLI, corrupción y proceso frío sin proveedor.
- Regresión Windows `.p4`: 374 casos Python, 373 aprobados y uno exclusivo Linux
  omitido, 31,605 s; tres comprobaciones JS aprobadas.
- Sintaxis: 100 archivos, cero errores.
- Matriz local `20261019T103911054532Z`: 24/8 aprobados y cero llamadas al proveedor.
- Primer intento enfocado bloqueado por WinError 5 del sandbox al reemplazar
  temporales; repetición autorizada fuera del aislamiento aprobada. La regresión
  y la matriz también se ejecutaron allí, conservando la publicación atómica.

Recibos en `.local-state/a05-groups-20261019/` y publicaciones sintéticas en
`.local-state/a05-offline-review/`, ambos ignorados. El [registro JSON](EVALUACION_GRUPOS_A05_2026_10_19.json)
recoge reproducción, contraste con el bloque anterior y verificaciones.

## Límites y reversión

La partición exacta es una expectativa escrita para estas fixtures, **no una
definición universal de incidente**. Un agrupamiento distinto de actividad real
puede necesitar criterio humano. Estas métricas no evalúan por sí solas estados,
severidades, éxito de autenticación, resistencia del LLM o precisión general.
No revocan las aceptaciones históricas de muestras concretas.

No cambian prompts, detector, publicación, contratos API, interfaz, pines,
Compose o servicios operativos. No hay llamadas LLM, Docker, notificaciones,
lectura de `.env` o modificación de Parrot. La reversión retira los campos
aditivos y el nuevo CLI del evaluador; los informes y sus formatos no cambian.
A-05 general, seguridad residual y entrega final siguen abiertos en el
[resumen vigente](ESTADO_FINAL_2026_10_12.md).

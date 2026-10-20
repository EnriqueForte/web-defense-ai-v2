# Revisión de evidencia y propuesta de aceptación A-05 — 20/10/2026

**A-05 aceptada para la primera versión local acotada.** El usuario eligió
expresamente «Aceptar alcance local acotado (recomendado)» el 20/10/2026, sobre
la propuesta de esta acta. No se ha ejecutado otro ensayo ni declarado calidad
general del modelo por una prueba sintética.
Esta acta resuelve la revisión de las evidencias E1/E2 de la
[matriz](MATRIZ_ACEPTACION_A05_2026_10_20.md) y propone una decisión concreta.

## Qué se volvió a comprobar

Se leyeron exclusivamente doce recibos de evaluaciones sintéticas ya ejecutadas:
ocho del 07/10 y cuatro del 14/10. Se verificaron once publicaciones, sus
punteros/manifiestos y hashes JSON/Markdown, referencias, observaciones y conteos.
El duodécimo recibo es el primer `same_family` fallido: no tiene publicación ni
generación y no se transforma en un resultado de cero hallazgos.

Los 56 archivos leídos conservaron sus hashes antes/después. Las tres
publicaciones válidas del 14/10 coinciden además con los hashes ya registrados
en [su acta pública](ENSAYO_REAL_A05_2026_10_14.md). Todos los textos de entrada
se ligaron a sus fixtures por digest, líneas seleccionadas y referencias; no
se usó el detector como verdad independiente para decidir los pares esperados.

En proceso Python con conexiones bloqueadas no se importaron CrewAI, LiteLLM,
main, pipeline, dotenv ni el resolver de configuración. No se leyeron logs,
SQLite o `.env` operativos. Los recibos de revisión están en
`.local-state/a05-acceptance-20261020/`, ignorados. El
[registro JSON publicable](REVISION_ACEPTACION_A05_2026_10_20.json) contiene
metadatos, hashes y resultados de comprobaciones, sin logs crudos o credenciales.

## Resultado por muestra

Los tiempos siguientes son los informados por sus ejecuciones históricas;
esta revisión no volvió a consumir esas llamadas.

| Fuente | Caso | Resultado conservado | Llamadas históricas | Segundos |
| --- | --- | --- | ---: | ---: |
| E1 · 07/10 | `mixed` de referencia | Cinco familias/nueve pares; cinco grupos | 4 | 81,000 |
| E1 · 07/10 | `normal` | Cero hallazgos; resumen original «1», defecto histórico conservado | 4 | 475,829 |
| E1 · 07/10 | `missing_body` | Sin hallazgos inferidos de cuerpos ausentes | 3 | 46,312 |
| E1 · 07/10 | `encoded` | Cuatro familias/cuatro pares; cuatro grupos | 3 | 35,719 |
| E1 · 07/10 | `login_window` | Una ráfaga, cinco referencias | 3 | 59,953 |
| E1 · 07/10 | `login_spread` | Sin ráfaga ni hallazgos | 3 | 18,562 |
| E1 · 07/10 | `timezone_split` | Sin ventana común ni hallazgos | 4 | 30,843 |
| E1 · 07/10 | `incomplete` | Cero hallazgos; sin atribución fabricada | 3 | 31,953 |
| E2 · 14/10 | `same_family` inicial | Fallo sin publicación; dos rechazos JSON conservados | 2 | 21,438 |
| E2 · 14/10 | `mixed` | Cinco familias/nueve pares; cinco grupos; normal excluida | 3 | 83,125 |
| E2 · 14/10 | `normal` | Cuatro solicitudes, cero hallazgos; alcance explícito | 1 | 5,000 |
| E2 · 14/10 | `same_family` posterior | Dos eventos SQLi referenciados; dos grupos | 3 | 41,641 |

Las once publicaciones cumplen familias y pares de las fixtures, con selección
completa. Pasan los contratos básicos y la validación observada actual sobre
esas salidas guardadas. Esto verifica compatibilidad de resultados existentes,
no cómo respondería hoy el proveedor a otra solicitud.

La métrica de partición exacta solo difiere en `same_family` posterior: la
fixture actual espera un grupo y el modelo publicó dos eventos separados.
Cada uno tiene una referencia SQLi válida. Se mantiene la aceptación histórica;
no se declara una regresión ni se fusionan los informes para hacer pasar la métrica.

## D1 — Clasificación, grupos y narrativa

La revisión de las tres publicaciones E2 no encontró un nuevo defecto reproducido:

- `mixed`: motivos compatibles con los indicadores de sus solicitudes y cinco
  estados `requires_investigation`; cuatro altas y un XSS medio, dentro de los
  techos de política. La solicitud normal no recibe hallazgo.
- `same_family`: dos motivos en español describen las dos solicitudes SQLi;
  estado `observed_indicator`, severidad alta. Describen indicadores visibles y
  no acreditan vulnerabilidad explotable, intrusión o autenticación exitosa.
- `normal`: cero hallazgos, sin recomendaciones inventadas; el resumen explica
  que el resultado limitado no demuestra tráfico benigno ni seguridad global.

Se reconstruyeron en memoria las tres narrativas deterministas y el Markdown
actual: iguales a los originales E2. Los conteos y referencias corresponden a
los hallazgos; las medidas piden revisión contextual y no ejecutan controles.

E1 usa prompt4/regla2 y narrativa anterior; E2 usa prompt8/regla3. Las ocho
publicaciones E1 no coinciden con el renderizador/narrativa actuales, algo
esperable por la evolución del formato y política. Su integridad original sí
pasa. No se reescriben ni se declara aprobada toda su narrativa: `normal` conserva
el «1» y algunas salidas negativas carecen de las advertencias actuales sobre
evidencia incompleta. Las muestras E2 y sus comprobaciones posteriores son
la referencia preferida para el alcance de narrativa de esta propuesta.

**Conclusión D1:** revisión técnica de muestras completada, sin necesidad
justificada de repetirlas. La aceptación sigue limitada a esas entradas y
versiones; no es una medida general de severidad correcta o detección de ataques.

## D2 — Contexto y selección

Se mantiene E3, la muestra Parrot XSS/ocho POST ya aceptada, por su evidencia
guiada. No se intentó acceder a la VM ni convertir esa confirmación en bytes
que no se recibieron.

Las ventanas 60/61 s, IP separadas, GET/avatar y cabeceras de E4/E5 siguen
verificadas offline. No hay una prueba de proveedor de esas nueve entradas
nuevas ni una demostración de resistencia del LLM a instrucciones en cabeceras.
Las once publicaciones históricas releídas tienen entrada completa: no añaden
aceptación real de una selección truncada. El código/evaluador sí distingue
omisiones de selección y de respuesta, como registra E5.

**Conclusión D2:** no se requiere más evidencia para describir estos límites
con exactitud. Para ampliar la afirmación de calidad haría falta un protocolo
nuevo; esta revisión no lo ejecuta ni lo convierte en requisito automático.

## D3 — Medición y comparación

Los tiempos, modelos y discrepancias de tokens se conservan por muestra en el
JSON. No se mezclan prompts4/8, modelos variables del router y entradas
distintas para calcular una mejora atribuible al código. El normal de 475,829 s
y el de 5 s no son un benchmark controlado. No hay p95 estable, coste facturado
o comparación legacy/structured suficiente para declarar superioridad general.

**Recomendación D3:** diferir expresamente esa afirmación comparativa de la
primera entrega local. Se conserva el criterio original, sin marcarlo cumplido.
Si la comparación se mantiene como requisito de entrega, el siguiente trabajo
será preparar su protocolo controlado antes de autorizar cualquier ejecución.

## Propuesta concreta para D4

Recomiendo aceptar A-05 **para una primera versión local de apoyo a la revisión
de indicadores**, con la evidencia y límites anteriores:

1. Mantener las muestras históricas aceptadas y la validación técnica actual;
   no repetir llamadas para confirmar otra vez los mismos informes.
2. Declarar que grupos y coincidencias no son ataques exitosos, y que el
   resultado depende de las líneas disponibles y seleccionadas.
3. No ofrecer garantías generales de detección, resistencia a prompt injection,
   latencia/coste o superioridad frente a legacy. La comparación original queda
   expresamente diferida si se acepta esta propuesta.
4. Conservar `quality=semantic_evaluation_pending` como estado del resultado;
   esta aceptación de alcance no cambia informes antiguos ni certifica el modelo.
5. Mantener C3 seguridad, C4 entrega y V1 VM como bloques independientes. Esta
   decisión no acepta riesgos residuales, publica una release o actualiza la VM.

## Decisión recibida y cierre de C2

El usuario aceptó la opción de alcance local acotado, incluyendo los cinco
puntos anteriores y el aplazamiento expreso de la comparación con legacy.
**C2 queda cerrado para esta primera versión local.** D1–D4 quedan resueltas
en ese alcance: muestras revisadas, límites declarados y afirmación comparativa
diferida. No se marca realizada una comparación que no existe.

La calidad universal y los casos fuera de las muestras no pasan a ser promesas
de esta versión ni un pendiente indefinido de su aceptación. Ampliar ese alcance
requerirá una tarea y evidencia propias. El campo histórico de resultados
`quality=semantic_evaluation_pending` se conserva porque no se certifica la
calidad general del proveedor; no se reescribe para representar esta decisión.

C3 seguridad, C4 publicación y V1 actualización/recuperación de la VM mantienen
sus condiciones separadas. La respuesta no autoriza nuevas llamadas LLM,
notificaciones, operaciones Docker, publicación de una release o cambios en la VM.

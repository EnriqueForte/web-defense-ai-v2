# A-05 — Cobertura por evidencia y revisión offline, 13/10/2026

Seguimiento 14/10: el [ensayo real autorizado](ENSAYO_REAL_A05_2026_10_14.md)
terminó con resultado parcial e identificó un defecto del envoltorio del
evaluador, corregido antes de los dos casos restantes. La propuesta de abajo
conserva el alcance previo a esa autorización; no es un presupuesto reutilizable.

Se revisó el resumen vigente y se avanzó en el bloque de calidad A-05. La
instalación/lectura Parrot y R-15 ya tienen su evidencia acotada; no necesitan
repetirse para este trabajo. **A-05 sigue abierta:** esta entrega comprueba el
evaluador, las guardas y la publicación con respuestas sintéticas escritas a
mano. No mide la calidad de un proveedor ni sustituye la aceptación del usuario.

## Problema y cambio

La evaluación existente comparaba familias de patrones. Dos solicitudes SQLi
pueden recibir un solo hallazgo sobre una de ellas y obtener recall de familias
igual a 1. Se añadió `same_family`, con dos solicitudes etiquetadas SQLi y una
solicitud normal, y una métrica de pares únicos `(patrón, línea de entrada)`.
En ese ejemplo, las familias pasan y la cobertura de evidencia es 0,5.

Las etiquetas se escriben en `agents/evaluation_fixtures.py` y no se obtienen
del detector. El evaluador verifica el digest de la fixture, las líneas crudas
seleccionadas y sus referencias antes de puntuar. Una referencia ajena o una
fuente distinta se rechazan. Agrupaciones o referencias repetidas entre grupos
no inflan los conteos de pares.

Se distinguen las referencias esperadas ausentes de la selección
(`unselected_evidence_pairs`) y las seleccionadas que faltan en la respuesta
(`missing_evidence_pairs`). `evidence_expectations_met` solo evalúa la selección;
`fixture_fully_selected` informa si todas las líneas de entrada se seleccionaron.
No debe aceptarse un ensayo completo mirando únicamente el primero. Los casos
negativos mantienen recall/precision indefinidos cuando no hay denominador;
`other` sobre el registro incompleto es opcional. Estas etiquetas representan
indicadores visibles, no ataques exitosos, ni exactitud de severidades del modelo.

El evaluador real existente incorpora estas métricas cuando se invoque para
**un caso expresamente autorizado**. `status=succeeded` sigue significando
ejecución/publicación y no aprobación de calidad. No se ejecutó ese evaluador
real en esta entrega. No cambian prompts, motor, versiones de informe,
parámetros del proveedor, reintentos ni condiciones de admisión.

## Matriz reproducible

En Windows, desde la raíz, con el entorno de validación aislado disponible:

```powershell
.p4/Scripts/python.exe -B scripts/check_a05_offline.py
```

En una instalación Linux se usa `.p2/bin/python -B scripts/check_a05_offline.py`.
La nueva matriz pasó posteriormente en Windows/Ubuntu para el commit `c7df36a`,
según el cierre de CI al final de esta acta. La validación local inicial anterior
a publicar y las comprobaciones remotas se distinguen en sus recibos.

El comando solo genera fixtures y publicaciones dentro de una carpeta nueva
de `.local-state/a05-offline-review/`, sin resolver configuración LLM ni leer
`.env`, logs, trabajos o publicaciones operativas. Bloquea conexiones TCP del
proceso durante la revisión. No importa CrewAI ni hace peticiones Docker.

| Comprobación | Resultado local |
| --- | --- |
| Nueve fixtures base: mixto, normal, POST sin cuerpo, codificado, ráfaga, intentos espaciados, zonas distintas, incompleto y misma familia | Expectativas de familias y pares satisfechas con respuestas escritas a mano |
| `other` opcional sobre incompleto y posible falso positivo explícito | Incertidumbre y cautela conservadas |
| Respuesta parcial de la misma familia | Publicable con aviso de omisión; evaluador detecta falta de una referencia |
| Selección limitada a una línea | Referencia fuera de selección registrada; no se declara fixture completa |
| Detección vacía con indicadores, referencia ajena, atribución a solicitud normal, severidad sin soporte, severidad incompatible con falso positivo, clasificación incompleta y narrativa inválida | Siete rechazos esperados; hashes de todos los archivos de la publicación previa conservados |

Los 13 casos y siete controles aprobaron. Se cargaron los manifiestos y se
verificaron hashes JSON/Markdown; también conteos, referencias de medidas,
fuente narrativa Python y ausencia del texto inventado de la respuesta simulada
en la narrativa publicada. El campo `quality=semantic_evaluation_pending`
se mantiene. El resultado parcial se considera correcto **porque el evaluador
detecta la omisión**, no porque esa respuesta esté aceptada como completa.

Recibo local:
`.local-state/a05-offline-review/20261013T125223238874Z/review.json`.
La CI preparada guardará el resumen por OS durante 30 días; las publicaciones
locales sintéticas se conservan en la carpeta del recibo, excluidas de Git.

## Verificación y límites

Regresión local `.p4`: 314 casos Python, 313 aprobados y uno exclusivo Linux
omitido; tres comprobaciones JavaScript aprobadas. Ocho pruebas nuevas cubren
omisiones de la misma familia, agrupación, atribución normal indebida,
selección parcial, negativos, referencias/fuente ajenas y la matriz completa.
Sintaxis: 89 archivos, cero errores; `git diff --check` correcto.
También aprobaron los 25 escenarios CrewAI/LiteLLM offline en `.p4`, con
transporte simulado y red bloqueada, incluidos formato JSON y reintentos de
clasificación. Logs de regresión y SDK en `.local-state/a05-review-20261013/`.

El primer ensayo acotado del evaluador pasó 11 casos y falló uno al reemplazar
un archivo temporal: WinError 5 del sandbox. La repetición autorizada fuera del
aislamiento pasó los 12 casos; después del ajuste de selección completa, la
regresión completa y el comando reproducible también pasaron. No se relajó la
publicación atómica para superar el bloqueo.

No se iniciaron servicios operativos, análisis reales, llamadas al proveedor,
Docker ni envíos. No se modificaron datos operativos, `.env` ni entornos/pines.
Esta entrega no vuelve a auditar el inventario histórico de trabajos/entregas
ni atribuye los hashes de un recibo anterior a una comprobación nueva.

## Siguiente cierre

1. Delimitar y autorizar un ensayo con proveedor para comprobar detección,
   clasificación, formato y narrativa actuales, incluyendo un caso de la misma
   familia y negativos representativos. Revisar ambos tipos de métricas,
   referencias, estados/severidades, guardas, hashes, llamadas y consumo. Cada
   invocación del evaluador existente tiene máximo seis intentos lógicos y
   600 segundos externos; un resultado publicado no acredita calidad por sí solo.
2. Aceptar el resultado con sus límites y completar por separado la ingesta y
   el recorrido del laboratorio en Parrot. La causa histórica de
   `ingestion_failed` sigue sin acreditarse; no se declara resuelta offline.

Seguridad residual/historial, operación/recuperación y entrega final conservan
sus pendientes en [el resumen vigente](ESTADO_FINAL_2026_10_12.md). La revisión
de A-05 no acepta esos riesgos ni acredita restauración o laboratorio real.

## Publicación y CI verificadas

Código publicado `c7df36afd92250f69fc3b7ae4fecb5f6ecf9f64b` en `origin/main`
del repositorio V2. [CI 38411563805](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38411563805),
attempt 1: workflow y jobs Windows-latest/Ubuntu24.04 `completed/success`.
Estados, pasos y logs finales descargados y revisados el 13/10/2026.

Ambos completaron instalación nueva/build, pip check, contrato y freeze de
172 paquetes, cero diferencias y cero extras. Ubuntu aprobó 314 pruebas Python;
Windows aprobó 313 y omitió una regresión exclusiva Linux. También aprobaron
89 archivos de sintaxis, tres comprobaciones JS, HTTP sintético, 25 escenarios
SDK offline, lint/tipos/17 grupos UI, nueve E2E de Configuración por OS
(Ubuntu 9,6 s/Windows 15,5 s) y smoke API/proxy 200/ejecutor offline/cierre de
puertos. Los tiempos E2E no son tiempos de build o de análisis LLM.

Se descargaron los dos artefactos A-05 y se verificaron sus 13 casos y siete
controles, incluyendo cada veredicto, código de rechazo y conservación de
publicación. Sus métricas, checks y hashes de JSON/Markdown coinciden con el
recibo local; solo las identidades aleatorias de generación se excluyeron de la
comparación. Se han revisado los resúmenes descargados; no se afirma haber
descargado los bytes JSON/Markdown de cada publicación remota, que no forman
parte del artefacto de resumen.

| Artefacto | ID | Comprobación |
| --- | --- | --- |
| A-05 Ubuntu | 11821147866 | 13/7 aprobados, métricas/checks/hashes iguales al recibo local |
| A-05 Windows | 11822051481 | 13/7 aprobados, métricas/checks/hashes iguales al recibo local |
| Inventario Python Ubuntu | 11822681266 | Freeze y metadatos completos, 172/0/0, uvloop0.23.0 |
| Inventario Python Windows | 11822241512 | Freeze y metadatos completos, 172/0/0, pywin32311 |

Los bytes de ambos freeze coinciden con el contrato por plataforma y con el
SHA-256 de sus metadatos. Ubuntu:
`2a89e0601de6126ec0449a723bcb0cf67f9b00af092e9abc60264439aa9127fa`;
Windows: `4444efe4144b1000fc66679788ca32dbd9d4685da2fd1161f7eb726fbd93553d`.

Antes de publicar se revisaron 240 archivos candidatos y 594 blobs/52 commits
alcanzables para exclusiones privadas y formatos específicos de credenciales,
sin coincidencias. Los ocho archivos del índice correspondían al candidato
revisado y los hashes vendor coincidían. **Es una revisión acotada**, no la
auditoría exhaustiva de archivos/historial pendiente en seguridad/entrega.

Durante esta publicación se compararon lecturas operativas antes/después:
29 trabajos, 14 entregas y cero activos; las filas consultadas y hashes del log,
puntero, informe y resultado coinciden. Metadatos de `.env` conservados, sin
leer sus bytes. No hubo servicios operativos nuevos, proveedor, Docker ni envíos.
Recibos, ZIP de logs, artefactos y verificación en
`.local-state/a05-ci-20261013/`; no se publican esos archivos ignorados.

El commit posterior de actas usa `[skip ci]`; el código probado por esta CI
sigue siendo `c7df36a`. A-05 continúa abierta por semántica del proveedor,
comprobación manual/ingesta y aceptación con límites.

## Propuesta concreta para el siguiente ensayo real

Pendiente de autorización: tres invocaciones secuenciales y aisladas del
evaluador existente, casos `same_family`, `mixed` y `normal`. Solo fixtures
sintéticas y el router gratuito configurado `openrouter/openrouter/free`, sin
fallback pagado, datos operativos, Docker o envíos. Máximo seis intentos lógicos
y 600 segundos externos por caso: 18 intentos lógicos como límite total; no
se repite un caso fallido ni se amplía el lote automáticamente. Las solicitudes
internas del transporte pueden diferir de los intentos lógicos registrados.

Se revisarían cobertura por familias y por línea, selección completa,
referencias, incertidumbre/severidades, narrativa/medidas, guardas, hashes,
latencia y consumo informado. El éxito técnico no sustituiría la revisión y
aceptación de calidad. Este plan no inicia servicios, worker o admisión manual;
el recorrido de ingesta real Parrot permanece separado.

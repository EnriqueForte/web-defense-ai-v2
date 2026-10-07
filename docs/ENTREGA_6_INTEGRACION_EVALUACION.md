# Entrega 6 — Integración reversible y evaluación A-05

Fecha: 06/10/2026. Estado: integración implementada y validada aisladamente;
evaluación real incompleta. A-05 no está cerrada ni activada.

**Verificación de optimización, 07/10/2026:** nueva muestra normal autorizada
exitosa con structured-prototype-5: 24,000 s, dos llamadas de detección por un
reintento de JSON inválido, cero llamadas de clasificación/narrativa (local_stage
y guardas aceptadas). Informe de Python, cero hallazgos, hashes verificados y
7443 tokens totales informados. Comparación con la misma entrada previa:
475,829 s/cuatro llamadas/34555 tokens. Modelos distintos; no atribuir toda la
mejora temporal solo al código ni declarar p95. Evidencia 20261007T110746967458Z.
Se alinearon después max_tokens=8192/timeout=60 en la fábrica estructurada de
main y el evaluador, sin cambiar legacy; construcción SDK verificada offline.
No arrancó main/worker ni se cambió .env. 212 pruebas Python, tres JS,
17 escenarios SDK aislados y adaptadores legacy/structured construidos sin red.
Detalles en [optimización](OPTIMIZACION_A05_SIN_HALLAZGOS.md); aceptación y
activación siguen pendientes.

**Lote ampliado autorizado, 07/10/2026:** el usuario escogió los siete casos
adicionales con máximo 42 llamadas lógicas. Los siete cumplieron expectativas
de familias y generaron artefactos verificados; se usaron 23 llamadas, sin
repetir casos ni notificar o activar. Resultados, tiempos, consumo, rutas y
límites en [evaluación ampliada](EVALUACION_AMPLIADA_A05_2026_10_07.md).
Normal tardó 475,829 s y su narrativa final era «1», aunque las familias eran
correctas. Se corrigió el formato de informes sin hallazgos: resumen de alcance
y limitaciones desde Python, con narrative_source y structured-report-2.
Los originales se preservaron; revisiones verificadas se publicaron offline en
scope-review-20261007. No hubo llamadas nuevas para esa corrección.
Validación: 211 pruebas Python, tres JS, 15 escenarios offline y 62 archivos
sin errores de sintaxis. El lote no equivale a aprobación semántica general,
comparativa real legacy o activación; A-05 sigue pendiente de esa decisión.

**Verificación real de las correcciones, 07/10/2026:** el usuario pidió continuar
con los pendientes. Se ejecutó una fixture mixta con observed-access-2,
structured-prototype-4 y máximo 8192 tokens. Éxito en 81,000 s y cuatro llamadas
lógicas. Detectó exactamente las cinco familias previstas, sin other ni
candidato sobre /index.html; conteos: cuatro altas y una media, cero bajas,
desconocidas o críticas. La primera detección fue rechazada por
invalid_evidence_reference; el reintento la corrigió. Clasificación y narrativa
pasaron sin reintento; los cuatro completados terminaron con stop.
No se relajaron guardas ni se activó el modo operativo.

Evidencia: `.local-state/a05-evaluation/20261007T102336191604Z/evaluation.json`.
Generación verificada:
`structured/generations/eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee-97d9c368c3fc4413968ae53dedf244fb/`
en esa carpeta. Los metadatos registran 16605 tokens de entrada, 4221 de salida,
20826 totales y **2334 de razonamiento**. usage usa esos metadatos y usage_sdk
conserva el 0 discrepante; usage_discrepancies lo señala, sin warnings de cifras
incoherentes. La cobertura de metadatos es completa. No hubo notificaciones,
Docker, pipeline, main.py, alteración de .env ni publicación en reports operativos.
Los modelos informados variaron por etapa/reintento. Las métricas 5/5 de familias
en esta fixture no acreditan precisión general ni el cierre de A-05.

**Preparación de evaluación ampliada, sin llamadas adicionales:** ocho casos
sintéticos etiquetados en evaluation_fixtures: mixed (misma entrada byte a byte
que el caso anterior), normal, missing_body, encoded, login_window, login_spread,
timezone_split e incomplete. Las expectativas se redactaron separadas del
detector y se contrastan en pruebas: ausencia de cuerpos no demuestra comandos,
una ventana debe alcanzar cinco solicitudes, separar tiempos/zonas evita una
ráfaga ficticia y evidencia no interpretable puede quedar sin candidatos o como
other incierto, sin inventar IP/fecha. No usar ausencia de indicadores como
certificado de seguridad. El caso incomplete admite other opcional, no obligatorio.

El evaluador acepta `--case` y ejecuta **solo un caso por invocación**, con la
autorización explícita existente del CLI, sin lote automático. Los resultados
nuevos explicitan missing_patterns, unexpected_patterns y
pattern_expectations_met; las métricas siguen siendo de familias, con null
cuando no hay denominador. status=succeeded acredita ejecución/publicación;
no equivale por sí solo a pattern_expectations_met ni a calidad semántica.
Presupuesto de una invocación: máximo seis llamadas lógicas, no HTTP internas,
y 600 s externos. Modelos de pago, notificaciones y activación no están incluidos.
Se pidió al usuario elegir el alcance del siguiente lote. Eligió siete casos,
se ejecutaron y quedaron registrados en la evaluación ampliada indicada arriba.

Verificación actual: **208 pruebas Python**, tres diagnósticos JS, 15 escenarios
CrewAI/LiteLLM offline, sintaxis de 62 archivos y diff limpio. Queda evaluar los
casos autorizados, revisar narrativa/incertidumbre y comparar calidad/latencia/
consumo de forma representativa antes de decidir la activación. Las cuatro
diferencias de .venv operativa y la excepción braces conservan su seguimiento.

**Seguimiento de calidad autorizado tras el ensayo exitoso:** se implementó
la política `observed-access-2` y las instrucciones `structured-prototype-4`.
El candidato `other` necesita que **cada** referencia tenga algún indicador
observado por Python o una petición que no se haya podido interpretar completa
(método, destino o estado HTTP ausente). Una petición interpretable sin criterios
observados no puede convertirse en un hallazgo solo para rellenar una tabla.
No se excluye una URL concreta ni se elimina evidencia de la muestra.
La preparación comunica `uncertainty_evidence_ids`; `other` puede conservar
requires_investigation/probable_false_positive, pero no observed_indicator.
Las guardas usan `other_without_observation` y `unobserved_other_state` y rechazan
antes de publicar. No corrigen silenciosamente la salida ni certifican tráfico
benigno. Un ataque desconocido sin criterio de soporte en una petición bien
formada sigue siendo un límite de esta política; futuras anomalías requieren
criterios explícitos, no una etiqueta inventada por el modelo.

Se comprobaron dos recorridos con CrewAI real/doble LLM: candidato falso sobre
/index.html rechazado y corregido en el reintento, y muestra normal no vacía
que termina con candidates/classifications/recommendations vacíos y cero
hallazgos. Los indicadores conocidos y la evidencia no interpretable conservan
su posibilidad de revisión. El informe anterior se preserva ante un rechazo.

La conciliación de uso ahora deriva `evaluation.json.usage` de los metadatos de
completado, con origen y cobertura explícitos; el acumulador SDK queda separado
en `usage_sdk`. `usage_discrepancies` registra diferencias sin ocultar el cero del
SDK y `usage_warnings` señala razonamiento superior a salida o total incoherente,
sin alterar las cifras del proveedor. Si falta un campo queda null; si falta una
llamada, se repite su ID o se perdieron eventos, no se informa un total completo.
Un hijo interrumpido conserva el checkpoint y el estado failed, con uso parcial
señalado. Estas cifras no equivalen a facturación ni a número de peticiones HTTP
internas: son completados observados asociados a llamadas lógicas.

Se revisaron **sin llamadas nuevas** los artefactos de la ejecución exitosa
20261006T205327334773Z. La nueva guarda rechaza su falso positivo y el agregado
reconcilia 17216 tokens totales/3403 de razonamiento frente al cero SDK. El
registro derivado está en `usage-quality-review.json` de esa carpeta; no se
reescribieron `evaluation.json`, diagnósticos, JSON, Markdown o manifiesto originales.

Verificación actual: **203 pruebas Python**, tres JS, **15 escenarios
CrewAI/LiteLLM aislados**, sintaxis de 60 archivos y diff sin errores de espacios.
No se hizo ninguna llamada real en este seguimiento. API `/api/v1`, lectores
históricos, tipos públicos y prompts legacy permanecen compatibles; las guardas
se endurecen solo para análisis nuevos del flujo estructurado. La configuración
operativa sigue legacy. Para revertir operacionalmente se mantiene ese modo y
se preservan los artefactos; no borrar históricos ni alterar la evidencia previa.
Falta verificar el comportamiento del proveedor con esta política y ampliar
la evaluación representativa antes de aceptar la activación.

**Primer ensayo real completo exitoso:** autorizado por el usuario el 06/10/2026,
con límite 8192 y revisión `structured-prototype-3`. El flujo pasó detección,
clasificación, narrativa, publicación y verificación de hashes. Cuatro llamadas
lógicas y 57,625 s de ejecución; todas terminaron con `stop` y contenido final.
La primera clasificación fue rechazada por `severity_without_support`; el único
reintento corrigió la salida y fue aceptado. No se relajaron las guardas.
Se publicó solo en la carpeta aislada; modo operativo legacy y notificaciones
desactivadas. A-05 permanece abierta por calidad/representatividad/aceptación.

Evidencia: `.local-state/a05-evaluation/20261006T205327334773Z/evaluation.json`.
Generación verificada:
`structured/generations/eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee-344681fb22534b6191e0095bf3420de4/`
en esa carpeta, con `result.json`, `report.md` y `manifest.json`.

Se encontraron las cinco familias previstas: SQLi, XSS, traversal, comandos y
la ventana de cinco POST /login. Se añadió un sexto candidato `other`, low,
observed_indicator, sobre la petición normal GET /index.html de la línea 10.
Ese candidato es un falso positivo de esta fixture. La tabla tiene cuatro altas,
una media y una baja, sin críticas. Las métricas del evaluador son de **familias**:
recall 5/5 y precision 5/6 (83,33 %); no son precisión global por evento ni una
evaluación general del motor. Un solo análisis no resuelve el falso positivo.

Los modelos informados variaron entre tareas y reintento: detección
nvidia/nemotron-3-super-120b-a12b:free; primera clasificación
liquid/lfm-2.5-2.6b:free; clasificación corregida poolside/laguna-s-2.1:free;
narrativa nvidia/nemotron-3-ultra-550b-a55b:free. Por esa variabilidad no se atribuye
el éxito exclusivamente al cambio de IDs ni se acredita la recuperación del
modelo cohere de intentos anteriores. El router configurado sigue siendo el mismo.

Uso informado: 11946 tokens de entrada + 5270 salida = 17216 totales. Los
metadatos por llamada suman 3403 tokens de razonamiento, mientras el acumulador
SDK de `evaluation.json.usage` informa 0. Se conserva la discrepancia; **no**
interpretar ese cero como ausencia de razonamiento. No se obtuvo un registro de
cargos y no se deduce facturación del número de tokens. Los archivos originales
de evidencia permanecen intactos. Próximos pendientes: falso positivo en tráfico
normal, conciliación del resumen de razonamiento, evaluación representativa y
decisión explícita de activación; no hacer llamadas adicionales sin su alcance.

**Intento real autorizado con límite 8192:** 06/10/2026, dos llamadas lógicas,
80,765 s de ejecución. En la primera, el modelo informado
`cohere/north-mini-code:free` terminó con `stop` y devolvió 1834 caracteres de
JSON válido según el esquema de ese momento. Uso: 2580 entrada, 3570 salida,
6150 total y 3039 de razonamiento. La guarda de detección rechazó
`duplicate_or_invalid_candidate`: algún ID incumplía el formato `c_...` o se
repetía. Al no conservar salidas crudas, no se distingue cuál de esas condiciones.
El reintento previsto por la guarda obtuvo `length`, sin contenido final, con
8192 tokens de salida; no hubo clasificación, narrativa o publicación.
El proveedor informó 8894 tokens de razonamiento en el reintento, superiores
a los de salida; se preserva esa discrepancia sin sumar ni reinterpretar.
Evidencia: `.local-state/a05-evaluation/20261006T204921271967Z/evaluation.json`.
No se hicieron llamadas adicionales ni se modificó el modo operativo.

**Corrección posterior comprobada offline:** el esquema Pydantic exponía
candidate_id como una cadena genérica, mientras el validador contractual ya
exigía `c_[a-zA-Z0-9_-]{1,60}` y unicidad. Ahora Detection, Classification y
Narrative incluyen ese patrón y longitud en el esquema recibido por el modelo.
La instrucción de detección pide IDs distintos `c_1`, `c_2`, `c_3` y prohíbe
repetir grupos; las siguientes etapas deben copiar los IDs sin renombrarlos.
No se normalizan IDs inválidos ni se relajan las guardas. Se registra la revisión
de instrucciones como `structured-prototype-3`; los prompts legacy no cambian.
Validación: 192 pruebas Python, tres JS y 13 escenarios CrewAI/LiteLLM aislados,
incluidos rechazo de formato y duplicación, preservando el informe anterior.
Sintaxis de 57 archivos sin errores. Falta evaluar esta corrección con otra
ejecución autorizada. El router y el límite 8192 siguen en el evaluador.

**Intento real con metadatos de completado:** autorizado por el usuario el
06/10/2026. Falló en detección tras una llamada y 15,531 s de ejecución.
La respuesta LiteLLM informó modelo `cohere/north-mini-code:free`,
`finish_reason=length`, `max_tokens=2048`, 2580 tokens de entrada, 2048 de
salida y 4628 totales. `message.content` no contenía texto y había razonamiento;
el adaptador devolvió 0 caracteres y CrewAI lanzó ValueError. No se llegó a
guardas, clasificación, narrativa o publicación. La llamada obtuvo un completado
del proveedor; no hubo error de autenticación, informe o notificaciones.
Evidencia: `.local-state/a05-evaluation/20261006T204703125251Z/evaluation.json`.

La causa inmediata ahora acreditada es el corte del completado al límite de
salida sin texto final. El proveedor también informó 2267 tokens de razonamiento,
superiores a los 2048 de salida: esa discrepancia se conserva, sin recalcularla,
sumarla ni afirmar que todos los tokens se gastaron en razonamiento.
Estos datos corresponden a este intento, no explican necesariamente cada fallo
anterior ni garantizan que el router vuelva a elegir ese modelo.

Se preparó un ajuste del **evaluador aislado** a `EVALUATION_MAX_TOKENS=8192`.
No altera `.env`, el LLM operativo, prompts, criterios, modelo o modo legacy;
mantiene seis llamadas lógicas máximas, timeout de 60 s por petición y plazo
externo de 600 s. No se hizo una segunda llamada tras el intento. Falta una
nueva ejecución autorizada con ese límite para comprobar si produce JSON válido;
aumentarlo no acredita por sí solo éxito ni cierra A-05.

**Metadatos de completado añadidos:** el usuario autorizó preparar el siguiente
diagnóstico sin nuevas llamadas. El evaluador observa ahora la salida síncrona
de `litellm.completion` **antes** de que CrewAI la convierta a texto, y añade un
evento `completion_returned` asociado a la etapa y llamada lógica. Registra
`finish_reason` de una lista permitida, modelo solicitado, modelo informado por
la respuesta, límite `max_tokens`, presencia/longitud de contenido, presencia
de razonamiento y tokens de entrada, salida, total y razonamiento. Las cifras
ausentes o inválidas quedan `null`, sin convertirlas a cero ni inferirlas.
El nombre de modelo se limita a un identificador válido y se omite si contiene
la credencial de la ejecución. No se guardan mensajes, razonamiento, cabeceras,
IDs de petición, argumentos completos ni objetos serializados del SDK.

La captura está restringida al proceso aislado del evaluador, restaura la función
original al salir incluso con excepción y devuelve la misma respuesta al
adaptador. No cambia el modelo, límite de 2048 tokens, reintentos, guardas,
notificaciones o modo operativo. Los metadatos quedan en el checkpoint y en
`evaluation.json` con el mismo límite de 100 eventos. Un formato inesperado del
SDK marca metadatos no disponibles; una excepción del SDK se conserva.
El modelo informado no acredita por sí solo qué modelo físico usó el router;
solo se registra lo que la respuesta LiteLLM expone. `finish_reason=length` y
tokens de razonamiento permiten investigar un agotamiento de salida, pero esta
entrega no atribuye esa causa al fallo real anterior.

Validación de esta ampliación: **192 pruebas Python**, tres diagnósticos JS,
**11 escenarios CrewAI/LiteLLM sin proveedor** y 57 archivos sin errores de
sintaxis. Se ensayan completado normal, contenido nulo con finalización por
límite y 2048 tokens de razonamiento, datos ausentes/hostiles, confidencialidad,
excepción del SDK y restauración del observador. Son fixtures sintéticas;
no hubo ninguna llamada real nueva. Falta una prueba autorizada para obtener
estos metadatos de OpenRouter y decidir la corrección necesaria.

**Nuevo intento real autorizado con diagnóstico:** el 06/10/2026 el usuario
pidió repetirlo de nuevo. Se hizo una llamada lógica al router gratuito y el
adaptador devolvió una cadena vacía: `characters=0`, etapa `detection`, duración
35,469 s de llamada/35,516 s de ejecución. La traza termina en
`agent_utils.py:417`, `_validate_and_finalize_llm_response`, que lanza ValueError
cuando la respuesta es vacía. No se llegó a las guardas de evidencia,
clasificación, narrativa o publicación. No aparece AuthenticationError.
No se generó un informe ni hubo notificaciones; el modo operativo sigue legacy.
Evidencia: `.local-state/a05-evaluation/20261006T203937479377Z/evaluation.json`
y `diagnostics.json` de esa misma carpeta. Esta evidencia identifica la causa
inmediata del ValueError en **este** intento; no prueba la causa de intentos
anteriores ni acredita el origen de la respuesta vacía.

La ruta LiteLLM de CrewAI instalada obtiene el texto de `message.content` y
usa una cadena vacía si no hay contenido. El evaluador limita la salida a
2048 tokens, pero no registró `finish_reason`, el modelo físico seleccionado
por el router ni los tokens de razonamiento. Por ello no se atribuye el fallo
a agotamiento de tokens, razonamiento o disponibilidad sin más evidencia.
El siguiente diagnóstico debe recoger solo esos metadatos seguros para
distinguir la respuesta del proveedor y su adaptación. No se repitieron
llamadas automáticamente tras el fallo.

**Diagnóstico por etapa implementado posteriormente:** el usuario autorizó
añadirlo. El evaluador ahora incluye metadatos de configuración, preparación,
construcción, detección, clasificación, narrativa, publicación, verificación y
métricas. Cada llamada registra duración, longitud y estado JSON/esquema;
las guardas registran aceptación o código contractual permitido. Los errores
guardan tipos y ubicaciones del código conocido, sin mensajes, líneas fuente,
variables locales, prompts, respuestas, claves, valores/ubicaciones Pydantic
o cuerpos HTTP. Los eventos se limitan a 100. Se escribe `diagnostics.json`
atómicamente tras cada evento y se incluye en `evaluation.json`, también si
el proceso termina sin reporte o alcanza los 600 segundos. El código fuera
de la lista conocida no muestra su ruta ni su función.

El observador es opcional; `main.py` no lo activa y la ruta legacy no cambia.
Las respuestas y guardas conservan su comportamiento: diagnosticar no repara
JSON, no relaja el contrato ni permite publicar una salida rechazada.
La descripción `json_invalid` de la respuesta directa debe interpretarse junto
con la guarda: CrewAI puede extraer JSON de su formato textual de respuesta.

Validación posterior: **186 pruebas Python**, tres diagnósticos JS y **nueve
escenarios CrewAI sin proveedor**, incluidos respuesta vacía, código de rechazo
por referencias y transmisión de clave/URL sintéticas a LiteLLM. Sintaxis:
55 archivos sin errores. Las pruebas de confidencialidad usan secretos ficticios
en excepciones, respuestas y errores Pydantic y comprueban que no se registran.
Se reproduce `ValueError` con un doble de respuesta vacía en CrewAI real y se
localiza en detección/`agent_utils.py`, conservando el informe anterior.
Eso es una reproducción sintética, no evidencia de la causa del intento real.
No se hicieron llamadas reales nuevas en esta entrega de diagnóstico; para
precisar el fallo real debe ejecutarse otro intento autorizado con este registro.

**Repetición real autorizada tras corregir el adaptador:** el usuario pidió
repetir la prueba. El intento del 06/10/2026 registró `ValueError`, dos llamadas
lógicas y 50,031 segundos; no aparece `AuthenticationError` en la cadena
registrada. No se publicó un informe ni una generación. Esto no permite marcar
el análisis ni A-05 como exitosos. El evaluador conservó tipos de excepción,
sin mensaje, respuestas crudas ni trazas; esa evidencia no identifica por sí
sola si el ValueError procede del formato, de una guarda o de otra capa.
El siguiente intento necesita diagnóstico por etapa antes de nuevas llamadas.
No se hicieron llamadas adicionales tras este fallo ni se activó el motor.
Evidencia local: `.local-state/a05-evaluation/20261006T203052903002Z/evaluation.json`.
La ausencia del error anterior en este intento no constituye una validación
independiente de la credencial ni una evaluación de calidad completada.

**Corrección del diagnóstico:** después de que el usuario indicara que la clave
ya estaba configurada, se revisó CrewAI 1.14.2 instalado. Su ruta
`LLM.call(response_model=...) → InternalInstructor.to_pydantic` invoca LiteLLM
sin transmitir `api_key`, `base_url`, timeout ni otras opciones del LLM recibido.
Por tanto, el rechazo observado no acredita que la clave guardada sea incorrecta.
Se añadió un adaptador de JSON original para las tareas estructuradas que
mantiene todas las llamadas en el LLM configurado y valida la salida localmente.
La prueba aislada con CrewAI/LiteLLM reales y credencial sintética verifica una
sola llamada de completado, clave y URL explícitas, y prohíbe la ruta Instructor.
Ahora pasan siete escenarios CrewAI. La prueba real se repitió posteriormente
con el resultado indicado al principio de este documento.

## Comportamiento y compatibilidad

`ANALYSIS_ENGINE_MODE=legacy` es el valor predeterminado. No se modificó `.env`
ni se reiniciaron servidores, coordinadores o laboratorios. Los prompts,
agentes y preparación anteriores se conservan para el retorno.

Con `structured`, `main.py` lee hasta 1 MiB de UTF-8 y utiliza preparación,
tres tareas CrewAI validadas y publicación JSON/Markdown por generaciones.
El identificador del trabajo del coordinador se transmite al subproceso;
una ejecución directa utiliza un UUID nuevo. No se publica una salida vacía,
inválida o incompleta ni se toca `reporte_seguridad.md` anterior.

El coordinador y Flask comparten el selector `active_report`. Solo una
generación con puntero, manifiesto y ambos hashes válidos puede representar
el informe actual. Un artefacto corrupto indica fuente no disponible; no se
sustituye silenciosamente por el informe anterior. El coordinador verifica
un identificador nuevo, archiva el mismo Markdown y deriva las notificaciones
de esa tabla. La entrega de notificaciones conserva su contrato anterior.

La API `/api/v1` mantiene sus rutas, campos e identificadores de 64 caracteres.
El informe actual estructurado tiene `filename=report.md`; el cliente debe
seguir usando su identificador para el detalle. El enlace HTML anterior
`/report/reporte_seguridad.md` utiliza el selector. Next.js no cambia, sigue
consumiendo Flask; no se incorporan claves ni accesos al motor al frontend.

El historial visible sigue siendo Markdown archivado por el coordinador.
Las generaciones conservan sus JSON localmente; esta entrega no añade una API
de resultados JSON ni expone huérfanos tras una publicación fallida.
El respaldo de los perfiles conocidos incluye `current.json`, `manifest.json`
y `result.json` generacionales, además del Markdown, y toma el bloqueo de
publicación. Se ensaya restauración aislada con verificación de la generación.
Las rutas personalizadas siguen fuera de esos perfiles automáticos.

## Verificación

- Suite aislada: 179 pruebas Python, sin fallos ni expectedFailure, y tres
  diagnósticos JavaScript. Fixtures sintéticas y transportes simulados.
- Sintaxis: 53 archivos Python sin errores.
- CrewAI 1.14.2 del entorno limpio `.p2`: siete escenarios sin proveedor,
  incluidos contratos, guardas, integración del runner, publicación temporal,
  lectura por el selector y retorno al informe anterior. Ninguna llamada real.
- La cobertura nueva incluye enrutamiento de `main.py` mediante AST, identidad
  del subproceso, coordinación/publicación/archivo/notificación simulada,
  API de catálogo/detalle, corrupción sin fallback, entrada acotada y respaldo.
- `git diff --check` sin errores de espacios; avisos de conversión LF/CRLF.

## Intento real autorizado

El usuario autorizó **un análisis sintético con OpenRouter y el modelo gratuito
configurado, sin modelos de pago**. Se creó un evaluador separado que comprueba
proveedor, credencial configurada, modo gratuito y candidato único
`openrouter/openrouter/free` antes de ejecutar. Ese identificador LiteLLM usa
el [router gratuito oficial](https://openrouter.ai/docs/cookbook/get-started/free-models-router-playground).
No tiene candidatos de pago. No invoca `main.py`, pipeline, Docker o transportes.

La fixture contiene diez peticiones de documentación `192.0.2.1`: indicadores
SQLi, XSS, traversal, comandos, cinco POST /login dentro de la ventana y una
petición normal. No se usan logs operativos. Se preparan métricas de familias,
recuento, latencia y uso; una sola fixture no acredita calidad semántica general.
La evaluación usa el adaptador LiteLLM sin reintentos configurados del SDK,
máximo seis llamadas al adaptador de tareas y límite externo de 600 segundos.
Ese contador no mide peticiones HTTP internas del proveedor/conversor.
El adapter de evaluación acotado no ensaya los reintentos operativos completos.

El primer intento restringido falló en la primera llamada lógica con
`InstructorRetryException`; no permite atribuir por sí solo la causa a la red.
El segundo intento, con acceso de red aprobado, registró la cadena
`InstructorRetryException → RetryError → AuthenticationError →
OpenRouterException → HTTPStatusError`, después de una llamada lógica (0,328 s).
No se guardaron claves, cuerpos HTTP o mensajes crudos de excepción.
No se repitieron llamadas después de identificar el rechazo de autenticación.

Evidencia local final:
`.local-state/a05-evaluation/20261006T194209641941Z/evaluation.json`.
Evidencia del intento inicial:
`.local-state/a05-evaluation/20261006T193734641544Z/evaluation.json`.
No se produjo un informe ni una generación en ninguno. No hay métricas de
calidad, tokens o coste real completadas; no inferir coste cero del fallo.

## Activación y retorno preparados, aún pendientes

1. Revisar y aceptar resultados/límites de la evaluación ampliada, incluyendo
   narrativa corregida y variabilidad de latencia. Si se requiere una comparativa
   real legacy o más repeticiones, definir alcance y presupuesto antes de llamar.
   No es necesario sustituir la clave por el fallo anterior. Solo revisar la
   credencial local si la llamada corregida también rechaza la autenticación,
   sin compartirla en el chat.
2. Revisar contrato, candidatos, referencias, falsos positivos/omisiones,
   incertidumbre, latencia y consumo. Para cerrar A-05 se necesita una comparación
   representativa y aceptación, no solo una fixture exitosa.
3. Tras aceptar la evaluación, detener los procesos de análisis y tomar respaldo
   verificado. Configurar **el mismo** `ANALYSIS_ENGINE_MODE=structured` y
   `REPORT_PATH` en motor, coordinador y Flask; reiniciarlos de forma coordinada.
   Next mantiene el rewrite local. Hasta la primera generación válida, la fuente
   estructurada aparecerá no disponible; no copiar el reporte anterior como nueva
   evidencia ni usar simultáneamente procesos con modos diferentes.
4. Para volver, detener los procesos de análisis, restaurar
   `ANALYSIS_ENGINE_MODE=legacy` en los tres procesos y reiniciarlos. El informe
   anterior sigue en su ruta; los JSON/Markdown estructurados se preservan.
   No eliminar históricos ni generaciones como parte del retorno.

Pendientes externos a esta entrega: transición de `.venv` a las dependencias
validadas, excepción braces sin parche publicado y las limitaciones de
observación histórica del piloto. Los defectos del flujo legacy continúan
vigentes mientras siga seleccionado. El estado `semantic_evaluation_pending`
del resultado y la dependencia del hook privado de CrewAI se mantienen explícitos.

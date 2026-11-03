# F5 — preparación de la evaluación del detector

02/11/2026. Estado: **preparación de código y protocolo; evaluación no ejecutada**.
No se han realizado escenarios, peticiones HTTP, llamadas al modelo ni nuevas
pruebas automáticas. El permiso Groq anterior está consumido.

**Decisión posterior del propietario, 03/11: F5 cerrada sin evaluación adicional.**
El propietario ordena cerrar F4/F5 si requieren pruebas. Se registra el cierre
expreso de alcance con la evidencia disponible y la evaluación del detector
omitida/no realizada. No se afirma que se hayan alcanzado 27/30, 5/6 por
familia o cero falsas alarmas. Los originales siguen sin localizar; no se
reconstruyen ni se inicia otra búsqueda para cerrar esta entrega.

Se retiran del trabajo de cierre la ejecución de los cinco tests del
empaquetador, el paquete real, el desarrollo/validación pendiente del ejecutor
y puntuador y las llamadas al modelo. Las herramientas preparadas se conservan
con su estado real, sin presentarlas como evaluación terminada. No se cambia
el PRD o los JSON históricos. El [registro de decisiones](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md)
prevalece sobre las propuestas inferiores; no queda ninguna de ellas como
instrucción de ejecución o bloqueo de fase F5.

## Revisión documental completada — 03/11, sin ejecución

Tras cerrar F6 por decisión expresa, el propietario pide continuar con trabajo
que no implique pruebas. Se revisan por lectura el PRD, los metadatos históricos,
el protocolo, el código del empaquetador y el puntuador sintético V2 existente.
No se ejecuta ninguno de esos programas, ni comandos de ayuda, parsers de
validación, búsquedas nuevas en la VM, empaquetado, hashes o evaluación.

| Elemento revisado | Conclusión documental |
| --- | --- |
| Archivo funcional histórico | El índice declara 45 casos: 30 intentos y 15 benignos, cinco familias y 75 líneas correlacionadas; 42 conformes HTTP y tres fallos históricos de comandos. Son resultados funcionales, no TP/FN/FP/TN del detector |
| Procedencia | El índice conserva referencias y hashes de 92 archivos revisados en su momento. No sustituye sus bytes originales ni permite verificar de nuevo su integridad; no hay una copia original nueva localizada por este paso |
| Preparación | El empaquetador contempla tres lotes de 15 casos/25 líneas, separación de entrada y etiquetas y rechazo de selección incompleta. Es lectura del código; no se prepara un paquete ni se acredita su funcionamiento |
| Puntuación existente | `agents/evaluation_scoring.py` puntúa fixtures V2 y grupos de indicadores. No es el puntuador por caso del archivo histórico Puerto Umbral ni aporta sus métricas F5 |
| Estado de evaluación | No hay resultados propios de esta evaluación para calcular precisión, recall o falsas alarmas. El informe anterior de 17 líneas y sus cuatro grupos no permiten completar esos denominadores |
| Presupuesto | Las 18 solicitudes inferiores son una propuesta histórica sin autorización. No se consume presupuesto, se consulta cuota o se contacta al proveedor |

### Expediente de criterios F5, con evidencia existente

| Criterio | Estado tras esta revisión |
| --- | --- |
| F5-AC1 | Registro histórico de los 45 casos cubierto según acta previa, con los tres fallos conservados; no se reejecuta |
| F5-AC2 | Cerrado por decisión expresa de alcance del 03/11; evaluación omitida y objetivos sin medir, sin declararlos cumplidos |
| F5-AC3 | Conclusiones editoriales revisadas: se distinguen intento, bloqueo, efecto y evidencia insuficiente; HTTP conforme no se presenta como acierto del detector |
| F5-AC4 | Se reutilizan las recepciones anteriores de instalación/actualización y cierre en Parrot, sin pedir una instalación o arranque nuevos |
| F5-AC5 | Se conservan índices, consumo registrado y límites de respaldos anteriores; los originales necesarios para la evaluación siguen sin localizar. No se afirma que el respaldo V2 incluya automáticamente los originales bajo `labs/` |

**Resultado vigente:** revisión documental F5 completada, evaluación
del detector no realizada y fase F5 cerrada por decisión expresa de alcance. La documentación de entrega
puede describir funciones, recorridos recibidos y cierre F6 por decisión del
propietario. No puede anunciar que se alcanzó 27/30, 5/6 por familia o cero
falsas alarmas, ni convertir 42/45 conformes HTTP en precisión del detector.

Mientras siga vigente el trabajo sin pruebas, se mantiene este expediente
con sus límites. Las instrucciones de ejecución inferiores se conservan como
preparación histórica suspendida; no son el siguiente paso autorizado ni se
solicita al propietario realizarlas. Tampoco se desarrolla otro ejecutor sin
validación como atajo para cerrar las métricas pendientes.

## Entrada que falta localizar

El [índice histórico](PUERTO_UMBRAL_F5_CORPUS_2026_10_27.json) conserva metadatos
y hashes de 45 casos y 92 archivos revisados. No contiene los logs originales.
La búsqueda dentro de este checkout no ha encontrado `suite.json`; tampoco
está la carpeta original `runs/` en la ubicación histórica. Esto no demuestra
que no exista otra copia en Windows, Parrot o un respaldo externo.

Se necesita la copia existente de `suite.json`, sus 45 carpetas `runs/<id>/`
con recibo y snapshot, y el `corpus.json` físico de esa ejecución. Se mantienen
sus bytes, incluidos finales de línea: el corpus de Git normalizado a LF puede
tener un hash diferente al original CRLF. No se regeneran solicitudes, recibos
o tráfico a partir de las etiquetas. El log actual de 94 líneas y el informe
anterior de 17 líneas no sustituyen este conjunto congelado.

## Herramienta preparada

`scripts/prepare_puerto_umbral_evaluation.py` permite consultar el plan sin
crear archivos. Solo `--prepare` habilita la creación de un directorio nuevo.
Su ayuda no importa la aplicación ni carga credenciales.

El empaquetado, cuando estén los originales, realiza lo siguiente:

1. Reutiliza el revisor de integridad existente y exige coincidencia del
   archivo completo con el índice histórico: corpus, suite, recibos y logs.
2. Extrae únicamente las líneas correlacionadas de cada recibo; no concatena
   snapshots acumulados ni añade respuestas HTTP a la entrada del detector.
3. Forma tres lotes, por variante histórica: 15 casos y 25 líneas cada uno,
   con diez intentos y cinco usos normales. Ordena por fecha observada y hash,
   sin ordenar por la respuesta esperada. Las líneas ambiguas se rechazan.
4. Comprueba mediante la preparación de producción que las 25 líneas quedan
   seleccionadas. La selección admite hasta 30; un lote único de 75 perdería
   evidencia. No se modifica esa política para mejorar una puntuación.
5. Escribe `detector/batch-N.log` y, por separado,
   `evaluator/manifest.json`: correspondencia caso/líneas, etiquetas, hashes,
   alcance de selección e identidad opaca del análisis. Recomprueba los bytes
   originales antes de escribir y nunca sobrescribe un directorio existente.

El manifiesto del evaluador **no se incorpora al prompt**. El futuro ejecutor
solo puede enviar al modelo la evidencia preparada y el contexto habitual del
detector. La separación de carpetas es una convención de entrada, no un límite
de permisos del sistema operativo.

Un fallo de escritura puede dejar un directorio parcial nuevo, que no debe
utilizarse ni sobrescribirse. Solo una salida final `prepared_not_evaluated`
acredita que el empaquetador terminó; no acredita detección correcta.

No se ha preparado un paquete real: los originales aún no están localizados.
Las cinco pruebas de `tests/test_puerto_umbral_evaluation_pack.py` están
escritas con archivos sintéticos temporales y revisión simulada; **no ejecutadas**.
No constituyen evidencia funcional del laboratorio ni una evaluación del modelo.

## Puntuación que debe fijarse antes de ejecutar

Objetivo del [PRD](PRD_PUERTO_UMBRAL_2026_10_26.md): al menos **27/30 intentos**
identificados, **5/6 por familia** y **cero falsas alarmas en 15 usos normales**.
La unidad es el caso, no el grupo del informe, la línea o el código HTTP.

| Regla | Tratamiento |
| --- | --- |
| Correspondencia | El resultado debe tener el mismo `analysis_id`, digest de entrada y evidencia exacta del lote; cada referencia debe existir |
| Intento identificado | Al menos un hallazgo de su familia referencia una línea del caso, con estado `observed_indicator` o `requires_investigation` |
| Intento omitido | Ningún hallazgo de su familia cumple esa condición; una familia equivocada no da un acierto |
| Uso normal | Cualquier hallazgo con uno de esos dos estados que lo referencia cuenta como falsa alarma, incluso en un grupo que incluye otros casos |
| Falso positivo probable | Se registra por separado; no se convierte en acierto de un intento ni se oculta del detalle del caso |
| Agrupación | Varios hallazgos no multiplican aciertos; un hallazgo compartido se atribuye a todos los casos que referencia |
| Error o evidencia omitida | Evaluación incompleta; no publicar un aprobado ni reducir denominadores para eliminar los casos difíciles |
| Fallos HTTP históricos | Los tres `Cannot fork` siguen en el histórico y en los denominadores de detección de intentos; detectar una solicitud no prueba su efecto |

Familias: `sqli → sql_injection`, `xss → xss`,
`traversal → path_traversal`, `command → command_injection`,
`brute → brute_force`. Brute force requiere su contexto de ráfaga: las
solicitudes no se analizan como casos aislados sin ese contexto. Una agrupación
que arrastre tráfico benigno debe reflejarse como falsa alarma; no se ajustan
ventanas, umbrales o lotes después de ver los resultados para borrarla.

La salida necesaria será una fila por cada uno de los 45 casos, con referencias,
familia/estado observados y veredicto, más TP/FN por familia, FP/TN benignos,
precisión, recall y tasa de falsas alarmas. Se conservan los tres resultados
estructurados y sus recibos de transporte. El puntuador y el ejecutor con
presupuesto aún deben implementarse y revisarse; este empaquetador no los sustituye.

## Presupuesto propuesto, todavía no autorizado

Tres lotes y tres etapas del detector. Los guardrails existentes admiten una
corrección por etapa. Se propone un **tope externo de 18 solicitudes de
transporte en total**, seis por lote, 8.192 tokens máximos de salida por
solicitud y 600 segundos por lote. Si el agente intenta más llamadas, el futuro
ejecutor debe detenerlas antes de enviarlas. No se presenta el guardrail como
garantía suficiente del número de solicitudes reales.

Sin reintentos de red, fallback de modelo, ejecuciones paralelas ni repetición
automática tras un fallo. Modelo propuesto: el Groq ya configurado
`groq/openai/gpt-oss-120b`, sujeto a disponibilidad y aceptación posterior del
propietario. Se registrarían llamadas iniciadas/completadas, tokens reales,
duración, errores y cualquier omisión; las respuestas incompletas se conservan.

Este límite no garantiza que la cuota gratuita permita terminar ni prueba un
coste de cero. No se ha consultado al proveedor, verificado facturación o
reservado cuota. Antes de ejecutar hay que revisar el paquete real, completar
el control de presupuesto y acordar expresamente ejecución y cuenta gratuita.
Los resultados se guardarían en un directorio de evaluación separado, sin
publicar sobre el informe actual, encolar trabajos o emitir notificaciones.

## Secuencia de ejecución prevista antes de la restricción vigente

Localizar la copia original conservada. Después: validar el empaquetador con
sus cinco pruebas aisladas cuando se autoricen, preparar el paquete real y
terminar ejecutor/puntuador sobre su formato comprobado. Ninguno de estos pasos
autoriza una llamada al modelo. Esta secuencia es histórica: F5-AC2 queda
después cerrado por decisión expresa de alcance, sin evaluación, según la
cabecera. La aceptación final del conjunto permanece separada.

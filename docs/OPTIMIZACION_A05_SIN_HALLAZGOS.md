# A-05 — Llamadas en análisis sin candidatos

Fecha: 07/10/2026. Implementado, verificado offline y medido con OpenRouter en
una nueva muestra autorizada. No se activa ni se reutiliza el saldo del lote.

## Medición real posterior

Se ejecutó normal con structured-prototype-5, router gratuito y 8192 tokens:
éxito en **24,000 s**, dos llamadas de detección. La primera devolvió JSON
inválido y fue rechazada; el reintento pasó. Clasificación y narrativa tuvieron
eventos local_stage y pasaron sus guardas sin llamadas al proveedor. El informe
contiene cero hallazgos, resumen de Python y aviso de alcance limitado.

Se verificaron puntero, manifiesto y hashes JSON/Markdown, tres guardas aceptadas,
narrative_source=python_scope y structured-report-2. Evidencia:
`.local-state/a05-evaluation/20261007T110746967458Z/evaluation.json`.
Comparación derivada sin alterar originales:
`.local-state/a05-evaluation/normal-latency-comparison-20261007.json`.

| Muestra normal | Segundos | Llamadas | Tokens totales informados |
| --- | ---: | ---: | ---: |
| Antes, 20261007T103027780944Z | 475,829 | 4 | 34555 |
| Después, 20261007T110746967458Z | 24,000 | 2 | 7443 |

El digest de entrada coincide. La prueba posterior informa 1497 tokens de
razonamiento y el cero SDK sigue separado como discrepancia. Las dos llamadas
informaron liquid/lfm-2.5-2.6b:free y apodex/apodex-1.1-mini:free. Los modelos
del ensayo anterior eran otros: una comparación de muestras no aísla la
influencia del router ni acredita un p95 o una reducción garantizada del tiempo.
Sí acredita que el recorrido real no hizo llamadas de clasificación/narrativa.
No se repitió tras el éxito ni hubo notificaciones o activación.

## Alineación de la entrada estructurada

La revisión posterior detectó que main.py no pasaba los límites que sí usaba
el evaluador. STRUCTURED_MAX_TOKENS=8192 y STRUCTURED_REQUEST_TIMEOUT_SECONDS=60
ahora tienen una fuente común en structured_engine. main.py los pasa únicamente
en el modo structured; get_llm_con_retry conserva la firma compatible sin
argumentos y omite ambos parámetros en la ruta legacy. Se mantuvieron candidatos,
proveedor, URL y reintentos configurados. No se modificó .env ni se reinició nada.

La construcción real de ambos adaptadores OpenRouter (legacy y structured) se
verificó en .p2 y .venv con CrewAI/LiteLLM y claves sintéticas, red prohibida,
sin call/kickoff. Esto no elimina las cuatro diferencias de dependencias
documentadas para .venv ni acredita su migración.
Los tests AST comprueban enrutamiento de main y argumentos de las fábricas.
La prueba real anterior **no** arrancó main.py, el coordinador o transportes:
el worker tiene plazo externo de 900 s, frente a 600 s y seis llamadas lógicas
máximas del evaluador. No presentar esa construcción offline como integración
real del ejecutor ni igualdad de presupuestos de reintento. timeout=60 tampoco
promete una cota global de petición: el lote previo acreditó mayor duración;
el plazo externo sigue siendo necesario.

## Problema observado

El caso normal de la evaluación ampliada tardó 475,829 s y consumió cuatro
llamadas: detección, clasificación vacía y dos intentos de narrativa. La salida
final de narrativa fue «1». El formato structured-report-2 ya sustituyó textos
sin hallazgos por un resumen de alcance de Python, pero seguían haciéndose las
llamadas de las dos tareas finales. Datos originales y limitaciones en
[evaluación ampliada](EVALUACION_AMPLIADA_A05_2026_10_07.md).

## Cambio implementado

La revisión structured-prototype-5 conserva tres agentes, tres tareas, contexto
secuencial, contratos, validación y publicación por generaciones. La ruta del
adaptador cambia solo después de que la guarda acepte una detección con
`candidates=[]`:

1. La clasificación vacía se construye localmente y pasa su guarda/Pydantic.
2. La narrativa local reutiliza el mismo resumen de alcance que el publicador;
   requiere clasificación validada y pasa su guarda/Pydantic.
3. Los JSON originales de esas tareas se vuelven a validar antes de publicar.

No se llaman proveedores para esas dos tareas. No se sustituyen errores o
respuestas vacías por cero candidatos; JSON inválido, referencias inválidas,
fallo del proveedor o detección rechazada conservan sus errores y no publican.
La ruta con candidatos conserva las llamadas de clasificación y narrativa.
Los contadores cuentan solo llamadas al delegado, no etapas locales ni supuestas
peticiones HTTP internas. El diagnóstico añade `local_stage`, source=python,
para distinguir esos pasos y mantener la cobertura de metadatos de uso.

El resumen conserva selección, omisiones y registros no interpretables; no
certifica seguridad ni benignidad. Si Python observó indicadores pero el modelo
produjo cero candidatos, señala posibles omisiones para revisión. No inventa
hallazgos ni afirma que el detector siempre encuentre todos los indicadores.

## Evidencia y compatibilidad

- 212 pruebas Python, tres diagnósticos JavaScript; sintaxis de 62 archivos.
- 17 escenarios CrewAI/LiteLLM sin proveedor: un caso normal completa las tres
  tareas con **una** llamada al delegado; ambas etapas locales pasan guardas.
- El escenario con LiteLLM real/completado simulado verifica una llamada de SDK,
  outputs Pydantic de las tres tareas y resumen de uso completo de esa llamada.
- La evidencia no interpretable puede terminar sin candidatos con advertencia
  de incertidumbre y una llamada; no recibe IP/fecha inferidas ni veredicto seguro.
- Los casos positivos y errores mantienen sus llamadas y rechazos previos.
  El informe anterior y los archivos de la evaluación real permanecen intactos.

Las pruebas offline acreditan supresión de llamadas; la medición posterior
acredita una muestra real, no un p95. La detección todavía depende del proveedor
y puede requerir reintentos o alcanzar los límites. No se promete un tiempo
concreto por una sola muestra. Los límites de seis llamadas/600 s del evaluador
y su router gratuito no cambian. API, frontend, prompts legacy, .env y modo
operativo permanecen compatibles. `ANALYSIS_ENGINE_MODE=legacy` es el retorno
y sigue seleccionado por defecto.

## Pendientes

La muestra normal ya se verificó con el proveedor. Revisar la aceptación de
calidad/latencia y la necesidad de comparativa legacy o prueba del ejecutor
antes de activar A-05. La transición de .venv y la excepción braces siguen
separadas; ninguna se cambia en esta optimización.

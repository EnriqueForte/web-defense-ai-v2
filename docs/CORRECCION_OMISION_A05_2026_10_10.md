# A-05 — Rechazo de detección vacía con indicadores, 10/10/2026

Seguimiento: la [evaluación real posterior](EVALUACION_CORRECCION_A05_2026_10_10.md)
terminó con cinco grupos y referencias verificadas. La detección no fue vacía
en ese ensayo; la protección de vacío se acredita offline. A-05 sigue abierta
por narrativa/aceptación, sin habilitar manual ni autorizar otros jobs.
Los pendientes de ensayo real de esta acta describen la entrega previa.

La vía structured preparada **ya rechaza una detección vacía si alguna línea
seleccionada contiene indicadores de Python**. La corrección está implementada y
validada offline. A-05 continúa abierta por validación con proveedor y aceptación
del resultado; el botón manual permanece desactivado.

## Problema y cambio

El [diagnóstico real anterior](DIAGNOSTICO_REAL_A05_2026_10_10.md) publicó cero
hallazgos sobre 30 líneas seleccionadas, 26 con indicadores. Su respuesta cumplía
el esquema JSON y las guardas anteriores: `validate_observed_detection` comprobaba
candidatos presentes, pero no rechazaba la lista vacía. El prompt permitía
`candidates=[]` sin condicionar esa salida a las observaciones.

La nueva guarda en `agents/evidence_preparation.py` devuelve el código interno
`empty_detection_with_observed_indicators` para ese caso. Se aplica durante la
tarea de detección y se vuelve a comprobar en clasificación/composición antes
de publicar. No basta con llamar directamente al publicador para saltarla.

El reintento de guarda existente sigue limitado a **uno**. Si el modelo corrige
su respuesta con candidatos válidos, continúan clasificación/narrativa y sus
guardas. Si devuelve de nuevo una lista vacía, el motor falla sin reemplazar
el puntero actual, sin entrar en las etapas locales de cero hallazgos y sin
publicar otra generación. No se amplían los reintentos ni los límites del LLM.

`agents/analysis_diagnostics.py` admite el nuevo código en su lista segura, de
modo que checkpoint/recibo permiten distinguir el rechazo sin guardar respuesta,
credenciales o mensaje de excepción. El prompt structured explica la condición
de salida vacía y conserva la incertidumbre y los posibles falsos positivos.
Versiones actuales: **observed-access-3 / structured-prototype-6**.

Las muestras seleccionadas sin indicadores siguen pudiendo producir cero
hallazgos y resolver clasificación/narrativa localmente, con advertencias de
alcance y registros incompletos. Un indicador puede clasificarse expresamente
como posible falso positivo con severidad baja o desconocida, o quedar por
investigar. La guarda no genera candidatos, severidades, IP o éxito de ataque.

## Evidencia de validación

- **261 pruebas Python y tres comprobaciones JS**, aprobadas en `.p3`, `.p2` y
  `.venv`, sin modificar sus paquetes. Cero expectedFailure.
- **20 escenarios CrewAI/LiteLLM offline** en `.p3`, con conexiones de red
  prohibidas y completados simulados. Nuevos recorridos: vacío rechazado y
  corregido dentro del único reintento (cuatro llamadas simuladas para las tres
  etapas); dos respuestas vacías con SDK real/transportes simulados producen
  recibo failed, dos llamadas/intentos, dos códigos de rechazo y puntero intacto.
- Pruebas de rechazo para SQLi, XSS, rutas, comandos y ráfaga de fuerza bruta;
  publicación anterior conservada sin añadir una generación rechazada;
  clasificación explícita de falso positivo aún válida; indicadores fuera de
  la ventana seleccionada no fuerzan candidatos; informes históricos vacíos
  conservan su advertencia al renderizarse.
- **70 archivos de sintaxis** sin errores y `git diff --check` aprobado.
- Comprobación de conservación: ningún job nuevo ni activo, mismos 25 trabajos
  y entregas; filas históricas, archivos previos, generación actual y metadatos
  de `.env` intactos respecto a la operación real anterior.

La primera suite dentro del aislamiento encontró WinError 5 en reemplazos
atómicos de temporales; la repetición fuera del aislamiento pasó íntegramente.
El primer ensayo SDK aislado se interrumpió sin resultado concluyente; el ensayo
completo fuera del aislamiento pasó los 20 escenarios, manteniendo la red
bloqueada por el script. No se presentan esos intentos iniciales como aprobados.

Recibos locales en `.local-state/a05-real-20261010/`: logs
`baseline-guard-p3-outside.txt`, `baseline-guard-p2-outside.txt`,
`baseline-guard-venv-outside.txt` y `guard-preservation.json`.
`scripts/check_structured_prototype.py` permite repetir los 20 escenarios sin
proveedor y publica exclusivamente en directorios temporales.

## Compatibilidad, límites y operación

El cambio afecta al flujo structured con preparación observada. No cambia el
contrato genérico que carece de esas observaciones, el motor legacy, API, UI,
selección, patrones Python, modelos o configuración persistente. Los informes y
recibos existentes siguen siendo datos inmutables; **el informe actual de cero
hallazgos no se reescribió ni se cambió el puntero para esconderlo**.

La guarda impide el caso de cero candidatos frente a indicadores seleccionados.
No acredita cobertura total de todos los patrones ni evita cualquier omisión
parcial de una lista no vacía; tampoco demuestra calidad semántica de cada razón
o clasificación. Si un patrón es falso positivo, debe aparecer en una evaluación
explícita en vez de desaparecer en una respuesta vacía. Fuera de la selección
continúan los límites y advertencias documentados.

No se reiniciaron servicios ni se ejecutaron motor real, Docker o notificaciones.
La autorización anterior cubría un único job y ya se utilizó. Una nueva evaluación
real requiere otro alcance expreso: se puede proponer un job sobre la misma copia,
OpenRouter gratuito, sin sincronizar Docker, envíos o repetición automática del
trabajo. Debe revisar recibos, guardas, evidencia y contenido; éxito técnico no
basta para aceptar la calidad.

Un futuro hijo `main.py` carga las nuevas guardas/prompts al iniciarse. No se
afirma que el proceso coordinador o Flask ya activos hayan recargado sus módulos.
No se requiere arrancar otro worker rutinariamente para esta entrega de fuentes.
El botón manual seguirá apagado durante la evaluación controlada; su habilitación
será una operación posterior con perfil explícito, identities/locks/trabajos
verificados y `--enable-manual` en Flask. El worker podrá conservar manual-only
y destinos vacíos. A-05 y los pendientes de instalación/dependencias siguen abiertos.

Para retirar esta corrección, revertir únicamente la guarda, su código seguro y
las versiones/instrucciones de prompt añadidas en esta entrega, conservando los
cambios anteriores. No restaurar bases o informes por un cambio de fuentes ni
usar `git reset` global. No hubo commit, push o publicación.

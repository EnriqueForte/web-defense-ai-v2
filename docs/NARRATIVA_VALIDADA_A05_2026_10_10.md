# A-05 — Narrativa de hechos y medidas revisadas, 10/10/2026

Seguimiento 11/10: el usuario aceptó la vista previa y la
[admisión manual se habilitó](ACTIVACION_MANUAL_A05_2026_10_11.md) sin ejecutar un
análisis o reescribir este informe. Los estados de manual apagado y aceptación
pendiente de abajo corresponden a esta entrega offline previa.

La publicación structured prepara ahora **un resumen en español desde los
hallazgos validados y medidas concretas desde un catálogo revisado**. Una
narrativa del modelo que cumpla JSON pero invente `SUBSTRING` o repita observaciones
como recomendaciones ya no introduce esos textos en la publicación nueva.
La corrección y su vista previa están aprobadas offline; no se ha ejecutado otro
análisis ni se ha cambiado el informe vigente o habilitado manual.

## Cambio y garantías

`agents/structured_reporting.py` valida primero la clasificación observada y el
contrato narrativo original. Para resultados con hallazgos, la narrativa publicada
se compone desde familias, severidades, estados, conteos y alcance ya validados.
No usa motivos del modelo, targets crudos o funciones SQL inferidas. Para muestras
sin hallazgos sigue el resumen de alcance existente, sujeto a la guarda que
rechaza detección vacía con indicadores seleccionados.

Cada candidato recibe una recomendación propia de su patrón, con el mismo
candidate_id validado. Incluye correlación con eventos de aplicación y medidas
concretas que requieren revisión humana. Los posibles falsos positivos mantienen
su estado/severidad y exigen verificar contexto antes de cambiar controles. La
evidencia incompleta `other` recibe acciones de comprobación de registros, sin
inventar una mitigación de un ataque desconocido.

Si una lista no vacía omite pares de indicador–evidencia seleccionados, el resumen
cuenta esas referencias sin representar y advierte de posibles omisiones. No se
añaden candidatos para rellenar la cobertura. El resumen conserva seleccionadas,
total y omitidas; no convierte una selección parcial en un diagnóstico completo.

Se mantienen **las tres tareas CrewAI y sus guardas**. La tarea narrativa sigue
llamando al LLM cuando hay hallazgos y ahora pide español, acciones y hechos del
contexto. Se valida su contrato antes de sustituir el texto en la publicación:
JSON inválido, referencias ajenas o Unicode inválido siguen impidiendo publicar.
No se reparan errores silenciosamente ni se afirma ahorro de llamadas. Los límites,
modelos, reintentos y prompts legacy no cambiaron.

Versiones: **structured-prototype-7 / structured-report-4 / grounded-narrative-1**.
Resultados nuevos con hallazgos indican `narrative_source=python_validated_facts`;
sin hallazgos conservan `python_scope`. El campo de calidad global sigue siendo
`semantic_evaluation_pending`: la clasificación/detección del modelo y sus
motivos no adquieren garantías semánticas generales por esta narrativa.

## Catálogo y fuentes

Las medidas son orientaciones de revisión por patrón, sin afirmar que ya se hayan
aplicado ni que exista una vulnerabilidad explotada:

- SQLi: revisar consultas y parametrizar valores en lugar de concatenar entradas.
  [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html).
- XSS: codificación de salida según contexto; sanitización si la aplicación acepta
  HTML. [OWASP Cross Site Scripting Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html).
- Rutas: identificadores permitidos y confinamiento de rutas resueltas.
  [OWASP Path Traversal](https://community.owasp.org/attacks/Path_Traversal).
- Comandos: preferir APIs, separar comando/argumentos y validar entradas permitidas.
  [OWASP OS Command Injection Defense](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html).
- Fuerza bruta: revisión por cuenta, limitación de intentos y valoración de MFA,
  evitando bloqueos indiscriminados.
  [OWASP Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html).
- Otra evidencia: revisar formato, fecha, petición y correlación antes de elegir
  medidas específicas. Es una política local de triage, no un ataque confirmado.

Fuentes primarias consultadas el 10/10/2026. No se seleccionan bibliotecas concretas,
se ejecutan medidas o se instalan controles mediante estas recomendaciones.

## Validación y vista previa

**268 pruebas Python y tres comprobaciones JS** en `.p3`, `.p2` y `.venv`; cero
expectedFailure. La versión final del ajuste gramatical se volvió a comprobar
en `.p3`. **21 escenarios CrewAI/LiteLLM offline** en `.p3`, con conexiones
prohibidas, y **71 archivos de sintaxis** sin errores. `git diff --check` aprobado.
La primera suite dentro del aislamiento falló en reemplazos atómicos de temporales
con WinError 5; la repetición fuera del aislamiento pasó con dobles de proveedor,
Docker y notificaciones. No se modifica el producto para eludir ese aislamiento.

La cobertura nueva comprueba:

- Narrativa inventada pero contractualmente válida no aparece en el resumen o
  recomendaciones publicados; cambia el texto/motivos libres y la narrativa final
  permanece igual si se conservan los hechos validados.
- Medidas concretas para los seis patrones, referencias válidas y falsos positivos
  con cautela antes de cambiar controles.
- Alcance/omisiones parciales conservados, sin inventar hallazgos adicionales.
- Contrato original inválido impide publicación y conserva el puntero.
- Renderer no reconstruye ni reescribe narrativas de informes históricos.
- CrewAI realiza sus tres llamadas en el recorrido positivo simulado, con las
  tres salidas Pydantic y la narrativa final de fuente Python revisada.

La vista previa en `.local-state/a05-narrative-20261010/VISTA_PREVIA_NARRATIVA.md`
recompone offline los hallazgos almacenados del job
`4b37542ec9f6494d9982e4591ac8529e`, tras verificar la generación y sus hashes.
Se mantienen exactamente los cinco hallazgos, referencias, estados, cuatro altos
y un medio, 30 líneas seleccionadas de 112 y 82 omitidas. Se elimina el detalle
no soportado y las medidas están en español. **No es otro job ni una publicación
del proveedor**: modelo etiquetado offline-preview y metadatos de proyección separados.
No se guardó una segunda copia de las líneas crudas en ese artefacto de vista previa.

El informe actual del dashboard conserva su Markdown/JSON originales, incluida
la narrativa anterior, y sus recibos no se alteraron. La vista previa no acredita
que los servicios activos hayan recargado módulos. Un futuro hijo `main.py`
cargará las fuentes nuevas; los resultados existentes siguen siendo inmutables.

Recibos locales: `baseline-p3-final.txt`, `baseline-p2.txt`, `baseline-venv.txt`,
`preview-metadata.json` y `guard-preservation.json`, en la misma carpeta.

## Estado y siguiente operación

Se conservan 26 trabajos, cero queued/running, filas históricas/entregas, archivos
previos y generación actual. `.env` mantiene tamaño/mtime, comprobados sin leer
sus bytes. No hubo reinicios, jobs, llamadas LLM, Docker, envíos, commit o push.
Manual permanece desactivado y A-05 abierta por revisión/aceptación del resultado
y validación operativa final según el alcance que se autorice.

La vista previa permite revisar esta corrección antes de consumir API o cambiar
admisión. Habilitar el botón requiere una operación explícita de Flask con
`--enable-manual`, preflight y comprobación de identidades/locks/trabajos. No
encola nada por sí solo; el worker puede seguir manual-only y sin notificaciones.
La ingesta configurada del botón continúa siendo la del perfil; esta entrega
no probó Docker ni la ingesta del laboratorio. Las autorizaciones de los jobs
anteriores ya se utilizaron; no son saldo para otros análisis.

Para retirar esta entrega, revertir solo la construcción de narrativa/catálogo,
las versiones/instrucciones narrativas y sus pruebas añadidas, conservando las
guardas de detección y demás cambios anteriores. No restaurar bases o publicaciones
por un cambio de fuentes ni usar `git reset` global. La vista previa y recibos son
artefactos locales excluidos de Git.

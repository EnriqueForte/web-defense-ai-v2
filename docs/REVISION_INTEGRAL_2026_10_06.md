# Revisión integral de web-defense-ai V2

Seguimiento posterior a la revisión: el 06/10/2026 se completó la
[entrega 1 de seguridad y línea base](ENTREGA_1_SEGURIDAD_LINEA_BASE.md).
R-01/R-02/R-09, la regresión OpenAPI y el alcance de lint están corregidos;
R-15 dispone de cobertura backend/factory y conserva pendientes de frontend.
La suite pasa con 111 pruebas Python. El cuerpo de este documento conserva
el diagnóstico inicial y sus resultados, no describe todos los hallazgos
como si siguieran sin corregir. Consultar el registro de entrega para límites
y aceptación; las siguientes entregas permanecen pendientes.

La [entrega 2](ENTREGA_2_DEPENDENCIAS_EJECUCION.md) corrige los dos avisos de
producción de R-03, declara/valida offline LiteLLM (R-04), acota notificaciones
(R-08) y añade instalación limpia y contrato verificable para dependencias de
R-16. Braces de desarrollo y transición de la `.venv` siguen pendientes;
la versión 3.0.4 de braces indicada por el audit inicial no está publicada.
La suite actual pasa con 125 pruebas. La tabla inicial de avisos y sus
versiones sugeridas se conserva como evidencia histórica, no como instrucciones
de instalación vigentes.

Fecha: 06/10/2026. Referencia inicial: `b6c4818`. Árbol Git limpio al comenzar.

## Dictamen

Seguimiento de entrega 6: [integración A-05](ENTREGA_6_INTEGRACION_EVALUACION.md)
implementada bajo conmutador predeterminado `legacy`, validada con 179 pruebas
y seis escenarios CrewAI simulados. El intento real sintético autorizado con
OpenRouter gratuito falló por autenticación sin publicar informe. A-05 no se
cierra ni activa; evaluación de calidad/latencia/consumo y aceptación pendientes.
Los defectos de la ruta legacy siguen vigentes mientras permanezca seleccionada.

Seguimiento de entrega 5: [A-03/A-04](ENTREGA_5_PREPARACION_PUBLICACION.md)
completadas como componentes aislados, con 167 pruebas y cinco escenarios
CrewAI simulados. No se integra ni activa todavía el nuevo motor; R-05/R-06/R-07
y demás límites de la ruta antigua siguen pendientes en operación. A-05 queda
para evaluación e integración reales con alcance explícito.

Seguimiento de entrega 4: [A-01/A-02](ENTREGA_4_CONTRATOS_PROTOTIPO.md)
completadas aisladamente con contratos, adaptador histórico y ensayo CrewAI
real/doble LLM. No se activa el motor nuevo ni se corrigen por ello los defectos
del flujo operativo. Suite actual: 149 pruebas. A-03–A-05 siguen pendientes.

Seguimiento de entrega 3: F7-01 cerrada localmente el 06/10 con confirmación
de uso, retorno real sobre fixture y respaldo/restauración de 47 archivos,
incluido SQLite piloto. [Registro](ENTREGA_3_OPERACION_CIERRE_LOCAL.md).
R-19 incorpora respaldo de la aplicación; volúmenes/buzón de laboratorio
siguen fuera de cobertura. La evaluación inicial de fases abiertas y datos
sin respaldo se conserva abajo como diagnóstico previo a las entregas.

El proyecto dispone de una base funcional de laboratorio local: motor Python/CrewAI, coordinador persistente, API Flask y consola Next.js. La migración y el rediseño han mejorado sustancialmente la presentación, la lectura segura y la exclusión entre ejecuciones. No hace falta rehacer la arquitectura ni añadir agentes para continuar.

Sin embargo, hay defectos actuales de seguridad, reproducibilidad y validación del resultado que deben corregirse antes de ampliar funciones. El principal límite de calidad está en el motor: la tabla Markdown generada por el LLM sigue siendo la fuente de clasificación y métricas, sin contrato de evidencia validado. Una ejecución terminada no equivale a una detección correcta.

La fase 7 de migración continúa abierta. Las mejoras A-01–A-05 siguen pendientes. El rediseño SOC figura cerrado hasta UI 8 en su acta, incluido el zoom real al 200 % confirmado por el usuario; README y AGENTS conservan un estado anterior.

Esta revisión identifica pendientes; no inicia ni autoriza su implementación.

## Alcance y límites de la revisión

Se inspeccionaron motor, preprocesamiento, prompts, coordinador, SQLite, bloqueos, API y parsing, frontend, estilos y componentes, notificaciones, contratos, dependencias, Compose, scripts de laboratorio y recuperación, tareas locales, pruebas y documentación de fases.

Se ejecutaron comprobaciones estáticas, suite aislada, compilación de una copia del frontend, auditoría npm y sondas con archivos temporales e I/O simulado. No se ejecutaron `main.py`, el ejecutor real, Docker ni notificaciones reales. No se inspeccionó el contenido de `.env`, logs o reportes operativos ni se volcaron secretos. Las sondas bloquearon la carga dotenv durante importaciones y utilizaron claves ficticias.

Los resultados históricos de integración se tomaron de las actas y de las confirmaciones allí registradas. No se repitieron integración LLM, pruebas visuales en navegador, zoom, rendimiento bajo carga, observación prolongada ni instalación limpia. La auditoría npm no sustituye una auditoría de dependencias Python o de imágenes Docker, que no se ha realizado en esta entrega.

No se modificó código de producto, prompts, contratos, dependencias, configuración local ni datos operativos. El único archivo versionable añadido es este informe. Las sondas y la copia compilada permanecen bajo `.local-state/review-20261006/`, excluido de Git. No se realizó commit ni publicación.

## Evidencia de verificación actual

| Comprobación | Resultado del 06/10/2026 | Interpretación |
|---|---|---|
| Sintaxis Python | 31 archivos, 0 errores | No importa ni ejecuta el motor |
| Suite Python | 88 pruebas: 87 aprobadas y 1 fallo; 0 expected failures | La regresión global está roja |
| Diagnósticos JavaScript del Flask anterior | 3 aprobados | Cubre los casos definidos de logs, Markdown y refresco |
| ESLint de todo el frontend | Aprobado | Se invocó sin limitar a `src/app` |
| TypeScript `--noEmit` | Aprobado | Tipado estático; no valida payloads reales |
| Regresión de componentes React | 6 grupos aprobados | Render estático, sin efectos ni interacciones completas |
| Build Next.js 16.3.6 | Aprobado en copia aislada | Compilación y generación estática con TypeScript |
| `pip check` | Sin requisitos incompatibles declarados entre paquetes instalados | No demuestra coincidencia con el fichero de requisitos |
| Pines Python frente a instalación | 148 pines comprobados, 4 discrepancias, ninguno ausente | Entorno instalado y contrato no son idénticos |
| `pnpm audit --prod --json` | 2 avisos altos, 0 críticos | Dependencias marcadas de producción |
| `pnpm audit --json` | 3 avisos altos, 0 críticos | Incluye un aviso adicional de desarrollo |

La suite falla en `tests/test_baseline.py:471`: la enumeración exacta de rutas no incluye `/configuracion/llm`, que sí está publicada en OpenAPI. No se ha ocultado ni actualizado la prueba en esta revisión.

Había un lock de desarrollo en `.next/dev/lock`. Para preservar la salida existente, se copiaron fuentes y configuración a `.local-state`, enlazando las dependencias instaladas. El primer intento de build rechazó el enlace por quedar fuera de la raíz de Turbopack; se corrigió únicamente la raíz en la configuración de la copia y la compilación terminó correctamente. Ese fallo inicial pertenece al montaje de revisión, no constituye un defecto demostrado del build habitual del proyecto. No se compiló sobre la `.next` original ni se arrancó otro dashboard.

## Arquitectura que conviene conservar

| Capa | Estado observado | Evaluación |
|---|---|---|
| Ingestión | Copia atómica y captura local de stdout de DVWA | Conserva la fuente anterior si falla la captura de laboratorio |
| Preprocesamiento | Reglas Python y muestra de logs | Necesita normalización, alcance explícito y agregados verificables |
| Agentes de producto | Analista, detective y reporter secuenciales | Tres agentes son suficientes; las operaciones deterministas deben seguir en Python |
| Coordinación | SQLite, índice único de trabajo activo, idempotencia, bloqueos y heartbeat | Base adecuada para un equipo y volumen local |
| Publicación | Reemplazo atómico del Markdown actual y copia histórica posterior | Protege frente a archivos parciales; falta validación y coherencia de la publicación completa |
| API | `/api/v1`, filtros, paginación, identificadores y rutas locales | Mantener contratos durante mejoras del motor |
| Frontend | Next.js/React/TypeScript con proxy a loopback | Buena separación de Docker, archivos y credenciales del motor |
| Retorno | Dashboard Flask y conmutador reversible | Debe mantenerse durante el cierre de fase 7 |

Los campos del modelo en React se muestran como texto y las pruebas actuales verifican el escapado de cargas hostiles. Los enlaces externos de autoría son fijos. La configuración LLM no devuelve claves, restringe proveedor y origen y comparte bloqueos con el análisis. Los escritores atómicos, la idempotencia y la recuperación de entregas ambiguas son mejoras reales que no conviene perder.

## Hallazgos prioritarios

P1: corregir en la siguiente entrega antes de ampliar alcance. P2: corregir en la estabilización o evolución correspondiente. P3: mantenimiento o mejora condicionada al uso. Estas prioridades son de desarrollo; no son puntuaciones CVSS.

### R-01 — P1 — HTML reflejado en una respuesta de error de Flask

Evidencia: `dashboard/app.py:865`. Cuando un nombre no pasa la expresión regular, se concatena directamente en una respuesta de texto que Flask sirve como `text/html`.

Una solicitud local de prueba a `/report/` con un nombre codificado que contiene `<img src=x onerror=alert(1)>` recibió HTTP 400 y devolvió la etiqueta intacta. Se confirmó la respuesta vulnerable con el cliente de pruebas; no se ejecutó el JavaScript en un navegador.

El escapado de reportes válidos no protege este camino de error. Un enlace construido para esa ruta puede introducir contenido ejecutable en el origen del dashboard local.

Corrección: mensaje constante, respuesta explícita de texto plano o escapado seguro; añadir regresión para nombres hostiles. Revisar las demás respuestas HTML de error sin alterar el contrato de reportes válidos.

### R-02 — P1 — La sincronización anterior carece de comprobación de origen

Evidencia: `dashboard/app.py:832`. La ruta `/api/sincronizar` comprueba ejecución coordinada y adquiere el bloqueo, pero no valida Origin ni dispone de otra defensa CSRF.

Con ejecutor simulado como detenido, una petición POST con `Origin: https://untrusted.example` devolvió 200 e invocó la copia Docker simulada. No se contactó Docker. La ausencia de CORS no impide que un POST simple alcance la acción; las restricciones concretas del navegador pueden afectar a un ataque real, que no se ha ensayado aquí.

Corrección: aplicar una política de origen explícita a todas las mutaciones locales, documentando el tratamiento de herramientas sin Origin. Conservar bloqueo y ausencia de ejecución IA en esta ruta.

La política de `/analisis` también debe armonizarse: admite Origin ausente y solo los orígenes `127.0.0.1`, mientras configuración LLM exige Origin y admite además `localhost`. El análisis exige Idempotency-Key, por lo que no se atribuye automáticamente a esa ruta la misma reproducción CSRF.

### R-03 — P1 — Dependencias transitivas con avisos altos actuales

Los dos comandos de auditoría terminaron con código 1 por avisos, tras una consulta de red autorizada. El resultado actual difiere del acta del 01/10, que registró un audit limpio; aquel resultado era histórico.

| Paquete en el lockfile | Dependencia | Ámbito según auditoría | Versión corregida indicada por el aviso |
|---|---|---|---|
| `source-map-js` 1.2.1 | Next/PostCSS y también herramientas Tailwind | Producción y desarrollo | 1.2.2 o superior |
| `sharp` 0.35.4 | Next.js, opcional | Producción | 0.35.5 o superior |
| `braces` 3.0.3 | ESLint Next → fast-glob → micromatch | Desarrollo | 3.0.4 o superior |

Las fichas describen denegación de servicio en [source-map-js](https://github.com/advisories/GHSA-68fv-2mgg-jv7q) y [braces](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm). El aviso de [sharp/librsvg](https://github.com/advisories/GHSA-wq5f-xc86-pv6w) describe condiciones específicas en Linux con glibc. No se ha demostrado explotación de esos caminos en esta app Windows/local ni recepción de mapas de fuentes o imágenes SVG hostiles por la funcionalidad actual.

Corrección: resolver versiones transitivas mediante actualización compatible o overrides justificados, comprobar lockfile y repetir audit/lint/tipos/componentes/build. No actualizar indiscriminadamente todo el stack ni instalar una corrección sin comprobar compatibilidad.

### R-04 — P1 — OpenRouter depende de un extra Python no declarado

Evidencia: `main.py:84`, `requirements.txt:20` y metadatos locales de CrewAI. OpenRouter fuerza `is_litellm=True`. El entorno tiene LiteLLM 1.83.0, pero ni requisitos ni constraints lo declaran. CrewAI 1.14.2 declara LiteLLM como dependencia del extra `litellm`, no de su instalación base.

La integración exitosa confirmada por el usuario demuestra funcionamiento del entorno actual. No demuestra que una instalación nueva de los requisitos incluya el adaptador usado.

Corrección: declarar el extra o la dependencia compatible y fijar una estrategia reproducible; verificar instalación en entorno aislado y construcción del adaptador con dobles, sin llamar al proveedor. No deshacer la corrección OpenRouter que ya permitió dos análisis exitosos.

### R-05 — P1 — Un reporte inválido puede quedar publicado como exitoso

Evidencia: `main.py:240` y `pipeline.py:117`. El motor solo exige texto no vacío. El coordinador comprueba que existe un archivo nuevo, pero no valida secciones, tabla, campos, referencias ni coherencia de cifras.

Una sonda con motor simulado escribió `Respuesta incompleta sin tabla ni contrato`. El trabajo terminó `succeeded`. La prueba utilizó archivos temporales y no ejecutó CrewAI. Esto puede presentar cero amenazas aunque la respuesta esté incompleta, e impedir alertas por falta de filas reconocidas.

Corrección: validar antes de reemplazar el reporte actual, distinguir resultado válido sin amenazas de respuesta inválida y preservar el último reporte válido. Esta corrección debe evolucionar hacia A-01/A-04; una comprobación mínima inicial no debe convertirse en otro parser frágil.

### R-06 — P1 — Criterios del motor confunden observación con confirmación

Evidencia: `config/prompts.py:20`, `:37`, `:45` y `:60`. Las instrucciones asocian POST a una ruta de ejecución con ejecución en servidor, y usan estado HTTP o redirección como señales demasiado concluyentes. El access.log no garantiza contenido del cuerpo POST, datos devueltos ni éxito de explotación.

La interfaz advierte correctamente que las coincidencias no prueban éxito, pero no corrige una clasificación inventada por el motor. No se afirma que una salida concreta actual haya cometido esa atribución: el defecto está en los criterios inspeccionados.

Corrección: en A-03, separar patrón observado, intento probable y éxito confirmado, exigir referencias y conservar incertidumbre. Evaluar precisión y cobertura con el dataset, sin modificar a la vez la UI.

### R-07 — P1 — El modelo puede perder ataques que el prefiltro reconoce

Evidencia: `agents/log_analyst.py:196`, `:207` y `:227`. Hay dos catálogos de patrones diferentes. El prefiltro reconoce `onerror=`, pero la selección balanceada de XSS se limita a `<script`, `%3cscript` y `alert(`. Si hay otra línea seleccionada, no se usa el fallback de líneas completas.

En una fixture con SQLi y XSS mediante `onerror=confirm(1)`, las estadísticas contaron dos líneas sospechosas, pero el texto enviado omitió la XSS.

Además, solo se considera la cola de 100 líneas; se envían todas las críticas de esa cola y hasta cinco altas y cinco de fuerza bruta. `MAX_LINEAS=30` no constituye un límite global de esa selección. Tampoco hay límite por bytes/tokens o longitud de línea.

Corrección: catálogo común, selección con presupuesto explícito, ventana/omisión declaradas y pruebas de cobertura por categoría. La frase “TODAS las líneas” del analista debe referirse al alcance efectivamente entregado.

### R-08 — P1 — SMTP puede mantener indefinidamente un trabajo activo

Evidencia: `config/notifications.py:49` y llamada síncrona desde `pipeline.py:127`. El constructor SMTP no recibe timeout. La sonda con transporte simulado confirmó la ausencia de ese argumento.

El timeout de 900 segundos del subprocess del motor no cubre las notificaciones posteriores. Una conexión o intercambio SMTP bloqueado puede conservar el trabajo, el bloqueo de ciclo y un heartbeat saludable, impidiendo nuevos análisis y guardado LLM.

Corrección: timeouts finitos y presupuesto para la etapa de notificación, estado de entrega consistente y recuperación sin reenvíos ambiguos. No se ha observado una conexión bloqueada real.

### R-09 — P1 — Los errores de Telegram no redactan el token

Evidencia: `config/notifications.py:17` y `:27`. El token forma parte de la URL y se imprime directamente la excepción de requests.

Una excepción de transporte simulada con una URL y token ficticio imprimió ese token. Se demuestra ausencia de redacción; no una filtración observada de credenciales reales. La redacción de diagnósticos del motor no cubre este módulo.

Corrección: diagnósticos por categoría/código con redacción centralizada. Añadir regresión para URL y errores de transporte usando tokens sintéticos.

## Hallazgos de estabilización y calidad

### R-10 — P2 — Contratos de prompt contradictorios

`PROMPT_REPORTER` exige cinco columnas (`config/prompts.py:71`); su tarea exige seis con fecha del evento (`agents/report_generator.py:47`). El detective no enumera Command Injection en su lista explícita de categorías aunque el prompt lo trata como central. El umbral Python es cinco intentos, mientras los criterios textuales alternan “más de 5”, “menos de 5” y “10+”.

Corrección: fuente común de tipos, severidades, estados, umbrales y columnas; cambios de prompts con pruebas comparativas, no retoques aislados sin línea base.

### R-11 — P2 — No hay trazabilidad de evidencia validada ni defensa suficiente ante instrucciones dentro del log

Las tareas no utilizan salida estructurada ni validación determinista de referencias. `main.py:144` interpola el log directamente en la descripción y las instrucciones actuales no establecen claramente que las órdenes contenidas en el tráfico son datos. Los agentes no tienen herramientas de actuación, lo que limita el impacto, pero la clasificación y la narrativa pueden contaminarse.

Los identificadores de amenaza actuales referencian filas del reporte, no una identidad estable de evidencia original. Un esquema debe verificar que IP, fecha y líneas citadas existen en la captura; un prompt por sí solo no garantiza esa integridad.

Esto corresponde a A-01/A-02 y su evaluación posterior A-05. No requiere crear un cuarto agente.

### R-12 — P2 — El parser acepta degradaciones silenciosas

`dashboard/app.py:74` depende del heading de amenazas, separadores `|`, nombres de cabecera y formato textual. Cabeceras Markdown válidas con `**Severidad**` y `**Tipo de Ataque**` produjeron una fila con severidad y tipo `-` en una sonda.

No hay validación semántica de filas ni vínculo con el log original. Los conteos del dashboard y de alertas se derivan de esa interpretación. Una fecha parseable representa un campo explícito del reporte, no una comprobación de que el evento realmente exista en la fuente.

Corrección: adaptador histórico que indique degradación y fuente estructurada nueva. A-04 debe construir tabla y conteos determinísticamente desde la clasificación validada.

### R-13 — P2 — Detector de ráfagas elimina la zona horaria

`agents/log_analyst.py:158` descarta el offset antes de calcular intervalos. El comentario que dice que el offset no cambia intervalos solo es válido si todos son iguales. Cinco peticiones con horas de pared cercanas y offsets alternos `+0000`/`+0900` se detectaron como una ráfaga aunque los instantes estuvieran separados por horas.

Además, el detector retorna solo el primer grupo de umbral por IP y su resultado llega a estadísticas como booleano; el LLM no recibe conteos ni ventana completos.

Corrección: timestamps conscientes de zona y agregados estructurados con evidencias, para A-01/A-03. Considerar también cambios de horario y fuentes combinadas.

### R-14 — P2 — Identidad de publicación y refresco pueden divergir

`dashboard/app.py:400` calcula snapshot por contenido de reporte/log y referencias históricas, mientras `CapturedFile.file_id` depende también de metadatos. Una republicación atómica del mismo texto produjo snapshot idéntico y report_id distinto en la sonda.

La página refresca amenazas y catálogo principalmente por `snapshotId` (`frontend/src/app/page.tsx:198` y `:228`). Si el log y los históricos visibles también siguen iguales, puede conservar IDs de la publicación anterior. El resumen nuevo puede referenciar otro report_id y un detalle seleccionado puede quedar obsoleto.

Corrección: decidir identidad por contenido frente a publicación de forma coherente, y refrescar listas por la identidad pertinente. Añadir prueba del mismo resultado publicado dos veces y de actualizaciones concurrentes.

Las capturas son estables por archivo; no son una transacción común entre log, reporte, archivo histórico y SQLite. La sustitución del reporte sucede antes de archivado/notificación/finalización del trabajo: un fallo posterior puede dejar un reporte nuevo con trabajo fallido. Esa situación debe representarse con precisión en A-04.

### R-15 — P2 — Falta cobertura de la nueva configuración LLM

El fallo OpenAPI está en `tests/test_baseline.py:471`. Las cuatro pruebas de `test_model_config.py` cubren selección/fallback de modelos, pero no cubren la ruta nueva, OpenRouter ni el guardado del `.env` administrado. La regresión React no incluye `LLMSettings`, `page.tsx` ni efectos de polling.

Añadir pruebas aisladas de GET sin secretos, validación de proveedor/modelo, clave ficticia, Origin, formato JSON, 409 por bloqueo, reemplazo atómico fallido, conservación de líneas ajenas y claves anteriores, precedencia frente al entorno heredado del worker y construcción del adaptador OpenRouter. Todos los archivos de configuración de prueba deben ser temporales.

La fixture `tests/serve_phase4_fixture.py` bloquea `load_dotenv` al importar Flask, pero las nuevas rutas llaman a `public_llm_settings`, cuyo resolver vuelve a leer `.env` por su propia función. Actualizar sus dobles si se reutiliza para afirmar aislamiento completo de la configuración local.

### R-16 — P2 — Configuración y entorno no son plenamente reproducibles

La comparación de metadatos instalados con requisitos encontró:

| Paquete | Declarado | Instalado |
|---|---|---|
| aiohttp | 3.13.5 | 3.13.3 |
| importlib_metadata | 8.7.1 | 8.5.0 |
| jsonschema | 4.26.0 | 4.23.0 |
| openai | 2.32.0 | 2.24.0 |

`pip check` no detecta este tipo de diferencia. No se deduce que esas cuatro versiones sean incompatibles o vulnerables, pero las comprobaciones actuales no certifican exactamente el entorno declarado.

`MAX_LINEAS_LOG` y `UMBRAL_FUERZA_BRUTA` se anuncian en `.env.example` y se leen en `config/settings.py:22`, pero no gobiernan el preprocesamiento, que conserva constantes y valores por defecto. Los casts de configuración en ese módulo también pueden impedir el arranque ante valores inválidos, a pesar de que el resolver LLM tiene otras defensas.

Corrección: contrato único de configuración con validación y errores comprensibles; reconciliar instalación, requisitos y constraints mediante una instalación limpia aislada, sin alterar a ciegas el entorno operativo.

### R-17 — P2 — Verificación de frontend incompleta desde la tarea local

`.vscode/run-frontend.ps1:42` ejecuta ESLint solo sobre `src/app`. Excluye `src/components`, `src/lib` y otros archivos del proyecto. El script npm `lint` y la comprobación completa realizada hoy tienen más alcance.

Corrección: unificar ambos puntos de entrada. No hay directorio `.github` ni CI versionada observada; la regresión depende de ejecución local. Un comando de verificación común para backend/frontend sería útil antes de decidir automatización CI.

### R-18 — P2/P3 — Robustez del cliente ante respuestas lentas o deformadas

`getApi` comprueba el sobre `meta/data`, y `validState` solo algunos campos. Listas, detalle y configuración se convierten por cast TypeScript. Un sobre con `data` nulo o campos inesperados puede provocar errores al renderizar.

El polling usa `setInterval` sin timeout ni control de una solicitud en vuelo. Una respuesta lenta puede solaparse con otra y llegar después, sustituyendo datos más recientes. Algunos callbacks de listas y el `.then(setDetail)` no comprueban el aborto antes de actualizar estado. Esto se infiere del código; no se ha reproducido una carrera de navegador en esta entrega.

Corrección: validadores de respuesta pequeños o compartidos con el contrato, límites de solicitud y control de orden/aborto. Probar pérdida y recuperación de conexión, latencia elevada y selección rápida de reportes con fixtures.

## Operación, laboratorio y mantenimiento

### R-19 — P2 — Recuperación y conservación de datos incompletas para la operación actual

`scripts/backup_baseline.py` respalda `.log` y `.md` de `logs/` y `reports/`. El piloto y las tareas manuales utilizan `.local-state/phase6-pilot/`, incluida SQLite; ese estado no queda cubierto por el script. Tampoco respalda el volumen DVWA, lo que debe tratarse por separado si se desea conservarlo.

Mailpit no dispone de volumen persistente en `compose.lab.yaml`. La pérdida de tres entregas históricas ya ocurrió al reiniciarlo. Preservar `unknown` es correcto; no deben marcarse como enviadas ni reintentarse sin evidencia.

El worker y los históricos acumulan registros/archivos; la función de limpieza antigua no tiene llamadas observadas. No activar borrado como parte de esta revisión. Definir política de conservación y respaldo coherente con las rutas efectivamente usadas, incluyendo copia consistente de SQLite y ensayo de restauración en destino aislado.

### R-20 — P2/P3 — Dos configuraciones Docker con garantías diferentes

`compose.lab.yaml` publica DVWA/Mailpit solo en loopback, utiliza la red interna para DVWA/DB y limita la rotación del log de DVWA. Ese es el laboratorio validado en fase 6.

El Compose heredado publica `8080:80`, monta el repositorio completo en `ai-engine`, usa imágenes flotantes y conserva otra infraestructura. Sus credenciales de DVWA son valores de laboratorio, no evidencia de secretos del proveedor. Mantenerlo sin una indicación clara puede inducir a iniciar un laboratorio con garantías distintas.

Corrección: identificar el legado de forma explícita, documentar su alcance o revisar sus puertos/montajes en una tarea dedicada. No eliminar contenedores, volúmenes ni modificar automáticamente la configuración heredada.

### R-21 — P3 — Endurecimiento local y autonomía del retorno Flask

Se confirmó con un cliente de pruebas que Flask acepta `Host: untrusted.example` para una lectura. La restricción por remote_addr no valida Host. No se realizó un ataque DNS rebinding: la comprobación demuestra el comportamiento del servidor, no exposición real.

Revisar allowlist de hosts locales y cabeceras de seguridad, con pruebas que conserven el proxy Next y ambos nombres locales. Asegurar también límites razonables de cuerpo para configuración LLM y respuesta JSON consistente en errores internos; actualmente el error handler específico solo maneja HTTPException.

El retorno Flask carga Chart.js/marked desde CDN y fuentes externas sin integridad SRI declarada. La lectura inicial de Markdown permanece escapada, pero gráficos/formato dependen de recursos externos. Valorar servir recursos fijados localmente si el retorno debe funcionar sin Internet. No se atribuye aquí vulnerabilidad conocida a esas versiones, que no fueron auditadas.

### R-22 — P2 — Documentación de estado contradictoria

README y AGENTS anuncian fases UI 1–7 y zoom pendiente; `docs/REDISENO_UI_SOC.md` registra UI 8 cerrada y la confirmación del zoom real. El historial Git también contiene la entrega UI 8.

Las actas de fases anteriores incluyen formulaciones temporales que eran correctas cuando se escribieron. No conviene reescribir la evidencia histórica como si todas las pruebas hubieran ocurrido hoy; sí actualizar el resumen operativo y aclarar supersesiones. También hay descripciones de funciones antiguas que ya no envían alertas desde sincronización.

Corrección: alinear README, AGENTS y tabla de backlog con las actas; conservar fecha, límites y evidencia original. C-04 aparece con interacción gráfica pendiente aunque parte del flujo VSCode ya fue comprobado: aclarar qué interacción concreta queda, sin convertir la configuración del editor en requisito del desarrollo.

## Estado real de fases

| Línea de trabajo | Estado | Qué falta |
|---|---|---|
| Migración fase 0 | Cerrada | Mantener línea base; hoy existe una regresión nueva que corregir |
| Migración fases 1–4 | Cerradas | Conservar correcciones Flask, API y lectura Next |
| Migración fase 5 | Cerrada/implementada, integrada en fase 6 | Estabilización de resultado/notificación indicada en este informe |
| Migración fase 6 | Cerrada anticipadamente por el usuario | Limitaciones históricas: 14 h 11 min 46 s saludables, sin 24 h/resumen automático y tres SMTP unknown; no se reabre automáticamente |
| Migración fase 7 | En curso | Registro de uso, recorridos aceptados, ensayo final de retorno y decisión de cierre/convivencia |
| Rediseño SOC UI 1–8 | Cerrado según acta detallada | Actualizar resúmenes desfasados; no repetir UI 8 o zoom como fases no ejecutadas |
| Configuración LLM | Implementada; OpenRouter con dos éxitos confirmados | Regresión de guardado/adaptador y reproducibilidad del extra |
| A-01 | Pendiente | Contratos de evidencia y resultado, adaptación histórica |
| A-02 | Pendiente, depende de A-01 | Prototipo aislado de salidas estructuradas y contextos |
| A-03 | Pendiente, depende de A-02 y línea base | Selección, instrucciones y criterios atribuibles a evidencia |
| A-04 | Pendiente, depende de A-02 | Separar clasificación, narrativa, tabla y publicación |
| A-05 | Pendiente, depende de A-03/A-04 | Evaluación real de calidad/coste/latencia y activación reversible |

La fase 7 empezó el 01/10/2026. Al 06/10 no han transcurrido siete días de calendario desde ese inicio. El plan presenta siete días de uso como sugerencia, no como cierre automático: pasar la fecha del 08/10 tampoco demostraría uso saludable. Falta evidencia documentada y aceptación del cierre. Flask debe conservarse mientras no se decida expresamente su retirada.

Autenticación, usuarios, permisos, credenciales por usuario, despliegue compartido, TLS operativo, remediación automática y base histórica de incidentes no están implementados ni son fases implícitamente autorizadas. Serían una línea de producto aparte si se amplía el alcance más allá del laboratorio autoalojado local.

## Orden propuesto de desarrollo

| Entrega propuesta | Alcance | Aceptación mínima |
|---|---|---|
| 1. Seguridad y línea base | R-01/R-02/R-09, regresión OpenAPI, pruebas LLM, alcance de lint y estado documental | Suite Python/JS verde; cargas hostiles y orígenes rechazados; pruebas de configuración sin secretos |
| 2. Dependencias y ejecución reproducible | R-03/R-04/R-16; timeouts de notificación R-08 | Audit sin los avisos identificados o excepción de alcance documentada; instalación limpia; adaptador simulado y presupuesto SMTP |
| 3. Cierre de migración fase 7 | Observación y acta, ensayo final de retorno, rutas de respaldo | Evidencia de uso y retorno, decisión explícita sobre convivencia, sin alterar prompts |
| 4. A-01 y A-02 | Evidencias, esquema, contexto y prototipo con dobles | Referencias válidas/inválidas probadas; salida estructurada y rechazo determinista; contrato API legado mantenido |
| 5. A-03 y A-04 | Muestreo, UTC/ráfagas, criterios, narrativa y publicación validada | Cobertura por ataque, precisión explicada, conteos comunes y conservación del reporte ante resultado inválido |
| 6. A-05 | Integración real controlada y conmutador del motor nuevo | Comparativa con línea base, costes/latencia, proveedor efectivo y retorno al flujo anterior |

Los defectos P1 del motor deben conservar prioridad aunque su implementación completa pase por contratos y prototipo. No hace falta esperar a terminar mejoras cosméticas ni crear nuevas vistas. Las entregas deben ser pequeñas y separar cambios de prompts de cambios visuales para atribuir resultados.

Para A-05 falta evaluar de forma real precisión/recall por categoría, falsos positivos con tráfico normal, incertidumbre por falta de cuerpo POST, referencias inventadas, resistencia a instrucciones en logs, cobertura truncada, tokens/coste, proveedor/modelo efectivo y latencia por etapa. Las diez ejecuciones exitosas de fase 6 y los dos éxitos OpenRouter prueban ejecución integrada, no esos resultados de calidad.

## Compatibilidad y reversión

La revisión conserva Python/CrewAI, Flask, Next.js, API `/api/v1`, reportes históricos y datos. No activa conmutadores ni cambia proveedor. El informe puede retirarse sin efecto en la aplicación; los artefactos de revisión son locales e ignorados. No eliminar el árbol enlazado de dependencias recursivamente sin verificar que la operación afecta únicamente al artefacto de revisión.

En las próximas entregas se debe mantener la API y un adaptador Markdown histórico, preservar la configuración y registrar la reversión concreta. La reversión operativa de fase 7 sigue siendo iniciar Flask con `NEXT_PRIMARY_ENABLED=0`; no requiere borrar volúmenes ni restaurar secretos. No se recomienda retirar Flask, activar el motor nuevo o publicar en una red compartida como consecuencia de este informe.

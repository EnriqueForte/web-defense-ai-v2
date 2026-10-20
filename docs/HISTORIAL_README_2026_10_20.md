# Historial de estados del README — conservado el 20/10/2026

Archivo histórico. Conserva los estados y enlaces que figuraban en el README
antes de consolidar la documentación. Sus pendientes y modos operativos
corresponden a cada fecha; no son instrucciones actuales. Los destinos de
enlaces se ajustaron a esta carpeta sin cambiar el texto histórico.

Para el estado actual, consultar el [resumen vigente](ESTADO_FINAL_2026_10_12.md)
y la [matriz de aceptación](MATRIZ_ACEPTACION_A05_2026_10_20.md).

## Estados trasladados


Consulta el [resumen vigente de pendientes para la versión final](ESTADO_FINAL_2026_10_12.md).
El lanzador y el contrato inicial de 158 paquetes por plataforma pasaron
Windows/Ubuntu CI y Parrot. La [migración CrewAI](MIGRACION_CREWAI_2026_10_12.md)
posterior fija 172 pines y pasó instalación/SDK/lanzador en Windows/Ubuntu CI,
reduciendo la auditoría Python de 36 entradas/cuatro paquetes a cinco solo en Chroma.
El 13/10 el usuario confirmó actualización, inventario 172/0/0, navegación y cierre
correctos en su VM Parrot. Las entradas fechadas
inferiores conservan estados históricos; los pendientes actuales están en ese resumen.

El 13/10 se completó la [validación de configuración global del ejecutor](CONFIGURACION_GLOBAL_2026_10_13.md):
los cuatro parámetros numéricos se rechazan con errores por variable antes de crear
estado si son inválidos. El [recorrido de Configuración](CONFIGURACION_E2E_2026_10_13.md)
también pasó nueve casos Chromium E2E en Windows/Ubuntu CI: guardar, recargar,
salir con solicitudes pendientes y recuperar errores, usando claves sintéticas.

La [entrada simplificada](INICIO_RAPIDO.md) prepara dependencias y build con
`python3 webdefense.py install` y arranca Flask/Next en una terminal con
`python3 webdefense.py start` (Windows: `py` en lugar de `python3`). Requiere
Python3.11/Node24/pnpm11.19.0 disponibles. Arranque de lectura; análisis y laboratorio
se configuran aparte. [Validación y límites](INSTALADOR_LANZADOR_2026_10_12.md):
el nuevo flujo pasó en Windows y Ubuntu CI, incluido cierre con puertos libres.
El comando unificado y el ajuste de puertos también fueron aceptados en Parrot.

La [validación Parrot del 12/10/2026](VALIDACION_PARROT_2026_10_12.md)
confirma instalación, pruebas offline, build, arranque y API directa/proxy HTTP200.
El usuario confirmó navegación correcta; faltan fuentes en el clon nuevo.
Docker e ingesta/análisis real en esa VM siguen pendientes. El inventario/pines
Linux adicionales se completó después en [el contrato Linux](CONTRATO_LINUX_2026_10_12.md).
Evidencia por capturas y
confirmación del usuario, sin acceso remoto a la VM.

La [validación CI del 12/10/2026](VALIDACION_CI_2026_10_12.md) pasó en
Windows y Ubuntu 24.04 desde checkout e instalación nueva: 269 Python, tres JS,
25 escenarios SDK, 15 grupos UI, lint/tipos y build. Se corrigió una prueba que
heredaba destinos de notificación vacíos; el producto conserva ese valor seguro.
Parrot y el arranque/proxy Linux se comprobaron después, según el registro anterior.
`uvloop==0.23.0` está fijado para Linux y el inventario completo se verificó
después en ambos runners y Parrot, según el contrato Linux enlazado.
Los servicios del mantenedor en Windows están detenidos.

El [refresco de indicadores del 11/10/2026](REFRESCO_INDICADORES_2026_10_11.md)
actualiza el resumen al observar una nueva ingesta/publicación y muestra la fecha
y referencia del informe. Pruebas UI y navegador aprobadas; frontend actualizado
sin análisis nuevos. El trabajo manual del usuario publicó prototype-8/report-4.
El total y círculo reflejan grupos del informe actual, sin acumular peticiones:
una publicación nueva puede mantener la misma distribución.

La [instalación limpia Windows del 11/10/2026](INSTALACION_LIMPIA_WINDOWS_2026_10_11.md)
pasó instalación, pruebas offline, build, producción/proxy y retorno en una copia
local sin entornos ni datos anteriores. El checkout e instalación Windows/Ubuntu
en CI y el ensayo guiado Parrot se acreditaron después.
Después se aplicó la [corrección de formato del análisis manual](CORRECCION_FORMATO_MANUAL_A05_2026_10_11.md):
JSON nativo solicitado a OpenRouter y validación local sin conversión parcial
de CrewAI. Pasaron 25 escenarios SDK offline; no se repitió el proveedor real.
A-05 sigue abierta por esa comprobación y por el primer fallo de ingesta cuya
causa no quedó registrada. Manual permanece habilitado en el piloto.

Las entradas siguientes son registros históricos; sus conmutadores y pendientes
corresponden a la fecha de cada operación.

La [activación manual del 11/10/2026](ACTIVACION_MANUAL_A05_2026_10_11.md)
deja admisión manual habilitada en el piloto con worker online, sin ciclos
automáticos o notificaciones. El usuario aceptó la vista previa; no se inició
un análisis ni se reescribió el informe vigente. API/condiciones del botón
verificadas; revisión visual limitada por la herramienta. A-05 conserva pendientes
de recorrido final con ingesta/publicación y confirmación de uso en navegador.

La [corrección narrativa del 10/10/2026](NARRATIVA_VALIDADA_A05_2026_10_10.md)
publica hechos validados y medidas revisadas en español, manteniendo las tres
tareas CrewAI y sus contratos. Pasaron 268 pruebas y 21 escenarios SDK offline.
Hay una vista previa local sobre los hallazgos del último job; el informe vigente
no se reescribió. A-05 sigue pendiente de revisión/aceptación y operación final
autorizada; manual permanece desactivado.

La [evaluación real de la corrección](EVALUACION_CORRECCION_A05_2026_10_10.md)
publicó cinco grupos coherentes con las referencias en un único job autorizado
(4 min 47 s/cinco llamadas). Diagnósticos, hashes y API verificados. A-05 continúa
abierta por narrativa/aceptación: un detalle del resumen carece de soporte y las
recomendaciones reiteran observaciones. Worker restaurado; manual desactivado.

La [corrección de omisión del 10/10/2026](CORRECCION_OMISION_A05_2026_10_10.md)
rechaza detecciones vacías cuando la selección contiene indicadores de Python.
Pasaron 261 pruebas en los tres entornos y 20 escenarios SDK offline; el ensayo
real posterior se registra arriba. Los informes anteriores se conservan y el
botón manual sigue desactivado hasta revisar el resultado del piloto.

El [diagnóstico real del 10/10/2026](DIAGNOSTICO_REAL_A05_2026_10_10.md)
verificó los recibos del motor/coordinador en un único análisis autorizado. El
usuario aceptó la revisión operativa previa, pero A-05 mantiene un pendiente de
calidad: la nueva detección devolvió cero hallazgos pese a indicadores Python en
26 líneas de la misma muestra. El informe advierte omisiones; el botón manual
sigue desactivado y el worker está restaurado. No se repitió el análisis.

El [Paso 2 operativo del 10/10/2026](OPERACION_A05_2026_10_10.md) deja el
piloto structured activo en `.p3` y Next 16.3.8 en producción local. Las lecturas,
cuatro vistas y un minuto de observación pasaron, con datos conservados,
admisión manual desactivada y sin análisis o envíos nuevos. A-05 sigue pendiente
de aceptación final; los diagnósticos de otro análisis real necesitan un alcance
autorizado. La instalación limpia final en Windows/Linux y Parrot sigue pendiente.

El [Paso 1 de dependencias del 10/10/2026](DEPENDENCIAS_2026_10_10.md)
actualiza Next/ESLint a 16.3.8 y el contrato Python compartido. La validación aislada
usa `.p3`, con 158 pines; los entornos anteriores se conservan y requieren transición
explícita. Producción frontend y vendor pasan audit; Python/braces mantienen avisos
documentados y el escaneo de imágenes está pendiente por Control de aplicaciones
de Windows. Los párrafos de entregas anteriores son registros históricos.

El motor continúa en Python/CrewAI y Flask conserva su dashboard anterior. La interfaz en `frontend/` usa Next.js 16, React 19 y TypeScript; consulta `/api/v1` para mostrar el resumen, las amenazas, la actividad y los reportes. La fase 5 añadió trabajos persistentes y una acción manual local desactivada por defecto. En la fase 6 se comprobaron el laboratorio DVWA/Mailpit, diez ciclos integrados, la carga de la API y el retorno a Flask. El usuario cerró anticipadamente esa fase el 29/09/2026 con 14 h 11 min 46 s saludables, sin completar las 24 horas previstas. La fase 7 se cerró para el alcance local reversible el 06/10/2026, con confirmación de uso y un nuevo ensayo de retorno, sin completar los siete días sugeridos. El conmutador permanece apagado por defecto; una tarea específica inicia Flask con Next.js como entrada sin editar `.env`.

El plan visual SOC es independiente de las fases de migración: sus fases UI 1–8 están completas, incluida seguridad/entrega. El usuario confirmó el zoom real al 200 % el 01/10/2026. La fase 7 de migración quedó cerrada en su alcance local reversible; Flask se conserva como respaldo.

El 06/10/2026 se completó la primera entrega del desarrollo derivado de la [revisión integral](REVISION_INTEGRAL_2026_10_06.md). Corrige rutas Flask y diagnósticos Telegram, recupera la regresión OpenAPI, incorpora pruebas aisladas de configuración LLM y unifica el lint completo. Su validación y límites se registran en [Seguridad y línea base](ENTREGA_1_SEGURIDAD_LINEA_BASE.md). Las mejoras del motor A-01–A-05 y las siguientes entregas permanecen pendientes.

Las fases 0–7 están cerradas para el alcance local, con los límites de observación registrados; la fase 6 incluye los límites de observación descritos en [su acta](FASE_6_PILOTO.md). Consultar [el plan de migración](PLAN_MIGRACION_INTERFAZ.md), [el contrato de fase 2](FASE_2_API_LECTURA.md), [la fase 5](FASE_5_ANALISIS_COORDINADO.md) y [el estado de la fase 7](FASE_7_ENTRADA_PRINCIPAL.md).

| Documento | Contenido |
|---|---|
| [Rediseño visual SOC](REDISENO_UI_SOC.md) | Fases UI 1–8 cerradas; zoom real al 200 % confirmado |
| [Guía de VSCode](GUIA_VSCODE.md) | Apertura, seguimiento de cambios, tareas y depuración |
| [Plan de migración](PLAN_MIGRACION_INTERFAZ.md) | Arquitectura, riesgos, fases, pruebas y reversión |
| [Fase 3 — Base visual](FASE_3_BASE_VISUAL.md) | Pantalla Next.js, datos sintéticos, validación y reversión |
| [Fase 4 — Lectura conectada](FASE_4_LECTURA_CONECTADA.md) | Integración con Flask, filtros, reportes, validación y reversión |
| [Fase 5 — Análisis coordinado](FASE_5_ANALISIS_COORDINADO.md) | Trabajos, ejecutor único, acción manual, límites y activación |
| [Fase 6 — Preparación del piloto](FASE_6_PILOTO.md) | Acceso local, mediciones, ventana de observación y reversión |
| [Laboratorio DVWA aislado](LABORATORIO_DVWA_FASE_6.md) | Inicio, detención, captura de logs y límites del Compose de piloto |
| [Fase 7 — Entrada principal](FASE_7_ENTRADA_PRINCIPAL.md) | Conmutación reversible, verificación y retorno |
| [Plan de agentes y tareas](PLAN_AGENTES_TAREAS.md) | Revisión de CrewAI, responsabilidades y backlog |
| [Contexto de desarrollo](../AGENTS.md) | Instrucciones compartidas para trabajar desde Codex |
| [Repositorios y recuperación](REPOSITORIOS.md) | Separación entre original y V2, remotos y copias locales |

La [entrega 2](ENTREGA_2_DEPENDENCIAS_EJECUCION.md) añade parches transitivos
del frontend, declara LiteLLM y verifica una instalación Python limpia con 155
paquetes fijados. Las notificaciones coordinadas tienen timeout SMTP y plazo
total por destino. El audit de producción pasa; queda un aviso de braces en
desarrollo sin corrección publicada. La `.venv` operativa se conserva con cuatro
diferencias conocidas; su transición sigue pendiente. A-01–A-05 no se
cierran por estas correcciones.

La [entrega 3](ENTREGA_3_OPERACION_CIERRE_LOCAL.md) registra el cierre local
de fase 7, un nuevo ensayo de retorno a Flask y respaldo/restauración verificados
de logs, reportes y SQLite del piloto. `scripts/backup_operational.py --list`
muestra la cobertura y `scripts/backup_operational.py` crea una copia nueva
sin sobrescribir datos. Se conservan Flask, los conmutadores y los límites de
observación. La siguiente línea de desarrollo es A-01/A-02.

La [entrega 4](ENTREGA_4_CONTRATOS_PROTOTIPO.md) completa A-01/A-02 en
alcance aislado: contratos de evidencia/resultados, adaptación histórica y
tareas CrewAI estructuradas verificadas con respuestas simuladas. El motor
operativo continúa con su flujo anterior; A-03–A-05 siguen pendientes.

La [entrega 5](ENTREGA_5_PREPARACION_PUBLICACION.md) completa A-03/A-04 en
alcance aislado: selección equilibrada, agregados UTC, criterios trazables,
tabla/conteos deterministas y publicación por generaciones validada. El motor
operativo anterior permanece activo; integración y evaluación real son A-05.

La [entrega 6](ENTREGA_6_INTEGRACION_EVALUACION.md) implementa la
integración reversible del motor estructurado con coordinador y Flask.
Validación: 179 pruebas Python, tres diagnósticos JS y seis escenarios CrewAI
con doble LLM. El modo `legacy` permanece predeterminado. A-05 continúa abierta:
el análisis sintético gratuito autorizado fue rechazado por autenticación en
OpenRouter y no generó un reporte. Falta evaluación real y aceptación para activar.
La revisión posterior detectó que la ruta de conversión CrewAI omitía la clave
y URL suministradas. Ese defecto está corregido y verificado offline; el fallo
anterior no demuestra una clave incorrecta. Siete escenarios CrewAI aprobados;
la repetición real con el adaptador corregido terminó con ValueError tras dos
llamadas y 50,031 s, sin el error de autenticación en la cadena registrada y sin
publicar informe. Falta precisar la causa y completar la evaluación.
Ya se añadió diagnóstico por etapa sin respuestas ni secretos; validación actual:
186 pruebas Python, tres diagnósticos JS y nueve escenarios CrewAI offline.
La nueva instrumentación aún no se ha usado en otra llamada real.
Posteriormente el usuario autorizó otra prueba real con diagnóstico: falló en
detección porque el adaptador devolvió 0 caracteres (una llamada, 35,516 s).
No se alcanzaron guardas ni publicación. Falta precisar el origen de esa respuesta
vacía; no se activó el motor estructurado ni se enviaron notificaciones.
La captura de metadatos de completado ya está preparada: motivo de finalización,
modelo informado y tokens, sin contenido ni claves. Validación actual: 192
pruebas Python, tres JS y 11 escenarios CrewAI/LiteLLM offline. Falta obtener
esos metadatos en otra prueba real autorizada; el modo operativo sigue `legacy`.
La prueba real posterior informó `finish_reason=length`, límite de 2048 tokens
y ausencia de texto final. Se preparó un límite de 8192 **solo para el evaluador
sintético**, aún sin repetir con ese ajuste. Se conserva la configuración operativa.
La repetición con 8192 obtuvo JSON en la primera llamada, rechazado por IDs
inválidos/duplicados; el reintento agotó la salida. Se alineó el esquema y se
explicitaron las restricciones de IDs (structured-prototype-3), con 13 escenarios
SDK offline aprobados. Falta otra evaluación autorizada; no se publicó informe.
La siguiente evaluación autorizada completó el flujo y generó JSON/Markdown
validados en la carpeta aislada: cuatro llamadas y 57,625 s. Encontró las cinco
familias, con un falso positivo low/other sobre la petición normal. A-05 sigue
abierta por calidad y aceptación; el modo operativo continúa en `legacy`.
El seguimiento de calidad endurece las guardas de `other` para impedir ese
hallazgo sin soporte y conserva la incertidumbre de evidencia no interpretable.
También reconcilia el uso desde los metadatos, separando el acumulador SDK y sus
discrepancias. 203 pruebas Python, tres JS y 15 escenarios SDK offline aprobados;
falta verificar estos ajustes con el proveedor. No se cambió el modo operativo.
El 07/10/2026 pasó la verificación real de esos ajustes: cinco familias, sin
falso positivo sobre /index.html, cuatro llamadas/81 s y métricas de tokens
conciliadas. Se prepararon ocho casos separados para ampliar la evaluación;
el evaluador permite escoger uno sin lanzar un lote. 208 pruebas Python,
tres JS y 15 escenarios offline aprobados. La ampliación requiere acotar las
llamadas y A-05 sigue abierta; no se activó el motor estructurado.
El lote ampliado autorizado del 07/10/2026 pasó los siete casos de familias,
con 23 de 42 llamadas. La revisión detectó narrativa insuficiente y latencia
alta en el caso normal; el resumen sin hallazgos ahora se genera desde Python,
con alcance y limitaciones, validado sin nuevas llamadas. 211 pruebas Python,
tres JS y 15 escenarios SDK aislados aprobados. [Resultados y límites](EVALUACION_AMPLIADA_A05_2026_10_07.md).
La aceptación y activación siguen pendientes; el modo operativo permanece legacy.
La [optimización sin hallazgos](OPTIMIZACION_A05_SIN_HALLAZGOS.md) elimina
las llamadas de clasificación y narrativa cuando la detección validada devuelve
cero candidatos, conservando las tareas y guardas. 212 pruebas Python, tres JS
y 17 escenarios offline aprobados; una llamada de SDK simulada para el recorrido
normal completo. Falta medir con el proveedor; no se activó el motor ni se
hicieron nuevas llamadas reales.
La siguiente muestra normal autorizada completó el flujo optimizado en 24 s
con dos llamadas de detección y las dos tareas restantes locales. La entrada es
igual a la muestra previa de 475,829 s, pero los modelos variaron; no es un p95.
Los límites 8192/60 se alinearon en la fábrica estructurada y el evaluador, sin
alterar legacy. Guardas/hashes y adaptadores offline verificados; no se activó.
La [propuesta de activación local](ACTIVACION_LOCAL_A05.md) prepara un
perfil compartido de Flask/worker con `.p2`, preflight y arranque solo mediante
`--start`. La comprobación del piloto pasó; análisis manual y notificaciones
quedan apagados. 223 pruebas Python en ambos entornos y 17 escenarios offline
aprobados. Después, el usuario aceptó y se arrancaron Flask/worker con el perfil
piloto estructurado; `.env` no cambia. Ejecutor online y cuatro rutas API HTTP 200,
sin nuevos trabajos; salud unavailable hasta el primer informe estructurado.
Respaldo/restauración de 17 archivos verificados. Primer análisis y observación
operativa pendientes; detalles en la propuesta actualizada.
El [primer análisis autorizado del coordinador](PRIMER_ANALISIS_COORDINADOR_A05.md)
terminó correctamente en 157 s: ingesta DVWA, publicación e histórico verificados,
salud ok y cero notificaciones. Seleccionó 30 de 112 líneas; los cinco grupos
son indicadores, sin confirmar explotación. Manual sigue desactivado;
observación operativa y aceptación final pendientes.
La [revisión de las cuatro vistas](REVISION_VISTAS_A05_2026_10_07.md)
verificó el informe en Next y corrigió un evento XSS etiquetado como SQLi por
una comilla codificada. 226 pruebas Python y tres diagnósticos JS aprobados;
motor e informe intactos. Consola local en http://127.0.0.1:3000, con análisis
manual desactivado y aceptación del usuario pendiente para este informe.
La [corrección de fechas y referencias](FECHAS_REFERENCIAS_A05_2026_10_07.md)
muestra intervalos observados y «Líneas del log», conservando los archivos
originales. La recaptura contiene peticiones del 1–2 de octubre, ninguna de hoy;
la UI distingue fecha de petición de fecha de copia. 227 pruebas Python,
siete grupos UI y tipos/lint aprobados. La aceptación A-05 sigue pendiente.
El [refresco por publicación](REFRESCO_PUBLICACIONES_2026_10_07.md) corrige
referencias obsoletas al republicar el mismo texto y evita aplicar lecturas
canceladas. 228 pruebas Python y nueve grupos UI aprobados; sin nuevos análisis.
Quedan robustez completa de solicitudes/polling y aceptación final de A-05.
La [robustez de lecturas](ROBUSTEZ_LECTURAS_2026_10_07.md) se completó
después: contratos de respuesta, espera acotada a 10 s y sondeo sin solapamiento
por canal. 14 grupos UI, tipos/lint y siete lecturas API reales aprobados;
fallos probados con dobles, sin nuevos análisis. A-05 conserva aceptación pendiente.
El [diagnóstico operativo](DIAGNOSTICO_OPERATIVO_2026_10_07.md) añade recibos
seguros por ejecución structured, metadatos LiteLLM por intento y reconciliación
con SDK. 243 pruebas Python y 18 escenarios SDK offline aprobados. No se hicieron
llamadas reales ni se reinició el worker; carga y comprobación operativa pendientes.


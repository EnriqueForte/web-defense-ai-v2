# 🛡️ web-defense-ai V2

Segunda versión de la aplicación de ciberseguridad defensiva de **T3r0S3c**. Analiza logs de Apache de un laboratorio DVWA mediante tres agentes CrewAI y presenta resultados en un dashboard.

**Desarrollo en Codex; seguimiento continuo de los archivos en VSCode.** Ambos utilizan la misma carpeta local. La denominación oficial de la aplicación es **web-defense-ai V2**; T3r0S3c se conserva como autor.

El destino de esta versión es [EnriqueForte/web-defense-ai-v2](https://github.com/EnriqueForte/web-defense-ai-v2), configurado como `origin`. Se prepara para distribuir el código por GitHub y permitir que cada persona lo clone y lo ejecute en su propia instalación. El [repositorio original](https://github.com/EnriqueForte/web-defense-ai) se conserva independiente y sin modificaciones. Véase [la separación de repositorios](docs/REPOSITORIOS.md).

La distribución utiliza la licencia MIT existente. El dashboard admite acceso
local: cada instalación configura sus credenciales y datos. Compartir el código
no habilita un servicio público del dashboard. Windows/Python 3.11 está validado
localmente; instalación y pruebas offline también pasan en Windows y Ubuntu
24.04 en CI. Parrot 7.3 x86_64 en VMware pasó instalación, pruebas y lectura
mediante validación guiada con el usuario; macOS no se ha comprobado.
Consulta la [guía de instalación para clonación](docs/INSTALACION_AUTOALOJADA.md)
y sus pendientes de validación antes de la publicación de una versión final.

## Estado de esta versión

Consulta el [resumen vigente de pendientes para la versión final](docs/ESTADO_FINAL_2026_10_12.md).
El lanzador y el contrato inicial de 158 paquetes por plataforma pasaron
Windows/Ubuntu CI y Parrot. La [migración CrewAI](docs/MIGRACION_CREWAI_2026_10_12.md)
posterior fija 172 pines y pasó instalación/SDK/lanzador en Windows/Ubuntu CI,
reduciendo la auditoría Python de 36 entradas/cuatro paquetes a cinco solo en Chroma.
El 13/10 el usuario confirmó actualización, inventario 172/0/0, navegación y cierre
correctos en su VM Parrot. Las entradas fechadas
inferiores conservan estados históricos; los pendientes actuales están en ese resumen.

La [entrada simplificada](docs/INICIO_RAPIDO.md) prepara dependencias y build con
`python3 webdefense.py install` y arranca Flask/Next en una terminal con
`python3 webdefense.py start` (Windows: `py` en lugar de `python3`). Requiere
Python3.11/Node24/pnpm11.19.0 disponibles. Arranque de lectura; análisis y laboratorio
se configuran aparte. [Validación y límites](docs/INSTALADOR_LANZADOR_2026_10_12.md):
el nuevo flujo pasó en Windows y Ubuntu CI, incluido cierre con puertos libres.
El comando unificado y el ajuste de puertos también fueron aceptados en Parrot.

La [validación Parrot del 12/10/2026](docs/VALIDACION_PARROT_2026_10_12.md)
confirma instalación, pruebas offline, build, arranque y API directa/proxy HTTP200.
El usuario confirmó navegación correcta; faltan fuentes en el clon nuevo.
Docker e ingesta/análisis real en esa VM siguen pendientes. El inventario/pines
Linux adicionales se completó después en [el contrato Linux](docs/CONTRATO_LINUX_2026_10_12.md).
Evidencia por capturas y
confirmación del usuario, sin acceso remoto a la VM.

La [validación CI del 12/10/2026](docs/VALIDACION_CI_2026_10_12.md) pasó en
Windows y Ubuntu 24.04 desde checkout e instalación nueva: 269 Python, tres JS,
25 escenarios SDK, 15 grupos UI, lint/tipos y build. Se corrigió una prueba que
heredaba destinos de notificación vacíos; el producto conserva ese valor seguro.
Parrot y el arranque/proxy Linux se comprobaron después, según el registro anterior.
`uvloop==0.23.0` está fijado para Linux y el inventario completo se verificó
después en ambos runners y Parrot, según el contrato Linux enlazado.
Los servicios del mantenedor en Windows están detenidos.

El [refresco de indicadores del 11/10/2026](docs/REFRESCO_INDICADORES_2026_10_11.md)
actualiza el resumen al observar una nueva ingesta/publicación y muestra la fecha
y referencia del informe. Pruebas UI y navegador aprobadas; frontend actualizado
sin análisis nuevos. El trabajo manual del usuario publicó prototype-8/report-4.
El total y círculo reflejan grupos del informe actual, sin acumular peticiones:
una publicación nueva puede mantener la misma distribución.

La [instalación limpia Windows del 11/10/2026](docs/INSTALACION_LIMPIA_WINDOWS_2026_10_11.md)
pasó instalación, pruebas offline, build, producción/proxy y retorno en una copia
local sin entornos ni datos anteriores. El checkout e instalación Windows/Ubuntu
en CI y el ensayo guiado Parrot se acreditaron después.
Después se aplicó la [corrección de formato del análisis manual](docs/CORRECCION_FORMATO_MANUAL_A05_2026_10_11.md):
JSON nativo solicitado a OpenRouter y validación local sin conversión parcial
de CrewAI. Pasaron 25 escenarios SDK offline; no se repitió el proveedor real.
A-05 sigue abierta por esa comprobación y por el primer fallo de ingesta cuya
causa no quedó registrada. Manual permanece habilitado en el piloto.

Las entradas siguientes son registros históricos; sus conmutadores y pendientes
corresponden a la fecha de cada operación.

La [activación manual del 11/10/2026](docs/ACTIVACION_MANUAL_A05_2026_10_11.md)
deja admisión manual habilitada en el piloto con worker online, sin ciclos
automáticos o notificaciones. El usuario aceptó la vista previa; no se inició
un análisis ni se reescribió el informe vigente. API/condiciones del botón
verificadas; revisión visual limitada por la herramienta. A-05 conserva pendientes
de recorrido final con ingesta/publicación y confirmación de uso en navegador.

La [corrección narrativa del 10/10/2026](docs/NARRATIVA_VALIDADA_A05_2026_10_10.md)
publica hechos validados y medidas revisadas en español, manteniendo las tres
tareas CrewAI y sus contratos. Pasaron 268 pruebas y 21 escenarios SDK offline.
Hay una vista previa local sobre los hallazgos del último job; el informe vigente
no se reescribió. A-05 sigue pendiente de revisión/aceptación y operación final
autorizada; manual permanece desactivado.

La [evaluación real de la corrección](docs/EVALUACION_CORRECCION_A05_2026_10_10.md)
publicó cinco grupos coherentes con las referencias en un único job autorizado
(4 min 47 s/cinco llamadas). Diagnósticos, hashes y API verificados. A-05 continúa
abierta por narrativa/aceptación: un detalle del resumen carece de soporte y las
recomendaciones reiteran observaciones. Worker restaurado; manual desactivado.

La [corrección de omisión del 10/10/2026](docs/CORRECCION_OMISION_A05_2026_10_10.md)
rechaza detecciones vacías cuando la selección contiene indicadores de Python.
Pasaron 261 pruebas en los tres entornos y 20 escenarios SDK offline; el ensayo
real posterior se registra arriba. Los informes anteriores se conservan y el
botón manual sigue desactivado hasta revisar el resultado del piloto.

El [diagnóstico real del 10/10/2026](docs/DIAGNOSTICO_REAL_A05_2026_10_10.md)
verificó los recibos del motor/coordinador en un único análisis autorizado. El
usuario aceptó la revisión operativa previa, pero A-05 mantiene un pendiente de
calidad: la nueva detección devolvió cero hallazgos pese a indicadores Python en
26 líneas de la misma muestra. El informe advierte omisiones; el botón manual
sigue desactivado y el worker está restaurado. No se repitió el análisis.

El [Paso 2 operativo del 10/10/2026](docs/OPERACION_A05_2026_10_10.md) deja el
piloto structured activo en `.p3` y Next 16.3.8 en producción local. Las lecturas,
cuatro vistas y un minuto de observación pasaron, con datos conservados,
admisión manual desactivada y sin análisis o envíos nuevos. A-05 sigue pendiente
de aceptación final; los diagnósticos de otro análisis real necesitan un alcance
autorizado. La instalación limpia final en Windows/Linux y Parrot sigue pendiente.

El [Paso 1 de dependencias del 10/10/2026](docs/DEPENDENCIAS_2026_10_10.md)
actualiza Next/ESLint a 16.3.8 y el contrato Python compartido. La validación aislada
usa `.p3`, con 158 pines; los entornos anteriores se conservan y requieren transición
explícita. Producción frontend y vendor pasan audit; Python/braces mantienen avisos
documentados y el escaneo de imágenes está pendiente por Control de aplicaciones
de Windows. Los párrafos de entregas anteriores son registros históricos.

El motor continúa en Python/CrewAI y Flask conserva su dashboard anterior. La interfaz en `frontend/` usa Next.js 16, React 19 y TypeScript; consulta `/api/v1` para mostrar el resumen, las amenazas, la actividad y los reportes. La fase 5 añadió trabajos persistentes y una acción manual local desactivada por defecto. En la fase 6 se comprobaron el laboratorio DVWA/Mailpit, diez ciclos integrados, la carga de la API y el retorno a Flask. El usuario cerró anticipadamente esa fase el 29/09/2026 con 14 h 11 min 46 s saludables, sin completar las 24 horas previstas. La fase 7 se cerró para el alcance local reversible el 06/10/2026, con confirmación de uso y un nuevo ensayo de retorno, sin completar los siete días sugeridos. El conmutador permanece apagado por defecto; una tarea específica inicia Flask con Next.js como entrada sin editar `.env`.

El plan visual SOC es independiente de las fases de migración: sus fases UI 1–8 están completas, incluida seguridad/entrega. El usuario confirmó el zoom real al 200 % el 01/10/2026. La fase 7 de migración quedó cerrada en su alcance local reversible; Flask se conserva como respaldo.

El 06/10/2026 se completó la primera entrega del desarrollo derivado de la [revisión integral](docs/REVISION_INTEGRAL_2026_10_06.md). Corrige rutas Flask y diagnósticos Telegram, recupera la regresión OpenAPI, incorpora pruebas aisladas de configuración LLM y unifica el lint completo. Su validación y límites se registran en [Seguridad y línea base](docs/ENTREGA_1_SEGURIDAD_LINEA_BASE.md). Las mejoras del motor A-01–A-05 y las siguientes entregas permanecen pendientes.

Las fases 0–7 están cerradas para el alcance local, con los límites de observación registrados; la fase 6 incluye los límites de observación descritos en [su acta](docs/FASE_6_PILOTO.md). Consultar [el plan de migración](docs/PLAN_MIGRACION_INTERFAZ.md), [el contrato de fase 2](docs/FASE_2_API_LECTURA.md), [la fase 5](docs/FASE_5_ANALISIS_COORDINADO.md) y [el estado de la fase 7](docs/FASE_7_ENTRADA_PRINCIPAL.md).

| Documento | Contenido |
|---|---|
| [Rediseño visual SOC](docs/REDISENO_UI_SOC.md) | Fases UI 1–8 cerradas; zoom real al 200 % confirmado |
| [Guía de VSCode](docs/GUIA_VSCODE.md) | Apertura, seguimiento de cambios, tareas y depuración |
| [Plan de migración](docs/PLAN_MIGRACION_INTERFAZ.md) | Arquitectura, riesgos, fases, pruebas y reversión |
| [Fase 3 — Base visual](docs/FASE_3_BASE_VISUAL.md) | Pantalla Next.js, datos sintéticos, validación y reversión |
| [Fase 4 — Lectura conectada](docs/FASE_4_LECTURA_CONECTADA.md) | Integración con Flask, filtros, reportes, validación y reversión |
| [Fase 5 — Análisis coordinado](docs/FASE_5_ANALISIS_COORDINADO.md) | Trabajos, ejecutor único, acción manual, límites y activación |
| [Fase 6 — Preparación del piloto](docs/FASE_6_PILOTO.md) | Acceso local, mediciones, ventana de observación y reversión |
| [Laboratorio DVWA aislado](docs/LABORATORIO_DVWA_FASE_6.md) | Inicio, detención, captura de logs y límites del Compose de piloto |
| [Fase 7 — Entrada principal](docs/FASE_7_ENTRADA_PRINCIPAL.md) | Conmutación reversible, verificación y retorno |
| [Plan de agentes y tareas](docs/PLAN_AGENTES_TAREAS.md) | Revisión de CrewAI, responsabilidades y backlog |
| [Contexto de desarrollo](AGENTS.md) | Instrucciones compartidas para trabajar desde Codex |
| [Repositorios y recuperación](docs/REPOSITORIOS.md) | Separación entre original y V2, remotos y copias locales |

La [entrega 2](docs/ENTREGA_2_DEPENDENCIAS_EJECUCION.md) añade parches transitivos
del frontend, declara LiteLLM y verifica una instalación Python limpia con 155
paquetes fijados. Las notificaciones coordinadas tienen timeout SMTP y plazo
total por destino. El audit de producción pasa; queda un aviso de braces en
desarrollo sin corrección publicada. La `.venv` operativa se conserva con cuatro
diferencias conocidas; su transición sigue pendiente. A-01–A-05 no se
cierran por estas correcciones.

La [entrega 3](docs/ENTREGA_3_OPERACION_CIERRE_LOCAL.md) registra el cierre local
de fase 7, un nuevo ensayo de retorno a Flask y respaldo/restauración verificados
de logs, reportes y SQLite del piloto. `scripts/backup_operational.py --list`
muestra la cobertura y `scripts/backup_operational.py` crea una copia nueva
sin sobrescribir datos. Se conservan Flask, los conmutadores y los límites de
observación. La siguiente línea de desarrollo es A-01/A-02.

La [entrega 4](docs/ENTREGA_4_CONTRATOS_PROTOTIPO.md) completa A-01/A-02 en
alcance aislado: contratos de evidencia/resultados, adaptación histórica y
tareas CrewAI estructuradas verificadas con respuestas simuladas. El motor
operativo continúa con su flujo anterior; A-03–A-05 siguen pendientes.

La [entrega 5](docs/ENTREGA_5_PREPARACION_PUBLICACION.md) completa A-03/A-04 en
alcance aislado: selección equilibrada, agregados UTC, criterios trazables,
tabla/conteos deterministas y publicación por generaciones validada. El motor
operativo anterior permanece activo; integración y evaluación real son A-05.

La [entrega 6](docs/ENTREGA_6_INTEGRACION_EVALUACION.md) implementa la
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
tres JS y 15 escenarios SDK aislados aprobados. [Resultados y límites](docs/EVALUACION_AMPLIADA_A05_2026_10_07.md).
La aceptación y activación siguen pendientes; el modo operativo permanece legacy.
La [optimización sin hallazgos](docs/OPTIMIZACION_A05_SIN_HALLAZGOS.md) elimina
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
La [propuesta de activación local](docs/ACTIVACION_LOCAL_A05.md) prepara un
perfil compartido de Flask/worker con `.p2`, preflight y arranque solo mediante
`--start`. La comprobación del piloto pasó; análisis manual y notificaciones
quedan apagados. 223 pruebas Python en ambos entornos y 17 escenarios offline
aprobados. Después, el usuario aceptó y se arrancaron Flask/worker con el perfil
piloto estructurado; `.env` no cambia. Ejecutor online y cuatro rutas API HTTP 200,
sin nuevos trabajos; salud unavailable hasta el primer informe estructurado.
Respaldo/restauración de 17 archivos verificados. Primer análisis y observación
operativa pendientes; detalles en la propuesta actualizada.
El [primer análisis autorizado del coordinador](docs/PRIMER_ANALISIS_COORDINADOR_A05.md)
terminó correctamente en 157 s: ingesta DVWA, publicación e histórico verificados,
salud ok y cero notificaciones. Seleccionó 30 de 112 líneas; los cinco grupos
son indicadores, sin confirmar explotación. Manual sigue desactivado;
observación operativa y aceptación final pendientes.
La [revisión de las cuatro vistas](docs/REVISION_VISTAS_A05_2026_10_07.md)
verificó el informe en Next y corrigió un evento XSS etiquetado como SQLi por
una comilla codificada. 226 pruebas Python y tres diagnósticos JS aprobados;
motor e informe intactos. Consola local en http://127.0.0.1:3000, con análisis
manual desactivado y aceptación del usuario pendiente para este informe.
La [corrección de fechas y referencias](docs/FECHAS_REFERENCIAS_A05_2026_10_07.md)
muestra intervalos observados y «Líneas del log», conservando los archivos
originales. La recaptura contiene peticiones del 1–2 de octubre, ninguna de hoy;
la UI distingue fecha de petición de fecha de copia. 227 pruebas Python,
siete grupos UI y tipos/lint aprobados. La aceptación A-05 sigue pendiente.
El [refresco por publicación](docs/REFRESCO_PUBLICACIONES_2026_10_07.md) corrige
referencias obsoletas al republicar el mismo texto y evita aplicar lecturas
canceladas. 228 pruebas Python y nueve grupos UI aprobados; sin nuevos análisis.
Quedan robustez completa de solicitudes/polling y aceptación final de A-05.
La [robustez de lecturas](docs/ROBUSTEZ_LECTURAS_2026_10_07.md) se completó
después: contratos de respuesta, espera acotada a 10 s y sondeo sin solapamiento
por canal. 14 grupos UI, tipos/lint y siete lecturas API reales aprobados;
fallos probados con dobles, sin nuevos análisis. A-05 conserva aceptación pendiente.
El [diagnóstico operativo](docs/DIAGNOSTICO_OPERATIVO_2026_10_07.md) añade recibos
seguros por ejecución structured, metadatos LiteLLM por intento y reconciliación
con SDK. 243 pruebas Python y 18 escenarios SDK offline aprobados. No se hicieron
llamadas reales ni se reinició el worker; carga y comprobación operativa pendientes.

## Abrir el proyecto en VSCode

Abrir **web-defense-ai V2.code-workspace** desde Archivo → Abrir área de trabajo desde archivo. Si el comando de VSCode está disponible, también puede abrirse desde la raíz:

```powershell
code "web-defense-ai V2.code-workspace"
```

El explorador y Control de código fuente permiten seguir los cambios guardados por Codex. No es necesario trasladar archivos. Evitar cambios sin guardar sobre un archivo que se esté modificando desde Codex.

Se recomiendan extensiones de Python, Pylance, depuración, Black y YAML. Seleccionar `.venv/Scripts/python.exe` con **Python: Select Interpreter**. Las recomendaciones no instalan extensiones automáticamente.

| Acción | Acceso en VSCode |
|---|---|
| Revisar sintaxis sin ejecutar el motor | Ctrl+Shift+B |
| Ver dashboard con recarga local | Terminal → Ejecutar tarea → web-defense-ai V2: dashboard con recarga local |
| Ver consola Next.js conectada | Terminal → Ejecutar tarea → web-defense-ai V2: lectura conectada (Flask + Next.js) |
| Usar Next.js como entrada local reversible | Terminal → Ejecutar tarea → web-defense-ai V2: entrada Next.js local (Fase 7) |
| Depurar el dashboard | Ejecutar y depurar → web-defense-ai V2: dashboard local → F5 |
| Leer documentación renderizada | Abrir Markdown y pulsar Ctrl+Shift+V |

Abrir [el dashboard local](http://127.0.0.1:5000) después de iniciar su tarea. Las modificaciones de archivos se reflejan en VSCode; la página web debe actualizarse al cambiar HTML o CSS. El proceso Flask se recarga ante cambios Python en la tarea de visualización. El perfil de depuración usa reinicio manual.

La tarea de Fase 7 hace que la misma dirección de Flask redirija a Next.js
cuando ambos están disponibles. Si Next.js cae, una visita nueva vuelve al
dashboard Flask. Para desactivar la redirección explícitamente, detener las
terminales de Fase 7 y arrancar la tarea habitual de Flask; no ejecutar dos
tareas Flask a la vez en el puerto 5000. El procedimiento y sus límites están
en [FASE_7_ENTRADA_PRINCIPAL.md](docs/FASE_7_ENTRADA_PRINCIPAL.md).

## Arquitectura actual

```text
DVWA / Apache → volumen Docker → sincronización → logs/access.log
                                                       ↓
                                           pipeline.py / main.py
                                                       ↓
                                    Analista → Detective → Reporter
                                                       ↓
                                      Markdown actual e históricos
                                                       ↓
                                              Dashboard Flask

El ejecutor puede enviar notificaciones mediante Telegram y SMTP.
La sincronización anterior del dashboard solo copia el log.
```

| Área | Tecnología actual |
|---|---|
| Motor | Python 3.11 y CrewAI 1.14.2 declarado |
| Modelos | Groq por defecto y OpenRouter opcional; configuración local por instalación |
| Dashboard | Flask + Jinja2 + JavaScript |
| Gráficos | Chart.js |
| Laboratorio | Docker Compose, DVWA y MySQL para DVWA |
| Alertas | Telegram Bot API y correo SMTP |
| Nueva interfaz de lectura | React + Next.js + TypeScript; consume `/api/v1` de Flask |

El contenedor `ai-engine` declarado en Compose permanece inactivo con `tail -f /dev/null`; no arranca automáticamente el motor o el dashboard. La base MySQL pertenece al laboratorio DVWA.

## Entorno y ejecución

El entorno local revisado utiliza Python 3.11.9. `requirements.txt` incluye ahora Flask y limita pywin32 a Windows. Para las pruebas aisladas basta instalar `requirements-test.txt` y disponer de Node; ejecutar `python -B scripts/check_baseline.py`. No requiere `.env`, Docker ni claves. La [línea base](docs/FASE_0_LINEA_BASE.md) detalla la verificación de instalación y sus límites.

Las regresiones de los componentes de la interfaz se ejecutan desde `frontend/` con `pnpm run test:ui`.

Para la instalación completa actual usar el instalador común, `requirements.txt`
y `constraints-py311.txt`, en un entorno nuevo de ruta corta. Primero prepara las
herramientas fijadas en `requirements-bootstrap.txt` dentro del venv.
`constraints-windows-py311-dependencies-20261010.txt` registra la validación Windows
actual; la instantánea de entrega 2 se conserva como evidencia histórica.
`scripts/check_environment.py` detecta diferencias de versión sin importar el
motor; `scripts/check_llm_adapter.py` construye el adaptador OpenRouter offline.
La instantánea de fase 0 permanece como evidencia histórica. Consultar la
entrega 2 antes de cambiar el intérprete utilizado en operación.

Para copiar la plantilla sin sobrescribir una configuración existente:

```powershell
if (-not (Test-Path -LiteralPath .env)) {
    Copy-Item -LiteralPath .env.example -Destination .env
}
```

La pantalla **Configuración** del dashboard permite elegir Groq (predeterminado) u OpenRouter, seleccionar un modelo del catálogo o indicar un identificador propio y guardar la clave API de esta instalación. El backend local la escribe en `.env`; la clave no vuelve al navegador ni se envía a un servicio central. `.env` es texto sin cifrar, está excluido de Git y el dashboard debe permanecer en localhost. No versionar ni compartir ese archivo.

Las opciones marcadas como gratuitas dependen de la disponibilidad y límites vigentes del proveedor. Un modelo personalizado puede generar cargos; el selector no conoce el saldo ni el plan de la cuenta. Para añadir proveedores, modelos gratuitos o fallbacks, consultar [Configuración local del proveedor LLM](docs/CONFIGURACION_PROVEEDOR_LLM.md). Rutas, intervalo y destinos opcionales de Telegram/SMTP siguen configurándose localmente.

El laboratorio DVWA aislado se inicia solo cuando se decida verificarlo, usando
`scripts/start_dvwa_lab.ps1`; para detenerlo conservando sus volúmenes, usar
`scripts/stop_dvwa_lab.ps1`. La [guía del laboratorio](docs/LABORATORIO_DVWA_FASE_6.md)
describe los límites, la copia del log y la eliminación explícita de los datos
del contenedor. Estas operaciones no inician Flask, CrewAI, el pipeline ni
notificaciones. La integración controlada de fase 6 ya se realizó; no
usar `main.py` o `pipeline.py` como comprobaciones de arranque. Para visualizar
Next.js con lectura de Flask basta la tarea conjunta de ambos servidores.

## Funciones y límites conocidos

El dashboard presenta métricas del reporte, tabla de amenazas, coincidencias de patrones por hora, cinco reportes históricos recientes y ocho líneas del log. El motor contempla SQLi, XSS, traversal, fuerza bruta e inyección de comandos, con las limitaciones de evidencia y muestreo descritas en los planes.

La fase 1 corrigió la pantalla sin reporte, la recursión del timeline, el recuento de severidades y la representación insegura de logs y reportes. La fase 2 separó las consultas de estado de la sincronización con Docker y añadió lecturas `/api/v1`. La fase 4 conectó Next.js a esa API. La fase 5 añadió trabajos coordinados y una solicitud manual opcional; el botón anterior solo sincroniza el log cuando el ejecutor está detenido.

## Estructura

```text
web-defense-ai V2/
├── .vscode/
│   ├── settings.json                 # Ajustes del proyecto
│   ├── extensions.json               # Extensiones recomendadas
│   ├── tasks.json                    # Sintaxis y visualización local
│   ├── run-frontend.ps1              # Tareas Next.js sin pnpm en PATH
│   └── launch.json                   # Depuración y operaciones reales
├── docs/
│   ├── GUIA_VSCODE.md
│   ├── PLAN_MIGRACION_INTERFAZ.md
│   ├── PLAN_AGENTES_TAREAS.md
│   ├── FASE_0_LINEA_BASE.md
│   ├── FASE_2_API_LECTURA.md
│   ├── FASE_3_BASE_VISUAL.md
│   └── FASE_4_LECTURA_CONECTADA.md
├── frontend/                         # Next.js: lectura conectada a Flask
├── agents/                           # Preprocesamiento, detective y reporter
├── config/                           # Configuración, prompts y alertas
├── dashboard/
│   ├── app.py                        # Flask
│   ├── templates/                    # Dashboard y reporte
│   └── static/                       # CSS y favicon
├── logs/                             # Datos operativos excluidos de Git
├── reports/                          # Reporte actual e históricos
├── screenshots/                      # Capturas de referencia anteriores
├── scripts/                          # Verificación y utilidades del laboratorio local
├── tests/                            # Suite aislada y comprobaciones JS
├── AGENTS.md
├── web-defense-ai V2.code-workspace
├── main.py                           # Crew y agente analista
├── pipeline.py                       # Ejecución periódica
├── sync_logs.ps1
├── requirements.txt
├── compose.lab.yaml                  # DVWA y Mailpit aislados para fase 6
└── docker-compose.yml                # Compose heredado, sin cambios por esta preparación
```

Se conservan los nombres de módulos, rutas de datos y contenedores para mantener su compatibilidad. La interfaz Next.js vive en `frontend/` y consulta Flask mediante `/api/v1`; no accede a Docker, secretos ni archivos brutos.

## Capturas de referencia

La [guía de instalación Windows y Linux](docs/INSTALACION_AUTOALOJADA.md) utiliza
un instalador Python común y comandos de arranque para ambos sistemas.
La [matriz de compatibilidad](docs/PORTABILIDAD_WINDOWS_LINUX_2026_10_07.md)
pasó posteriormente en [Windows y Ubuntu 24.04](docs/VALIDACION_CI_2026_10_12.md).
El [ensayo guiado Parrot](docs/VALIDACION_PARROT_2026_10_12.md) acredita después
instalación y lectura en esa VM, incluido el arranque/proxy Next.

El [endurecimiento del retorno local](docs/ENDURECIMIENTO_RETORNO_LOCAL_2026_10_07.md)
incorpora recursos Flask locales con licencias e integridad verificadas, elimina
fuentes/CDN externos y añade CSP y protección contra marcos. Incluye pruebas y
límites de la política aplicada a Flask y Next.

Estas imágenes corresponden al dashboard Flask anterior y pueden mostrar la denominación previa. La nueva base visual V2 está en `frontend/`; las capturas se actualizarán cuando la interfaz conectada quede validada.

![Dashboard anterior](screenshots/screenshot-1-dashboard.png)

- [Dashboard con inyección de comandos](screenshots/screenshot-1a-dashboard.png)
- [Arquitectura del laboratorio](screenshots/screenshot-2-architecture.png)
- [Timeline](screenshots/screenshot-5-timeline.png) y [timeline con varias categorías](screenshots/screenshot-5a-timeline.png)
- [Reporte](screenshots/screenshot-3-report.png) y [otro reporte](screenshots/screenshot-3a-report.png)
- [Notificación Telegram](screenshots/screenshot-4-telegram.png) y [detalle de otra notificación](screenshots/screenshot-4a-telegram.png)

## Autor y ámbito de uso

**T3r0S3c** — Proyecto de portfolio en ciberseguridad.

[Repositorio de origen](https://github.com/EnriqueForte/web-defense-ai) · [GitHub del autor](https://github.com/EnriqueForte) · [LinkedIn](https://linkedin.com/in/enriqueforte)

Proyecto para laboratorio y aprendizaje. DVWA es intencionadamente vulnerable: mantener el laboratorio aislado y trabajar únicamente sobre sistemas autorizados.

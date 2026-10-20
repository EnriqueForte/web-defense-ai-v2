# Historial del plan de agentes — conservado el 20/10/2026

Registro histórico de planificación y seguimiento previo a la consolidación.
Las afirmaciones de pendiente o activación describen cada momento y no
sustituyen el [plan vigente](PLAN_AGENTES_TAREAS.md) ni sus criterios de cierre.

## Estado inicial y cronología

Revisión inicial: 26 de septiembre de 2026. Estado al 01/10/2026: fases 0–6 completadas; fase 6 cerrada anticipadamente con diez ciclos integrados, medición local, retorno a Flask y 14 h 11 min 46 s saludables. No se alcanzaron las 24 horas ni se generó el resumen automático; ver [FASE_6_PILOTO.md](FASE_6_PILOTO.md). El usuario aceptó esa evidencia parcial para activar localmente en fase 7 el conmutador reversible, que sigue apagado por defecto. Las mejoras A-01–A-05 del motor siguen separadas y pendientes. Todo el desarrollo se realiza en Codex y VSCode permite revisar el mismo proyecto local.



Estado posterior de entrega 6, 06/10/2026: integración A-05 implementada por
conmutador reversible, 179 pruebas y seis escenarios CrewAI aislados aprobados.
El primer análisis real falló por autenticación; tras corregir el adaptador,
la repetición autorizada falló con ValueError (dos llamadas, 50,031 s), sin informe.
A-05 sigue abierta por evaluación/aceptación; modo operativo `legacy`.
[Registro y retorno](ENTREGA_6_INTEGRACION_EVALUACION.md).
Diagnóstico por etapa añadido después: 186 pruebas y nueve escenarios CrewAI
offline aprobados. Falta usarlo en un nuevo intento real autorizado para precisar
el ValueError; no inferir la causa a partir de las reproducciones sintéticas.
Intento real posterior con ese diagnóstico: respuesta vacía en detección,
una llamada/35,516 s, ValueError en agent_utils.py:417, sin publicación.
Falta precisar el origen del contenido vacío; A-05 sigue abierta.
Captura de finish_reason/modelo/tokens preparada después sin llamadas reales:
192 pruebas y 11 escenarios SDK offline aprobados. Pendiente prueba autorizada
con esos metadatos; no se cambia el límite ni el proveedor sin evidencia.
Intento posterior: corte `length` al límite de 2048 sin texto final; se preparó
ampliación a 8192 solo en el evaluador. Pendiente ejecución autorizada con el
ajuste; no se activó el motor ni se cerró A-05.
La repetición con 8192 obtuvo JSON, rechazado por IDs inválidos/duplicados,
y el reintento terminó por límite sin texto. Restricciones de ID alineadas
en esquema/instrucciones, revisión structured-prototype-3 y 13 escenarios
offline aprobados. Pendiente evaluar esa corrección; modo operativo legacy.
Ensayo real posterior exitoso: cuatro llamadas/57,625 s, publicación aislada
verificada. Cinco familias esperadas y un falso positivo sobre /index.html;
resumen de razonamiento del SDK discrepante. Calidad, métricas, representatividad
y aceptación siguen pendientes; no activar por una sola fixture exitosa.
Seguimiento posterior: falso positivo bloqueado por política observed-access-2,
incertidumbre preservada y uso conciliado con metadatos/SDK separados. 203 pruebas
y 15 escenarios SDK aislados aprobados, sin llamadas nuevas. Pendiente evaluar
structured-prototype-4 con el proveedor y completar aceptación representativa.
Verificación real del 07/10/2026 de esos cambios: éxito sin candidato normal,
cuatro llamadas/81 s, tokens conciliados. Ocho casos etiquetados preparados y
208 pruebas aprobadas; alcance de la ampliación preguntado al usuario.
El usuario autorizó los siete casos (máximo42); pasaron expectativas de familias
con 23 llamadas. Narrativa normal «1» y latencia475,829 s requieren revisión;
formato sin hallazgos corregido a Python y verificado offline, originales intactos.
211 pruebas y 15 escenarios offline aprobados. [Resultado del lote](EVALUACION_AMPLIADA_A05_2026_10_07.md).
Optimización posterior structured-prototype-5: tareas finales locales con detección
vacía validada, una llamada en el escenario SDK simulado. 212 pruebas y 17
escenarios offline aprobados; medición real/aceptación pendientes.
[Cambio y límites](OPTIMIZACION_A05_SIN_HALLAZGOS.md).
Medición posterior autorizada: normal pasó en 24 s/dos llamadas de detección,
clasificación/narrativa locales y guardas/hashes correctos. Límites 8192/60
alineados en main structured y evaluador; constructor SDK verificado offline.
Aceptación y activación siguen pendientes; comparación no acredita un p95.
Preparación operativa posterior: perfil piloto/.p2 común, preflight pasó sin
procesos nuevos, arranque explícito y manual/notificaciones desactivados.
223 pruebas en ambos entornos y 17 escenarios offline aprobados.
[Activación y retorno](ACTIVACION_LOCAL_A05.md): aceptación y arranque completados
después; worker online, cuatro rutas API HTTP 200, sin nuevos jobs. Salud
unavailable por ausencia del primer informe structured; observación y prueba
real del coordinador pendientes.
El primer job del coordinador se autorizó y completó después: succeeded en
157 s, publicación/histórico/API válidos y salud ok, manual y notificaciones
apagados. [Registro y límites](PRIMER_ANALISIS_COORDINADOR_A05.md).
Quedan observación operativa y aceptación final; A-05 no se cierra por un job.
Estabilización posterior R-14/R-18: refresco por identidad de publicación,
lecturas validadas/acotadas y sondeos sin solapamiento por canal implementados;
14 grupos UI, tipos/lint y contratos reales aprobados, sin nuevas llamadas LLM.
[Registro de lecturas y límites](ROBUSTEZ_LECTURAS_2026_10_07.md).
Objetivo de cierre aclarado: código distribuible por GitHub para instalaciones
propias. [Endurecimiento y pendientes de distribución](ENDURECIMIENTO_DISTRIBUCION_2026_10_07.md)
implementa hosts/cuerpo/errores locales y defaults/exclusiones seguros; 232 Python
aprobados. Clonación limpia final, diagnóstico y publicación no se declaran hechos.

Estado posterior de entrega 5, 06/10/2026: A-01–A-04 completadas como
componentes aislados, con reglas/preparación, reportes deterministas y
publicación generacional. [Registro de A-03/A-04](ENTREGA_5_PREPARACION_PUBLICACION.md).
El flujo operativo sigue intacto; A-05 pendiente de evaluación e integración.

Estado posterior de entrega 4, 06/10/2026: A-01/A-02 completadas solo en
alcance aislado. El flujo operativo no cambia. Registro en
[Contratos y prototipo](ENTREGA_4_CONTRATOS_PROTOTIPO.md); siguientes A-03–A-05.
Los estados de entregas anteriores de esta sección son históricos.

Estado actualizado al 06/10/2026: F7-01 cerrada en alcance local reversible,
con confirmación del usuario de las cuatro vistas, retorno ensayado y respaldo
verificado. Se conserva Flask. No se completaron siete días sugeridos ni
monitorización continua; [evidencia y límites](ENTREGA_3_OPERACION_CIERRE_LOCAL.md).
A-01–A-05, transición del entorno operativo y aviso braces siguen pendientes.
Los estados anteriores fechados se conservan como seguimiento histórico.

Seguimiento del 06/10/2026: el rediseño SOC UI 1–8 y el zoom real al 200 %
están cerrados según su acta. Se completó la entrega 1 de seguridad y línea base
de [la revisión integral](REVISION_INTEGRAL_2026_10_06.md); cambios y aceptación
en [su registro](ENTREGA_1_SEGURIDAD_LINEA_BASE.md). F7-01 y A-01–A-05 siguen
pendientes de su propia evidencia y alcance. Los resultados históricos de las
tablas siguientes se conservan con sus fechas.

La entrega 2 también tiene implementación y verificaciones completadas:
[dependencias y ejecución reproducible](ENTREGA_2_DEPENDENCIAS_EJECUCION.md).
Conserva la excepción de braces sin parche publicado y las cuatro diferencias
de la `.venv` operativa. No activa nuevas fases ni cierra la observación F7-01.

Las fases 0–4 se completaron en Codex sin crear subagentes de desarrollo. Véanse
[línea base](FASE_0_LINEA_BASE.md), [API de lectura](FASE_2_API_LECTURA.md) y
[base visual](FASE_3_BASE_VISUAL.md). La [fase 4](FASE_4_LECTURA_CONECTADA.md)
conectó Next.js con la API Flask en modo lectura.


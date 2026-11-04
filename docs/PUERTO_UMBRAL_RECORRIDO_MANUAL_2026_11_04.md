# Recorrido manual V2 y Puerto Umbral — 04/11/2026

Estado: **recorrido funcional representativo de principio a fin completado a
su alcance observado**, según capturas aportadas por el propietario en Parrot.
La petición nueva de probar la aplicación, el seguimiento y el análisis autoriza
este recorrido posterior a los cierres por alcance del 03/11. No reactiva
automáticamente sus suites, corpus o comprobaciones omitidas.

## Secuencia y resultados recibidos

| Etapa | Evidencia observada |
| --- | --- |
| Fuente corregida | Captura manual disponible del 04/11, inicialmente 94 líneas. El error de seguimiento visible al principio pertenecía a la sesión del 02/11; no se operó Docker para corregir ese mensaje histórico |
| Seguimiento | Sesión solicitada con intervalo de 5 segundos y duración de 5 minutos. Capturas sucesivas muestran 10 ciclos sin cambios; después 38 ciclos/1 snapshot nuevo/37 sin cambios; finalmente sesión terminada por duración con 49 ciclos/1 snapshot/48 sin cambios, último ciclo 20:07:39 Madrid |
| Uso normal SQL corregido | Ejecución con prefijo `45bda3c6311c`, variante 1, `COMPLETED`, una petición y una línea Apache correlacionada. HTTP 200 devuelve la carga normal `UM-1284`; la consulta a `/mercancias` busca «navegación» |
| Incorporación al log | La petición normal aparece el 04/11 a las 19:05:44 UTC, 20:05:44 Madrid. La copia pasa de 94 a 95 líneas; el seguimiento registra un snapshot nuevo |
| Primer análisis manual | Trabajo `0a8e4ed1b569…`, `succeeded / finished`; informe publicado a las 20:10:47 Madrid. Selección de 30 líneas de 95, con 65 omitidas y cero hallazgos. No permite afirmar benignidad de todo el log o evaluar falsos positivos |
| Intento SQL vulnerable | El propietario ejecuta el modo vulnerable, aunque el paso guiado proponía corregido. Run con prefijo `ac029c2f83d5`, variante 1, `COMPLETED`, una petición/línea correlacionada. La respuesta HTTP 200 incluye el señuelo reservado `UM-9000`: efecto funcional observado en esa respuesta |
| Alineación de fuentes | V2 seguía leyendo la fuente corregida y su última línea era la consulta normal. Tras arrancar con `--lab-mode vulnerable` y capturar, muestra fuente vulnerable disponible, 26 líneas y la petición SQL con `OR` y `1=1` codificados, a las 19:19:40 UTC / 20:19:40 Madrid. No se repite el intento |
| Segundo análisis manual | Arranque con `--lab-mode vulnerable --enable-manual`. Trabajo `b12709abd521441a90e47b8912e46a70`, `succeeded / finished`; informe publicado a las 20:26:48 Madrid. Selecciona 26/26 líneas, cero omitidas y clasifica dos grupos altos con estado «Requiere investigación» |
| Amenazas | Sin filtros, muestra SQLi en línea 26, 04/11 a las 20:19:40 Madrid, y Command Injection en línea 7, 02/11 a las 00:29:56 Madrid. Eventos recientes muestra la petición SQL del 04/11 con HTTP 200 |
| Retorno a lectura | La última captura muestra ejecutor no disponible, solicitudes manuales desactivadas, botón Iniciar análisis inactivo y el nuevo trabajo `b12709abd521…` conservado como exitoso. La tabla de amenazas conserva ambos grupos |

El grupo Command Injection corresponde a una petición anterior del
01/11 a las 23:29:56 UTC; no es otro ataque generado en este recorrido.
El hallazgo SQLi de línea 26 coincide en tipo, petición y fecha con el intento
vulnerable recibido. El informe clasifica el indicador; el efecto sobre el
señuelo está acreditado por la respuesta del laboratorio, no por el access.log.

La prueba de seguimiento con tráfico nuevo corresponde a la consulta normal
en modo corregido. El intento vulnerable posterior se incorpora mediante
captura manual de su fuente, después de terminar aquella sesión; no se afirma
que el seguimiento capturó ese intento mientras estaba activo.

## Qué queda comprobado en este recorrido

- Captura de la fuente, seguimiento activo, incorporación de una petición
  nueva y finalización por duración con contadores conservados.
- Separación efectiva de la fuente corregida y la vulnerable: cambiar solo
  el selector del panel no cambia el log que consulta V2.
- Solicitud manual, finalización exitosa y publicación/lectura del informe,
  tanto con resultado vacío como con hallazgos referenciados.
- Presentación de SQLi en eventos recientes y en la clasificación del informe;
  distinción entre actividad nueva y un hallazgo procedente del historial.
- Retorno a lectura con análisis deshabilitado y resultado nuevo conservado.

## Límites de la evidencia

Pausa y reanudación se guiaron, pero no se recibió una captura del estado
«Pausado» con estabilidad de contadores durante la pausa. No se atribuye una
verificación independiente de ese intervalo ni se pide repetirlo. La ausencia
de auto-resume del seguimiento está observada tras el primer retorno a lectura;
la última captura acredita el retorno del ejecutor a lectura, sin mostrar un
nuevo estado del seguimiento.

La configuración mostrada selecciona Groq y `groq/openai/gpt-oss-120b`.
Se observan dos trabajos de análisis terminados; no se revisan recibos de
transporte, número de llamadas, tokens, coste, cuota o posibles fallbacks.
La selección configurada no acredita por sí sola el modelo efectivo de cada
llamada. No se solicita otro análisis para documentar estos datos.

El agente guía y registra las capturas; no accede a la VM ni ejecuta casos,
servicios, modelo o suites. No se recalculan hashes, crean respaldos o modifican
JSON históricos. No se identifica aquí el commit efectivo de la instalación
Parrot ni se acredita integridad independiente de sus archivos.

Este recorrido no es una evaluación del corpus F5, medición general de
precisión/recall, cobertura de todas las familias, rotación real o aceptación
global del proyecto. F4/F5/F6 conservan sus cierres por alcance y F7 su matriz
aceptada, según el [registro de decisiones](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md).
Los originales F5 sin localizar y las verificaciones omitidas no cambian de
estado por estas dos observaciones. No se realizan nuevas ejecuciones por
redactar el acta; su publicación Git queda separada.

## Validación posterior del arranque unificado — entrega 7ecfcf1

El propietario autoriza publicar y validar en Parrot la simplificación de
arranque y el selector de fuente. La publicación de
`7ecfcf150d8cfb9b42fcc0bbf851a2cce7546433` se verificó en remoto antes de
guiar la actualización. Capturas de Parrot acreditan pull fast-forward,
`HEAD/main/origin` en `7ecfcf1` y build `--webpack` terminado, incluidas
TypeScript y generación de rutas. No se repiten por esta recepción.

| Comprobación del recorrido unificado | Resultado recibido por capturas |
| --- | --- |
| Arranque habitual sin opción manual | Resumen muestra ejecutor activo y solicitudes manuales habilitadas; conserva el trabajo anterior `b12709abd521…` |
| Selección y captura con ejecutor esperando | Fuente de V2 Vulnerable, captura disponible de 26 líneas a las 21:12:24 Madrid, sin cerrar V2 para habilitar captura |
| Seguimiento con ejecutor activo | Estado Siguiendo logs, intervalo 5 s y duración solicitada 5 min; cinco ciclos válidos, cero snapshots nuevos y cinco sin cambios |
| Solicitud de análisis durante seguimiento | Tras guiar una pulsación sin parada manual previa, nuevo trabajo `ed972c941c08…` terminado como `succeeded / finished`; seguimiento Detenido. La última captura de seguimiento corresponde a una sesión posterior, con dos ciclos, cero snapshots nuevos y dos sin cambios, último ciclo 21:23:02 y expiración prevista 21:27:56. No se suma a la sesión anterior de cinco ciclos |
| Informe nuevo | `report.md` publicado a las 21:23:32 Madrid, análisis `ed972c941c08…`, 26/26 líneas y cero omitidas; dos grupos ALTA, SQLi y Command Injection, ambos con estado Indicador observado. Es el resultado de esta ejecución, no se fuerza a repetir el estado Requiere investigación del informe anterior |
| Cambio posterior a la fuente corregida | Selector Corregido y captura disponible de 95 líneas a las 21:26:31 Madrid; el ejecutor sigue activo y el último trabajo sigue siendo `ed972c941c08…`. Cambiar y capturar no solicita otro análisis |
| Conservación visible | El catálogo muestra el informe actual y publicaciones anteriores. Incluye una fila con prefijo `3409292…` a las 21:18:47; no se revisan sus recibos ni se atribuye un origen automático/manual o consumo a partir de esa fila |

**Recorrido manual del arranque unificado y cambio de fuente completado a su
alcance observado.** La selección vulnerable alcanza al análisis del ejecutor:
el informe nuevo procesa sus 26 líneas; después la captura corregida muestra
sus 95 líneas. La secuencia se guía dentro de la misma sesión, sin solicitar
reinicios para cambiar de función o fuente; no se inspeccionan procesos de la VM.

Las trece regresiones preparadas no se ejecutan por esta validación. No se
prueban todos los conflictos, corrupción del selector, errores de origen,
concurrencia o plataformas; la recepción no es una evaluación global F5 o
rotación real. No se infieren número de llamadas LLM, tokens, costes o modelo
efectivo de cada transporte. Se registra lo recibido sin solicitar nuevos
análisis, capturas, snapshots, copias, suites o servicios. Los cierres de fases
y sus limitaciones siguen vigentes. Esta ampliación del acta permanece local
hasta una publicación Git solicitada por el propietario.

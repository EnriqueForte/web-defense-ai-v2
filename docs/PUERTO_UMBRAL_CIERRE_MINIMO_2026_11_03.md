# Cierre mínimo F6 y operación — 3 de noviembre de 2026

Objetivo del propietario: finalizar el desarrollo el jueves **5 de noviembre**.
Se mantiene el proyecto F0–F7 con los ajustes expresos de alcance registrados. Esta fecha no acepta
criterios pendientes ni autoriza nuevos escenarios, suites o llamadas al modelo.

## Decisión más reciente: matriz F7 aceptada y F4/F5 cerradas

El propietario acepta la matriz F7 actualizada y ordena cerrar F4/F5 si requieren
pruebas. Se registran **F4/F5 cerradas por decisión expresa de alcance**, con
rotación/discontinuidad real no verificada y evaluación del detector no realizada.
No se solicitan más ensayos o búsquedas de originales F5; preparación, pruebas
y desarrollo/validación adicional para esa evaluación quedan fuera de esta entrega.
F6 conserva su cierre previo con omisiones. La matriz F7 queda aceptada en su
alcance educativo, sin detección completa OWASP. Queda consolidación/aceptación
final del conjunto. El [registro de decisiones](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md)
prevalece sobre los pendientes históricos de las secciones siguientes.

## Decisión vigente del propietario: F6 cerrada sin más pruebas

El 03/11 el propietario indica que las pruebas bloquean la conversación y
decide: «la F6 la cerramos y no lo haremos». **F6 queda cerrada por decisión
expresa de alcance**, con la evidencia ya recibida y las limitaciones conocidas.
No se solicitan más recorridos, comprobaciones o regresiones de F6 ni se
reformulan ejercicios para sustituir los omitidos.

Bitácora y Preferencias vulnerables, el resultado vulnerable de Baliza y la
regresión F6 restante quedan **omitidos/no verificados**, sin puntuarlos como
superados. La revisión de contrato realizada conserva su alcance estático;
no se añade una lectura de recibos VM para cerrar la fase. Cargas/Atraque y
los controles corregidos mantienen sus resultados observados.

El cierre por decisión no certifica cumplimiento íntegro de todos los criterios
F6 originales y no acepta automáticamente F4, F5, F7 o el proyecto completo.
La instrucción vigente es continuar trabajo sin ejecución de pruebas. El
siguiente bloque documental es la [revisión F5 sin ejecución](PUERTO_UMBRAL_EVALUACION_F5_2026_11_02.md).
Las propuestas F6 inferiores quedan como antecedentes, sin trabajo pendiente.

Esta revisión concreta comportamientos distintos, no una cuota de variantes.
La base publicada es `7d4d10f1d3a0c26f04fdb14f7766a57a01e23ba2`, con cinco
regresiones de perfiles correctas y sus límites registrados. El propietario
confirma la actualización en Parrot; no se solicita repetir pull o build.

## Qué no se repite

Se reutilizan los normales y negativos corregidos F6, CSRF corregido en
navegador, Atraque corregido con permiso consumido y comparación Cargas
vulnerable/corregida. También quedan recibidos el bloque representativo de
comandos, medición API, parada/reinicio de fuente, conservación del snapshot,
interfaces, lanzador y regresiones de perfiles. No se repiten para redactar actas.

## Antecedente: candidatos F6 y recepción previa al cierre

**Recepción del 03/11:** el propietario autoriza el único recorrido Atraque
vulnerable/Intento/variante 1, con lectura y conservación de auditoría V2.
La captura recibida muestra `COMPLETED`, ejecución con prefijo `b2df9053`,
HTTP 200 y respuesta real `previous_state: pending`, `permit_state: consumed`.
Constan tres peticiones, tres líneas Apache correlacionadas, dos eventos de
aplicación y dos referencias HTTP; V2 no consultado por el ejecutor.
La captura V2 posterior muestra la misma ejecución en modo vulnerable, dos
eventos, observación **Atraque ejecutado sin aprobación**, componente `docking`,
actor `estibador.demo` y recurso `dock-1`. El mensaje confirma copia conservada
en V2 sin solicitar análisis. **Recorrido autorizado completado**: efecto,
lectura y copia observados por capturas; comparación puntual con rechazo
corregido previo. No se repiten caso, copia, exportación, hash o respaldo.
No es aceptación F6 global ni lectura independiente de bytes de la VM.
El aviso rojo superior corresponde a la sesión de seguimiento fallida del
02/11 a las 18:00:15; no acredita fallo de esta auditoría o salud actual de
la fuente. No se opera la pasarela por ese mensaje histórico.

| Orden | Recorrido mínimo propuesto | Qué distinguiría | Evidencia necesaria |
| --- | --- | --- | --- |
| 1 | Atraque, vulnerable, intento, variante 1 | Consumo del permiso `dock-1` estando pendiente, comparado con rechazo corregido ya recibido | Cuerpo real con `previous_state: pending` y `permit_state: consumed`, HTTP 200; evento de aplicación de mismo run/modo/actor/recurso, observación V2 y copia conservada |
| 2 | Bitácora, vulnerable, intento, variante 1 | Persistencia y renderizado posterior, frente a codificación corregida ya recibida | El texto almacenado y su renderizado no bastan para afirmar ejecución: se requiere el marcador confirmado en navegador con iframe/nonce propios; auditoría distingue renderizado de ejecución |
| 3 | Preferencias, vulnerable, intento, variante 1, recorrido del navegador | Cambio de estado con sesión ficticia del navegador desde el otro origen, comparado con el corregido recibido | Control normal y formulario cruzado de la misma preparación; evento con `auth_source: cookie`, `origin_relation: cross`, `outcome: updated`, confirmación del panel y copia V2; la sonda HTTP del ejecutor sola no acredita CSRF de navegador |

Las propuestas Bitácora y Preferencias quedan retiradas del trabajo pendiente
por la decisión de cierre indicada arriba. Se conserva la tabla para explicar
qué evidencia no se obtuvo, sin ejecutar esos recorridos. El agente no opera la VM.

**Baliza vulnerable queda omitida del cierre F6.** La fila `525a2076b8ae` no aporta un
resultado funcional evaluable. Su perímetro y los controles corregidos tienen
evidencia, pero no se afirma un positivo recibido. El cierre no la reactiva
ni sustituye su criterio por otro ejercicio.

Se eligió primero Atraque porque usa el recorrido predefinido de estado
sin comprobación JavaScript en navegador. Según el ejecutor revisado, variante
1 usa dos peticiones funcionales (sesión y operación) y una de auditoría:
tres peticiones del ejecutor y dos eventos de aplicación como expectativa del
código, confirmada después por la recepción indicada arriba. La ejecución restablece el target avanzado del
modo elegido; se conserva la evidencia anterior. Por ello no se preparan dos
ejercicios de navegador a la vez. V2 debe seleccionar la misma fuente vulnerable;
cambiar solo el selector del panel no cambia la fuente de V2.

## Revisión del contrato F6 realizada por código

Se leen, sin importarlos ni ejecutarlos, `advanced_target.py`,
`audit_contract.py`, `controller.py` y `application_audit.py`:

- El target emite identidad, acción, recurso, decisión y estado observados.
  El contrato exige campos exactos: no admite `expected_effect`, `kind`,
  contraseñas o tokens como campos adicionales de eventos.
- `mode` identifica la fuente de aplicación declarada; no se confunde con el
  veredicto esperado del evaluador. El lector valida identidad del run, esquema,
  modo y hash del archivo antes de aplicar reglas.
- Las observaciones de V2 se derivan de eventos y estados, no del
  `expected_effect` del catálogo. No se integran en el informe del modelo.
- El controlador redacta los tokens transitorios de las respuestas de sesión;
  los eventos excluyen cuerpos y credenciales. Un evento de renderizado crudo
  no acredita ejecución JavaScript y una sonda con bearer no acredita el
  recorrido de formulario con cookie del navegador.

Esto aporta trazabilidad de F6-AC4 por revisión de código, no una inspección
de todos los recibos de Parrot o una nueva evaluación LLM. Las cinco regresiones
de perfiles no cubren por sí solas el pipeline completo del MVP. La regresión
adicional debe justificarse por cambios reales, sin convertir el catálogo de
45/99 casos en una nueva obligación de repetir todo.

## Operación: qué falta realmente

Fuente revisada: `httpd.conf` escribe accesos en `/proc/self/fd/1`;
`capture_access_log` consulta `docker logs --tail 1000` del gateway seleccionado.
Compose declara logging `json-file`, `max-size: 5m`, `max-file: 3`.
Estos valores son configuración en código, no una nueva inspección de la VM.

`_transition` distingue línea añadida, ventana desplazada, cambio de fuente y
discontinuidad sin solapamiento; con una ventana limitada no atribuye una causa
concreta ni inventa offsets. La interfaz tiene mensajes para esos estados.
Revisión de código realizada, comportamiento real de rotación aún no observado.

Renombrar o truncar `.local-state/puerto-umbral/access.log` actuaría sobre la
copia de V2 y **no probaría rotación del origen**. No se propone ese atajo,
manipular archivos internos de Docker o llenar cinco megabytes con tráfico
para conseguir una captura. Una prueba aislada con contenido simulado podría
corroborar la clasificación de discontinuidad, pero no se presentaría como
rotación real en Parrot.

La decisión operativa queda resuelta posteriormente por el propietario:
cerrar F4 sin pruebas restantes. Rotación/discontinuidad real se conserva no
verificada y se retira el ensayo del trabajo de cierre; no se sustituye por
otro ejercicio ni se añaden comandos de escritura o nuevas sesiones.

## Calendario y límite de entrega

| Día | Trabajo acordado como prioridad, no autorización de ejecución |
| --- | --- |
| Martes 3 | Registro del cierre F6 por decisión expresa; revisión documental F5 y límites de evidencia, sin ejecutar pruebas |
| Miércoles 4 | Continuar revisión de documentación, manual de operación y matriz F7; conservar límites de F4/F5 sin nuevas pruebas |
| Jueves 5 | Congelar código, revisión final de documentación V2 y Puerto Umbral, decisión del propietario y publicación Git cuando se solicite |

F5 queda después cerrada por decisión expresa sin evaluación adicional;
originales sin localizar y métricas sin medir se mantienen como limitaciones,
sin búsquedas o ejecución nuevas. F7 está aceptada en su alcance educativo.
Las decisiones de fases están resueltas; resta la consolidación/aceptación
final de entrega. No se crea release o publicación de LinkedIn por este plan.

Referencias: [estado de entrega](PUERTO_UMBRAL_ENTREGA_2026_11_02.md),
[auditoría de criterios](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md),
[preparación F5](PUERTO_UMBRAL_EVALUACION_F5_2026_11_02.md),
[medición y recuperación F4](PUERTO_UMBRAL_MEDICION_F4_2026_11_02.md).

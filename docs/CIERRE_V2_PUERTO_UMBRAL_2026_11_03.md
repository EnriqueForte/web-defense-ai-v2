# Cierre de Web Defense AI V2 y Puerto Umbral para el 03/11/2026

Estado al 29/10/2026, Europe/Madrid: **desarrollo en curso; cierre F0–F7 solicitado,
todavía no aceptado**. El propietario quiere terminar antes del martes 3 de
noviembre para preparar su publicación en LinkedIn. Confirma expresamente que
incluye F6 y F7, además del MVP F0–F5. El objetivo de revisión final es el lunes
2 de noviembre. El calendario es una previsión, no una validación anticipada.

## Punto de partida comprobado

| Área | Evidencia disponible | Límite |
| --- | --- | --- |
| Distribución V2 | Repositorio público, versión local anterior v0.1.0; paquete F6/F7 publicado y remoto verificado en `cc363af` | No nueva release o CI atribuida a los commits `[skip ci]` |
| Puerto Umbral F1/F2 | Prototipo privado, cinco familias locales y dos modos | Corpus histórico 42/45; tres fallos de comandos preservados |
| F3, recorrido de integración | Un snapshot de 17 líneas, análisis Groq, publicación y lectura en V2 | No evaluación de los 45 casos |
| F4 | Inicio, pausa, reanudación, parada, vencimiento y reapertura sin auto-resume | Condiciones ampliadas y latencias individuales pendientes |
| F5, conservación | Copia y recuperación aislada de 66 archivos, SQLite e informe verificados en Parrot | Sin promover datos recuperados ni restaurar la VM completa |
| Interfaz | Nombre de fuente Puerto Umbral confirmado por el propietario | No revisión actual completa de móvil/teclado |
| F6/F7 | [Código de ampliación revisado y publicado](PUERTO_UMBRAL_F6_F7_2026_10_29.md), recibido y compilado en Parrot; lanzador listo y panel visible informando 14 contenedores | Sin inspección Docker independiente, vista Actividad V2 actual o aceptación funcional de escenarios |

El [estado consolidado](PUERTO_UMBRAL_ESTADO_ACTUAL_2026_10_26.md), el
[acta del análisis y recuperación](PUERTO_UMBRAL_ANALISIS_ACOTADO_2026_10_27.md)
y la [evaluación histórica F5](PUERTO_UMBRAL_F5_2026_10_27.md) contienen los
resultados originales. Este documento no reemplaza sus denominadores ni
reescribe los JSON históricos.

## Trabajo de cierre, en orden

| ID | Trabajo | Evidencia necesaria para cerrarlo | Estado |
| --- | --- | --- | --- |
| DOC-01 | Sincronizar README, arquitectura, inicio y plan V2 | Enlaces válidos y distinción entre estado actual e historia | Actualizado localmente; revisión final conjunta pendiente |
| F6-01 | Contrato de auditoría de aplicación y correlación | Actor, recurso, acción, decisión y secuencia; sin claves, tokens o etiquetas esperadas del corpus | Código preparado; ejecución pendiente |
| F6-02 | XSS almacenado, IDOR, CSRF, SSRF y permisos de atraque | Modos vulnerable/corregido, controles normales, reset, evidencia HTTP/negocio y prueba de navegador cuando corresponda | Código preparado; ejecución pendiente |
| F7-01 | Ejercicios para configuración, suministro, criptografía, integridad, registro y excepciones | Catálogo con tipo de ejercicio explícito y artefactos ficticios verificables | Código preparado; ejecución pendiente |
| EVAL-01 | Resolver o conservar con causa los fallos del corpus actual | Resultados actuales trazables; el histórico 42/45 permanece intacto | Pendiente de ejecución autorizada |
| EVAL-02 | Evaluar detección y falsas alarmas del corpus definido | Expectativas fijadas antes de puntuar, resultados por caso, presupuesto, modelo y uso | Pendiente de alcance/budget de nuevas llamadas |
| OPS-01 | Condiciones ampliadas F4 y regresión de aislamiento | Observaciones reproducibles de rotación, truncado, fallo, cuotas y ausencia de actividad automática | Pendiente de ejecución autorizada |
| UX-01 | Lectura final, móvil, teclado y exportación de evidencias | Comprobación del producto actual y ausencia de contenido sin fuente | Pendiente |
| DOC-02 | Revisar documentación completa de V2 con el propietario | README/manual/estado/catálogo/actas coherentes y enlaces comprobados | Después de terminar el laboratorio |
| ACC-01 | Decisión de cierre y alcance de comunicación | Criterios F0–F7 revisados expresamente, limitaciones pendientes visibles | No aceptado |

F6 y F7 pueden prepararse en código sin declarar superado su requisito de
aceptación del MVP. Las dependencias del PRD siguen vigentes para el cierre.
La fecha objetivo no autoriza declarar completado un criterio no observado.

El propietario elige después mantener solo desarrollo y revisión de código;
decidirá las pruebas más adelante. No se interpretará la petición de todas las
fases o la fecha de LinkedIn como permiso para iniciar suites o llamadas LLM.
La primera preparación de F6/F7 y la sincronización documental pasan revisión
estática de sintaxis, tipos, configuración y enlaces; no se confunde esa revisión
con los recorridos de aceptación que aún deben decidirse.
El propietario autoriza a continuación el paso 1 de revisión de código. Se
completa localmente con correcciones de concurrencia, ventana manual,
validación/lectura acotada y conservación de evidencias, registradas en el
[acta F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md). Los criterios operativos siguen
pendientes. Después el propietario autoriza commit/push del paquete revisado
con `[skip ci]`; su identidad queda en el commit que incorpora la nota de
distribución del acta F6/F7. Publicar no ejecuta la validación ni actualiza la VM.
La publicación se completa en `cc363af`, con remoto coincidente y árbol limpio.
El propietario autoriza después el paso 3 y sus capturas confirman ese commit
en Parrot y la compilación completa del frontend con Webpack y TypeScript.
**Paso 3 completado**; no acredita todavía arranque de V2, construcción o
disponibilidad de la topología nueva, escenarios o métricas del detector.
El siguiente bloque de arranque y revisión de pantallas queda autorizado por
el propietario, limitado a disponibilidad y navegación en el perfil corregido;
su resultado permanece pendiente. No autoriza recorrer casos ni repetir LLM.
Las capturas siguientes acreditan salida «Consola lista» y acceso al panel de
Puerto Umbral, que informa 14 contenedores. El alcance de disponibilidad del
panel queda observado; falta la captura de Actividad V2 y no se validan casos.
La petición adicional de autoría en cabecera se implementa en HTML/CSS local;
su recepción en Parrot y revisión visual quedan pendientes de distribución.

## Calendario propuesto

| Fecha | Prioridad de trabajo |
| --- | --- |
| Jueves 29/10 | Documentación V2 al día y contrato de ampliación F6 |
| Viernes 30/10 | Escenarios F6 y recibos de estado/identidad |
| Sábado 31/10 | Ejercicios F7 y matriz de categorías/evidencias |
| Domingo 01/11 | Validación acotada, correcciones y métricas si su ejecución se autoriza |
| Lunes 02/11 | Congelación de alcance, revisión del laboratorio y documentación V2 con el propietario |
| Martes 03/11 | Publicación del propietario en LinkedIn con afirmaciones respaldadas |

Si una validación no está disponible a tiempo, se registrará como pendiente y
se revisará la fecha o el alcance con el propietario; no se omitirá para dar
el proyecto por terminado. Este plan no configura tareas programadas ni
publica mensajes en LinkedIn.

## Límites de ejecución que siguen vigentes

La única autorización de análisis Groq ya se consumió. No se inician llamadas,
escenarios, suites o recorridos automáticos nuevos por este documento. Antes
de ejecutar el siguiente bloque se necesita concretar su alcance y, si usa
modelo, número máximo de solicitudes, proveedor/modelo y presupuesto. No
solicitar ni publicar claves; utilizar la configuración propia de Parrot.

Los escenarios permanecen locales y confinados. El prototipo privado de Sites
mantiene su identidad y audiencia; no se despliega el backend vulnerable allí.
F7 distinguirá ejercicio HTTP real, demostración con datos ficticios y revisión
de artefactos. Un mapa educativo de diez categorías no acredita detección de
todas ellas por V2 ni explotación real de todos los ejemplos.

## Qué respaldará la comunicación final

Podrán describirse las funciones implementadas y los recorridos observados,
con sus versiones y límites. Los porcentajes de detección solo procederán de
la evaluación identificada del detector; no del corpus funcional 42/45.
La nueva ampliación no será una actualización de la release v0.1.0 hasta que
se decida expresamente una entrega identificada. El texto de LinkedIn y la
revisión documental final se prepararán tras cerrar el laboratorio, como
solicita el propietario.

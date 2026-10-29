# Puerto Umbral — estado consolidado y cierre de la ronda manual

Fecha: 26/10/2026, Europe/Madrid.

## Actualización vigente del 29/10/2026

Objetivo vigente: cerrar **todas las fases F0–F7 antes del martes 03/11**, según
respuesta expresa del propietario. La autorización actual sigue limitada a
desarrollo y revisión de código; las pruebas se decidirán después. El
[plan de cierre de V2/laboratorio](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md) ordena
el trabajo y la revisión final de documentación con el propietario. La
[ampliación F6/F7](PUERTO_UMBRAL_F6_F7_2026_10_29.md) tiene fuente preparada
sin ejecución o aceptación: no se convierte una fecha objetivo en cumplimiento.

El ejecutor acotado se publicó en `1403f8d` y la corrección de nombres de fuente
en `9e71c0c`. Ambas publicaciones se verificaron contra main remoto y el árbol
local quedó limpio en sus respectivos cierres. El propietario confirma ahora
que comprobó la corrección en Parrot; es una confirmación del propietario, sin
una nueva captura de HEAD, compilación o procesos.

El recorrido **snapshot guardado → análisis Groq → publicación → informe visible
en V2** está comprobado para el análisis
`f5b674c867994aeba3beeb4a638d7a33`: 17 líneas de 17, tres llamadas, 8150 tokens
reportados y cuatro grupos que requieren investigación (tres altos y uno medio).
El coste real del proveedor sigue sin medirse. El
[acta del análisis](PUERTO_UMBRAL_ANALISIS_ACOTADO_2026_10_27.md) conserva los
identificadores, hashes, alcance y origen de la evidencia. La autorización de
ese único análisis está consumida y no se repite.

Se publican después en `c8abcaf` dos ajustes: incluir `manual-validation.json`
en la lista de respaldo/restauración y distinguir la ausencia de publicación
(`missing`) de una publicación inválida (`error`). Las capturas posteriores
muestran ese recibo en la selección, lectura conectada e informe conservado.
No se borra el informe para ensayar la rama de ausencia.

El propietario crea una copia de 66 archivos sin faltantes y ejecuta el
restaurador independiente en un árbol nuevo. Ambas salidas devuelven
`verified: true`; la recuperación verifica SQLite, un trabajo `succeeded`,
ninguna entrega y la misma generación del informe observado. El recorrido
básico de respaldo y recuperación aislada del perfil queda completado según
esas capturas. No se promovieron datos al estado vivo ni se arrancó la copia
recuperada; no constituye restauración completa de la VM. Los destinos y el
alcance se conservan en el acta enlazada, sin inspección independiente del
agente sobre los archivos de Parrot.

Quedan abiertos la calidad del detector sobre los 45 casos, los tres fallos
funcionales históricos, las condiciones ampliadas de F4, cualquier promoción
o arranque de datos recuperados y la aceptación global del MVP. La continuación del desarrollo no
acepta esos criterios ni autoriza escenarios, suites o nuevas llamadas al LLM.

## Cronología anterior

Actualización del 27/10: [F4 implementada](PUERTO_UMBRAL_F4_2026_10_27.md), sin
activar seguimiento durante su desarrollo. El propietario autoriza después su
publicación y revisión operativa guiada con logs existentes. La ronda anterior
de escenarios sigue finalizada; no se reabren sus casos aplazados.
La ronda operativa básica F4 queda después completada mediante capturas del
propietario, incluida la reapertura sin reanudación automática. La aceptación
ampliada conserva sus pendientes; no se solicitan nuevos casos para este cierre.
El [bloque F5](PUERTO_UMBRAL_F5_2026_10_27.md) consolida después las evidencias
existentes y la documentación de entrega, sin nuevos ensayos o análisis. Su
evaluación del detector y la aceptación del MVP siguen pendientes.

El propietario da margen para terminar las pruebas y continuar con el trabajo
que no requiera nuevas ejecuciones. Se da por finalizada esta ronda manual:
no se solicitan más casos, capturas, suites ni análisis del modelo. Los pasos
propuestos anteriormente que aún no se realizaron quedan aplazados. Esta
decisión no constituye aceptación de los criterios de las fases pendientes.

## Evidencia disponible

La evidencia de Parrot procede de capturas de pantalla y de la confirmación
del propietario. El agente no tiene acceso operativo a la VM ni ha recibido
los archivos completos de recibos o snapshots para recalcular sus hashes.
La cronología y los detalles están en la [guía de Parrot](PUERTO_UMBRAL_PARROT_2026_10_26.md).

| Familia / control | Resultado observado en el laboratorio | Recepción visible en V2 | Pendientes |
| --- | --- | --- | --- |
| SQL, intento variante 1 | Vulnerable devuelve `UM-9000`; corregido devuelve una lista vacía | Peticiones de ambos modos visibles | Resto de variantes, recibos completos y análisis |
| SQL, búsqueda normal `Asteria` | Corregido devuelve `UM-1284` y `UM-1287`; también se observó la solicitud normal vulnerable | Búsquedas normales visibles | No generalizar al resto de entradas |
| XSS, intento variante 1 | Corregido codifica y muestra texto literal; vulnerable confirma ejecución mediante el marcador del iframe | Peticiones de ambos modos visibles | Resto de variantes; el recorte corregido no incluye su mensaje final de estado del navegador |
| Path traversal, intento variante 1 | Vulnerable devuelve el documento señuelo; corregido responde 403 con `document_not_authorized` | Peticiones de ambos modos visibles | Resto de variantes |
| Archivo público `atraque.txt` | Corregido responde 200 con el protocolo ficticio | Petición visible | No generalizar a todo el archivo |
| Comandos, intento variante 1 | Corregido responde 400 con `invalid_component` | Petición visible | Comparación vulnerable, uso normal y fallo histórico de creación de procesos |
| Autenticación | Sin nueva observación manual en Parrot | Sin nueva evidencia aportada para este escenario | Revisión aplazada |

Una petición en Actividad demuestra recepción del registro, no que el analizador
la haya clasificado. El estado HTTP tampoco demuestra por sí solo un efecto.
Las imágenes de fuente que muestran snapshot y SHA-256 acreditan que esos datos
se presentan en la interfaz; no sustituyen una comprobación de los archivos.

El primer corpus histórico conserva su resultado **42/45**, con tres fallos en
comandos. Esta revisión parcial no lo convierte en 45/45 ni descarta el fallo
histórico por haber observado un rechazo en el modo corregido.

## Estado de las fases

| Fase | Desarrollo y observación actuales | Estado de aceptación |
| --- | --- | --- |
| F1 | Prototipo privado publicado en Sites | Conservar el alcance del registro F1 |
| F2 | Cinco familias en código; revisión manual parcial de Parrot documentada | Abierta: cobertura funcional y verificaciones pendientes |
| F3 | Conector, perfil, API y vista de fuente implementados; captura y lectura observadas en ambos modos; un recorrido de snapshot guardado a informe visible completado después | Abierta: validación básica limitada a ese snapshot; errores, regresión y evaluación ampliada pendientes |
| F4 | Seguimiento publicado en 02d2638 y frontend compilado en Parrot | Ronda operativa básica completada, incluida reapertura sin auto-resume; aceptación ampliada pendiente |
| F5 | Archivo histórico de 45 entradas revisado offline, nueve observaciones manuales relacionadas, análisis acotado y respaldo/restauración aislada posteriores documentados | Revisión documental y recorridos básicos de integración y recuperación completados; evaluación del corpus y aceptación del MVP pendientes |

El frontend se compiló en Windows con Webpack. La evidencia posterior F4
acredita actualización a `02d2638`, compilación, acceso y cierre/reapertura en
Parrot. No se atribuyen IDs actuales de contenedores o una instalación limpia
a esas imágenes. El informe F5 mantiene separado el alcance de cada fuente.

La fuente anterior estaba publicada hasta `abab01d`, posterior a `fdffd08`.
El propietario autoriza después publicar F4 junto con las actas de esta ronda;
su identificación queda en el historial Git. No se crea una release ni se
atribuye nueva CI a esta publicación.

## Alcance F4 preparado el 26/10 (histórico)

Puede prepararse e implementarse sin ejecutar escenarios ni llamar al modelo.
Sus criterios de aceptación seguirán pendientes hasta una revisión posterior;
su desarrollo no cierra retroactivamente F2/F3.

Alcance previsto:

- Inicio explícito por el operador, con duración y frecuencia limitadas según
  el PRD; abrir una página o arrancar V2 no activa el seguimiento.
- Estados visibles de detenido, siguiendo, pausado, finalizado y error, con
  último ciclo válido y causa de parada diferenciados de ausencia de eventos.
- Captura de una sola pasarela elegida en el perfil. El selector de escenario
  del laboratorio no cambia esa fuente.
- Reutilizar snapshots inmutables y conservar el último válido ante fallo.
  Registrar checkpoint, modo y procedencia; no mezclar reinicios o cambios de
  origen sin señalarlos.
- Si no cambian los datos, no publicar duplicados ni crear trabajos nuevos.
- Excluir captura/seguimiento de operaciones incompatibles mediante el bloqueo
  existente. Pausar o detener debe impedir nuevas capturas.
- Mantener el análisis y las notificaciones separados y desactivados. El
  seguimiento solo actualiza evidencia; no solicita análisis automáticamente.

La preparación inicial pedía resolver cancelación durante una captura,
identidad del contenedor, rotación/truncado y conservación del checkpoint antes
de activar el seguimiento. El registro F4 del 27/10 enlazado al inicio describe
su implementación posterior. En el momento de aquella preparación aún no se
habían ejecutado ciclos F4. La ronda básica posterior está documentada; el
objetivo completo de latencia sigue sin medirse. F5 no habilita nuevos servicios.

## Conservación

Los recibos, snapshots, logs y datos existentes no se borran ni se reescriben.
No se modifica el Site alojado, el detector, las dependencias o la configuración
operativa por este cierre. Se mantiene la separación entre datos del laboratorio
y resultados esperados del evaluador. La [especificación original](PRD_PUERTO_UMBRAL_2026_10_26.md)
conserva sus criterios; las verificaciones aplazadas no se presentan como realizadas.

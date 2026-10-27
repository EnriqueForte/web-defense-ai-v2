# Puerto Umbral — estado consolidado y cierre de la ronda manual

Fecha: 26/10/2026, Europe/Madrid.

Actualización del 27/10: [F4 implementada](PUERTO_UMBRAL_F4_2026_10_27.md), sin
activar seguimiento durante su desarrollo. El propietario autoriza después su
publicación y revisión operativa guiada con logs existentes. La ronda anterior
de escenarios sigue finalizada; no se reabren sus casos aplazados.

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
| F3 | Conector, perfil, API y vista de fuente implementados; captura y lectura observadas en ambos modos | Abierta: recorrido snapshot → trabajo → informe, errores y regresión pendientes |
| F4 | Seguimiento local implementado el 27/10; controles, API y checkpoint; compilación correcta | Publicación y revisión guiada autorizadas; operación en Parrot aún pendiente de evidencia |
| F5 | Evidencia parcial organizada | Evaluación completa y aceptación pendientes |

El frontend se compiló previamente en Windows con Webpack. El propietario
confirmó el acceso a los servicios en Parrot y aportó las imágenes posteriores.
No se atribuyen a esas imágenes una compilación completa de Parrot, IDs de
contenedores o verificación del commit efectivo de la VM.

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
su implementación posterior. No se han ejecutado ciclos de F4 ni se ha medido su
objetivo de latencia. Tampoco se han habilitado servicios nuevos en este cierre.

## Conservación

Los recibos, snapshots, logs y datos existentes no se borran ni se reescriben.
No se modifica el Site alojado, el detector, las dependencias o la configuración
operativa por este cierre. Se mantiene la separación entre datos del laboratorio
y resultados esperados del evaluador. La [especificación original](PRD_PUERTO_UMBRAL_2026_10_26.md)
conserva sus criterios; las verificaciones aplazadas no se presentan como realizadas.

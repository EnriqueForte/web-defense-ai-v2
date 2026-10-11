# Tarjetas y gráfico tras análisis manual — 11/10/2026

El usuario confirmó que el análisis funciona y pidió revisar las tarjetas y el
gráfico circular. El nuevo trabajo manual `297cfc8a4c5d4eb2bdd0a81b409b3382`
figura `succeeded`, terminado a las 19:13:12 Madrid, con nueva publicación
`938dbff10379546b28f4269731cd4530f4e35c462343dfb05dd6bcad6da6b17b`.
La lectura de su resultado confirma prototype-8/report-4 y narrativa
`python_validated_facts`; no se ejecutó otro análisis para esta revisión.

## Hallazgo y significado de los datos

Flask y su proxy Next devuelven el mismo informe: **cinco grupos clasificados,
cuatro altos, uno medio, una IP observada**; el log tiene **68 coincidencias**.
Los conteos de severidad coinciden también con el JSON validado de la generación.
El informe anterior ya contenía cinco grupos con la misma distribución.
Por tanto, otro análisis puede conservar el total y el círculo **80 % alta /
20 % media** aunque cambien publicación, referencias y fechas de evidencia.
Las tarjetas del informe no suman cada petición del log ni todos los históricos.

No se acreditó un congelamiento indefinido o una caché propia del SVG. Los
componentes calculan sus valores desde `estado`. Sí había una demora evitable:
la consola lee el trabajo cada cinco segundos y el resumen cada quince, sin
enlazar el cambio de ingesta/publicación a la lectura del resumen.

## Corrección aplicada

`analysisSourcesChanged` detecta una ingesta nueva o una publicación exitosa
nueva. Al observarla, `Home` solicita otra lectura de estado, utilizando el
mismo mecanismo de actualización y cancelación existente. Así, tarjetas,
gráficos, tabla y catálogos reciben una captura común sin esperar otro ciclo
de quince segundos. Releer el mismo trabajo no inicia un bucle de refrescos.
Las respuestas abortadas siguen sin actualizar el estado.

El resumen muestra ahora fecha y referencia de **Informe actual**, y la tarjeta
explica que son grupos clasificados, sin acumular solicitudes o históricos.
Eso permite ver una publicación nueva aunque sus cifras no hayan cambiado.
No se alteraron estadísticas, contratos, clasificación, selección de evidencia,
conmutadores, modelo o matemáticas del gráfico.

El disparador depende de observar el cambio en el sondeo de trabajo de cinco
segundos. No es un evento push ni una promesa de actualización instantánea con
red lenta, pestaña oculta o fallo de lectura; se conservan pausa por visibilidad,
límites de lectura y recuperación periódica.

## Comprobaciones

- Lint, TypeScript y **15 grupos de regresión UI** aprobados.
- Build de producción Next 16.3.8 aprobado en copia aislada, con las mismas
  dependencias/configuración. Build final apunta a API 5000.
- **Navegador real, datos simulados**, en 60202/60203, sin proveedor, Docker o
  trabajos reales: ingesta cambia tarjeta de log 10→20 manteniendo informe de
  dos grupos; éxito cambia tarjetas 2/1/1/10→5/4/2/20 y círculo 50/50→80/20;
  publicación posterior con conteos idénticos cambia referencia b→c.
- SVG comprobado en DOM: segmentos `80 20` y `20 80`, desplazamientos 0 y -80.
  Se comprobaron cambios automáticos, sin pulsar Actualizar o recargar el ensayo.
- UI operativa nueva: tarjetas **5/4/1/68**, publicación 19:13:10 Madrid /
  `938dbff10379`, círculo 80/20. Cero warnings/errores de consola capturados.
  Captura visual de tarjetas y círculo guardada, sin adjuntar líneas de log.

## Carga y preservación

Se verificó identidad, fecha, argumentos y listener del Next anterior
28120 (11/10 16:23:55 UTC). Se conservó su build completo en
`.local-state/ui-refresh-20261011/next-build-before`, se cargó el build verificado
y se reinició **solo Next**. Nuevo PID **3632**, creado 11/10 17:26:47 UTC,
Node instalado, producción en 127.0.0.1:3000 y API 5000. Verificar identidad antes
de cualquier operación futura; el PID anterior es histórico.

Flask conserva listener 29408 en 127.0.0.1:5000. No se reiniciaron Flask/worker,
no se cambió manual y no se pulsó Iniciar análisis. Puertos de ensayo cerrados.
Antes/después y tras revisar el navegador: **29 trabajos, cero activos,
14 entregas históricas**, filas de trabajos/entregas idénticas, hashes del log,
puntero/report/result y metadatos `.env` iguales. No se restaura actividad del
usuario. Sin nuevas llamadas reales, envíos, Docker, commit o push.

La aceptación funcional del usuario y esta lectura acreditan que su trabajo
publicó la corrección de formato/narrativa. No cierran por sí solas evaluación
semántica general, cobertura completa o el motivo desconocido del primer fallo
de ingesta. Linux/Parrot y distribución/CI mantienen sus pendientes independientes.

Recibos en `.local-state/ui-refresh-20261011/`: API resumida sin contenido libre,
invariantes, build, lecturas del ensayo, `test-summary.json`, identidad de
activación y `tarjetas-grafico-actual.jpg`. El intento inicial de captura por
región salió vacío y se sustituyó por una captura normal válida tras desplazar
la página. No se utiliza aquella imagen como prueba.

Si hace falta reversión, verificar Next vigente y mover su build a una carpeta
local separada antes de restaurar `next-build-before`; reiniciar únicamente
ese servicio. No restaurar SQLite, logs o informes por un cambio de frontend.
Para revertir fuentes, retirar solo el disparador y el texto nuevos, conservando
las correcciones anteriores y los cambios del usuario.

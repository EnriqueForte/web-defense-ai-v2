# R-14 — Refresco por identidad de publicación

Entrega del 07/10/2026 tras la conformidad del usuario con la corrección de
fechas/referencias. No supone aceptación de todos los criterios A-05.

## Problema y comportamiento resultante

Una republicación atómica con el mismo texto puede conservar snapshot_id
(identidad de contenido) y cambiar report_id (identidad del archivo publicado).
Las listas dependían principalmente del snapshot: podían conservar referencias
al archivo anterior aunque el resumen ya mostrase la nueva publicación.

Se conservan ambas identidades y el contrato API. Los efectos de Amenazas y
Reportes dependen ahora también de report_id. Amenazas comprueba que coincidan
contenido y publicación al recibir una respuesta. Si el reporte actual estaba
seleccionado, el catálogo mueve la selección a la nueva publicación actual;
si se había elegido un histórico, mantiene esa selección. Si la página del
catálogo no contiene un actual, no inventa ni borra la selección.

Las respuestas de listas/detalle canceladas no actualizan estado. getApi comprueba
el aborto después de fetch y de decodificar el cuerpo, incluso si un transporte
devuelve tarde una respuesta pese a la cancelación. Se mantiene el último reporte
válido según la selección vigente; una respuesta anterior no debe sustituirlo.

## Verificación

- Prueba Python con archivo temporal: mismo texto, misma captura, nuevo report_id;
  el catálogo/detalle y amenazas refieren la nueva publicación. La anterior deja
  de abrirse como actual. No se repitió una publicación operativa.
- Regresión JS: selección de actual frente a histórico, catálogo sin actual,
  ausencia de selección, aborto durante lectura diferida del cuerpo y recuperación
  en la siguiente lectura. Fetch sustituido por doble, sin HTTP externo.
- 228 pruebas Python en `.p2` y `.venv`, tres diagnósticos JS por ejecución,
  nueve grupos de UI, TypeScript y ESLint aprobados; diff sin errores.
- Navegador real: enlace directo al informe existente carga report.md y su vista
  con intervalos. Se cerró la pestaña temporal sin modificar la del usuario.

No se ejecutaron nuevos jobs, llamadas LLM, notificaciones, recapturas de logs
o reinicios Flask/worker. Next recargó el código del frontend; .env, informes,
generaciones, configuración y API operativa se conservaron.

## Límites y pendientes

R-14 queda corregida en la lógica de refresco por publicación, con reproducción
aislada de la identidad y cobertura de selección. No se hizo una prueba de
republicación operativa en navegador ni de todas las carreras posibles de React.
R-18 sigue parcialmente pendiente: validación detallada de respuestas, timeout
de solicitudes, polling sin solapamiento y simulación completa de conexión lenta
o perdida. Este cambio cubre cancelación de las lecturas, no todo R-18.

A-05 mantiene pendiente observación/aceptación final de sus límites; la conformidad
con las fechas no amplía presupuesto de proveedor ni habilita análisis manuales.
La reversión es de frontend: restaurar dependencias/selección anteriores. No
requiere restaurar datos ni cambiar el motor operativo.

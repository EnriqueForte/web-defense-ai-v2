# Fase 6 — Validación y preparación del piloto

Estado: preparación local completada con datos sintéticos y notificaciones
simuladas. El piloto con Docker, proveedor IA y destinos de notificación reales,
así como la observación continua de 24–48 horas, queda aplazado hasta disponer
de un laboratorio aislado.

## Preparación local realizada

- El arranque directo de Flask queda ligado a `127.0.0.1` y sin depurador.
  Las rutas Flask rechazan clientes cuya dirección no sea loopback, incluidas
  las lecturas de logs e históricos.
- La solicitud manual sigue desactivada por defecto y exige ejecutor activo,
  clave idempotente, origen de navegador local y cliente loopback.
- Se comprueban lecturas simultáneas, diez ciclos sintéticos persistidos,
  recuperación de trabajos interrumpidos, exclusión del segundo ejecutor,
  contenido y resultado de notificaciones capturadas en memoria, fallo de
  análisis y denegación de acceso remoto. Los transmisores de red están
  sustituidos por un receptor de prueba que no realiza conexiones.
- La concurrencia sintética con 1, 5 y 10 clientes comprueba respuestas y
  consistencia de captura; no mide p95 ni sustituye la carga con tamaños de
  log y hardware representativos descrita en el plan principal.
- La revisión conectada en navegador usa la fixture en el puerto aislado
  `5051`, mientras Next.js dirige su API local mediante
  `WEB_DEFENSE_API_PORT=5051`. Se recorrieron resumen, filtros, históricos y
  actividad en 390, 768, 1280 y 1440 píxeles de ancho; no hubo desbordamiento
  horizontal. El HTML de prueba del reporte se mantuvo como texto y el menú
  móvil pasó a ocultarse del foco cuando está cerrado.
- La base SQLite y bloqueos permanecen en almacenamiento local ignorado por
  Git. Las lecturas no inician trabajos ni hacen llamadas externas.

## Condiciones antes del piloto real

1. Confirmar que DVWA está en un laboratorio local aislado, que el usuario
   puede detenerlo y que ningún pipeline antiguo está activo.
2. Preparar destinos de notificación de prueba, distintos de destinatarios
   operativos. No poner credenciales en el repositorio ni en esta conversación.
3. Revisar `.env.example` y configurar las variables necesarias localmente;
   `ANALYSIS_MANUAL_ENABLED` permanece en `0` hasta confirmar el entorno.
4. Arrancar primero Flask y Next.js en loopback y comprobar lecturas, salud,
   reporte actual, históricos y ruta de retorno Flask.
5. Activar el ejecutor de forma explícita, medir un ciclo completo y verificar
   sincronización, publicación nueva, histórico, estado durable y cada destino
   de prueba. Si una entrega queda `unknown`, comprobar el receptor antes de
   intentar otra vez.
6. Mantener el laboratorio bajo observación al menos 24–48 horas y completar
   diez ciclos, lo que tarde más. Registrar duración, resultado, errores,
   reporte publicado y entrega de cada destino, sin copiar secretos o logs
   completos a los registros de desarrollo.
7. Ensayar retorno: cerrar nuevas solicitudes, esperar o reconciliar el trabajo
   activo, detener un único ejecutor, apagar Next.js y confirmar que Flask y
   los reportes siguen disponibles. Medir el tiempo de retorno.

La aplicación sigue restringida a un usuario local. No desplegarla en una red
compartida: el guardado local no sustituye autenticación central para Flask,
Next.js y el proxy. Si el alcance cambia a acceso compartido, primero se debe
añadir y validar esa protección en todas las rutas de lectura y escritura.

## Criterios de cierre

La parte local de la fase queda completada por la suite automatizada con
dobles. La fase de piloto/despliegue solo se cierra cuando se aprueban los
recorridos del navegador, la medición de rendimiento con volúmenes de log y
hardware representativos, diez ciclos reales y la ventana de estabilidad,
los destinos de prueba, el reinicio y el ensayo de retorno. Las pruebas con
dobles no cuentan como integración externa. No se ha hecho aún la medición
representativa ni la observación de 24–48 horas; este documento no declara
aprobado el piloto.

## Reversión

Desactivar nuevas solicitudes con `ANALYSIS_MANUAL_ENABLED=0`, reiniciar Flask,
detener el ejecutor de forma controlada y reconciliar cualquier trabajo activo.
Usar Flask en `127.0.0.1:5000` y conservar `.local-state/`, logs, reporte actual
e históricos. No iniciar el programador anterior hasta confirmar que el nuevo
ejecutor ya se detuvo.

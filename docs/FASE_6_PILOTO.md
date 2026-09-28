# Fase 6 — Validación y preparación del piloto

Estado: diez ciclos integrados terminaron correctamente el 28/09/2026 y
publicaron diez reportes archivados. Se probaron DVWA/MySQL y Mailpit en
loopback. Siete entregas de correo están confirmadas; tres intentos anteriores
permanecen `unknown` porque se reinició Mailpit antes de poder revisarlos. Una
alerta sintética posterior confirmó el envío tras corregir el falso estado
causado por la codificación de consola. El retorno a Flask se ensayó con Next
detenido: Flask respondió HTTP 200 en 53 ms y conservó salud `ok`. La ventana
de observación de 24 horas comenzó el 28/09/2026 a las 17:27 UTC; la fase sigue
abierta hasta validar su resumen.

La medición local de la API con 88 y 10.000 líneas sintéticas pasó los
objetivos p95 de estado (<500 ms) y filtro (<200 ms) con 1, 5 y 10 clientes,
después de evitar que el filtro de amenazas recalcule métricas del log. La
medición usó Windows 10 build 26200, Python 3.11.9, 16 procesadores lógicos y
31 GB de memoria. Las latencias p95 (estado/filtro, milisegundos) fueron:

| Log sintético | 1 cliente | 5 clientes | 10 clientes |
|---|---:|---:|---:|
| 88 líneas | 24.9 / 27.1 | 23.9 / 15.6 | 38.2 / 31.9 |
| 10.000 líneas | 30.0 / 12.7 | 22.0 / 23.4 | 50.4 / 41.1 |

La ruta de retorno Flask respondió HTTP 200 con Next.js detenido. El script reproducible es
[`scripts/benchmark_phase6_api.py`](../scripts/benchmark_phase6_api.py).

La puesta en marcha, detención, captura del log aislado y límites del entorno
están en [la guía del laboratorio DVWA](LABORATORIO_DVWA_FASE_6.md). Esta
preparación no cambia `docker-compose.yml` ni activa el motor. La comprobación
manual del laboratorio no equivale al piloto integrado ni a su aceptación.

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

1. Antes de iniciar una integración controlada, confirmar que ningún pipeline
   antiguo esté activo. Ya se comprobó desde VSCode la tarea **laboratorio DVWA
   (Flask + Next.js)**, el Compose en loopback y la detención conservando la base.
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
6. Mantener el laboratorio bajo observación al menos 24–48 horas; diez ciclos
   exitosos ya están registrados. Registrar duración, resultado, errores,
   reporte publicado y entrega de cada destino, sin copiar secretos o logs
   completos a los registros de desarrollo.
7. Ensayar retorno: cerrar nuevas solicitudes, esperar o reconciliar el trabajo
   activo, detener un único ejecutor, apagar Next.js y confirmar que Flask y
   los reportes siguen disponibles. Medir el tiempo de retorno.

## Ciclo integrado acotado

El recorrido real de un ciclo se ejecuta con
[`scripts/run_phase6_cycle.ps1`](../scripts/run_phase6_cycle.ps1). Este comando
usa el proveedor LLM configurado localmente y puede consumir cuota; requiere
DVWA y Mailpit activos. Separa el log, los reportes, el historial y SQLite bajo
`.local-state/phase6-pilot/`, limita notificaciones a email con destinatarios
ficticios en Mailpit y omite Telegram. Mailpit local no requiere contraseña; la
aplicación solo permite omitirla cuando el servidor SMTP es loopback. El comando
termina tras un ciclo, tanto si tiene éxito como si falla. No activa el análisis manual ni la entrada
principal de Next.js. Revisar el estado durable y Mailpit antes de decidir
cualquier repetición.

El 28/09/2026 se completaron diez ciclos exitosos en el almacén aislado; los
intentos fallidos no se cuentan. El límite de tokens por minuto de Groq exigió
espaciar las llamadas. Tres entregas `unknown` no se reintentaron
automáticamente. Seis mensajes de la última tanda se reconciliaron con Mailpit
por hora de entrega. Un envío sintético posterior quedó confirmado como `sent`
tras hacer los mensajes de consola compatibles con Windows. El monitor
[`scripts/observe_phase6.ps1`](../scripts/observe_phase6.ps1) registra cada cinco
minutos la salud de Flask, Next.js, DVWA, Mailpit y MySQL, sin ejecutar análisis
ni guardar cuerpos de respuestas. Su resumen se guarda en
`.local-state/phase6-pilot/observation/summary.json` al completar las 24 horas.

La aplicación sigue restringida a un usuario local. No desplegarla en una red
compartida: el guardado local no sustituye autenticación central para Flask,
Next.js y el proxy. Si el alcance cambia a acceso compartido, primero se debe
añadir y validar esa protección en todas las rutas de lectura y escritura.

## Criterios de cierre

La medición local, los diez ciclos y el ensayo de retorno ya están completados.
El benchmark usa fixtures sintéticas y un servidor WSGI local, por lo que no
representa el renderizado del navegador ni una carga de producción. Los tres
estados `unknown` siguen documentados y no se reintentan sin evidencia del
receptor. La fase continúa abierta hasta revisar el resumen de observación de
24 horas; si registra fallos, se prolongará hasta 48 horas y se analizarán
antes del cierre.

## Reversión

Desactivar nuevas solicitudes con `ANALYSIS_MANUAL_ENABLED=0`, reiniciar Flask,
detener el ejecutor de forma controlada y reconciliar cualquier trabajo activo.
Usar Flask en `127.0.0.1:5000` y conservar `.local-state/`, logs, reporte actual
e históricos. No iniciar el programador anterior hasta confirmar que el nuevo
ejecutor ya se detuvo.

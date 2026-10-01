# Fase 6 — Validación y preparación del piloto

Estado: cerrada anticipadamente el 29/09/2026 por decisión del usuario, con
observación parcial documentada. Diez ciclos integrados terminaron correctamente el 28/09/2026 y
publicaron diez reportes archivados. Se probaron DVWA/MySQL y Mailpit en
loopback. Siete entregas de correo están confirmadas; tres intentos anteriores
permanecen `unknown` porque se reinició Mailpit antes de poder revisarlos. Una
alerta sintética posterior confirmó el envío tras corregir el falso estado
causado por la codificación de consola. El retorno a Flask se ensayó con Next
detenido: Flask respondió HTTP 200 en 53 ms y conservó salud `ok`. La ventana
de observación de 24 horas comenzó el 28/09/2026 a las 20:23 UTC, después de
descartar la ventana anterior por una interrupción prolongada entre muestras.
Sus registros se conservan en
`.local-state/phase6-pilot/observation/health.partial-20260928T172742Z.jsonl`.
La ventana válida conservó su inicio del 28/09/2026 a las 20:23:28 UTC y se
reanudó con `-Resume`; la observación anterior de las 17:27 UTC permanece
archivada como parcial. El proceso volvió a interrumpirse después de la muestra
del 29/09/2026 a las 03:26:45 UTC cuando Docker dejó de estar disponible. El
mismo `health.jsonl` se reanudó a las 05:35 UTC y se amplió a 48 horas desde su
marca inicial. Los registros de recuperación incluyen seis muestras fallidas.
La última muestra disponible es del 29/09/2026 a las 20:15:37 UTC. Desde la
primera muestra saludable posterior a la recuperación (06:03:51 UTC) se
registraron 171 muestras consecutivas saludables durante 14 h 11 min 46 s,
con un intervalo máximo entre muestras de 301,2 s. El usuario decidió terminar
la observación antes de las 24 horas consecutivas inicialmente previstas. El
monitor se detuvo y se conservó `health.jsonl`; al pararlo antes del plazo no
se generó `summary.json`, por lo que esta aceptación no equivale a superar la
ventana completa ni su resumen automático.

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
están en [la guía del laboratorio DVWA](LABORATORIO_DVWA_FASE_6.md). El piloto
usa el Compose aislado de DVWA y ejecuta los ciclos solo mediante el script
acotado descrito abajo; no activa el programador de análisis ni la entrada
principal de Next.js.

## Validaciones locales realizadas

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
- El benchmark reproducible mide p95 con 1, 5 y 10 clientes y logs sintéticos
  de 88 y 10.000 líneas; los resultados y el hardware figuran al inicio de
  este documento. Es una carga local representativa, no una prueba de
  producción.
- La revisión conectada en navegador usa la fixture en el puerto aislado
  `5051`, mientras Next.js dirige su API local mediante
  `WEB_DEFENSE_API_PORT=5051`. Se recorrieron resumen, filtros, históricos y
  actividad en 390, 768, 1280 y 1440 píxeles de ancho; no hubo desbordamiento
  horizontal. El HTML de prueba del reporte se mantuvo como texto y el menú
  móvil pasó a ocultarse del foco cuando está cerrado.
- La base SQLite y bloqueos permanecen en almacenamiento local ignorado por
  Git. Las lecturas no inician trabajos ni hacen llamadas externas.

## Piloto local ejecutado

El 28/09/2026 se comprobó el Compose aislado y la tarea de arranque de Flask,
Next.js y DVWA. Se usaron destinos ficticios en Mailpit; se verificaron diez
ciclos integrados, reportes e historial, estados durables y entregas. Tres
resultados antiguos permanecen `unknown` porque Mailpit había sido reiniciado;
no se repitieron sin evidencia. También se midieron las API y se ensayó la
reversión a Flask con Next.js detenido. La observación se cerró anticipadamente
por decisión del usuario. La evidencia disponible y sus límites quedan
registrados abajo; no se afirma que se haya cumplido el objetivo original de
24 horas.

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
ni guardar cuerpos de respuestas. La opción `-Resume` conserva la primera
marca de tiempo y los contadores del registro existente; `-DurationHours` puede
extender su fecha límite sin crear otro registro. Su resumen se guarda en
`.local-state/phase6-pilot/observation/summary.json` al alcanzar el plazo
configurado.

La aplicación sigue restringida a un usuario local. No desplegarla en una red
compartida: el guardado local no sustituye autenticación central para Flask,
Next.js y el proxy. Si el alcance cambia a acceso compartido, primero se debe
añadir y validar esa protección en todas las rutas de lectura y escritura.

## Criterios de cierre

La medición local, los diez ciclos y el ensayo de retorno ya están completados.
El benchmark usa fixtures sintéticas y un servidor WSGI local, por lo que no
representa el renderizado del navegador ni una carga de producción. Los tres
estados `unknown` siguen documentados y no se reintentan sin evidencia del
receptor. El usuario acepta cerrar la fase con la evidencia disponible: diez
ciclos integrados, medición local, ensayo de retorno y un tramo final de 171
muestras saludables en 14 h 11 min 46 s (intervalo máximo 301,2 s). El registro
completo contiene seis fallos de disponibilidad durante la recuperación,
todos antes de ese tramo saludable. La observación terminó por decisión del
usuario antes de las 24 horas consecutivas requeridas inicialmente y no existe
`summary.json`; por tanto, el cierre es una aceptación explícita de ese límite,
no una certificación de estabilidad durante 24 horas. Los tres correos
`unknown` siguen sin reconciliarse y no se reintentaron. La Fase 7 puede
continuar en su preparación, pero este cierre anticipado por sí solo no cumple
su criterio separado de 24–48 horas estables ni autoriza activar el conmutador.

## Reversión

Desactivar nuevas solicitudes con `ANALYSIS_MANUAL_ENABLED=0`, reiniciar Flask,
detener el ejecutor de forma controlada y reconciliar cualquier trabajo activo.
Usar Flask en `127.0.0.1:5000` y conservar `.local-state/`, logs, reporte actual
e históricos. No iniciar el programador anterior hasta confirmar que el nuevo
ejecutor ya se detuvo.

# Comprobación de puertos tras cerrar — 12/10/2026

## Incidencia y alcance

El usuario confirmó instalación, arranque y navegación del lanzador unificado
en Parrot. Después de cerrar, la web dejó de cargar pero `check` rechazó tres
veces el puerto 3000. Una captura posterior mostró ausencia de listeners y
TIME_WAIT en 3000/5000, y `check` preparado. No hay captura durante el rechazo
ni duración medida; no se atribuye definitivamente el episodio a TIME_WAIT.

El código anterior usaba bind sin reutilización en tres comprobadores. En POSIX
esto puede rechazar sockets residuales de servidores HTTP reutilizables aunque
el servidor ya haya terminado. La [documentación de Python](https://docs.python.org/3/library/socket.html)
describe SO_REUSEADDR para reutilizar sockets en TIME_WAIT en POSIX. Windows
tiene [semántica diferente de reutilización y exclusividad](https://learn.microsoft.com/en-us/windows/win32/winsock/using-so-reuseaddr-and-so-exclusiveaddruse).

## Cambio

`scripts/local_port.py` centraliza la prueba para install, start/check y perfil
Flask. En POSIX usa SO_REUSEADDR y comprueba bind/listen local, cerrando enseguida
sin aceptar peticiones. En Windows usa una reserva exclusiva en todas las
interfaces sin listen, para rechazar también solapamientos wildcard/específicos.
No conecta con servidores existentes ni termina procesos ajenos.

Los fallos distintos de EADDRINUSE no se presentan como ocupación acreditada:
se indica que no se pudo comprobar y se bloquea el inicio. El preflight sigue
sin reservar el puerto hasta el arranque real; puede haber carreras con procesos
externos. No se cambian políticas TCP del sistema ni se añaden esperas fijas.

## Validación y pendientes

- Windows local `.p3`: suite de 289 casos, 288 aprobados y una omisión explícita
  para Linux; tres comprobaciones JavaScript aprobadas.
- Pruebas reales con sockets efímeros: listener activo normal/reutilizable,
  loopback y wildcard, rechazo sin interrumpirlo y liberación del socket de prueba.
- Error de permisos y estado de puerto no verificable bloquean el inicio.
- 78 archivos de sintaxis y diff check aprobados. Los diez casos de perfil local
  se repitieron después de ampliar la comprobación del estado no verificable.
- Smoke real en la copia aislada `.i1` con los nuevos comprobadores: API directa
  y proxy HTTP 200, ejecutor offline, cierre y puertos libres. Recibo en
  `.i1/.local-state/launcher-smoke/result.json`; servicios de prueba detenidos.
- Regresión Linux preparada: conexión real cerrada primero por servidor, bind
  antiguo rechazado, nuevos comprobadores aceptados y nuevo listener inmediato.
  Se omite en Windows; pasó después en Ubuntu CI. Confirmación Parrot pendiente.

No se iniciaron servicios operativos, análisis, llamadas a proveedores, Docker
ni notificaciones. Pruebas con datos temporales y sockets sintéticos. La CI
anterior no acredita esta corrección.

## Publicación y seguimiento

El commit `2a73ff043298bccd5419298a491a28b59ec56411` se publicó en `origin/main`
del repositorio V2. La [ejecución 38237671713](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38237671713)
terminó con `success` en el primer intento, tanto en Windows-latest como en
Ubuntu 24.04. Se comprobaron los estados y los logs finales del mismo SHA.

Ambos runners completaron instalación nueva, pip check, contrato sin diferencias
(158 pines Windows/157 Linux), build, 78 archivos de sintaxis, tres JS, HTTP
sintético, 25 escenarios SDK offline, lint/tipos y 15 grupos UI. Ubuntu aprobó
los 289 casos Python, incluida la regresión real TIME_WAIT/reinicio inmediato.
Windows aprobó 288 y omitió expresamente ese caso Linux. Los dos completaron
el smoke: API directa/proxy HTTP 200, ejecutor offline y cierre con puertos libres.

Recibos ignorados bajo `.local-state/launcher-20261012/`:
`actions-2a73ff043298bccd5419298a491a28b59ec56411.json`,
`run-38237671713-logs.zip` y `ci-checks-38237671713.json`.
La actualización documental posterior usa `[skip ci]`; el código comprobado
corresponde a `2a73ff0`. La confirmación de reinicio inmediato en la VM Parrot
sigue pendiente; no se exige reinstalar dependencias ni recompilar por este ajuste Python.

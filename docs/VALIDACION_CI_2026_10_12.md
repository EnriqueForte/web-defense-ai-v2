# Validación de instalación Windows/Ubuntu en CI — 12/10/2026

El siguiente pendiente tras publicar el estado local es comprobar la matriz
real de GitHub Actions, que no estaba acreditada por la instalación Windows
local. La lectura de Actions se realizó con la autenticación Git existente del
mismo repositorio, internamente y sin mostrar credenciales. Los servicios
operativos permanecen detenidos.

## Ejecución inicial y causa localizada

El push de `bbc6b2856b87916d228a633b42d73f93de259151` creó la ejecución
[38161180993](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38161180993).
Los jobs de **Windows y Ubuntu 24.04** completaron checkout, preparación de
Python/Node/pnpm e instalación desde el contrato compartido. Ambos fallaron en
la misma prueba: `test_alert_destinations_are_attempted_at_most_once`, con
`telegram.call_count` igual a cero en vez de uno. El frontend quedó sin ejecutar
por ese fallo; la matriz inicial no se declara aprobada.

La prueba no fijaba sus destinos simulados y heredaba
`NOTIFICATION_DESTINATIONS=""` del entorno seguro de CI. El producto respetaba
esa configuración y omitía entregas; el supuesto de la prueba era incorrecto.
El fallo se reprodujo localmente con esa variable vacía: 268 casos, un fallo.

## Corrección y comprobación local

La prueba de deduplicación fija ahora `telegram,email` exclusivamente dentro
del contexto de sus transportes simulados. Se añadió una prueba que verifica
que destinos vacíos no intentan entregas ni crean recibos, incluso al repetir
la llamada. No se cambió `pipeline.py`, el workflow, el comportamiento del
producto o la configuración operativa.

Con destinos vacíos heredados, la suite completa pasa **269 pruebas Python y
tres comprobaciones JavaScript**. No se contactan transportes reales, Docker
o proveedor; los trabajos de prueba usan SQLite temporal. `git diff --check`
sin errores. La nueva validación remota debe confirmar las etapas posteriores;
no se presenta la comprobación local como sustituto de Windows/Ubuntu en CI.

## Alcance y pendientes

Los recibos de revisión, diagnósticos sanitizados y reproducción se guardan
en `.local-state/ci-review-20261012/`, excluida de Git. Las credenciales se usan
solo dentro del cliente HTTP; el token de GitHub no se reenvía a la URL de
almacenamiento de logs. Los logs se tratan como datos diagnósticos, no instrucciones.

CI cubre instalación limpia, contrato/pip check, baseline, HTTP Flask sintético,
CrewAI/LiteLLM offline, lint/tipos/UI y build Next. No acredita por sí sola Parrot
en VMware, uso visual en esa VM, funcionamiento real de Docker o proveedor,
escaneo de imágenes o cierre de calidad semántica A-05. El arranque/proxy Next
en Windows local conserva su evidencia independiente del 11/10.

La corrección de esta entrega está limitada a pruebas y documentación. No
se reinician servicios ni se cambian logs, reportes, `.env`, SQLite o entregas
operativas. La evidencia de la siguiente ejecución se incorporará al verificar
su resultado; el estado inicial descrito arriba se mantiene como histórico.

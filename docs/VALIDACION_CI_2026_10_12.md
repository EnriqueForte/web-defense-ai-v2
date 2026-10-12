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
sin errores. La revalidación remota descrita a continuación confirma también
las etapas posteriores.

## Matriz remota aprobada

El commit de corrección `96d190c56109504c9475edf1f9bbe59ec0d078bd` se publicó
en `origin/main`. La ejecución
[38224024703](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38224024703),
creada el 12/10/2026 a las 08:30:53 UTC, terminó con `completed/success` en su
primer intento. Los logs finales y los estados de cada etapa se comprobaron.

| Comprobación | Windows (`windows-latest`, job 114726981900) | Ubuntu 24.04 (job 114726981989) |
| --- | --- | --- |
| Checkout e instalación nueva con Python 3.11/Node 24/pnpm 11.19.0 | Aprobados | Aprobados |
| Contrato y `pip check` | 158 pines, cero diferencias | 157 pines, cero diferencias |
| Sintaxis | 71 archivos, cero errores | 71 archivos, cero errores |
| Baseline | 269 Python y tres JS | 269 Python y tres JS |
| HTTP Flask sintético, CSP, retorno y recursos/hash | Aprobados | Aprobados |
| CrewAI/LiteLLM offline | 25 escenarios | 25 escenarios |
| Frontend | lint, tipos, 15 grupos UI y build Next 16.3.8 | lint, tipos, 15 grupos UI y build Next 16.3.8 |

En la etapa frontend de Windows también se revisaron los logs de las órdenes
intermedias: no hay errores de lint/tipos/UI y se confirma la compilación y
generación de páginas. El mensaje de ausencia de caché de build es informativo.
La salida `Ciclo único: failed (error=analysis_failed)` del baseline pertenece
a una prueba negativa deliberada; el resultado global es 269/269 aprobadas.

El instalador Linux excluye `pywin32` por marcador y resolvió adicionalmente
`uvloop==0.23.0`, que aún no está fijado en el contrato común derivado de Windows.
Los mensajes de instalación informan 158 paquetes en cada plataforma. Esta
revisión de los logs no sustituye a un `pip freeze` de Linux; capturar y fijar
sus dependencias adicionales sigue pendiente para reproducibilidad completa.
No se modifican ahora los pines a partir de una matriz ya aprobada.

## Alcance y pendientes

Los recibos de revisión, diagnósticos sanitizados y reproducción se guardan
en `.local-state/ci-review-20261012/`, excluida de Git. Las credenciales se usan
solo dentro del cliente HTTP; el token de GitHub no se reenvía a la URL de
almacenamiento de logs. Los logs se tratan como datos diagnósticos, no instrucciones.

CI acredita checkout e instalación limpia en esos runners, contrato/pip check, baseline, HTTP Flask sintético,
CrewAI/LiteLLM offline, lint/tipos/UI y build Next. No acredita por sí sola Parrot
en VMware, uso visual en esa VM, arranque/proxy Next en Linux, funcionamiento real de Docker o proveedor,
escaneo de imágenes o cierre de calidad semántica A-05. El arranque/proxy Next
en Windows local conserva su evidencia independiente del 11/10.

La corrección de esta entrega está limitada a pruebas y documentación. No
se reinician servicios ni se cambian logs, reportes, `.env`, SQLite o entregas
operativas. El estado fallido inicial se conserva como histórico. La revisión
de seguridad, el escaneo efectivo de imágenes, la calidad A-05 y la aceptación
en Parrot siguen siendo ámbitos pendientes independientes.

La actualización posterior que registra estos resultados solo cambia documentación;
utiliza `[skip ci]` para evitar repetir la matriz por ese registro. La evidencia
de código probado corresponde al SHA `96d190c56109504c9475edf1f9bbe59ec0d078bd`.

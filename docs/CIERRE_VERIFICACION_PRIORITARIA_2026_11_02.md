# V2 y Puerto Umbral — verificación prioritaria de cierre

Fecha: 02/11/2026, Europe/Madrid. El propietario pide hacer lo necesario e
importante para terminar el proyecto. Se mantiene el objetivo F0–F7 y se
priorizan fallos conocidos y criterios abiertos. No se añaden variantes por
cantidad ni se repiten capturas de interfaz, arranques o análisis completados.

## Resultado realizado: cinco regresiones aisladas del lanzador

El propietario autoriza expresamente las cinco pruebas ya preparadas de
`tests/test_manual_application_launcher.py`. Se ejecutan una vez en Windows,
desde el repositorio, con el entorno `.p2` y Python **3.11.9**:

```powershell
.p2/Scripts/python.exe -B -m unittest tests.test_manual_application_launcher -v
```

Resultado: **5 pruebas, 5 correctas, 0 fallos, exit 0**. La salida de unittest
informa 0,020 s de ejecución de las pruebas. No hizo falta modificar código.

| Prueba | Qué verifica |
| --- | --- |
| `test_pending_jobs_block_manual_start_before_process_creation` | Los trabajos pendientes bloquean el inicio antes de crear el supervisor de procesos |
| `test_manual_flag_does_not_turn_install_or_legacy_into_an_analysis_start` | La opción manual se rechaza en instalación y en el inicio legacy; no lanza procesos |
| `test_worker_readiness_requires_admission_and_heartbeat_not_provider_contact` | La disponibilidad requiere admisión y ejecutor online; no depende de contactar al proveedor |
| `test_worker_failure_closes_owned_processes_without_starting_next` | Un fallo de disponibilidad del worker cierra los procesos propios simulados y no inicia Next |
| `test_manual_check_reports_the_same_mode_without_starting_services` | `check` conserva modo/opción en la indicación de inicio sin llamar a `serve` |

Son pruebas de orquestación con procesos/HTTP simulados y archivos temporales.
No arrancan Docker, VM, Flask, Next o un worker real; no ejecutan escenarios,
modelo o notificaciones. No cargan la aplicación Flask ni credenciales. Se
complementan con el ciclo básico manual recibido en Parrot el 01/11, sin
sustituir pruebas Linux, de un trabajo real o de otros componentes.

**Queda cerrada la ejecución pendiente de estas cinco regresiones.** No se
declara cerrada toda la regresión del MVP, la operación F4 o la aceptación F6.
No se amplía la suite después de este resultado correcto sin otro alcance.

## Incidencia funcional: bloque representativo completado

El histórico conserva tres resultados `Cannot fork` del módulo de comandos.
La fuente actual elimina el límite por UID `RLIMIT_NPROC`, que contaba procesos
de otros contenedores con el mismo usuario. Se mantiene el techo de procesos
del contenedor, además de CPU, memoria, archivos y descriptores. La revisión
de esa fuente no demuestra que la imagen en Parrot contenga o ejecute la
corrección.

Propuesta acotada para la siguiente validación manual: **dos recorridos** del
módulo existente, uno de uso normal corregido y uno representativo vulnerable
de variante 1, observando respuesta funcional, ausencia de `Cannot fork` y
recibo correlacionado. El primero comprueba que el subproceso normal funciona;
el segundo aborda el fallo conocido. No se suministran comandos nuevos ni
destinos distintos de los fixtures del laboratorio.

Antes de ese recorrido se identifica la versión/imagen local usada por la VM
con la información existente; no se prescribe reinstalar o reconstruir todo
por defecto. Si la imagen no corresponde, se revisa la preparación necesaria.
Si falla, se conserva la salida y se corrige la causa antes de ampliar casos.
Las variantes 2/3 históricas conservan su fallo original; una equivalencia por
causa común no las convierte en ejecuciones nuevas superadas.

El propietario acepta después «sigamos con la siguiente prioridad»: quedan
acordados esos dos recorridos manuales y la identificación previa de la imagen,
sin ampliar suites o llamadas al modelo. **Ambos resultados se reciben después
y completan ese bloque**, según las capturas detalladas debajo.
No se reinicia la VM, el laboratorio o los servicios desde el agente.

Primera lectura guiada, sin ejecutar el caso: identificar las imágenes de
`puerto-umbral-f2-command-corrected` y `puerto-umbral-f2-command-vulnerable`
con `docker inspect`, y leer el SHA-256 de `/srv/target.py` en el contenedor
corregido. El Dockerfile copia esa fuente a dicha ruta y ambos modos usan
la imagen target compartida. SHA-256 local de la fuente vigente:
`e05cce8a819728358e0d00886814593c0f3879868b7e7cfe53b4fafd169ce637`.
Coincidencia de IDs entre los dos contenedores y del hash de fuente permite
identificar el contenido que se va a comprobar; no demuestra el efecto
funcional. Si difiere o falla, recoger salida antes de reconstruir o ejecutar.
No se repite la inspección completa del perímetro de 14 contenedores.

Recepción del propietario, 02/11: ambos contenedores muestran el mismo ID de
imagen, prefijo `sha256:0ccdadfa84ad`; el hash leído de `/srv/target.py` coincide
exactamente con `e05cce8a819728358e0d00886814593c0f3879868b7e7cfe53b4fafd169ce637`.
**Identificación previa completada por captura**, sin reconstrucción necesaria
por una diferencia de fuente y sin repetirla. No acredita todavía el efecto
funcional o el estado de todos los límites del sistema.

Recepción del uso normal, 02/11: ejecución
`0e78b2e1bd2dc4bd48ec28aa6d8cd2e6`, F2/corrected/benign/variante 1,
COMPLETED, HTTP 200, `GET /mantenimiento?equipo=baliza-07`. La respuesta visible
contiene `stdout: "DIAG:baliza-07\n"`, `timed_out: false`, `returncode: 0`,
sin `Cannot fork`. Una petición del ejecutor y una línea Apache correlacionada;
V2 no consultado y auditoría de aplicación no disponible, conforme al módulo
base. **Uso normal corregido completado por captura del cuerpo real**;
no solo por el banner. No se repite ni se solicita auditoría F6 o exportación.

Recepción del segundo recorrido, 02/11: ejecución
`d2bf894ca4914ef4a7c3b43e7d97a445`, F2/vulnerable/attempt/variante 1,
COMPLETED, HTTP 200. El cuerpo mostrado contiene el diagnóstico y
`uid=10001(umbral)`, `timed_out: false`, `returncode: 0`, sin `Cannot fork`.
El panel informa efecto funcional observado, una petición del ejecutor y una
línea Apache correlacionada. V2 no consultado y auditoría de aplicación no
disponible, conforme al módulo base. No es una evaluación del detector.

**Incidencia `Cannot fork` corregida y verificada para el recorrido vulnerable
representativo de variante 1**, con fuente identificada y control normal
corregido previo. Bloque de dos recorridos COMPLETADO por capturas, sin
repetirlos, exportar o pedir una auditoría F6. Se conservan los tres fallos
históricos: variantes 2/3 no reejecutadas y sin resultado nuevo. La evidencia
representativa no cambia el archivo histórico a 45/45 ni acepta toda F2/F6.

## Qué sigue siendo imprescindible después

La siguiente prioridad recomendada es **operación F3/F4**, separada de nuevos
casos de seguridad y del modelo: concretar una sesión acotada para medir la
lectura y cotejar conservación/deduplicación/trabajos; definir aparte la
comprobación de discontinuidad con evidencia conservada. No basta repetir una
captura de contadores: deben conservarse veinte latencias individuales, o
revisarse expresamente una desviación como admite el PRD. No hay todavía
autorización o ejecución de ese bloque por recibir la captura del segundo
recorrido. Se prepara su alcance antes de modificar fuentes o iniciar ciclos.

El propietario acepta después continuar con operación. Primer paso guiado:
**lectura de las sesiones ya conservadas y los trabajos SQLite**, sin iniciar
seguimiento, cambiar la fuente o contactar a Docker/modelo. Se leen los JSON
de `following/sessions/` y `following/current.json`, deduplicados por ID;
se muestran fechas, modo, estado y contadores de las cinco últimas sesiones.
La base `analysis.sqlite3` se abre con `mode=ro` y `PRAGMA query_only=ON`;
se consultan el total de trabajos, estados/fechas de los veinte últimos y
el número de entregas, sin cuerpos de logs, claves o destinos de entrega.
Ausencia/error se informa como tal, no como cero trabajos. Resultado pendiente
de salida del propietario; esta lectura no certifica por sí sola ausencia de
trabajos durante cada sesión o deduplicación de archivos. La relación temporal
y las referencias deben revisarse con lo realmente conservado.

Revisión del servicio existente: guarda `cycles`, `last_cycle_seconds` y
checkpoint, sin veinte muestras individuales. Por tanto, no se vuelve a pedir
una captura del contador como medición completa de F4-AC1/RNF-09. RNF-09 pide
captura visible en diez segundos, con hardware/carga registrados: la duración
de lectura del último ciclo no demuestra por sí sola esa visibilidad. No se
inicia una nueva sesión de medición o interrupción de fuente por este primer
paso de lectura, ni se acepta una desviación temporal automáticamente.

### Historial y SQLite recibidos — 02/11

La salida del propietario muestra tres sesiones conservadas, todas de modo
corregido. Horas de esta tabla en **UTC del 27/10/2026**, redondeadas al segundo
para su lectura; no son sesiones nuevas realizadas el 02/11.

| Sesión (prefijo) | Estado persistido | Inicio / fin UTC | Ciclos | Snapshots nuevos / sin cambios | Última lectura (s) |
| --- | --- | --- | --- | --- | --- |
| `efd533dc` | completed | 16:50:51 / 16:55:51 | 26 | 1 / 25 | 0,057 |
| `9cc5313e` | stopped | 16:58:48 / 17:01:37 | 31 | 0 / 31 | 0,065 |
| `cf462e69` | following | 17:04:32 / sin fin | 5 | 0 / 5 | 0,058 |

SQLite informa **un trabajo total**, `succeeded`, solicitado el
27/10/2026 a las **21:38:37 UTC**, finalizado a las **21:38:42 UTC**;
**cero entregas registradas**. Ninguno de los trabajos actualmente conservados
cae dentro de los intervalos de las dos sesiones cerradas: el único trabajo
es posterior a ambas. Es corroboración temporal con la base conservada,
no una auditoría de transportes del proveedor ni prueba de registros borrados.

Los contadores respaldan la reutilización de snapshots en esas sesiones.
No prueban por sí solos deduplicación de todos los archivos/eventos ni veinte
latencias de visibilidad: solo se muestran tres últimas duraciones de lectura.
F4-AC1 y las condiciones de discontinuidad/rotación permanecen abiertos.

La tercera sesión tiene `finished_at: null`: **no se puede dar por cerrado
su intervalo ni concluir actividad actual a partir del JSON persistido**.
Siguiente lectura guiada: `GET /api/v1/fuentes/log/seguimiento` en V2, que
consulta el estado/lease actual sin iniciar el hilo o una captura. Por código,
un estado activo guardado cuyo lease está libre se presenta como `interrupted`,
`error_code: process_interrupted`, `session_active: false`. Es una expectativa,
pendiente de respuesta actual; si muestra activo o error, revisar antes de
iniciar otra sesión. No editar el JSON, borrar locks o reiniciar por defecto.

Respuesta posterior recibida del propietario: `status: interrupted`,
`error_code: process_interrupted`, `session_active: false`, `owned_here: false`,
`in_flight: false`, `enabled: true`, con `analysis_requested: false` y
`notifications_requested: false`. Conserva el checkpoint corregido de 17 líneas
`df39623de3684fa7932edf6b688b2f04`, SHA
`2f891446d512be3a31ee858db5f3318156f74b3d2348b40a7ee41dd8c59f2b4a`.
**Estado actual de interrupción/inactividad comprobado por API**. No se borra
el JSON ni se pide repetir la consulta; `running_at_capture` y los IDs del
gateway pertenecen al checkpoint antiguo, no certifican la pasarela actual.
No se obtiene una hora exacta de fin de la sesión histórica ni una inspección
exhaustiva de procesos del host por este resultado.

Para la medición necesaria se prepara un
[observador acotado](PUERTO_UMBRAL_MEDICION_F4_2026_11_02.md): veinte ciclos
distintos disponibles por API, metadatos SQLite y directorios antes/después,
un recibo nuevo y ninguna solicitud de control o modelo. No modifica el
servicio. El propietario autoriza después las cinco pruebas nuevas con
respuestas simuladas: **5/5 correctas, exit 0**, Windows/Python 3.11.9,
sin transporte real; no se amplía la suite. Medición Parrot/publicación siguen
pendientes. Se distingue
disponibilidad API de renderizado del navegador al revisar RNF-09/F4-AC1.

| Bloque | Trabajo concreto | Qué se reutiliza |
| --- | --- | --- |
| Operación F3/F4 | Un recorrido acotado de salud/discontinuidad de fuente y conservación; cotejo de snapshots/trabajos; veinte muestras de latencia o desviación expresamente revisada | Inicio, pausa/reanudación, parada, vencimiento, reapertura, perímetro y respaldo ya recibidos no se repiten |
| F6 y regresión MVP | Cubrir las conductas positivas distintas aún sin evidencia y la separación de perfiles/contrato de auditoría; definir el alcance antes de ejecutarlo | Normales/negativos corregidos, CSRF corregido en navegador, reutilización corregida y comparación Cargas ya observados |
| F5 | Preparar evaluación del corpus con entradas/expectativas separadas, resultados por caso y presupuesto explícito; medir los objetivos o documentar una decisión expresa del propietario sobre alcance | Los 45 registros históricos y sus causas; el informe único anterior no se vuelve a ejecutar ni se convierte en métrica del corpus |
| Entrega | Revisar matriz educativa F7, documentación V2 y decisión final con el propietario | Once recorridos F7 y revisión básica de ambas interfaces completados |

Baliza vulnerable mantiene su resultado funcional sin recibir y el recorrido
aplazado por el propietario. No se propone repetirlo o reformularlo para evitar
el bloqueo comunicado. Esa limitación permanece visible en el cierre F6.

No hay una cifra honesta de pruebas restantes deducible del catálogo: faltan
criterios y evidencias concretas, no completar 99 entradas. Tampoco se inicia
otra evaluación con el permiso Groq consumido. Esta priorización y sus
propuestas no autorizan nuevas suites, casos, servicios, Git o modelos.

Estado general y criterios: [resumen de entrega](PUERTO_UMBRAL_ENTREGA_2026_11_02.md),
[auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md) y
[PRD](PRD_PUERTO_UMBRAL_2026_10_26.md).

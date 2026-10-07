# Entrega 3 — Operación y cierre local de fase 7

Estado: completada el 06/10/2026, incluyendo cierre de F7-01 para el alcance
local reversible. Responsable: Codex principal, sin delegación. Se conserva
la arquitectura Python/CrewAI + API Flask + interfaz Next.js.

## Evidencia de uso y alcance del cierre

El 06/10/2026, durante esta entrega, el usuario respondió:
«He usado las cuatro vistas sin incidencias bloqueantes», en referencia a
Resumen, Amenazas, Reportes y Actividad desde el 01/10/2026.
Esta confirmación se registra como evidencia de experiencia de uso, distinta
del ensayo automatizado y de los registros históricos de fase 6.

El periodo sugerido de siete días desde el 01/10 no se ha completado el 06/10.
Era una sugerencia de aceptación, no un cierre automático por calendario.
El cierre local se apoya en esa confirmación, los recorridos ya registrados,
el ensayo actual de retorno y el respaldo verificado. No se afirma que hubiera
observación continua de cinco o siete días ni monitorización automatizada de uso.
Los logs de servidor de fase 7 tienen metadatos del 01/10 y no sustituyen esa
evidencia; no se inspeccionaron sus contenidos. No se encontró un registro
específico de observación continua de fase 7. Los registros de salud de fase 6
permanecen como evidencia histórica, sin ampliar artificialmente su duración.

Decisión de convivencia: Next.js sigue siendo la entrada local mediante la
tarea/conmutador aceptados; Flask permanece como backend y dashboard de
respaldo. No se retira Flask ni se activa el conmutador por defecto.
`NEXT_PRIMARY_ENABLED=0` y `ANALYSIS_MANUAL_ENABLED=0` continúan en el contrato
de instalación. No se publican servicios en una red compartida.

## Ensayo actual de retorno

Se añadió `scripts/check_phase7_return.py`. Solo utiliza un build Next aislado
bajo `.local-state`, sin archivos dotenv, y la fixture sintética Flask que
bloquea tanto carga dotenv como el resolver LLM. Requiere puertos 3000/5000
libres: si están ocupados, se niega a continuar y no detiene servidores ajenos.
Inicia sus propios procesos ocultos, comprueba el recorrido y los cierra al
terminar, también ante fallos. No ejecuta el motor, el coordinador ni transportes.

La ejecución del 06/10/2026 verificó:

| Comprobación | Resultado |
|---|---|
| Entrada Flask con conmutador encendido y Next disponible | 302 hacia `http://127.0.0.1:3000/` |
| Página Next real | 200 |
| API directa y proxy Next | Igual snapshot sintético; 28 amenazas |
| Estado de análisis en la fixture | Admisión manual apagada y LLM no preparado |
| Entrada tras terminar el proceso Next propio | 200, 357,4 ms |
| API Flask tras caída de Next | 200 |
| Reporte tras caída de Next | 200 |
| Reinicio de la fixture con conmutador apagado | 200 sin redirección |

La medición es puntual, no p95 ni rendimiento de producción. El contenido,
los históricos y los identificadores del ensayo eran sintéticos. No se
repitió aquí una auditoría visual/accesibilidad en navegador; se conservan
las verificaciones previas y la confirmación de uso del usuario.

Resultado local en `.local-state/phase7/checks/return-20261006T184753621946Z.json`.
Para repetir:

```powershell
.venv/Scripts/python.exe -B scripts/check_phase7_return.py
```

El build por defecto es `.local-state/delivery2-frontend`, creado en entrega 2;
no es una dependencia versionada del producto. Si falta, preparar otra copia
aislada con las mismas fuentes/dependencias, proxy a 5000 y sin `.env`, o
indicarla con `--build`. No se debe apuntar al directorio operativo del usuario.

## Respaldo operativo nuevo

`scripts/backup_operational.py` complementa al script histórico de fase 0,
que solo cubría `logs/` y `reports/`. El nuevo respaldo admite perfiles fijos
según el contrato y las tareas locales conocidas:

| Perfil | Log | Reportes | Registro de trabajos |
|---|---|---|---|
| legacy | `logs/access.log` | `reports/**/*.md` | `.local-state/analysis.sqlite3` |
| pilot | `.local-state/dvwa-lab/access.log` | `.local-state/phase6-pilot/reports/**/*.md` | `.local-state/phase6-pilot/analysis.sqlite3` |

El perfil `all`, predeterminado, incluye ambos. No lee `.env` ni descubre
rutas a partir de sus claves. Si la instalación utiliza rutas personalizadas
distintas, esas rutas no están cubiertas automáticamente: revisar el listado
y extender explícitamente el perfil en una tarea antes de afirmar cobertura.

El script adquiere bloqueos cycle/engine para impedir escritores coordinados,
vuelve a enumerar fuentes bajo bloqueo y rechaza trabajos queued/running.
No recupera ni altera trabajos. Los archivos deben pasar captura estable;
no se siguen symlinks, junctions ni rutas externas. SQLite se abre en modo
solo lectura, fija una transacción de lectura y usa la API de backup, con
presupuesto de 30 s e integrity_check. Incluye commits presentes en WAL sin
copiar un fichero SQLite vivo a ciegas ni transportar locks/WAL/SHM.
El worker puede actualizar su heartbeat; la copia SQLite corresponde a la
instantánea de lectura. Escritores ajenos que ignoren los bloqueos no están
coordinados por este mecanismo; los archivos solo se garantizan estables
individualmente. No se promete una transacción universal entre todos los datos.

Cada copia nueva tiene ZIP, manifiesto SHA-256, snapshots SQLite auxiliares y
una restauración de comprobación en un directorio nuevo `restore-check`.
Solo se publica `operational.zip` con `verified=true` después de restaurar,
comprobar hashes y verificar integridad SQLite. Si falla, se conservan los
artefactos parciales con `verified=false`, sin eliminar fuentes ni publicar
una copia verificada. La restauración rechaza directorios existentes, rutas
que escapen, contenido alterado y miembros duplicados o no previstos.

La ejecución real de esta entrega creó una copia local de **47 archivos**:
logs, reportes actuales/históricos y registro SQLite del piloto. Los hashes
y la restauración pasaron. La base legacy `.local-state/analysis.sqlite3`
no existía y se registró expresamente como ausente; no se creó ni se inventó.
Ubicación: `.local-backups/operational-20261006T184950593361Z`.
Su contenido no se publica ni se adjunta al chat.

Para revisar cobertura y hacer una nueva copia:

```powershell
.venv/Scripts/python.exe -B scripts/backup_operational.py --list
.venv/Scripts/python.exe -B scripts/backup_operational.py
# Solo datos del piloto:
.venv/Scripts/python.exe -B scripts/backup_operational.py --profile pilot
```

Si hay un análisis activo o un bloqueo, esperar a una ventana sin trabajos;
no forzar el bloqueo ni reconciliar SQLite para conseguir un respaldo.
Los comandos no inician análisis ni notificaciones. Solo copian fuentes a
un destino nuevo y realizan una restauración aislada; no restauran en vivo.

## Política de conservación y recuperación

Crear una copia verificada antes de cambiar esquema de datos, publicación
del motor o rutas operativas. Mantener las copias versionadas locales sin
borrado automático durante la evolución A-01–A-05. Revisar espacio disponible
y decidir una limpieza mediante tarea explícita si es necesario; esta entrega
no activa la función de borrado antigua ni impone retención destructiva.

Los logs y reportes pueden contener información sensible: ZIP, snapshots,
restauración y manifiesto permanecen en `.local-backups`, excluido de Git.
No se añade exportación a nube ni respaldo de claves. `.env`, imágenes,
volúmenes Docker, configuración Mailpit y su buzón efímero no se incluyen.
La base DVWA y el buzón requieren una estrategia separada si se necesita
conservar el laboratorio completo. Las tres entregas SMTP históricas `unknown`
se conservan como tales; la copia de SQLite no recupera correos desaparecidos.

Para recuperación real, detener admisión/ejecutor y servidores que escriban,
verificar el manifiesto y restaurar primero en un destino nuevo. Comparar
rutas/estado y decidir el cambio de datos en una tarea concreta. No copiar
automáticamente sobre fuentes operativas o sobre SQLite con procesos activos.
La restauración aislada realizada hoy es evidencia del archivo recuperable,
no una sustitución del almacenamiento del usuario.

## Validación y compatibilidad

- Suite: 134 pruebas Python, 0 fallos/expected failures y 3 diagnósticos JS.
- Sintaxis: 40 archivos, 0 errores.
- Ensayo real de entrada/retorno con fixture: aprobado; servidores propios cerrados.
- Respaldo real: 47 archivos y SQLite del piloto, restauración/hash/integridad aprobados.
- Pruebas nuevas: WAL, persistencia de `unknown`, conservación de fuentes,
  copias sin sobrescritura, bloqueo/estado activo, fuente cambiante, enlaces,
  archivo alterado y escape de restauración.
- No se cambian fuentes React o dependencias; no se repiten lint/build/audit
  ya verificados en entrega 2. El ensayo utiliza aquel build.

Se mantienen API, contratos de reportes, motor, prompts, modelos, `.env`,
intérprete operativo y conmutadores. La copia usa locks cooperativos y puede
crear sus ficheros de bloqueo, sin escribir estados de análisis ni contenido
en las fuentes. No se reiniciaron procesos del usuario ni se hicieron envíos,
llamadas LLM, operación Docker, commit o publicación.

## Reversión y siguiente entrega

Los cambios de esta entrega son scripts, pruebas y estado documental.
Retirarlos no cambia fuentes ni configuración del producto. Conservar las
copias locales si se revierte código; no borrar recuperación como parte de
una reversión. El retorno a Flask sigue siendo iniciar la aplicación local
con `NEXT_PRIMARY_ENABLED=0`, sin borrar datos ni modificar proveedores.

La siguiente línea es A-01/A-02: contratos de evidencia y resultado y prototipo
aislado de salidas estructuradas, manteniendo API y adaptación Markdown histórica.
Siguen pendientes la transición de `.venv`, braces de desarrollo sin parche,
regresión de efectos frontend y garantías de calidad del motor A-03–A-05.
El cierre local de fase 7 no acredita esas mejoras ni un despliegue compartido.

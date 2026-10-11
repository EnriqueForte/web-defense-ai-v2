# A-05 — Propuesta concreta de activación local reversible

Seguimiento más reciente: [diagnóstico real del 10/10](DIAGNOSTICO_REAL_A05_2026_10_10.md)
verificado, revisión operativa anterior aceptada por el usuario. A-05 sigue abierta
por la omisión observada en la detección; botón manual desactivado y worker
restaurado con nueva identidad. No ampliar llamadas a partir de esta acta.

Estado vigente 10/10/2026: la [operación del Paso 2](OPERACION_A05_2026_10_10.md)
inició el mismo piloto en `.p3` con el contrato nuevo y Next 16.3.8, sin análisis
nuevos. Los comandos `.p2`, PID y resultados de abajo son históricos; comprobar
el estado vigente antes de repetirlos. A-05 sigue abierta por aceptación final.

Fecha: 07/10/2026. **Aceptada y ejecutada localmente.** No cierra A-05.
El usuario pidió continuar con pendientes; esta entrega prepara la operación
para que la aceptación sea una decisión sobre rutas, procesos y límites concretos.

## Resultado de la activación aceptada

El usuario aceptó el perfil y el alcance en Codex. El 07/10/2026 a las 13:01 UTC
se creó `.local-backups/operational-20261007T130119779538Z`: 17 archivos,
restauración aislada, hashes e integridad SQLite verificados. Después se
arrancaron Flask y el ejecutor con `.p2`, profile=pilot y mode=structured,
usando los comandos descritos abajo, en procesos sin ventana visible.
Lanzadores: Flask PID 37260 y worker PID 34812; son identificadores de esta
sesión, no comandos para detener procesos futuros que reutilicen esos PID.

La comprobación del 07/10/2026 a las 13:02:48 UTC confirmó:

- `/api/v1/salud`, `/api/v1/estado`, `/api/v1/reportes` y
  `/api/v1/analisis/actual` respondieron HTTP 200; ejecutor online y heartbeat actual.
- manual_enabled=false, cero trabajos activos y todos los registros de trabajos
  iguales al respaldo previo. Logs y reportes mantienen sus hashes.
- current.json structured sigue ausente. La API devuelve report.status=error
  y salud unavailable para esta ausencia; HTTP 200 no significa salud completa.
- No se lanzó un análisis, sincronización Docker o notificación. `.env` permanece
  sin modificar; los límites del perfil se aplican mediante variables de proceso.

Recibos locales: `.local-state/a05-activation/activation-20261007T1301Z/activation.json`
y `verification.json`. La observación es puntual; no garantiza disponibilidad
continua ni arranque automático al reiniciar Windows. El primer análisis del
coordinador y su consumo de proveedor requieren definir/autorizar su alcance.

## Evidencia y alcance propuesto

Seguimiento: el usuario autorizó después el primer análisis del coordinador;
terminó succeeded en 157 s, con generación/histórico/API verificados, salud ok,
manual desactivado y sin notificaciones. Docker fue recuperado y el ejecutor
propio reiniciado con permisos de acceso; su lanzador vigente es PID 37076.
La ausencia inicial del informe descrita aquí ya quedó resuelta por esa
publicación, sin copiar fixtures. Véase
[primer análisis y límites](PRIMER_ANALISIS_COORDINADOR_A05.md).

El lote real de siete casos cumplió expectativas de familias con 23 de 42
llamadas autorizadas. El caso normal tardó 475,829 s y su narrativa original era
«1»; el formato sin hallazgos se corrigió a resumen de Python. La siguiente
medición autorizada de structured-prototype-5 pasó en 24 s con dos llamadas de
detección (un reintento), clasificación/narrativa locales y guardas/hashes válidos.
No es p95 ni comparación con modelos idénticos. Véanse
[evaluación ampliada](EVALUACION_AMPLIADA_A05_2026_10_07.md) y
[optimización](OPTIMIZACION_A05_SIN_HALLAZGOS.md).

Se propone usar el **perfil piloto existente** y el intérprete `.p2` validado:

| Parámetro | Valor compartido por Flask, ejecutor y su motor hijo |
| --- | --- |
| ANALYSIS_ENGINE_MODE | structured |
| LOG_PATH | .local-state/dvwa-lab/access.log, absoluto |
| REPORT_PATH | .local-state/phase6-pilot/reports, absoluto |
| ANALYSIS_DB_PATH | .local-state/phase6-pilot/analysis.sqlite3, absoluto |
| LOG_SYNC_SOURCE | dvwa-lab |
| ANALYSIS_MANUAL_ENABLED | 0 |
| NOTIFICATION_DESTINATIONS | vacío |
| Modo del ejecutor | --manual-only |

No hay ciclos programados, solicitudes manuales nuevas desde el dashboard ni
notificaciones en este arranque. No se cambia el proveedor, credencial o modelo
guardados. No se modifica `.env`, el frontend, NEXT_PRIMARY_ENABLED, tareas de
VSCode existentes o el repositorio original. Las rutas legacy fuera del piloto
se preservan. El mismo lanzador permite seleccionar profile=legacy, pero esa
selección sería otra decisión operativa, no el alcance recomendado aquí.

**Consecuencia visible:** todavía no existe current.json operativo structured
en ese perfil. La lectura del informe estará no disponible hasta un primer
análisis válido autorizado por separado. No se copian reportes sintéticos o
históricos como si fueran un análisis nuevo. Para usar después el análisis
manual habría que habilitarlo expresamente en Flask; el lanzador de esta
entrega lo mantiene desactivado. Este arranque no verifica todavía Docker,
autenticación del proveedor o ejecución real de un trabajo del coordinador.

## Comprobación previa y herramienta preparada

`scripts/local_runtime_profile.py` no inicia nada por defecto. Produce un plan
con comandos de argumentos estructurados y variables compartidas sin leer o
imprimir `.env`/credenciales. `--start` es obligatorio para arrancar **un solo**
componente después del preflight. El modo predeterminado es legacy.

Preflight realizado con `.p2`, profile=pilot y mode=structured:

- 155 paquetes fijados, cero diferencias; `.venv` conserva cuatro diferencias.
- worker/cycle/engine libres, queued=0/running=0 y SQLite consultada en modo ro.
- puerto 5000 disponible; no se crean bloqueos o bases que no existen.
- fuente estructurada ausente, condición prevista del primer arranque.
- ready=true para esos requisitos de arranque, **no** para cerrar evaluación.

Evidencia: `.local-state/a05-activation/preflight-20261007.json`.
Es una instantánea y no una reserva atómica. Si cambia cualquier condición,
se repite el preflight antes de arrancar. El helper rechaza diferencias de
dependencias, procesos/bloqueos activos o desconocidos, trabajos en cola/en
ejecución, DB no consultable, puerto ocupado para Flask y puntero inválido.
Rechaza enlaces/junctions en rutas; también se corrigió el lector generacional
para rechazar un current.json enlazado antes de leer su destino.
El preflight del retorno a legacy también pasó, con el informe anterior
disponible. Ese modo no lee el puntero structured, por lo que un defecto en
ese puntero no impide preparar el retorno.

## Procedimiento aplicado tras la aceptación operativa

No ejecutar automáticamente estos comandos como comprobación de desarrollo.
El arranque descrito se ejecutó tras la aceptación del usuario; repetirlo exige
comprobar que los componentes anteriores estén detenidos. VSCode es opcional.

1. Confirmar aceptación de los resultados y límites, del perfil piloto y del
   arranque con manual/notificaciones desactivados. Si se exige comparación
   real legacy o más repeticiones, acordar su presupuesto primero.
2. Detener únicamente los componentes de esta instalación, sin cancelar un
   trabajo activo. Repetir preflight y tomar respaldo del perfil con
   `scripts/backup_operational.py --profile pilot`, verificando restauración.
3. En una sesión, después del respaldo y con autorización:

```powershell
.p2/Scripts/python.exe -B scripts/local_runtime_profile.py --profile pilot --mode structured --component flask --start
```

4. En otra sesión, arrancar el ejecutor manual; no iniciar otro sobre el mismo
   SQLite ni cambiar sus rutas. La comprobación del worker no requiere que el
   puerto Flask esté libre, puesto que Flask ya debe estar funcionando:

```powershell
.p2/Scripts/python.exe -B scripts/local_runtime_profile.py --profile pilot --mode structured --component worker --start
```

5. Comprobar lectura/estado del ejecutor por `/api/v1`, Loopback y conservación
   del informe legacy. Mantener el informe structured como ausente hasta que
   se autorice su primer trabajo real. No usar el saldo del lote para ese trabajo.

## Retorno concreto

Detener los dos componentes iniciados por esta operación, esperando cualquier
trabajo activo si lo hubiera; conservar DB, logs, histórico y generaciones.
Repetir el mismo preflight/arranque en profile=pilot con `--mode legacy` para
ambos. Se vuelve al Markdown anterior del piloto, manteniendo `.p2` y las
protecciones manual/notificaciones apagadas. Para recuperar exactamente otro
perfil/intérprete previo, usar sus tareas anteriores tras revisar sus rutas:
la migración de `.venv` no está incluida. No restaurar encima ni borrar datos
como parte del retorno rutinario. El respaldo se conserva para recuperación.

## Verificación y pendientes de cierre

223 pruebas Python aprobadas tanto en `.venv` como en `.p2`, tres diagnósticos
JS por ejecución, 17 escenarios CrewAI/LiteLLM aislados, sintaxis de 64 archivos
y diff sin errores. La cobertura nueva comprueba plan sin procesos, arranque
explícito con mock, rechazo por DB/trabajos/lock/puerto/entorno/puntero, ausencia
de secretos en salida y lectura de symlink bloqueada. Estos mocks no equivalen
a arrancar servicios, consultar Docker o ejecutar el motor con un proveedor.

La aceptación y el arranque local están completados. Quedan observación
operativa y aceptación final; la primera prueba real del ejecutor se completó
posteriormente según el seguimiento anterior. Las cuatro
diferencias de `.venv` y braces sin parche conservan seguimiento independiente.
No se retira Flask ni se amplía la observación parcial histórica de fases 6/7.

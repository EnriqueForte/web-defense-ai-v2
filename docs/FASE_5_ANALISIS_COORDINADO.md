# Fase 5 — Análisis coordinado

Estado: implementación local verificada con dobles de prueba. La activación con
Docker, Groq y destinos de notificación reales queda para el piloto controlado
de la fase 6; no se ha ejecutado el motor real durante esta entrega.

## Cambio entregado

- `pipeline.py` es ahora el único ejecutor programado. El análisis manual y el
  periódico entran en la misma cola SQLite; un índice único impide dos trabajos
  `queued`/`running` y un bloqueo de proceso impide dos ejecutores en el mismo
  equipo. `main.py` toma otro bloqueo durante el análisis, también cuando se
  inicia directamente.
- El registro local `.local-state/analysis.sqlite3` persiste identificador,
  origen, fase, tiempos y resultado, sin guardar logs, reportes ni secretos.
  `.local-state/` está excluido de Git. Un reinicio marca un trabajo `running`
  como `interrupted`; no lo presenta como completado ni lo reintenta a ciegas.
- `POST /api/v1/analisis` exige `Idempotency-Key`, ejecutor observado y
  `ANALYSIS_MANUAL_ENABLED=1`. Devuelve 202 para una solicitud nueva o repetida
  con la misma clave, 409 ante otro trabajo activo y 503 si el ejecutor está
  desconectado. `GET /api/v1/analisis/actual` y `/{id}` permiten observar
  estado y resultado tras recargar la página. La API admite POST solo desde
  loopback y rechaza orígenes de navegador ajenos a la consola local.
- Next.js muestra el estado real del ejecutor y del último trabajo; el botón
  solo se habilita cuando corresponde. Nunca interpreta 202 como análisis
  completado. Ante error de red no reintenta automáticamente la mutación.
- La sincronización publica el log atómicamente. Solo se acepta éxito si
  `main.py` terminó bien y publicó un reporte nuevo, estable y no vacío. El
  historial conserva una copia por trabajo. Las alertas usan severidades de
  la misma tabla que el dashboard y registran una tentativa por destino antes
  de enviar; una entrega incierta queda `unknown` y no se reenvía a ciegas.
- La sincronización anterior de Flask devuelve 409 mientras el ejecutor está
  activo. Un bloqueo de ciclo evita que una sincronización ya iniciada cruce
  la lectura y publicación de un trabajo nuevo.

## Puesta en marcha controlada

1. Detener cualquier proceso anterior de `pipeline.py`; esperar a que termine
   el ciclo activo y comprobar el último reporte. No iniciar dos pipelines.
2. Mantener `ANALYSIS_MANUAL_ENABLED=0` mientras se verifica lectura. Para el
   laboratorio local, cambiarla a `1` en `.env` y reiniciar Flask. No compartir
   esa consola fuera de `127.0.0.1`: la autenticación central corresponde a
   la fase 6.
3. Iniciar Flask y Next.js con la tarea **lectura conectada** de VSCode.
   Iniciar el ejecutor explícitamente en otra terminal desde la raíz:

   ```powershell
   .\.venv\Scripts\python.exe -B pipeline.py
   ```

   El ejecutor inicia el primer ciclo periódico al arrancar y luego usa
   `INTERVALO_MINUTOS`. Los ciclos y el botón pueden contactar Docker, Groq,
   Telegram y SMTP; no usar ese comando como prueba rutinaria.

4. En el piloto, verificar reporte nuevo, archivo histórico, estado del trabajo
   y destinos de prueba. Si un envío queda `unknown`, conciliar con el
   destinatario antes de decidir otro envío.

## Validación y límites

La suite aislada cubre simultaneidad de solicitudes, idempotencia, exclusión
del segundo ejecutor, recuperación de un trabajo interrumpido, respuesta API,
ausencia de notificación cuando no hay reporte nuevo y una sola tentativa por
destino. Usa un reporte sintético y transmisores simulados. ESLint, tipos y build
de Next.js se comprueban sin iniciar el laboratorio.

SQLite y los bloqueos son para un solo equipo y disco local, no para varios
nodos o unidades compartidas. La entrega exactamente una vez a Telegram/SMTP
no es demostrable sin confirmación del receptor; `unknown` evita reintentos
automáticos. El contenido del reporte aún depende del motor CrewAI anterior;
la validación semántica de evidencia y esquema sigue en A-01–A-04. El reporte
actual puede haber sido publicado antes de un fallo posterior de historial o
notificación: el trabajo se marca fallido y requiere conciliación, sin
sobrescribir la última salida. El piloto de fase 6 debe cubrir apagados durante
un subproceso, carga, permisos, autenticación, destinos de prueba y retorno.

## Compatibilidad y reversión

Las rutas GET de fase 2, la UI de lectura de fase 4 y el dashboard Flask siguen
disponibles. Para desactivar la acción manual, poner
`ANALYSIS_MANUAL_ENABLED=0` y reiniciar Flask. Para detener ciclos, parar el
ejecutor; un trabajo en curso se reconcilia antes de restaurar un programador
anterior. No borrar `.local-state/` ni los históricos al revertir. Si se
retorna a la versión anterior de `pipeline.py`, mantener solo ese programador
activo y conservar la base SQLite como registro de auditoría local.

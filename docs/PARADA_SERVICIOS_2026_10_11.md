# Parada local solicitada — 11/10/2026

El usuario pidió detener el servidor activo y liberar puertos antes de una
posterior tarea de commit y push. **Next, Flask y el worker manual-only están
detenidos. No se hizo commit ni push en esta operación.**

Se comprobaron ejecutable, argumentos, creación y parentesco de las cadenas
propias del proyecto: Flask 15840→19388→33696→29408, worker
32856→10616→32520→4592 y Next 3632. Se identificaron también sus tres procesos
conhost auxiliares (20140, 28904, 36820); no se incluyeron terminales, Codex,
navegadores o servicios ajenos. Estos PID son ahora **históricos**.

SQLite se consultó en modo solo lectura: cero queued/running antes de detener
y de nuevo antes de parar el worker. Se cerraron los árboles propios con
taskkill /T /F, con sus identidades comprobadas, y se verificó que ninguno de
los procesos identificados continuaba presente. No había análisis en curso
que interrumpir. Los archivos de lock se conservan; sus bloqueos worker/cycle
están libres.

Comprobación de bind local IPv4 tras la parada: **3000, 5000, 4280, 8025, 1025
y 8080 libres**. Los puertos del laboratorio ya no tenían listener observado;
no se invocó Docker ni se modificaron contenedores, volúmenes o su configuración.
La comprobación no afirma el estado interno de un laboratorio en otra VM.

Filas de 29 trabajos y 14 entregas, hashes del log/puntero/report/result y
metadatos `.env` iguales antes/después. No se borraron logs, informes,
respaldos, SQLite o builds. Tampoco se modificaron proveedores, modelos,
conmutadores persistentes o fuentes funcionales.

Recibos excluidos de Git en `.local-state/shutdown-20261011/`:
`processes-before.json`, `invariants-before.json`, `invariants-guard.json`,
`invariants-after.json` y `ports-after.json`. Los scripts de esta operación
utilizan las identidades verificadas de ese momento; no son lanzadores de
uso general y no deben repetirse con PID históricos.

Los registros de activación/refresco anteriores describen estados históricos
con servicios activos. El estado vigente tras esta petición es **servicios
detenidos**. No arrancarlos para preparar Git; la revisión, selección de fuentes,
commit y push corresponden a la siguiente tarea solicitada por el usuario.

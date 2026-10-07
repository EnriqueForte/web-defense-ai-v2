# R-18 — Lecturas validadas, acotadas y sin solapamiento

Entrega del 07/10/2026. Alcance: lecturas de Next.js y aplicación segura de
sus respuestas. No cambia el motor, API, SQLite, proveedor o configuración.

## Comportamiento implementado

getApi valida el contrato de cada ruta antes de entregar datos al componente:
estado, amenazas, catálogo/detalle de informes, estado/detalle de trabajos y
configuración LLM. Comprueba sobres, campos consumidos, listas, números enteros
no negativos, identificadores y fechas con zona/calendario válido. Los campos
opcionales de intervalos y vista del informe se conservan. Tolera campos
adicionales para compatibilidad, pero no omisiones o tipos inválidos en campos
que la consola necesita. Una ruta nueva necesita su validador explícito.

Las lecturas tienen presupuesto de 10 s para petición y cuerpo JSON. El timeout
aborta el controlador local y se muestra como error legible, aunque un transporte
simulado ignore el aborto o nunca entregue el cuerpo. Los listeners/timers se
liberan tras completar/cancelar. Las respuestas tardías no se aplican. Esto
no constituye una cancelación de un trabajo del coordinador en el servidor.

Los canales estado y análisis usan sondeo por finalización: espera 15 s y 5 s,
respectivamente, después de completar la lectura anterior. El disparo por volver
a una pestaña visible comparte la consulta en curso. Cada canal tiene como máximo
una lectura activa; los dos canales son independientes. La pestaña oculta no
inicia nuevos sondeos. Detener el efecto aborta su lectura y elimina el timer;
un error no impide el siguiente sondeo. La consulta posterior a una creación
manual usa el mismo ciclo, sin invocar en paralelo un segundo lector de análisis.

La consola conserva la última captura válida al fallar una lectura, muestra
«Sin lectura» y el error, y recupera el estado cuando llega una respuesta válida.
No atribuye automáticamente una respuesta inválida a pérdida de conexión.
Configuración tampoco aplica una respuesta después de desmontarse.

Las respuestas de guardado/configuración y creación de job también se validan
antes de presentarse como éxito. Su transporte de escritura no recibe reintentos
automáticos ni el timeout de las lecturas; una respuesta fallida no demuestra
que el servidor no haya ejecutado una escritura. La idempotencia previa del
análisis y su instrucción de consultar estado antes de reintentar se conservan.

## Evidencia

14 grupos de regresión de UI aprobados, TypeScript, ESLint y diff sin errores.
La suite usa fixtures sintéticas y fetch sustituido por dobles. Incluye:

- Contratos válidos de las siete rutas, sobres/data nulos, tipos inesperados,
  NaN, fecha imposible y detalle con ID distinto al solicitado.
- Transporte que no responde, JSON que nunca termina, JSON inválido, respuesta
  incompleta, aborto tardío y siguiente lectura válida.
- Lectura lenta mientras llegan disparos de sondeo/visibilidad: sin solapamiento;
  siguiente lectura tras completar, stop durante vuelo y ausencia de nuevos timers.
- Recuperación después de fallo y pausa/reanudación por visibilidad.

Siete respuestas de la API local real devolvieron HTTP 200 y pasaron los nuevos
validadores. El recibo contiene solo rutas/HTTP/resultado, sin cuerpos ni claves:
`.local-state/a05-activation/read-robustness-20261007/contracts.json`.
En navegador real se comprobó Resumen, Amenazas (cinco coincidencias), detalle
report.md y lectura de Configuración; no se guardó configuración ni se pulsó
Iniciar análisis. La pestaña temporal se cerró conservando la del usuario.

No se ejecutó otro análisis, llamada LLM, Docker, notificación, recaptura,
republicación o reinicio de servicios Python. Next cargó los cambios del frontend.
La última suite backend sigue siendo la de 228 casos documentada en R-14;
esta entrega no cambia Python ni pretende aportar nuevos casos backend.

## Límites, compatibilidad y reversión

R-18 queda implementada para este alcance de lecturas. Los fallos y las carreras
se reprodujeron con dobles: no se apagó la conexión real ni se simuló toda la
aplicación React bajo cada fallo. No es una prueba de carga, auditoría general
de todos los valores semánticos ni cambio del presupuesto de análisis LLM.
Los límites de escritura/operación y aceptación final A-05 conservan su alcance.

La reversión es de frontend: retirar validadores/deadline y restablecer sondeos
anteriores. No necesita cambiar endpoints, credenciales, informes o recuperar DB.
La API y sus campos adicionales de fechas permanecen compatibles.

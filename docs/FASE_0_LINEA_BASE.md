# web-defense-ai V2 — Fase 0: línea base

Fecha: 27/09/2026. Estado: **completada para el entorno local Windows/Python 3.11**.
Punto de partida: `6be08bb`. No se ha iniciado la fase 1 ni la implementación de Next.js.
Responsable: Codex, trabajo secuencial sin subagentes. F0-01 y F0-02 completadas.

## Entrega y aceptación

- Dataset sintético en `tests/fixtures/traffic.json`: tráfico normal, cinco familias,
  cuerpo POST ausente y entrada malformada. Las etiquetas describen indicadores;
  no confirman éxito de ataques. IP de documentación, sin datos operativos.
- `tests/test_baseline.py`: 18 casos, **10 aprobados y 8 fallos esperados**.
  Incluye umbral/ventana de ráfagas, selección de últimas 100 líneas, muestra de
  cinco altas, prioridad de comandos, archivos vacíos/ausentes y contrato JSON actual.
- `tests/browser_baseline.cjs`: tres diagnósticos con **tres fallos conocidos**.
  Dobles de DOM/Marked; no constituye prueba de navegador ni de ejecución XSS.
- `scripts/check_baseline.py`: combina ambas comprobaciones, rechaza cero pruebas,
  Node ausente, fallos inesperados y correcciones que aún conserven la marca pendiente.
- `.vscode/tasks.json`: nueva tarea de línea base, sin arranque automático.
- Dependencias del dashboard declaradas; `requirements.txt` convertido de UTF-16
  a UTF-8 y pywin32 restringido a Windows. No se actualizaron versiones del motor.
- Instalación mínima y posteriormente completa realizadas en un entorno nuevo
  `.local-backups/phase0-test-env`, sin cambiar `.venv`. Ambas pasaron `pip check`.
  `constraints-windows-py311.txt` registra las versiones completas instaladas.
- Copia y restauración de 30 archivos locales `.log`/`.md`, con SHA-256 coincidente.

Un resultado `OK (expected failures=8)` significa que la línea base se reproduce,
**no que la herramienta esté libre de fallos**. Las correcciones deben retirar las
marcas correspondientes y conservar las aserciones de comportamiento deseado.

## Repetir la verificación

Desde la raíz, con Python 3.11 y Node disponibles:

```powershell
python -m venv .local-backups/phase0-test-env
.local-backups/phase0-test-env/Scripts/python.exe -m pip install -r requirements-test.txt
.local-backups/phase0-test-env/Scripts/python.exe -B scripts/check_baseline.py
.local-backups/phase0-test-env/Scripts/python.exe -B scripts/check_syntax.py
```

Para reproducir también las dependencias completas verificadas en Windows:

```powershell
.local-backups/phase0-test-env/Scripts/python.exe -m pip install -r requirements.txt -c constraints-windows-py311.txt
.local-backups/phase0-test-env/Scripts/python.exe -m pip check
```

No hace falta crear `.env`. Los tests desactivan su carga, vacían el entorno dentro
de cada caso y sustituyen conexiones/procesos externos; archivos y reportes son
temporales. No se importa `main.py` ni se arranca CrewAI. El ensayo usa unittest de
la biblioteca estándar; no se añadió pytest porque no es necesario para estos casos.
Node usa módulos estándar, sin instalar dependencias JavaScript.

Versiones observadas: Python 3.11.9, Node 24.19.0, Flask 3.1.3, Werkzeug 3.1.8,
CrewAI 1.14.2, python-dotenv 1.1.1. Última ejecución en entorno completo: 18 casos
Python en 0,161 s; sintaxis de 16 archivos sin errores. Es tiempo de tests aislados,
no latencia de IA, Docker ni carga multiusuario. No se midió rendimiento productivo.
La instalación completa se comprobó realmente; la resolución previa con `--dry-run`
por sí sola no fue utilizada como prueba de instalación.

## Catálogo de fallos pendientes

| Hallazgo | Reproducción incorporada | Siguiente corrección |
|---|---|---|
| H01 | Sincronización simulada anuncia análisis nuevo | Mensaje y acción acordes a lo ejecutado |
| H02 | Dashboard sin reporte lanza error de plantilla | Estado vacío válido |
| H03 | Alias de refresco apunta a su propia función | Unificar actualización y evitar recursión |
| H04 | HTML sintético llega a innerHTML en log y reporte | Texto seguro y renderizado restringido; ampliar a navegador real |
| H05 | Consulta GET llama Docker; Docker ausente lanza excepción | Consulta sin efectos y estado de ingestión explícito |
| H06 | BAJA se cuenta como MEDIA | Recuento por categorías |
| H07 | Celda vacía desplaza estado/IP | Preservar posiciones |
| H08 | IP desconocida se sustituye por la más frecuente | Conservar evidencia ausente |
| H09 | 01/May se ordena antes de 30/Apr | Orden temporal real |

La cobertura es representativa, no exhaustiva: el timestamp atribuido al reporte
actual, IPv6/IP inválidas, solapamiento de categorías, concurrencia, política de
notificaciones y renderizado en navegador requieren ampliación en sus tareas.
No se evaluó precisión del LLM ni prompts con respuestas reales. La caracterización
del truncado documenta una limitación actual, no aprueba su suficiencia analítica.

## Flujos y configuración efectiva por inspección

| Entrada / variable | Comportamiento existente |
|---|---|
| `main.py` | Preprocesado → tres agentes secuenciales → reporte Markdown; dos caminos de escritura |
| `pipeline.py` | Copia Docker → motor como proceso → historial/avisos → espera |
| `/` y `/report/<nombre>` | Lectura de reportes y HTML; el índice también lee logs |
| `/api/estado` | Copia Docker antes de construir JSON; se reproduce con doble |
| `/api/sincronizar` | Copia, reutiliza reporte, archiva y puede notificar; no ejecuta nuevo análisis |
| `LOG_PATH`, `REPORT_PATH` | Consumidos por aplicación; reporter concatena ruta y exige separador final |
| `LLM_MODEL`, `LLM_TEMPERATURE` | Declarados en settings; flujo principal usa modelos y temperatura fijados en código |
| `MAX_LINEAS_LOG`, `UMBRAL_FUERZA_BRUTA` | Declarados, pero preprocesador usa límite 100 y umbral por defecto 5 |
| `INTERVALO_MINUTOS` | Pipeline lo consume; ejemplo 2, valor por defecto 3 |
| Groq, Telegram y SMTP | Configuración sensible no leída ni validada en esta fase |

## Respaldo, compatibilidad y reversión

`scripts/backup_baseline.py` crea una copia nueva cada vez de `.log` y `.md` bajo
`logs/` y `reports/`, excluye enlaces externos, restaura en subdirectorio separado
y verifica hashes. No incluye `.env`, bases Docker ni otras extensiones. Se debe
ejecutar con productores detenidos si se requiere una instantánea coherente de todos
los archivos durante actividad; este ensayo verifica integridad archivo a archivo.

Ensayo local guardado en `.local-backups/phase0-data-20260927T180950226150Z/`:
`operational.zip`, `manifest.json` y `restored/`. Las copias y el entorno nuevo están
excluidos de Git. Los originales no se sobrescribieron. El respaldo previo de Git
sigue disponible según `REPOSITORIOS.md`.

No se cambió lógica operativa, prompts, rutas ni formato de reportes. La reversión
consiste en retirar los archivos de prueba/configuración de esta entrega o recuperar
los archivos modificados desde `6be08bb`, preservando cambios posteriores y datos.
No es necesario restaurar logs para revertir esta fase. No restaurar copias encima
de datos más recientes sin revisar previamente las diferencias.

## Siguiente fase

Fase 1: estabilizar la interfaz Flask mediante H01–H09 y ampliar las pruebas de cada
corrección. Mantener IA/prompts separados. La nueva interfaz Next.js empieza en fase 3,
después de estabilizar el contrato de datos en fase 2. Esta entrega no inicia esas fases.

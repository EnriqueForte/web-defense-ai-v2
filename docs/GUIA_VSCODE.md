# web-defense-ai V2 — Seguimiento del desarrollo en VSCode

El desarrollo se realiza en Codex. VSCode abre la misma carpeta y permite
seguir las modificaciones, revisar diferencias y consultar la documentación.
No es necesario copiar ni exportar el proyecto entre aplicaciones.

## Abrir y seguir los cambios

1. En VSCode, usar **Archivo → Abrir área de trabajo desde archivo** y elegir
   `web-defense-ai V2.code-workspace` en la raíz del proyecto.
2. Abrir los archivos que se quieran seguir. Los cambios externos en archivos
   sin modificaciones pendientes se reflejan en el editor. Evitar editar el
   mismo archivo mientras Codex lo modifica; si hay cambios locales sin guardar,
   revisar las diferencias antes de sobrescribir.
3. Usar **Control de código fuente** para ver los archivos modificados y su diff.
   Los archivos nuevos aparecerán sin seguimiento hasta que se incorporen a Git.
4. Usar **Ctrl+Shift+V** para la vista previa de un documento Markdown.

El remoto `origin` apunta a `EnriqueForte/web-defense-ai-v2`. El original se
conserva como `original-readonly`, con envíos bloqueados en esta copia. La rama
`main` de V2 utiliza `origin/main` para sincronizar. Comprobar siempre que el
destino es V2. La separación se documenta en `docs/REPOSITORIOS.md`.

El guardado automático y el formato al guardar están desactivados en este
proyecto para evitar modificaciones involuntarias durante la revisión. El
formato manual sigue disponible con la extensión recomendada.

## Configuración preparada

| Archivo | Contenido |
|---|---|
| `web-defense-ai V2.code-workspace` | Raíz y nombre del espacio de trabajo |
| `.vscode/settings.json` | Intérprete local, UTF-8, formato manual y exclusiones |
| `.vscode/extensions.json` | Recomendaciones de Python, Pylance, depurador, Black y YAML |
| `.vscode/tasks.json` | Comprobación de sintaxis y dashboard local con recarga |
| `.vscode/launch.json` | Depuración de dashboard, análisis real y pipeline por separado |
| `scripts/check_syntax.py` | Comprobación estática sin importar el motor |

Las extensiones se recomiendan, no se instalan automáticamente. Seleccionar
`.venv/Scripts/python.exe` mediante **Python: Select Interpreter**. La ruta
predeterminada está adaptada al entorno Windows de este proyecto; si VSCode ya
tiene otro intérprete guardado, hay que cambiar esa selección explícitamente.
En otro sistema operativo, seleccionar su intérprete equivalente.
Las tareas Python del proyecto invocan directamente `.venv/Scripts/python.exe`
desde PowerShell; seleccionar el intérprete en el editor sirve para análisis y
depuración, pero no cambia el ejecutable de esas tareas. Si falta `.venv`, crear
el entorno e instalar las dependencias antes de iniciarlas.

Las exclusiones de búsqueda reducen ruido y evitan mostrar datos operativos
en búsquedas habituales; no impiden abrir archivos ni son una barrera de acceso
para asistentes o terminales. `.env.example` sigue disponible en el explorador.

## Comprobar el proyecto

**Terminal → Ejecutar tarea → web-defense-ai V2: verificar sintaxis Python**.
También puede lanzarse con **Ctrl+Shift+B**. Comprueba la raíz y las carpetas
Python del proyecto, incluida `scripts/`, sin iniciar Docker, IA o notificaciones.
Devuelve un error si encuentra sintaxis inválida. No equivale a pruebas
funcionales. La tarea **web-defense-ai V2: verificar regresión aislada** ejecuta
la suite Python y los diagnósticos JavaScript de fase 0. Requiere las dependencias
de `requirements-test.txt` y Node en PATH. La suite actual comprueba las
correcciones de fases 1 y 2 con datos sintéticos; no ejecuta el laboratorio real.
Véanse `FASE_0_LINEA_BASE.md` y `FASE_2_API_LECTURA.md`.

## Visualizar la aplicación actual

Ejecutar la tarea **web-defense-ai V2: dashboard con recarga local** y abrir
[el dashboard local](http://127.0.0.1:5000) en un navegador. La tarea mantiene
el servidor activo hasta detenerlo desde la terminal o el menú de tareas.
Escucha solo en la máquina local y desactiva el depurador web de Flask.

Flask recarga el proceso cuando detecta cambios Python; al cambiar HTML o CSS,
actualizar la página del navegador. La interfaz Next.js tiene recarga de desarrollo
y consulta los datos de Flask mediante `/api/v1`.

Para depurar con puntos de interrupción, seleccionar **web-defense-ai V2:
dashboard local** y pulsar **F5**. Este perfil no usa recarga de proceso;
reiniciar la depuración tras modificar Python. No iniciar tarea y depuración
al mismo tiempo en el puerto 5000. Los perfiles de análisis y pipeline son
operaciones reales, claramente separadas.

La consulta de estado del dashboard existente ya no sincroniza logs desde Docker.
La sincronización es una acción separada y no ejecuta un análisis nuevo; la vista
sin reporte también está corregida. Flask muestra los archivos locales disponibles,
no un modo de datos simulados. El análisis manual coordinado sigue pendiente.

## Visualizar la nueva interfaz Next.js

La tarea **web-defense-ai V2: interfaz Next.js de lectura** inicia la UI en
`http://127.0.0.1:3000`, aislada de la red local. Usa Node 24 o posterior y las
dependencias ya instaladas en `frontend/node_modules`; las tareas ejecutan las
herramientas locales mediante `.vscode/run-frontend.ps1`, sin requerir `pnpm` en
el PATH de VSCode. El script busca Node en el PATH, en las instalaciones habituales
de Windows y en el runtime local de Codex. Si no encuentra Node, instala Node.js 24
o posterior y vuelve a abrir VSCode. Para ver datos del backend, ejecutar
**web-defense-ai V2: lectura conectada (Flask + Next.js)**, que inicia también Flask
en `127.0.0.1:5000`. Si Flask no responde, la UI muestra el error y conserva la
última captura disponible. No requiere iniciar Docker, CrewAI ni notificaciones.
La tarea **verificar frontend** ejecuta ESLint, **comprobar tipos frontend** valida
TypeScript y **compilar frontend** crea una build de producción. Ninguna se ejecuta
al abrir VSCode. Resumen, amenazas, reportes y actividad leen `/api/v1`; el análisis
manual y la coordinación periódica corresponden a la fase 5. El contrato y los
límites están en `FASE_4_LECTURA_CONECTADA.md`.

La estructura actual está bajo `frontend/src/app/`; su propio `AGENTS.md` conserva
la guía de desarrollo generada por la versión instalada de Next.js. La distribución
Python permanece en la raíz para no alterar imports o rutas del motor.

## Referencias

La depuración usa `debugpy` y una configuración por proceso, conforme a la
[documentación de Python para VSCode](https://code.visualstudio.com/docs/python/debugging).
Los atajos se definen como tareas de proceso con directorio explícito y sin
arranque al abrir la carpeta, siguiendo el [sistema de tareas de VSCode](https://code.visualstudio.com/docs/debugtest/tasks).
Black se configura como proveedor de formato independiente, según la
[documentación de formato Python](https://code.visualstudio.com/docs/python/formatting).

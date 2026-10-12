# Instalador y arranque simplificados — 12/10/2026

Se añade `webdefense.py install|start|check`, con guía de usuario en
[Inicio rápido](INICIO_RAPIDO.md). El usuario ya no necesita ejecutar por separado
la instalación del backend/frontend, el build y las dos terminales de lectura.
Los requisitos globales Python 3.11, Node 24 y pnpm 11.19.0 siguen siendo previos.

## Comportamiento

- `install` descubre Python 3.11 con venv/ensurepip, valida Node/pnpm y utiliza el
  instalador común con `--install --frontend --build --init-env`. Mantiene el
  contrato compartido y configura el build para el proxy loopback 5000.
- Bloquea instalación concurrente con el lanzador, puertos ocupados, bloqueos
  worker/cycle/engine existentes y trabajos queued/running en ambos perfiles.
  SQLite se consulta de solo lectura. No borra ni recrea un entorno existente.
- `start` usa `.p2` y el perfil pilot/legacy de lectura. Comprueba el build y su
  rewrite, contrato y bloqueos. Inicia Flask, verifica salud, inicia Next y espera
  respuesta API por proxy y página HTTP200 antes de declarar la consola lista.
- `check` ejecuta solo el preflight. Modo structured opcional para lectura;
  no worker, análisis manual, ciclos o notificaciones activados.
- Ctrl+C cierra los procesos propios. En Windows, un [Job Object](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) con cierre de
  descendientes; en POSIX, sesiones/grupos propios. Una compuerta Python base
  espera a tener propietario antes de ejecutar las aplicaciones, evitando
  descendientes prematuros del redirector de venv Windows. El transporte de
  argumentos usa subprocess en Windows para preservar rutas con espacios.
- Una caída o timeout provoca limpieza y salida no exitosa. No se matan
  procesos encontrados por nombre o por ocupar puertos.
- Logs por ejecución bajo `.local-state/launcher`, ignorados por Git.
  La lógica del lanzador no lee ni imprime el contenido de `.env`.

## Validación

Suite final: 285 pruebas Python y tres comprobaciones JavaScript aprobadas
en `.p3`; 77 archivos sin errores de sintaxis y `git diff --check` correcto.

Pruebas añadidas para herramientas incorrectas/ausentes, error de instalación/
build, conservación de configuración y base con análisis activo, puerto ocupado,
build ausente/proxy erróneo, preflight sin arranque, caída del segundo componente,
timeout y cierre real de descendientes sintéticos después de salir su padre.

Ensayo Windows en `.i1`, copia aislada con dependencias previamente instaladas:
el nuevo comando `install` pasó contrato/pip check, instalación frontend y build
Next16.3.8; `.env` existente preservado. No es otra instalación desde cero.
Se utilizó el pnpm11.19.0 ya aislado del ensayo anterior; el pnpm11.25.0 del
runtime de herramientas fue rechazado correctamente por el chequeo inicial.

Smoke con `check_application_start.py --isolated-root .i1`: consola lista,
Flask5000/proxyNext3000 HTTP200, ejecutor offline y cierre por señal de consola
con ambos puertos libres, comprobado antes de la limpieza de respaldo del ensayo.
El script rechaza copias con bases/logs operativos. No se ejecutó el motor.

Recibos en `.local-state/launcher-20261012/` y
`.i1/.local-state/launcher-smoke/result.json`. Comparación de invariantes antes/
después: 29 trabajos, 14 entregas, cero activos, hashes de log/publicación y
metadatos de `.env` operativos intactos. No se arrancaron servicios operativos
del mantenedor. Los servicios de ensayo quedaron detenidos.

## Publicación y validación remota

El commit `c82441cc054746a013f2b71321c099b93f6d8ddd` se publicó en `origin/main`
del repositorio V2. La [ejecución 38234970879](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38234970879)
terminó con success en su primer intento, tanto en Windows-latest como en Ubuntu
24.04. Los estados y los logs finales se revisaron antes de indicar la actualización
en Parrot.

Ambos runners completaron instalación nueva mediante `webdefense.py install`,
pip check, contrato sin diferencias (158 pines Windows/157 Linux), build Next,
77 archivos de sintaxis, 285 Python/tres JS, HTTP sintético, 25 escenarios SDK,
lint/tipos y 15 grupos UI. El smoke del comando unificado confirmó API directa/
proxy HTTP200, ejecutor offline y cierre con puertos libres en ambas plataformas.
Recibos `actions-c82441cc054746a013f2b71321c099b93f6d8ddd.json` y
`ci-successful-checks.json` bajo el directorio local de esta entrega.

El nuevo comando fue probado después en la VM del usuario: instalación, arranque,
navegación y cierre con puertos libres después de esperar. El aviso de puerto
ocupado tras cerrar y su corrección publicada `2a73ff0` se documentan en
[el seguimiento Parrot](VALIDACION_PARROT_2026_10_12.md) y
[el ajuste de puertos](CORRECCION_PUERTOS_2026_10_12.md).
El ajuste pasó después en Windows/Ubuntu CI (run38237671713), incluyendo la
regresión TIME_WAIT Linux. El usuario confirmó después el recorrido guiado en Parrot;
su captura muestra check/start/Ctrl+C/check correctos, según el seguimiento enlazado.
La actualización documental `f8318d6` llevó `[skip ci]`; no se atribuye
una nueva ejecución al commit que únicamente registra el resultado anterior.

## Límites y reversión

No incluye instalación automática de herramientas globales, Docker/DVWA,
configuración del proveedor ni activación del análisis. No es un servicio de
sistema. POSIX depende de una parada normal o señal atendida; SIGKILL al supervisor
no puede ejecutar su limpieza. No garantiza recuperación ante caída del sistema.
Para volver al procedimiento anterior, utiliza `local_runtime_profile.py` y
`pnpm run start` en terminales separadas; el nuevo comando debe estar detenido.
El instalador anterior conserva por defecto su plan sin ejecutar ni compilar.

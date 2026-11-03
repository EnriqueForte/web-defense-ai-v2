# Revisión integral del proyecto — 03/11/2026

Fecha: 03/11/2026, Europe/Madrid. Revisión local de estructura, código,
contratos, documentación y evidencias registradas, solicitada por el propietario.

**Dictamen actualizado tras decisión del propietario:** F4/F5/F6 cerradas por
decisión expresa de alcance, con verificaciones omitidas; matriz F7 aceptada
en su alcance educativo. Las decisiones de fases están resueltas, sin declarar
cumplimiento íntegro de las verificaciones originales F0–F7. Resta consolidación/
aceptación final del conjunto. V2 v0.1.0 conserva su aceptación local anterior.
El [registro de decisiones](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md) prevalece
sobre los antecedentes de revisión que siguen.

**Decisión posterior del 03/11:** el propietario cierra F6 y decide no realizar
sus pruebas restantes porque bloquean la conversación. La fase queda cerrada
por decisión expresa de alcance, con verificaciones omitidas/no acreditadas,
sin declararlas aprobadas. Se retiran sus propuestas del trabajo pendiente.
Se continúa revisión documental sin ejecutar pruebas; F4/F5/F7 y la aceptación
global conservan sus estados. Detalle en el [registro de cierre F6](PUERTO_UMBRAL_CIERRE_MINIMO_2026_11_03.md).

**Recepción documental posterior:** revisión F7 completada sin pruebas,
con cotejo de los once identificadores del acta, mapa de diez categorías y
dictamen documental F7-AC1/2/3. La matriz queda lista para aceptación final
del propietario; no se añade validación operativa o detección de categorías.

## Estado de cierre y limitaciones conservadas

| Bloque | Pendiente concreto | Evidencia existente que se conserva |
| --- | --- | --- |
| F5: cerrada por decisión expresa de alcance | Evaluación, búsqueda de originales y desarrollo/validación pendiente del ejecutor/puntuador retirados del trabajo de esta entrega, sin más pruebas | Índice histórico y preparación conservados; cinco tests del empaquetador no ejecutados. Originales sin localizar y métricas sin medir; no se puntúa el informe de 17 líneas como corpus completo |
| F6: cerrada por decisión del propietario | Sin trabajo de pruebas restante: Bitácora/Preferencias vulnerables, resultado vulnerable de Baliza y regresión F6 no verificados quedan omitidos por decisión expresa del 03/11 | Cargas/Atraque, controles corregidos y revisión de contrato se conservan; cierre de fase con límites, sin afirmar validación íntegra de los criterios originales |
| F2/F3: cobertura acotada | Documentar el alcance de evidencia existente; planes/preflight no acreditan todos los endpoints o pipeline. No se ejecutan nuevas regresiones bajo la instrucción actual | Cinco pruebas del lanzador, cinco del observador y cinco de separación de perfiles ya pasaron con permisos independientes. Comandos normal corregido y vulnerable representativo verificados sin `Cannot fork` |
| F4: cerrada por decisión expresa de alcance | Pruebas restantes omitidas, sin ensayo adicional; rotación/discontinuidad real conserva estado no verificado | Veinte muestras API y desviación F4-AC1 aceptada; desconexión/reinicio/captura recuperada/snapshot anterior conservado completados. No se convierten en prueba de rotación |
| Entrega y aceptación | Matriz F7 aceptada y decisiones de fases resueltas; queda consolidación/aceptación final del conjunto y publicación cuando se solicite | Once recorridos F7 y tres criterios revisados documentalmente; interfaces y lanzador recibidos. No se afirma detección completa OWASP o validación exhaustiva |

F5-AC2 mantiene los objetivos originales: al menos **27/30 intentos**, **5/6
por familia** y **0 falsas alarmas entre 15 benignos**. Son objetivos, no
resultados obtenidos. El ejecutor y puntuador propios de esa evaluación quedan
sin completar y fuera del trabajo de cierre acordado; las utilidades sintéticas V2 no demuestran
por sí solas esos resultados de Puerto Umbral.

El detalle vinculante está en el [PRD](PRD_PUERTO_UMBRAL_2026_10_26.md), la
[auditoría](PUERTO_UMBRAL_AUDITORIA_CIERRE_2026_10_31.md), el
[plan mínimo](PUERTO_UMBRAL_CIERRE_MINIMO_2026_11_03.md) y el
[protocolo F5](PUERTO_UMBRAL_EVALUACION_F5_2026_11_02.md).
Ninguna ejecución nueva queda autorizada por esta revisión.
La revisión documental F5 posterior está completada en el protocolo enlazado:
separación de resultados funcionales y métricas, procedencia, herramientas y
estado de sus cinco criterios. F5 queda después cerrada por decisión expresa,
sin ejecutar su evaluación o pruebas. Los estados previos «abierta/pendiente»
de los antecedentes describen la preparación anterior a ese cierre.

## Alcance técnico revisado

Se inventarían los archivos fuente y de configuración fuera de dependencias,
entornos, builds, datos operativos y respaldos. Se comprueban estáticamente
todos los Python inventariados, JSON estricto, imports internos absolutos y
destinos de enlaces Markdown locales. Se revisan los puntos de entrada y las
rutas críticas de instalación, perfiles, API local, publicación estructurada,
captura/seguimiento y auditoría de aplicación; se cotejan sus límites con las
actas. También se revisan configuración y referencias del frontend, scripts
de validación y definición de CI.

No se importa el motor ni se ejecutan suites, builds, HTTP, escenarios,
proveedores, servicios o Docker. No se lee `.env` ni el contenido de logs,
SQLite, capturas o respaldos operativos; tampoco se opera Git. Las recepciones
de Parrot son evidencia registrada del propietario, sin inspección nueva de
la VM por el agente. Esta revisión estática no certifica funcionamiento
actual, seguridad exhaustiva ni ausencia de defectos.

| Comprobación estática | Resultado |
| --- | --- |
| Sintaxis Python, incluidos laboratorio y tests | 124 archivos analizados mediante AST; 0 errores |
| Imports internos absolutos de los paquetes del proyecto | 0 destinos ausentes entre los imports comprobados; no valida imports dinámicos o disponibilidad de paquetes externos |
| Imports relativos/alias locales TypeScript y JavaScript | 18 destinos comprobados; 0 ausentes. No sustituye comprobación de tipos o compilación |
| JSON | 24 archivos de JSON estricto válidos; `frontend/tsconfig.json` usa JSON con comentarios y se excluye de este parser |
| API implementada y contrato | 16 operaciones de negocio coinciden en ruta/método con OpenAPI, aplicando su servidor `/api/v1`; el endpoint que sirve el propio contrato se trata aparte |
| Referencias a SVG de plantilla retirados | Sin referencias en código, configuración, pruebas o documentación del inventario; no se requieren para el arranque |
| Enlaces Markdown locales | 601 referencias de archivo comprobadas, 0 destinos ausentes; 22 referencias absolutas del plan histórico convertidas a rutas relativas, conservando la indicación de línea histórica. No comprueba URLs externas o anclas de sección |

No se ejecuta TypeScript, ESLint o CI en este paso; sus resultados anteriores
mantienen su fecha. No se afirma que las dependencias estén libres de avisos
actuales: el tratamiento residual previo conserva su alcance y no se ha hecho
una auditoría de red nueva.

## Estructura y limpieza

La separación principal es coherente; se conserva para evitar romper rutas
de importación, lanzadores, perfiles, Compose, tests y documentación.

| Ubicación | Responsabilidad y decisión |
| --- | --- |
| `webdefensev2.py`, `webdefense.py` | Entrada conjunta y lanzador reutilizado; ambos necesarios |
| `main.py`, `pipeline.py`, `agents/`, `config/` | Motor, coordinación, contratos y configuración Python |
| `dashboard/` | API Flask, servicios y dashboard alternativo conservado para compatibilidad |
| `frontend/` | Interfaz Next.js/React y sus contratos; se retiran únicamente los assets de plantilla sin uso |
| `labs/puerto_umbral/` | Laboratorio educativo separado, código y fixtures ficticios; sus datos locales no se reorganizan |
| `scripts/`, `tests/`, `.github/` | Instalación, operación, validación y CI; los nombres históricos no prueban que una utilidad esté en desuso |
| `docs/`, `screenshots/` | Guías, actas, índices de evidencia y capturas de producto; nuevo [índice documental](README.md) por tarea y estado |
| `requirements*.txt`, `constraints*.txt`, Compose | Contratos de instalación/plataforma y compatibilidad; conservar snapshots históricos, no deducir duplicidad solo por el nombre |
| `.p2`, otros entornos, `node_modules`, `.next` | Dependencias y salida local; no se borran sin acreditar que están fuera de uso. El lanzador requiere el build de Next.js |
| `.local-state`, `.local-backups`, `logs`, `reports`, `.env` | Estado, evidencia, recuperación y configuración del propietario; no son limpieza descartable |

Se eliminan exactamente cinco archivos de `frontend/public/`: `file.svg`,
`globe.svg`, `next.svg`, `vercel.svg` y `window.svg`, **3.314 bytes** en total.
Eran recursos de la plantilla inicial sin referencias. El favicon real de
`frontend/src/app/` se conserva. `frontend/CLAUDE.md` remite a `AGENTS.md` y se
conserva como archivo de instrucciones, no como código sobrante.

Se corrigen cabeceras, fecha objetivo y resúmenes que seguían presentando como
pendientes el despliegue de catorce contenedores, comandos representativos,
Atraque o verificaciones ya recibidas. Se distinguen las entregas anteriores
de la referencia publicada del 03/11, sin volver a verificar remoto o VM.
Las cronologías y los JSON históricos no cambian sus resultados.

No se requiere una migración de carpetas del runtime para cerrar. Como mejora
posterior de mantenimiento, `dashboard/app.py` concentra 1.075 líneas; separarlo
en módulos de rutas podría facilitar su lectura, pero exige regresión propia
y no se añade ahora como requisito de aceptación. El índice reduce la confusión
documental sin mover actas enlazadas o alterar contratos operativos.

La reversión de esta limpieza consiste en restaurar los cinco SVG y los cambios
documentales desde la copia/versionado del propietario. No se crea otro backup,
commit o release por esta revisión.

# Revisión actual de web-defense-ai V2 — 08/10/2026

## Dictamen

La base del proyecto pasa la regresión actual y dispone de motor estructurado,
coordinación local, API Flask, consola Next y retorno Flask. El trabajo restante
se concentra en estabilización, aceptación operativa y distribución verificable.
No hace falta rehacer la arquitectura ni repetir A-01–A-04 o la fase 7 local.

Hay un cambio relevante frente a la revisión anterior: la auditoría de producción
ya **no está limpia**. El registro actual devuelve seis avisos para Next 16.3.6,
uno alto, cuatro moderados y uno bajo. Desarrollo añade el aviso alto de braces.
Debe resolverse o justificarse cada aviso antes de la entrega final, distinguiendo
versiones afectadas de condiciones explotables en esta aplicación.

A-05 permanece abierta: la activación y el primer job real ya se hicieron el
07/10, pero faltan carga operativa del diagnóstico nuevo, observación y aceptación
final. Linux/Parrot todavía no tiene instalación real acreditada. El workflow
preparado no acredita ejecuciones aprobadas.

## Alcance y estado Git

Revisión sobre `main`, HEAD `b9726be`, con 17 entradas modificadas y 12 entradas
sin seguimiento al comenzar; las entradas de directorio agrupan varios archivos.
Se preservaron esos cambios. `origin` apunta a `EnriqueForte/web-defense-ai-v2`;
`original-readonly` conserva el push bloqueado. La referencia local `origin/main`
coincide con HEAD; no se hizo fetch ni se verificó el estado remoto actual,
visibilidad, Actions o releases en GitHub.

Se inspeccionaron código y contratos del motor/coordinador, configuración,
cliente API/polling, cabeceras, instalación, CI, Compose, dependencias, pruebas
y actas. Se repitieron verificaciones aisladas y audit npm. No se leyó `.env`
operativo ni contenido de logs/reportes del piloto, no se ejecutaron análisis LLM,
Docker o notificaciones reales, ni se reiniciaron servicios operativos.

Esta revisión añade este informe y un resumen en AGENTS.md. No cambia producto,
prompts, versiones, configuración local o datos. Los recibos y copia de build
están en `.local-state/review-20261008/`, excluido de Git. No hay commit o push
realizado por esta revisión.

## Verificación del 08/10

| Comprobación | Resultado | Límite |
|---|---|---|
| Sintaxis Python | 69 archivos, cero errores | Sin importar el motor |
| Baseline `.p2` | 254 pruebas aprobadas; cero expected failures | Fixtures/dobles |
| Baseline `.venv` | 254 pruebas aprobadas; cero expected failures | No acredita coincidencia de versiones |
| JavaScript Flask | Tres comprobaciones aprobadas en cada baseline | Casos definidos de XSS, Markdown y timeline |
| Metadatos `.p2` | 155 pines, cero diferencias | Entorno existente, no clonación limpia nueva |
| Metadatos `.venv` | 155 pines, cuatro diferencias | aiohttp, importlib-metadata, jsonschema y openai |
| `pip check` | Ambos entornos sin conflictos declarados | No equivale a audit de vulnerabilidades |
| Frontend | ESLint, TypeScript sin emisión y 14 grupos UI aprobados | Render/helpers/dobles; no E2E completo de efectos |
| Build Next 16.3.6 | Aprobado, rutas `/` y `/_not-found` estáticas | Copia aislada con dependencias existentes |
| CrewAI/LiteLLM | 18 escenarios offline aprobados | Completado simulado, conexiones a proveedor bloqueadas |
| Adaptador OpenRouter | Legacy/structured y límites 8192/60 verificados | Sin call/kickoff o proveedor real |
| HTTP sintético | Flask, CSP, informe, vendor y hashes aprobados | Puerto libre y servidor efímero propio |
| Audit npm producción | 6 avisos: 1 alto, 4 moderados, 1 bajo; 0 críticos | Según registro consultado hoy |
| Audit npm completo | 7 avisos: 2 altos, 4 moderados, 1 bajo; 0 críticos | Añade braces de herramientas de desarrollo |
| `git diff --check` | Sin errores | Advertencias de conversión LF/CRLF existentes |

El sandbox rechazó reemplazos atómicos en temporales y enlaces de dependencias.
Las suites pasaron al repetirlas fuera de ese aislamiento con permiso; los fallos
iniciales no se atribuyen al producto. El primer ensayo SDK restringido no terminó
y fue interrumpido; la repetición acotada fuera del sandbox pasó. La consulta npm
restringida falló por red y se repitió con permiso.

El build usa una copia de fuentes/configuración, sin `.env` ni `.next` originales,
y un enlace a node_modules existente. Solo en esa copia se amplía turbopack.root
al padre común para resolver el enlace, según la documentación incluida con Next.
No es una instalación limpia ni certifica la copia que una persona clonará.

## R-03 reabierta: dependencias y avisos actuales

`frontend/package.json` mantiene next y eslint-config-next 16.3.6. El audit actual
señala 16.3.8 como umbral corregido de los seis avisos de Next. Los overrides de
source-map-js 1.2.2 y sharp 0.35.5 siguen presentes y no aparecen como avisos en
los recibos actuales. Esa corrección anterior sigue siendo válida.

| Aviso Next | Nivel | Condiciones y lectura del proyecto |
|---|---|---|
| [SSRF en Image Optimization](https://github.com/vercel/next.js/security/advisories/GHSA-cjq9-62q9-8jv4) | Alto | El mantenedor excluye apps sin images.remotePatterns. La configuración actual no los define; no se demuestra este camino vulnerable en la app |
| [Cache poisoning Pages Router SSG/ISR](https://github.com/advisories/GHSA-4jqv-mc3x-m676) | Moderado | El proyecto usa App Router; no hay Pages Router observado |
| [Cache poisoning con catch-all raíz](https://github.com/vercel/next.js/security/advisories/GHSA-mcj8-r9mp-w47p) | Moderado | No hay página catch-all raíz observada |
| [Metadatos de imágenes/dynamicParams](https://github.com/vercel/next.js/security/advisories/GHSA-f87g-xv8r-7p7x) | Moderado | No hay esas rutas dinámicas observadas |
| [Draft Mode/use cache](https://github.com/vercel/next.js/security/advisories/GHSA-3w37-wq28-93x7) | Moderado | No se observan Draft Mode, use cache ni cacheComponents |
| [MCP del servidor de desarrollo](https://github.com/vercel/next.js/security/advisories/GHSA-39w2-rjm5-chcv) | Bajo | El proyecto permite next dev; requiere revisar este alcance aunque use loopback |

La aplicabilidad anterior procede de inspección de fuentes/configuración y
condiciones del mantenedor; no es un ensayo de explotación ni una certificación
global de ausencia de riesgo. Actualizar de forma compatible Next y su configuración
ESLint, regenerar el lockfile y repetir audit/lint/tipos/UI/build es la primera
entrega recomendada. No se aplica esa actualización como parte de esta revisión.

El aviso [braces](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) continúa en
desarrollo. Hay discrepancia entre la versión corregida sugerida por npm y la
ficha GitHub, que muestra ausencia de parche. Verificar publicación real y
alternativas compatibles antes de añadir un override; no inventar la versión.

Falta auditoría actual de dependencias Python, recursos Chart.js/marked vendorizados
y de imágenes del laboratorio. pip check y los hashes de vendor no sustituyen esas
auditorías. No se instala pip-audit ni se inicia Docker en esta revisión.

## Estado consolidado de lo ya implementado

| Área / referencia anterior | Estado actual y límites |
|---|---|
| Migración 0–7 / F7-01 | Cerrada para alcance local reversible; conserva los límites de observación aceptados |
| Rediseño UI 1–8 | Completado; zoom real al 200 % confirmado históricamente |
| A-01–A-04 / R-05–R-07, R-10–R-13 | Contratos, selección UTC, criterios, guardas y publicación implementados en structured; no trasladar estas garantías al motor legacy |
| A-05 | Integración, evaluación y activación ya realizadas; primer job real exitoso documentado. Cierre final pendiente |
| R-01/R-02/R-09 | Correcciones de rutas/origen/diagnósticos cubiertas por regresión |
| R-04 | Extra LiteLLM declarado y adaptadores verificados offline |
| R-08 | SMTP y presupuesto por destino acotados; no envíos reales nuevos |
| R-14 | Refresco por identidad de publicación y aborto corregidos/cubiertos |
| R-15 | Backend/factory y helpers del cliente cubiertos; E2E de montaje/guardado/desmontaje de Configuración y efectos completos sigue sin acreditarse por los 14 grupos |
| R-16 | `.p2` conforme y contrato compartido; `.venv` discordante, configuración global y clonación limpia pendientes |
| R-17 | Lint completo y CI preparados; matriz real sin evidencia de ejecución |
| R-18 | Validadores, plazo de lectura, cancelación y polling sin solapamiento implementados y cubiertos con dobles |
| R-19 | Respaldo/restauración de la aplicación verificados históricamente; volumen DVWA y buzón Mailpit fuera de cobertura |
| R-20 | Compose anterior marcado legacy; laboratorio recomendado local. No se revisaron imágenes con scanner hoy |
| R-21 | Host/cuerpo/errores/cabeceras y vendor locales implementados; CSP de Next sigue parcial |
| R-22 | Resúmenes mejorados, pero tablas y párrafos históricos mezclan estados superados con actuales |

La guía mantiene legacy como configuración de instalación nueva. En ese modo
continúan sus límites de parsing, criterios y selección. El piloto structured no
convierte en structured las instalaciones que usen los valores predeterminados.
La revisión debe expresar esta diferencia al presentar las garantías de la versión.

## Pendientes y criterios de cierre

| Orden | Trabajo | Evidencia necesaria para cerrarlo |
|---|---|---|
| 1 | Actualización/auditoría de dependencias | Resolver avisos Next con versión publicada compatible; justificar o corregir braces; repetir comprobaciones y auditar Python/vendor/imágenes |
| 2 | Cierre operativo A-05 | Cargar diagnóstico en worker propio y cabeceras nuevas en los servicios necesarios mediante operación documentada; observación y aceptación final del usuario. Cualquier nueva llamada requiere alcance autorizado |
| 3 | Instalación limpia final | Clon/copia final sin entornos locales en Windows y Ubuntu; instalador, pins/pip check, baseline, HTTP, SDK offline, build/start y retorno aprobados |
| 4 | Parrot OS en VMware | Registrar versión, arquitectura y herramientas; repetir instalación y lectura desde navegador dentro de la VM, disco local y sin entornos Windows reutilizados |
| 5 | Reproducibilidad y configuración | Elegir `.p2` como referencia coherente o migrar `.venv` en tarea propia; validar configuración global y comprobar coherencia de rutas de arranque/recuperación |
| 6 | Documentación y recuperación | Tabla actual única de fases/hallazgos, política de datos y cobertura explícita del laboratorio; documentación final alineada con la distribución |
| 7 | Entrega GitHub | Auditar contenido e historial, integrar todos los archivos nuevos necesarios, CI Windows/Ubuntu aprobada, versión y publicación al destino V2 |

Para A-05, el primer job del 07/10 duró 157 s y publicó cinco grupos. Es evidencia
histórica, no se repitió hoy. No tiene métricas retroactivas por llamada/tokens.
Los recibos nuevos requieren cargar la parte coordinadora en el worker; no inferir
que el proceso activo ya la tenga. No reutilizar PIDs históricos sin comprobar
identidad y ausencia de jobs activos. El timeout documentado no garantiza terminar
todos los descendientes. La comparación de pocas ejecuciones tampoco acredita p95
o calidad general de cualquier tráfico.

Para R-16, `config/settings.py:18–23` mantiene conversiones directas float/int al
importar. Un valor inválido puede impedir cargar el worker antes de una validación
comprensible. Es un pendiente conservado por inspección, no un nuevo fallo operativo
reproducido hoy. Structured sí usa MAX_LINEAS_LOG y UMBRAL_FUERZA_BRUTA validados
en evidence_preparation; no conservar la afirmación antigua de que esos parámetros
se ignoran en todo el producto.

Para R-22, `docs/PLAN_AGENTES_TAREAS.md:231–235` aún etiqueta contratos como no
integrados y activación como pendiente; la fila 254 conserva A-01 pendiente.
README y la revisión del 06/10 acumulan resultados históricos que necesitan un
resumen vigente inequívoco. No reescribir actas para inventar pruebas o aceptación;
añadir estado actual y marcar los apartados antiguos como históricos.

El inventario de rutas versionadas muestra `.env` y datos locales excluidos; en
logs/reports solo se siguen `.gitkeep`. En el inventario de nombres de las refs
locales consultadas también aparecen solo `.env.example` y esos marcadores para
estas rutas. Esto no es un escaneo de secretos en contenidos de archivos/historial,
ni cubre capturas, otras rutas o estado remoto: la revisión previa a publicación
sigue pendiente. No se mostraron secretos en el chat.

La cobertura de recuperación de la app no incluye `.env`, volúmenes Docker o
buzón Mailpit. Si se requiere recuperar el laboratorio completo, definir y ensayar
esa cobertura por separado. No activar limpieza o cambiar entregas unknown sin
evidencia. CSP completa de scripts en Next, retención automatizada y ampliación a
otras arquitecturas/sistemas son mejoras condicionadas al alcance, no cierres ya
implementados ni requisitos inventados de un dashboard público central.

## Compatibilidad y reversión de esta revisión

Se conservan Python/CrewAI, Flask, contratos API, conmutadores, proveedores,
datos y configuración. No hay cambio operativo que revertir. Para retirar esta
entrega documental basta eliminar este informe y su resumen de AGENTS.md,
preservando todos los cambios previos del usuario. Los recibos locales no se
publican; no se borran fuentes, respaldos o históricos.

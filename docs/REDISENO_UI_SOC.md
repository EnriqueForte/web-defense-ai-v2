# Rediseño SOC — web-defense-ai V2

## Alcance y diagnóstico (01/10/2026)

Este plan visual es independiente de las fases de migración: la fase 7 de
migración continúa abierta. Las fases UI 1–6 están completadas.
Las referencias aportadas orientan la densidad, jerarquía, paneles oscuros y
acentos de una consola SOC; no se reproducen sus marcas ni métricas ajenas.

El frontend existente usa Next.js 16.3.6, React 19.2.8, TypeScript y Tailwind 4,
con componentes propios y CSS global. No tiene shadcn/ui ni Recharts. UI 3 incorpora Lucide React 1.49.0.
La consulta periódica sigue siendo de 15 segundos para estado y 5 para análisis.
Se conservan filtros en URL, paginación, capturas consistentes y guardas de análisis.
No existen `.cursor/agents/` ni `.agents/` en esta copia; el desarrollo sigue en
Codex y VSCode permite revisar sus archivos.

El contrato ofrece amenazas del reporte, severidades, IP observadas,
coincidencias por periodo, actividad reciente y reportes. No ofrece MTTD,
MTTR, SLA, activos inventariados, incidentes resueltos ni variaciones porcentuales
comparables. No deben simularse estos indicadores. Una coincidencia no demuestra
un ataque exitoso y una IP observada no equivale a un atacante.

## Fases de UI

| Fase | Trabajo y aceptación | Estado |
|---|---|---|
| 1. Fundamentos | Tokens de color, tipografía, espaciado, superficies, foco y base adaptable; sin modificar contratos | Completada |
| 2. Estructura | Refinar navegación, cabecera y organización de vistas; conservar rutas, filtros y menú accesible | Completada |
| 3. Indicadores | Componentes KPI y Lucide con nombres accesibles; solo métricas disponibles | Completada |
| 4. Gráficos | Evaluar Recharts; distribución y series disponibles, estados vacíos y alternativa textual | Completada |
| 5. Tablas | Densidad, filtros, evidencias y reportes; conservar paginación y presentación segura de texto | Completada |
| 6. Adaptación y accesibilidad | Teclado, foco, reflujo equivalente a zoom 200 %, anchos intermedios y móvil; estados y contraste | Completada; zoom real confirmado por el usuario |
| 7. Regresión | Pruebas de componentes, filtros, vistas, estados vacíos/error y compilación final | Completada |
| 8. Seguridad y entrega | Revisar renderizado de datos no confiables, dependencias, límites locales y reversión | Completada el 01/10/2026 |

Cada fase debe pasar lint, tipos/compilación y comprobaciones proporcionales al
cambio antes de avanzar. Las bibliotecas propuestas se incorporarán cuando la
fase correspondiente justifique su uso; UI 3 añade únicamente Lucide, con versión exacta en el manifiesto y lockfile.

## Responsables

Codex principal implementa y es responsable de los archivos compartidos. En esta
entrega un agente de apoyo revisó arquitectura y riesgos en modo solo lectura.
Para las próximas fases, las tareas de revisión visual, accesibilidad y seguridad
pueden delegarse explícitamente; no se crean agentes automáticamente por este plan.
Estos roles de desarrollo son independientes de los agentes CrewAI del producto.

## Entrega de fase UI 1

- `frontend/src/app/tokens.css`: paleta navy/cian, severidades, escalas tipográficas,
  espacios, radios y movimiento centralizados.
- `frontend/src/app/globals.css`: superficies y controles coherentes, foco visible,
  movimiento reducido y cuadrícula de indicadores 4/2/1 según ancho. Eliminados
  estilos del antiguo mockup que ya no se utilizan.
- `frontend/src/app/layout.tsx`: color del navegador alineado con el fondo.
- Conservados componentes, API, motor, datos, configuración y dashboard Flask.

Validación: lint y compilación Next.js con verificación TypeScript aprobados;
suite aislada con 75 pruebas Python y 3 diagnósticos JavaScript aprobados.
En navegador, fixture sintético con 28 amenazas: escritorio 1440 × 1000 y móvil
390 × 844 sin desbordamiento del documento, menú móvil operativo y filtro Alta
con 14 resultados. La tabla mantiene desplazamiento dentro de su contenedor.
Contraste contra el panel: texto principal 16,11:1, secundario 11,26:1,
atenuado 7,76:1, cian 10,70:1 y borde de control 3,05:1. Estas mediciones no
sustituyen una auditoría de accesibilidad completa.

La comprobación visual utilizó los puertos temporales 3001/5051, sin ejecutar el
motor ni notificaciones; ambos procesos se detuvieron al terminar. La captura
local está en `.local-state/ui-review/soc-fase1-desktop.png` (no se publica).
Esta primera base todavía no incluía iconos, nuevos gráficos ni refinamiento
estructural; esas entregas se documentan en las fases posteriores.

## Compatibilidad y reversión

Los cambios son de presentación y compatibles con `/api/v1` existente. Para
revertir, restaurar únicamente los estilos y el color de `layout.tsx` desde la
revisión anterior, preservando cualquier trabajo posterior. No requiere cambiar
`.env`, históricos, laboratorio ni el conmutador de fase 7. El dashboard Flask
permanece disponible como retorno. Las entregas posteriores se describen abajo.

## Entrega de fase UI 2 (01/10/2026)

Cabecera fija, ubicación semántica, descripción específica de cada vista y etiqueta
explícita de última captura. El contenido principal dispone de enlace de salto;
al cambiar de vista el foco pasa al título y el título del navegador se actualiza.
El menú móvil incorpora fondo atenuado, cierre con Escape/botón/fondo, bloqueo del
contenido posterior y recorrido de foco limitado al menú. Al cerrar, el foco
regresa al botón de apertura; al ampliar a escritorio se cierra el panel móvil.

Se conservaron los parámetros URL, filtros, paginación, polling y guardas de
análisis. No se añadieron dependencias ni se modificó el backend. Archivos de
implementación: `page.tsx`, `globals.css` y el token de fondo superpuesto.

Validación: lint y compilación con TypeScript aprobados. Navegador con fixture
sintético en 390 × 844 y 1440 × 1000: apertura, foco inicial, Escape, retorno del
foco, recorrido inverso de teclado, navegación a Amenazas y filtro Alta con 14
resultados. Corregida una interferencia de la transición de visibilidad con el
foco inicial. Captura local: `.local-state/ui-review/soc-fase2-desktop.png`.
La revisión de accesibilidad se describe en UI 6; no se ejecutaron
análisis reales ni notificaciones. Para revertir esta fase, restaurar los cambios
de estructura y estilos correspondientes conservando la base de UI 1.

## Entrega de fase UI 3 (01/10/2026)

Componente reutilizable `frontend/src/components/metric-card.tsx` con tipado de
icono, tono y origen. Cada tarjeta presenta origen, nombre, cifra y explicación;
las cifras siguen usando los mismos campos y cálculos. Se usan listas de
definición para relacionar etiqueta y valor, con iconos decorativos ocultos a
lectores de pantalla y nombres textuales siempre visibles. No se añaden tendencias,
porcentajes, MTTD/MTTR ni datos inventados.

Lucide React 1.49.0 sustituye los glifos de las tarjetas, navegación, marca y
controles de menú/actualización. Importaciones explícitas; no se carga el catálogo
completo dinámicamente. `package.json` y `pnpm-lock.yaml` fijan la dependencia.

Validación: lint y build con TypeScript aprobados. Fixture sintético: las tarjetas
conservan 28 amenazas, 14 críticas/altas, 28 IP y 11 coincidencias. Revisión visual
1440 × 1000 y 390 × 844 sin desbordamiento del documento; móvil muestra una
columna y mantiene navegación. Captura en
`.local-state/ui-review/soc-fase3-desktop.png`. Pruebas sin motor ni notificaciones.
La revisión de accesibilidad se describe en UI 6 y la regresión integral está
prevista en UI 7. Backend y contrato API permanecen compatibles.

Reversión: restaurar las tarjetas e importaciones previas y sus estilos; retirar
Lucide del manifiesto y lockfile solo si no lo utilizan cambios posteriores.
Los servidores temporales de comprobación se detuvieron al finalizar.

## Entrega de fase UI 4 (01/10/2026)

`security-charts.tsx` separa los gráficos de la vista. Distribución circular SVG
con leyenda textual, cantidades y porcentajes calculados sobre la suma de las
cinco severidades. Barras por periodo con escala desde cero y etiquetas completas;
los intervalos ausentes no se rellenan. Un valor cero tiene altura cero, sin
mínimos visuales que sugieran actividad. Los periodos conservan el orden de la API.
Una tabla desplegable ofrece valores por periodo y categoría, y puede recorrerse
con teclado. Sin periodos se muestra un mensaje; sin amenazas, un anillo neutro.

Se evaluó Recharts y se mantuvo SVG/CSS: las dos visualizaciones actuales no
requieren otra dependencia. No hay interpolación temporal, comparativas inventadas
ni carga externa. Las etiquetas se renderizan como texto React, nunca como HTML.

Validación: lint y build/TypeScript aprobados. Cuatro comprobaciones puntuales de
renderizado cubren severidades vacías, reparto 14/14, escala con cero y tres
coincidencias, y etiqueta con HTML escapado. En navegador: fixture con 28 amenazas,
50 % alta y 50 % baja, 11 coincidencias, apertura de la tabla y revisión en
1440 × 1100 y 390 × 844. Captura local:
`.local-state/ui-review/soc-fase4-desktop.png`.

Compatible con la API actual; no cambia el motor. Reversión: restaurar los dos
bloques de gráficos y sus estilos previos, retirando el componente nuevo si ya
no se utiliza. La revisión de accesibilidad se describe en UI 6.
Los servidores temporales se detuvieron al terminar; no se ejecutó análisis real.

## Entrega de fase UI 5 (01/10/2026)

Tabla extraída a `threat-table.tsx`, con cabeceras semánticas, encabezado fijo,
desplazamiento propio accesible por teclado y referencias desplegables. Estas
muestran los identificadores completos de amenaza y reporte de origen disponibles
en el contrato; no se inventa un cuerpo de evidencia ni se infiere éxito del ataque.
Se conservan IP, clasificación, estado y fecha disponibles, con alternativas para
campos ausentes. Los datos permanecen como texto React.

Filtros activos visibles y botón Limpiar filtros (restablece la primera página).
Paginación con rango y total, estado vacío explicativo y controles deshabilitados
en los límites. Reporte seleccionado con `aria-pressed`; lectura de reportes y
logs con foco para desplazamiento por teclado. Sin nuevas dependencias o cambios
al backend, polling, solicitudes de análisis o contrato de URL.

Validación: lint y build/TypeScript aprobados. Navegador con fixture: filtro Alta
14 resultados, limpieza 28, segunda página 26–28, filtro sin coincidencias y
recuperación, apertura de referencias y selección de reporte. En móvil 390 × 844,
reporte sin desbordamiento del documento; la etiqueta script del fixture se muestra
literalmente en el contenido. Escritorio 1440 × 1000; captura local:
`.local-state/ui-review/soc-fase5-desktop.png`.

La trazabilidad se limita a los identificadores que ofrece la API; no se añade
un visor de evidencias externas. La accesibilidad se revisa en UI 6.
Reversión: restaurar tabla, filtros, paginación y estilos anteriores; retirar el
componente extraído si no tiene otros consumidores. Los servidores temporales
se detuvieron sin ejecutar motor ni notificaciones.

## Entrega de fase UI 6 (01/10/2026)

Se ampliaron las escalas de texto pequeñas. La serie horizontal ahora admite foco
de teclado y conserva la tabla de datos como alternativa. Los resultados filtrados
se anuncian como estado y una pérdida de conexión se anuncia como alerta. Cuando
faltan el reporte o el log, los indicadores muestran «—» y los gráficos y la tabla
explican la ausencia; un cero queda reservado para una fuente disponible sin
coincidencias. La cabecera muestra «SIN CONEXIÓN» cuando falla la lectura.

Validación con fixture sintético: 320, 390, 650, 720, 768, 1024 y 1440 píxeles
en el resumen, y 320/720/1024 en amenazas, reportes y actividad. El documento no
desbordó horizontalmente; las tablas mantienen desplazamiento propio. El ancho
útil de 720 px representa el reflujo de una ventana de 1440 px al 200 %. El
navegador integrado no permitió aplicar el zoom real durante la revisión inicial;
el usuario confirmó después la prueba manual al 200 %. En teclado se verificaron el enlace
«Saltar al contenido», el foco del gráfico, el menú móvil y su cierre con Escape
y retorno del foco. La auditoría automatizada de texto visible en las cuatro
vistas no detectó relaciones inferiores a 4,5:1; la mínima medida fue 6,92:1.
El texto situado fuera de la barra del gráfico se comprobó sobre el panel.
La hoja conserva la regla para movimiento reducido, sin emular la preferencia del
sistema durante esta prueba.

Se probaron fuentes ausentes, pérdida de conexión con captura previa y apertura
sin backend. En una compilación intermedia el proxy temporal apuntó brevemente
al Flask local; se corrigió y se repitieron las comprobaciones de datos con el
fixture aislado en 5051. Esa lectura fue pasiva; no se ejecutaron análisis ni
notificaciones. Lint y build/TypeScript terminaron correctamente. Captura local:
`.local-state/ui-review/soc-fase6-desktop.png`.

Compatibilidad: no se cambiaron API, motor ni parámetros URL. Reversión: restaurar
las reglas tipográficas, el foco del gráfico y los mensajes condicionados por el
estado de las fuentes. La siguiente tarea prevista al cerrar UI 6 era la regresión integral de UI 7.

## Entrega de fase UI 7 (01/10/2026)

Se añadió `frontend/scripts/test_ui_regression.mjs`, ejecutable con
`pnpm run test:ui`. Cubre seis grupos: distribución real/vacía/no disponible,
serie temporal con ceros y sin datos, escapado de contenido hostil en amenazas,
campos ausentes y severidad desconocida, tabla vacía frente a fuente ausente, y
etiquetas/origen de las tarjetas KPI. Los componentes se renderizan como HTML
estático con los módulos del proyecto; las aserciones comprueban salida visible,
marcado accesible y ausencia de elementos HTML ejecutables.

Además, el recorrido del navegador con fixture verificó las cuatro vistas,
filtrado Alta (14 resultados), limpieza (28), búsqueda sin resultados,
selección de reporte y presentación del texto `<script>` sin crear nodos script,
y actividad reciente. Se repitió con las fuentes ausentes: las cuatro tarjetas
indican «—» y las visualizaciones muestran su estado no disponible.

Verificaciones finales: `pnpm run test:ui` (6 grupos), `pnpm run lint`,
`pnpm run build` con TypeScript, y `python -B scripts/check_baseline.py`
(75 pruebas Python, 0 fallos conocidos pendientes, 3 comprobaciones JavaScript).
El build final usa el destino habitual de API en el puerto 5000; durante el
recorrido visual se aisló en el puerto 5051. No se ejecutó el motor ni se
enviaron notificaciones. El usuario confirmó la comprobación del zoom real del
navegador al 200 % el 01/10/2026.

## Ajuste de navegación y autoría (01/10/2026)

El logo de la consola devuelve al Resumen y limpia filtros, paginación y reporte
seleccionado para restablecer el inicio. A petición del usuario, la autoría se
trasladó desde el pie a la cabecera, con nombre, alias, rol de desarrollador y
mantenedor, e iconos SVG accesibles para abrir GitHub y LinkedIn en pestañas
nuevas. La cabecera conserva una sola fila: en tamaños estrechos oculta primero
el rol y el breadcrumb antes de compactar la identidad. El pie queda como una franja
compacta de estado: salud de las fuentes, API v1, entorno local, hora de captura
cuando hay una captura y denominación del producto. No muestra versión de
frontend/build porque esos valores no están disponibles como datos fiables.

## Entrega de fase UI 8 — Seguridad y entrega (01/10/2026)

La revisión del frontend no encontró `dangerouslySetInnerHTML`, `innerHTML`,
`eval` ni construcción dinámica de código. Los campos de API y el Markdown/log
se presentan como texto mediante React; la regresión de amenazas ya verifica
que cargas de prueba con etiquetas y atributos hostiles queden escapadas. Los
enlaces a GitHub y LinkedIn son destinos fijos y usan `rel="noopener noreferrer"`
al abrir una pestaña nueva. No se exponen secretos ni credenciales del motor.

Las dependencias directas siguen fijadas en `package.json` y `pnpm-lock.yaml`;
no se añadieron paquetes en esta fase. `pnpm audit` consultado el 01/10/2026 no
reportó vulnerabilidades conocidas. El proxy de `/api/v1` se limita a loopback,
su puerto se valida en el rango permitido y utiliza 5000 como alternativa segura.
Los scripts `dev` y `start` de Next.js quedan ligados explícitamente a
`127.0.0.1`; antes, `start` usaba el valor predeterminado `0.0.0.0`.

La API y el motor no cambiaron. Si la interfaz Next.js falla, la entrada local
de Flask conserva su dashboard como retorno, descrito en
[`FASE_7_ENTRADA_PRINCIPAL.md`](FASE_7_ENTRADA_PRINCIPAL.md). Para revertir una
entrega de UI, revertir únicamente los cambios de `frontend/` y esta
documentación, conservando Flask, datos, logs e históricos. No requiere borrar
volúmenes ni restaurar secretos.

Verificación final: `pnpm run test:ui` (6 grupos), `pnpm run lint`,
`pnpm run build` con comprobación TypeScript, y la suite base con el intérprete
`.venv` (75 pruebas Python y 3 comprobaciones JavaScript). El auditor de pnpm
informó que no hay vulnerabilidades conocidas. El build de producción se inició
temporalmente en el puerto 3101: respondió HTTP 200 y `netstat` confirmó escucha
únicamente en `127.0.0.1`; el proceso de prueba se cerró al terminar.

Con la fase UI 8 completada, queda cerrado el rediseño SOC planificado.

# Fase 4 — Lectura conectada

Estado: **completada el 28/09/2026** en entorno local con fixtures sintéticos.
Next.js consume los GET versionados de Flask a través de un rewrite del mismo
origen. Flask conserva sus rutas y plantillas como vía de retorno; el motor,
los prompts, Docker y las notificaciones no cambiaron.

## Alcance entregado

- El resumen muestra estadísticas del reporte actual, severidades, IP observadas,
  coincidencias de patrones por periodo, una vista corta de amenazas, terminal
  limitado y reportes recientes de una captura `/api/v1/estado`.
- Una única lectura de estado por ciclo actualiza la consola cada 15 segundos
  cuando la pestaña está visible. El botón Actualizar fuerza una nueva lectura.
  Un fallo conserva la última captura y muestra un aviso. Los estados iniciales
  sin fuentes se representan como vacíos o degradados.
- Amenazas usa `/api/v1/amenazas` con filtros de severidad, tipo e IP exacta y
  paginación. La lista solo se muestra si su `snapshot_id` coincide con el del
  resumen; ante cambio se solicita actualizar. Filtros y página sobreviven a una
  recarga mediante la URL.
- Reportes usa `/api/v1/reportes` y el detalle por ID opaco, incluidos históricos
  fuera de los cinco recientes. El Markdown se representa como texto en React:
  permite leerlo sin interpretar HTML o enlaces del archivo. Un 409 indica que
  debe recargarse el catálogo.
- Actividad muestra la ventana limitada de líneas entregada por Flask. Logs y
  salidas del modelo se tratan como datos no confiables. La IP es un origen
  observado, la fecha del evento sigue ausente cuando el reporte no la acredita
  y el gráfico cuenta coincidencias de patrones, no ataques confirmados.

## Ejecución local

En VSCode, **Terminal → Ejecutar tarea → web-defense-ai V2: lectura conectada
(Flask + Next.js)**. Flask escucha en `127.0.0.1:5000` y Next.js en
`127.0.0.1:3000`; abrir esta última dirección. Las tareas no arrancan solas.
`frontend/next.config.ts` encamina `/api/v1/*` al Flask local, sin CORS ni
credenciales en el navegador. Para comprobar la UI con fuentes sintéticas, la
fixture escucha por defecto en `127.0.0.1:5051`; iniciar
`python -B tests/serve_phase4_fixture.py` y configurar
`WEB_DEFENSE_API_PORT=5051` al lanzar Next.js. `--empty` sirve un estado sin
reporte ni log. La fixture usa un puerto separado para no cruzarse con el Flask
habitual.

## Verificación

- ESLint, TypeScript y `next build`: correctos. La ruta inicial se compila como
  carcasa estática y los datos se obtienen en el navegador; no se incrustan
  logs o reportes en la compilación.
- Suite Python aislada: 39 casos; comprobaciones JavaScript del dashboard
  anterior: 3 aprobadas. No ejecutan integraciones externas.
- Integración local con fixture: `/api/v1/estado` comunicó 28 amenazas y la
  segunda página de `/api/v1/amenazas` devolvió las 3 restantes con el mismo
  `snapshot_id`; la segunda página de reportes devolvió 3 de 23. El navegador
  mostró esos valores, mantuvo `severidad=ALTA` al recargar y abrió un histórico.
  Un `<script>` incluido en el Markdown permaneció como texto; no apareció un
  elemento `script` en el detalle.
- Se comprobó la vista sin fuentes y la interrupción de Flask. En ambos casos
  la UI avisó sin inventar amenazas ni estado del ejecutor. Se revisó el ancho
  de la vista móvil y de sus paneles; la tabla conserva su scroll interno.

La comprobación no equivale a un piloto con Docker, LLM, notificaciones,
autenticación, carga concurrente ni accesibilidad completa. El Markdown se lee
como texto sin formato enriquecido. Antes de exponer la consola fuera de localhost
hay que revisar los parches de Next.js y completar la protección de acceso y el
despliegue de la fase 6. La acción de análisis real sigue pendiente de fase 5.

## Compatibilidad y reversión

La API y los contratos anteriores permanecen. La nueva consola solo hace GET;
no escribe reportes ni inicia análisis. Para volver a la interfaz anterior basta
con detener Next.js y usar Flask en `127.0.0.1:5000`. No hay esquema ni archivos
operativos convertidos que restaurar.

# Fase 7 — Preparación de la entrada principal

Estado al 01/10/2026: Fase 7 en curso. El usuario aceptó la evidencia parcial
de Fase 6 (14 h 11 min 46 s saludables) para una activación **local y
reversible**. El conmutador sigue desactivado por defecto en `.env.example`;
solo el proceso Flask iniciado con `NEXT_PRIMARY_ENABLED=1` cambia la entrada.
Flask y Next.js están ligados a loopback. Esta aceptación no equivale a una
observación de 24–48 horas ni autoriza un despliegue compartido.

## Comportamiento

- `NEXT_PRIMARY_ENABLED=0` mantiene Flask como página de entrada en
  `http://127.0.0.1:5000/` y no sondea Next.js.
- Con `NEXT_PRIMARY_ENABLED=1`, Flask comprueba `http://127.0.0.1:3000/` en
  loopback. Si recibe HTTP 200, responde con redirección temporal a Next.js.
- Si Next.js no está disponible o no devuelve HTTP 200, Flask renderiza su
  dashboard anterior en la misma solicitud. No se hace un sondeo externo ni se
  siguen redirecciones durante la comprobación.
- El cliente conserva la entrada Flask como ruta manual de retorno. El
  conmutador no cambia API, ejecutor, almacenamiento, históricos ni el
  comportamiento de `/api/v1`.

## Activación local reversible

La Fase 6 aportó los diez ciclos, la medición local y el retorno a Flask; el
usuario aceptó expresamente que la observación parcial sustituya, **solo para
esta activación local**, al criterio inicial de 24–48 horas. No se modificó
`.env` ni se inició el ejecutor de análisis. Para reproducirlo en VSCode,
detener primero cualquier servidor que ocupe los puertos 5000 y 3000:

1. Ejecutar la tarea **web-defense-ai V2: entrada Next.js local (Fase 7)**.
   Sus dos procesos arrancan en loopback; Flask recibe
   `NEXT_PRIMARY_ENABLED=1` y `ANALYSIS_MANUAL_ENABLED=0` solo en su entorno.
2. Abrir `http://127.0.0.1:5000/`. Debe redirigir a
   `http://127.0.0.1:3000/`. Revisar resumen, amenazas, reportes y actividad.
3. Para comprobar la caída de Next.js, detener su terminal. Una visita nueva
   a `http://127.0.0.1:5000/` debe servir el dashboard Flask.
4. Para volver al modo anterior de forma explícita, detener ambas terminales
   de Fase 7 y ejecutar **web-defense-ai V2: dashboard con recarga local** o
   **web-defense-ai V2: lectura conectada (Flask + Next.js)**. Estas tareas
   fijan `NEXT_PRIMARY_ENABLED=0` en Flask.

La observación de uso sugerida de siete días en el plan sigue pendiente para
dar por cerrada la Fase 7. No hay una monitorización nueva en marcha; registrar
incidencias y comprobar la reversión antes de decidir la configuración habitual
para futuras sesiones.

## Retorno

Detener el proceso Flask con `NEXT_PRIMARY_ENABLED=1` e iniciarlo con
`NEXT_PRIMARY_ENABLED=0`, por ejemplo con la tarea de dashboard anterior.
Abrir `http://127.0.0.1:5000/`; Flask servirá su dashboard sin depender de
Next.js. Si Next.js cae antes de reiniciar Flask, una visita nueva a esa misma
dirección también recibe Flask. La acción manual continúa controlada por
separado mediante `ANALYSIS_MANUAL_ENABLED`.

## Validación local y límites

La suite automatizada comprueba el modo apagado, redirección con Next disponible
y render Flask cuando Next no responde. La verificación de disponibilidad está
aislada en pruebas y no requiere iniciar Next.js. La activación local ensayada
usa la aceptación parcial de fase 6 indicada arriba; no hay despliegue público,
autenticación compartida ni telemetría centralizada.

El 01/10/2026 se inició Flask y Next.js reales con una fixture sintética
aislada. Flask respondió `302` hacia Next.js; Next.js y ambas rutas de estado
respondieron `200` con el mismo `snapshot_id`. Los filtros de amenazas
devolvieron 28 elementos y el catálogo 23 reportes. Tras detener Next.js,
Flask sirvió `/`, `/api/v1/estado` y un reporte histórico con `200`; la primera
respuesta de retorno tardó 393 ms. Después se cerraron ambos procesos de
prueba. Se inició también la aplicación local con la configuración existente:
entrada Flask `302`, Next.js `200`, ambas API `200` con igual captura y acción
manual desactivada. Al detener Next.js, Flask sirvió la entrada con `200` en
378 ms. Después se reinició Flask con `NEXT_PRIMARY_ENABLED=0` y volvió a
servir la entrada con `200` sin redirección. Finalmente se reactivó el modo
local de Fase 7 y se verificaron otra vez `302` hacia Next.js, página y API
`200` y análisis manual desactivado. Este recorrido no ejecutó CrewAI ni
notificaciones. Los dos servidores locales quedaron activos para su revisión.

La revisión visual local también comprobó navegación, persistencia de filtros,
lectura de históricos con HTML tratado como texto y actividad con la fixture de
fase 4. En móviles el panel lateral cerrado se excluye de la navegación por
teclado; tras elegir una sección, el foco vuelve al control de menú. El ancho del
documento no superó el viewport en 390, 768, 1280 y 1440 píxeles.

La comprobación puntual de contraste corrigió la etiqueta de navegación, el
nombre del espacio de trabajo, los encabezados de tabla y el pie de página. Los
pares medidos quedan entre 5.38:1 y 6.03:1, y el foco por teclado muestra un
borde visible de 2 píxeles. Es una revisión parcial de componentes visibles,
no una certificación WCAG ni una auditoría automatizada completa.

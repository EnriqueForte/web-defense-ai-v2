# web-defense-ai V2 — Frontend

Consola Next.js 16, React 19 y TypeScript conectada a la API de lectura `/api/v1`
de Flask. El resumen, las amenazas, la actividad reciente y los reportes muestran
archivos locales observados por el backend. La acción manual de fase 5 solo
solicita un trabajo al ejecutor cuando está habilitada; las lecturas no inician
análisis ni notifican.

En VSCode, ejecuta **web-defense-ai V2: lectura conectada (Flask + Next.js)** y
abre `http://127.0.0.1:3000`. Inicia Flask en `127.0.0.1:5000` y Next.js en
`127.0.0.1:3000`. La tarea individual **interfaz Next.js de lectura** permite
comprobar el estado sin conexión cuando Flask no está activo. Ninguna tarea
se inicia al abrir el proyecto.

Desde una terminal en `frontend/`, tras instalar las dependencias fijadas en
`pnpm-lock.yaml`:

```powershell
node node_modules/next/dist/bin/next dev --hostname 127.0.0.1
node node_modules/eslint/bin/eslint.js src/app
node node_modules/typescript/bin/tsc --noEmit
node node_modules/next/dist/bin/next build
```

Next.js encamina `/api/v1/*` al Flask local mediante `next.config.ts`, por lo que
el navegador consulta el mismo origen y no necesita CORS ni credenciales del motor.
El estado se lee cada 15 segundos cuando la pestaña está visible. Las listas y
detalles se solicitan al abrirlos. Los filtros de amenazas y la selección de
reportes se conservan en la URL. El Markdown se muestra como texto para impedir
la ejecución de HTML procedente del reporte.

La integración y la verificación sintética se detallan en
[`docs/FASE_4_LECTURA_CONECTADA.md`](../docs/FASE_4_LECTURA_CONECTADA.md).
Flask conserva su dashboard anterior como vía de retorno.
La coordinación, activación y límites de la acción manual se documentan en
[`docs/FASE_5_ANALISIS_COORDINADO.md`](../docs/FASE_5_ANALISIS_COORDINADO.md).

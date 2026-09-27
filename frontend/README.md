# web-defense-ai V2 — Frontend

Base visual en Next.js 16, React 19 y TypeScript. Esta fase presenta un resumen
estático con datos sintéticos; no consulta Flask ni representa telemetría real.

Desde VSCode, ejecuta **web-defense-ai V2: interfaz Next.js de demostración**.
Desde una terminal en este directorio, con dependencias ya instaladas:

```powershell
node node_modules/next/dist/bin/next dev --hostname 127.0.0.1
node node_modules/eslint/bin/eslint.js src/app
node node_modules/typescript/bin/tsc --noEmit
node node_modules/next/dist/bin/next build
```

La pantalla se abre en `http://127.0.0.1:3000`. La conexión de lectura con la API,
las vistas completas de amenazas e históricos y el refresco real corresponden a
la fase 4. Flask continúa siendo la aplicación operativa.

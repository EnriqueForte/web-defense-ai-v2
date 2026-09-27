# Fase 3 — Base visual Next.js

Estado: **completada el 27/09/2026**. Se creó la nueva consola visual en
`frontend/`, manteniendo Flask como aplicación operativa. La pantalla es una
demostración desconectada: todos los valores, eventos, ubicaciones e indicadores
son sintéticos. No llama a `/api/v1`, Docker, CrewAI ni servicios de notificación.

## Base tecnológica

- Next.js 16.3.6, App Router y React 19.2.8.
- TypeScript 5.9.3 y ESLint 9.39.5 con `eslint-config-next`.
- Tailwind CSS 4.3.3 está preparado; la primera composición usa CSS propio para
  fijar tokens, paneles y adaptación de pantalla sin añadir una biblioteca visual.
- Node observado: v24.19.0. Next.js 16 requiere Node 20.9 o posterior.
- `pnpm-lock.yaml` fija el árbol instalado. Las versiones se anotan porque se
  eligieron y compilaron en esta fase; deben revisarse parches antes de publicar.

La interfaz queda en desarrollo local. El equipo de Next.js anunció el 23/09
una actualización de seguridad prevista para el 30/09/2026 (Next.js 16.3.7);
antes de cualquier exposición externa, comprobar el aviso y aplicar la versión
parcheada cuando se publique: [aviso oficial de Next.js](https://nextjs.org/blog/upcoming-nextjs-security-release-september-2026).

La elección de Next.js 16 responde a su estado de soporte y al uso de App Router;
la documentación oficial especifica Node 20.9 como mínimo. Referencias:
[instalación y requisitos de Next.js](https://nextjs.org/docs/app/getting-started/installation),
[lanzamientos de Next.js](https://nextjs.org/blog) y
[ciclo de soporte de Node.js](https://nodejs.org/en/about/previous-releases).

Se mantiene ESLint 9 porque `eslint-plugin-react` 7.37.5, incluido por la
configuración de Next, falla al ejecutar reglas con ESLint 10; su soporte aún no
está publicado. Es una dependencia de desarrollo y se debe actualizar cuando el
plugin publique compatibilidad comprobable. Véase el [seguimiento del cambio en
eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react/pulls).

## Experiencia incluida

`src/app/page.tsx` presenta una consola en español con navegación lateral, resumen
de métricas, dos gráficos SVG, lista de eventos, búsqueda y filtro local por
severidad. Los botones de periodo, navegación y mensajes muestran el alcance de
esta demo. El conjunto local contiene 12 eventos; la vista enseña los cuatro más
recientes y las búsquedas/filtros trabajan sobre todo el conjunto. Las IP usan
los rangos de documentación TEST-NET definidos para ejemplos, no orígenes reales
([RFC 5737](https://www.rfc-editor.org/info/rfc5737/)). Los demás módulos muestran
un estado de fase posterior, no páginas conectadas.

`src/app/globals.css` define el tema oscuro, tonos cian/verde para información,
ámbar y rojo para severidad, foco visible, comportamiento reducido de movimiento
y reglas adaptables a escritorio y móvil. Los gráficos incluyen descripción para
lectores de pantalla. La tabla conserva un desplazamiento horizontal interno en
pantallas estrechas.

Los metadatos del documento llevan el nombre oficial `web-defense-ai V2`; se
quitó la descarga de fuentes externas para que la compilación no dependa de una
conexión a Google Fonts. La interfaz no incorpora claves, URLs privadas ni acceso
a Docker.

## Verificación

- ESLint: correcto.
- `tsc --noEmit`: correcto.
- `next build`: correcto; `/` queda prerenderizada como página estática.
- Revisión en navegador local: búsqueda por IP reservada devuelve un evento; severidad Alta
  devuelve dos; escritorio y móvil revisados. El exceso de ancho de la tabla queda
  contenido en su zona con scroll propio.
- Las tareas de VSCode permiten iniciar Next en `127.0.0.1:3000`, ejecutar ESLint,
  comprobar tipos y compilar. No se inicia automáticamente ningún proceso.

La verificación no prueba lectura de Flask, funcionamiento de rutas secundarias,
accesibilidad WCAG completa, navegador real de producción ni vulnerabilidades de
dependencias. Estas cuestiones quedan para la conexión de lectura y validación
de fases posteriores.

## Compatibilidad y reversión

Flask conserva sus rutas, plantillas y ejecución habitual. La UI nueva vive en su
propio subdirectorio y el build estático no importa módulos Python. Para volver a
la experiencia anterior basta con detener el servidor Next local y continuar en
Flask; no hay transformación de datos ni cambio de esquema que revertir.

## Ejecución desde la raíz del repositorio

En VSCode: ejecutar **web-defense-ai V2: interfaz Next.js de demostración**.
Tras instalar dependencias con `pnpm install --frozen-lockfile`, también se puede
ejecutar desde una terminal situada en `frontend/`:

```powershell
node node_modules/next/dist/bin/next dev --hostname 127.0.0.1
node node_modules/eslint/bin/eslint.js src/app
node node_modules/typescript/bin/tsc --noEmit
node node_modules/next/dist/bin/next build
```

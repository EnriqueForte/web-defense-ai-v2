# Endurecimiento del retorno local — 07/10/2026

Alcance: distribución del código para instalaciones propias. Esta entrega amplía
las protecciones HTTP anteriores y elimina dependencias de red al visualizar el
dashboard Flask y sus informes. No convierte la aplicación en servicio público.

## Cambios

- Chart.js 4.4.1 y marked 9.1.6 se sirven desde `dashboard/static/vendor/`.
  Se conservan las versiones utilizadas anteriormente y sus licencias MIT.
  El manifiesto registra los paquetes oficiales npm, integridad SHA-512 de cada
  archivo tar y SHA-256 de los JavaScript y licencias extraídos. La descarga
  verificó la integridad antes de extraer los archivos concretos; no instaló ni
  ejecutó los paquetes. `.gitattributes` evita conversiones de fin de línea en
  estos recursos. Esto acredita procedencia e integridad, no ausencia de fallos
  ni una auditoría de seguridad actualizada de esas versiones.
- Se eliminan Google Fonts y las referencias a CDN en las plantillas Flask y
  su CSS. Se utilizan fuentes disponibles en el sistema. No se ha ensayado un
  corte completo de red: se comprobó que estas páginas no solicitan recursos
  externos y que sus bibliotecas se entregan localmente.
- Flask añade CSP: recursos y conexiones del mismo origen, nonce aleatorio por
  respuesta para scripts de plantilla, objetos y marcos bloqueados, base URI
  bloqueada y formularios limitados al origen. Los eventos `onclick` pasan a
  listeners. No se permite `unsafe-inline` ni `unsafe-eval` en scripts.
  `style-src` conserva `unsafe-inline` por los estilos existentes; no se declara
  una política completamente libre de estilos inline. Se añade X-Frame-Options
  DENY y protección `noopener noreferrer` a enlaces de historial en nueva ventana.
- Next añade nosniff, Referrer-Policy, X-Frame-Options y una CSP limitada a
  objetos, base URI y marcos. No se afirma que aplique la política completa de
  scripts de Flask a React; requeriría un trabajo específico de hidratación y
  nonces. El rewrite API se conserva.
- La lectura Markdown recorta el espacio exterior introducido por la plantilla,
  evitando que su título se interprete como bloque de código. Se mantiene el
  copiado DOM con lista de etiquetas y atributos permitidos; la CSP complementa
  esa defensa y no sustituye el tratamiento seguro de contenido.

## Verificación

245 pruebas Python en `.p2` y `.venv`, tres comprobaciones JavaScript, 14 grupos
de regresión UI, TypeScript, ESLint, sintaxis de 66 archivos y diff sin errores.
Las fixtures comprueban nonces diferentes por respuesta, ausencia de CDN y
handlers inline, cabeceras, respuesta de recursos y hashes exactos del manifiesto.

Servidor efímero con fixtures sintéticas en 127.0.0.1:5051: HTTP 200 y CSP
comprobados; navegador con gráfico visible, biblioteca local y sin recursos
externos ni errores/avisos de consola. Informe sintético: título Markdown
renderizado y etiqueta script de la fixture eliminada. La primera conexión
falló; el recorrido se completó al iniciar el servidor fuera del aislamiento.
El servidor de pruebas se detiene tras la comprobación.

No se modificó `.env` ni se ejecutaron jobs, LLM, Docker o notificaciones.
No se reiniciaron servicios operativos; cargar las nuevas cabeceras de Flask
requiere la recarga documentada del servicio. Estas pruebas no certifican el
paquete desde una clonación limpia ni los sistemas Linux/macOS. No se publicó
un commit nuevo en esta entrega.

## Compatibilidad, reversión y pendientes

Los contratos API, informes originales y fuentes de datos se conservan. Los
archivos vendor deben incluirse en la distribución y conservar sus licencias.
La reversión consiste en restaurar código/plantillas/configuración y recargar
los servicios; no requiere restaurar SQLite, logs ni históricos. Evitar retirar
solo los nonces mientras siga activa la CSP, pues bloquearía scripts propios.

Quedan instalador/arranque definitivo y clonación limpia, revisión de dependencias
incluidos estos recursos, auditoría de historial/datos, entrega GitHub y cierre
operativo A-05. El diagnóstico operativo necesita cargar el código del worker
por la operación prevista; cualquier nueva evaluación real necesita alcance
autorizado. Este bloque no cierra por sí solo A-05 ni toda la revisión integral.

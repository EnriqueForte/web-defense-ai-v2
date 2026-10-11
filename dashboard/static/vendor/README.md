# Recursos de terceros

Chart.js 4.4.1 y marked 9.1.6: distribuciones UMD oficiales del registro npm,
con sus respectivas licencias MIT adjuntas. Son las versiones que antes se
cargaban mediante CDN; esta entrega cambia su ubicación, no su versión.

`manifest.json` registra origen, integridad SHA-512 del paquete y SHA-256 de los
archivos. Las pruebas de línea base verifican estos últimos. `.gitattributes`
conserva los bytes al clonar en Windows. No editar los JavaScript o licencias.

Para actualizar: revisar la versión y sus avisos, verificar la integridad del
paquete oficial, extraer únicamente la distribución y licencia necesarias,
actualizar manifiesto y referencias y comprobar regresión de gráfico/Markdown,
hashes y compatibilidad CSP. La existencia del manifiesto no sustituye la
revisión de seguridad de las bibliotecas.

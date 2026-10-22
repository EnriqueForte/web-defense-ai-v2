# Capturas de Web Defense AI

## Consola V2

Las tres capturas siguientes se prepararon el 21/10/2026 a partir de la interfaz Next.js compilada del
proyecto. El navegador recibió respuestas API simuladas en memoria; no se
arrancó un servidor ni se consultaron servicios o datos operativos.

| Archivo | Vista |
| --- | --- |
| [v2-summary.png](v2-summary.png) | Resumen, indicadores, actividad y severidades |
| [v2-threats.png](v2-threats.png) | Eventos observados y grupos clasificados con referencias |
| [v2-reports.png](v2-reports.png) | Catálogo y lectura del informe de ejemplo |

Los datos y el texto del informe son **sintéticos**, preparados para documentar
la interfaz. La IP `198.51.100.23` pertenece al espacio reservado para
documentación. Los dos grupos de ejemplo no acreditan incidentes reales,
resultados del proveedor ni una nueva evaluación del modelo. La captura no
requirió llamadas LLM, lectura de `.env`, tráfico DVWA ni envío de avisos.

## Configuración del LLM

[v2-llm.png](v2-llm.png) fue aportada por el propietario el 22/10/2026 y muestra
la pantalla de Configuración de su instalación: selección de proveedor Groq u
OpenRouter, catálogo de modelos y almacenamiento local de la configuración.
Esta imagen tiene una procedencia distinta de las tres muestras sintéticas
anteriores. Se publica tal como fue aportada, tras comprobar visualmente que
el campo de clave está vacío y no muestra el valor de la credencial guardada.

La captura ilustra la interfaz; no acredita una nueva ejecución del modelo,
validación de la clave ni disponibilidad o gratuidad de los modelos mostrados.
Su incorporación documental no requirió consultar proveedores, leer `.env`,
ejecutar análisis ni modificar la instalación del propietario.

## Interfaz anterior

Los archivos `screenshot-*.png` se conservan como referencias históricas del
dashboard Flask. Pueden mostrar la denominación y funciones de etapas anteriores;
no representan el aspecto actual de la consola Next.js.

[Volver al README](../README.md)

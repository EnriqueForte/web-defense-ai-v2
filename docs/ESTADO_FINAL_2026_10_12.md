# Estado para la entrega final — 12/10/2026

Este es el resumen vigente. Las actas fechadas anteriores conservan sus pruebas
y límites históricos; sus pendientes pueden haberse cerrado después.

## Completado

- Migración de interfaz y rediseño SOC; Flask conservado como retorno local.
- Instalación y build con una orden, arranque Flask/Next con otra y cierre por Ctrl+C.
- Clon/instalación limpia y CI Windows/Ubuntu; validación guiada Parrot7.3/VMware.
- Corrección de comprobación de puertos y aceptación del recorrido en Parrot.
- 158 pines por plataforma e inventario completo: freeze/metadatos/contrato,
  uvloop Linux fijado, comprobación estricta/exportación aprobadas en Parrot.
- Código y evidencias publicados en el repositorio V2; original independiente.

Referencias: [inicio rápido](INICIO_RAPIDO.md), [contrato Linux](CONTRATO_LINUX_2026_10_12.md),
[validación Parrot](VALIDACION_PARROT_2026_10_12.md) y [corrección de puertos](CORRECCION_PUERTOS_2026_10_12.md).

## Pendientes de cierre

| Bloque | Trabajo restante | Evidencia de cierre |
| --- | --- | --- |
| Seguridad | Auditorías actuales, revisión/migración de paquetes residuales, imágenes del laboratorio/base e historial | Informes con versiones/digests/base/fecha, revisión de condiciones, parches compatibles o riesgos explícitamente documentados; fallos de scanner separados de resultados |
| Calidad A-05 | Evaluación semántica y comprobación final de las correcciones del análisis manual | Casos representativos, evidencia/guardas/publicación y aceptación con límites; nuevas llamadas reales requieren alcance concreto |
| Recorrido completo Parrot | Preparar laboratorio, capturar logs, analizar y verificar informe/indicadores/gráficos | Ensayo guiado en esa VM; no se deduce de CI o de la consola de lectura |
| Configuración/interfaz | Validación global de valores y E2E de guardar/recargar/desmontar Configuración | Errores comprensibles y pruebas de efectos completos; helpers/dobles existentes no acreditan todo el recorrido |
| Operación/recuperación | Procedimiento definitivo de análisis, conservación y recuperación; delimitar volúmenes/buzón del laboratorio | Guía ejecutable y restauración dentro del alcance prometido, preservando datos y entregas |
| Entrega final | Consolidar documentación, revisar archivos/historial y preparar versión final GitHub | Resumen vigente, revisión de distribución, CI final y versión/release en V2 |

La auditoría de archivos/historial aparece en seguridad y entrega, pero es una
misma tarea de cierre. La revisión acotada previa al push no fue exhaustiva.
No se presenta el clon de lectura como prueba del análisis real o laboratorio.

`config/settings.py` mantiene conversiones directas float/int al importar;
los valores inválidos requieren una validación comprensible pendiente. R-15
conserva el E2E de los efectos de Configuración. A-05 mantiene la evaluación
semántica pendiente y la revisión del recorrido manual según
[formato manual](CORRECCION_FORMATO_MANUAL_A05_2026_10_11.md).

## Seguridad en curso

Auditorías PyPI/npm actualizadas el 12/10: producción frontend/vendor sin avisos,
braces de desarrollo con un aviso y Python36entradas en cuatro paquetes para
cada inventario completo de158. Trivy Windows sigue bloqueado por Control de
aplicaciones; se prepara escaneo remoto en Ubuntu CI sin iniciar contenedores.
Los resultados y decisiones se registran en [seguimiento de seguridad](SEGURIDAD_2026_10_12.md).

La CSP completa de scripts Next, retención automatizada, soporte de otras
arquitecturas/macOS y funcionamiento como servicio de sistema son mejoras
adicionales condicionadas al alcance; no se añaden como requisitos para terminar
la versión local actualmente acordada.

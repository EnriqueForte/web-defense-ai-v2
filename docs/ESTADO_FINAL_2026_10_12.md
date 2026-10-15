# Estado para la entrega final — 12/10/2026

Este es el resumen vigente. Las actas fechadas anteriores conservan sus pruebas
y límites históricos; sus pendientes pueden haberse cerrado después.

## Completado

- Migración de interfaz y rediseño SOC; Flask conservado como retorno local.
- Instalación y build con una orden, arranque Flask/Next con otra y cierre por Ctrl+C.
- Clon/instalación limpia y CI Windows/Ubuntu; validación guiada Parrot7.3/VMware.
- Corrección de comprobación de puertos y aceptación del recorrido en Parrot.
- Contrato inicial de 158 pines/inventario completo y uvloop Linux aprobados en Parrot.
  La [migración posterior CrewAI](MIGRACION_CREWAI_2026_10_12.md) pasó Windows/Ubuntu
  desde instalación nueva con 172 pines. El 13/10 el usuario acreditó actualización,
  inventario 172/0/0, arranque/cierre y navegación correcta en su VM Parrot.
- Código y evidencias publicados en el repositorio V2; original independiente.
- Validación numérica del ejecutor y [recorrido E2E de Configuración](CONFIGURACION_E2E_2026_10_13.md):
  nueve casos Chromium en Windows/Ubuntu CI, con guardado sintético, recarga,
  desmontaje/cancelación, errores y cierre de puertos comprobados el 13/10.
- [Operación/recuperación de aplicación](OPERACION_RECUPERACION_2026_10_14.md):
  guía, copia de 76 archivos/12 diagnósticos y restauración aislada con datos
  Windows, filas/entregas/publicación preservadas y CI Windows/Ubuntu propia.
  Volúmenes DVWA/buzón Mailpit y promoción en vivo tienen alcance separado.

Referencias: [inicio rápido](INICIO_RAPIDO.md), [contrato Linux](CONTRATO_LINUX_2026_10_12.md),
[validación Parrot](VALIDACION_PARROT_2026_10_12.md) y [corrección de puertos](CORRECCION_PUERTOS_2026_10_12.md).

## Pendientes de cierre

| Bloque | Trabajo restante | Evidencia de cierre |
| --- | --- | --- |
| Seguridad | Auditorías/escaneo y migración CrewAI completados; quedan Chroma/braces, infraestructura e historial | Migración172pines/5entradasChroma comprobada; riesgos residuales gestionados y compatibilidad de cambios de infraestructura |
| Calidad A-05 | Matriz offline/CI y corrección verificadas; mixed/normal y nuevo same_family autorizado satisfacen sus muestras, con informes/guardas/hashes revisados | Aceptación con límites e ingesta manual/Parrot; semántica general sigue pendiente |
| Recorrido completo Parrot | Laboratorio/acceso/captura/lectura acreditados; HTTP 400 Groq por cache_breakpoint identificado, corrección local aprobada offline; publicar/actualizar y verificar informe/indicadores/gráficos | [Incidencia y corrección local](INCIDENCIA_GROQ_PARROT_2026_10_15.md); no repetir el ensayo sin nuevo alcance |
| Entrega final | Consolidar documentación, revisar archivos/historial y preparar versión final GitHub | Resumen vigente, revisión de distribución, CI final y versión/release en V2 |

La auditoría de archivos/historial aparece en seguridad y entrega, pero es una
misma tarea de cierre. La revisión acotada previa al push no fue exhaustiva.
No se presenta el clon de lectura como prueba del análisis real o laboratorio.

La [validación global del ejecutor](CONFIGURACION_GLOBAL_2026_10_13.md) reemplaza
las conversiones directas de `config/settings.py`: errores por variable y rechazo
antes de crear estado, con regresión offline aprobada. R-15 dispone ahora del
E2E del formulario en Chromium con Flask/proxy reales y persistencia sintética;
se cierra en ese alcance, sin acreditar uso con un proveedor real. A-05 mantiene la evaluación
semántica pendiente y la revisión del recorrido manual según
[formato manual](CORRECCION_FORMATO_MANUAL_A05_2026_10_11.md).

El 13/10 se añadió una [revisión A-05 offline reproducible](EVALUACION_OFFLINE_A05_2026_10_13.md):
13 casos con respuestas sintéticas y siete controles de rechazo/conservación de
publicación. La evaluación incorpora cobertura por pares de patrón–línea además
de familias, separando omisiones de selección y de respuesta. Esto verifica el
evaluador y las guardas; no acredita calidad del proveedor ni cierra A-05.
Código `c7df36a` publicado y [CI 38411563805](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38411563805)
Windows/Ubuntu completada con success; logs y artefactos A-05/inventarios revisados.
El [ensayo real autorizado del 14/10](ENSAYO_REAL_A05_2026_10_14.md) consumió
seis intentos lógicos: mixed y normal publicaron resultados verificados,
same_family falló con dos JSON inválidos. Se corrigió offline un envoltorio del
evaluador que ocultaba el formato JSON antes de los otros dos casos; no se repitió
el fallido. Corrección publicada como `6f0e549`, con
[CI 38545831374](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38545831374)
Windows/Ubuntu success y logs/artefactos revisados, incluidos 27 SDK offline.
Un nuevo ensayo único same_family autorizado el mismo día pasó con tres llamadas,
dos referencias SQLi cubiertas y solicitud normal sin hallazgo. Se revisaron
informe/guardas/métricas/hashes y conservación operativa. El fallo inicial sigue
registrado; los dos presupuestos se mantienen separados y sus saldos no se
reutilizan. Quedan aceptación con límites y recorrido de ingesta; no se cierra A-05.

[Operación y recuperación del 14/10](OPERACION_RECUPERACION_2026_10_14.md)
añade `restore_operational.py --backup <carpeta>` para un destino nuevo aislado,
sin sustituir datos o reproducir entregas. Recibos de diagnóstico conocidos
entran ahora en la cobertura del respaldo. Parrot acredita por capturas Docker
respondiendo y Compose independiente validando el archivo (salida 0), desde
`e5af1a6`; laboratorio/ingesta y restauración en esa VM siguen sin acreditarse.
Código `4cb1707`, [CI 38552056806](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38552056806)
Windows/Ubuntu success; logs y artefactos/inventarios revisados. El siguiente
recorrido guiado requiere actualizar el clon Parrot y preparar laboratorio,
después delimitar el análisis real antes de consumir nuevas llamadas.

## Seguridad en curso

Auditorías PyPI/npm actualizadas el 12/10: producción frontend/vendor sin avisos,
braces de desarrollo con un aviso y Python 36 entradas/cuatro paquetes en el
contrato de 158. Las 22 fichas primarias fueron revisadas. La migración posterior
reduce a cinco entradas/cuatro IDs en Chroma, con 172 pines y CI Windows/Ubuntu aprobada.
Trivy Linux completó el escaneo remoto de las seis referencias en Ubuntu CI con
digests/fecha de base, sin iniciar contenedores. Todas presentan avisos; no se
declara cierre de seguridad. CI de compatibilidad final pasó en ambos sistemas.
Los resultados y decisiones se registran en [seguimiento de seguridad](SEGURIDAD_2026_10_12.md).

La CSP completa de scripts Next, retención automatizada, soporte de otras
arquitecturas/macOS y funcionamiento como servicio de sistema son mejoras
adicionales condicionadas al alcance; no se añaden como requisitos para terminar
la versión local actualmente acordada.

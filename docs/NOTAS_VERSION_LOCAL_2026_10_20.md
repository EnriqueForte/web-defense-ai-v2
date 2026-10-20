# Notas de la primera versión local — borrador del 20/10/2026

**Preparadas para revisión; sin tag ni release publicados.** La identificación
de versión y la referencia de código se completarán después de verificar la
[CI de entrega C4](ENTREGA_LOCAL_C4_2026_10_20.md).

## Uso previsto

Aplicación personal en localhost para revisar indicadores de un registro de
acceso y consultar informes trazables. La instalación controla sus datos y
credenciales. Los hallazgos requieren investigación; no confirman explotación
exitosa o autenticación conseguida.

## Incluido

- Consola SOC con Resumen, Actividad, Reportes y Configuración; Flask conserva
  el retorno local. Instalación/build, lectura y análisis manual se documentan
  como recorridos distintos.
- Análisis structured con referencias a evidencias, grupos de hallazgos,
  conteos y tabla generados por Python, validación antes de publicar y
  conservación del informe anterior ante un fallo.
- Muestra guiada Parrot XSS/fuerza bruta aceptada el 15/10 y evaluación offline
  sintética ampliada, con límites recogidos en la aceptación local C2.
- Entorno de 172 paquetes por plataforma; parche aiohttp 3.14.4/yarl 1.25.1 y
  caché de tokenizadores empaquetados verificada para los casos documentados.
- Guías consolidadas, recuperación aislada de aplicación y laboratorio
  recomendado separado, con imágenes fijadas por digest y avisos conservados.

## Límites y riesgos aceptados

La [decisión C2](REVISION_ACEPTACION_A05_2026_10_20.md) acepta apoyo local a la
revisión de indicadores. No certifica calidad general, resistencia del LLM,
superioridad frente a legacy ni rendimiento/coste universales; la comparación
legacy está diferida y `quality=semantic_evaluation_pending` permanece intacto.

El [tratamiento C3](TRATAMIENTO_RIESGOS_C3_2026_10_20.md) conserva los avisos
Chroma/MCP, braces de desarrollo, imágenes del laboratorio/Mailpit y la muestra
CSRF histórica de procedencia no acreditada, anonimizada en el fixture actual.
La aceptación de riesgos no equivale a corregir esas vulnerabilidades.

Uso personal local aislado; `.env` contiene texto sin cifrar y no debe
compartirse. No incluye despliegue público/multiusuario, remediación automática,
nuevos servidores/herramientas MCP/Chroma o garantías de seguridad global.

## Instalación y conservación de datos

Seguir la [guía de instalación y actualización](INSTALACION_AUTOALOJADA.md).
Respaldar y comprobar los datos antes de modificar una instalación existente.
La VM Parrot no se ha actualizado a los pines de esta entrega ni se ha probado
la restauración de sus volúmenes Docker; ese trabajo es V1, independiente.
Conservar el correo necesario antes de recrear Mailpit y no borrar volúmenes.

## Validación de esta versión

Pendiente de la CI nueva Windows/Ubuntu del parche y de la revisión de sus
artefactos. Las pruebas locales de C3 están registradas en su acta. No se usa
la CI anterior como validación de los nuevos pines. No se han realizado nuevos
ensayos LLM ni cambios operativos como parte de la preparación de esta versión.

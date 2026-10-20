# C3 — Tratamiento de riesgos para la primera versión local — 20/10/2026

**C3 aceptado en tratamiento de riesgos para uso local aislado.** El usuario
eligió expresamente «Aceptar tratamiento local acotado (recomendado)» el
20/10/2026 sobre esta propuesta, independientemente de A-05/C2. Se mantienen
los avisos y la CI del parche como requisito de entrega; no se certifica seguridad global.
El [registro JSON](TRATAMIENTO_RIESGOS_C3_2026_10_20.json) conserva fuentes,
fechas, hashes, auditorías y comprobaciones.

**Continuación C4:** [CI y artefactos del parche verificados](ENTREGA_LOCAL_C4_2026_10_20.md)
después de esta revisión, sobre `0d73ec2` en Windows/Ubuntu. El registro JSON
de C3 conserva el estado de su revisión local original; la evidencia nueva,
incluida la instalación real Linux, se registra en C4.

## Revisión actual y corrección aplicada

Se auditaron los freezes completos de la CI39239742802: 172 paquetes por OS,
con hashes verificados y sin leer el entorno operativo. La consulta del 20/10
encuentra **nueve entradas por OS**, frente a seis el 18/10. Las tres nuevas
corresponden a aiohttp 3.14.3 y tienen corrección en 3.14.4:

| Aviso | Corrección declarada y fuente |
| --- | --- |
| CVE-2026-111063 / GHSA-494j-54xm-rwp3 | Cookie compartida Secure podía seleccionarse para conexión sin cifrar. [Aviso del mantenedor](https://github.com/aio-libs/aiohttp/security/advisories/GHSA-494j-54xm-rwp3). |
| CVE-2026-111064 / GHSA-5wr8-gcqf-gqf3 | Límite inicial de petición/cabeceras del servidor. La base GitHub indica alta y el mantenedor baja: se conservan ambas. [Aviso](https://github.com/aio-libs/aiohttp/security/advisories/GHSA-5wr8-gcqf-gqf3). |
| GHSA-2g87-pp6c-29x5 | Casos de consumo excesivo de memoria/CPU. [Aviso del mantenedor](https://github.com/aio-libs/aiohttp/security/advisories/GHSA-2g87-pp6c-29x5). |

Cambios locales en `requirements.txt` y `constraints-py311.txt`:

- aiohttp 3.14.3 → **3.14.4**.
- yarl 1.23.0 → **1.25.1**, mínimo requerido por aiohttp corregido. El primer
  dry-run rechazó el pin anterior; se resolvió el conjunto sin forzar metadatos.

PyPI ofrece wheels CPython 3.11 Windows y Linux x86_64 para ambas versiones.
El plan y la instalación en el entorno de pruebas `.p4` cambiaron exclusivamente
esos dos paquetes. Sus hashes Windows coinciden con los metadatos de PyPI y
`pip check` pasa. `.p2`, `.env`, servicios y VM no se modificaron. Las
instantáneas históricas de constraints se conservan; el test de contrato admite
solo este par de cambios respecto a la referencia anterior y mantiene el resto.

La auditoría posterior del inventario **real Windows `.p4`** da seis entradas;
la **proyección Linux** con sustitución de esos dos pines también da seis.
La proyección no es una instalación Linux. **La CI Windows/Ubuntu con el
contrato nuevo sigue pendiente y deberá pasar antes de la entrega C4.** No se
presenta la CI anterior como validación del parche.

## Comprobaciones locales

- Dos pruebas nuevas reproducen cinco fallos de subcasos en aiohttp 3.14.3 y
  pasan en 3.14.4. Filtran cookies sintéticas en memoria: HTTP/HTTPS, WS/WSS,
  caché calentada y excepción limitada al origen indicado; no hacen peticiones.
  Esto verifica ese comportamiento, no reproduce todos los avisos del servidor.
- 376 Python: 375 aprobadas y una exclusiva Linux omitida en Windows; tres
  comprobaciones JS; 101 archivos sin errores de sintaxis; HTTP sintético y
  27 escenarios SDK offline aprobados. No hubo llamadas reales de proveedor.
- Contrato e inventario `.p4`: 172/0/0. Primer pase de regresión: falló solo la
  expectativa de igualdad con la instantánea histórica; se ajustó esa prueba
  conservando el archivo histórico, y el pase final fue correcto.
- Frontend: auditoría de producción cero avisos; desarrollo conserva uno alto
  en braces. No cambió el lockfile ni se actualizaron paquetes frontend.
- Gitleaks 8.30.1, binario con hash ya verificado, reglas estándar y redacción al 100 %:
  cuatro coincidencias actuales de hashes públicos y cinco históricas, todas
  triadas. La quinta histórica es el CSRF opaco conocido; no aparece como valor
  original en el fixture actual. No se añadieron allowlists ni se reescribió Git.

La red del sandbox bloqueó el primer audit; se conservó su resultado fallido y
la repetición autorizada completó las consultas. Los intentos de prueba atascados
se identificaron por su comando y se cerraron; la ejecución autorizada fuera
del bloqueo pasó. Un error de lectura UTF-8 del plan se corrigió antes de
instalar. Estos incidentes no se cuentan como pruebas aprobadas.

## Registro de riesgos y tratamiento propuesto

La severidad de un aviso no se rebaja por no observar un camino de explotación.
«No observado» describe el alcance revisado; no demuestra ausencia universal.

| ID | Riesgo conservado | Evidencia/exposición revisada | Tratamiento para esta entrega |
| --- | --- | --- | --- |
| R1 | Aiohttp vulnerable en el contrato publicado anterior | Tres avisos corregibles; fuga de selección de cookie reproducida sin red | Par aiohttp/yarl corregido y validado localmente; exigir CI nueva en C4 antes de distribuir la versión final. No afirmar que una instalación existente ya se actualizó |
| R2 | Chroma 1.5.9: cinco entradas/cuatro IDs, incluidas críticas, sin parche declarado en las fichas consultadas | No hay servidor Chroma, `trust_remote_code` o cliente Chroma en las construcciones legacy/structured observadas el 18/10. Fuentes de esas rutas siguen iguales; aquella prueba solo cubre construcción en Windows | Retener avisos y dependencia compatible. No activar servidor, memoria/conocimiento o herramientas Chroma como parte de esta entrega. Una integración futura exige reevaluar exposición y compatibilidad |
| R3 | MCP 1.28.1: agotamiento de sesiones Streamable HTTP; correcciones 1.30.0/2.2.0 fuera del rango CrewAI | CrewAI instalado 1.15.27 y publicado 1.15.28 mantienen `mcp~=1.28.1`. No se observa servidor stateful MCP en las rutas revisadas; no se certifican todos los caminos. Base GitHub media/mantenedor alta conservadas | No forzar override. Mantener el uso local sin servidor MCP/herramientas nuevas y revisar una migración compatible cuando exista. Los dry-run del 18/10 siguen como evidencia histórica, no como resoluciones repetidas hoy |
| R4 | braces 3.0.3, un aviso alto de desarrollo, sin 3.0.4 publicada | Auditoría de producción: cero; no se observan patrones glob de logs usados como configuración de build | Mantener lockfile y builds con fuentes de confianza. Conservar aviso; no presentar cero avisos globales o un parche inexistente |
| R5 | MariaDB/DVWA y referencias legacy con vulnerabilidades, incluidas críticas/altas | Último escaneo completo 19/10: MariaDB: 102 entradas, una crítica y 24 altas; DVWA: 4011 entradas, 16 críticas y 276 altas. Son imágenes fijadas, no imágenes corregidas. No se ejecutó otro escaneo Docker el 20/10 | Laboratorio intencionalmente vulnerable: solo Compose recomendado, puertos loopback, red DB interna, sin montaje del repo ni publicación pública. Legacy no es instalación recomendada. Cualquier cambio de imagen necesita evaluación propia y respaldo DB antes de aplicar |
| R6 | Mailpit conserva UNKNOWN GO-2026-5932 | El registro Go describe OpenPGP sin mantenimiento y sin versión corregida en su rango. Se conserva el hallazgo del escaneo 19/10; no se probó aquí qué función invoca Mailpit | Solo sink de correo sintético local, sin entrega externa. Conservar mensajes necesarios antes de recrear; no excluir el aviso por su etiqueta UNKNOWN |
| R7 | CSRF opaco histórico de procedencia no acreditada | Fixture actual anonimizado con 32 ceros; hallazgo original permanece en el historial. No se probó su validez o servicio asociado | Mantener triage e incertidumbre. No afirmar credencial válida, historial limpio o incidente descartado. Si se acredita una sesión real, gestionar su invalidación con su propietario antes de ampliar la exposición; sin probar el valor contra servicios |
| R8 | Datos/credenciales locales y límites de interfaz/modelo | `.env` es texto sin cifrar; logs/backups pueden contener datos. Lectura local, hosts/orígenes y límites de cuerpo existentes; no autenticación multiusuario. Los agentes no actúan sobre shell/Docker/avisos | Instalación personal en localhost, permisos propios y datos autorizados; no compartir `.env` ni desplegar como servicio público. Sin promesas de resistencia LLM o remediación automática; C2 mantiene su alcance aceptado |

Fuentes de R2–R4: [CrewAI/PyPI](https://pypi.org/pypi/crewai/json),
[Chroma/PyPI](https://pypi.org/pypi/chromadb/json),
[MCP del mantenedor](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-84m7-p3x7-pcfv),
[braces/npm](https://registry.npmjs.org/braces) y
[aviso braces](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm).
R5 usa [el escaneo verificado del19/10](FIJACION_IMAGENES_LAB_2026_10_19.md),
sin atribuirle una DB o fecha nuevas. R6 conserva la
[ficha Go](https://pkg.go.dev/vuln/GO-2026-5932).
La [revisión anterior](REVISION_DEPENDENCIAS_SECRETOS_2026_10_18.md) contiene
los IDs, límites de construcción y tratamiento histórico del CSRF.

## Propuesta presentada y decisión recibida

Recomiendo aceptar este **tratamiento residual para uso local aislado**,
conservando R2–R8 como riesgos/limitaciones y R1 como corrección que necesita
CI de entrega. C3 se cerraría en tratamiento y decisión, sin afirmar que se han
eliminado vulnerabilidades o auditado exhaustivamente toda la aplicación.

La alternativa es mantener su corrección integral como requisito previo y
abrir una migración de dependencias/arquitectura separada; no puede lograrse
forzando MCP o suprimiendo resultados del escáner.

La aceptación no autoriza LLM, notificaciones, Docker/VM o una release. C4
mantiene revisión del contenido final, CI del parche, notas y publicación;
V1 mantiene sus respaldos y comprobaciones antes de actualizar la VM existente.
El usuario aceptó expresamente el tratamiento descrito y sus condiciones.
**C3 queda cerrado en tratamiento de riesgos para este uso local acotado.**
R2–R8 permanecen registrados como riesgos/limitaciones; no se marcan arreglados.
R1 tiene corrección local y debe validar su CI en C4 antes de entregar.
No se reutilizará esta decisión para justificar una exposición pública o una
integración nueva con Chroma/MCP sin revisión propia.

Los riesgos se revisarán de nuevo al cambiar pines, capacidades Chroma/MCP,
exposición de red, finalidad del laboratorio o datos transmitidos. No se crea
una automatización ni una garantía de actualización continua por esta acta.

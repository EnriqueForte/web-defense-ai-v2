# Dependencias y revisión de secretos — 18/10/2026

Estado: revisión de compatibilidad y aplicabilidad completada; fixture DVWA
anonimizado y comprobado localmente. Publicación y CI del ajuste pendientes.
Chroma/MCP/braces conservan sus avisos; no se declara cierre global de seguridad.
Los recibos y hallazgos originales con redacción se conservan en
`.local-state/security-dependencies-20261018/`, excluido de Git.

## Auditoría actualizada y decisión de compatibilidad

Se repitió pip-audit 2.10.1/PyPI sobre los freezes completos verificados de
CI39120143671: 172 paquetes por plataforma y los mismos hashes de entrada.
Windows y Linux mantienen seis entradas/cinco IDs principales en Chroma 1.5.9
y MCP 1.28.1. pnpm 11.19.0 mantiene cero avisos de producción y uno alto de
desarrollo en braces 3.0.3. No se instalaron paquetes ni se suprimieron avisos.
El [registro JSON](REVISION_DEPENDENCIAS_SECRETOS_2026_10_18.json) conserva IDs,
aliases, correcciones declaradas, fuentes y alcance.

| Dependencia | Consulta oficial del 18/10 | Decisión |
| --- | --- | --- |
| CrewAI | Publicado 1.15.28; instalado 1.15.27; ambos requieren MCP ~=1.28.1 | Actualizar solo CrewAI no resuelve el aviso MCP |
| MCP | La ficha corrige la rama 1.x en 1.30.0 y la 2.x en 2.2.0; latest 2.3.0 | No forzar fuera del rango declarado por CrewAI |
| Chroma | Latest 1.5.9; cuatro IDs sin corrección declarada en las fichas revisadas | Mantener el aviso y la revisión de caminos de uso |
| braces | Latest 3.0.3; 3.0.4 no publicada; ficha sin versión corregida | Mantener el aviso de desarrollo |

Dos resoluciones pip reales con `--dry-run --ignore-installed --only-binary`
rechazan MCP 1.30.0 combinado con CrewAI 1.15.27 y 1.15.28:
`ResolutionImpossible`, conflicto con `mcp~=1.28.1`. Se usa PyPI público y modo
aislado, sin instalar o construir paquetes. Una migración necesita una versión
compatible del conjunto, no un override que ignore sus metadatos.

Fuentes: [CrewAI/PyPI](https://pypi.org/pypi/crewai/json),
[MCP/PyPI](https://pypi.org/pypi/mcp/json),
[ficha MCP del mantenedor](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-84m7-p3x7-pcfv),
[Chroma/PyPI](https://pypi.org/pypi/chromadb/json),
[braces/npm](https://registry.npmjs.org/braces) y
[ficha braces](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm).
La ficha MCP del mantenedor indica alta y la base GitHub consultada media;
ambos datos quedan conservados, sin escoger uno para ocultar el otro.

## Uso observado en la aplicación

La revisión de fuentes no encuentra un servidor MCP Streamable HTTP, Chroma
servidor, `trust_remote_code` o patrones de glob derivados de logs de usuario.
Se construyen los objetos reales de las rutas legacy y structured con un LLM
que rechaza cualquier invocación, dotenv desactivado y conexiones bloqueadas.
Se extraen solo las definiciones necesarias de `main.py`, sin ejecutar su entrada.
El almacenamiento de los constructores se dirige a una carpeta aislada.

Resultado en las dos rutas: tres agentes sin referencias MCP, herramientas,
fuentes de conocimiento o ejecución de código; memoria del Crew desactivada.
Los interceptores no observan construcción de clientes Chroma ni servidor
FastMCP. No se ejecuta kickoff. Esta evidencia cubre la construcción de esos
objetos; no certifica todo el comportamiento de dependencias o una integración
MCP/Chroma futura. Los avisos siguen retenidos.

## Archivos publicados e historial

Se descargó Gitleaks 8.30.1 desde su publicación oficial y se verificó el ZIP
Windows x64 contra su checksum SHA-256:
`d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e`.
La [documentación de Gitleaks](https://github.com/gitleaks/gitleaks) describe sus
modos de análisis de archivos y parches Git. Se usan sus reglas estándar,
redacción al 100 %, sin baseline ni lista de exclusiones del proyecto, ignorando
comentarios inline de permiso. Un identificador AWS sintético fue detectado y
redactado antes de analizar el proyecto; no se contactó AWS.

Primera revisión sobre `4c02306`: 255 archivos candidatos y los 73 commits
alcanzables desde HEAD, incluyendo parches de merges. Se copian únicamente
archivos publicables a una carpeta aislada; no se recorre el directorio operativo
ni se leen archivos `.env` ignorados. No se incluyen otras referencias, objetos
inalcanzables ni archivos locales excluidos de Git. Es una búsqueda por patrones,
no prueba de ausencia de cualquier secreto o una auditoría completa del producto.

El escáner produjo cinco coincidencias en el candidato inicial y cinco en el
historial. Cuatro de cada conjunto coinciden exactamente con hashes públicos
de recursos BPE de tiktoken 0.12.0 o con sus claves de caché derivadas por SHA-1
de la URL pública. No son material de autenticación; se conservan como hallazgos
revisados, sin añadir allowlists o descartar archivos completos de pruebas.
El contraste usa los valores de `expected_hash` y URLs del
[módulo público de tiktoken](https://github.com/openai/tiktoken/blob/0.12.0/tiktoken_ext/openai_public.py).

La quinta coincidencia era un valor CSRF opaco en el log generado por
`tests/test_groq_cache_transport.py`, introducido en `33d987b`. Se reemplaza en
el fixture actual por 32 ceros y un comentario que explicita su carácter
sintético, conservando el formato y longitud. Su origen y validez como sesión
real no están acreditados; no se prueba contra ningún servicio ni se presenta
como credencial de autenticación confirmada. El hallazgo histórico permanece,
sin imprimir su valor ni reescribir Git. La revisión posterior del código
anonimizado da cuatro coincidencias actuales de hashes públicos y las cinco
históricas anteriores. La procedencia del valor histórico sigue sin acreditarse.
El candidato con estas actas añade dos archivos: 257 revisados, mismas cuatro
coincidencias actuales y cinco históricas, todas con triage individual conservado.

## Validación y límites de esta entrega

Las siete pruebas de transporte Groq/fixture pasan, incluidas conservación de
líneas/referencias, HTTP sintético, publicación aislada y rechazo 413 sin
fallback. Pip check correcto y contrato estricto: 172 paquetes, cero diferencias
y cero adicionales. Los primeros dos procesos de comprobación se bloquearon
dentro del sandbox; se verificaron y detuvieron sus procesos propios y las
ejecuciones aprobadas fuera de ese bloqueo pasaron, manteniendo la red y dotenv
desactivados. No se cambia código de producto, prompts ni requisitos.

CI Windows/Ubuntu pendiente del commit. No se actualiza la VM ni se inicia un
servicio operativo, Docker, un análisis LLM real o un envío externo. Continúan
abiertos los riesgos de dependencias/infraestructura, la procedencia del dato
CSRF histórico, la calidad semántica general A-05 y la entrega final.

# Migración compatible de CrewAI — 12/10/2026

## Resultado local y selección

Se resolvió e instaló un candidato completo en `.p4`, entorno nuevo de prueba.
Pasa pip check, contrato estricto de 172 paquetes sin diferencias/adicionales,
regresión Python/JS, los 25 escenarios CrewAI/LiteLLM offline, construcción de
adaptadores legacy/structured y HTTP sintético. No se llama al proveedor.

El contrato del proyecto incorpora 13 versiones modificadas y 14 paquetes
adicionales. Las instalaciones anteriores `.p2`, `.p3` y `.venv` se conservan;
no se activan con el contrato nuevo hasta su actualización controlada. `.p3`
informa 27 diferencias respecto al nuevo contrato; `.p4` no es un piloto activo.

| Componente | Antes | Candidato comprobado |
| --- | --- | --- |
| CrewAI | 1.14.3 | 1.15.27 |
| LiteLLM | 1.83.0 | 1.105.0 |
| JSON Repair | 0.25.3 | 0.60.1 |
| MCP | 1.26.0 | 1.28.1 |
| Chroma | 1.1.1 | 1.5.9 |
| pydantic-settings | 2.10.1 | 2.14.2 |
| OpenTelemetry API/SDK/exportadores/proto | 1.34.1 | 1.42.0 |
| OpenTelemetry convenciones | 0.55b1 | 0.63b0 |

CrewAI 1.15.27 exige crewai-core/crewai-cli de la misma versión y admite los
rangos corregidos de JSON Repair/MCP/LiteLLM. Sus dependencias se resolvieron
respetando los metadatos publicados, sin ignorar dependencias al instalar.
LiteLLM añade AWS/HTTP2; el grafo también añade CEL/pendulum y sus dependencias.
Las 14 adiciones están fijadas en requisitos/constraints. Pydantic 2.11.10,
OpenAI 2.32.0, modelos, proveedores y límites del proyecto se conservan.

Fuentes: [CrewAI 1.15.27](https://pypi.org/project/crewai/1.15.27/),
[changelog](https://docs.crewai.com/v1.15.27/en/changelog),
[LiteLLM 1.105.0](https://pypi.org/project/litellm/1.105.0/).

## Tokenización offline y candidato anterior

Un primer candidato con LiteLLM 1.96.2 resolvió 166 paquetes y redujo los avisos,
pero falló el SDK offline al importar: el wheel no contenía el recurso cl100k_base
en la caché utilizada por default_encoding. Intentó descargar el archivo; el
bloqueo de sockets de la prueba lo impidió antes de cualquier conexión real.
Se conservan sus recibos y no se considera una migración final válida.

El wheel oficial de LiteLLM 1.105.0 se descargó y verificó contra el SHA-256 de
PyPI. Incluye cl100k_base con el hash esperado por tiktoken 0.12.0:
`223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7`.
El SDK posterior pasó con la red bloqueada. No se reemplazó el tokenizador por
un doble ni se preparó una caché global para ocultar el problema del primer wheel.

## Auditoría y verificación

pip-audit 2.10.1/PyPI sobre el inventario completo del candidato: 172 paquetes,
cinco entradas en Chroma 1.5.9, cuatro IDs principales, sin corrección declarada.
Antes: 36 entradas/22 IDs/cuatro paquetes. No son recuentos de explotaciones
probadas. JSON Repair/LiteLLM/MCP no aparecen como avisos en esta consulta.
No se suprimió ningún aviso ni se declara seguridad global cerrada.

- Windows `.p4`: pip check y 172 pines/0 diferencias/0 adicionales.
- Freeze completo/metadatos/contrato y hash coincidentes.
- 298 casos Python: 297 aprobados, un caso Linux omitido; tres JS aprobados.
- CrewAI/LiteLLM: 25 escenarios offline aprobados, incluida preservación de
  publicación ante fallos, formato JSON original y reintento de clasificación.
- Adaptadores: legacy/structured, candidatos y límites 8192/60 conservados.
- HTTP sintético: Flask/CSP/informe/recursos e integridad aprobados.
- Diez pruebas de instalación repetidas tras cambiar la instantánea de referencia;
  82 archivos de sintaxis y diff check aprobados.

La [instantánea Windows nueva](../constraints-windows-py311-crewai-20261012.txt)
deriva de metadatos observados en `.p4`. El contrato común tiene marcador
pywin32 Windows/uvloop Linux; el objetivo Linux es 172 pines. Las instantáneas
anteriores de 158 paquetes se conservan como evidencia histórica.

Recibos `.local-state/migration-20261012/`; primer candidato en `litellm-1.96.2/`.
29 trabajos, 14 entregas, cero activos, hashes de log/publicación e informe y
metadatos de `.env` operativos preservados según comparación antes/después.
No se leen secretos ni se ejecutan análisis reales, Docker, notificaciones o
servicios operativos del mantenedor. El guardrail y las tres tareas no cambian.

## Validación remota y actualización del usuario

Instalación limpia, SDK y lanzador Windows/Ubuntu con el contrato nuevo están
pendientes de CI. No se atribuye al nuevo contrato la CI anterior de 158 pines.
No se acredita análisis real con proveedor ni calidad semántica A-05 por pruebas
con respuestas simuladas. Chroma, braces de desarrollo y riesgos de imágenes
conservan sus pendientes independientes.

Después de publicación y CI aprobada, con la consola de la VM detenida:

```bash
git pull --ff-only
python3 webdefense.py install
.p2/bin/python -B scripts/check_environment.py --strict
.p2/bin/python -B scripts/snapshot_environment.py
```

Se espera 172 pines y cero diferencias/adicionales. La actualización conserva
`.env` existente; no inicia worker, proveedor ni análisis. Confirmación en Parrot
pendiente; no se prescribe actualizar mientras haya trabajos/servicios activos.

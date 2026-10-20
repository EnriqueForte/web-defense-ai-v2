# C4 — Entrega local v0.1.0 — 20/10/2026

**Código y contenido de entrega verificados.** El usuario pidió continuar C4
después de aceptar C2 y C3. El código `0d73ec26f5c214f820cd3b6bbefd5fe0681d62c8`
está publicado en V2 y su [CI 39466610699](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/39466610699),
intento 1, terminó correctamente en Windows/Ubuntu. La identidad de distribución
es [v0.1.0](https://github.com/EnriqueForte/web-defense-ai-v2/releases/tag/v0.1.0),
primera versión local acotada; su publicación formal se comprueba en GitHub.
El [registro JSON](ENTREGA_LOCAL_C4_2026_10_20.json) conserva la evidencia técnica.
No se actualiza la VM.

## Contenido de la entrega

- [Documentación vigente](../README.md), instalación, lectura, análisis manual
  y recuperación diferenciados; cronologías anteriores preservadas.
- [Aceptación C2](REVISION_ACEPTACION_A05_2026_10_20.md) para la primera versión
  local de apoyo a la revisión de indicadores; comparación legacy diferida.
- [Tratamiento C3](TRATAMIENTO_RIESGOS_C3_2026_10_20.md) aceptado para uso personal
  local aislado, con los riesgos R1–R8 y avisos conservados.
- Parche exacto aiohttp 3.14.3 → 3.14.4 y yarl 1.23.0 → 1.25.1 en requisitos y
  contrato actual. Los snapshots históricos permanecen intactos.
- Dos regresiones de cookies Secure y ajuste de la comprobación del inventario
  histórico para permitir exclusivamente ese par revisado.

No cambia el detector, los prompts, el proveedor, la API, la interfaz, los
digests del laboratorio o las publicaciones operativas existentes.

## Comprobaciones de entrega

La validación local C3 pasó 376 casos Python (375 aprobados y uno exclusivo de
Linux omitido en Windows), tres JS, 101 comprobaciones de sintaxis, HTTP
sintético, 27 escenarios SDK offline e inventario 172/0/0. La auditoría posterior
conserva seis entradas Chroma/MCP y el aviso braces de desarrollo. La proyección
Linux de C3 queda contrastada con la instalación real de esta CI: su freeze
completo tiene el mismo hash. La evidencia de C3 conserva su fecha original.

| Comprobación | Evidencia verificada el 20/10 |
| --- | --- |
| Repositorio de destino | V2 privado; publicación de código `0d73ec2` sobre `ca2f6af`, sin alterar el repositorio original |
| Identificación de distribución | `v0.1.0`; no había tags/releases en la consulta autenticada inicial. La etiqueta final debe conservar el mismo árbol de producto que el código probado; después solo se actualizan actas |
| Contenido y secretos | Candidato de código: 278 archivos y 81 commits alcanzables. Gitleaks conserva cuatro hashes públicos actuales y cinco hallazgos históricos, incluido CSRF opaco; cero casos sin clasificar. Revisión final repetida tras las actas, sin allowlists propias ni reescritura de historia |
| CI del parche | Instalación nueva/build Windows y Ubuntu, 376 casos Python por OS (Windows: 375 aprobados y uno Linux omitido), tres JS, 101 sintaxis, HTTP y 27 SDK offline, lint/tipos, 17 grupos UI y nueve E2E por OS; API/proxy 200 y puertos libres al cerrar |
| Inventarios | Artefactos 12285142801 Windows y 12285816295 Ubuntu: 172 paquetes/0 diferencias/0 adicionales; solo cambia el par aiohttp/yarl frente a CI39239742802. Hashes iguales al inventario auditado Windows y a la proyección auditada Linux |
| Publicaciones sintéticas | Artefactos 12285716664 Windows y 12285441800 Ubuntu: 24 casos/ocho controles, 25 publicaciones completas y 101 archivos por OS; manifiestos, punteros, hashes y métricas recomputadas comprobados, bytes JSON/Markdown iguales a la revisión local anterior |
| Notas de versión | [Contenido de v0.1.0](NOTAS_VERSION_LOCAL_2026_10_20.md), alcance y riesgos aceptados, con referencia a código y CI |
| VM/recuperación Docker | V1 condicional separado; no realizado ni incluido como afirmación de esta entrega |

La CI usada es `compatibility.yml`, ya existente: credenciales de proveedor
vacías, notificaciones desactivadas y pruebas sintéticas. Este bloque no
despacha el escaneo de imágenes ni las pruebas Docker opcionales. No autoriza
análisis LLM reales ni reutiliza los ensayos consumidos.

Los logs finales acreditan en ambos OS las dos regresiones de cookies y la
comprobación del snapshot histórico ajustada. Python tardó 42,345 s en Ubuntu
y 46,295 s en Windows; los nueve E2E, 10,6 s y 9,0 s respectivamente. Son tiempos
de estas ejecuciones sintéticas, sin estimación de rendimiento del proveedor.

C4 vincula el código probado, el contenido revisado y las notas a `v0.1.0`.
La publicación formal es el último paso de distribución y no constituye otra
validación del motor. Las actas añadidas después de `0d73ec2` se verifican como
cambios documentales; no se atribuye una nueva CI a esos commits de actas.
V1 permanece condicional y C2/C3 conservan íntegros sus límites y avisos.

Los recibos locales se conservan ignorados en
`.local-state/c4-delivery-20261020/`; no son archivos de la distribución.

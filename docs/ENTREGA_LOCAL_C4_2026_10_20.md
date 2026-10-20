# C4 — Preparación de la entrega local — 20/10/2026

**En curso.** El usuario pidió continuar C4 después de aceptar C2 y C3.
Este bloque publica el código revisado en el repositorio V2 y verifica su CI
Windows/Ubuntu antes de proponer una versión formal. No actualiza la VM.

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

## Comprobaciones y condición de cierre

La validación local C3 pasó 376 casos Python (375 aprobados y uno exclusivo de
Linux omitido en Windows), tres JS, 101 comprobaciones de sintaxis, HTTP
sintético, 27 escenarios SDK offline e inventario 172/0/0. La auditoría posterior
conserva seis entradas Chroma/MCP y el aviso braces de desarrollo. La proyección
de paquetes Linux de C3 no sustituye una instalación real en CI.

| Comprobación | Estado al preparar la publicación |
| --- | --- |
| Repositorio de destino | V2 privado; `main` local/remoto coincide con `ca2f6af6ceba7af7b5d1fe78bff2bdf0c740ef4c` antes de publicar |
| Tags y releases | Consulta autenticada del 20/10: ninguno; no se infiere una versión ya entregada |
| Contenido y secretos | Revisión final del candidato y del historial alcanzable antes de publicar; conservar triage y avisos |
| CI del parche | Pendiente; instalación nueva Windows/Ubuntu, inventarios, pruebas, build, UI/E2E sintéticos y cierre de puertos |
| Artefactos completos | Pendientes; verificar inventarios y las 25 publicaciones sintéticas por OS, hashes y métricas |
| Notas de versión | [Borrador revisable](NOTAS_VERSION_LOCAL_2026_10_20.md), sin tag ni release creados |
| VM/recuperación Docker | V1 condicional separado; no realizado ni incluido como afirmación de esta entrega |

La CI usada es `compatibility.yml`, ya existente: credenciales de proveedor
vacías, notificaciones desactivadas y pruebas sintéticas. Este bloque no
despacha el escaneo de imágenes ni las pruebas Docker opcionales. No autoriza
análisis LLM reales ni reutiliza los ensayos consumidos.

C4 se cerrará cuando el código final tenga CI revisada, contenido comprobado,
notas coherentes y la identificación/publicación de versión acordada. Una
actualización posterior de actas se distinguirá del commit de código probado.

Los recibos locales se conservan ignorados en
`.local-state/c4-delivery-20261020/`; no son archivos de la distribución.

# Validación de configuración global — 13/10/2026

## Comportamiento

El ejecutor podía fallar al importar `config/settings.py` con una conversión
numérica poco comprensible. Ahora valida conjuntamente sus cuatro parámetros
numéricos y muestra los nombres que deben corregirse antes de cargar el resto
del ejecutor. No imprime los valores introducidos ni el traceback en la CLI.
Por ejemplo, `INTERVALO_MINUTOS=abc` termina con código 2 y explica que debe ser
un entero positivo; no crea la base de trabajos, el heartbeat o archivos de datos.

| Variable | Valores admitidos | Predeterminado si falta |
| --- | --- | --- |
| `INTERVALO_MINUTOS` | Entero >=1, con segundos representables como número finito | 3 |
| `MAX_LINEAS_LOG` | Entero entre 1 y 1000 | 100 |
| `UMBRAL_FUERZA_BRUTA` | Entero entre 1 y 100 | 5 |
| `LLM_TEMPERATURE` | Número finito entre 0 y 2 | 0.1 |

Una variable presente pero vacía, no numérica o fuera de rango se rechaza;
no se sustituye silenciosamente por el predeterminado. Los límites de líneas
e intentos coinciden con los ya exigidos por la preparación structured.
Se mantienen el comportamiento de rutas, la precedencia de dotenv existente y
los predeterminados de configuración global. No se cambia el resolver LLM,
sus reintentos ni el preprocesamiento legacy. Esta validación corresponde al
ejecutor que importa `config.settings`, no certifica todas las entradas del motor
iniciado directamente ni el formulario de Configuración.

## Comprobación

Cinco pruebas nuevas cubren predeterminados/límites, valores vacíos y tipos
incorrectos, NaN/infinito/desbordamiento, varios errores simultáneos y carga real
del módulo. Un intérprete separado ejecuta la CLI del worker con configuración
sintética inválida: salida 2, mensaje sin valor privado/traceback y directorio
temporal sin archivos creados. Dotenv operativo deshabilitado para esta prueba.

Se usa `.p4` como entorno de pruebas aislado del contrato de 172 paquetes;
no se activa como entorno operativo. La línea base completa pasó 303 casos
Python (302 aprobados y uno exclusivo de Linux omitido en Windows) y tres JS.
El primer ensayo dentro del sandbox fue bloqueado por permisos de reemplazo
de archivos temporales y sockets locales; el ensayo autorizado fuera del sandbox
pasó. La comprobación de sintaxis cubre 84 archivos.

Recibos ignorados: `.local-state/config-validation-20261013/`. No se modifica
el `.env` operativo ni se inicia el worker operativo, Docker, análisis real,
proveedor o notificaciones. El E2E de guardar/recargar/desmontar Configuración
(R-15), A-05, laboratorio Parrot y seguridad residual conservan sus pendientes.

## Publicación y CI comprobada

Código `710a34bbdd2fcae5b9ede171a025f88b59cb7b20`,
[CI 38377769557](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38377769557),
attempt 1: Windows-latest y Ubuntu24.04 completaron con success. Se revisaron
los estados finales, logs de comprobación y artefactos de ambos sistemas.

Ambos completaron instalación nueva/build, pip check/172 pines estrictos sin
diferencias ni extras, 84 archivos de sintaxis, tres JS, HTTP sintético,
25 escenarios SDK offline, lint/tipos/15 UI y smoke del lanzador con API directa
y proxy HTTP200, ejecutor offline y puertos libres al cerrar. Ubuntu aprobó los
303 casos Python; Windows aprobó 302 y omitió el caso TIME_WAIT exclusivo Linux.

Artefactos de inventario 11802305796 (Windows Python3.11.9) y 11801918324
(Ubuntu Python3.11.17): 172 paquetes cada uno, metadatos/freeze/contrato
coincidentes. Sus hashes freeze coinciden con los ya conservados en la
[migración CrewAI](MIGRACION_CREWAI_2026_10_12.md); no hubo cambio de dependencias.
Recibos en `.local-state/launcher-20261012/` y
`.local-state/linux-contract-20261012/artifacts-38377769557/`.

El estado operativo local coincide con el último recibo de la migración:
29 trabajos, 14 entregas, cero activos, mismos hashes log/publicación/informe/
resultado y metadatos de `.env`. Comparación registrada en
`.local-state/migration-20261012/invariants-configuration-20261013.json`.
La actualización documental posterior usa `[skip ci]`; la CI corresponde al
código 710a34b. El nuevo código no se ha ejecutado operativamente en la VM Parrot.

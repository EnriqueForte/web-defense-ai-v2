# Paso 1 — Dependencias, 10/10/2026

Seguimiento posterior: la [operación del Paso 2](OPERACION_A05_2026_10_10.md)
activó `.p3` y actualizó la instalación real del frontend con estas dependencias.
Las afirmaciones de aislamiento y ausencia de arranque de esta acta describen
la entrega del Paso 1, anterior a esa operación. Los avisos residuales siguen abiertos.
El [seguimiento del 12/10](SEGURIDAD_2026_10_12.md) actualizó ambas auditorías
Python y npm/vendor, revisó las 22 fichas y completó el escaneo de las seis
referencias remotas con Trivy Linux/digests/base. Quedan migración e infraestructura,
según ese registro; el bloqueo Windows y el escaneo pendiente de esta acta son históricos.

## Resultado

La actualización compatible está implementada y validada en Windows aislado.
Producción frontend tiene cero avisos; Python dispone de un contrato de 158 pines,
sin diferencias en `.p3` ni conflictos declarados. **El Paso 1 sigue abierto**:
quedan avisos residuales y el escaneo efectivo de imágenes.

Se preservaron `.p2`, `.venv`, node_modules y `.next` del frontend operativo,
`.env`, datos y cambios anteriores. No se ejecutaron motor, LLM, notificaciones
o Docker, ni se reiniciaron servicios o publicó código. El frontend nuevo se
instaló y compiló en una copia bajo `.local-state/dependencies-20261010/`.
`.p3` es un entorno de validación, no una activación del piloto.

La [revisión del 08/10](REVISION_PROYECTO_2026_10_08.md) es evidencia anterior.
El [recibo de auditoría](DEPENDENCIAS_AUDIT_2026_10_10.json) conserva versiones,
IDs, recuentos y estados pendientes sin suprimir avisos.

## Cambios

Next y eslint-config-next pasan de 16.3.6 a **16.3.8**, con lockfile actualizado.
Se cambian los paquetes de Next, su plugin ESLint y SWC; React, Lucide, Tailwind,
TypeScript y los overrides source-map-js/sharp conservan sus versiones.
El mantenedor identifica las [correcciones de esta publicación](https://github.com/vercel/next.js/releases/tag/v16.3.8).

La verificación final utiliza pnpm 11.19.0 instalado como herramienta local.
Una primera resolución usó el pnpm del PATH, 11.25.0; la instalación congelada
y los ensayos finales usaron el 11.19.0 declarado. No se cambian herramientas globales.

Python actualiza 23 versiones y añade langchain-protocol exigido por las versiones
corregidas de LangChain. También se fijan pip/setuptools tras auditar el venv completo.

| Paquetes | Versiones nuevas |
|---|---|
| aiohttp / anyio | 3.14.3 / 4.14.2 |
| CrewAI / python-dotenv | 1.14.3 / 1.2.2 |
| cryptography / fsspec / idna | 50.0.0 / 2026.6.0 / 3.15 |
| langchain / langchain-core / langchain-protocol | 1.3.9 / 1.4.6 / 0.0.19 |
| langgraph / checkpoint / prebuilt / SDK | 1.2.4 / 4.1.1 / 1.1.0 / 0.4.4 |
| langsmith / multidict / oauthlib | 0.8.18 / 6.9.1 / 4.0.0 |
| Pillow / PyJWT / python-multipart | 12.3.0 / 2.15.0 / 0.0.31 |
| starlette / urllib3 / uv / Werkzeug | 1.3.1 / 2.8.0 / 0.11.15 / 3.1.9 |
| pip / setuptools del venv | 26.2.1 / 83.0.0 |

La selección responde a avisos y requisitos publicados. Las resoluciones en seco
rechazaron combinaciones incompatibles de LangChain; core/graph/prebuilt se
alinearon con sus mínimos requeridos. CrewAI 1.14.3 permite dotenv corregido.
No se cambiaron prompts, modelos, límites o modo de análisis para aceptar el candidato.

Se conserva LiteLLM 1.83.0: las versiones de parche examinadas de la rama 1.83
fijan versiones concretas de otras dependencias; 1.83.14 no encaja con el candidato.
La línea 1.96.2 examinada y CrewAI 1.15.27 implican una migración mayor del grafo,
incluida su separación en crewai-core/cli, que esta entrega no acredita.
No se eluden requisitos con `--no-deps` al instalar. Ese flag se usa solamente
para auditar inventarios completos ya fijados, junto con `--disable-pip`.

`requirements.txt`, `requirements-test.txt` y `constraints-py311.txt` comparten
el contrato nuevo. `requirements-bootstrap.txt` fija herramientas: el instalador
las prepara en el venv antes de las dependencias de la app, y un fallo detiene el
plan antes de instalar app/frontend. Plan por defecto, `--install` explícito y
preservación de `.env` se mantienen; no se ejecuta sobre los entornos operativos.

La [instantánea Windows nueva](../constraints-windows-py311-dependencies-20261010.txt)
se genera de metadatos observados en `.p3`, incluyendo bootstrap y marcador pywin32.
Las instantáneas históricas se conservan. La comparación con marcadores Linux
no acredita instalación Linux/Parrot.

## Auditorías y avisos residuales

| Inventario | Antes | Después |
|---|---|---|
| Frontend producción | 6 avisos: 1 alto/4 moderados/1 bajo | 0 |
| Frontend completo | 7 avisos | 1 alto: braces de desarrollo |
| Python | 162 entradas en 24 paquetes del contrato inicial de 155 pines | 36 entradas en 4 paquetes del entorno final de 158 pines |
| Chart.js 4.4.1 / marked 9.1.6 | Sin auditoría actual acreditada | 0 avisos en manifiesto temporal con versiones exactas |

Python se auditó con pip-audit 2.10.1/servicio PyPI. No hay paquetes omitidos.
La base contiene duplicados y aliases: 162 entradas tenían 100 IDs distintos;
36 entradas finales tienen 22 IDs. **No son recuentos de vulnerabilidades
explotables distintas en esta app.** No se usó `--ignore-vuln`; el audit final
Python sigue devolviendo código 1.

También se auditó el candidato instalado antes de actualizar bootstrap: pip 24.0
y setuptools 65.5.0 añadían 20 entradas a las 36 de la aplicación. Tras corregirlos,
la auditoría completa de los 158 paquetes vuelve a esas 36 entradas.

Braces 3.0.3 entra por ESLint/fast-glob/micromatch. La consulta npm no encuentra
3.0.4; [GitHub tampoco declara parche](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm).
Se conserva el aviso sin override ficticio, supresión o parche propio no acreditado.
La app no ofrece una API de patrones glob de ESLint a sus usuarios; eso limita
el alcance observado, no certifica ausencia de riesgo.

| Paquete retenido | Entradas | Revisión de alcance |
|---|---|---|
| chromadb 1.1.1 | 5 | Avisos de endpoints del servidor; la base no informa versión corregida. No se despliega servidor Chroma en esta app |
| json-repair 0.25.3 | 1 | El aviso describe SchemaRepairer/loads(schema=...). La versión instalada no contiene esa clase ni ese argumento; no se observa el camino descrito, aunque la ficha usa un rango amplio |
| litellm 1.83.0 | 24 | Avisos principalmente del proxy/servidor y funciones administrativas. La app usa completion cliente; resta revisión individual y migración del conjunto compatible |
| mcp 1.26.0 | 6 | Avisos de sesiones/tareas experimentales/WebSocket de servidor. La app no despliega servidor MCP; las correcciones quedan fuera del rango del CrewAI retenido |

Fuentes de alcance: [JSON Repair](https://github.com/advisories/GHSA-xf7x-x43h-rpqh),
[LiteLLM](https://github.com/BerriAI/litellm/security/advisories/GHSA-3cv6-jpf6-8222),
[MCP](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-jpw9-pfvf-9f58)
y [Chroma](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c).
El JSON de esta entrega conserva todos los IDs residuales y versiones sugeridas.
No se demuestra explotación ni se certifica todo camino posible por esta inspección.

Chart.js/marked no se sustituyen: el audit no encontró avisos y los bytes,
licencias y hashes siguen verificados por tests/HTTP. Se auditaron aparte porque
los recursos vendorizados no entran en el lockfile del frontend.

## Compatibilidad IPv6 y verificación

Werkzeug 3.1.9 provocó HTTP 400 para Host `[::1]:5000`: conserva la autoridad
IPv6 pero todavía divide las referencias trusted por el primer `:`. La versión
anterior tampoco realizaba una comparación exacta de IPv6.

LocalHostFlask valida autoridades con corchetes de forma explícita. Acepta `[::1]`
solo si figura en TRUSTED_HOSTS, con puerto opcional 1–65535, y preserva la autoridad
original para rutas/enlaces. Otros hosts mantienen Flask/Werkzeug; no se reescribe
el entorno ni configuración global durante una petición.

Pruebas añadidas cubren IPv6 ajena/mapeada, sufijos hostiles, puertos inválidos,
ausencia de la entrada trusted y enlaces absolutos. Utilizan WSGI directo para
evitar que el cliente antiguo rechace esos puertos antes/después de llegar a la app.
Se corrigió el cierre del builder de la fixture; no se omiten casos.

| Verificación final | Resultado |
|---|---|
| `.p3`, `.p2`, `.venv` | 257 pruebas en cada entorno; cero expected failures; tres JS por ejecución |
| `.p3` | 158 pines/0 diferencias; pip check aprobado |
| Sintaxis | 70 archivos Python/0 errores |
| Frontend aislado | Instalación frozen/ignore-scripts, lint, tipos, 14 grupos UI y build Next 16.3.8 aprobados |
| SDK `.p3` | 18 escenarios CrewAI/LiteLLM offline y adaptadores legacy/structured aprobados |
| HTTP `.p3` | Flask/CSP/informe/vendor/hash en servidor efímero sintético aprobados |

Errores de red/enlaces/temporales del sandbox se separaron del producto. El proceso
CSS falló en el primer build; una salida nueva y luego `.next` limpia compilaron.
El build final usa configuración y tsconfig originales; solo se conservó/movió
la salida fallida dentro de la copia aislada. No se cambió el bundler del producto.

Los entornos anteriores pasan regresión de código, pero no son el contrato nuevo:
`.p2` tiene 26 diferencias y `.venv` 29 frente a los 158 pines. El preflight impide
presentarlos como conformes; requieren transición operativa explícita. No se
acredita integración LLM real del entorno nuevo ni clonación final de la distribución.

## Imágenes pendientes y reversión

Trivy 0.75.0 se descargó de [su publicación oficial](https://github.com/aquasecurity/trivy/releases/tag/v0.75.0).
El ZIP coincide con el SHA-256 publicado:
`4e43bd71a30f51aee39525f60f2b47043af77eb8df8fe082aae4372b69c6660f`.
**Control de aplicaciones de Windows bloqueó el ejecutable**, también fuera del
sandbox. No se deshabilitó esa protección ni se arrancó Docker como alternativa.
No hay resultados de vulnerabilidades/SBOM/digests escaneados de imágenes.

Referencias pendientes: laboratorio `mariadb:10.11`,
`ghcr.io/digininja/dvwa:b496a5d`, `axllent/mailpit:v1.31.1`; bases legacy
`mysql:8.0`, `vulnerables/web-dvwa:latest`, `python:3.11-slim`.
Una etiqueta flotante no identifica necesariamente la imagen instalada.
Compose, imágenes operativas y volúmenes se conservan.

En un entorno permitido, [Trivy admite registros remotos](https://trivy.dev/docs/latest/target/container_image/)
sin arrancar contenedores. Ejemplo preparado, **no ejecutado**:

```text
trivy image --image-src remote --platform linux/amd64 --scanners vuln --format json --output mariadb-audit.json mariadb:10.11
```

Repetir por cada referencia, registrar digest/plataforma/fecha de la base y separar
fallos intencionales de DVWA de su infraestructura. Requiere un host que permita
el scanner, como la VM cuando esté preparada; no se solicita desactivar controles.

Quedan revisión/migración de los paquetes residuales, escaneo de imágenes y
validación Linux/Parrot. Estas actualizaciones no autorizan llamadas reales ni
cierran A-05. Recibos y copias iniciales permanecen en `.local-state/dependencies-20261010/`.
Para revertir, retirar solo los cambios de esta entrega de manifests/lockfile/
contratos y bootstrap, conservando cambios anteriores e instantáneas históricas.
La corrección de hosts es compatible con las dependencias anteriores y puede
conservarse. No usar git reset/restore global ni restaurar datos: SQLite/logs/
reportes no cambiaron. Activar el entorno exige respaldo y operación controlada;
no reemplazar paquetes de un worker activo.

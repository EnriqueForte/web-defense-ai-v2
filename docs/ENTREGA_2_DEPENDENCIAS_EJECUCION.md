# Entrega 2 — Dependencias y ejecución reproducible

Estado al 06/10/2026: implementación y comprobaciones completadas, con excepción
documentada para `braces` en desarrollo y transición del entorno operativo pendiente.
Responsable: Codex principal, sin delegación. Alcance derivado de
[la revisión integral](REVISION_INTEGRAL_2026_10_06.md).

## Resultado por hallazgo

| Hallazgo | Resultado | Límite |
|---|---|---|
| R-03, producción | `source-map-js` 1.2.2 y `sharp` 0.35.5 fijados por overrides y lockfile; audit producción sin avisos | La auditoría completa conserva `braces` |
| R-03, desarrollo | `braces` 3.0.3 identificado en ESLint Next → fast-glob → micromatch | No hay versión corregida publicada en npm; excepción temporal, no vulnerabilidad corregida ni aviso ocultado |
| R-04 | `crewai[litellm]==1.14.2`, `litellm==1.83.0` y dependencias adicionales fijadas | Cliente real construido offline; no se realizaron llamadas LLM |
| R-08 | SMTP con timeout por socket y proceso de envío con límite total por destino | Se preserva `unknown` ante timeout y no se reenvía automáticamente |
| R-16, dependencias | Instalación completa nueva, 155 paquetes fijados y comprobador de metadatos | La `.venv` operativa conserva cuatro diferencias; no se cambió durante esta entrega |

La configuración de límites de muestreo y fuerza bruta incluida en R-16 se
mantiene para la evolución A-01/A-03; no se modificaron criterios ni prompts.

## Dependencias del frontend

Se añadieron overrides exactos en `frontend/pnpm-workspace.yaml`, siguiendo
[la configuración oficial de pnpm](https://pnpm.io/settings):

- `source-map-js: 1.2.2`, corrección del [aviso de source-map-js](https://github.com/advisories/GHSA-68fv-2mgg-jv7q).
- `sharp: 0.35.5`, corrección del [aviso de sharp/librsvg](https://github.com/advisories/GHSA-wq5f-xc86-pv6w).

El lockfile actualiza esos paquetes y los binarios/libvips asociados a sharp.
No cambian versiones directas de Next.js, React o Lucide ni los rangos de
herramientas existentes. La instalación usó lockfile congelado y scripts de
paquetes desactivados, conservando `allowBuilds`.

El audit de la revisión había indicado `braces >=3.0.4` como versión corregida.
La consulta efectiva del registro confirmó que la última publicada es 3.0.3;
la [ficha GitHub del aviso](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm)
indica que no hay versión corregida. Se retiró el override no instalable.
Esta entrega corrige esa suposición del informe inicial; no publica ni utiliza
un supuesto paquete inexistente.

Excepción de alcance: la ruta es de desarrollo/lint y no aparece en
`pnpm audit --prod`. La aplicación no entrega patrones de logs o del LLM a
esas herramientas; la configuración de lint utiliza patrones del proyecto.
Esto reduce exposición en el flujo actual, pero no elimina el defecto de
la dependencia. Mantener los patrones de lint como código revisado y volver
a evaluar el aviso cuando haya una corrección o alternativa compatible.
No se añadió ningún ignore de auditoría ni se afirma que el audit completo pase.

## Contrato Python y reproducción

Se añadió el extra que realmente usa OpenRouter y se fijaron LiteLLM 1.83.0,
fastuuid 0.14.0 y tiktoken 0.12.0, compatibles con los metadatos de CrewAI
instalado. Se mantienen las cuatro versiones declaradas de aiohttp,
importlib_metadata, jsonschema y openai; no se rebajan para hacer coincidir
artificialmente el entorno operativo anterior.

Se instaló todo en un entorno nuevo, separado de `.venv`, usando Python
3.11.9/Windows x64 y el índice oficial PyPI con configuración pip aislada.
El primer destino largo `.local-state/delivery2-python` falló al extraer un
recurso de LiteLLM por el límite de rutas Windows. No se habilitaron políticas
de Windows ni se alteró el paquete. Una instalación nueva en la ruta corta
`.p2/` terminó correctamente; ambos destinos están excluidos de Git.

`constraints-windows-py311-delivery2.txt` registra los 155 paquetes del entorno
completo instalado, incluyendo dependencias de LiteLLM. La instantánea histórica
`constraints-windows-py311.txt` permanece intacta. Un dry-run sin índice contra
los nuevos requisitos y constraints terminó con cero cambios necesarios.
El contrato fija versiones para este entorno Windows/Python, no hashes de
distribuciones ni una garantía de reproducción en Linux u otra versión de Python.

Para reproducir en otro entorno nuevo de ruta corta, sin arrancar el producto:

```powershell
.venv/Scripts/python.exe -m venv .p2
.p2/Scripts/python.exe -m pip install -r requirements.txt -c constraints-windows-py311-delivery2.txt
.p2/Scripts/python.exe -m pip check
.p2/Scripts/python.exe -B scripts/check_environment.py
.p2/Scripts/python.exe -B scripts/check_baseline.py
.p2/Scripts/python.exe -B scripts/check_llm_adapter.py
```

No crear el entorno sobre otro destino con trabajo existente. `.p2` es un
entorno de comprobación; las tareas operativas siguen apuntando a `.venv`.
`check_environment.py` compara metadatos, requisitos incluidos, extras y
constraints sin importar el motor ni consultar red. Detecta paquetes ausentes,
pines diferentes y contratos contradictorios. En `.p2` informa 155 paquetes y
cero diferencias; en `.venv` informa las cuatro diferencias conocidas:

| Paquete | Contrato | `.venv` operativa |
|---|---|---|
| aiohttp | 3.13.5 | 3.13.3 |
| importlib_metadata | 8.7.1 | 8.5.0 |
| jsonschema | 4.26.0 | 4.23.0 |
| openai | 2.32.0 | 2.24.0 |

No se ha cambiado el intérprete operativo ni se ha certificado su igualdad con
el contrato nuevo. La transición debe hacerse en una ventana de operación
identificada, conservando el entorno anterior y probando el retorno. La
reproducibilidad está demostrada en el entorno nuevo; la transición queda
registrada como pendiente, sin ocultar las diferencias.

`check_llm_adapter.py` extrae únicamente clase y factory de `main.py` mediante
AST y construye el adaptador OpenRouter con CrewAI/LiteLLM reales. Bloquea
dotenv y conexiones, usa clave ficticia y mapa de costes local, y verifica
clase, ruta LiteLLM y candidatos. No importa el módulo `main.py`, no llama
`call`/`kickoff` y no contacta proveedores. Es una comprobación opcional del
entorno completo, separada de la suite mínima de Flask.

## Notificaciones acotadas

`EMAIL_SMTP_TIMEOUT_SECONDS` establece la espera de socket SMTP: 10 s por
defecto, intervalo 1–60 s. Valores no numéricos, no finitos o no positivos
vuelven a 10 s; se acotan valores positivos fuera del intervalo. El puerto
SMTP se valida antes de conectar. Se conserva STARTTLS obligatorio para
destinos no loopback, autenticación y compatibilidad con Mailpit local.

Un timeout de socket no cubre por sí solo todas las operaciones acumuladas,
DNS o un interlocutor que entregue datos lentamente. Por ello el coordinador
ejecuta cada destino mediante `config/notification_delivery.py` en un proceso
separado, con `NOTIFICATION_DEADLINE_SECONDS`: 30 s por defecto, intervalo
1–120 s, siempre finito. El límite incluye la espera de DNS y del protocolo
dentro del hijo; la creación/terminación del proceso puede añadir una pequeña
sobrecarga del sistema operativo. Dos destinos se intentan secuencialmente:
el límite de la etapa es la suma de los dos presupuestos, no 30 s para ambos.

El proceso recibe por stdin solamente destino y resumen agregado, sin logs,
IPs, claves ni argumentos secretos en la línea de comandos. Las credenciales
siguen resolviéndose en el backend por entorno/.env. La salida del hijo se
descarta para no propagar datos sensibles de errores de transporte; el
registro persistente sigue exponiendo estado de entrega, no el error crudo.

Si expira el límite, `subprocess.run` termina el hijo y espera su cierre.
La entrega queda `unknown`: el destino podría haber aceptado el aviso antes
de perder la confirmación. No hay reintento automático. El trabajo puede
finalizar correctamente por su análisis, con entrega no confirmada, y admite
trabajos posteriores. La recuperación y deduplicación siguen vigentes.
Las tres entregas históricas `unknown` no se cambian ni se reenvían.

Las funciones de transporte conservan su API booleana. Una invocación directa
de `enviar_email` tiene timeout por socket; el presupuesto total corresponde
al camino coordinado del pipeline. El helper legado de alertas directas no
se utiliza en el coordinador y no obtiene implícitamente un plazo global.

## Verificación del 06/10/2026

| Comprobación | Resultado |
|---|---|
| Instalación completa nueva `.p2` | Aprobada con requisitos y constraints de fase 0 más nuevas dependencias fijadas |
| Contrato final por dry-run sin índice | Aprobado, cero instalaciones/cambios necesarios |
| `pip check` en `.p2` | Sin requisitos incompatibles |
| Comparación final `.p2` | 155 paquetes, cero diferencias |
| Adaptador real offline en `.p2` | Construido con candidatos y ruta LiteLLM conservados |
| Suite en `.p2` y `.venv` | 125 pruebas Python y 3 diagnósticos JavaScript aprobados en cada entorno |
| Sintaxis | 37 archivos, cero errores |
| ESLint completo y TypeScript | Aprobados |
| Regresión React | 6 grupos aprobados |
| Sharp nativo 0.35.5 | Raster sintético de 1×1 creado/leído correctamente |
| Build Next.js | Aprobado en copia aislada con dependencias actualizadas |
| `pnpm audit --prod` | Código 0, cero avisos |
| `pnpm audit` completo | Código 1, un aviso alto: braces de desarrollo |
| `git diff --check` | Sin errores de espacios |

Las pruebas nuevas cubren timeouts en conexión/TLS/login/envío/QUIT, valores
de configuración inválidos, argumentos del hijo y salida descartada, dispatch
con transportes dobles, payload interno inválido, finalización con `unknown`,
ausencia de reenvíos y admisión posterior. También se inició y terminó por
timeout un hijo sintético que únicamente dormía: no importó transportes ni
realizó notificaciones. Los transportes SMTP/Telegram se simularon.

El build utilizó `.local-state/delivery2-frontend` para preservar `.next` del
usuario; la única adaptación fue la raíz Turbopack de la copia para resolver
el enlace a node_modules. No se modificó la configuración Next del producto.
Las consultas de npm/PyPI tuvieron autorización de red. No se ejecutó el
motor, el pipeline real, Docker ni transportes reales, ni se leyeron/mostraron
secretos operativos.

## Compatibilidad, reversión y siguientes trabajos

Se mantienen API, frontend, modelos, prompts, archivos de datos, SQLite,
conmutadores y retorno Flask. El worker debe reiniciarse para cargar el nuevo
código de notificación; no se detuvieron ni reiniciaron procesos del usuario
en esta entrega. No se realizó commit ni publicación.

Para revertir, retirar solo los cambios de entrega 2, manteniendo entrega 1
y cualquier trabajo posterior. Restaurar workspace/lockfile de frontend y
reinstalar con lockfile congelado si se necesita volver a los paquetes
anteriores, que reintroducirían los avisos de producción. Restaurar el envío
directo y quitar el helper reintroduciría el bloqueo de notificaciones.
Los defaults nuevos permiten reversión sin editar `.env`; los históricos y
estados `unknown` no deben tocarse. La `.venv` original se ha conservado.

La siguiente entrega propuesta es el cierre operativo de fase 7: evidencia
de uso, retorno final y política de respaldo de las rutas reales. Continúan
pendientes la corrección publicada de braces, transición del entorno Python,
R-15 de efectos frontend y A-01–A-05. La fase 7 no se cierra automáticamente
por completar esta entrega ni por tiempo de calendario.

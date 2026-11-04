# Primera instalación y arranque

Guía actualizada el 04/11/2026 para iniciar **Web Defense AI V2 y Puerto Umbral
juntos**, desde una terminal. La instalación conserva tus propios logs,
credenciales e informes; el clon no incluye los datos privados del mantenedor.

## Requisitos

- Git.
- Python **3.11** con `venv` y `ensurepip`.
- Node.js **24 o posterior**.
- pnpm **11.19.0**: `npm install --global pnpm@11.19.0`.
- Docker iniciado y Compose disponible para Puerto Umbral. En Windows utiliza
  Docker Desktop con contenedores Linux.

Instala en disco local; en una VM, instala y ejecuta dentro de la VM y usa su
navegador. No copies entornos Python o `node_modules` entre sistemas operativos.
Las herramientas se preparan por separado; el instalador no instala Docker
ni modifica el Python del sistema.

## Instalar una vez

```bash
git clone https://github.com/EnriqueForte/web-defense-ai-v2.git
cd web-defense-ai-v2
python3 webdefensev2.py install
```

En Windows sustituye la última línea por `py webdefensev2.py install`.
El instalador busca Python 3.11, crea o reutiliza `.p2`, instala Python y
frontend con sus contratos y compila Next.js. Crea `.env` si falta y conserva
uno existente. No requiere activar `.p2` manualmente. Detén la sesión propia
antes de instalar o actualizar; no borres datos o bloqueos para forzar el proceso.

## Iniciar habitualmente

```bash
python3 webdefensev2.py
```

En Windows: `py webdefensev2.py`. El mismo comando habilita captura,
seguimiento y ejecutor de análisis manual. No solicita análisis o seguimiento
por el mero arranque. La primera preparación de imágenes del laboratorio
puede tardar; espera a **«Consola lista»**.

| Dirección local | Aplicación |
| --- | --- |
| http://127.0.0.1:3000 | Web Defense AI V2 |
| http://127.0.0.1:4381 | Panel de Puerto Umbral |
| http://127.0.0.1:4380 | Portal vulnerable |
| http://127.0.0.1:4382 | Portal corregido |

Mantén la terminal abierta. **Ctrl+C** solicita detener los servicios propios,
conservando evidencias y volúmenes. Espera a que termine cualquier análisis
antes de cerrar. El lanzador no adopta otra instancia ya abierta; los puertos
ocupados impiden iniciar una segunda sesión.

## Capturar, seguir y analizar desde la interfaz

1. En Puerto Umbral elige escenario, modo y variante; ejecuta desde el panel.
2. En **V2 → Actividad → Fuente de V2** elige el mismo modo: **Corregido** o
   **Vulnerable**. Ambos portales están disponibles y el cambio no exige reiniciar.
3. Pulsa **Capturar log de Puerto Umbral** para una captura o **Iniciar seguimiento**
   para lecturas periódicas. El ejecutor de análisis puede seguir disponible.
4. Configura proveedor, modelo y clave en **Configuración** si quieres usar IA.
5. Pulsa **Iniciar análisis**. V2 detiene el seguimiento propio, espera a su
   parada y solicita el trabajo. Consulta el resultado en **Amenazas** y **Reportes**.

Un trabajo pendiente/activo impide cambiar de fuente o iniciar otra operación
incompatible. Para cambiar la fuente o capturar manualmente, detén antes el
seguimiento. Tras un análisis, el seguimiento permanece detenido: puedes
iniciarlo otra vez desde su botón. No hace falta cerrar V2 para estas acciones.

La fuente inicial es corregida. Cambiar de fuente y capturar no cambia el
informe anterior: un informe nuevo requiere solicitar otro análisis. La
actividad reciente representa una ventana limitada de logs, no todo el historial.
Las peticiones y los hallazgos del informe se muestran por separado.

Capturar o seguir logs no llama al modelo. Solicitar análisis puede enviar
contenido al proveedor y consumir cuota o saldo. Cada instalación gestiona
sus propias credenciales. Las notificaciones siguen desactivadas en el perfil
conjunto. Consulta [Configuración LLM](CONFIGURACION_PROVEEDOR_LLM.md).

## Opciones avanzadas y ayuda

| Necesidad | Comando en Linux/Parrot; en Windows sustituir `python3` por `py` |
| --- | --- |
| Comprobar requisitos sin iniciar | `python3 webdefensev2.py check` |
| Abrir sin ejecutor de análisis | `python3 webdefensev2.py --read-only` |
| Elegir fuente inicial vulnerable | `python3 webdefensev2.py --lab-mode vulnerable` |
| Consultar opciones | `python3 webdefensev2.py --help` |
| Iniciar solo V2 sin laboratorio | `python3 webdefense.py start --mode structured` |

`--enable-manual` se conserva por compatibilidad; el arranque conjunto ya lo
habilita por defecto. La entrada anterior `webdefense.py` mantiene sus opciones
y perfiles separados; no copies sus recetas avanzadas encima de una sesión
conjunta abierta. La instalación y el uso de logs propios se detallan en
[Instalación autoalojada](INSTALACION_AUTOALOJADA.md).

Si el arranque falla, conserva el mensaje y consulta los logs en
`.local-state/launcher/<sesión>/`. No reinstales ni elimines evidencias como
primer paso. Las suites Python/SDK/UI son verificaciones de desarrollo,
no parte de cada arranque del usuario.

## Alcance y conservación

La entrega `7ecfcf1` tiene actualización/build y recorrido manual unificado
observados en Parrot: selector, captura, seguimiento, análisis y publicación.
El [acta del 04/11](PUERTO_UMBRAL_RECORRIDO_MANUAL_2026_11_04.md) delimita esa
recepción y las trece regresiones preparadas sin ejecutar. No es certificación
de todas las plataformas ni evaluación general de detección.

Consulta el [manual local](PUERTO_UMBRAL_OPERACION_LOCAL.md) para operación,
el [registro de decisiones](CIERRE_V2_PUERTO_UMBRAL_2026_11_03.md) para alcance,
y [Operación y recuperación](OPERACION_RECUPERACION_2026_10_14.md) para respaldos.
Cada copia tiene selección y fecha propias; no incluye automáticamente toda
la VM, las bases de laboratorios o credenciales.

## Validación histórica de V2 anterior a Puerto Umbral

Estado revisado el 21/10/2026: [resumen vigente](ESTADO_FINAL_2026_10_12.md).
El código de entrega `0d73ec2` pasó instalación, regresión, E2E y smoke API/proxy
en [CI Windows/Ubuntu 39466610699](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/39466610699).
La muestra guiada posterior a la instalación en Parrot sí acreditó captura
DVWA, análisis XSS/fuerza bruta y lectura del informe el 15/10. La actualización
posterior a `v0.1.0`, los pines Docker, la recuperación aislada y la lectura/cierre
se acreditaron el 21/10 en [V1](ACTUALIZACION_PARROT_V1_2026_10_20.md), conservando
el informe anterior sin otro análisis LLM.
La aceptación de A-05 para la primera versión local se confirmó el 20/10 con
límites explícitos y comparación legacy diferida, según la
[matriz A-05](MATRIZ_ACEPTACION_A05_2026_10_20.md). Los párrafos siguientes
conservan la historia de validación del lanzador.

El nuevo instalador y lanzador se ensayaron en una copia aislada de Windows,
incluido build, API directa/proxy y cierre con puertos libres. Después pasó el
mismo recorrido desde una instalación nueva en [Windows y Ubuntu CI](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38234970879),
para el commit `c82441c`, ya publicado. Después, el usuario confirmó instalación,
arranque unificado y navegación en [Parrot](VALIDACION_PARROT_2026_10_12.md).
El cierre dejó los puertos libres tras una espera; el comprobador indicó ocupado
antes de ella. El [ajuste posterior de puertos](CORRECCION_PUERTOS_2026_10_12.md)
del commit `2a73ff0` pasó después en [Windows y Ubuntu CI](https://github.com/EnriqueForte/web-defense-ai-v2/actions/runs/38237671713),
incluida la regresión de conexiones residuales y reinicio inmediato en Linux.
El usuario confirmó después el recorrido guiado en Parrot: comprobación preparada,
arranque listo, cierre por Ctrl+C y nueva comprobación preparada sin aviso de puerto.
El registro Parrot conserva los límites de las capturas y de la confirmación.

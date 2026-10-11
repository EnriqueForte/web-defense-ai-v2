# Instalación y arranque Windows/Linux — 07/10/2026

Objetivo solicitado: distribuir código que pueda ejecutarse en instalaciones
propias de Windows y Linux. Base objetivo Python 3.11, Node 24, pnpm 11.19.0;
Linux: Parrot OS x86_64 en VMware como caso prioritario del usuario y Ubuntu
24.04 x86_64 como entorno inicial de CI. No se declara cobertura de ARM, macOS ni de
todas las distribuciones Linux.

## Implementación

- Instalador Python común `scripts/setup_installation.py`: plan por defecto;
  `--install` crea/reutiliza .p2, instala contrato y ejecuta pip check/verificación.
  `--frontend` incorpora instalación con lockfile. Selecciona Scripts/python.exe
  en Windows y bin/python en Linux. No borra entornos y rechaza los inválidos o
  construidos con otra versión de Python. `--init-env` conserva cualquier .env
  existente sin leerlo; una configuración nueva copia solo la plantilla.
- Contrato `constraints-py311.txt` compartido, derivado sin cambios de versiones
  de la instantánea Windows entrega 2, que se conserva. Marcadores pywin32
  excluidos en Linux; aún no hay freeze Linux acreditado. No se trasladan los
  entornos o node_modules entre sistemas.
- Preflight y comprobación de entorno usan el contrato compartido. El lanzador
  admite `--enable-manual` explícito; por defecto lectura, manual apagado,
  notificaciones vacías y worker sin ciclos periódicos. La opción no encola jobs.
  La guía explica un mismo perfil/modo para Flask y worker, fuente ausente al
  inicio, captura Compose, arranque Next build/start y parada mediante Ctrl+C.
- Verificación HTTP efímera con fixtures y puerto libre: entrega de Flask,
  informe, CSP y recursos vendor/hash; elimina solo el proceso creado por ella.
- Matriz GitHub Actions Windows/Ubuntu: instalación, pip check, metadatos,
  baseline, HTTP, SDK offline y frontend lint/tipos/UI/build. Permisos de lectura,
  checkout sin credencial persistida, sin secretos de proveedor ni Docker.
  Configuración basada en documentación oficial de
  [checkout v5](https://github.com/actions/checkout/blob/v5/README.md),
  [setup-python v6](https://github.com/actions/setup-python/blob/v6/README.md) y
  [setup-node v6](https://github.com/actions/setup-node/blob/v6/README.md).

## Evidencia y límites

254 pruebas Python aprobadas en .p2 y .venv, tres comprobaciones JS. Se prueban
selección de rutas Windows/Linux, no mutación del plan, preservación de .env,
rechazo de entorno inválido/versiones distintas y admisión manual explícita.
155 pines, cero diferencias en .p2; sintaxis y diff comprobados.
HTTP real sintético en Windows aprobado, con servidor temporal detenido.

La selección Linux y sus marcadores se comprobaron mediante dobles; esto no es
ejecución Linux. WSL solo presenta docker-desktop, sin una distribución Ubuntu
de pruebas. No se accedió a su entorno interno ni se instaló Linux. El workflow
está preparado, no publicado ni ejecutado: compatibilidad real e instalación
limpia final de Linux siguen pendientes, igual que un freeze de sus dependencias
adicionales si el resolutor las incorpora. No confundir Windows .p2 existente
con una nueva instalación desde clonación del contenido final.

No se ejecutó el instalador con --install en el entorno del mantenedor, ni se
tocaron .env, servicios operativos, jobs, proveedor, Docker o notificaciones.
No hay nuevo commit/push en este bloque. Dependencias/motor API/UI se conservan.
Se puede revertir el lanzador y los defaults de contrato sin restaurar datos;
las instantáneas Windows originales permanecen disponibles.

## Pendientes

Ejecutar la matriz real tras revisar/publicar el contenido, corregir cualquier
incompatibilidad Linux con evidencia, ensayar instalación limpia final y cargar
el diagnóstico del worker mediante la operación documentada. Auditorías de
dependencias/historial, conservación de datos y aceptación A-05/entrega final
siguen abiertas. No dar el proyecto por finalizado solo por añadir el workflow.

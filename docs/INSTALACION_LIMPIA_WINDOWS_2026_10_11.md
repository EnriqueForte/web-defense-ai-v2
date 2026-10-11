# Instalación limpia Windows — 11/10/2026

La copia limpia del estado actual pasa la instalación y las comprobaciones
offline en Windows. El usuario pidió continuar con el siguiente pendiente
independiente y corregir después el fallo manual de A-05. Esta prueba no acredita
Linux/Parrot ni un análisis real exitoso.

## Candidato y aislamiento

Se exportaron **197 archivos** del árbol de trabajo, incluidos archivos nuevos
no ignorados, a `.i1/`, excluida de Git. Cada archivo conserva el hash de la
fuente. No se copió `.git`, `.env`, entornos Python, `node_modules`, `.next`,
estado local, respaldos o datos del piloto. Se incluyó únicamente `.env.example`.
Es una **copia limpia local**, no una clonación remota ni una ejecución GitHub
Actions. La documentación de este ensayo se añade después del snapshot probado.

Se crearon `.i1/.p2` y `.i1/frontend/node_modules` desde los contratos fijados.
Las cachés de paquetes del equipo pueden reutilizar descargas; no se enlazó el
`node_modules` operativo ni se copió un entorno Python existente. La ruta corta
evita alargar los recursos de dependencias Windows.

Herramientas utilizadas: Python **3.11.9**, Node **24.21.0**, pnpm **11.19.0**
instalado solo en `.local-state/clean-install-20261011/tools`. El pnpm general
de esta sesión era 11.25.0 y no se sustituyó globalmente. `py -3.11` no encontró
el runtime en esta sesión; se utilizó directamente el ejecutable Python 3.11
que corresponde al proyecto.

## Resultado

| Comprobación | Resultado |
|---|---|
| Instalador Python `--install --init-env` | Entorno nuevo creado, bootstrap pip/setuptools fijado, instalación completada |
| Contrato y dependencias | 158 pines, cero diferencias; `pip check` sin conflictos |
| Frontend limpio | pnpm 11.19.0, instalación con `--frozen-lockfile` completada |
| Instalador completo repetido `--install --frontend --init-env` | Completado; `existing_preserved`, frontend actualizado sin cambios |
| Sintaxis | 71 archivos, cero errores |
| Baseline | 268 Python y tres comprobaciones JavaScript aprobadas |
| CrewAI/LiteLLM offline | 21 escenarios aprobados con conexiones a proveedor bloqueadas |
| Adaptadores OpenRouter | Legacy/structured y límites 8192/60 verificados sin llamadas |
| Frontend | Lint, TypeScript sin emisión y 14 grupos UI aprobados |
| Build Next 16.3.8 | Turbopack aprobado con configuración original; rutas `/` y `/_not-found` |
| HTTP Flask sintético | CSP, informe y recursos vendor/hash aprobados |
| Producción y proxy | Raíz Next, nueve recursos estáticos y siete rutas API directa/proxy HTTP 200 |
| Retorno Flask | Informe sintético HTTP 200 con marked local |

La integración utilizó puertos efímeros **65056/65057**, fuentes exclusivamente
sintéticas, manual apagado y destinos vacíos. El build de esa comprobación
recibe `WEB_DEFENSE_API_PORT` para apuntar al servidor sintético; no modifica
`next.config.ts`. Los procesos de prueba se detuvieron al finalizar.
No se verificaron hidratación en navegador, pulsación del botón, Docker,
proveedor real o envíos en este ensayo.

Los intentos restringidos fallaron por acceso a registros, enlaces pnpm,
reemplazos atómicos temporales y sockets. La baseline y HTTP pasaron al repetir
fuera del sandbox con permiso. El ensayo SDK restringido no terminó; se detuvo
su cadena propia tras verificar identidad y la repetición offline pasó.
El primer build falló en el proceso PostCSS/Turbopack y también falló la
repetición con esa caché; se apartó la caché generada sin borrarla. El build
con caché nueva y la comprobación posterior mediante pnpm pasaron. No se cambió
el producto para encubrir esos resultados ni se atribuye una causa única
demostrada al fallo de build.

## Preservación y pendientes

Los 197 archivos del snapshot mantuvieron sus hashes tanto en la copia como
en las fuentes durante las pruebas. Logs/jobs del piloto se compararon con la
lectura de la incidencia previa: 28 trabajos (17 succeeded/11 failed), entregas
11 sent/3 unknown, hash de log y puntero actual iguales. La configuración pública
creada por el instalador coincide textualmente con `.env.example`, considerando
los finales de línea Windows. No se leyó ni modificó el `.env` operativo.

WSL solo dispone de `docker-desktop`: no se utiliza como sustituto de Ubuntu o
Parrot. La validación Linux y Parrot/VMware requiere un entorno real disponible;
se solicitó al usuario versión, arquitectura y disponibilidad de su VM. Tampoco
se acredita clonación desde GitHub, ejecución de la matriz CI o publicación.

La instalación limpia **Windows local** queda comprobada para este candidato.
El paso de distribución completo permanece abierto por Linux/Parrot y clonación
remota/CI. A-05 conserva la incidencia de clasificación y el primer fallo de
ingesta documentados; no se declaran resueltos por las pruebas de instalación.
Los avisos residuales y el escaneo de imágenes siguen en su registro independiente.

Recibos excluidos de Git: `.local-state/clean-install-20261011/`, incluidos
`candidate.json`, `candidate-verification.json`, logs de instalación/pruebas/build
y `production-verification.json`. La copia `.i1/` se conserva para revisión;
no se publica ni se convierte en entorno operativo. Sin análisis reales,
Docker, envíos, reinicios operativos, commit o push.

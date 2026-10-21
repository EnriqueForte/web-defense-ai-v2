# web-defense-ai V2 — Repositorios y recuperación

## Distribución vigente

El 21/10/2026 el usuario decidió distribuir V2 como **repositorio público en
GitHub**, bajo la licencia MIT existente, para clonación e instalación propias.
El destino se mantiene en [EnriqueForte/web-defense-ai-v2](https://github.com/EnriqueForte/web-defense-ai-v2).
El código está publicado en `main` y el cambio se ha aplicado: GitHub devuelve
`visibility=public` y `private=false`. Se ha comprobado el acceso a los metadatos
del repositorio sin autenticación. Véase [Distribución pública](DISTRIBUCION_PUBLICA.md)
para el alcance y las comprobaciones del cambio.

La publicación del código conserva el alcance de ejecución local de la
aplicación. No incluye credenciales, datos operativos ignorados, copias locales
ni acceso a la VM del mantenedor. El historial Git y la actividad de Actions
también quedan accesibles al abrir el acceso. Se conservan los resultados y
límites de la revisión previa, incluida la confirmación del propietario sobre
la muestra CSRF histórica.

## Separación de versiones

El proyecto original permanece en `https://github.com/EnriqueForte/web-defense-ai`.
No se ha renombrado, eliminado ni actualizado desde este trabajo. V2 utiliza
un repositorio independiente: `EnriqueForte/web-defense-ai-v2`.

Inicialmente se creó privado en GitHub, sin inicializar otro README o historial.
Esa separación inicial se conserva como historia; la decisión posterior del
21/10 es abrir el acceso al repositorio V2. Se publica la rama local `main`
conservando la base histórica y los cambios propios de V2.

| Elemento | Valor |
|---|---|
| Carpeta de trabajo | `F:\Proyectos ChatGpt\web-defense-ai V2` |
| Rama local | `main` |
| Remoto principal de V2 | `origin`: `https://github.com/EnriqueForte/web-defense-ai-v2.git` |
| Referencia al original | `original-readonly`: `https://github.com/EnriqueForte/web-defense-ai.git` |
| Destino push del original | `DISABLED-original-repository` |
| Push predeterminado | `origin` |
| Seguimiento de rama | `main` → `origin/main` |

El bloqueo del original es local: impide enviar mediante el nombre de ese
remoto. No cambia permisos de GitHub ni evita que alguien cambie la
configuración o utilice explícitamente la URL original. No hacerlo desde V2.

## Historia conservada

La base local de V2 era `f4262ef9fa060f6d9b5399bdfaed860eaf441489`.
Al revisar GitHub, la rama principal original estaba en
`91651ba4154f0222c332e576a4dd83ccbca0ded8`. La diferencia es el commit
`Add MIT License to the project`.

Se conserva el historial de la base local para V2 y se ha copiado su licencia
desde la referencia original actualizada. No se ha hecho una fusión automática
ni reescrito la historia original. Los cambios de V2 se guardan en un commit
propio y se publica únicamente su rama `main`, sin enviar referencias internas
de herramientas o todas las ramas indiscriminadamente.

## Copias locales verificadas

Directorio: `.local-backups/repository-separation-20260926-203121/`.

- `before-separation.bundle`: historia y referencias locales anteriores.
- `original-remote.bundle`: historia completa de la rama original observada.
- `working-tree.zip`: 43 archivos de trabajo versionados o pendientes de añadir,
  capturados antes de separar los remotos.
- `git-config-before.txt`: configuración Git anterior.
- `status-before.txt` y `metadata.json`: estado y referencias observadas.

Los bundles pasaron la verificación de Git y el ZIP pasó la comprobación de
integridad. El ZIP no incluye secretos, entorno virtual o datos operativos
ignorados: esos archivos permanecen intactos en su ubicación actual. Estas
copias no sustituyen una copia externa de todo el disco.

Para recuperar la historia, clonar el bundle deseado en una carpeta nueva.
Extraer el ZIP también en otra carpeta si se necesita recuperar los cambios
locales anteriores. Comparar antes de restaurar; no sobrescribir el trabajo
actual ni copiar sin revisar la configuración antigua, que apuntaba al original.

## Uso en VSCode

Abrir `web-defense-ai V2.code-workspace`. Control de código fuente consulta
la carpeta `.git` de esta raíz. Mantener el original en otra carpeta si se
quieren abrir ambas versiones simultáneamente.

La rama `main` sigue a `origin/main`. Si VSCode
conserva una vista anterior, actualizar Control de código fuente o recargar la
ventana. El enlace al repositorio original en el README es una atribución y no
determina el destino de Git.

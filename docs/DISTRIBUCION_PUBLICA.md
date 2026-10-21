# Distribución pública en GitHub

Revisión: **21/10/2026**.

## Estado del cambio

**[EnriqueForte/web-defense-ai-v2](https://github.com/EnriqueForte/web-defense-ai-v2)
es público desde el 21/10/2026**, por decisión expresa de su propietario.
El cambio se aplicó con permisos de administración y GitHub confirmó
`visibility=public` y `private=false`. Una consulta posterior a la API sin
cabecera de autorización verificó el acceso público al repositorio.

El [repositorio original](https://github.com/EnriqueForte/web-defense-ai)
permanece independiente. Esta operación no modifica la etiqueta `v0.1.0`, crea
otra release ni cambia el código de la aplicación.

## Qué se distribuye

El código fuente, las guías, las pruebas y las capturas versionadas se ofrecen
bajo [licencia MIT](../LICENSE). Cada usuario instala sus dependencias y aporta
sus credenciales, registros e informes. La consulta y clonación por HTTPS no
requieren autenticación; enviar cambios
al repositorio seguirá requiriendo permisos.

Los archivos `.env`, logs e informes operativos, bases locales, backups,
entornos y recibos ignorados no forman parte del paquete versionado. La
plantilla `.env.example` y los fixtures de pruebas sí se distribuyen.
Antes de adjuntar una incidencia, elimina claves, cookies, tokens y datos
personales del ejemplo que vayas a compartir.

La consola sigue ejecutándose en localhost y el laboratorio DVWA debe
permanecer aislado. La distribución pública del código no amplía el soporte a
un servicio accesible por Internet ni modifica los límites de evaluación,
privacidad y seguridad documentados en el [README](../README.md).

## Revisión antes de abrir el acceso

La apertura alcanza el historial Git y también el historial y los logs de
Actions, según la [documentación de GitHub](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility).
Las actas de validación de esta entrega utilizan pruebas sintéticas en CI;
su aceptación de uso local no sustituye la revisión del contenido distribuido.

La [revisión previa de secretos](REVISION_DEPENDENCIAS_SECRETOS_2026_10_18.md)
identificó hashes públicos de recursos de tokenización y una muestra opaca de
token CSRF en el historial de `tests/test_groq_cache_transport.py`, commit
`33d987b`. El fixture actual usa ceros; el valor anterior permanece recuperable
desde Git. El riesgo R7 está conservado en el [tratamiento C3](TRATAMIENTO_RIESGOS_C3_2026_10_20.md).

El 21/10 el propietario confirmó expresamente que la muestra pertenecía
exclusivamente a su DVWA local y que aquella sesión ya estaba invalidada.
Esta confirmación resuelve la consulta previa a la apertura; no equivale a una
verificación técnica de la sesión por el agente. Se conserva el hallazgo y la
incertidumbre documentada en las actas anteriores, sin transcribir aquí su valor,
probarlo contra servicios ni reescribir la historia.

El escaneo de preparación del 21/10 sobre `e6e7e0c` abarcó 84 commits
alcanzables y 286 archivos del candidato documental. Conservó cuatro
coincidencias actuales de hashes públicos y cinco históricas (cuatro hashes
y la muestra CSRF conocida). No aparecieron hallazgos nuevos. Se utilizó
Gitleaks 8.30.1 con reglas estándar, resultados redactados y control positivo
sintético, sin exclusiones propias para ocultar hallazgos.

Los escaneos por patrones tienen un alcance limitado: un informe sin hallazgos
nuevos no garantiza ausencia total de secretos. Las vulnerabilidades residuales
de dependencias e imágenes continúan documentadas, con sus fechas y límites.

## Conservación de las actas

Las referencias a «repositorio privado» en actas fechadas anteriores describen
su estado en aquella revisión. Se conservan como evidencia histórica; el estado
vigente de distribución se consulta en este documento y en [Repositorios](REPOSITORIOS.md).

Cualquier reescritura futura del historial, eliminación de referencias o cambio
de versión necesitará su propio alcance; no forma parte de esta actualización
documental.

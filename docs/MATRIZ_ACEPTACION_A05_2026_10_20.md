# Matriz de aceptación A-05 — 20/10/2026

Estado: **C2 aceptado para la primera versión local acotada**, por respuesta
expresa del usuario el 20/10/2026. Reúne la evidencia y los límites de cierre del
[análisis](ANALISIS_CIERRE_2026_10_20.md). No declara calidad general del modelo,
modifica su política o autoriza nuevas llamadas.

Continuación del 20/10: [revisión técnica terminada](REVISION_ACEPTACION_A05_2026_10_20.md)
sobre doce recibos y once publicaciones guardadas, con 56 archivos preservados.
D1 dispone de una conclusión técnica y D2/D3 de límites explícitos. El usuario
aceptó D4 con comparación legacy diferida; véase la decisión completa en el acta.
No hubo otro ensayo. C3 seguridad, C4 entrega y V1 VM siguen separados.

## Alcance y forma de leer los estados

Objetivo de cierre propuesto: aplicación local de apoyo a la revisión de logs,
con indicadores trazables y límites de selección explícitos. No se propone
certificar explotación, autenticación exitosa, ausencia de ataques desconocidos
o remediación automática a partir de un access.log.

- **Técnico verificado**: implementación/guardas/evaluador probados; las
  respuestas sintéticas no acreditan comportamiento semántico del proveedor.
- **Muestra real revisada**: ensayo histórico con entrada y alcance identificados.
  No se traslada automáticamente a otra versión, modelo, instalación o conjunto.
- **Pendiente de decisión**: falta revisión acotada, evidencia o acuerdo sobre
  una limitación de la versión. No significa que deba ejecutarse otro ensayo.

La preparación inicial usó actas y código de fixtures/contratos de `ca2f6af`.
La continuación lee publicaciones sintéticas E1/E2 guardadas y vuelve a verificar
sus contratos/métricas, sin leer informes operativos o repetir llamadas. La
revisión posterior no transforma sus resultados en aceptación semántica general.

## Evidencia base

| Ref. | Evidencia | Qué permite afirmar |
| --- | --- | --- |
| E1 | [Lote real 07/10](EVALUACION_AMPLIADA_A05_2026_10_07.md) | Siete casos adicionales cumplieron expectativas de familias con la revisión de entonces. Se conserva el problema de narrativa normal y su corrección posterior; latencia normal de 475,829 s, sin p95 general. |
| E2 | [Ensayos reales 14/10](ENSAYO_REAL_A05_2026_10_14.md) | `mixed` y `normal` revisados con soporte de referencias; `same_family` inicial fallido y nuevo ensayo autorizado posterior revisado. Resultado, límites, guardas, hashes y discrepancias de uso registrados. |
| E3 | [Muestra guiada Parrot 15/10](INCIDENCIA_GROQ_413_2026_10_15.md) y [preparación DVWA](CORRECCION_DVWA_POST_RESUMEN_2026_10_15.md) | Informe y Resumen coherentes: XSS línea 31 y fuerza bruta líneas 39–46; ocho POST en 45 s, dos grupos en total. Aceptación por capturas/confirmación; sin bytes completos/hash/usage de la VM. |
| E4 | [Contexto offline 19/10](EVALUACION_CONTEXTO_A05_2026_10_19.md) | Nueve entradas nuevas de contexto: límites de ventana, separación IP, visitas GET, zona horaria y cabeceras. No son ensayos LLM. |
| E5 | [Grupos offline 19/10 y cierre CI20/10](EVALUACION_GRUPOS_A05_2026_10_19.md) | 24 casos/ocho controles; 25 publicaciones sintéticas/101 archivos por OS, bytes y métricas verificados en CI39239742802. Incluye salidas divididas/solapadas deliberadamente disconformes. |

Los informes del proveedor de E1/E2 están aislados y no sustituyen el reporte
operativo. E3 tiene un tipo de evidencia distinto. No se rellenan sus datos
ausentes con bytes o métricas de E5.

## Matriz finita de cierre

Los criterios de esta tabla delimitan el alcance aceptado, sin convertir
limitaciones en comprobaciones realizadas ni ordenar doce pruebas nuevas.
«Sin omisiones» se refiere a etiquetas visibles de la
entrada seleccionada, no a ataques que el registro no permita observar.

| ID | Criterio de alcance | Evidencia y estado actual | Resolución en esta entrega |
| --- | --- | --- | --- |
| AC01 | En la muestra mixta, cubrir SQLi/XSS/traversal/comandos y ráfaga de login con referencias correctas; no atribuir hallazgo a la solicitud normal | E2: cinco familias/nueve pares esperados, líneas 1–9; normal 10 sin hallazgo. Muestra revisada. E5 verifica el evaluador | Aceptado para la muestra, sin promesa de cobertura en todos los logs/modelos |
| AC02 | En la muestra normal, no inventar hallazgos y explicar el alcance sin declarar seguridad global | E2: cuatro solicitudes, cero hallazgos y narrativa local revisados. E1 conserva el fallo narrativo anterior | Aceptado con distinción explícita entre cero hallazgos y ausencia demostrada de ataques |
| AC03 | Para XSS + ocho POST DVWA, mostrar evidencia de ambos y no perder referencias de la ráfaga | E3: XSS 31 y POST 39–46, 45 s; dos grupos, alta/media, aceptados para esa muestra | Aceptación guiada conservada; no se repite el ensayo ni se infiere éxito de login |
| AC04 | Mantener todos los pares de evidencia sin inflar o fusionar grupos de forma injustificada | E2 `same_family`: dos grupos SQLi aceptados, uno por evento. E5 detecta división/solapamiento/duplicados y unión de ráfagas de distinta IP en fixtures | Agrupación por evento aceptada en E2; la partición exacta sintética no es una definición universal |
| AC05 | No inferir el contenido de POST ausentes ni fabricar IP/fecha de una entrada incompleta | E1: `missing_body` e `incomplete` cumplieron familias; E5 mantiene verificación sintética | Evidencia histórica y limitación aceptadas para esta entrega; no equivale a otro ensayo del proveedor actual |
| AC06 | Atribuir indicadores al destino de la solicitud; manejar codificación sin sumar indicadores de Referer/User-Agent como solicitudes distintas | E1 `encoded` revisado por familias; E4/E5 cubren cabeceras solo con respuestas sintéticas | Límite aceptado: la resistencia del LLM a instrucciones en cabeceras no está demostrada ni se garantiza |
| AC07 | Distinguir ráfaga, actividad espaciada, ventanas 60/61 s y origen IP; visitas GET/avatar no demuestran envíos ni éxito | E1 cubre `login_window/login_spread/timezone_split`; E3 cubre la ráfaga real guiada. E4/E5 verifican los límites y separación IP offline | Alcance aceptado distinguiendo prueba de proveedor y de código; no se afirma cobertura general de ventanas |
| AC08 | Mostrar selección/omisiones explícitas y no convertir cobertura parcial en cobertura total | E5 liga digest/texto/refs y distingue selección proyectada de entrada completa | Limitación aceptada: no se garantiza descubrir actividad fuera de la selección |
| AC09 | Mantener severidad/estado y motivos apoyados en evidencia; recomendaciones sin hechos inventados ni ejecución automática | E2: `mixed` requiere investigación y `same_family` usa indicador observado, dentro de techos; narrativa revisada en esas muestras. E3: ambos requieren investigación | Aceptación acotada a esas muestras; contrato/techo no certifican verdad semántica universal |
| AC10 | Salida inválida sin publicación ni avisos; informe/API/conteos coherentes y publicación anterior conservada | Guardas, rechazos y conservación verificados técnicamente en E5; publicaciones reales revisadas en E2 y lectura guiada en E3 | Técnico verificado en ese alcance; no hay motivo documentado para repetirlo por cambiar estas guías |
| AC11 | Informar versión/modelo/selección, duración y tokens disponibles; conservar incertidumbre, errores y discrepancias | E1/E2 registran duración/uso y variación del router; E3 carece de usage completo. E5 es offline | Alcance aceptado sin SLA, p95 o coste facturado garantizados; se conservan discrepancias |
| AC12 | Una afirmación de mejora frente a legacy debe basarse en comparación controlada de la misma entrada y condiciones | Hay retorno/configuración probados; las actas examinadas no sustentan superioridad general en calidad/coste/latencia | Comparación expresamente diferida por el usuario; no se marca cumplida ni se afirma superioridad |

## Decisiones resueltas para el alcance local

| Decisión | Evidencia y alcance | Resolución aceptada |
| --- | --- | --- |
| D1 — Clasificación y narrativa | Revisión técnica completada sobre E1/E2; tres narrativas/Markdown E2 iguales a la política actual, sin nuevo defecto reproducido. E1 conserva sus límites históricos | Alcance de muestras aceptado; sin repetición de ensayos |
| D2 — Contexto y cobertura | Diferencia entre código, simulación y proveedor documentada; selección parcial y resistencia LLM sin aceptación real adicional | Límites explícitos aceptados para la primera entrega; no se garantiza cobertura fuera de muestras/selección |
| D3 — Medición y comparación | Datos históricos por caso, sin benchmark controlado | Comparación y afirmación de superioridad expresamente diferidas, sin declararlas realizadas |
| D4 — Aceptación final C2 | Usuario eligió «Aceptar alcance local acotado (recomendado)» el 20/10 | C2 cerrado en ese alcance; C3/C4/V1 separados y sin autorizar nuevas llamadas |

El responsable de preparar evidencia y corregir defectos es el desarrollo en
este repositorio. La aceptación de límites procede de la respuesta expresa del
usuario, registrada en el acta enlazada; no se infirió del silencio o de un test.

## Si se amplía el alcance con evidencia nueva

No es un requisito pendiente de esta entrega acotada. Para una ampliación,
antes de pedir autorización se preparará un protocolo concreto con:

1. Fila y pregunta a resolver; entrada sintética identificada y etiquetas
   independientes del detector. Indicar selección, agrupaciones aceptables y
   condiciones de rechazo antes de ver la respuesta.
2. Código/prompt/esquema y proveedor/modelo o router elegido. Si varía el modelo,
   no atribuir diferencias únicamente a un cambio de código.
3. Presupuesto total de intentos y tiempo, criterio de parada y destino aislado.
   No activar worker, ciclos, Docker o notificaciones como consecuencia de
   ejecutar un evaluador sintético.
4. Revisión de referencias, omisiones/sobrantes, clasificación, narrativa,
   publicación, duración/usage y errores. Separar ejecución correcta de conformidad
   de fixture y de aceptación humana; conservar también los fallos.

Se solicitará autorización nueva para ese protocolo. Los ensayos anteriores
están consumidos y sus saldos no se reutilizan. No se copian fixtures a reports,
ni se reescriben informes operativos ni se repiten llamadas para completar actas.

## Condición documental y condición de producto

Este documento registra fuentes y cuatro decisiones resueltas para cerrar C2
en el alcance local aceptado. No cambia `quality=semantic_evaluation_pending`,
porque no se certifica calidad general del proveedor, ni convierte
`fixture_expectations_met` o `status=succeeded` en aprobación semántica universal.
Las limitaciones aceptadas siguen siendo limitaciones; no se marcan como
pruebas realizadas o como conformidad de todos los modelos/entradas.

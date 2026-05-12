# Ejemplo de Reporte: Optimización de Costos en GCP

Este documento muestra cómo la habilidad `finops-specialist` debe procesar y presentar un análisis de costos.

## Resumen Ejecutivo

Tras analizar el consumo del trimestre Q1 en el proyecto `prod-data-pipeline`, se identificó un potencial de ahorro del **22% ($1,450 USD/mes)** mediante estrategias de Rightsizing y Lifecycle Management.

## Hallazgos por Dimensión

### Compute Engine (GCE)

- **Instancia**: `worker-node-alt-01` (n1-standard-16).
- **Observación**: Utilización promedio de CPU inferior al 15% y memoria al 20% durante 30 días.
- **Acción**: Migrar a familia `e2-standard-4`.
- **Ahorro Estimado**: $420 USD/mes.

### Cloud Storage (GCS)

- **Bucket**: `raw-logs-archive`.
- **Observación**: 15TB de datos en clase "Standard" sin acceso en los últimos 90 días.
- **Acción**: Aplicar Lifecycle Policy para mover a clase "Archive".
- **Ahorro Estimado**: $850 USD/mes.

## Plan de Acción (Quick Wins)

| Prioridad | Tarea | Impacto | Esfuerzo |
| :--- | :--- | :--- | :--- |
| **Alta** | Mover logs antiguos a clase Archive. | $$$ | Bajo |
| **Media** | Implementar Commitment de 1 año para base de datos SQL. | $$ | Medio |
| **Baja** | Cambiar n1 por e2 en nodos de desarrollo. | $ | Bajo |

---

## Nota Final de Reporte

Este análisis fue generado por el Especialista FinOps (GCP).
Se recomienda implementar etiquetas de `environment:prod` y `owner:team-data` para mejorar la visibilidad.

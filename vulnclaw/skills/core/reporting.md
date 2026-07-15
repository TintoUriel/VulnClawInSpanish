---
name: reporting
description: Flujo de generación de informes — genera informes de pentesting y PoC estructurados
routing:
  phases: [reporting]
  task_types: [report]
---

# Skill de Generación de Informes

Organiza los resultados del pentesting en un informe estructurado, incluyendo hallazgos detallados, scripts PoC y recomendaciones de remediación.

## Estructura del informe

### 1. Resumen del proyecto
- Objetivo de la prueba
- Fecha de la prueba
- Alcance de la prueba
- Metodología de la prueba

### 2. Resumen ejecutivo
- Visión general de los hallazgos de alto riesgo
- Distribución de niveles de riesgo
- Recomendaciones clave

### 3. Hallazgos detallados
Para cada vulnerabilidad:
- Nombre de la vulnerabilidad y nivel de gravedad
- Tipo de vulnerabilidad
- Alcance del impacto
- Pasos de verificación
- Evidencia clave (solicitud/respuesta/capturas de pantalla)
- Script PoC
- Recomendaciones de remediación

### 4. Ruta de ataque
- Diagrama completo de la cadena de ataque
- Ruta desde el acceso inicial hasta el objetivo final

### 5. Anexos
- Scripts PoC
- Capturas de tráfico
- Evidencia fotográfica

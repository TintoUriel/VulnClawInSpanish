---
name: ai-mcp-security
description: Evaluación de seguridad de IA y MCP — Inyección de Prompt, abuso de herramientas, límites de confianza de MCP, escalada de privilegios de Agent, fuga de datos, riesgo de modelo, matriz de riesgos GAARM
routing:
  target_types: [ai_agent, mcp]
  task_types: [pentest, audit]
  technologies: [llm, rag, memory, plugin]
  vulnerability_classes: [prompt_injection, tool_abuse, info_disclosure]
---

# Skill de Evaluación de Seguridad de IA y MCP

Usa este Skill cuando el objetivo incluya LLM, Agent, herramientas MCP, Skills, RAG, Memory, Plugin o componentes de servicio de modelo.

**Prerrequisito**: si la superficie de IA es solo una capa de presentación y el verdadero bloqueo sigue siendo la firma del cliente o el protocolo de cifrado, vuelve primero al Skill `client-reverse`.

## Enrutamiento de escenarios

| Tipo de riesgo | Referencia preferida |
|---------|---------|
| Inyección de Prompt / inyección indirecta / interferencia de CoT | `references/ai-app-security.md` |
| Abuso de herramientas / envenenamiento de MCP / cadena de suministro de Skills | `references/04-ai-and-mcp-security-integrated.md` capítulo MCP |
| Escalada de privilegios / evasión de rol / abuso de credenciales | `references/ai-identity-security.md` |
| Fuga de datos / fuga de Prompt / inversión de modelo | `references/ai-data-security.md` |
| Escape de contenedor / CI-CD / fallo de sandbox | `references/ai-baseline-security.md` |
| Riesgo de modelo / ejemplos adversarios / backdoor | `references/ai-model-security.md` |
| Clasificación de impacto y evaluación de cobertura | `references/gaarm-risk-matrix.md` |

## Flujo de pruebas

### 1. Ataques a la capa de aplicación
- Inyección de Prompt directa
- Inyección indirecta (a través de fuentes de datos externas)
- Interferencia de CoT y sobrescritura de instrucciones
- Abuso de Agent (operaciones no autorizadas)
- Ruptura por ejecución de código
- Envenenamiento de Memory

### 2. Riesgos de MCP y Agent
- Envenenamiento de descripción de herramientas
- Sobrescritura de instrucciones
- Inyección de instrucciones ocultas
- Acceso no autorizado a recursos
- Problemas de cadena de suministro de Skills/Rules

### 3. Identidad y autorización
- Abuso de acciones
- Evasión de rol
- Deriva de privilegios
- Abuso de credenciales de nube

### 4. Datos y privacidad
- Fuga de Prompt
- Exposición de datos sensibles
- Problemas de datos de entrenamiento
- Inversión de modelo
- Robo de datos vía API

### 5. Línea base y despliegue
- Fallos de CI/CD
- Escape de contenedor
- Seguridad de bases de datos vectoriales
- Fallo de sandbox
- Fallos de aislamiento de entorno
- Fallos del servicio de modelo

## Documentos de referencia

- `references/04-ai-and-mcp-security-integrated.md` — Referencia integrada de seguridad de IA y MCP
- `references/ai-app-security.md` — Seguridad de aplicaciones de IA
- `references/ai-identity-security.md` — Seguridad de identidad de IA
- `references/ai-data-security.md` — Seguridad de datos de IA
- `references/ai-baseline-security.md` — Seguridad de línea base de IA
- `references/ai-model-security.md` — Seguridad de modelos de IA
- `references/gaarm-risk-matrix.md` — Matriz de riesgos GAARM

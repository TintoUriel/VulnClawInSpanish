---
name: secknowledge-skill
description: |
  Base de conocimiento de seguridad Web+IA. Combina 88,636 casos de WooYun + metodología
  Xianzhi L1-L4 + 150 riesgos GAARM + OWASP Top 10 (LLM/ASI/WSTG).
  TRIGGER cuando la tarea es una prueba de seguridad real: pentesting, descubrimiento/explotación
  de vulnerabilidades, red team, auditoría de seguridad (SAST/DAST), CTF, pruebas de seguridad
  de IA/LLM (inyección de Prompt/jailbreak/MCP/Agent/escape de sandbox). El usuario da un
  objetivo de prueba explícito (URL/código/modelo/arquitectura de Agent) y su intención es
  "probar/auditar/buscar vulnerabilidades/explotar".
  DO NOT trigger:
  - Discusión de conceptos de seguridad ("qué es XSS", "cuál es el principio de la inyección SQL") → respuesta normal
  - Code review / debug / optimización de rendimiento de naturaleza no relacionada con seguridad → code-audit-skill u otro
  - Corrección de errores de sintaxis / bugs de lógica de negocio → asistencia de programación normal
  - Auditoría de código en caja blanca puramente Web (directorio completo del proyecto / análisis de contaminación Source-Sink) → code-audit-skill
  - Solo consultar documentación por número de CVE → WebSearch
  Reglas de límite: fragmento de código corto de CTF + idea de explotación → este Skill; directorio completo del proyecto + auditoría sistemática en caja blanca → code-audit-skill
routing:
  target_types: [web, ai_agent]
  task_types: [pentest, audit, bugbounty, ctf]
  broad: true
---

# Base de conocimiento de seguridad Web e IA

> Fuente de conocimiento: 88,636 vulnerabilidades de WooYun × 5,600+ documentos de Xianzhi × 150 riesgos de IA de GAARM × OWASP
> Arquitectura: SKILL.md (enrutamiento) → references/ (carga según escenario)

## Notas de integración en VulnClaw

- Este Skill está integrado desde `Pa55w0rd/secknowledge-skill`, y se usa en VulnClaw como specialized skill `secknowledge-skill`; el upstream declara licencia MIT.
- En escenarios CTF/SRC, cargar primero `references/vulnclaw-ctf-src-routing.md` para determinar la entrada de material, y luego cargar `web-*`, `ai-*`, `testing-methodology.md` o `gaarm-risk-matrix.md` según el tipo de vulnerabilidad.
- En colaboración con las skills existentes de VulnClaw: para técnicas de un solo reto CTF, priorizar la combinación con `ctf-web`/`ctf-crypto`/`ctf-misc`; para SRC y descubrimiento de vulnerabilidades reales, priorizar la metodología, el mapeo de casos, la matriz de riesgos y las restricciones de evidencia de este Skill.
- En la salida, conservar los límites de autorización, las anotaciones de referencia y la distinción "hipótesis/confirmación" del upstream; todo payload, CVE o número GAARM/OWASP que no pueda respaldarse con una reference debe marcarse explícitamente como no verificado.

## Condiciones de activación

**Condiciones de activación (combinación AND)**:
1. La intención del usuario es **ejecutar** una prueba de seguridad (pentest/búsqueda de vulnerabilidades/explotación/auditoría) — no discusión/aprendizaje
2. Se proporciona un **objetivo concreto**: URL, endpoint, fragmento de código, modelo/arquitectura de Agent, configuración MCP — no una pregunta abstracta
3. La tarea **involucra uno de los siguientes dominios**:
   - Web: inyección SQL/XSS/ejecución de comandos/control de acceso indebido/subida de archivos/SSRF/deserialización insegura/XXE/GraphQL/HTTP request smuggling
   - IA: inyección de Prompt/jailbreak/envenenamiento de MCP/abuso de Agent/envenenamiento de RAG/escape de sandbox/robo de modelo
   - Bypass: WAF/filtrado de contenido/bypass de Guard Rails

**No se activa** (si se cumple cualquiera, se enruta a otro lugar):
- Explicación de conceptos: "qué es…", "principio de…", "cómo defenderse de…" → respuesta normal
- Revisión de código no relacionada con seguridad: "revisar calidad de código", "optimizar rendimiento" → code review normal
- Bugs de negocio: errores de sintaxis, punteros nulos, errores de lógica de negocio (no lógica de seguridad) → debug normal
- **Auditoría de código en caja blanca profunda** (propagación de contaminación Source-Sink, análisis AST) → code-audit-skill
- Consultar documentación de CVE o de herramientas → WebSearch/Context7

**Manejo de ambigüedad**: si el objetivo y la intención no están claros, preguntar primero: "¿Cuál es el objetivo? ¿Quieres hacer una prueba de penetración / auditoría de código / o entender el concepto?"

## Normas de comportamiento (válidas durante toda la sesión, no se relajan por la duración de la conversación)

1. ❗ **Todo Payload/número de CVE/número de riesgo debe citar la sección concreta del archivo de reference** — autoverificación antes de cada salida. Lo que no esté en la reference debe marcarse como "UNABLE TO CITE"; queda prohibido inventar.
2. ❗ **Distinguir entre "hipótesis de vulnerabilidad" y "vulnerabilidad confirmada"** — un riesgo potencial inferido a partir de la metodología → marcar `Hipótesis (requiere verificación)`; uno con evidencia clara → marcar `Confirmado (evidencia: …)`. Prohibido confundir ambos.
3. ❗ **Límites de autorización** — antes de emitir cualquier paso de explotación se debe confirmar que se trata de CTF/pentest autorizado/entorno propio. Sin contexto de autorización, solo se emite el análisis, no un Payload completo listo para usarse como arma.

## Prevención de alucinaciones y citación de fuentes

| Tipo de contenido | Salida correcta | Salida prohibida |
|---------|---------|---------|
| Número de CVE | Citar el archivo y sección concretos de reference, o marcar "UNABLE TO CITE — se recomienda verificar con WebSearch" | Inventar CVE-YYYY-NNNN |
| Payload | Citar desde la sección de payloads de `references/web-*.md` o `references/ai-*.md` | Escribir el payload de memoria |
| Número de riesgo GAARM | Citar `references/gaarm-risk-matrix.md` | Inventar un número |
| Entrada OWASP | LLM01-10 / ASI01-10 / WSTG-* citar `testing-methodology.md §10.x` | Reescribir el significado del número |
| Herramienta/comando | Usar solo lo que aparece en la reference, o marcar explícitamente "comando genérico (no verificado en la reference)" | Falsificar parámetros de herramientas |
| Sin resultado de búsqueda | "UNABLE TO ASSESS: la reference no cubre este escenario, se recomienda WebSearch" | Especular por experiencia como si fuera conclusión |

**Niveles de anotación**:
- `[Cita]` — proviene de una sección concreta de la reference (debe incluir file:section)
- `⚠️ Conocimiento general` — no verificado en las reference de este Skill, solo a modo informativo
- `💡 Sugerencia` — razonamiento metodológico, no es una afirmación factual

## Restricciones de salida

Prohibido emitir:
- Frases de apertura: "Déjame analizar…" / "Primero necesitamos…" / "Según tu solicitud…"
- Descripción de llamadas a herramientas: "Voy a usar la herramienta Read para leer XX"
- Repetición de información ya conocida (la URL que el usuario acaba de dar, el tipo de objetivo)
- Payload o número de CVE sin cita de fuente
- Cadena de explotación completa lista para usarse como arma en un escenario no autorizado

Límites de salida:
- Cada respuesta ≤ 3 niveles de sugerencias (evitar la inflación de información)
- Ejemplos de Payload ≤ 5 por tipo de vulnerabilidad (la lista completa se cita desde la reference)
- Usar formato de tabla/referencia rápida, prohibidos los párrafos largos narrativos

## Prioridad de herramientas (uso interno de este Skill)

| Operación | Preferida | Condición de degradación | Herramienta de respaldo |
|------|------|---------|---------|
| Leer reference | Read | Falla Read | Bash cat |
| Buscar palabra clave/CVE | Grep (dentro de reference) | 2 fallos consecutivos | WebSearch |
| Objetivo de auditoría de código | Delegar a code-audit-skill | — | — |

Un timeout puntual ≠ no disponible; debe reintentarse 1 vez antes de degradar.

## Flujo de uso

**Restricción de cadena de dependencias (aplica a los tres pasos, obligatoria)**:
- La entrada del Paso 2 == la "lista de reference ya localizadas" del Paso 1, no se pueden añadir archivos nuevos
- El conjunto de citas del Paso 3 ⊆ la "lista ya cargada" del Paso 2, prohibido volver a buscar reference en el Paso 3
- El conteo de citas del Checkpoint del Paso 3 debe poder encontrar su origen correspondiente en el Checkpoint del Paso 2

**Paso 1: Clasificación del objetivo + localización de reference**
- Determinar: Web / IA / Mezcla Web+IA / Sandbox de contenedor
- Localizar: usar el "índice de navegación de escenarios" para encontrar el archivo de reference correspondiente, registrado como lista `L1`

Degradación por fallo:
- Información del objetivo insuficiente para clasificar → activar pregunta de aclaración de ambigüedad, no adivinar; no se permite clasificar por defecto como "Mezcla Web+IA"
- El índice de navegación de escenarios no cubre este escenario → marcar "UNABLE TO CITE: el escenario {X} no está en el índice", lista `L1` vacía, al llegar al Paso 3 solo se pueden emitir sugerencias a nivel metodológico

✅ Checkpoint: `Paso 1 completado: tipo de objetivo={X}, |L1| == número de coincidencias del índice de navegación de escenarios = {N}`

**Paso 2: Carga bajo demanda de las reference localizadas en el Paso 1 (carga perezosa)**
- Entrada: la lista `L1` producida por el Paso 1; el conjunto cargado en este paso se registra como `L2`, debe cumplir `L2 ⊆ L1`
- Cargar 1 archivo a la vez, ≤ 1000 tokens por vez; las reference que excedan el presupuesto (p. ej. `ai-identity-app.md` con 906 líneas, `ai-data-app.md` con 903 líneas) deben localizarse primero con Read offset/limit o Grep antes de leerse
- Prohibido cargar en este paso archivos que no estén en `L1`

Degradación por fallo:
- Falla Read → reintentar 1 vez → si sigue fallando usar Bash cat → si todo falla → marcar "UNABLE TO ASSESS: archivo no legible", eliminar ese elemento de `L2`, no se permite saltar directamente al Paso 3
- Grep sin coincidencias → marcar "UNABLE TO CITE: {palabra clave} no encontrada en {archivo}"
- El archivo de reference no existe → marcar enlace roto + añadir a la lista de reference pendientes, no inventar contenido

✅ Checkpoint: `Paso 2 completado: |L2| == |L1| - número de archivos no legibles = {M}, total {X} tokens`

**Paso 3: Emitir la línea de prueba según la metodología (L1→L4)**
- Entrada: el conjunto cargado `L2` producido por el Paso 2; todas las citas de este paso deben ser ⊆ `L2`
- Identificación de superficie de ataque L1 → Construcción de hipótesis L2 → Explotación profunda L3 → Contramedidas de defensa L4
- Cada conclusión debe citar una sección/línea concreta de algún archivo de `L2`; sin fundamento → marcar "UNABLE TO CITE" y detener esa línea de hipótesis
- Prohibido volver a buscar: si en este paso se detecta la necesidad de una nueva reference, volver al Paso 1 a localizarla, en lugar de hacer Read/Grep directamente

✅ Checkpoint: `Paso 3 completado: se emitieron N hipótesis, de las cuales M citadas + K UNABLE TO CITE == N (verificación de igualdad)`

**Validación cruzada de todo el proceso**:
- [ ] Todos los archivos citados en el Paso 3 ∈ `L2` del Paso 2 (verificación mediante grep)
- [ ] Número de elementos citados + número de UNABLE TO CITE == número total de hipótesis

## Índice de navegación de escenarios

> Cada fila apunta a la reference correspondiente. Todos los Payloads/casos/metodología detallados están en la reference; este SKILL.md ya no los desarrolla.

### Metodología central

| Escenario | reference |
|------|----------|
| Pirámide de pensamiento L1-L4 + fórmula de vulnerabilidades de WooYun + mapeo GAARM | `references/testing-methodology.md` |
| Mapeo OWASP Top 10 (LLM/ASI/WSTG) | `testing-methodology.md §10.1-10.3` |
| 150 números de riesgo de GAARM | `references/gaarm-risk-matrix.md` |

### Seguridad Web (por tipo de vulnerabilidad)

| Escenario | reference |
|------|----------|
| Inyección SQL (incluye referencia rápida de SQLMap) | `references/web-sqli.md` |
| XSS (Cross-Site Scripting) | `references/web-xss.md` |
| Ejecución de comandos (RCE) | `references/web-rce.md` |
| XXE (entidad externa XML) | `references/web-xxe.md` |
| Vulnerabilidades de deserialización | `references/web-deser.md` |
| Subida de archivos (incluye evasión de webshells) | `references/web-upload.md` |
| Traversal de directorios / inclusión de archivos | `references/web-traversal.md` |
| Fuga de información (.git / backups / mensajes de error) | `references/web-leak.md` |
| SSRF / errores de configuración de servidor / apéndice CMS+URL | `references/web-ssrf-misc.md` |
| Control de acceso indebido / pagos / restablecimiento de contraseña / sesión / autenticación de API | `references/web-logic-auth.md` |
| CORS / GraphQL / HTTP request smuggling / WebSocket / OAuth | `references/web-modern-protocols.md` |
| Cadena de suministro / configuración cloud / contenedores / CI/CD / CVE de frameworks | `references/web-deployment-security.md` |

### Seguridad de IA/LLM (por etapa GAARM)

| Dominio de seguridad | Etapa de aplicación | Etapa de despliegue | Etapa de entrenamiento |
|--------|---------|---------|---------|
| **Aplicación de IA** (la etapa de aplicación se subdivide por categoría de riesgo ↓) | ver tabla detallada abajo | `ai-app-deploy.md` | `ai-app-train.md` |
| **Modelo de IA** (la etapa de aplicación se subdivide por categoría de riesgo ↓) | ver tabla detallada abajo | `ai-model-deploy.md` | `ai-model-train.md` |
| **Datos de IA** (fuga/robo/inferencia de Prompt) | `ai-data-app.md` | `ai-data-deploy.md` | `ai-data-train.md` |
| **Identidad de IA** (escape de rol/suplantación de Agent) | `ai-identity-app.md` | `ai-identity-deploy.md` | `ai-identity-train.md` |
| **Base de IA** (contenedor/sandbox/cadena de suministro) | `ai-baseline-app.md` | `ai-baseline-deploy.md` | `ai-baseline-train.md` |

**Aplicación de IA - etapa de aplicación por categoría de riesgo**:

| Categoría de riesgo | Número GAARM | reference |
|---------|----------|----------|
| Inyección de Prompt y variantes (directa/indirecta/XSS/Memory/gusano/ofuscación/codificación/inducción inversa/multimodal) | GAARM.0039, 0040.x, 0043.x, 0044, 0045, 0061 | `ai-app-prompt.md` |
| Ataques al protocolo MCP (fraude tipo alfombra/envenenamiento de herramientas/sobrescritura de instrucciones/instrucciones ocultas) | GAARM.0046.x | `ai-app-mcp.md` |
| Ataques a Agent y CoT (abuso de Agent/SSRF/RCE/CoT/inyección de consultas/inyección de entorno) | GAARM.0041.x, 0042.x, 0047, 0056.001, 0060 | `ai-app-agent-cot.md` |

**Modelo de IA - etapa de aplicación por categoría de riesgo**:

| Categoría de riesgo | Número GAARM | reference |
|---------|----------|----------|
| Jailbreak (DAN/Many-shot/sufijo adversarial/activación de conceptos) | GAARM.0027.x | `ai-model-jailbreak.md` |
| Alucinación (factual/cross-modal) | GAARM.0028.x, 0064 | `ai-model-hallucination.md` |
| Contenido no conforme (sesgo/violencia/político/falso/inducción) | GAARM.0029.x | `ai-model-content.md` |
| Derechos de autor e infracciones comerciales | GAARM.0030.x | `ai-model-copyright.md` |
| Abuso funcional y falsificación de información (imagen/audio/video/phishing) | GAARM.0031.x, 0033, 0062, 0063 | `ai-model-misuse.md` |
| Ejemplos adversariales y extracción de modelo | GAARM.0032.x | `ai-model-extraction.md` |

**Reference especializadas**:
- Riesgos de vanguardia 2025-2026 en AI Agent / MCP / Skills → `references/ai-app-frontier.md`
- Metodología práctica de escape de contenedores y sandboxes → `references/ai-baseline-escape.md`

### Referencia rápida de Payloads (buscar en la reference principal según el escenario)

| Escenario | reference |
|------|----------|
| Payload de inyección SQL | `references/web-sqli.md` |
| Payload de XSS | `references/web-xss.md` |
| Payload de RCE / ejecución de comandos | `references/web-rce.md` |
| Payload de deserialización / XXE | `references/web-deser.md` / `references/web-xxe.md` |
| Payload de bypass de subida de archivos / traversal de rutas | `references/web-upload.md` / `references/web-traversal.md` |
| Payload de SSRF | `references/web-ssrf-misc.md` |
| Payload de protocolos web modernos (GraphQL/HTTP smuggling/WebSocket) | `references/web-modern-protocols.md` |
| Payload de inyección de Prompt | `references/ai-app-prompt.md` |
| Payload de envenenamiento de MCP | `references/ai-app-mcp.md` |
| Payload de inyección de Agent / CoT | `references/ai-app-agent-cot.md` |
| Payload de jailbreak / sufijo adversarial | `references/ai-model-jailbreak.md` |
| Escape de contenedor / persistencia / movimiento lateral | `references/ai-baseline-escape.md` |

## Manejo de resultados vacíos

| Situación | Acción correcta |
|------|---------|
| Grep sin coincidencias en la reference | "UNABLE TO CITE: el escenario {X} no está cubierto en la reference. Se recomienda WebSearch o complementar la reference" |
| La URL dada por el usuario no responde | "UNABLE TO ASSESS: el objetivo no es alcanzable" — no adivinar vulnerabilidades basándose en la estructura de la URL |
| Se requiere ejecución pero no hay contexto de autorización | "Solo se emite el análisis, no la cadena lista para usarse como arma. Si se trata de una prueba autorizada, especifique el alcance de la autorización" |
| La reference coincide parcialmente con el escenario del usuario | Citar la parte coincidente + marcar explícitamente la parte no cubierta como "UNABLE TO CITE" |

## Enrutamiento hacia otros Skills

| Solicitud del usuario | Enrutamiento correcto |
|---------|---------|
| Pentest / red team / CTF / búsqueda de vulnerabilidades | **Este Skill** |
| Auditoría de código en caja blanca profunda Java/JS (Source-Sink) | code-audit-skill |
| Pruebas específicas de la plataforma Mirawork | mirawork-security-tester |
| Metodología de análisis de vulnerabilidades históricas de WooYun | wooyun-legacy |
| Metodología de investigación de la comunidad Xianzhi | xianzhi-research |

---

*v2.0 | Fuente de conocimiento: WooYun 88,636 × Xianzhi 5,600+ × GAARM 150 × OWASP LLM/ASI/WSTG*

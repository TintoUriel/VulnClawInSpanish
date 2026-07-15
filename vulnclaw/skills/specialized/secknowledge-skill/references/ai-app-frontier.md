# Seguridad de Aplicaciones de IA - Riesgos de Seguridad de Vanguardia (2025-2026)

> Fuente: Comunidad AISS NSFOCUS de Seguridad de Grandes Modelos | Extraído de ai-app-security.md
> Tema: Riesgos de vanguardia de AI Agent/MCP/Skills (Claude Code CVE / Inyección de Skills / Gusanos de Agent)

## 35. Riesgos de Seguridad de Vanguardia de AI Agent/MCP/Skills (2025-2026)

> El siguiente contenido se basa en la investigación de seguridad más reciente de 2025-2026, cubriendo OWASP Agentic AI Top 10 (ASI01-ASI10).

### Seguridad del Protocolo MCP (Model Context Protocol)

#### 11 Categorías de Riesgos Emergentes de MCP (investigación de Checkmarx/Invariant Labs/Trail of Bits 2025)

| Tipo de riesgo | Descripción | Escenario de ataque |
|----------|------|----------|
| Envenenamiento de la descripción de herramientas | Se incrustan instrucciones maliciosas ocultas en la tool description | El modelo lee y sigue el Prompt oculto en la description al ejecutar la herramienta |
| Estafa tipo alfombra (Rug Pull) | El Server modifica dinámicamente la descripción de la herramienta después de que el usuario la autoriza | La revisión inicial se aprueba, pero la lógica de la función se manipula posteriormente |
| Sobrescritura de instrucciones (Shadow Tool) | La descripción de la herramienta de un Server malicioso secuestra el comportamiento de una herramienta confiable | Se modifica el destinatario de una herramienta de envío de correo para que sea el atacante |
| Instrucciones ocultas mediante ANSI/Unicode | Se aprovechan códigos de escape de terminal o caracteres Unicode invisibles para ocultar instrucciones | Ataque a la cadena de suministro: el modelo sugiere descargar un paquete malicioso |
| Ataques entre Servers | Conflicto y secuestro de definiciones de herramientas entre múltiples MCP Servers | El Server A redefine el nombre de una herramienta del Server B |
| Robo de Token/credenciales | Extracción de los Tokens OAuth y claves de API almacenados por el MCP Server | Un único punto de compromiso permite obtener las credenciales de todos los servicios conectados |
| Suplantación de Server | Un MCP Server malicioso se hace pasar por un servicio legítimo y registra todas las consultas | Robo de datos y monitoreo de comportamiento |
| Manipulación de Schema | Se modifica dinámicamente el Schema de entrada/salida de la herramienta para eludir la validación | Se inyectan parámetros adicionales o se modifican los valores de retorno |
| Inyección de comandos | Se inyectan comandos del SO a través de los parámetros de la herramienta | El MCP Server ejecuta comandos shell sin filtrar |
| Desbordamiento de contexto | Se construye una respuesta de herramienta extremadamente grande para agotar la ventana de contexto del modelo | Se desplazan las instrucciones de seguridad, reduciendo la capacidad de juicio del modelo |
| Envenenamiento persistente | Se contamina el historial de la conversación mediante los valores de retorno de la herramienta | Afecta a largo plazo la seguridad de todas las interacciones posteriores |

#### Métodos de Prueba de Seguridad de MCP

1. **Auditoría de descripción de herramientas**: verificar si el campo description de todas las tools registradas contiene instrucciones ocultas (códigos ANSI/Unicode/comentarios HTML)
2. **Monitoreo de comportamiento dinámico**: comparar si la descripción de la herramienta en el registro inicial coincide con la del tiempo de ejecución
3. **Aislamiento entre Servers**: verificar si hay conflictos de nombres de herramientas en entornos con múltiples Servers
4. **Auditoría de almacenamiento de credenciales**: verificar la forma de almacenamiento del Token OAuth/API Key (texto plano vs. cifrado)
5. **Pruebas de validación de entrada**: realizar pruebas de inyección de comandos/inyección SQL sobre los parámetros de la herramienta
6. **Pruebas de límites de permisos**: verificar si la herramienta puede acceder a recursos fuera del ámbito declarado

### Seguridad de AI Agent (complemento a OWASP ASI01-ASI10)

#### Caso Real Clawdbot/Moltbot (enero de 2026)

Incidente de seguridad de AI Agent en el que se descubrieron más de 4500 instancias expuestas a nivel mundial:
- **Causa raíz**: una configuración incorrecta del proxy inverso provocó que la autenticación de localhost se aprobara automáticamente
- **Impacto**: se extrajeron claves de API, Tokens de servicio y credenciales de sesión de WhatsApp
- **Lección**: el AI Agent concentra privilegios elevados como ejecución de shell, estado persistente e inicio autónomo de tareas; un único punto de exposición equivale a un compromiso total

#### Ataques de Selección de Herramientas del Agent (investigación CATS)

- El pool de herramientas funciona como un repositorio no controlado, y los atacantes pueden publicar herramientas con metadatos engañosos
- Bajo ataques adversarios, la precisión de autenticación en la selección de herramientas del Agent cae más de un 60%
- Tras ataques adversarios adaptativos, la precisión cae por debajo del 20%

#### ASI07: Seguridad de la Comunicación entre Múltiples Agents

| Vector de ataque | Descripción |
|----------|------|
| Falsificación de mensajes | El Agent A se hace pasar por el Agent B para enviar instrucciones |
| Abuso de la transferencia de confianza | Un Agent de bajos privilegios aprovecha la relación de confianza de un Agent de altos privilegios |
| Secuestro de la coordinación | Se manipula la asignación de tareas y la agregación de resultados entre Agents |
| Ataque de intermediario (man-in-the-middle) | Se intercepta y manipula la comunicación entre Agents |

#### ASI09: Explotación de la Confianza Humano-Máquina

- Dependencia excesiva: el usuario ejecuta directamente las salidas de la IA sin verificarlas
- Ingeniería social potenciada: el contenido de phishing generado por IA resulta más creíble
- Sesgo de confirmación: el usuario tiende a confiar en las salidas de IA que coinciden con sus expectativas
- Sesgo de automatización: la mentalidad de "lo que dice la IA debe ser correcto"

#### ASI10: Agent Malicioso/Fuera de Control

- El Agent, tras ser comprometido, opera fuera de los parámetros autorizados
- Deriva de objetivos en la cadena de toma de decisiones autónoma
- Movimiento lateral: infección de otros Agents a través de la comunicación entre Agents

### Seguridad de la Cadena de Suministro de Skills/Rules

#### Superficie de Ataque

Los sistemas de Skills y Rules de los asistentes de programación con IA (Claude Code/Cursor, etc.) introducen una nueva superficie de ataque en la cadena de suministro:

| Vector de ataque | Descripción | Impacto |
|----------|------|------|
| Inyección de Skill maliciosa | Se incrustan instrucciones de Prompt maliciosas en un skill compartido por la comunidad | La IA ejecuta comandos ocultos (como exfiltración de datos) |
| Manipulación del archivo Rules | Se modifica .cursorrules/.claude/RULES.md mediante un PR | Control a largo plazo del comportamiento de IA del desarrollador |
| Envenenamiento de SKILL.md | Se incrusta inyección indirecta en los archivos reference referenciados por el skill | La IA ejecuta instrucciones maliciosas al leer el reference |
| Ataque a la cadena de dependencias | Se sustituye el MCP Server externo del que depende el skill | Todos los usuarios que usan ese skill se ven afectados |
| Explotación de hooks de compilación | Se activan operaciones de compilación maliciosas a través de scripts/ del skill | Ejecución de código, robo de claves |

#### CVEs Divulgados de Claude Code (2025-2026)

| CVE | Gravedad | Descripción |
|-----|--------|------|
| CVE-2025-54795 | Alta | El comando echo elude la aprobación del usuario y se ejecuta directamente |
| GHSA-qxfv-fcpc-w36x | Alta | La inyección de comandos rg elude el Prompt de aprobación |
| - | Alta | La elusión de la validación del comando sed permite la escritura arbitraria de archivos |
| - | Alta | Es posible ejecutar comandos antes de que se muestre el cuadro de diálogo de confianza inicial |
| - | Moderada | Una configuración de repositorio maliciosa provoca filtración de datos |

#### Recomendaciones de Defensa

- **Auditoría de Skills**: revisar el contenido de SKILL.md y de todos los archivos reference antes de la instalación
- **Verificación de firma**: verificar el origen y la integridad del skill (actualmente no existe un mecanismo oficial, debe hacerse manualmente)
- **Aislamiento de permisos**: restringir el rango de herramientas y archivos a los que puede acceder el skill
- **Protección de Rules**: incorporar .cursorrules y AGENTS.md al proceso de revisión de código
- **Lista blanca de MCP Server**: permitir la conexión únicamente a MCP Servers de confianza
- **Monitoreo de comportamiento**: registrar todos los logs de llamadas a herramientas y operaciones de archivos del asistente de IA

### Marco Integral de Pruebas de Seguridad de Agentic AI

Basado en OWASP ASI01-ASI10, un proceso sistemático de pruebas para aplicaciones de AI Agent:

1. **Enumeración de objetivos**: identificar todos los Agents, herramientas, MCP Servers y canales de comunicación
2. **Pruebas de autenticación**: verificación de identidad del Agent, gestión de Tokens, límites de permisos (ASI03)
3. **Seguridad de herramientas**: auditoría de description, inyección de parámetros, exceso de permisos (ASI02)
4. **Pruebas de inyección**: inyección de Prompt directa/indirecta, inyección mediante valores de retorno de herramientas (ASI01)
5. **Auditoría de la cadena de suministro**: origen del MCP Server, integridad del skill, seguridad de dependencias (ASI04)
6. **Ejecución de código**: escape de sandbox, inyección de comandos, operaciones de archivos (ASI05)
7. **Seguridad de la memoria**: envenenamiento de contexto, ataques de persistencia, corrupción de estado (ASI06)
8. **Seguridad de la comunicación**: autenticación entre Agents, integridad de mensajes, transferencia de confianza (ASI07)
9. **Pruebas de cascada**: alcance de propagación de un fallo puntual, aislamiento de fallos (ASI08)
10. **Pruebas de confianza**: mecanismo de validación de salidas, proceso de aprobación humana (ASI09)
11. **Pruebas de escape**: monitoreo de comportamiento del Agent, detección de anomalías, Kill Switch (ASI10)

# 08 Rapid Checklists And Payloads

This file is the rapid operator-reference layer of the final skill system.
Use it only after routing is clear. It is meant for fast lookup, not for replacing methodology or workflow selection.

## Use This File For

- Recordar rápidamente qué revisar primero para cierto tipo de vulnerabilidad o punto de bloqueo
- Filtrar rápidamente familias de payload, direcciones de bypass y orden de verificación
- Confirmar rápidamente tarjetas de prueba comunes de AI, MCP, contenedores, WebSocket, JWT, archivos, autenticación, SSRF, etc.
- Pasar rápidamente de "sé qué necesito probar" a "por cuál categoría de verificación empiezo"

## Do Not Use This File For

- Sustituir `00-usage-and-routing.md` para la distribución de escenarios
- Sustituir `01-unified-methodology.md` para decisiones metodológicas
- Entrar directamente en pruebas de payload a ciegas cuando la solicitud no se ha capturado o la reproducción no es estable

## Fast Routing Cards

### Web injection or output execution

- Ver primero `web-playbook-index.md` (Skill `web-security-advanced`)
- Si es validación de punto de entrada, priorizar clasificar en `SQLi`, `XSS`, `command execution`, `SSTI`, `XXE`
- Si la solicitud es construida por el cliente, volver primero a `02-client-api-reverse-and-burp.md`

### Auth, logic, token, or state bugs

- Ver primero `web-playbook-index.md` (Skill `web-security-advanced`)
- Confirmar primero la identificación de objetos, los límites de roles, el flujo de reset, los montos de pago, las dependencias de orden
- Si el token o la firma provienen del cliente, estabilizar la reproducción antes de probar

### Browser-side sign, anti-bot, or WebSocket handshake

- Ver primero `browser-js-signing-workflow.md`
- Luego avanzar por fases en `browser-locate-and-request-chain.md`, `browser-recover-and-shell-reduction.md`, `browser-runtime-fit-and-risk.md`, `browser-validation-and-handoff.md`
- Una vez estable la reproducción, volver a `web-playbook-index.md` (Skill `web-security-advanced`)

### Android runtime, packet visibility, or sign recovery

- Ver primero `android-external-url-runtime-first-workflow.md`
- Si se avanza mediante el estado de la interfaz, continuar con `android-ui-driven-observation-and-packet-loop.md`
- Solo entrar en `android-signing-and-crypto-workflow.md` cuando no se pueda capturar el paquete, el paquete no sea transparente o la reproducción esté bloqueada

### AI, agent, or MCP exposure

- Ver primero `04-ai-and-mcp-security-integrated.md`
- Clasificar primero en `prompt injection`, `tool abuse`, `MCP trust boundary`, `memory/state poisoning`, `output approval gaps`
- Para consultar rápidamente semánticas de prueba comunes, ver las tarjetas AI/MCP más abajo

### Intranet, host, or AD work

- Ver primero `06-intranet-and-host-operations-integrated.md`
- Si hay dudas sobre herramientas, complementar con `tools-reference-index.md` (Skill `pentest-tools`)

## Web Rapid Cards

### SQL injection

- Verificación rápida: `'`, `"`, `)`, diferencia booleana, diferencia de tiempo, diferencia de error
- Confirmar primero la ubicación de la inyección: query, body, JSON, header, cookie, WebSocket message
- Verificar primero si la entrada está afectada por firma o cifrado del cliente; si es así, restaurar primero el ciclo de vida de la solicitud
- Direcciones de bypass comunes: inline comments, whitespace variation, keyword case folding, alternate encodings, parameter pollution

### XSS

- Clasificación rápida: reflected, stored, DOM
- Confirmar primero el contexto: HTML body, attribute, JS string, URL, template
- Familias de arranque comunes: event handlers, SVG, tag breaking, JS context breaking
- Si el resultado pasa por un framework de renderizado del cliente, verificar simultáneamente el DOM sink y el comportamiento de CSP

### Command execution

- Verificación rápida: timing, DNS or HTTP OOB, harmless command echo
- Identificar primero si el punto de ejecución es system shell, template helper, language runtime o worker sidecar
- Direcciones de bypass comunes: separators, whitespace bypass, concatenación de variables, Base64 or hex decode chains

### File and SSRF

- Problemas de archivos, clasificar primero: upload, traversal/download, inclusion, parser confusion
- SSRF, clasificar primero: raw fetch, image proxy, webhook, PDF render, URL preview, cloud metadata reachability
- Direcciones de bypass comunes: encoding layers, mixed path separators, alternate IP formats, redirect chaining, protocol pivot

### Modern protocols

- WebSocket: confirmar primero la autenticación del handshake, la validación de Origin, la autenticación a nivel de mensaje, los límites de sala
- JWT: confirmar primero el manejo del algoritmo, la validación de firma, la ruta dinámica de obtención de clave como `kid` o `jku`
- OAuth/OIDC: confirmar primero redirect URI, state, PKCE, vinculación de cuenta
- Request smuggling: confirmar primero la cadena de proxies y las diferencias de análisis entre frontend y backend

## AI And MCP Rapid Cards

### Prompt injection

- Clasificación rápida: direct, indirect, retrieval-borne, tool-description-borne, memory-borne
- Confirmar primero en qué límite entra la inyección: model prompt, retrieval context, tool metadata, tool output, persisted memory
- Direcciones de bypass comunes: role play, instruction override, encoding, multilingual phrasing, hidden text, long-context dilution

### Tool abuse and MCP trust boundary

- Confirmar primero si la tool description será leída con alta confianza por el modelo
- Confirmar primero si tool parameters, resource paths, tool outputs serán reinterpretados
- Verificación rápida: unauthorized resource reads, prompt override in description, hidden instructions, cross-tool request rewriting

### Agent memory and state poisoning

- Confirmar primero si la memory es almacenamiento explícito o un resumen implícito del historial
- Verificar primero si es posible escribir objetivos maliciosos, preferencias de rol o instrucciones externas en el estado persistente
- Prestar atención a la deriva de comportamiento entre turnos, el bypass de aprobación, la exfiltración silenciosa

### Model or data leakage

- Verificación rápida: system prompt extraction, tool inventory exposure, API or secret leakage, training-data style continuation, RAG source disclosure
- Distinguir primero entre direct disclosure e inference-style leakage

## Container And Sandbox Rapid Cards

### Environment triage

- Confirmar primero si se está dentro de un contenedor, sandbox, shell restringida o agent execution sandbox
- Verificar primero capabilities, namespace, mount, socket, metadata reachability
- Si solo se está verificando el límite de aislamiento, no intentar primero acciones destructivas

### Escape paths

- Direcciones comunes: exposed Docker socket, writable host mounts, privileged container, cgroup abuse, `/proc` traversal, kernel CVE, cloud metadata pivots
- Hacer primero una recopilación de información mínima, luego decidir si continuar

### Persistence or staged foothold

- Confirmar primero el límite de autorización y el objetivo de la prueba
- Priorizar verificar "si se puede persistir" en lugar de propagarse directamente
- Ubicaciones comunes: shell rc files, scheduled tasks, service startup, workspace poisoning, SSH keys

## Payload Family Hints

Use families, not copied full lists, unless the current task specifically needs detail from a deeper source.

- SQLi: boolean, time, error, union, second-order
- XSS: reflected, stored, DOM, mutation-based, CSP-aware
- Command execution: separator-based, subshell, whitespace-bypass, encoded launcher, OOB validation
- File bugs: upload extension variants, MIME mismatch, parser confusion, traversal encodings
- SSRF: alternate IP encodings, redirect pivot, protocol pivot, metadata paths
- AI injection: direct override, indirect document-borne, description poisoning, memory poisoning, encoded or multilingual prompts
- Escape and shell: environment triage, breakout path validation, persistence validation, callback channel selection

## Escalation Rule

- If the route is still unclear, go back to `00-usage-and-routing.md`.
- If packet visibility or replay is blocked, go back to `02-client-api-reverse-and-burp.md` or the matching browser or Android workflow.
- If you need exact original payload wording or exhaustive raw examples, use the Web Rapid Cards section above or open the relevant `web-playbook-*.md` files in `web-security-advanced`.



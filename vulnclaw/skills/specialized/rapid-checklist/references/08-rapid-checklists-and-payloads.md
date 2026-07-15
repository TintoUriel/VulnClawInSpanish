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

- 快速验证: `'`, `"`, `)`, 布尔差异, 时间差异, 报错差异
- 先确认注入位置: query, body, JSON, header, cookie, WebSocket message
- 先看输入是否受客户端签名或加密影响, 有的话先恢复请求生命周期
- 常见绕过方向: inline comments, whitespace variation, keyword case folding, alternate encodings, parameter pollution

### XSS

- 快速分型: reflected, stored, DOM
- 先确认上下文: HTML body, attribute, JS string, URL, template
- 常见起手族: event handlers, SVG, tag breaking, JS context breaking
- 如果结果经过客户端渲染框架, 同时检查 DOM sink 和 CSP 行为

### Command execution

- 快速验证: timing, DNS or HTTP OOB, harmless command echo
- 先识别执行点是 system shell、template helper、language runtime 还是 worker sidecar
- 常见绕过方向: separators, whitespace bypass, variable拼接, Base64 or hex decode chains

### File and SSRF

- 文件问题先分: upload, traversal/download, inclusion, parser confusion
- SSRF 先分: raw fetch, image proxy, webhook, PDF render, URL preview, cloud metadata reachability
- 常见绕过方向: encoding layers, mixed path separators, alternate IP formats, redirect chaining, protocol pivot

### Modern protocols

- WebSocket: 先确认握手鉴权、Origin 校验、消息级鉴权、房间边界
- JWT: 先确认算法处理、签名校验、`kid` 或 `jku` 等动态取钥路径
- OAuth/OIDC: 先确认 redirect URI、state、PKCE、账户绑定
- Request smuggling: 先确认代理链和前后端解析差异

## AI And MCP Rapid Cards

### Prompt injection

- 快速分型: direct, indirect, retrieval-borne, tool-description-borne, memory-borne
- 先确认注入进入哪个边界: model prompt, retrieval context, tool metadata, tool output, persisted memory
- 常见绕过方向: role play, instruction override, encoding, multilingual phrasing, hidden text, long-context dilution

### Tool abuse and MCP trust boundary

- 先确认 tool description 是否会被模型高信任读取
- 先确认 tool parameters、resource paths、tool outputs 是否会被二次解释
- 快速检查: unauthorized resource reads, prompt override in description, hidden instructions, cross-tool request rewriting

### Agent memory and state poisoning

- 先确认 memory 是显式存储还是隐式历史摘要
- 先检查是否能把恶意目标、角色偏好或外部指令写入持久状态
- 关注跨轮次行为漂移、审批绕过、静默外带

### Model or data leakage

- 快速检查: system prompt extraction, tool inventory exposure, API or secret leakage, training-data style continuation, RAG source disclosure
- 先分清是 direct disclosure 还是 inference-style leakage

## Container And Sandbox Rapid Cards

### Environment triage

- 先确认是否在容器、沙箱、受限 shell 或 agent execution sandbox 内
- 先查 capabilities、namespace、mount、socket、metadata reachability
- 如果只是验证隔离边界，不要先尝试破坏性动作

### Escape paths

- 常见方向: exposed Docker socket, writable host mounts, privileged container, cgroup abuse, `/proc` traversal, kernel CVE, cloud metadata pivots
- 先做最小信息收集，再决定是否继续

### Persistence or staged foothold

- 先确认授权边界和测试目标
- 优先验证“是否可持久化”而不是直接扩散
- 常见位置: shell rc files, scheduled tasks, service startup, workspace poisoning, SSH keys

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



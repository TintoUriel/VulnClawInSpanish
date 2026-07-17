# Guía de enrutamiento CTF/SRC de VulnClaw

Esta referencia conecta `secknowledge-skill` con los flujos de trabajo de CTF y SRC de VulnClaw.

## Cuándo usar esta skill

Usa `secknowledge-skill` cuando el usuario esté realizando pruebas prácticas autorizadas con un objetivo concreto, especialmente:

- Investigación de vulnerabilidades SRC/bug bounty con superficie de ataque Web o de IA.
- Retos de CTF que se asemejen a vulnerabilidades reales de Web, IA, MCP, Agente, sandbox, SSRF, subida de archivos, deserialización, XXE, lógica o autenticación.
- Preguntas mixtas de CTF/SRC donde el usuario necesita tanto ideas de explotación como una checklist para evidencia, riesgo y reportabilidad.
- Tareas de seguridad de IA/LLM que requieran GAARM, OWASP LLM/ASI, inyección de prompts, MCP, Agente, RAG, o mapeo de escape de sandbox.

Mantén en el circuito las skills especializadas existentes de VulnClaw:

- Usa `ctf-web` para trucos cortos de CTF Web como comparación débil de PHP, bypass de preg_match, eval/RCE, SSTI y cadenas de subida de archivos.
- Usa `ctf-crypto` para problemas de criptografía pura.
- Usa `ctf-misc` para pyjail, bash jail, cadenas de codificación, esteganografía y tareas de plataforma.
- Usa `web-security-advanced` cuando el usuario pida un playbook enfocado en Web sin contexto de SRC/bug-bounty.
- Usa `ai-mcp-security` cuando la solicitud sea una evaluación general de IA/MCP y no necesite la base de conocimiento más amplia de secknowledge.

## Mapa de referencia rápida

| Escenario | Referencias a cargar primero |
| --- | --- |
| Triaje inicial de SRC | `testing-methodology.md`, `web-deployment-security.md` |
| Inyección SQL | `web-sqli.md`, `testing-methodology.md` |
| XSS o pruebas de sink DOM | `web-xss.md`, `testing-methodology.md` |
| RCE o inyección de comandos | `web-rce.md`, `web-upload.md` |
| Subida de archivos / traversal / fuga de información | `web-upload.md`, `web-traversal.md`, `web-leak.md` |
| SSRF, XXE, deserialización | `web-ssrf-misc.md`, `web-xxe.md`, `web-deser.md` |
| Autenticación, lógica, IDOR, riesgo de pagos | `web-logic-auth.md`, `testing-methodology.md` |
| GraphQL, WebSocket, OAuth, casos límite de protocolo | `web-modern-protocols.md` |
| Inyección de prompts o jailbreak de IA | `ai-app-prompt.md`, `ai-model-jailbreak.md` |
| Abuso de MCP / Agente / herramienta | `ai-app-mcp.md`, `ai-app-agent-cot.md`, `ai-app-frontier.md` |
| RAG / envenenamiento de datos / fuga | `ai-data-app.md`, `ai-data-deploy.md`, `ai-model-extraction.md` |
| Calificación de riesgo de IA | `gaarm-risk-matrix.md`, `testing-methodology.md` |

## Flujo de trabajo de CTF

1. Clasifica el reto en Web, IA/MCP/Agente, sandbox, criptografía o misceláneo.
2. Si es un truco específico de CTF, enrútalo a la skill de CTF de VulnClaw correspondiente y usa esta skill solo para familias de vulnerabilidades más amplias o disciplina de evidencia.
3. Si se asemeja a una vulnerabilidad real, carga la referencia `web-*` o `ai-*` correspondiente y mantén cada hipótesis de explotación separada del comportamiento confirmado.
4. Mantén la salida de payloads reducida y cita el archivo de referencia específico cuando sea posible.

## Flujo de trabajo de SRC

1. Confirma el alcance de autorización, el objetivo y el objetivo de la prueba.
2. Comienza con `testing-methodology.md` para cobertura y `web-deployment-security.md` para verificaciones de exposición.
3. Carga la referencia de familia de vulnerabilidad más relevante solo después de que aparezca una pista observable.
4. Registra cada elemento como `hipótesis`, `necesita validación` o `confirmado`, con evidencia como solicitud/respuesta, límite de impacto, rol de usuario afectado y reproducibilidad.
5. Para objetivos de IA, mapea el comportamiento observado a `gaarm-risk-matrix.md` antes de escribir el lenguaje de severidad o del informe.

## Disciplina de salida

- No presentes un payload, CVE, ID de OWASP o ID de GAARM como verificado a menos que esté respaldado por un archivo de referencia o evidencia en vivo.
- Para informes de SRC, separa el impacto de los pasos de explotación y evita expandirte más allá del alcance autorizado.
- Para writeups de CTF, mantén los pasos de solución reproducibles pero no exageres el impacto en el mundo real a menos que la referencia lo respalde.

## Atribución ascendente (upstream)

Integrado desde `Pa55w0rd/secknowledge-skill`: https://github.com/Pa55w0rd/secknowledge-skill

Autor original (upstream): Pa55w0rd

Versión upstream indicada en el README al momento de la integración: v2.0, 2026-05-18

Declaración de licencia upstream: Licencia MIT

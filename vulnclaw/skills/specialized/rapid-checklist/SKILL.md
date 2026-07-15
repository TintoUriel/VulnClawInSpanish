---
name: rapid-checklist
description: Referencia rápida de pentesting y Payloads — familias rápidas de Payload, recordatorios de bypass, orden de verificación, tarjetas de pruebas comunes, aplicable para búsqueda rápida una vez conocida la dirección de la prueba
---

# Skill de referencia rápida de pentesting y Payload

**Usar solo cuando el enrutamiento ya está claro**. Este Skill es para búsqueda rápida, no sustituye la metodología ni la selección de flujo de trabajo.

## Escenarios de uso

- Recordar rápidamente qué revisar primero para cierto tipo de vulnerabilidad o punto de bloqueo
- Filtrar rápidamente familias de Payload, direcciones de bypass y orden de verificación
- Confirmar rápidamente tarjetas de prueba comunes de AI, MCP, contenedores, WebSocket, JWT, archivos, autenticación, SSRF, etc.
- Pasar de "sé qué necesito probar" a "por cuál categoría de verificación empiezo"

## Escenarios no aplicables

- Sustituir la distribución de escenarios → usar `pentest-flow`
- Sustituir decisiones metodológicas → usar el Skill especializado correspondiente
- Pruebas a ciegas cuando la solicitud no se ha capturado o la reproducción no es estable → usar primero `client-reverse`

## Referencia rápida especializada de CTF

> Para retos de CTF, priorizar los Skills `ctf-web` / `ctf-crypto` / `ctf-misc`, a continuación las tarjetas rápidas:

| Escenario | Ubicación rápida |
|------|---------|
| Comparación débil de PHP → valor MD5 que empieza con 0e | `ctf-web` → `php-bypass-cheatsheet.md` |
| Bypass de espacios en inyección de comandos → ${IFS}/$IFS$9/< | `ctf-web` → `command-injection-bypass.md` |
| eval sin echo → escritura de archivo/exfiltración por DNS | `ctf-web` → `eval-and-rce-techniques.md` |
| Exponente pequeño de RSA → raíz cúbica/Coppersmith | `ctf-crypto` → `rsa-attacks-cheatsheet.md` |
| Python Jail → `__import__`/func_globals | `ctf-misc` → `python-jail-escape.md` |
| Cadena de codificación → base64→hex→ROT13 múltiples capas | `ctf-misc` → `encoding-chain-reference.md` |

## Tarjetas de enrutamiento rápido

### Inyección Web / ejecución de salida
- SQLi → `'`, `"`, `)`, diferencia booleana, diferencia de tiempo, diferencia de error
- XSS → `<script>`, `<img onerror>`, `javascript:`, DOM sink
- Inyección de comandos → `;id`, `|id`, `` `id` ``, `$(id)`
- SSTI → `{{7*7}}`, `${7*7}`, `<%= 7*7 %>`, fingerprinting del motor de plantillas
- XXE → `<!ENTITY>`, entidades de parámetro, exfiltración OOB

### Autenticación / Lógica / Token
- JWT → algoritmo none, manipulación de algoritmo, fuerza bruta de clave, inyección jku/x5u
- CSRF → Token ausente, Token predecible, defecto en validación de Referer
- IDOR → modificación de parámetro ID, enumeración masiva
- Lógica de pagos → manipulación de montos, negativos, condiciones de carrera

### Firma en navegador / anti-scraping
- Usar primero `client-reverse` para reproducción estable
- Fases: locate → recover → runtime → validation

### Estado de ejecución en Android / recuperación de firma
- Usar primero la ruta runtime-first de `client-reverse`
- Recurrir a ingeniería inversa solo cuando no se pueda capturar el paquete/cifrado/reproducir

### AI / MCP
- Inyección de prompt → interferencia directa/indirecta/CoT
- Abuso de herramientas → envenenamiento MCP/sobrescritura de instrucciones
- Escape de identidad → exceso de rol/desviación de permisos

### Intranet / AD
- Usar primero `intranet-pentest-advanced`
- Si hay dudas sobre herramientas, complementar con `pentest-tools`

## Documentación de referencia

- `references/08-rapid-checklists-and-payloads.md` — Referencia integrada de búsqueda rápida y Payload
- `references/testing-methodology.md` — Metodología de pruebas

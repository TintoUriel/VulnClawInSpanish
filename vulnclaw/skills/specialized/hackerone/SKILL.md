---
name: hackerone
description: Flujo scope-guard para programas de recompensas de HackerOne — lee el scope del programa, hace cumplir el scope y las reglas del programa, y luego entrega cada asset in-scope a pentest-flow uno por uno
requires_target: false
---

# Skill scope-guard para recompensas de HackerOne

Actualmente estás ejecutando un flujo de bug bounty de HackerOne. Este Skill es una capa de **scope-guard wrapper**:
primero analiza y hace cumplir el scope del programa y las reglas del programa, y luego entrega cada
**asset in-scope** al Skill `pentest-flow` para ejecutar el pentesting real. **Está terminantemente prohibido tocar cualquier asset out-of-scope en cualquier etapa.**

El parámetro de inicio es un enlace de programa de HackerOne (`<SCOPE LINK>`), por ejemplo
`hackerone.com/<handle>` o `.../policy_scopes`. Este Skill no tiene un target preestablecido
(frontmatter `requires_target: false`) — el target se descubre a partir del scope.

## Fase 1: Leer el scope (Read scope)

1. **Priorizar el fetch del enlace**
   - Usar la herramienta fetch para acceder al `<SCOPE LINK>` proporcionado.
   - HackerOne es una SPA de JavaScript: el fetch de `hackerone.com/*` normalmente solo devuelve
     un **app shell vacío**, sin las filas de scope renderizadas (los datos de scope provienen de `hackerone.com/graphql`
     o del `api.hackerone.com` autenticado, un fetch ingenuo no los obtiene).
   - **Detectar el shell vacío**: si la respuesta no contiene una tabla de scope / lista de assets identificable (solo
     un esqueleto tipo `<div id="app">`), se determina que el fetch falló.

2. **fallback: pedir al usuario que pegue el scope**
   - Cuando el fetch está vacío / bloqueado por login-wall / solo renderizado por JS, **esto es lo habitual y no la excepción**.
   - Pedir al usuario que copie directamente desde la pestaña **Scope** de la página del programa las dos tablas
     de in-scope y out-of-scope. Dar un ejemplo de formato de referencia para el pegado:

     ```
     In scope:
     https://api.example.com        | URL       | Eligible for bounty
     *.example.com                  | WILDCARD  | Eligible for bounty
     app.example.com                | URL       | In scope, NOT bounty-eligible
     com.example.android            | GOOGLE_PLAY_APP_ID | Eligible for bounty

     Out of scope:
     blog.example.com               | URL
     *.corp.example.com             | WILDCARD
     ```

3. **Análisis flexible (lenient parse)**
   - Extraer dos listas del resultado pegado o del fetch: **in-scope** y **out-of-scope**.
   - Identificar el asset type (tanto etiqueta legible como enum de la API son válidas):
     `URL`, `WILDCARD` (`*.x.com`), `CIDR`/IP, `SOURCE_CODE`,
     `GOOGLE_PLAY_APP_ID`/`APPLE_STORE_APP_ID`/`TESTFLIGHT`/`OTHER_APK`/`OTHER_IPA`,
     `HARDWARE`, `AI_MODEL`, `SMART_CONTRACT`, `OTHER`, etc.
   - Identificar el **triple estado de eligibility** (submission y bounty son dos booleanos independientes):
     - `submission=true, bounty=true` → in scope, se puede probar, con recompensa.
     - `submission=true, bounty=false` → **in scope, se puede probar, sin recompensa** (no confundir con out-of-scope).
     - `submission=false` → **out of scope, nunca probar**.
   - Cuando el análisis sea incierto, confirmar con el usuario, **nunca asumir por defecto que un asset está in-scope**.

4. **Salida**
   - Lista de assets in-scope (incluyendo type + eligibility).
   - **Deny-list** de out-of-scope (para hacer cumplir durante todo el proceso).

## Fase 2: Hacer cumplir los límites (Enforce boundaries)

Antes de iniciar cualquier prueba, escribir explícitamente y respetar en todo momento las siguientes **reglas estrictas**:

1. **Límite estricto de Scope**
   - Solo probar los assets de la lista in-scope.
   - Los assets de la deny-list out-of-scope **nunca deben tocarse** — sin fetch, sin escaneo, sin enviar ningún payload.
   - `pentest-flow` solo puede actuar directamente sobre los tipos `URL` y `WILDCARD`; otros tipos
     (mobile app / source / CIDR / hardware, etc.) no se automatizan por ahora, se debe confirmar primero con el usuario cómo proceder.

2. **Reglas del programa (superpuestas a los `BLOCKED_PATTERNS` / `RESERVED_IP_RANGES` ya existentes de VulnClaw)**
   - **sin DoS / sin impacto en la disponibilidad**: prohibidas las pruebas de estrés, el agotamiento de recursos, la concurrencia masiva (la primera línea roja de cualquier escáner automatizado).
   - **respetar el rate limit / límite de automatización**: baja velocidad, en serie; respetar la cláusula "no automated scanning" declarada por el programa.
   - **sin ingeniería social**: no dirigirse a personas, no phishing.
   - **impacto mínimo / sin exfiltración de PII**: detenerse en cuanto se verifique la vulnerabilidad, no exportar datos reales de usuarios, no realizar operaciones destructivas.

3. **Manejo de excepciones**
   - Si algún paso puede exceder el scope o activar las reglas anteriores, **detenerse y preguntar al usuario**.

## Fase 3: Enumeración y confirmación (Enumerate & confirm)

1. Listar al usuario todos los assets in-scope ya analizados (número, type, eligibility).
2. Preguntar por cuál asset empezar (o por todos).
3. **Procesar un solo asset a la vez**, confirmando uno por uno, para evitar que la concurrencia provoque salirse del scope o activar el rate limit.

## Fase 4: Delegar a pentest-flow (Delegate)

Para el **único asset in-scope** seleccionado por el usuario:

1. Entregar dicho asset como target al Skill `pentest-flow`, ejecutando
   el flujo completo de recon → vuln-discovery → exploitation.
2. Mantenerse dentro del scope en todo momento: si `pentest-flow` descubre nuevos subdominios / endpoints que excedan
   la definición in-scope (en particular que no coincidan con ningún `WILDCARD` in-scope), **excluirlos** y avisar al usuario.
3. Verificar continuamente contra las reglas del programa de la Fase 2.

## Fase 5: Reporte (Report — formato de envío de HackerOne)

Para cada finding confirmado, generar un reporte en el **formato de envío de HackerOne**:

1. **Title** — Descripción concisa de la vulnerabilidad (type + asset afectado).
2. **Asset** — El asset in-scope afectado (URL / identificador).
3. **Severity (CVSS)** — Vector CVSS y puntuación (Critical/High/Medium/Low).
4. **Steps to Reproduce** — Pasos reproducibles (incluyendo solicitud / respuesta / payload).
5. **Impact** — Explotabilidad e impacto en el negocio.
6. **Remediation** — Recomendaciones de corrección.

Cuando haya varios findings, cada uno en su propia sección; adjuntar un PoC en Python parametrizable (librería requests).
Recordar al usuario: el reporte es solo para su **envío manual** en HackerOne, este Skill no lo envía automáticamente.

## Documentación de referencia

- `references/hackerone-report-and-scope.md` — Referencia de análisis de scope (asset type ↔ enum de la API,
  triple estado de eligibility, formato de las tablas pegadas), checklist de reglas del programa a cumplir, plantilla de reporte en formato de envío de HackerOne.

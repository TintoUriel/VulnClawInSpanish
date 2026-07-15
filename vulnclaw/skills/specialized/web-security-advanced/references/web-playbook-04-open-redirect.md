# Redirección abierta
English: Open Redirect
- Entry Count: 3
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Redirección abierta básica
- ID: redirect-basic
- Difficulty: beginner
- Subcategory: Básico
- Tags: redirect, url, phishing
- Original Extracted Source: original extracted web-security-wiki source/redirect-basic.md
Description:
Explotación de vulnerabilidad de salto de URL
Prerequisites:
- El parámetro objetivo controla la dirección de salto
Execution Outline:
1. Salto directo
2. Bypass de validación
3. Bypass con barra
## Bypass de redirección
- ID: redirect-bypass
- Difficulty: intermediate
- Subcategory: Bypass
- Tags: redirect, bypass
- Original Extracted Source: original extracted web-security-wiki source/redirect-bypass.md
Description:
Técnicas de bypass para redirección abierta
Prerequisites:
- Existe un parámetro de redirección
Execution Outline:
1. Codificación de URL
2. Símbolo @
3. Barra invertida
## Redirección a SSRF
- ID: redirect-ssrf
- Difficulty: intermediate
- Subcategory: SSRF
- Tags: redirect, ssrf
- Original Extracted Source: original extracted web-security-wiki source/redirect-ssrf.md
Description:
Usar la vulnerabilidad de redirección abierta como trampolín para dirigir el sondeo SSRF hacia la red interna, eludiendo las restricciones de lista blanca/negra de URL del SSRF
Prerequisites:
- El objetivo tiene una vulnerabilidad de redirección abierta (Open Redirect)
- El objetivo tiene un punto funcional de SSRF (parámetro URL/Webhook, etc.)
- El filtro SSRF solo verifica la URL inicial y no sigue la redirección
Execution Outline:
1. Identificar el punto de redirección abierta
2. Eludir el filtro SSRF mediante redirección
3. Uso auxiliar de acortadores de URL y DNS rebinding
4. Cadena de explotación completa: redirección → SSRF → sondeo de red interna
</content>

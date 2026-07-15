# Clickjacking
English: Clickjacking
- Entry Count: 2
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Clickjacking básico
- ID: clickjacking-basic
- Difficulty: beginner
- Subcategory: Básico
- Tags: clickjacking, ui-redressing, iframe
- Original Extracted Source: original extracted web-security-wiki source/clickjacking-basic.md
Description:
Superponer un iframe transparente para engañar al usuario y hacer que, sin saberlo, haga clic en un botón o enlace malicioso oculto
Prerequisites:
- El sitio objetivo permite ser embebido en un iframe
- El objetivo no tiene configurada la cabecera de respuesta X-Frame-Options
- El objetivo no tiene configurada la política CSP frame-ancestors
- Conocimientos básicos de HTML/CSS
Execution Outline:
1. Detectar X-Frame-Options y CSP
2. POC básica de superposición con iframe transparente
3. Secuestro de arrastrar y soltar en varios pasos (Drag-and-Drop)
4. Bypass explotando CSS pointer-events
## Clickjacking + XSS
- ID: clickjacking-xss
- Difficulty: intermediate
- Subcategory: XSS
- Tags: clickjacking, xss
- Original Extracted Source: original extracted web-security-wiki source/clickjacking-xss.md
Description:
Combinar clickjacking con ataques XSS, usando primero el clickjacking para disparar un vector de ataque XSS y obtener un control más profundo
Prerequisites:
- El objetivo tiene una vulnerabilidad XSS
- El objetivo permite ser embebido en un iframe
- El payload XSS puede activarse mediante un clic
Execution Outline:
1. Identificar combinaciones explotables de XSS y Clickjacking
2. Explotación combinada de Self-XSS + Clickjacking
3. Explotación de XSS reflejado + embebido en iframe
</content>

# XSS cross-site scripting
English: XSS Cross-Site Scripting
- Entry Count: 12
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## XSS reflejado
- ID: xss-reflected
- Difficulty: beginner
- Subcategory: Reflejado
- Tags: xss, reflected, javascript
- Original Extracted Source: original extracted web-security-wiki source/xss-reflected.md
Description:
Técnicas de ataque de cross-site scripting reflejado
Prerequisites:
- La entrada del usuario se refleja en la página
- La entrada no está filtrada ni codificada
Execution Outline:
1. 1. Sondear el punto de inyección XSS
2. 2. Bypass mediante manejadores de eventos
3. 3. Bypass mediante etiquetas
4. 4. Robar la cookie
## XSS almacenado
- ID: xss-stored
- Difficulty: intermediate
- Subcategory: Almacenado
- Tags: xss, stored, persistent
- Original Extracted Source: original extracted web-security-wiki source/xss-stored.md
Description:
Técnicas de ataque de cross-site scripting almacenado
Prerequisites:
- Existe una función de almacenamiento de datos
- Los datos almacenados se muestran sin filtrar
Execution Outline:
1. 1. Sondear el punto de almacenamiento
2. 2. Ocultar el payload
3. 3. Control persistente
4. 4. Hook de BeEF
## XSS basado en DOM
- ID: xss-dom
- Difficulty: intermediate
- Subcategory: Basado en DOM
- Tags: xss, dom, javascript
- Original Extracted Source: original extracted web-security-wiki source/xss-dom.md
Description:
Ataque de cross-site scripting basado en el DOM
Prerequisites:
- Existe manipulación dinámica del DOM mediante JavaScript
- La entrada del usuario se escribe directamente en el DOM
Execution Outline:
1. 1. Sondear el XSS de DOM
2. 2. Sinks (puntos de destino) comunes
3. 3. Explotación de location.hash
4. 4. Explotación de postMessage
## Bypass de CSP
- ID: xss-csp-bypass
- Difficulty: advanced
- Subcategory: Bypass de CSP
- Tags: xss, csp, bypass
- Original Extracted Source: original extracted web-security-wiki source/xss-csp-bypass.md
Description:
Técnicas de XSS para eludir la política de seguridad de contenido (CSP)
Prerequisites:
- Existe una vulnerabilidad XSS
- Existe una política CSP pero está mal configurada
Execution Outline:
1. 1. Analizar la política CSP
2. 2. Explotar unsafe-inline
3. 3. Explotar unsafe-eval
4. 4. Bypass mediante JSONP
## XSS por mutación (mXSS)
- ID: xss-mxss
- Difficulty: advanced
- Subcategory: Por mutación
- Tags: xss, mxss, mutation, bypass
- Original Extracted Source: original extracted web-security-wiki source/xss-mxss.md
Description:
Ataque XSS provocado por diferencias en el parseo del navegador
Prerequisites:
- Existe un punto de salida HTML
- Existen diferencias de parseo entre navegadores
Execution Outline:
1. 1. Sondeo básico de mXSS
2. 2. mXSS con SVG
3. 3. mXSS con Math
4. 4. Combinación con DOM clobbering
## XSS con Unicode
- ID: xss-unicode
- Difficulty: intermediate
- Subcategory: Codificación Unicode
- Tags: xss, unicode, encoding, bypass
- Original Extracted Source: original extracted web-security-wiki source/xss-unicode.md
Description:
Uso de características de codificación Unicode para eludir filtros
Prerequisites:
- Existe un punto de inyección XSS
- El filtro verifica palabras clave
Execution Outline:
1. 1. Escape Unicode
2. 2. Codificación de entidades HTML
3. 3. Ataque de normalización Unicode
4. 4. Codificación UTF-7
## Bypass de filtros XSS
- ID: xss-filter-bypass
- Difficulty: intermediate
- Subcategory: Bypass de filtros
- Tags: xss, filter, bypass, waf
- Original Extracted Source: original extracted web-security-wiki source/xss-filter-bypass.md
Description:
Diversas técnicas para eludir filtros de XSS
Prerequisites:
- Existe un punto de inyección XSS
- Existe un mecanismo de filtrado
Execution Outline:
1. 1. Confusión de mayúsculas/minúsculas
2. 2. Bypass por doble escritura
3. 3. Confusión mediante comentarios
4. 4. Truncamiento con byte nulo
## Bypass de codificación XSS
- ID: xss-encoding
- Difficulty: intermediate
- Subcategory: Bypass de codificación
- Tags: xss, encoding, bypass
- Original Extracted Source: original extracted web-security-wiki source/xss-encoding.md
Description:
Uso de diversas técnicas de codificación para eludir filtros de XSS
Prerequisites:
- Existe un punto de inyección XSS
- Existe procesamiento de codificación
Execution Outline:
1. 1. Codificación URL
2. 2. Codificación de entidades HTML
3. 3. Codificación JavaScript
4. 4. Codificación CSS
## XSS Polyglot
- ID: xss-polyglot
- Difficulty: intermediate
- Subcategory: Polyglot
- Tags: xss, polyglot, universal
- Original Extracted Source: original extracted web-security-wiki source/xss-polyglot.md
Description:
Payload de XSS universal, válido en múltiples entornos
Prerequisites:
- Existe un punto de inyección XSS
- No se conoce con certeza el entorno específico
Execution Outline:
1. 1. Polyglot clásico
2. 2. Polyglot corto
3. 3. Polyglot para inyección en atributos
4. 4. Polyglot para parámetros de URL
## Robo de cookies mediante XSS
- ID: xss-cookie-theft
- Difficulty: beginner
- Subcategory: Robo de cookies
- Tags: xss, cookie, theft, session
- Original Extracted Source: original extracted web-security-wiki source/xss-cookie-theft.md
Description:
Uso de XSS para robar la cookie del usuario
Prerequisites:
- Existe una vulnerabilidad XSS
- La cookie no tiene configurado HttpOnly
Execution Outline:
1. 1. Robo básico de cookies
2. 2. Robo mediante Fetch API
3. 3. Robo mediante XMLHttpRequest
4. 4. Transmisión codificada
## Registro de teclado mediante XSS
- ID: xss-keylogger
- Difficulty: intermediate
- Subcategory: Registro de teclado
- Tags: xss, keylogger, credential
- Original Extracted Source: original extracted web-security-wiki source/xss-keylogger.md
Description:
Uso de XSS para registrar la entrada de teclado del usuario
Prerequisites:
- Existe un XSS almacenado
- La página objetivo tiene campos de entrada sensibles
Execution Outline:
1. 1. Registro básico de teclado
2. 2. Registro completo de teclado
3. 3. Robo de formularios
4. 4. Secuestro del envío de formularios
## Explotación con el framework BeEF
- ID: xss-beef
- Difficulty: advanced
- Subcategory: Explotación con BeEF
- Tags: xss, beef, framework, exploitation
- Original Extracted Source: original extracted web-security-wiki source/xss-beef.md
Description:
Uso del framework BeEF para la explotación de XSS
Prerequisites:
- Existe una vulnerabilidad XSS
- Se ha desplegado un servidor BeEF
Execution Outline:
1. 1. Desplegar BeEF
2. 2. Inyectar el script Hook
3. 3. Comandos habituales
4. 4. Explotación de módulos

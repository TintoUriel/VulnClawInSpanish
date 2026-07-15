# CSRF falsificación de solicitud entre sitios
English: CSRF Cross-Site Request Forgery
- Entry Count: 8
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Ataque básico de CSRF
- ID: csrf-basic
- Difficulty: beginner
- Subcategory: Ataque básico
- Tags: csrf, cross-site, request, forgery
- Original Extracted Source: original extracted web-security-wiki source/csrf-basic.md
Description:
Técnicas básicas de ataque de falsificación de solicitud entre sitios
Prerequisites:
- El objetivo tiene operaciones sensibles
- Falta protección CSRF
Execution Outline:
1. 1. Construir el formulario CSRF
2. 2. CSRF mediante solicitud GET
3. 3. CSRF con JSON
4. 4. Inducción mediante enlace
## Ataque de CSRF con JSON
- ID: csrf-json
- Difficulty: intermediate
- Subcategory: JSON CSRF
- Tags: csrf, json, api, post
- Original Extracted Source: original extracted web-security-wiki source/csrf-json.md
Description:
Técnicas de ataque CSRF dirigidas a solicitudes en formato JSON
Prerequisites:
- El objetivo usa solicitudes en formato JSON
- Falta protección CSRF
- Configuración CORS inadecuada
Execution Outline:
1. 1. CSRF JSON simple
2. 2. CSRF JSON con Flash
3. 3. Ataque XSSI
4. 4. Ataque con archivo SWF
## Técnicas de bypass de CSRF
- ID: csrf-bypass
- Difficulty: intermediate
- Subcategory: Técnicas de bypass
- Tags: csrf, bypass, token, referer
- Original Extracted Source: original extracted web-security-wiki source/csrf-bypass.md
Description:
Diversas técnicas para eludir la protección CSRF
Prerequisites:
- El objetivo tiene protección CSRF
- El mecanismo de protección tiene defectos
Execution Outline:
1. 1. Bypass de la validación de Token
2. 2. Bypass de la validación de Referer
3. 3. Bypass de la validación de Origin
4. 4. Bypass de SameSite
## Técnicas de bypass de SameSite
- ID: csrf-samesite
- Difficulty: intermediate
- Subcategory: Bypass de SameSite
- Tags: csrf, samesite, cookie, bypass
- Original Extracted Source: original extracted web-security-wiki source/csrf-samesite.md
Description:
Ataque CSRF que elude el atributo SameSite de las cookies
Prerequisites:
- La cookie tiene configurado el atributo SameSite
- La configuración de SameSite tiene defectos
Execution Outline:
1. 1. Bypass de SameSite=Lax
2. 2. Bypass de SameSite=Strict
3. 3. SameSite no configurado
4. 4. Explotación del flujo OAuth
## Técnicas de bypass de Token
- ID: csrf-token-bypass
- Difficulty: intermediate
- Subcategory: Bypass de Token
- Tags: csrf, token, bypass, predictable
- Original Extracted Source: original extracted web-security-wiki source/csrf-token-bypass.md
Description:
Técnicas para eludir la validación del Token CSRF
Prerequisites:
- El objetivo usa un Token CSRF
- El mecanismo de Token tiene defectos
Execution Outline:
1. 1. Token predecible
2. 2. Token no vinculado a la sesión
3. 3. Fuga del Token
4. 4. Repetición del Token
## Técnicas de bypass de Referer
- ID: csrf-referer-bypass
- Difficulty: intermediate
- Subcategory: Bypass de Referer
- Tags: csrf, referer, bypass, header
- Original Extracted Source: original extracted web-security-wiki source/csrf-referer-bypass.md
Description:
Ataque CSRF que elude la validación de la cabecera Referer
Prerequisites:
- El objetivo valida la cabecera Referer
- La lógica de validación tiene defectos
Execution Outline:
1. 1. Bypass mediante coincidencia de expresión regular
2. 2. Bypass con Referer vacío
3. 3. Bypass mediante subdominio
4. 4. Explotación de Referrer-Policy
## Ataque de CSRF con Flash
- ID: csrf-flash
- Difficulty: advanced
- Subcategory: Flash CSRF
- Tags: csrf, flash, swf, crossdomain
- Original Extracted Source: original extracted web-security-wiki source/csrf-flash.md
Description:
Realiza un ataque CSRF utilizando Flash
Prerequisites:
- El objetivo permite solicitudes de Flash
- Configuración inadecuada de crossdomain.xml
Execution Outline:
1. 1. Explotación de crossdomain.xml
2. 2. Creación de un SWF malicioso
3. 3. Envío de solicitud JSON
4. 4. Cabecera personalizada
## Explotación de configuración incorrecta de CORS
- ID: csrf-cors
- Difficulty: intermediate
- Subcategory: Configuración incorrecta de CORS
- Tags: csrf, cors, misconfiguration, api
- Original Extracted Source: original extracted web-security-wiki source/csrf-cors.md
Description:
Realiza un ataque CSRF explotando una configuración incorrecta de CORS
Prerequisites:
- Configuración incorrecta de CORS
- Se permite el envío de credenciales entre dominios
Execution Outline:
1. 1. Detectar la configuración de CORS
2. 2. Ataque de reflexión de Origin
3. 3. Ataque de origen null
4. 4. Bypass mediante expresión regular
</content>

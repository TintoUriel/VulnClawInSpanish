# Vulnerabilidades de autenticación
English: Authentication Vulnerabilities
- Entry Count: 10
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Bypass de autenticación
- ID: auth-bypass
- Difficulty: intermediate
- Subcategory: Bypass de autenticación
- Tags: auth, bypass, authentication
- Original Extracted Source: original extracted web-security-wiki source/auth-bypass.md
Description:
Técnicas de bypass de autenticación en aplicaciones web
Prerequisites:
- El objetivo tiene un mecanismo de autenticación
- La implementación de la autenticación tiene defectos
Execution Outline:
1. Bypass mediante inyección SQL
2. Bypass mediante array
3. Conversión de tipos
4. Bypass mediante JSON
## Fuerza bruta
- ID: auth-brute
- Difficulty: beginner
- Subcategory: Fuerza bruta
- Tags: auth, brute-force, password
- Original Extracted Source: original extracted web-security-wiki source/auth-brute.md
Description:
Ataque automatizado de adivinación de contraseñas
Prerequisites:
- Sin CAPTCHA
- Sin política de bloqueo
Execution Outline:
1. Pitchfork
2. Cluster bomb
3. Enumeración de nombres de usuario basada en diferencias de respuesta
4. Fuerza bruta y bypass de código de verificación/OTP
## Secuestro de sesión
- ID: auth-session
- Difficulty: intermediate
- Subcategory: Gestión de sesión
- Tags: auth, session, hijack
- Original Extracted Source: original extracted web-security-wiki source/auth-session.md
Description:
Explota defectos en la gestión de sesión para secuestrar o falsificar la sesión del usuario y obtener acceso no autorizado
Prerequisites:
- El objetivo usa gestión de sesión basada en Cookie o Token
- Es posible interceptar o predecir el identificador de sesión
- La comunicación de red no está completamente cifrada (HTTP) o existe XSS
Execution Outline:
1. Análisis de atributos de la cookie de sesión
2. Ataque de fijación de sesión (Session Fixation)
3. Secuestro de sesión (sniffing HTTP)
4. Predicción de sesión (aleatoriedad débil)
## Vulnerabilidad de restablecimiento de contraseña
- ID: auth-password-reset
- Difficulty: intermediate
- Subcategory: Vulnerabilidad lógica
- Tags: auth, password-reset, logic
- Original Extracted Source: original extracted web-security-wiki source/auth-password-reset.md
Description:
Elude el flujo de restablecimiento de contraseña
Prerequisites:
- La funcionalidad de restablecimiento de contraseña tiene un defecto lógico
Execution Outline:
1. Envenenamiento de la cabecera Host
2. Fuerza bruta del Token
3. Análisis de la predictibilidad del Token de restablecimiento de contraseña
4. Defecto lógico en el flujo de restablecimiento de contraseña
## Vulnerabilidad de OAuth
- ID: auth-oauth
- Difficulty: advanced
- Subcategory: OAuth
- Tags: auth, oauth, redirect
- Original Extracted Source: original extracted web-security-wiki source/auth-oauth.md
Description:
Vulnerabilidades en el flujo de autenticación OAuth
Prerequisites:
- Se usa inicio de sesión con OAuth
Execution Outline:
1. Ataque CSRF
2. Redirect URI
3. Ausencia/predictibilidad del parámetro State de OAuth (CSRF)
4. Robo de Token y control de acceso indebido de Scope
## Vulnerabilidad de SAML
- ID: auth-saml
- Difficulty: advanced
- Subcategory: SAML
- Tags: auth, saml, xml
- Original Extracted Source: original extracted web-security-wiki source/auth-saml.md
Description:
Ataque contra aserciones SAML
Prerequisites:
- Se usa SAML SSO
Execution Outline:
1. Bypass de firma XML
2. Ataque XXE
3. Manipulación y repetición de SAML Response
4. Técnicas avanzadas de bypass de firma SAML
## Bypass de 2FA
- ID: auth-2fa
- Difficulty: intermediate
- Subcategory: 2FA
- Tags: auth, 2fa, mfa
- Original Extracted Source: original extracted web-security-wiki source/auth-2fa.md
Description:
Elude la autenticación de dos factores
Prerequisites:
- 2FA está activado
Execution Outline:
1. Acceso directo
2. Fuerza bruta del código de verificación
3. Bypass lógico
## Bypass de CAPTCHA
- ID: auth-captcha
- Difficulty: beginner
- Subcategory: CAPTCHA
- Tags: auth, captcha, bypass
- Original Extracted Source: original extracted web-security-wiki source/auth-captcha.md
Description:
Elude el CAPTCHA gráfico
Prerequisites:
- Existe CAPTCHA
Execution Outline:
1. Reutilización
2. Bypass con valor vacío
3. Eliminación del parámetro
## Vulnerabilidad de "Recordarme"
- ID: auth-remember-me
- Difficulty: intermediate
- Subcategory: Gestión de sesión
- Tags: auth, remember-me, cookie
- Original Extracted Source: original extracted web-security-wiki source/auth-remember-me.md
Description:
Vulnerabilidad de la funcionalidad Remember Me
Prerequisites:
- Remember Me está activado
Execution Outline:
1. Falsificación de cookie
2. Decodificación Base64
3. Análisis inverso del Token de contraseña recordada
4. RCE por deserialización de Shiro RememberMe
## Vulnerabilidad de autenticación JWT
- ID: auth-jwt
- Difficulty: intermediate
- Subcategory: JWT
- Tags: auth, jwt, token
- Original Extracted Source: original extracted web-security-wiki source/auth-jwt.md
Description:
Explota defectos de implementación de JWT (JSON Web Token) para falsificar o manipular el token de autenticación, logrando acceso no autorizado o escalada de privilegios
Prerequisites:
- El objetivo usa JWT para autenticación
- Es posible obtener o interceptar el token JWT
- La biblioteca JWT tiene vulnerabilidades conocidas o la configuración del servidor es inadecuada
Execution Outline:
1. Decodificación y análisis de JWT
2. Ataque de algoritmo None
3. Fuerza bruta de la clave HS256
4. Ataque de confusión de algoritmo RS256→HS256
</content>

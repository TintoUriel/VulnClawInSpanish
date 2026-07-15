# Seguridad de JWT
English: JWT Security
- Entry Count: 4
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Ataque del algoritmo None en JWT
- ID: jwt-none-attack
- Difficulty: beginner
- Subcategory: Ataque de algoritmo
- Tags: JWT, algoritmo none, bypass de autenticación, falsificación de token, CVE-2015-2951
- Original Extracted Source: original extracted web-security-wiki source/jwt-none-attack.md
Description:
Explota el defecto de soporte de algunas bibliotecas JWT para el algoritmo "none", modificando el algoritmo de firma en la cabecera del JWT a none y eliminando la parte de la firma, para construir un token falsificado que pasa la validación sin necesidad de clave. Es una de las vulnerabilidades JWT más clásicas.
Prerequisites:
- El objetivo usa JWT para la autenticación
- jwt_tool o la biblioteca Python PyJWT
Execution Outline:
1. 1. Decodificar el JWT existente
2. 2. Construir un JWT con algoritmo None
3. 3. Ataque automatizado con jwt_tool
4. 4. Verificar el token falsificado
## Ataque de confusión de clave en JWT (RS→HS)
- ID: jwt-key-confusion
- Difficulty: advanced
- Subcategory: Ataque de algoritmo
- Tags: JWT, confusión de clave, RS256, HS256, manipulación de algoritmo
- Original Extracted Source: original extracted web-security-wiki source/jwt-key-confusion.md
Description:
Cuando el servidor usa una clave pública RSA para validar el JWT, el atacante cambia el algoritmo de RS256 a HS256; en ese caso, el servidor usará erróneamente la clave pública RSA como clave HMAC para la validación. Dado que la clave pública RSA es de acceso público, el atacante puede usarla para firmar cualquier JWT.
Prerequisites:
- El JWT objetivo usa algoritmo RS256/RS384/RS512
- Se ha obtenido la clave pública RSA
- jwt_tool o Python
Execution Outline:
1. 1. Obtener la clave pública RSA
2. 2. Ataque de confusión de clave
3. 3. Ataque automatizado con jwt_tool
4. 4. Inyección en el endpoint JWKS
## Fuerza bruta de la clave secreta de JWT
- ID: jwt-secret-bruteforce
- Difficulty: intermediate
- Subcategory: Descifrado de clave
- Tags: JWT, fuerza bruta de clave, HS256, clave débil, hashcat
- Original Extracted Source: original extracted web-security-wiki source/jwt-secret-bruteforce.md
Description:
Cuando el JWT usa un algoritmo simétrico HMAC (HS256/HS384/HS512) y la clave es débil, es posible recuperar la clave de firma mediante ataque de diccionario o fuerza bruta, y así falsificar cualquier token JWT.
Prerequisites:
- El JWT objetivo usa algoritmo HMAC (HS256, etc.)
- Se ha obtenido una muestra de JWT válido
- hashcat o jwt_tool
Execution Outline:
1. 1. Confirmar el algoritmo y la estructura
2. 2. Fuerza bruta acelerada por GPU con hashcat
3. 3. Fuerza bruta por diccionario con jwt_tool
4. 4. Falsificar el JWT usando la clave descifrada
## Inyección de cabecera JKU/X5U en JWT
- ID: jwt-jku-x5u-injection
- Difficulty: advanced
- Subcategory: Inyección de Header
- Tags: JWT, JKU, X5U, inyección de Header, JWKS, secuestro de clave
- Original Extracted Source: original extracted web-security-wiki source/jwt-jku-x5u-injection.md
Description:
Explota los parámetros jku (JWK Set URL) o x5u (X.509 URL) en la cabecera del JWT, apuntando el origen de la clave hacia un servidor controlado por el atacante, de modo que el servidor use la clave pública del atacante para validar el JWT, logrando así la falsificación del token.
Prerequisites:
- El JWT objetivo soporta los parámetros de Header jku/x5u
- El atacante dispone de un servidor con acceso público
- Entorno Python
Execution Outline:
1. 1. Sondear el soporte de JKU/X5U
2. 2. Generar el par de claves del atacante
3. 3. Alojar el JWKS y firmar el JWT
4. 4. Verificar el ataque
</content>

# Técnicas de ataque criptográfico

## 1. Ataques a hashes

### Consulta en rainbow tables
- crackstation.net — gratuito, soporta MD5/SHA1/SHA256
- cmd5.com — en chino, cobertura amplia
- hashes.org — mantenido por la comunidad

### Ataque de extensión de longitud de hash
- Aplicable a: MD5, SHA1, SHA256 y otros hashes basados en Merkle-Damgård
- Condición: se conoce `H(message)` y `len(message)`, pero no el mensaje en sí
- Herramientas: hashpump, hash_extender
- Escenario: bypass de verificación de firmas en API

### Colisión de hashes
- MD5: fastcoll, HashClash
- SHA1: SHAttered (viable en teoría)
- Escenario: bypass de integridad de archivos, falsificación de certificados

## 2. Ataques a cifrado simétrico

### Ataque al modo ECB
- Mismo bloque de texto plano → mismo bloque de texto cifrado
- Se puede reordenar el texto plano reordenando los bloques de texto cifrado
- Permite identificar patrones repetidos (por ejemplo, el campo de rol de usuario)

### Ataque de volteo de bits en CBC (byte flipping)
- Modificar el IV o el bloque de texto cifrado anterior permite voltear el byte correspondiente del siguiente bloque de texto plano
- Fórmula: `P[i] = D(C[i]) XOR C[i-1]`
- Modificar `C[i-1][j]` → voltea `P[i][j]`
- Escenario: modificar el ID de usuario o el campo de rol cifrados

### Ataque Padding Oracle
- Condición: el servidor indica si el padding es correcto o no
- Recupera el texto plano byte a byte, sin necesidad de la clave
- Herramientas: padbuster, padding-oracle-attacker
- Escenario: tokens serializados de ASP.NET, Java

### Reutilización de IV
- En modo CBC, mismo IV + misma clave → filtración de información
- Permite inferir si los textos planos son iguales

## 3. Ataques a RSA

### Ataque de exponente público pequeño
- Con e=3, si el texto plano m^3 < n, se puede recuperar directamente mediante raíz cúbica
- Ataque de difusión con exponente de cifrado bajo: mismo texto plano cifrado con el mismo e pero distinto n

### Ataque de módulo común
- Mismo texto plano cifrado con el mismo n pero distinto e
- Se recupera el texto plano mediante el algoritmo extendido de Euclides

### Ataque de Wiener
- Con d < n^0.25 se puede factorizar n
- Aplicable a escenarios con exponente privado pequeño

### Factorización de Fermat
- Cuando p y q son cercanos, n se puede factorizar rápidamente
- Aplicable a generación de claves débil

### Archivo de clave conocido
- Extraer los parámetros de archivos .pem/.der
- openssl rsa -text -noout -in key.pem

## 4. Ataques a cifrados clásicos

### Fuerza bruta sobre Caesar
- Solo 25 posibilidades, recorrerlas directamente
- Combinar con análisis de frecuencias para elegir el resultado más probable

### Análisis de Vigenère
- Prueba de Kasiski para determinar la longitud de la clave
- Método del índice de coincidencia para verificar la longitud de la clave
- Una vez determinada la longitud, romper cada columna como un Caesar

### Cifrado de transposición en columnas (rail fence)
- Número de columnas común: 2-8
- Recorrer todos los números de columnas posibles
- Comprobar si el resultado tiene sentido

### Cifrado de Bacon
- Dos tipos de fuente/estilo → codificación A/B
- Decodificar una letra cada 5 caracteres

## 5. Ataques a JWT

### Bypass del algoritmo none
```json
{"alg": "none", "typ": "JWT"}
```
- Cambiar el algoritmo a none
- Eliminar la parte de la firma
- Algunas implementaciones aceptan tokens sin firma

### Confusión de algoritmo RS256 → HS256
- Cambiar el algoritmo de RS256 a HS256
- Usar la clave pública como clave HMAC para firmar
- Si el servidor verifica la firma HS256 con la clave pública → bypass

### Fuerza bruta de clave débil
- jwt-tool, jwt-cracker
- Claves débiles comunes: secret, password, 123456, etc.

### Inyección de JWK / jku
- Incrustar la clave pública en el Header (campo jwk)
- O apuntar a una URL jku controlada por el atacante
- Si el servidor confía en la clave del Header → falsificación

## 6. Patrones de ataque de cadenas de codificación

### Codificación para bypass de WAF
- Doble codificación URL: `%2527` → `%27` → `'`
- Normalización Unicode: `％27` → `'` (ancho completo a ancho medio)
- Entidad HTML: `&#39;` → `'`
- Inyección de parámetros codificados en Base64

### Codificación en deserialización
- PHP: objeto serializado codificado en base64
- Java: flujo de bytes serializado codificado en Base64
- Python: payloads pickle en base64

## 7. Chuleta de herramientas

| Escenario | Herramienta |
|------|------|
| Codificación/decodificación general | CyberChef |
| Ruptura de hashes | hashcat, john |
| Análisis de RSA | RsaCtfTool |
| Análisis de JWT | jwt-tool |
| Padding Oracle | padbuster |
| Extensión de hash | hashpump |
| Decodificación online | base64decode.org, cyberchef.org |

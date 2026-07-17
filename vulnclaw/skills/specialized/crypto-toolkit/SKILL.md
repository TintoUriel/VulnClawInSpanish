---
name: crypto-toolkit
description: Herramientas de codificación/decodificación y cifrado/descifrado — codificación/decodificación base64/URL/Hex/entidades HTML, hashes MD5/SHA, cifrado/descifrado AES/DES/RSA, análisis de JWT, cifrados Caesar/ROT13, cifrados de transposición en columnas/Vigenère, escape Unicode, código Morse, etc.
---

# Skill de codificación/decodificación y cifrado/descifrado

Ofrece capacidades integrales de codificación/decodificación y cifrado/descifrado para los escenarios de codificación, cifrado y ofuscación más comunes en pentesting.
**Importante**: ante cualquier cadena codificada/cifrada, usa primero la herramienta `crypto_decode` para decodificarla, en lugar de adivinar por intuición.

## Principios fundamentales

1. **Herramienta primero** — ante cadenas en base64, hex, codificación URL, etc., invoca la herramienta `crypto_decode` para decodificarlas; no las infieras manualmente
2. **Probar múltiples formatos** — si el resultado de una decodificación no es razonable, prueba otros formatos de codificación
3. **Decodificación en cadena** — en CTF es común encontrar codificación en múltiples capas (por ejemplo, base64→hex→ROT13); tras decodificar, revisa si el resultado necesita otra pasada de decodificación
4. **Verificar el resultado** — tras decodificar, verifica que el resultado sea razonable (si es texto legible, si parece una ruta/URL/flag, etc.)

## 1. Identificación y decodificación de codificaciones

### Identificación de características de codificaciones comunes

| Tipo de codificación | Característica | Ejemplo |
|---------|------|------|
| Base64 | `A-Za-z0-9+/=`, suele terminar con relleno `=` | `TnNTY1RmLnBocA==` |
| Base32 | `A-Z2-7=` | `OBZHK5DFN2A====` |
| Hex | `0-9a-f`, longitud par | `4e73536354662e706870` |
| Codificación URL | Formato `%XX` | `%2F%61%64%6D%69%6E` |
| Entidad HTML | `&#xNN;` o `&#NNN;` | `&#x3C;script&#x3E;` |
| Escape Unicode | `\uXXXX` o `\UXXXXXXXX` | `\u003c\u0073\u0063` |
| JWT | base64 con tres segmentos separados por `.` | `eyJhbG...` |

### Estrategia de decodificación

1. Identificar el tipo de codificación → invocar la herramienta `crypto_decode` especificando la operación correspondiente
2. Comprobar si el resultado decodificado es legible/razonable
3. Si no lo es, probar otro formato de codificación
4. Si el resultado sigue pareciendo codificado, repetir los pasos 1-3

## 2. Hashes y funciones resumen

### Tipos de hash comunes

| Tipo | Longitud de salida | Característica |
|------|---------|------|
| MD5 | 32 hex | `e10adc3949ba59abbe56e057f20f883e` |
| SHA1 | 40 hex | `aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d` |
| SHA256 | 64 hex | `2c26b46b68ffc68ff99b453c1d30413413422d7064...` |
| SHA512 | 128 hex | Cadena hex más larga |
| NTLM | 32 hex | Hash de Windows |
| MySQL5 | 41 caracteres | `*E6CC90B878B948C35E92B003C792C46758BF4` |

### Estrategia de procesamiento de hashes

- Identificar el tipo de hash (por longitud y conjunto de caracteres)
- Probar consultas en rainbow tables online (mediante la herramienta fetch, accediendo a servicios como crackstation)
- Para hashes con salt conocido, probar fuerza bruta con el salt correspondiente

## 3. Cifrado simétrico

### AES/DES/3DES

- Requiere clave y modo (ECB/CBC/CTR, etc.)
- El modo CBC requiere IV
- Rellenos (padding) comunes: PKCS7/ZeroPadding
- En pentesting es frecuente encontrar claves embebidas en el código; extráelas del código fuente cuando sea posible

## 4. Cifrado asimétrico

### RSA

- Extraer los parámetros de los archivos de clave pública/privada
- Un RSA con módulo demasiado pequeño puede factorizarse
- Si se conoce la clave privada, se puede descifrar directamente

## 5. Cifrados clásicos

| Tipo | Característica | Método de ruptura |
|------|------|---------|
| Caesar/ROT13 | Desplazamiento de letras | Fuerza bruta con los 25 desplazamientos |
| Vigenère | Sustitución polialfabética | Kasiski/análisis de frecuencias |
| Cifrado de transposición en columnas (rail fence) | Reagrupación de caracteres | Probar números de columnas comunes |
| Cifrado de Bacon | Quíntuplas AB | Consulta en tabla |
| Morse | Puntos y rayas `.-` | Consulta en tabla |

## 6. Procesamiento de JWT

- Decodificar Header + Payload (base64url)
- Revisar el algoritmo: bypass del algoritmo `none`, confusión de algoritmo RS256→HS256
- Probar falsificación de firma con clave débil
- Revisar las declaraciones temporales exp/nbf, etc.

## Uso de la herramienta

### Herramienta `crypto_decode`

Cuando se necesite realizar una operación de codificación/decodificación/cifrado/descifrado, invoca esta herramienta:

```
crypto_decode(operation="base64_decode", input="TnNTY1RmLnBocA==")
```

Lista de operaciones soportadas:
- **Codificación**: `base64_encode`, `base32_encode`, `hex_encode`, `url_encode`, `html_encode`, `unicode_encode`, `rot13_encode`, `morse_encode`, `caesar_encode`, `base58_encode`
- **Decodificación**: `base64_decode`, `base32_decode`, `hex_decode`, `url_decode`, `html_decode`, `unicode_decode`, `rot13_decode`, `morse_decode`, `caesar_decode`, `base58_decode`
- **Hash**: `md5_hash`, `sha1_hash`, `sha256_hash`, `sha512_hash`
- **Cifrado/descifrado**: `aes_encrypt`, `aes_decrypt`, `des_encrypt`, `des_decrypt`, `rsa_encrypt`, `rsa_decrypt`
- **JWT**: `jwt_decode`, `jwt_encode`
- **Identificación automática**: `auto_decode` (identifica automáticamente el tipo de codificación y decodifica)

## Enrutamiento de ataques criptográficos de CTF

> Ante un escenario de ataque criptográfico (algoritmo de cifrado conocido, se necesita recuperar el texto plano o la clave), usa preferentemente el Skill `ctf-crypto`:

| Escenario de ataque | Enrutar a ctf-crypto | Documento de referencia |
|---------|-----------------|---------|
| RSA exponente pequeño/módulo común/Wiener | `ctf-crypto` | `references/rsa-attacks-cheatsheet.md` |
| AES Padding Oracle/volteo de bits en ECB | `ctf-crypto` | `references/aes-and-block-cipher-attacks.md` |
| ECC subgrupo pequeño/logaritmo discreto | `ctf-crypto` | `references/ecc-attacks-cheatsheet.md` |
| Predicción de PRNG/MT19937 | `ctf-crypto` | `references/prng-and-stream-cipher-attacks.md` |
| Cifrados clásicos (Vigenère/XOR) | `ctf-crypto` | `references/classic-cipher-attacks.md` |
| Ataques de retículos (lattice)/LWE | `ctf-crypto` | `references/lattice-and-lwe-attacks.md` |

**Este Skill se centra en las herramientas de codificación/decodificación**; para los métodos y parámetros concretos de ataques criptográficos, consulta `ctf-crypto`.

## Documentos de referencia

- `references/encoding-cheatsheet.md` — Chuleta de identificación de codificaciones
- `references/crypto-attacks.md` — Técnicas de ataque criptográfico
- `references/crypto-attacks-roadmap.md` — Enrutamiento de clasificación de ataques criptográficos (elegir el método de ataque según las características del reto)

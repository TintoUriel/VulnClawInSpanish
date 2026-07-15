---
name: ctf-crypto
description: Base de conocimiento de ataques criptográficos para CTF — ataques RSA (exponente pequeño/módulo común/Wiener/Coppersmith), ataques AES (Padding Oracle/volteo de bytes ECB/reutilización de nonce en GCM), ataques ECC, ataques LFSR/LCG/PRNG, cifrados clásicos, ataques de retículos LWE
routing:
  target_types: [ctf, crypto]
  task_types: [ctf, crypto]
---

# Base de conocimiento de ataques criptográficos para CTF

Base de conocimiento de ataques prácticos para retos de CTF Crypto, que proporciona **parámetros de ataque concretos, fórmulas matemáticas y fragmentos de código Python**.

**Diferencia con `crypto-toolkit`**:
- `crypto-toolkit` → herramientas de operaciones de codificación/decodificación (decodificación base64, hash MD5, cifrado/descifrado AES)
- `ctf-crypto` → conocimiento de ataques criptográficos (cómo realizar un ataque de exponente pequeño en RSA, cómo explotar un Padding Oracle)

## Principios fundamentales

1. **Identificar primero el sistema criptográfico** — observar la longitud de la clave, el modo de cifrado y las cantidades conocidas para determinar la dirección del ataque
2. **Verificación con herramientas** — usar `python_execute` para ejecutar código de ataque, y `crypto_decode` como apoyo de codificación/decodificación
3. **Sensibilidad a los parámetros** — los ataques criptográficos son extremadamente sensibles a los parámetros, deben calcularse con precisión

## Enrutamiento de escenarios

| Escenario | Documento de referencia | Ataques principales |
|------|---------|---------|
| Ataques RSA | `rsa-attacks-cheatsheet.md` | e pequeño/módulo común/Wiener/Pollard/Fermat/Coppersmith |
| Ataques AES/cifrado por bloques | `aes-and-block-cipher-attacks.md` | Volteo ECB/Padding Oracle/reutilización de nonce en GCM |
| Ataques ECC | `ecc-attacks-cheatsheet.md` | Subgrupo pequeño/curva inválida/Smart/Pohlig-Hellman |
| Ataques PRNG/cifrado de flujo | `prng-and-stream-cipher-attacks.md` | MT19937/LCG/LFSR/RC4 |
| Cifrados clásicos | `classic-cipher-attacks.md` | Vigenère/análisis de frecuencia XOR/reutilización de OTP |
| Ataques de retículos | `lattice-and-lwe-attacks.md` | LLL/BKZ/HNP/embedding LWE |

## Guía rápida de identificación

| Característica del reto | Ataque probable | Referencia recomendada |
|---------|---------|---------|
| Se dan n, e, c | RSA | rsa-attacks-cheatsheet.md |
| e=3 o e muy pequeño | Ataque de exponente pequeño RSA | rsa-attacks-cheatsheet.md |
| Varios grupos (n, e, c) con el mismo n | Ataque de módulo común RSA | rsa-attacks-cheatsheet.md |
| n muy grande pero e muy grande | Ataque de Wiener | rsa-attacks-cheatsheet.md |
| AES-CBC + oracle de descifrado | Padding Oracle | aes-and-block-cipher-attacks.md |
| AES-ECB + texto plano controlable | Volteo de bytes ECB | aes-and-block-cipher-attacks.md |
| Parámetros de curva elíptica | Ataques ECC | ecc-attacks-cheatsheet.md |
| Se da una secuencia de números aleatorios | Predicción de PRNG | prng-and-stream-cipher-attacks.md |
| Se dan el criptograma y parte del texto plano | XOR/cifrado de flujo | classic-cipher-attacks.md |
| Operaciones con matrices/vectores | Ataques de retículos | lattice-and-lwe-attacks.md |

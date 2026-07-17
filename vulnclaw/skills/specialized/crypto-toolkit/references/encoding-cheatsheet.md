# Chuleta de identificación de codificaciones

## Flujo de identificación rápida

```
Cadena de entrada
  ├─ Contiene %XX → codificación URL → url_decode
  ├─ Contiene &# o &#x → entidad HTML → html_decode
  ├─ Contiene \uXXXX → escape Unicode → unicode_decode
  ├─ Contiene .- y solo puntos/rayas/espacios → Morse → morse_decode
  ├─ Tres segmentos base64 unidos por . → JWT → jwt_decode
  ├─ Relleno = al final + A-Za-z0-9+/ → Base64 → base64_decode
  ├─ Relleno = al final + A-Z2-7 → Base32 → base32_decode
  ├─ Solo caracteres hex (0-9a-f), longitud par → Hex → hex_decode
  ├─ Solo mayúsculas + números, sin relleno → posible Base58 → base58_decode
  ├─ Patrón de desplazamiento de letras (p. ej. E→M, A→I) → Caesar → caesar_decode
  └─ No se puede determinar → auto_decode
```

## Variantes de Base64

| Variante | Conjunto de caracteres | Uso |
|------|--------|------|
| Base64 estándar | `A-Za-z0-9+/=` | General |
| Base64 URL-safe | `A-Za-z0-9-_` | Parámetros URL |
| Base64url (JWT) | `A-Za-z0-9_-` sin relleno | JWT |

## Base58

| Variante | Caracteres excluidos | Uso |
|------|---------|------|
| Bitcoin | `0OIl` | Codificación de direcciones |
| Flickr | `0OIl` | URLs cortas |
| Ripple | `0OIl` | Codificación de direcciones |

## Patrones de ofuscación comunes

### Doble codificación
```
Original: admin
→ Codificación URL: %61%64%6D%69%6E
→ Doble codificación URL: %2561%2564%256D%2569%256E
```

### Cadena Base64 + Hex
```
Original: NsScTf.php
→ Hex: 4e73536354662e706870
→ Base64: TnNTY1RmLnBocA==
```

### ROT13 anidado
```
Original: password
→ ROT13: cnffjbeq
→ ROT13 de nuevo: password (ROT13 es autoinverso)
```

## Correspondencia entre longitudes y codificaciones

| Longitud del original | Longitud Base64 | Longitud Hex | Longitud Base32 |
|---------|------------|---------|------------|
| 1 byte | 4 caracteres | 2 caracteres | 8 caracteres |
| 4 bytes | 8 caracteres | 8 caracteres | 8 caracteres |
| 8 bytes | 12 caracteres | 16 caracteres | 16 caracteres |
| 16 bytes | 24 caracteres | 32 caracteres | 28 caracteres |

## Cadenas de codificación comunes en CTF

1. **Base64 → texto plano** — la más común
2. **Base64 → Hex → texto plano** — doble codificación
3. **Base64 → Base64 → texto plano** — Base64 anidado
4. **Hex → Base64 → ROT13 → texto plano** — codificación en tres capas
5. **Codificación URL → Base64 → texto plano** — común en escenarios Web
6. **Morse → Base64 → Hex → texto plano** — retos de criptografía

## Verificación tras decodificar

Tras decodificar, comprobar si el resultado:
- [ ] Es texto legible ASCII/UTF-8
- [ ] Parece una ruta (/xxx/yyy.php)
- [ ] Parece una URL (http://...)
- [ ] Contiene un formato de flag (flag{...}, NSSCTF{...})
- [ ] Sigue estando codificado (requiere seguir decodificando)

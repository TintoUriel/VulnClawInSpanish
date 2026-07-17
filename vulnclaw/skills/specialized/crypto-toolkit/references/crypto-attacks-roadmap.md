# Enrutamiento de clasificación de ataques criptográficos

Determina rápidamente qué método de ataque usar según la información conocida proporcionada por el reto.

## Árbol de decisión

```
Condiciones conocidas
├── ¿Se conoce el texto plano + el texto cifrado?
│   ├── ¿La misma clave cifrada varias veces? → análisis XOR/cifrado de flujo
│   └── ¿Cifrado único? → analizar el modo de cifrado
├── ¿Se conoce el texto cifrado + la clave?
│   ├── Cifrado simétrico → descifrar directamente
│   └── Cifrado asimétrico → ataques RSA/ECC
├── ¿Se conocen n, e, c (RSA)?
│   ├── e muy pequeño → ataque de exponente pequeño
│   ├── varios grupos con n común → ataque de módulo común
│   ├── d muy pequeño → ataque de Wiener
│   ├── p-1 suave (smooth) → Pollard p-1
│   └── probar factorización online (factordb)
├── ¿Parámetros de curva elíptica?
│   ├── orden suave → Pohlig-Hellman
│   ├── curva anómala → ataque de Smart
│   └── nonce de ECDSA reutilizado → recuperación de clave privada
├── ¿Se conoce la secuencia de salida del PRNG?
│   ├── MT19937 → recuperación de estado
│   ├── LCG → recuperación de parámetros
│   └── LFSR → Berlekamp-Massey
└── ¿Cifrado clásico?
    ├── César/ROT13 → fuerza bruta
    ├── Vigenère → Kasiski + análisis de frecuencias
    └── One-Time Pad reutilizado → ataque estadístico
```

## Selección rápida de ataques a RSA

| Conocido | Ataque |
|------|------|
| n, e, c, e=3 | Raíz de exponente pequeño |
| Varios grupos (n, c), mismo e, mismo texto plano | Difusión de Håstad |
| Varios grupos (n, c), mismo n, distinto e | Ataque de módulo común |
| n, e, aproximación de d muy pequeña | Ataque de Wiener |
| n factorizable, p≈q | Factorización de Fermat |
| n factorizable, p-1 suave | Pollard p-1 |
| Se conoce parte del texto plano | Coppersmith |
| Consultable en factordb | Factorización online |

## Selección rápida de ataques a AES/cifrados de bloque

| Escenario | Ataque |
|------|------|
| Modo ECB | Análisis de patrones + reordenamiento de bloques |
| Modo CBC, IV controlable | Ataque de volteo de IV |
| Modo CBC, Padding Oracle | Ataque Padding Oracle |
| CTR/GCM, nonce reutilizado | Recuperación del keystream |
| Se conoce parte del texto plano | Recuperación del keystream mediante XOR |

## Selección rápida de ataques a PRNG

| Escenario | Ataque |
|------|------|
| Python random(), 624 salidas | Recuperación de estado de MT19937 |
| 3 salidas consecutivas de LCG | Recuperación de parámetros |
| Secuencia de salida de LFSR | Berlekamp-Massey |
| RC4 (tras descartar los primeros 3072 bytes) | Ataque RC4 Drop |

## Selección rápida de cifrados clásicos

| Característica del texto cifrado | Ataque |
|---------|------|
| Sustitución de un solo carácter | Análisis de frecuencias |
| Desplazamiento de múltiples caracteres | Fuerza bruta César |
| Sustitución polialfabética | Vigenère Kasiski |
| XOR binario multibyte | Análisis de frecuencias + estimación de longitud de clave |
| One-Time Pad reutilizado | Ataque de comparación XOR |

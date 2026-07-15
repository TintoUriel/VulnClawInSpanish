# Ataques a PRNG y cifrados de flujo

## Ataque a MT19937 (Mersenne Twister)

```python
# Recuperación del estado de MT19937 (dadas 624 salidas)
from ctypes import *

def untemper(y):
    y ^= y >> 18
    y ^= (y << 15) & 0xefc60000
    y ^= (y << 7) & 0x9d2c5680
    y ^= (y << 14) & 0x9d2c5680
    y ^= (y << 13) & 0x9d2c5680
    y ^= (y << 11) & 0x9d2c5680
    y ^= y >> 18
    return y

def recover_mt(outputs):
    """Recupera el estado interno a partir de 624 salidas consecutivas de MT19937"""
    state = [untemper(y) for y in outputs[:624]]
    MT = c_ulong * 624
    mt = MT(*state)
    index = 624
    def twist():
        global index, mt
        for i in range(227):
            y = (mt[i] & 0x80000000) + (mt[(i+1)%624] & 0x7fffffff)
            mt[i] = mt[(i+397) % 624] ^ (y >> 1)
            if y & 1:
                mt[i] ^= 0x9908b0df
        index = 0
    return mt, twist, index
```

## Ataque a LCG (generador congruencial lineal)

```python
"""
LCG: s_{n+1} = a * s_n + c (mod m)
Con parámetros conocidos: recurrencia directa
Con parámetros desconocidos: con 3 pares (s, s_next) conocidos se pueden hallar a, c, m
"""

def lcg_attack(states):
    """Recupera los parámetros del LCG (a, c, m) a partir de 3 estados consecutivos"""
    s0, s1, s2 = states[0], states[1], states[2]
    # s1 = a*s0 + c (mod m)
    # s2 = a*s1 + c (mod m)
    # s2 - s1 = a*(s1 - s0) (mod m)
    # Euclides extendido para hallar a, m
```

## Ataque a LFSR (registro de desplazamiento con retroalimentación lineal)

```python
"""
Algoritmo de Berlekamp-Massey: recupera el polinomio de retroalimentación del LFSR a partir de la secuencia de salida
"""

def berlekamp_massey(s):
    """Recupera el polinomio de retroalimentación más corto del LFSR a partir de una secuencia binaria"""
    # Implementación en Sage
    # F.<x> = GF(2)[]
    # s_seq = sequence(s)
    # return list(lfsr_sequence(f, [1]+[0]*15, len(s)))
```

## Ataque de texto plano conocido (cifrado de flujo XOR)

```python
"""
Cifrado de flujo: C = P XOR keystream
Si se conoce parte del texto plano P, se puede recuperar keystream = C XOR P
El keystream puede usarse para descifrar otros criptogramas
"""

def xor_attack(ciphertext, known_plaintext):
    """Ataque de texto plano conocido sobre cifrado de flujo XOR"""
    key = bytes(a ^ b for a, b in zip(ciphertext, known_plaintext))
    return key

def xor_decrypt(key, ciphertext):
    """Descifra usando el flujo de claves recuperado"""
    return bytes(a ^ b for a, b in zip(key, ciphertext))
```

## Ataque a RC4

```python
"""
Debilidades conocidas de RC4:
1. RC4 Drop (tras descartar los primeros N bytes, el flujo de claves se acerca a lo aleatorio)
2. Algunas inicializaciones de clave presentan sesgo
"""

def rc4_drop(ciphertext, drop=3072):
    """Descifra tras aplicar RC4 Drop de N bytes"""
```

## Predicción del módulo random de Python

```python
import random

# Si se puede acceder al estado del random de Python, se pueden predecir los próximos números aleatorios
# Se necesita el estado de 624 * 4 = 2496 bytes
state = random.getstate()
# Avanzar el generador de números aleatorios
random.setstate(state)
next_val = random.randint(0, 2**31)
```

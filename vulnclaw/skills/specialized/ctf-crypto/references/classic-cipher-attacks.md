# Ataques a cifrados clásicos

## Cifrado César

```python
def caesar_break(ciphertext):
    """Prueba todos los desplazamientos"""
    for shift in range(26):
        result = ""
        for c in ciphertext:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                result += chr((ord(c) - base + shift) % 26 + base)
            else:
                result += c
        print(f"Shift {shift}: {result}")
```

## Cifrado de Vigenère

```python
def vigenere_break(ciphertext, max_keylen=20):
    """Rompe Vigenère mediante Kasiski + análisis de frecuencia"""
    from collections import Counter

    # 1. Kasiski: encontrar secuencias repetidas, estimar la longitud de la clave
    def kasiski(text):
        distances = []
        for length in range(3, 6):
            seqs = {}
            for i in range(len(text) - length):
                seq = text[i:i+length]
                if seq in seqs:
                    distances.append(i - seqs[seq])
                seqs[seq] = i
        return distances

    # 2. Índice de coincidencia (IC) para estimar la longitud de la clave
    def ic(text):
        freq = Counter(text.upper())
        n = len(text)
        return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

    # 3. Análisis de frecuencia para resolver una letra individual
    def solve_char(text, key_char):
        ENGLISH_FREQ = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'
        key_base = ord(key_char.upper()) - ord('A')
        best_score = 0
        best_char = 'E'
        for shift in range(26):
            freq = Counter()
            for c in text:
                if c.isalpha():
                    shifted = chr((ord(c.upper()) - ord('A') - shift) % 26 + ord('A'))
                    freq[shifted] += 1
            score = sum(ENGLISH_FREQ.index(k) * freq[k] for k in freq if k in ENGLISH_FREQ)
            if score > best_score:
                best_score = score
                best_char = chr(ord('A') + shift)
        return best_char
```

## Cifrado XOR multibyte

```python
def multi_byte_xor_break(ciphertext, max_keylen=16):
    """Ataque XOR multibyte: distancia de Hamming + análisis de frecuencia"""
    from collections import Counter

    def hamming_distance(b1, b2):
        return sum(bin(a ^ b).count('1') for a, b in zip(b1, b2))

    # Estimar la longitud de la clave con la distancia de Hamming
    best_keylen = 1
    best_score = float('inf')
    for keylen in range(2, max_keylen + 1):
        chunks = [ciphertext[i:i+keylen] for i in range(0, len(ciphertext), keylen)]
        avg_dist = sum(hamming_distance(c1, c2) for c1, c2 in zip(chunks[:4], chunks[1:5])) / 4
        normalized = avg_dist / keylen
        if normalized < best_score:
            best_score = normalized
            best_keylen = keylen

    # Agrupar según la longitud de la clave, hacer XOR de un solo byte en cada grupo
    key = b''
    for i in range(best_keylen):
        block = bytes(ciphertext[j] for j in range(i, len(ciphertext), best_keylen))
        # Análisis de frecuencia para encontrar la mejor clave de un byte
        best = 0
        best_score = 0
        for k in range(256):
            decrypted = bytes(b ^ k for b in block)
            score = sum(1 for b in decrypted if chr(b).isalpha() or chr(b).isspace())
            if score > best_score:
                best_score = score
                best = k
        key += bytes([best])

    return key
```

## Ataque de reutilización de One-Time Pad (OTP)

```python
"""
Si la misma clave OTP se usa para cifrar dos mensajes:
C1 = P1 XOR key
C2 = P2 XOR key
C1 XOR C2 = P1 XOR P2

Se explota la redundancia del lenguaje (frecuencia de palabras en inglés) para descifrarlo
"""
from collections import Counter

def otp_reuse_attack(c1, c2):
    """Ataque de reutilización de clave OTP"""
    xor_result = bytes(a ^ b for a, b in zip(c1, c2))
    # Análisis de frecuencia para recuperar el texto plano
```

## Cifrado de valla (Rail Fence)

```python
def railfence_break(ciphertext, max_rails=10):
    """Prueba distintos números de rieles para descifrar"""
    for rails in range(2, max_rails + 1):
        # Reconstruir la estructura de la valla
        fence = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        for c in ciphertext:
            fence[rail].append(c)
            rail += direction
            if rail == 0 or rail == rails - 1:
                direction = -direction
        # Leer fila por fila
        result = ''.join(''.join(row) for row in fence)
        print(f"Rails {rails}: {result}")
```

# Ataques a AES y cifrados por bloques

## Referencia rápida de modos de cifrado

| Modo | Característica | Vulnerabilidad explotable |
|------|------|-----------|
| ECB | Mismo texto plano → mismo criptograma | Reconocimiento de patrones, ataque de reordenamiento |
| CBC | El bloque de criptograma anterior participa en el cifrado actual | Volteo de IV, Padding Oracle |
| CTR | Cifrado de flujo | Reutilización de nonce → filtración por XOR |
| CFB | Similar a cifrado de flujo | Volteo de IV |
| OFB | Similar a cifrado de flujo | Reutilización de nonce |
| GCM | Cifrado autenticado | Reutilización de nonce → recuperación del flujo de claves |

## Volteo de bytes en ECB

```python
from Crypto.Cipher import AES

# En modo ECB, bloques de texto plano idénticos producen bloques de criptograma idénticos
# Ataque: identificar bloques de criptograma repetidos → inferir la estructura del texto plano
# Se pueden reordenar los bloques de criptograma para cambiar la estructura del texto plano

def ecb_detect(ciphertext, block_size=16):
    """Detecta el modo ECB (busca bloques repetidos)"""
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    return len(blocks) != len(set(blocks))
```

## Ataque de volteo de IV en CBC

```python
"""
Principio: en CBC, P[i] = Decrypt(C[i]) XOR C[i-1]
Modificar un byte de C[i-1] → el byte correspondiente de P[i] también se voltea

Uso: modificar el IV permite cambiar el primer bloque de texto plano, modificar C[i-1] permite cambiar el bloque i de texto plano
Costo: el texto plano P[i-1] correspondiente a C[i-1] se destruye
"""

def cbc_iv_flip(ciphertext, known_plain, target_plain, block_size=16):
    """Voltea el primer bloque de texto plano de CBC (modificando el IV)"""
    iv = bytearray(ciphertext[:block_size])
    for i in range(block_size):
        iv[i] = iv[i] ^ known_plain[i] ^ target_plain[i]
    return bytes(iv) + ciphertext[block_size:]
```

## Ataque Padding Oracle

```python
"""
Principio: al descifrar en CBC, si el padding no es válido, el servidor devuelve un error distinto
Mediante fuerza bruta byte a byte, se explota la diferencia entre respuesta correcta/incorrecta para recuperar el texto plano

Condiciones:
1. Se usa el modo CBC
2. El servidor devuelve respuestas distintas para error de padding y error de criptograma
3. Se puede enviar repetidamente el criptograma modificado
"""

def padding_oracle_attack(oracle, ciphertext, block_size=16):
    """Ataque Padding Oracle para recuperar el texto plano
    
    oracle: función que recibe el criptograma y devuelve True (padding correcto) / False (padding incorrecto)
    """
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    plaintext = b''
    
    for block_idx in range(1, len(blocks)):
        prev_block = bytearray(blocks[block_idx - 1])
        curr_block = blocks[block_idx]
        intermediate = bytearray(block_size)
        
        for byte_pos in range(block_size - 1, -1, -1):
            padding_val = block_size - byte_pos
            
            # Construir el criptograma de prueba
            test_block = bytearray(block_size)
            for k in range(byte_pos + 1, block_size):
                test_block[k] = intermediate[k] ^ padding_val
            
            found = False
            for guess in range(256):
                test_block[byte_pos] = guess
                test_cipher = bytes(test_block) + curr_block
                
                if oracle(test_cipher):
                    intermediate[byte_pos] = guess ^ padding_val
                    found = True
                    break
            
            if not found:
                raise Exception(f"Padding oracle attack failed at byte {byte_pos}")
        
        # Recuperar el texto plano
        for i in range(block_size):
            plaintext += bytes([intermediate[i] ^ prev_block[i]])
    
    return plaintext
```

## Ataque de reutilización de Nonce en GCM

```python
"""
Cuando el mismo nonce se usa en dos cifrados:
- Los dos cifrados usan el mismo flujo de claves
- C1 = P1 XOR keystream
- C2 = P2 XOR keystream
- C1 XOR C2 = P1 XOR P2

Si se conoce P1, se puede recuperar P2
"""

def gcm_nonce_reuse(c1, c2, p1):
    """Recupera el texto plano explotando la reutilización de nonce en GCM"""
    return bytes(a ^ b ^ c for a, b, c in zip(c1, c2, p1))
```

## Reutilización de Nonce en CTR

```python
"""
En modo CTR, la reutilización de nonce equivale a la reutilización de clave en cifrado de flujo
C1 = P1 XOR keystream
C2 = P2 XOR keystream
C1 XOR C2 = P1 XOR P2
"""

def ctr_nonce_reuse(c1, c2, known_p1):
    """Recupera el texto plano explotando la reutilización de nonce en CTR"""
    return bytes(a ^ b ^ c for a, b, c in zip(c1, c2, known_p1))
```

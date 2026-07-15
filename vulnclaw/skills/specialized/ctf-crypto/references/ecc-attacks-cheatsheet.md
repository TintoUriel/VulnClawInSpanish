# Hoja de referencia rápida de ataques ECC

## Fundamentos de curvas elípticas

```python
# Curva elíptica: y² = x³ + ax + b (mod p)
# Operaciones de punto: P + Q, k*P
# ECDLP: dados P, Q=k*P, hallar k
```

## Selección de ataque

| Condición | Método de ataque | Escenario aplicable |
|------|---------|---------|
| El orden n es un número suave (smooth) | Pohlig-Hellman | Todos los factores de n son pequeños |
| Curva anómala (p=n) | Ataque de Smart | Curvas anómalas |
| Orden de subgrupo pequeño | Ataque de subgrupo pequeño | El orden tiene un factor primo grande |
| Parámetros de curva sospechosos | Ataque de curva inválida (Invalid Curve) | Curvas no estándar |
| Reutilización de nonce en ECDSA | Ataque determinista | Se firma dos veces con el mismo k |
| Orden muy pequeño | Fuerza bruta/Baby-step Giant-step | n < 2^40 |

## Ataque Pohlig-Hellman

```python
# Implementación en Sage
# Cuando todos los factores del orden del grupo n son pequeños

P = EllipticCurve(GF(p), [a, b])
G = P(P_x, P_y)  # Punto base
Q = P(Q_x, Q_y)  # Punto objetivo

n = P.order()  # Orden del grupo
factors = factor(n)

# Pohlig-Hellman
k = discrete_log(Q, G, operation='+')
# O especificando el método
k = Q.discrete_log(G)
```

## Ataque de Smart (curvas anómalas)

```python
# Cuando el orden de la curva es igual a la característica p (curva anómala)
# E.lift_x() puede fallar pero se puede usar el levantamiento p-ádico

# Implementación en Sage
def smart_attack(P, Q, p, a, b):
    """Ataque de Smart, aplicable a curvas anómalas donde #E = p"""
    E = EllipticCurve(Qp(p), [a, b])
    P_lift = E.lift_x(ZZ(P.xy()[0]))
    Q_lift = E.lift_x(ZZ(Q.xy()[0]))
    
    pP = p * P_lift
    pQ = p * Q_lift
    
    x1 = pP.xy()[0] / pP.xy()[1]
    x2 = pQ.xy()[0] / pQ.xy()[1]
    
    k = ZZ(x2) / ZZ(x1) % p
    return k
```

## Ataque de curva inválida (Invalid Curve)

```python
# Cuando el servidor no valida si el punto está en la curva
# Se puede enviar un punto que no está en la curva, ese punto puede estar en otra curva
# Si el orden de esa otra curva es suave, se puede usar Pohlig-Hellman

# Construcción: elegir a' de modo que y² = x³ + a'*x + b tenga orden suave
```

## Ataque de reutilización de Nonce en ECDSA

```python
"""
Si en ECDSA el mismo nonce k se usa en dos firmas:
s1 = k^(-1) * (h1 + r*d) mod n
s2 = k^(-1) * (h2 + r*d) mod n

s1 - s2 = k^(-1) * (h1 - h2) mod n
k = (h1 - h2) * (s1 - s2)^(-1) mod n
d = (s1 * k - h1) * r^(-1) mod n  (clave privada)
"""

def ecdsa_nonce_reuse(r1, s1, h1, r2, s2, h2, n):
    """Recupera la clave privada explotando la reutilización de nonce en ECDSA"""
    from gmpy2 import invert
    # Confirmar que r es igual en ambas firmas
    assert r1 == r2
    k = ((h1 - h2) * invert(s1 - s2, n)) % n
    d = ((s1 * k - h1) * invert(r1, n)) % n
    return int(d)
```

## Tipos comunes de retos ECC en CTF

| Tipo de reto | Característica | Ataque |
|------|------|------|
| Curva estándar + orden pequeño | n < 2^40 | Fuerza bruta |
| Curva estándar + orden suave | n tiene factores pequeños | Pohlig-Hellman |
| Curva anómala | #E = p | Ataque de Smart |
| Curva personalizada | a, b sospechosos | Invalid Curve / factorización del orden |
| Firma ECDSA | Varios grupos de firmas | Reutilización de nonce |
| Twisted Edwards | x² + a*y² = 1 + d*x²*y² | Conversión a Weierstrass |

# Hoja de referencia rápida de ataques RSA

## Árbol de decisión de selección de ataque

```
Se conocen n, e, c
├── ¿e es muy pequeño (e=3)?
│   ├── ¿Mismo texto plano cifrado varias veces (varios c)? → Ataque de difusión de Håstad
│   └── ¿Solo un grupo? → Ataque de raíz de exponente pequeño (baja probabilidad)
├── ¿Varios grupos (n, e, c)?
│   ├── ¿n es igual? → Ataque de módulo común
│   ├── ¿e es igual? → Ataque de difusión de Håstad
│   └── ¿p o q comparten factor común? → Factorización por MCD
├── ¿e es muy grande (>65537)?
│   └── d puede ser muy pequeño → Ataque de Wiener
├── ¿n se puede factorizar?
│   ├── Factorización de Fermat (p≈q)
│   ├── Pollard p-1 (factores de p-1 pequeños)
│   ├── Williams p+1 (factores de p+1 pequeños)
│   └── Consulta en línea (factordb)
└── ¿Se conoce información parcial?
    ├── Texto plano parcial → Coppersmith
    ├── p parcial → Coppersmith
    └── d parcial → Construcción directa
```

## Ataque de exponente pequeño (e=3)

### Ataque de difusión de exponente bajo (Håstad)
```python
from gmpy2 import iroot
from functools import reduce

def hastard_broadcast(cs, ns, e=3):
    """Cuando el mismo texto plano se cifra con e grupos de distintos n"""
    # Resolución por CRT
    N = reduce(lambda a, b: a * b, ns)
    x = 0
    for i in range(e):
        Mi = N // ns[i]
        yi = pow(Mi, -1, ns[i])
        x += cs[i] * Mi * yi
    x %= N
    m = iroot(x, e)
    if m[1]:
        return int(m[0])
    return None
```

## Ataque de módulo común

```python
from gmpy2 import gcd

def common_modulus_attack(c1, c2, e1, e2, n):
    """Mismo texto plano, mismo n, cifrado con distintos e"""
    g, s1, s2 = extended_gcd(e1, e2)
    if s1 < 0:
        c1 = pow(c1, -1, n)
        s1 = -s1
    if s2 < 0:
        c2 = pow(c2, -1, n)
        s2 = -s2
    m = (pow(c1, s1, n) * pow(c2, s2, n)) % n
    return m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x
```

## Ataque de Wiener (e muy grande, d muy pequeño)

```python
def wiener_attack(e, n):
    """Válido cuando d < n^(1/4)"""
    cf = continued_fraction(e, n)
    convergents = get_convergents(cf)
    for k, d in convergents:
        if k == 0:
            continue
        phi = (e * d - 1) // k
        # Comprobar si es un phi válido
        x = n - phi + 1
        disc = x * x - 4 * n
        if disc >= 0:
            s = int(disc ** 0.5)
            if s * s == disc:
                return d
    return None
```

## Factorización de Fermat (p ≈ q)

```python
from gmpy2 import is_square, iroot

def fermat_factor(n):
    """Válido cuando p y q están muy cerca entre sí"""
    a = iroot(n, 2)[0] + 1
    b2 = a * a - n
    while not is_square(b2):
        a += 1
        b2 = a * a - n
    p = a + iroot(b2, 2)[0]
    q = a - iroot(b2, 2)[0]
    return int(p), int(q)
```

## Ataque Pollard p-1

```python
from math import gcd

def pollard_p1(n, B=100000):
    """Válido cuando todos los factores de p-1 son menores que B"""
    a = 2
    for j in range(2, B):
        a = pow(a, j, n)
        d = gcd(a - 1, n)
        if 1 < d < n:
            return d, n // d
    return None
```

## Ataque de Coppersmith (texto plano parcialmente conocido)

```python
# Usando SageMath
# Cuando se conocen los bits altos o bajos del texto plano
# m = parte_conocida + parte_desconocida
# parte_desconocida < n^(1/e)

# Implementación en Sage:
P.<x> = PolynomialRing(Zmod(n))
f = (known_prefix + x)^e - c
f = f.monic()
roots = f.small_roots()
if roots:
    m = known_prefix + roots[0]
```

## Herramientas de factorización en línea

- https://factordb.com — consultar valores de n ya factorizados
- http://sagecell.sagemath.org — cálculo en línea con Sage

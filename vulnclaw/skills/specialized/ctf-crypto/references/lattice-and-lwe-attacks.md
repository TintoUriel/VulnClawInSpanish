# Ataques de retículos y LWE

## Conceptos básicos

```
Retículo (Lattice): subgrupo aditivo discreto de Z^n
Base del retículo (Basis): conjunto de vectores linealmente independientes que generan el retículo
Algoritmo LLL: halla un vector aproximadamente más corto de la base del retículo (aproximación de SVP)
CVP (Closest Vector Problem): encontrar el vector más cercano
SVP (Shortest Vector Problem): encontrar el vector más corto
```

## Algoritmo LLL

```python
# Implementación en SageMath
"""
A = matrix(ZZ, [[...], [...], ...])  # Matriz de base del retículo
B = A.LLL()  # Base reducida por LLL
# Los vectores columna de B son vectores del retículo cercanos al más corto
```

## Hidden Number Problem (HNP)

```python
"""
Conocido: (d_i, (t_i * a + k_i * d_i) mod p) bits parciales
Recuperar: a (clave privada)
Se usa Coppersmith para hallar k_i
"""
# SageMath
def hnp_attack(d, t, bits, p):
    F.<x> = PolynomialRing(Zmod(p))
    # Construir el polinomio...
```

## Relacionado con Coppersmith

```python
"""
Coppersmith halla raíces pequeñas de polinomios:
f(x) = 0 mod n, |x| < n^(1/d)
donde d es el grado del polinomio
"""

# SageMath
def coppersmith_small_root(f, n, d, m):
    """f(x) = 0 mod n, halla la raíz pequeña x, |x| < n^(1/(d*omega))"""
    # Construir el retículo y aplicar LLL
```

## LWE (Learning With Errors)

```python
"""
Problema LWE:
Conocido: (A, b = As + e) mod q
Recuperar: s (clave privada)
donde e es un vector de error pequeño

Ataques habituales:
1. Enumeración del error pequeño (cuando e es muy pequeño)
2. Algoritmo BKW
3. Reducción a SVP/CVP
"""
```

## Plantilla de ataque HNP

```python
# SageMath: recuperar la clave privada RSA a partir de una clave privada parcial
"""
Variante del DCP (Diffie-Hellman Claw Problem)
Se resuelve mediante reducción de retículos
"""

# Plantilla básica
"""
F = GF(p)
P.<x> = PolynomialRing(F)

# Construir la matriz de base del retículo
# Aplicar LLL
# Extraer la clave privada de la base reducida
"""
```

## Plantilla general de ataques de retículos

```python
# Considerar un ataque de retículo cuando se dé alguno de estos escenarios:
# 1. Varias ecuaciones con incógnitas y "errores pequeños"
# 2. Recuperación de clave privada parcial/texto plano parcial
# 3. Reducción al problema del vector más cercano en un retículo

# Pasos:
# 1. Modelar el problema como CVP/SVP en un retículo
# 2. Construir la matriz de base del retículo
# 3. Reducir usando LLL/BKZ
# 4. Extraer la solución de la base reducida
```

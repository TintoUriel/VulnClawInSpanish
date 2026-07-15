# Referencia rápida de CTF Web

## Ubicaciones comunes de la flag

### Linux
```
/flag
/flag.txt
/flag.php
/var/www/html/flag.php
/home/ctf/flag
/root/flag
/tmp/flag
/opt/flag
/srv/flag
```

### Docker/variables de entorno
```
/proc/self/environ
/environment
/.env
```

### Específico de PHP
```php
// flag en phpinfo()
// Revisar la sección de variables de entorno
// Revisar secciones personalizadas

// Nombres de archivo de flag comunes
flag.php
flag.txt
f1ag.php
fl4g.php
fl@g.php
th1s_1s_flag.php
```

## Flujo de trabajo de primera pasada

```
1. Acceder a la URL objetivo
   → Revisar el código fuente de la página (Ctrl+U)
   → Revisar las cabeceras HTTP (Server, X-Powered-By, Set-Cookie)
   → Revisar el valor de las cookies (base64/JWT/serializado)

2. Revisar información oculta
   → robots.txt
   → .git/HEAD
   → .svn/
   → archivos de respaldo: index.php.bak, www.zip, .index.php.swp, index.php~
   → DS_Store: .DS_Store

3. Escaneo de directorios
   → /flag, /admin, /login, /upload, /api, /debug
   → /phpinfo.php, /info.php, /test.php
   → /console (Flask Debug), /actuator (Spring Boot)

4. Si hay código fuente → auditoría de código
   → consultar php-code-audit-checklist.md

5. Si no hay código fuente → sondeo activo
   → pruebas de inyección SQL
   → pruebas de XSS
   → subida de archivos
   → pruebas de SSTI
   → LFI/RFI
```

## Comandos de prueba rápida

```bash
# Revisar información básica
curl -I http://target/              # cabeceras HTTP
curl http://target/robots.txt        # robots
curl http://target/.git/HEAD         # filtración de git

# Pruebas de inyección comunes
' OR 1=1 --                          # SQLi
{{7*7}}                              # SSTI
<script>alert(1)</script>            # XSS
../../../etc/passwd                  # LFI
```

## Pistas comunes en cabeceras de respuesta

| Cabecera de respuesta | Significado | Siguiente paso |
|--------|------|--------|
| `X-Forwarded-For: 127.0.0.1` | Se requiere acceso local | Añadir la cabecera X-Forwarded-For |
| `Server: nginx/1.x` | Tipo de servidor | Buscar CVE conocidos |
| `X-Powered-By: PHP/7.x` | Versión de PHP | Vulnerabilidades específicas de PHP |
| `Set-Cookie: role=guest` | Control de permisos | Modificar la cookie |
| `Hint: xxx` | Pista directa | Actuar según la pista |
| `Flag: xxx` | A veces está directamente en la cabecera | Revisar todas las cabeceras de respuesta |

## Formas comunes de cadenas de explotación

### Cadena simple PHP
```
URL → código fuente → se detecta un filtro → bypass del filtro → RCE → leer la flag
```

### Cadena PHP de múltiples pasos
```
Página de entrada → se descubre una pista → se sigue el enlace → se descubre una nueva página → se obtiene el código fuente → se analiza y explota → RCE
```

### Cadena de inclusión de archivos
```
LFI → leer código fuente (php://filter) → descubrir el punto de inclusión → envenenamiento de logs/inclusión de sesión → RCE
```

### Cadena de inyección SQL
```
Formulario de login → SQLi → leer datos → descubrir la contraseña del administrador → iniciar sesión en el panel → subir webshell → RCE
```

### Cadena de deserialización
```
Datos serializados controlables → analizar los gadgets disponibles → construir la cadena de explotación → RCE/SSRF/lectura de archivos
```

## Pistas comunes de codificación/cifrado

| Característica | Posible codificación | Método de decodificación |
|------|---------|---------|
| Termina en `=` | Base64 | `crypto_decode base64_decode` |
| `0-9a-f` de longitud par | Hex | `crypto_decode hex_decode` |
| `%XX` | Codificación URL | `crypto_decode url_decode` |
| `&#xNN;` | Entidad HTML | `crypto_decode html_decode` |
| `\uXXXX` | Escape Unicode | `crypto_decode unicode_decode` |
| Tres segmentos separados por `.` | JWT | `crypto_decode jwt_decode` |
| Puntos y rayas | Morse | `crypto_decode morse_decode` |
| Ilegible pero parece letras | ROT13/César | `crypto_decode rot13_decode` |

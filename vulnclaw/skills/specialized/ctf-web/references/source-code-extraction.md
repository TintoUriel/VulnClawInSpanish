# Referencia de métodos de extracción de código fuente en CTF Web

## Idea central

- Los retos de CTF Web suelen usar `highlight_file(__FILE__)` para mostrar el código fuente, generando salida HTML resaltada
- Algunos retos solo exponen parte del código fuente en comentarios HTML o elementos ocultos; esto forma parte del diseño del reto
- **El código fuente es una pista importante, pero no la única**: en algunos retos la vía de entrada clave está en robots.txt, cabeceras de respuesta, archivos ocultos, etc.

---

## Método 1: extracción con strip_tags (opción preferida para escenarios con highlight_file)

**Aplicable a**: páginas que muestran el código fuente mediante `highlight_file()` / `show_source()`

```python
import requests, re
r = requests.get(url)
# Eliminar todas las etiquetas HTML para obtener texto plano
clean = re.sub(r'<[^>]+>', '', r.text)
# Opcional: eliminar líneas en blanco sobrantes
clean = re.sub(r'\n{3,}', '\n\n', clean)
print(clean)
```

**Nota**:
- Se eliminan todas las etiquetas HTML; si el propio código fuente contiene cadenas HTML, también se eliminarán
- La salida HTML resaltada obtenida por la herramienta fetch **no es adecuada para reconstruirse a simple vista**; se recomienda verificarla con python_execute

---

## Método 2: lectura del código fuente con php://filter

**Aplicable a**: escenarios con vulnerabilidad de inclusión de archivos (`include`/`require`)

```
?page=php://filter/convert.base64-encode/resource=index.php
?page=php://filter/read=convert.base64-encode/resource=flag.php
```

Una vez obtenido el código fuente codificado en base64:
```python
import base64
source = base64.b64decode(base64_string).decode('utf-8')
print(source)
```

---

## Método 3: sufijo .phps

**Aplicable a**: servidores configurados para mostrar el código fuente PHP

```
/learning.phps
/index.phps
```

---

## Método 4: archivos de respaldo / filtración de control de versiones

| Ruta | Descripción |
|------|------|
| `.git/HEAD` | Filtración del repositorio Git |
| `.svn/entries` | Filtración del repositorio SVN |
| `index.php.bak` | Archivo de respaldo |
| `index.php~` | Archivo temporal del editor |
| `www.zip` / `web.tar.gz` | Empaquetado completo del sitio |
| `.index.php.swp` | Archivo de intercambio de Vim |

---

## Método 5: comentarios HTML y elementos ocultos

Algunos retos colocan código fuente o pistas en comentarios HTML:

```python
import requests, re
r = requests.get(url)
# Extraer el contenido de los comentarios HTML
comments = re.findall(r'<!--(.*?)-->', r.text, re.DOTALL)
for c in comments:
    print(c)
```

---

## Método 6: cabeceras de respuesta y cookies

Algunos retos ocultan pistas en las cabeceras de respuesta:

```python
import requests
r = requests.get(url)
print("Headers:", dict(r.headers))
print("Cookies:", dict(r.cookies))
```

---

## Evaluación de la integridad del código fuente

Tras extraer el código fuente, se puede verificar si está completo:

| Elemento a verificar | Descripción |
|--------|------|
| Coincidencia de llaves | Un `if` sin `}` de cierre puede indicar que el código fuente está truncado, o puede ser algo intencional del reto |
| Presencia de sentencias de salida | Si no hay `echo`/`print`/`die`, puede haber código adicional que aún no se ha visto |
| Presencia de funciones peligrosas | Si no hay `eval`/`system` etc., la vía de RCE puede estar en otra página |

**Nota**: un código fuente incompleto puede deberse a dos causas:
1. El método de extracción tiene un problema → probar otro método
2. El reto solo expone esa cantidad de código de forma intencional → hay que seguir explorando otras pistas (otras páginas, parámetros, archivos)

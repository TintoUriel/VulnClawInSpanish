# Seguridad Web - Fuga de información

> Fuente: base de vulnerabilidades WooYun | separado de web-file-infra.md

## III. Fuga de información

### 3.1 Esencia de la vulnerabilidad

```
Esencia de la fuga de información: exposición de superficie de ataque -> ruptura de la cadena de confianza -> penetración en profundidad
Patrón: un solo punto de fuga puede provocar el colapso de toda la cadena de confianza
      código fuente -> configuración -> base de datos -> red interna -> compromiso total
```

### 3.2 Diccionario de rutas de archivos sensibles

Fuga de control de versiones:

```bash
# Fuga de Git (máxima prioridad de detección)
/.git/config          # contiene la dirección del repositorio remoto
/.git/HEAD            # rama actual
/.git/index           # índice del área de staging
/.git/logs/HEAD       # log de operaciones

# Fuga de SVN
/.svn/entries         # SVN 1.6 y anteriores
/.svn/wc.db           # base de datos SQLite de SVN 1.7+

# Herramientas de explotación: dvcs-ripper, GitHack, svn-extractor
```

Fuga de archivos de backup:

```bash
# Backup en archivo comprimido (530 casos detectados)
/wwwroot.rar | /www.zip | /web.rar | /backup.zip | /site.tar.gz
/{domain}.zip | /{domain}.rar

# Backup SQL (136 casos detectados)
/backup.sql | /database.sql | /db.sql | /dump.sql

# Backup de configuración (101 casos detectados)
/config.php.bak | /web.config.bak | /.env.bak
/config_global.php.bak
```

Fuga de archivos de configuración:

```bash
# General
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

Archivos de sonda/depuración/logs:

```bash
# Archivos de sonda
/phpinfo.php | /info.php | /test.php | /probe.php

# Archivos de log
/ctp.log | /logs/ctp.log | /debug.log | /storage/logs/

# Interfaz de administración
/phpmyadmin/ | /pma/ | /adminer.php
/swagger-ui.html | /api-docs
/actuator/env                    # Spring Boot
```

### 3.3 Metodología de sondeo

```
Fase 1 recolección pasiva: cabeceras de respuesta (Server/X-Powered-By) -> página de error -> robots.txt -> comentarios de código fuente/JS
Fase 2 sondeo dirigido: control de versiones (.git/.svn) -> archivos de backup (dominio/fecha) -> rutas sensibles
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

### 3.4 Cadena de explotación de la información

```
Fuga de código fuente -> archivo de configuración -> credenciales de BD -> toma de control de BD -> escalada de privilegios en el servidor
Control de versiones   -> auditoría de código  -> inyección SQL, etc. -> permisos de administrador -> subida de archivos y obtención de shell
Fuga de configuración  -> cadena de conexión BD -> base de datos    -> datos de usuario   -> toma de control del negocio
Fuga de logs           -> Session  -> secuestro de identidad  -> datos de negocio   -> movimiento lateral
Interfaz de API        -> credenciales/contraseña -> descifrado     -> control masivo   -> penetración total
Credenciales de terceros -> SMS/OSS -> código de verificación -> toma de control de cuenta -> fuga de datos
```

### 3.5 Medidas de defensa

Configuración de seguridad de Nginx:

```nginx
location ~ /\.(git|svn|env|htaccess|htpasswd) { deny all; return 404; }
location ~ \.(bak|sql|log|config|ini|yml)$ { deny all; return 404; }
location ~* /(backup|bak|old|temp|test|dev)/ { deny all; return 404; }
autoindex off;
server_tokens off;
```

Configuración de seguridad de Apache:

```apache
<FilesMatch "\.(git|svn|env|bak|sql|log|config)">
    Order Allow,Deny
    Deny from all
</FilesMatch>
Options -Indexes
ServerSignature Off
```

Integración CI/CD: escanear archivos sensibles antes del despliegue -> prohibir el despliegue de .git/.svn -> cifrar los archivos de configuración

---

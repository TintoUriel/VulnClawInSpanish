# Referencia de Recopilación de Información del Servidor

## 1. Puertos abiertos e identificación de versiones de servicio

### Comandos comunes de nmap
```bash
# Escaneo de todos los puertos (lento pero exhaustivo)
nmap -p- -sV <target>

# Escaneo rápido de puertos comunes
nmap -sV -top-ports 1000 <target>

# Escaneo de puertos UDP
nmap -sU --top-ports 100 <target>

# Identificación de versión de servicio + detección de SO
nmap -sV -O <target>
```

### Método con python_execute (cuando no hay nmap)
```python
import socket

def scan_port(host, port, timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except:
        return False

host = "target.com"
common_ports = [21,22,23,25,53,80,110,143,443,445,993,995,1433,1521,3306,3389,5432,6379,8080,8443,9200,27017]
open_ports = [p for p in common_ports if scan_port(host, p)]
print(f"Puertos abiertos: {open_ports}")
```

### Identificación de versión de servicio (Banner Grabbing)
```python
import socket

def grab_banner(host, port, timeout=3):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        # Para servicios HTTP, enviar una solicitud para obtener el banner
        if port in [80, 443, 8080, 8443]:
            s.send(b"HEAD / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
        else:
            s.send(b"\r\n")
        banner = s.recv(1024).decode('utf-8', errors='ignore')
        s.close()
        return banner[:200]
    except:
        return None
```

## 2. Detección de la IP real (IP del servidor origen detrás de un CDN)

### Método 1: Historial DNS
- SecurityTrails (https://securitytrails.com/dns-trials)
- DNSHistory (https://dnshistory.org)
- ViewDNS (https://viewdns.info/iphistory/)
- Netcraft Site Report (https://sitereport.netcraft.com/)

### Método 2: Ping global
```python
import requests
# Usar servicios de ping desde múltiples ubicaciones
urls = [
    f"https://www.whatsmydns.net/#A/{domain}",
    f"https://ping.pe/{domain}",
    f"https://tools.keycdn.com/curl?url={domain}",
]
# Si distintas regiones resuelven a IPs diferentes, indica el uso de un CDN
# Si múltiples regiones resuelven a la misma IP, esa IP podría ser el servidor origen real
```

### Método 3: Extracción de cabeceras de correo
- Registrarse/iniciar sesión en el sitio objetivo y recibir un correo
- Revisar el campo `Received:` en las cabeceras del correo
- Puede revelar la IP real del servidor de correo

### Método 4: Resolución de subdominios
- Los CDN normalmente solo sirven al dominio principal
- Los subdominios (como mail.ftp.dev.staging) pueden resolver directamente a la IP del origen
- Revisar los registros A de todos los subdominios, descartando las IP del CDN

### Método 5: Búsqueda de certificados SSL
```python
import requests
domain = "target.com"
r = requests.get(f"https://crt.sh/?q=%.{domain}&output=json")
if r.status_code == 200:
    # Buscar las IP asociadas a certificados de distintos subdominios
    for entry in r.json():
        print(entry.get('name_value', ''))
```

## 3. Huella del sistema operativo

### Inferencia por TTL
| Valor TTL | Sistema operativo probable |
|--------|-------------|
| ≈ 64 | Linux / Unix / macOS |
| ≈ 128 | Windows |
| ≈ 255 | Dispositivo de red / Unix antiguo |

```python
import subprocess
# Ping para obtener el TTL
result = subprocess.run(['ping', '-c', '1', host], capture_output=True, text=True)
# Windows: ping -n 1 host
# Extraer el TTL de la salida
import re
ttl_match = re.search(r'TTL[=:]\s*(\d+)', result.output, re.I)
if ttl_match:
    ttl = int(ttl_match.group(1))
    if ttl <= 64:
        print("Inferencia: Linux/Unix")
    elif ttl <= 128:
        print("Inferencia: Windows")
    else:
        print("Inferencia: dispositivo de red")
```

### Detección de SO con nmap
```bash
nmap -O <target>
# Modo más agresivo (requiere root)
sudo nmap -O --osscan-guess <target>
```

## 4. Identificación de versiones de middleware

### Análisis de cabeceras de respuesta HTTP
```
Server: Apache/2.4.49 (Ubuntu)
Server: nginx/1.18.0
Server: Microsoft-IIS/10.0
X-Powered-By: PHP/7.4.3
X-Powered-By: Express
X-AspNet-Version: 4.0.30319
```

### Características de las páginas de error
- Apache: la página 404 por defecto contiene la cadena "Apache"
- Nginx: la página 404 por defecto contiene la cadena "nginx"
- IIS: la página de error por defecto contiene información de versión de IIS
- Tomcat: la página 404 por defecto contiene la versión de Apache Tomcat

### Sondeo de archivos característicos
```python
import requests
target = "https://target.com"
# Apache
r = requests.get(f"{target}/server-status")  # 403 = existe
r = requests.get(f"{target}/server-info")    # 403 = existe
# Nginx
r = requests.get(f"{target}/nginx_status")   # puede revelar el estado
# Tomcat
r = requests.get(f"{target}/manager/html")   # interfaz de administración
# IIS
r = requests.get(f"{target}/aspnet_client/") # característica de ASP.NET
```

## 5. Identificación de bases de datos

### Sondeo de puertos
| Base de datos | Puerto por defecto | Nota |
|--------|---------|------|
| MySQL | 3306 | La más común |
| PostgreSQL | 5432 | Común en Rails/Django |
| MSSQL | 1433 | Entornos Windows |
| MongoDB | 27017 | NoSQL |
| Redis | 6379 | Caché/cola de mensajes |
| Oracle | 1521 | Nivel empresarial |
| Memcached | 11211 | Caché |

### Características de los mensajes de error
- MySQL: `You have an error in your SQL syntax`
- PostgreSQL: `ERROR: syntax error at or near`
- MSSQL: `Microsoft SQL Server`
- Oracle: `ORA-01756`

### Detección con python_execute
```python
import socket

def check_db(host, port, timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        # Intentar leer el banner
        s.send(b"\r\n")
        banner = s.recv(1024)
        s.close()
        return banner.hex()[:40], banner[:100]
    except:
        return None, None

db_ports = {
    3306: "MySQL", 5432: "PostgreSQL", 1433: "MSSQL",
    27017: "MongoDB", 6379: "Redis", 1521: "Oracle",
}
for port, name in db_ports.items():
    hex_banner, banner = check_db(host, port)
    if hex_banner:
        print(f"[+] {name} ({port}): {banner}")
```

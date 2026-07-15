# Referencia de Recopilación de Información de Sitios Web

## 1. Identificación de la arquitectura del sitio

### Métodos de inferencia del stack tecnológico
1. **Cabeceras de respuesta HTTP** — características de Server, X-Powered-By, Set-Cookie
2. **Características del código fuente HTML** — meta generator, nombres específicos de class/id
3. **Rutas de archivos JS** — /static/js/app.js, /wp-content/, /assets/
4. **Nombres de cookies** — PHPSESSID (php), JSESSIONID (Java), _rails_session (Rails)
5. **Rutas de URL** — ?id= (PHP), /api/ (REST), /wp-admin/ (WordPress)

### Combinaciones de arquitectura habituales
| Lenguaje | Framework | Base de datos | Servidor | Característica |
|------|------|--------|--------|------|
| PHP | Laravel | MySQL | Apache/Nginx | Set-Cookie: laravel_session |
| PHP | WordPress | MySQL | Apache | /wp-content/, /wp-admin/ |
| Python | Django | PostgreSQL | Nginx+Gunicorn | Cookie del middleware CSRF |
| Python | Flask | SQLite/MySQL | Nginx+uWSGI | Set-Cookie: session= |
| Java | Spring | MySQL/Oracle | Tomcat | JSESSIONID |
| Node.js | Express | MongoDB | Nginx | X-Powered-By: Express |
| Ruby | Rails | PostgreSQL | Nginx+Puma | _rails_session |

### Sondeo de arquitectura con python_execute
```python
import requests

url = "https://target.com"
r = requests.get(url, timeout=10)

# 1. Análisis de cabeceras de respuesta
headers = r.headers
print(f"Server: {headers.get('Server', 'N/A')}")
print(f"X-Powered-By: {headers.get('X-Powered-By', 'N/A')}")

# 2. Análisis de cookies
cookies = r.cookies
for cookie in cookies:
    print(f"Cookie: {cookie.name} = {cookie.value[:20]}...")

# 3. Análisis de características HTML
html = r.text
# WordPress
if 'wp-content' in html or 'wp-includes' in html:
    print("[+] Detección de WordPress")
# Laravel
if 'laravel_session' in str(cookies):
    print("[+] Detección de Laravel")
# Django
if 'csrftoken' in str(cookies) or 'csrfmiddlewaretoken' in html:
    print("[+] Detección de Django")
# Hexo
if 'hexo' in html.lower():
    print("[+] Detección de blog Hexo")
# Hugo
if 'hugo' in html.lower():
    print("[+] Detección de blog Hugo")
```

## 2. Identificación de huella digital web

### Características de huella de CMS
| CMS | Ruta característica | Cadena característica |
|-----|---------|-----------|
| WordPress | /wp-login.php, /wp-content/ | wp-content, xmlrpc.php |
| Joomla | /administrator/ | /media/jui/ |
| Drupal | /misc/drupal.js | Drupal.settings |
| Discuz | /forum.php | discuz_uid |
| Typecho | /admin/login.php | typecho |
| Hexo | /archives/ | hexo |
| Ghost | /ghost/ | ghost-frontend |

### Características de frameworks de frontend
| Framework | Característica |
|------|------|
| React | data-reactroot, __NEXT_DATA__ |
| Vue.js | data-v-xxx, __vue__ |
| Angular | ng-version, _nghost |
| jQuery | jQuery en los scripts |
| Bootstrap | bootstrap.css/js |

### Identificación de huella con python_execute
```python
import requests, re

url = "https://target.com"
r = requests.get(url, timeout=10)
html = r.text

# Detección de CMS
cms_signatures = {
    "WordPress": ["wp-content", "wp-includes", "wp-admin"],
    "Joomla": ["/administrator/", "media/jui"],
    "Drupal": ["Drupal.settings", "/misc/drupal"],
    "Hexo": ["hexo", "/archives/"],
    "Hugo": ["hugo", "gohugo"],
    "Ghost": ["ghost-frontend", "/ghost/"],
}

for cms, sigs in cms_signatures.items():
    if any(sig in html for sig in sigs):
        print(f"[+] CMS: {cms}")

# Detección de framework de frontend
fw_signatures = {
    "React": ["data-reactroot", "__NEXT_DATA__", "react"],
    "Vue.js": ["data-v-", "__vue__", "vue"],
    "Angular": ["ng-version", "_nghost", "angular"],
    "jQuery": ["jquery", "jQuery"],
    "Bootstrap": ["bootstrap"],
}

for fw, sigs in fw_signatures.items():
    if any(sig.lower() in html.lower() for sig in sigs):
        print(f"[+] Framework de frontend: {fw}")

# Extracción de archivos JS
js_files = re.findall(r'src=["\']([^"\']*\.js[^"\']*)["\']', html)
print(f"Archivos JS: {js_files[:10]}")
```

## 3. Detección de WAF

### Características habituales de WAF
| WAF | Característica de bloqueo |
|-----|---------|
| Cloudflare | Server: cloudflare, cabecera CF-Ray |
| AWS WAF | Server: AmazonS3, x-amz-request-id |
| Alibaba Cloud WAF | Set-Cookie contiene acw_tc |
| Tencent Cloud WAF | Página de bloqueo específica |
| BT-WAF (aaPanel) | La página de bloqueo contiene "宝塔" (BT/aaPanel) |
| Safedog | La página de bloqueo contiene "safedog" |
| ModSecurity | Respuesta 403 específica |

### Detección de WAF con python_execute
```python
import requests

url = "https://target.com"

# 1. Petición normal
r1 = requests.get(url)

# 2. Petición que provoca el WAF
waf_payloads = [
    "/?id=1' OR 1=1--",
    "/?search=<script>alert(1)</script>",
    "/../../../etc/passwd",
    "/?file=php://filter/convert.base64-encode/resource=index",
]

for payload in waf_payloads:
    r2 = requests.get(url + payload, allow_redirects=False)
    # Cambio en el código de estado
    if r2.status_code in [403, 406, 429, 501]:
        print(f"[!] Detección de WAF: {payload} → {r2.status_code}")
    # Cambio significativo en la longitud de la respuesta
    if abs(len(r2.text) - len(r1.text)) > 500:
        print(f"[!] Cambio en la longitud de la respuesta: normal={len(r1.text)}, ataque={len(r2.text)}")

# 3. Comprobar cabeceras de respuesta específicas de WAF
waf_headers = {
    "cloudflare": ["cf-ray", "server: cloudflare"],
    "aws": ["x-amz-request-id", "x-amz-cf-id"],
    "alibaba_cloud": ["acw_tc"],
}
for waf_name, sigs in waf_headers.items():
    for sig in sigs:
        if sig in str(r1.headers).lower():
            print(f"[+] Detección de WAF: {waf_name}")
```

## 4. Directorios y archivos sensibles

### Lista de rutas sensibles habituales
```
/robots.txt
/sitemap.xml
/.git/
/.svn/
/.env
/.DS_Store
/web.config
/config.php
/config.yml
/backup/
/admin/
/login/
/api/
/swagger/
/graphql
/phpinfo.php
/test/
/debug/
/console/
/actuator/
/.well-known/
```

### Escaneo de directorios con python_execute
```python
import requests

target = "https://target.com"
paths = [
    "/robots.txt", "/sitemap.xml", "/.git/", "/.env", "/.DS_Store",
    "/admin/", "/backup/", "/config.php", "/api/", "/phpinfo.php",
    "/.git/config", "/.git/HEAD", "/wp-config.php",
    "/swagger/", "/graphql", "/actuator/",
]

for path in paths:
    try:
        r = requests.get(target + path, timeout=5, allow_redirects=False)
        if r.status_code in [200, 301, 302, 401, 403]:
            print(f"[{r.status_code}] {path}")
    except:
        pass
```

## 5. Comprobación de fuga de código fuente

### Tipos habituales de fuga de código fuente
| Tipo | Ruta | Método de detección |
|------|------|---------|
| Repositorio Git | /.git/config, /.git/HEAD | 200 y contiene contenido de git |
| Repositorio SVN | /.svn/entries | 200 y contiene contenido de svn |
| .DS_Store | /.DS_Store | Descargar y analizar |
| Archivo .env | /.env | Contiene DB_PASSWORD, etc. |
| web.config | /web.config | Configuración de IIS |
| Archivos de respaldo | /.bak, /.swp, /.old, /~ | Descarga directa |
| Docker | /Dockerfile, /docker-compose.yml | Configuración de contenedor |
| package.json | /package.json | Dependencias de Node.js |
| composer.json | /composer.json | Dependencias de PHP |

### Explotación de fuga de repositorio Git
```python
import requests

target = "https://target.com"

# 1. Comprobar .git/HEAD
r = requests.get(f"{target}/.git/HEAD")
if r.status_code == 200 and "ref:" in r.text:
    print("[!] ¡Fuga de repositorio Git!")
    # 2. Intentar obtener el ref
    ref_path = r.text.strip().split("ref: ")[1] if "ref: " in r.text else ""
    if ref_path:
        r2 = requests.get(f"{target}/.git/{ref_path}")
        if r2.status_code == 200:
            print(f"[+] Git ref: {r2.text.strip()}")

# 3. Intentar obtener config
r3 = requests.get(f"{target}/.git/config")
if r3.status_code == 200:
    print(f"[+] Git config:\n{r3.text}")
```

## 6. Consulta de sitios vecinos (dominios que comparten la misma IP)

### Métodos de consulta
1. **Stool ChinaZ** — https://stool.chinaz.com/same
2. **ThreatBook (Weibu)** — https://x.threatbook.cn
3. **crt.sh** — consultar dominios asociados por IP mediante certificados
4. **Censys** — https://search.censys.io

### Consulta de sitios vecinos con python_execute
```python
import requests, json

ip = "1.2.3.4"

# Método 1: consultar certificados de la misma IP en crt.sh
r = requests.get(f"https://crt.sh/?q={ip}&output=json", timeout=15)
if r.status_code == 200:
    domains = set()
    for entry in r.json():
        for name in entry.get('name_value', '').split('\n'):
            if name.strip() and '*' not in name:
                domains.add(name.strip())
    print(f"[+] Dominios en la misma IP ({len(domains)}):")
    for d in sorted(domains):
        print(f"  - {d}")
```

## 7. Consulta de segmento C (hosts activos en la misma subred)

### Escaneo de segmento C con python_execute
```python
import requests, socket
from concurrent.futures import ThreadPoolExecutor

# Obtener la IP a partir del dominio
domain = "target.com"
ip = socket.gethostbyname(domain)
# Extraer el segmento C
c_segment = ".".join(ip.split(".")[:3])

def check_host(ip, timeout=1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((ip, 80))
        s.close()
        if result == 0:
            return ip
    except:
        pass
    return None

# Escanear el segmento C (1-254)
alive_hosts = []
with ThreadPoolExecutor(max_workers=50) as executor:
    ips = [f"{c_segment}.{i}" for i in range(1, 255)]
    results = executor.map(check_host, ips)
    alive_hosts = [ip for ip in results if ip]

print(f"[+] Hosts activos en el segmento C: {alive_hosts}")
```

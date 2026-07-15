# Manual de Uso de Herramientas OSINT

## 1. crt.sh — Consulta de subdominios por transparencia de certificados

### Uso
```python
import requests

def query_crtsh(domain):
    """Consulta subdominios a través de crt.sh"""
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            data = r.json()
            subdomains = set()
            for entry in data:
                name = entry.get('name_value', '')
                for n in name.split('\n'):
                    n = n.strip().lower()
                    if n and '*' not in n:
                        subdomains.add(n)
            return sorted(subdomains)
    except Exception as e:
        return [f"Error en la consulta: {e}"]
    return []
```

### Notas
- crt.sh puede ser lento; establecer un tiempo de espera de 30s
- Los resultados incluyen certificados comodín (`*.example.com`), que deben filtrarse
- Devolver tras eliminar duplicados

## 2. GitHub API — Búsqueda de código y usuarios

### Búsqueda de código (detección de filtraciones)
```python
def search_github_code(query, max_results=10):
    """Busca código en GitHub (detecta filtraciones de claves/configuración)"""
    url = "https://api.github.com/search/code"
    params = {'q': query, 'per_page': max_results}
    headers = {'Accept': 'application/vnd.github.v3+json'}
    
    r = requests.get(url, params=params, headers=headers)
    if r.status_code == 200:
        items = r.json().get('items', [])
        return [{
            'repo': item['repository']['full_name'],
            'path': item['path'],
            'url': item['html_url'],
        } for item in items]
    return []
```

### Dorks de búsqueda habituales
```
"domain.com" password
"domain.com" api_key
"domain.com" secret
"domain.com" .env
filename:.env domain.com
filename:config domain.com
org:company-name password
```

## 3. Consultas DNS

### Consulta DNS integrada en Python
```python
import socket

def dns_lookup(domain):
    """Consulta DNS básica"""
    results = {}
    try:
        # Registro A
        results['A'] = socket.gethostbyname_ex(domain)[2]
    except:
        results['A'] = 'Error de resolución'
    
    return results
```

### Consulta DNS completa (requiere dnspython)
```python
# Si el entorno tiene dnspython
try:
    import dns.resolver
    
    def full_dns_lookup(domain):
        record_types = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS']
        results = {}
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                results[rtype] = [str(r) for r in answers]
            except:
                pass
        return results
except ImportError:
    pass
```

## 4. Consulta WHOIS

### API WHOIS en línea
```python
def whois_lookup(domain):
    """Consulta WHOIS a través de una API en línea"""
    # Usa la API gratuita de whoisjson.com
    url = f"https://whoisjson.com/api/v1/whois?domain={domain}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {
                'registrar': data.get('registrar'),
                'creation_date': data.get('creation_date'),
                'expiration_date': data.get('expiration_date'),
                'name_servers': data.get('name_servers'),
                'registrant': data.get('registrant'),
            }
    except:
        pass
    return {}
```

## 5. Google Dorking

### Sintaxis de búsqueda habitual
| Sintaxis | Uso | Ejemplo |
|------|------|------|
| `site:` | Limitar a un dominio | `site:github.com "unclec"` |
| `intitle:` | Palabra clave en el título | `intitle:"index of" site:example.com` |
| `inurl:` | Palabra clave en la URL | `inurl:admin site:example.com` |
| `filetype:` | Tipo de archivo | `filetype:pdf site:example.com` |
| `"frase exacta"` | Coincidencia exacta | `"UncleCheng" security` |
| `related:` | Sitios relacionados | `related:github.com` |

### Dorks habituales para recopilación de información
```
site:github.com "nombre_de_usuario_objetivo"
site:bilibili.com "nombre_de_usuario_objetivo"
site:zhihu.com "nombre_de_usuario_objetivo"
"correo@domain.com"
"número de teléfono"
```

## 6. Shodan/Censys (requiere API Key)

### Búsqueda en Shodan
```python
def shodan_search(api_key, query):
    import shodan
    api = shodan.Shodan(api_key)
    try:
        results = api.search(query)
        return [{
            'ip': result['ip_str'],
            'port': result['port'],
            'org': result.get('org', ''),
            'data': result['data'][:200],
        } for result in results['matches'][:10]]
    except Exception as e:
        return [f"Error en la consulta Shodan: {e}"]
```

## 7. Wayback Machine

### Consulta de instantáneas históricas
```python
def wayback_query(domain):
    """Consulta instantáneas históricas en Wayback Machine"""
    url = f"http://archive.org/wayback/available?url={domain}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            snapshots = data.get('archived_snapshots', {})
            if snapshots.get('closest'):
                return snapshots['closest']['url']
    except:
        pass
    return None
```

## 8. Consulta de sitios vecinos (dominios que comparten la misma IP)

### Herramientas en línea
| Herramienta | URL | Descripción |
|------|-----|------|
| Stool ChinaZ | https://stool.chinaz.com/same | La más usada en China |
| ThreatBook (Weibu) | https://x.threatbook.cn | Inteligencia de amenazas + sitios vecinos |
| crt.sh | https://crt.sh | Consultar dominios asociados por IP mediante certificados |
| Censys | https://search.censys.io | Búsqueda global de activos |
| Fofa | https://fofa.info | Motor de búsqueda de ciberespacio |

### Consulta de sitios vecinos con python_execute
```python
import requests

def reverse_ip_lookup(ip):
    """Consulta inversa de dominios en la misma IP a través de crt.sh"""
    domains = set()
    try:
        r = requests.get(f"https://crt.sh/?q={ip}&output=json", timeout=30)
        if r.status_code == 200:
            for entry in r.json():
                for name in entry.get('name_value', '').split('\n'):
                    name = name.strip()
                    if name and '*' not in name:
                        domains.add(name)
    except Exception as e:
        print(f"Error en la consulta crt.sh: {e}")
    return sorted(domains)

# Uso
ip = "1.2.3.4"
result = reverse_ip_lookup(ip)
print(f"[+] Dominios en la misma IP ({len(result)}):")
for d in result:
    print(f"  - {d}")
```

## 9. Consulta de segmento C (hosts activos en la misma subred)

### Herramientas en línea
| Herramienta | URL | Descripción |
|------|-----|------|
| Fofa | https://fofa.info | `ip="1.2.3.0/24"` |
| Shodan | https://www.shodan.io | `net:1.2.3.0/24` |
| Censys | https://search.censys.io | `ip:/1.2.3.0-1.2.3.255/` |

### Escaneo de segmento C con python_execute
```python
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_c_segment(ip, timeout=1, max_workers=100):
    """Escanea hosts activos en el segmento C"""
    prefix = ".".join(ip.split(".")[:3])
    alive = []

    def check(host_ip):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((host_ip, 80))
            s.close()
            if result == 0:
                return host_ip
        except:
            pass
        return None

    targets = [f"{prefix}.{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check, t): t for t in targets}
        for future in as_completed(futures):
            result = future.result()
            if result:
                alive.append(result)

    return sorted(alive, key=lambda x: int(x.split(".")[-1]))

# Uso
ip = "1.2.3.4"
hosts = scan_c_segment(ip)
print(f"[+] Hosts activos en el segmento C ({len(hosts)}):")
for h in hosts:
    print(f"  - {h}")
```

## 10. Consulta de registro ICP (China)

### Herramientas en línea
| Herramienta | URL | Descripción |
|------|-----|------|
| Consulta oficial del MIIT | https://beian.miit.gov.cn | Fuente oficial |
| Consulta de registro ChinaZ | https://icp.chinaz.com | Consulta rápida |
| Tianyancha | https://www.tianyancha.com | Relación empresa + registro |
| Consulta de registro Aizhan | https://www.aizhan.com/cha/ | Consulta por lotes |

### Consulta de registro ICP con python_execute
```python
import requests

def icp_lookup(domain):
    """Consulta información de registro ICP (mediante API pública)"""
    # Método 1: usar la API de ChinaZ (requiere API key)
    # Método 2: usar una interfaz de consulta pública
    try:
        # Consultar información de dominios chinos mediante whois
        url = f"https://whois.chinaz.com/{domain}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, headers=headers, timeout=10)
        # Analizar la información de registro
        import re
        icp_match = re.search(r'备案号[：:]\s*([^<\s]+)', r.text)
        if icp_match:
            return icp_match.group(1)
    except:
        pass

    # Si es un dominio extranjero, normalmente no tiene registro ICP
    return "No se encontró registro (posiblemente dominio extranjero)"
```

## 11. Descubrimiento de subdominios (métodos múltiples)

### Estrategia combinada de métodos
1. **crt.sh** — transparencia de certificados (el más rápido)
2. **Dorks de motores de búsqueda** — búsquedas site: en Google/Bing
3. **Fuerza bruta DNS** — diccionario de prefijos comunes
4. **Transferencia de zona DNS** — intentar axfr
5. **Análisis de archivos JS** — extraer subdominios de los JS de la página

### Fuerza bruta de subdominios con python_execute
```python
import socket
from concurrent.futures import ThreadPoolExecutor

def subdomain_brute(domain, wordlist=None, max_workers=20):
    """Fuerza bruta de subdominios"""
    if wordlist is None:
        wordlist = [
            'www', 'mail', 'ftp', 'admin', 'blog', 'dev', 'staging',
            'api', 'test', 'portal', 'cdn', 'ns1', 'ns2', 'mx',
            'app', 'web', 'git', 'ci', 'jenkins', 'jira',
            'vpn', 'remote', 'shop', 'store', 'news',
        ]

    found = []
    def check(sub):
        fqdn = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(fqdn)
            return (fqdn, ip)
        except:
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(check, wordlist)
        found = [r for r in results if r]

    return sorted(found, key=lambda x: x[0])

# Uso
domain = "example.com"
subs = subdomain_brute(domain)
print(f"[+] Subdominios descubiertos ({len(subs)}):")
for sub, ip in subs:
    print(f"  - {sub} → {ip}")
```

### Intento de transferencia de zona DNS
```python
import socket

def try_zone_transfer(domain):
    """Intenta una transferencia de zona DNS"""
    # Obtener registros NS
    try:
        ns_servers = socket.getaddrinfo(domain, None)
    except:
        return []

    # Intentar la transferencia de zona en cada servidor NS
    # Nota: los servidores DNS modernos suelen tener esta función deshabilitada
    import subprocess
    results = []
    try:
        result = subprocess.run(
            ['dig', 'axfr', domain, '@' + domain],
            capture_output=True, text=True, timeout=10
        )
        if 'XFR size' in result.stdout:
            results.append(result.stdout)
    except:
        pass

    return results
```

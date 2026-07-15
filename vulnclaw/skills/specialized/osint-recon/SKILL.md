---
name: osint-recon
description: Base de conocimiento de recopilación de inteligencia de fuentes abiertas (OSINT) — modelo de recopilación de información en cuatro dimensiones (servidor → sitio web → dominio → personas), la dimensión cuatro (información de personas) se activa condicionalmente
routing:
  phases: [recon]
  task_types: [osint, recon]
---

# Base de conocimiento de recopilación de inteligencia OSINT

Base de conocimiento práctica para escenarios de recopilación de información/reconocimiento/ingeniería social, que proporciona un **modelo de recopilación de información en cuatro dimensiones** (información del servidor → información del sitio web → información del dominio → información de personas), junto con métodos concretos de uso de herramientas y técnicas de extracción de datos.

**Diferencia con la Skill `recon`**:
- `recon` → reconocimiento a nivel técnico (escaneo de puertos, DNS, enumeración de directorios) — versión básica
- `osint-recon` → reconocimiento en todas las dimensiones (servidor + sitio web + dominio + personas/ingeniería social) — versión profunda

## Principios fundamentales

1. **Cobertura completa de las cuatro dimensiones** — las dimensiones de servidor/sitio web/dominio siempre se ejecutan, la dimensión de personas se activa condicionalmente
2. **Extraer de la página todo lo que se pueda extraer** — no solo mirar las cabeceras HTTP, también el contenido HTML, archivos JS, comentarios
3. **Primero pasivo, luego activo** — primero revisar cabeceras de respuesta, DNS, WHOIS (pasivo), luego hacer escaneo de puertos/enumeración de directorios (activo)
4. **Autoevaluación de completitud por dimensión** — en cada ronda revisar qué dimensiones están completas ✅ y cuáles no ❌, solo permitir [DONE] cuando todas estén completas
5. **Los enlaces externos son pistas** — cada enlace externo en la página puede ser una fuente de información
6. **Salida estructurada** — resumir todos los hallazgos en un informe Markdown

## Modelo de recopilación de información en cuatro dimensiones

### Dimensión uno: información del servidor
| Elemento a revisar | Herramienta/método | Descripción |
|--------|----------|------|
| Puertos abiertos y versión de servicios | MCP nmap / `python_execute` + socket | Escaneo de todos los puertos o puertos comunes (21/22/80/443/3306/6379/8080/8443) |
| Detección de IP real | Historial de DNS / Ping global / extracción de cabeceras de correo | IP del servidor de origen detrás de un CDN — SecurityTrails/DNSHistory/Ping global |
| Fingerprint del sistema operativo | Inferencia por TTL + detección de OS de nmap | Linux TTL≈64, Windows TTL≈128, Unix TTL≈255 |
| Versión del middleware | Cabecera de respuesta Server + páginas de error + archivos característicos | Identificación de versiones de Apache/Nginx/IIS/Tomcat |
| Identificación de bases de datos | Sondeo de puertos + mensajes de error + comportamiento característico | MySQL(3306)/Redis(6379)/MongoDB(27017)/MSSQL(1433) |

### Dimensión dos: información del sitio web
| Elemento a revisar | Herramienta/método | Descripción |
|--------|----------|------|
| Arquitectura del sitio | Cabeceras de respuesta + características de la página + librerías JS | SO + middleware + base de datos + lenguaje + framework → stack tecnológico completo |
| Fingerprint Web | `fetch` + coincidencia de características de respuesta | Tipo de CMS, framework frontend, librerías JS, motor de plantillas |
| Detección de WAF | Lógica de wafw00f + características de respuesta | Páginas de bloqueo/cabeceras de respuesta especiales/códigos de estado anómalos |
| Directorios y archivos sensibles | `python_execute` + diccionario de rutas comunes | /admin /backup /config /api /robots.txt /sitemap.xml |
| Filtración de código fuente | Revisar rutas de filtración comunes | .git/.svn/.DS_Store/.env/web.config/archivos de respaldo (.bak/.swp/.old) |
| Consulta de sitios vecinos (mismo servidor) | Búsqueda inversa de dominios por la misma IP | Herramientas de webmaster/ThreatBook/consulta de misma IP en crt.sh |
| Consulta de segmento C | Escaneo de hosts activos en el mismo segmento de red | Escaneo de nmap -sn en el segmento /24 |

### Dimensión tres: información del dominio
| Elemento a revisar | Herramienta/método | Descripción |
|--------|----------|------|
| Información de registro WHOIS | `python_execute` + API/comando whois | Registrante/registrador/servidores NS/fecha de registro/fecha de expiración |
| Información de registro ICP | API de consulta de registro del Ministerio de Industria y TI de China | Solo se debe consultar para dominios de China continental, los dominios extranjeros no tienen registro ICP |
| Descubrimiento de subdominios | crt.sh + fuerza bruta + motores de búsqueda + transferencia de zona DNS | Verificación cruzada con varios métodos, garantizando cobertura completa |
| Registros DNS completos | `python_execute` + dnspython/socket | Consulta completa de A/CNAME/MX/TXT/NS/SPF/SOA |
| Logs de transparencia de certificados | crt.sh / Censys / certspotter | Descubrir certificados históricos, subdominios, dominios relacionados |

### Dimensión cuatro: información de personas activación condicional ⚡
**Atención: esta dimensión solo se ejecuta si se cumple alguna de las siguientes condiciones:**
- El comando del usuario menciona explícitamente "ingeniería social/social engineering/información de personas/rastreo de autor/perfil de persona", etc.
- El sitio web objetivo tiene información de autor explícita (meta author, página about, información de contacto)

**Casos en los que NO se debe hacer ingeniería social**: sitio web corporativo ordinario sin autor personal / el usuario solo pide "escanear el objetivo" / el objetivo es una IP/dirección de red interna

| Dirección de rastreo | Método | Descripción |
|----------|------|------|
| Extracción de identificador de autor | meta author de la página, página about | Nombre de usuario, apodo, correo electrónico |
| Rastreo en GitHub | `fetch` + API de GitHub | Repositorios, preferencias de lenguaje, historial de contribuciones, correo electrónico |
| Redes sociales | Extraer enlaces de la página → visitarlos | Bilibili, Weibo, Zhihu, Twitter, LinkedIn |
| Correlación entre plataformas | Buscar en otras plataformas con nombre de usuario/correo | Búsqueda del mismo ID en distintas plataformas |
| Commits históricos | Commits de GitHub → correo de los commits | Correlacionar con otros proyectos e identidades |
| Detección de filtraciones | Búsqueda en el historial de código de GitHub | Filtración de .env, config, claves |

## Flujo de trabajo First-Pass

1. **Acceder al objetivo** → `fetch` para obtener la página principal, extraer cabeceras HTTP + contenido HTML
2. **Dimensión uno: información del servidor** → escaneo de puertos, IP real, fingerprint de SO, identificación de middleware/base de datos
3. **Dimensión dos: información del sitio web** → fingerprint Web, detección de WAF, directorios sensibles/filtración de código fuente, sitios vecinos/segmento C
4. **Dimensión tres: información del dominio** → WHOIS, registro ICP, subdominios, registros DNS, transparencia de certificados
5. **Dimensión cuatro (activación condicional)** → extracción de información de autor, rastreo entre plataformas, resumen de información
6. **Autoevaluación de completitud por dimensión** → confirmar que cada dimensión tuvo al menos una ronda de revisión
7. **Informe resumen** → generar el informe de reconocimiento en formato Markdown

## Enrutamiento de escenarios

| Escenario | Documento de referencia | Contenido principal |
|------|---------|---------|
| Recopilación de información del servidor | `server-recon.md` | Escaneo de puertos, IP real, fingerprint de SO, identificación de middleware/base de datos |
| Recopilación de información del sitio web | `website-recon.md` | Arquitectura/fingerprint/WAF/directorios sensibles/filtración de código fuente/sitios vecinos/segmento C |
| Identificación de fingerprint Web | `web-fingerprinting.md` | Detección de framework, identificación de versión, inferencia de stack tecnológico |
| Método de rastreo de autor | `author-tracking.md` | Extraer autor de la página → rastreo entre plataformas → resumen de información |
| Uso de herramientas OSINT | `osint-toolkit.md` | crt.sh, API de GitHub, dorks de motores de búsqueda, sitios vecinos/segmento C/ICP |
| Resumen de inteligencia de ingeniería social | `social-engineering-intel.md` | Perfil de persona, red de relaciones, verificación cruzada de información |
| Plantilla de informe de reconocimiento | `recon-report-template.md` | Formato estándar de informe Markdown (cuatro dimensiones) |

## ⭐ Fragmentos de código de extracción de uso frecuente

### Extraer todos los enlaces externos del HTML
```python
import re
html = "..."  # HTML obtenido con fetch
links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
for link in set(links):
    print(link)
```

### Extraer información de autor del HTML
```python
import re
# meta author
author = re.findall(r'<meta\s+name=["\']author["\']\s+content=["\']([^"\']+)["\']', html)
# enlaces a página about
about_links = re.findall(r'href=["\']([^"\']*(?:about|me|contact)[^"\']*)["\']', html, re.I)
```

### Consultar subdominios en crt.sh
```python
import requests
domain = "example.com"
r = requests.get(f"https://crt.sh/?q=%.{domain}&output=json")
if r.status_code == 200:
    for entry in r.json():
        print(entry['name_value'])
```

### Información de usuario de GitHub
```python
import requests
username = "target_user"
r = requests.get(f"https://api.github.com/users/{username}")
if r.status_code == 200:
    data = r.json()
    print(f"Name: {data.get('name')}")
    print(f"Bio: {data.get('bio')}")
    print(f"Email: {data.get('email')}")
    print(f"Blog: {data.get('blog')}")
    print(f"Location: {data.get('location')}")
    print(f"Company: {data.get('company')}")
```

### Detección de WAF (método de características de respuesta)
```python
import requests
url = "https://target.com"
# Petición normal
r1 = requests.get(url)
# Petición que activa el WAF (con características de ataque)
r2 = requests.get(url + "/?id=1' OR 1=1--")
# Comparar respuestas
if r1.status_code != r2.status_code or len(r1.text) != len(r2.text):
    print("[!] Posible presencia de WAF")
    print(f"Código de estado normal: {r1.status_code}, código de estado de ataque: {r2.status_code}")
```

### Consulta de sitios vecinos (búsqueda inversa de dominios por la misma IP)
```python
import requests
ip = "1.2.3.4"
# Usar la API de chinaz u otra interfaz de búsqueda inversa
# También se puede consultar en crt.sh certificados de la misma IP
r = requests.get(f"https://crt.sh/?q={ip}&output=json")
```

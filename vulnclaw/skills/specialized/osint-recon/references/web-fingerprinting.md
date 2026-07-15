# Identificación de Huella Digital Web

## Lista de comprobación

### Huella en las cabeceras de respuesta HTTP
| Cabecera | Información inferida | Ejemplo |
|--------|---------|------|
| `Server` | Servidor web | `nginx/1.18.0`, `Apache/2.4.41`, `GitHub.com` |
| `X-Powered-By` | Lenguaje/framework de backend | `PHP/7.4.3`, `Express`, `Next.js` |
| `X-AspNet-Version` | Versión de .NET | `4.0.30319` |
| `Set-Cookie` | Característica del framework | `PHPSESSID`→PHP, `JSESSIONID`→Java, `csrf_token`→Django |
| `X-Generator` | CMS | `Hugo`, `WordPress`, `Ghost` |
| `X-DRupal-Cache` | CMS | Drupal |
| `Via` | Proxy/CDN | `1.1 varnish`→CDN Varnish |

### Huella en el código fuente HTML
```python
import re

# WordPress
wp_signs = ['wp-content', 'wp-includes', 'wordpress']
# Hexo
hexo_signs = ['hexo', 'hexo-theme']
# Hugo
hugo_signs = ['hugo', 'gohugo']
# Jekyll
jekyll_signs = ['jekyll']
# Next.js
next_signs = ['__NEXT_DATA__', '_next/']
# Vue
vue_signs = ['data-v-', '__vue__']
# React
react_signs = ['data-reactroot', '__react']

def detect_framework(html):
    html_lower = html.lower()
    frameworks = []
    checks = {
        'WordPress': wp_signs,
        'Hexo': hexo_signs,
        'Hugo': hugo_signs,
        'Jekyll': jekyll_signs,
        'Next.js': next_signs,
        'Vue': vue_signs,
        'React': react_signs,
    }
    for name, signs in checks.items():
        if any(s in html_lower for s in signs):
            frameworks.append(name)
    return frameworks
```

### Huella en archivos JavaScript
- Rutas de archivos JS propias de cada framework: `/wp-includes/js/` → WordPress
- Detección de Vue/React DevTools: `__VUE_DEVTOOLS_GLOBAL_HOOK__`, `__REACT_DEVTOOLS_GLOBAL_HOOK__`
- La versión del framework suele aparecer en comentarios o variables de JS

### Huella en CSS
- `/wp-content/themes/` → WordPress
- Nombres de clases característicos de temas Hexo
- Características de clases de Bootstrap/Tailwind

### Archivos característicos
| Ruta de archivo | Información inferida |
|---------|---------|
| `/robots.txt` | Información del CMS, rutas ocultas |
| `/sitemap.xml` | Estructura del sitio |
| `/favicon.ico` | Icono por defecto del framework |
| `/.well-known/security.txt` | Contacto de seguridad |
| `/humans.txt` | Información del desarrollador |
| `/.git/HEAD` | Fuga del repositorio Git |
| `/.env` | Fuga de variables de entorno |

## Características de GitHub Pages
- Cabecera de respuesta `Server: GitHub.com`
- Presencia de `X-GitHub-Request-Id`
- `X-Cache: HIT` + `X-Fastly-Request-ID` → CDN Fastly
- `Via: 1.1 varnish` → caché Varnish
- Frameworks comunes: Jekyll, Hexo, Hugo

---

## Detección de WAF

### Características habituales de identificación de WAF
| WAF | Cabecera de respuesta/característica de la página | Código de estado de bloqueo |
|-----|----------------|-----------|
| Cloudflare | `Server: cloudflare`, `CF-Ray` | 403 |
| AWS WAF | `x-amz-request-id`, `x-amz-cf-id` | 403 |
| Alibaba Cloud WAF | Cookie contiene `acw_tc` | 405/403 |
| Tencent Cloud WAF | Página de bloqueo JSON específica | 403 |
| BT-WAF (aaPanel) | La página de bloqueo contiene "宝塔" (BT/aaPanel) | 403 |
| Safedog | La página de bloqueo contiene "safedog" | 403/404 |
| ModSecurity | 403 específico + cabecera Server | 403 |
| Nginx WAF | `HTTP/1.1 444` o 403 especial | 444/403 |

### Métodos de detección de WAF
1. **Comparación entre petición normal y petición de ataque** — enviar una petición con características de ataque y observar la diferencia en la respuesta
2. **Revisión de cabeceras de respuesta** — algunos WAF añaden cabeceras de respuesta específicas
3. **Revisión de cookies** — algunos WAF establecen cookies de seguimiento
4. **Códigos de estado anómalos** — las peticiones de ataque devuelven códigos de estado anómalos (403/406/429/444)

### Payloads habituales para provocar la detección de WAF
```
/?id=1' OR 1=1--
/?search=<script>alert(1)</script>
/../../../etc/passwd
/?file=php://filter/convert.base64-encode/resource=index
```

---

## Comprobación de fuga de código fuente

### Tipos habituales de fuga de código fuente y su detección
| Tipo | Ruta | Método de detección | Nivel de gravedad |
|------|------|---------|---------|
| Repositorio Git | `/.git/config`, `/.git/HEAD` | 200 y contiene contenido de git | 🔴 Crítico |
| Repositorio SVN | `/.svn/entries` | 200 y contiene contenido de svn | 🔴 Crítico |
| .DS_Store | `/.DS_Store` | Descargar y analizar la estructura de directorios | 🟡 Medio |
| Archivo .env | `/.env` | Contiene DB_PASSWORD, etc. | 🔴 Crítico |
| web.config | `/web.config` | Fuga de configuración de IIS | 🟡 Medio |
| Archivos de respaldo | `/.bak`, `/.swp`, `/.old`, `/.tar.gz` | Descarga directa | 🟡 Medio |
| Docker | `/Dockerfile`, `/docker-compose.yml` | Configuración de contenedor | 🟡 Medio |
| package.json | `/package.json` | Dependencias de Node.js | 🟢 Bajo |
| composer.json | `/composer.json` | Dependencias de PHP | 🟢 Bajo |
| webpack | `/webpack.json`, `/map Files` | Mapa de código fuente | 🟡 Medio |

### Flujo de explotación de fuga de Git
1. Acceder a `/.git/HEAD` → obtener la ruta ref
2. Acceder a `/.git/config` → obtener información del repositorio remoto
3. Acceder a `/.git/objects/` → recorrer los objetos Git
4. Usar herramientas como GitHack/scrabble para recuperar el código fuente automáticamente

### Lista de rutas de escaneo de archivos sensibles
```
/.git/config
/.git/HEAD
/.svn/entries
/.DS_Store
/.env
/.env.bak
/.env.local
/web.config
/config.php
/config.yml
/backup.sql
/database.sql
/db.sql
/phpinfo.php
/test/
/debug/
/console/
/admin/
/wp-config.php
/robots.txt
/sitemap.xml
/.well-known/security.txt
```

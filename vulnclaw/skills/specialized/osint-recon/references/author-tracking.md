# Métodos de Seguimiento del Autor

## Flujo central

```
Extraer identificador del autor en la página → determinar identificador único (usuario/correo) → búsqueda entre plataformas → resumen de información
```

## Paso 1: Extraer el identificador del autor de la página

### Etiquetas Meta de HTML
```python
import re

def extract_author_from_meta(html):
    """Extrae la información del autor a partir de las etiquetas meta de HTML"""
    authors = []
    
    # <meta name="author" content="XXX">
    m = re.findall(r'<meta\s+name=["\']author["\']\s+content=["\']([^"\']+)["\']', html)
    authors.extend(m)
    
    # <meta name="copyright" content="XXX">
    m = re.findall(r'<meta\s+name=["\']copyright["\']\s+content=["\']([^"\']+)["\']', html)
    authors.extend(m)
    
    # Etiquetas OG
    m = re.findall(r'<meta\s+property=["\']article:author["\']\s+content=["\']([^"\']+)["\']', html)
    authors.extend(m)
    
    return list(set(authors))
```

### Extracción de enlaces de la página
```python
def extract_social_links(html):
    """Extrae enlaces de redes sociales de la página"""
    links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
    
    social = {}
    for link in links:
        if 'github.com' in link:
            social['github'] = link
        elif 'bilibili.com' in link:
            social['bilibili'] = link
        elif 'weibo.com' in link or 'weibo.cn' in link:
            social['weibo'] = link
        elif 'zhihu.com' in link:
            social['zhihu'] = link
        elif 'twitter.com' in link or 'x.com' in link:
            social['twitter'] = link
        elif 'linkedin.com' in link:
            social['linkedin'] = link
        elif 'youtube.com' in link:
            social['youtube'] = link
        elif 'facebook.com' in link:
            social['facebook'] = link
    
    return social
```

## Paso 2: Seguimiento en GitHub

### API de información de usuario
```python
import requests

def get_github_profile(username):
    """Obtiene la información pública del usuario de GitHub"""
    r = requests.get(f"https://api.github.com/users/{username}")
    if r.status_code != 200:
        return None
    
    data = r.json()
    return {
        'name': data.get('name'),
        'bio': data.get('bio'),
        'email': data.get('email'),
        'blog': data.get('blog'),
        'location': data.get('location'),
        'company': data.get('company'),
        'public_repos': data.get('public_repos'),
        'followers': data.get('followers'),
        'following': data.get('following'),
        'created_at': data.get('created_at'),
        'avatar_url': data.get('avatar_url'),
    }

def get_github_repos(username):
    """Obtiene los repositorios públicos del usuario (para inferir el stack tecnológico)"""
    r = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100")
    if r.status_code != 200:
        return []
    
    repos = r.json()
    languages = {}
    for repo in repos:
        lang = repo.get('language')
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
    
    return {
        'top_languages': sorted(languages.items(), key=lambda x: -x[1])[:5],
        'repo_count': len(repos),
        'starred_total': sum(r.get('stargazers_count', 0) for r in repos),
    }
```

### Extracción de correos a partir del historial de commits de GitHub
```python
def get_github_commit_email(username, repo):
    """Extrae el correo del autor a partir del historial de commits de GitHub"""
    r = requests.get(f"https://api.github.com/repos/{username}/{repo}/commits?per_page=10")
    if r.status_code != 200:
        return []
    
    emails = set()
    for commit in r.json():
        author = commit.get('commit', {}).get('author', {})
        if author.get('email'):
            emails.add(author['email'])
    
    return list(emails)
```

## Paso 3: Correlación entre plataformas

### Búsqueda en otras plataformas usando el nombre de usuario
```python
# Detección de plataformas habituales
PLATFORMS = {
    'GitHub': 'https://github.com/{username}',
    'Bilibili': 'https://space.bilibili.com/search?keyword={username}',
    'Zhihu': 'https://www.zhihu.com/search?type=content&q={username}',
    'CSDN': 'https://blog.csdn.net/{username}',
    'Juejin': 'https://juejin.cn/user/{username}',
    'Twitter': 'https://twitter.com/{username}',
    'LinkedIn': 'https://www.linkedin.com/in/{username}',
}

async def cross_platform_search(username, fetch_tool):
    """Busca el nombre de usuario en múltiples plataformas"""
    results = {}
    for platform, url_template in PLATFORMS.items():
        url = url_template.format(username=username)
        try:
            resp = await fetch_tool(url=url)
            if resp.get('status') == 200:
                results[platform] = f"✅ Encontrado ({url})"
            else:
                results[platform] = f"❌ No encontrado"
        except:
            results[platform] = f"⚠️ Fallo en la detección"
    return results
```

## Paso 4: Plantilla de resumen de información

```markdown
## Perfil de la persona: {alias}

### Información básica
- **Alias**: xxx
- **Nombre real**: xxx (si se conoce)
- **Correo**: xxx
- **Ubicación**: xxx
- **Profesión/empresa**: xxx

### Perfil técnico
- **Lenguaje principal**: Python / JavaScript / ...
- **Preferencia de stack tecnológico**: ...
- **Contribuciones de código abierto**: N repositorios, M estrellas
- **Áreas de interés**: ...

### Redes sociales
- GitHub: xxx
- Bilibili: xxx
- Zhihu: xxx
- ...

### Información de correlación
- ID idéntico entre plataformas: xxx
- Proyectos conocidos: xxx
- Filtraciones históricas: xxx
```

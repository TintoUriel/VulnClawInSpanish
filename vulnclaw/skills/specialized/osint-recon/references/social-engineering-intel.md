# Resumen de Información de Ingeniería Social

## Marco de construcción del perfil de la persona

### Dimensiones de información

| Dimensión | Fuente de datos | Método de extracción |
|------|--------|---------|
| Identificación | meta de la página, GitHub | Extracción por regex de author/copyright |
| Redes sociales | Enlaces externos de la página | Coincidencia de `<a href>` con dominios de redes sociales |
| Preferencias técnicas | Distribución de lenguajes en repositorios de GitHub | GitHub API |
| Ubicación geográfica | location de GitHub, blog | Página de perfil personal |
| Información profesional | company de GitHub, LinkedIn | Página de perfil personal |
| Datos de contacto | email de GitHub, página de contacto del blog | API + extracción de la página |
| Áreas de interés | Topics de repositorios de GitHub, artículos del blog | Topics de repositorios + categorías de artículos |

## Validación cruzada de la información

### Principios
1. **No confiar en una única fuente** — la información clave requiere al menos 2 fuentes independientes de confirmación
2. **Marcar la vigencia** — anotar el momento en que se obtuvo la información; marcar por separado la información desactualizada
3. **Clasificación por nivel de confianza**:
   - 🟢 **Alto**: confirmado por varias fuentes independientes
   - 🟡 **Medio**: una única fuente confiable
   - 🔴 **Bajo**: inferido/no verificado

### Patrones de correlación habituales

```
Enlace a GitHub en el blog → nombre de usuario de GitHub → obtener correo mediante GitHub API
                                  → obtener repositorios mediante GitHub API → inferir stack tecnológico
                                  → correo de los commits de GitHub → correlacionar con otras identidades

Enlace a Bilibili en el blog → UID de Bilibili → página principal de Bilibili → seguidos/seguidores → etiquetas de interés
                                    → vídeos publicados → área técnica

Nombre de usuario → búsqueda entre plataformas → descubrir más cuentas sociales
Correo → haveibeenpwned → registros de filtración de datos
```

## Extracción de información de redes sociales

### Bilibili
```python
import re

def extract_bilibili_uid(url):
    """Extrae el UID a partir de una URL de Bilibili"""
    # space.bilibili.com/12345
    m = re.search(r'bilibili\.com/(\d+)', url)
    if m:
        return m.group(1)
    return None
```

### Weibo
```python
def extract_weibo_uid(url):
    """Extrae el UID a partir de una URL de Weibo"""
    # weibo.com/u/12345 o weibo.com/username
    m = re.search(r'weibo\.com/(?:u/)?(\w+)', url)
    if m:
        return m.group(1)
    return None
```

### Zhihu
```python
def extract_zhihu_username(url):
    """Extrae el nombre de usuario a partir de una URL de Zhihu"""
    # zhihu.com/people/username
    m = re.search(r'zhihu\.com/people/([^/?]+)', url)
    if m:
        return m.group(1)
    return None
```

## Formato del informe resumen de información

```markdown
# Informe de Reconocimiento del Objetivo

## 📋 Información básica
| Elemento | Contenido | Confianza | Fuente |
|------|------|--------|------|
| Objetivo | https://xxx | - | Entrada del usuario |
| Framework | Hexo | 🟢 | Cabecera HTTP + características HTML |
| Servidor | GitHub Pages | 🟢 | Cabecera Server |
| Autor | XXX | 🟢 | meta author |
| ... | ... | ... | ... |

## 👤 Perfil de la persona
- **Alias**: XXX
- **GitHub**: https://github.com/xxx
- **Bilibili**: https://space.bilibili.com/xxx
- **Stack tecnológico**: Python / JavaScript
- **Ubicación**: Shenzhen
- ...

## 🔗 Hallazgos de correlación
- [Hallazgo 1]
- [Hallazgo 2]

## 📌 Hallazgos clave
1. ...
2. ...

---
*Fecha de generación del informe: AAAA-MM-DD HH:MM*
*Fuentes de datos: sitio web objetivo, GitHub API, información pública de redes sociales*
```

## Privacidad y ética

- ✅ Solo recopilar **información pública** (contenido accesible sin necesidad de iniciar sesión)
- ✅ No intentar iniciar sesión en cuentas ajenas
- ✅ No utilizar la información recopilada para acoso o ataques de ingeniería social
- ✅ Anotar la fuente de la información para asegurar la trazabilidad
- ❌ No recopilar contenido de comunicaciones privadas
- ❌ No utilizar la información para phishing u otras formas de engaño

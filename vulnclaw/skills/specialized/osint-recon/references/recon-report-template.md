# Plantilla de Informe de Reconocimiento

## Instrucciones de uso

Al completar una tarea de recopilación de información, usa la herramienta `python_execute` para
rellenar la siguiente plantilla como informe completo y guardarlo en la ruta indicada por el
usuario o en el escritorio.

## Plantilla de informe en Markdown

```markdown
# 🦞 Informe de Reconocimiento de {objetivo}

> Fecha de generación: {fecha_hora}
> Herramienta: VulnClaw v0.3.3

---

## 1. Resumen del objetivo

| Elemento | Contenido |
|------|------|
| URL objetivo | {url} |
| Dirección IP | {ip} |
| Servidor | {server} |
| Framework/CMS | {framework} |
| CDN | {cdn} |
| Certificado SSL | {ssl_info} |

---

## 2. Reconocimiento técnico

### 2.1 Cabeceras de respuesta HTTP
| Cabecera | Valor | Nota de seguridad |
|--------|---|---------|
| Server | {value} | {punto_de_atencion} |
| X-Powered-By | {value} | Revela el stack tecnológico |
| ... | ... | ... |

### 2.2 Registros DNS
| Tipo | Valor |
|------|---|
| A | {ip} |
| CNAME | {cname} |
| MX | {mx} |
| TXT | {txt} |

### 2.3 Subdominios
| Subdominio | IP | Nota |
|--------|---|------|
| {sub} | {ip} | {nota} |

### 2.4 Puertos abiertos
| Puerto | Servicio | Versión |
|------|------|------|
| 80 | HTTP | nginx/1.18 |
| 443 | HTTPS | nginx/1.18 |

### 2.5 Directorios y archivos
| Ruta | Código de estado | Nota |
|------|--------|------|
| /robots.txt | 200 | {resumen_de_contenido} |
| /sitemap.xml | 200 | {resumen_de_contenido} |
| /.git/HEAD | 403/200 | {si_hay_fuga} |

---

## 3. Reconocimiento de contenido

### 3.1 Metadatos de la página
- **Title**: {title}
- **Description**: {desc}
- **Keywords**: {keywords}
- **Author**: {author}

### 3.2 Enlaces externos
| Enlace | Tipo | Nota |
|------|------|------|
| {url} | GitHub | Página personal |
| {url} | Bilibili | Espacio de vídeos |
| {url} | CDN | Carga de recursos |

### 3.3 Archivos JavaScript
| Archivo | Hallazgo clave |
|------|---------|
| {path} | {api_endpoint/config/key} |

### 3.4 Información oculta
- Comentarios HTML: {comments}
- Campos ocultos: {hidden_fields}
- Correo/contacto: {contacts}

---

## 4. Seguimiento de personas

### 4.1 Información del autor
| Elemento | Contenido | Fuente | Confianza |
|------|------|------|--------|
| Alias | {name} | {source} | 🟢/🟡/🔴 |
| GitHub | {url} | {source} | 🟢 |
| Bilibili | {url} | {source} | 🟢 |
| Correo | {email} | {source} | 🟡 |
| Ubicación | {location} | {source} | 🟡 |

### 4.2 Perfil técnico
- **Lenguajes principales**: {languages}
- **Stack tecnológico**: {stack}
- **Proyectos de código abierto**: {repos}
- **Áreas de interés**: {interests}

### 4.3 Correlación entre plataformas
| Plataforma | Usuario/ID | Nivel de coincidencia | Nota |
|------|----------|--------|------|
| {platform} | {id} | Alto/Medio/Bajo | {nota} |

---

## 5. Hallazgos clave

| # | Hallazgo | Nivel de riesgo | Nota |
|---|------|---------|------|
| 1 | {finding} | 🔴Alto/🟡Medio/🟢Bajo | {detail} |

---

## 6. Recomendaciones

1. {suggestion_1}
2. {suggestion_2}

---

*Este informe fue generado automáticamente por VulnClaw; toda la información procede de fuentes públicas.*
```

## Código Python para guardar el informe

```python
import os
from datetime import datetime

def save_recon_report(target, report_content, output_path=None):
    """Guarda el informe de reconocimiento en un archivo"""
    if not output_path:
        # Guardar en el escritorio por defecto
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        safe_name = re.sub(r'[^\w]', '_', target)[:30]
        date_str = datetime.now().strftime('%Y%m%d_%H%M')
        output_path = os.path.join(desktop, f'{safe_name}_informe_reconocimiento_{date_str}.md')
    
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return output_path
```

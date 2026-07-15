---
name: recon
description: Flujo de recopilación de información — reconocimiento pasivo y activo
routing:
  phases: [recon]
  task_types: [recon]
---

# Skill de Recopilación de Información

Ejecuta reconocimiento pasivo y activo para construir el perfil del objetivo y el mapa de la superficie de ataque.

## Pasos de ejecución

### 1. Reconocimiento pasivo
- Acceder al objetivo mediante la herramienta fetch y recopilar las cabeceras de respuesta HTTP
- Identificar el tipo y versión del servidor, así como el WAF
- Analizar el código fuente HTML en busca de indicios del stack tecnológico

### 2. Reconocimiento activo
- Sondear los puertos web comunes
- Enumerar directorios y rutas
- Verificar archivos sensibles (robots.txt, .env, .git)
- Descubrir endpoints de API

### 3. Identificación del stack tecnológico
- Framework de frontend (React/Vue/Angular/jQuery)
- Framework de backend (Express/Django/Flask/Spring)
- Sistema CMS (WordPress/Joomla/personalizado)
- Tipo de base de datos

### 4. Salida
- Perfil del objetivo (IP/dominio/puertos/servicios/stack tecnológico)
- Mapa de la superficie de ataque (rutas accesibles, API, puntos de acceso administrativos)

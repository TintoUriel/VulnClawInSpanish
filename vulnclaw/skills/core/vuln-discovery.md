---
name: vuln-discovery
description: Flujo de descubrimiento de vulnerabilidades — escaneo de vulnerabilidades basado en los resultados de la recopilación de información
---

# Skill de Descubrimiento de Vulnerabilidades

Descubre sistemáticamente las vulnerabilidades de seguridad presentes en el objetivo, basándose en los resultados de la recopilación de información.

## Pasos de ejecución

### 1. Correlación con CVE conocidos
- Buscar CVE correspondientes según las versiones de servicio identificadas
- Priorizar los niveles Crítico/Alto
- Registrar el ID del CVE, las versiones afectadas y las condiciones de explotación

### 2. Escaneo de vulnerabilidades web
- Detección de inyección SQL
- Detección de XSS (reflejado/almacenado/DOM)
- Detección de SSRF
- Detección de LFI/RFI
- Detección de inyección de comandos
- Detección de vulnerabilidades de carga de archivos

### 3. Detección de defectos de configuración
- Pruebas de credenciales por defecto
- Detección de fuga de información
- Detección de acceso no autorizado
- Detección de configuración CORS
- Detección de configuración HTTPS

### 4. Salida
- Lista de vulnerabilidades (tipo, nivel de gravedad, URL, parámetro, método de verificación)

---
name: web-security-advanced
description: Pruebas de seguridad web avanzadas — familia de ataques de inyección, seguridad de protocolos, vulnerabilidades de autenticación y lógica, seguridad de archivos y despliegue, superficie de ataque web moderna, incluye Playbook completo
routing:
  target_types: [web, api]
  phases: [vuln_discovery, exploitation]
  task_types: [pentest, audit]
  vulnerability_classes:
    - sqli
    - xss
    - ssrf
    - ssti
    - xxe
    - rce
    - deserialization
    - idor
    - csrf
    - cors
    - file_upload
    - path_traversal
    - auth_bypass
    - jwt
    - oauth
    - graphql
    - websocket
    - request_smuggling
    - prototype_pollution
    - business_logic
  exclude_signals: ["无法重放", "签名阻塞", "重放被阻"]
---

# Skill de Pruebas de Seguridad Web Avanzadas

Usa este Skill cuando el objetivo sea una aplicación web, API, gateway o servicio orientado a navegador, y se requieran pruebas sistemáticas de vulnerabilidades.

**Requisito previo**: si la solicitud todavía está controlada por el cliente y la repetición (replay) no es estable, usa primero el Skill `client-reverse`.

## Enrutamiento de escenarios CTF

> Cuando el objetivo sea un reto de CTF (se sabe que hay una flag y se necesita eludir un filtro específico), utiliza primero el Skill `ctf-web` para obtener valores de bypass y payloads concretos:

| Escenario CTF | Enrutar a ctf-web | Documento de referencia |
|---------|---------------|---------|
| Comparación débil de PHP / bypass de tipos | `ctf-web` | `references/php-bypass-cheatsheet.md` |
| Bypass de espacios en inyección de comandos | `ctf-web` | `references/command-injection-bypass.md` |
| eval con/sin eco de salida | `ctf-web` | `references/eval-and-rce-techniques.md` |
| Auditoría de código PHP | `ctf-web` | `references/php-code-audit-checklist.md` |
| Cadenas de inyección SSTI | `ctf-web` | `references/ssti-injection-chains.md` |
| Cadenas de explotación de deserialización | `ctf-web` | `references/deserialization-playbook.md` |
| Subida de archivos → RCE | Este Skill | `references/web-playbook-08-file-vulnerabilities.md` |

**Este Skill se centra en la metodología de pentesting**; para valores de bypass y plantillas de payload de CTF en la práctica, consulta `ctf-web`.

## Enrutamiento de escenarios

| Tipo de superficie de ataque | Referencia preferida |
|-----------|---------|
| Inyección de parámetros (SQLi/XSS/ejecución de comandos/SSTI/XXE) | `references/web-injection.md` |
| Seguridad de protocolos (CORS/GraphQL/WebSocket/OAuth/contrabando de solicitudes) | `references/web-modern-protocols.md` |
| Autenticación y lógica (IDOR/control de acceso indebido/pagos/restablecimiento de contraseña/bypass de autorización) | `references/web-logic-auth.md` |
| Archivos e infraestructura (subida/recorrido de directorios/inclusión/despliegue/caché/CDN/nube) | `references/web-file-infra.md` |
| Seguridad de despliegue | `references/web-deployment-security.md` |

## Flujo de pruebas

### 1. Pruebas de validación de entrada
- Inyección SQL: booleana/temporal/basada en errores/Union/apilada (stacked queries)
- XSS: reflejado/almacenado/DOM/bypass de CSP
- Inyección de comandos: bypass de separadores, bypass de codificación
- SSTI: identificación del motor de plantillas + cadena de RCE
- XXE: inyección de entidades, exfiltración de datos fuera de banda (OOB)
- Deserialización: cadenas de Java/PHP/Python

### 2. Pruebas de autenticación y sesión
- Credenciales por defecto, fuerza bruta
- Defectos de gestión de sesión (fijación/secuestro/cookies inseguras)
- Seguridad de JWT (manipulación de algoritmo/fuerza bruta de clave/algoritmo "none")
- Defectos de configuración de OAuth/OIDC
- Bypass de MFA

### 3. Pruebas de vulnerabilidades de lógica
- Acceso no autorizado (horizontal/vertical)
- Bypass de lógica de negocio (pagos/cupones/votaciones)
- Condiciones de carrera
- IDOR (referencia directa a objetos insegura)

### 4. Pruebas de seguridad de protocolos
- Configuración incorrecta de CORS
- Introspección/inyección en GraphQL
- Autenticación e inyección en WebSocket
- Contrabando de solicitudes HTTP (HTTP request smuggling)
- SSRF (sondeo de red interna/metadatos de nube)

### 5. Seguridad de archivos y despliegue
- Bypass de subida de archivos
- Recorrido de rutas (path traversal)
- LFI/RFI
- Envenenamiento de CDN/caché
- Ataques a la cadena de suministro
- Configuración de seguridad en la nube

## Documentos de referencia

- `references/web-injection.md` — Referencia detallada de ataques de inyección
- `references/web-modern-protocols.md` — Seguridad de protocolos modernos
- `references/web-logic-auth.md` — Vulnerabilidades de autenticación y lógica
- `references/web-file-infra.md` — Seguridad de archivos e infraestructura
- `references/web-deployment-security.md` — Seguridad de despliegue
- `references/web-ai-attack-map.md` — Mapa de ataques Web y IA
- `references/web-playbook-*.md` — Playbooks especializados (23)
</content>

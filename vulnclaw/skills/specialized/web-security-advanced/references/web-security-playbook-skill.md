---
name: web-security-playbook
description: Authorized web security reference for selecting attack categories, payload families, bypass notes, workflow summaries, and mitigations across web, API, JWT, cloud, AI, framework, and WebSocket testing. Use for pentest planning, report drafting, or converting the extracted wiki into narrower web-focused skills.
---

# Web Security Playbook

Usa este skill para pruebas de seguridad autorizadas, validación de defensas, capacitación o trabajo de documentación.

## Cuándo usar

- El usuario necesita una chuleta de pruebas web a nivel de categoría en lugar de una receta de exploit puntual.
- La tarea implica elegir entre múltiples familias de ataque web, estilos de payload o enfoques de bypass.
- El usuario quiere convertir la wiki extraída en skills, checklists, notas o reportes más específicos.

## Cuándo no usar

- Un skill existente más específico ya cubre mejor la solicitud.
- La tarea es principalmente trabajo de red interna, AD, Windows, Exchange o SharePoint.
- El usuario solo necesita una chuleta de herramientas en lugar de guía por familia de ataque.

## Flujo de trabajo

1. Comienza con `references/web-playbook-index.md`, luego reduce a 1-3 archivos de categoría relevantes.
2. Si la solicitud sigue abarcando múltiples familias de ataque, mantén la respuesta agrupada por categoría en lugar de por payload individual.
3. Si se necesita una entrada de payload específica, usa las entradas de referencia empaquetadas en `references/`; cualquier ruta de origen extraída que aún aparezca en las entradas debe tratarse solo como procedencia.
4. Devuelve únicamente las familias de payload, variantes, prerrequisitos, notas de bypass, notas OPSEC y mitigaciones que correspondan al alcance autorizado.
5. Al redactar un nuevo skill, checklist o reporte, reescribe el material seleccionado en el formato objetivo en lugar de copiar archivos de referencia completos.

## Category Map

- Clickjacking: `references/web-playbook-01-clickjacking.md`
- Ataques a la cadena de suministro: `references/web-playbook-02-supply-chain-attacks.md`
- Seguridad de caché y CDN: `references/web-playbook-03-cache-and-cdn-security.md`
- Redirección abierta: `references/web-playbook-04-open-redirect.md`
- Vulnerabilidades de frameworks: `references/web-playbook-05-framework-vulnerabilities.md`
- Contrabando de solicitudes: `references/web-playbook-06-request-smuggling.md`
- Vulnerabilidades de autenticación: `references/web-playbook-07-authentication-vulnerabilities.md`
- Vulnerabilidades de archivos: `references/web-playbook-08-file-vulnerabilities.md`
- Vulnerabilidades de lógica de negocio: `references/web-playbook-09-business-logic-vulnerabilities.md`
- Contaminación de prototipos: `references/web-playbook-10-prototype-pollution.md`
- Vulnerabilidades de seguridad en la nube: `references/web-playbook-11-cloud-security-vulnerabilities.md`
- Seguridad de IA: `references/web-playbook-12-ai-security.md`
- Seguridad de API: `references/web-playbook-13-api-security.md`
- CSRF falsificación de solicitud entre sitios: `references/web-playbook-14-csrf-cross-site-request-forgery.md`
- Seguridad de JWT: `references/web-playbook-15-jwt-security.md`
- Inclusión de archivos LFI/RFI: `references/web-playbook-16-lfi-rfi-file-inclusion.md`
- RCE ejecución remota de código: `references/web-playbook-17-rce-remote-code-execution.md`
- Inyección SQL/NoSQL: `references/web-playbook-18-sql-nosql-injection.md`
- SSRF falsificación de solicitud del lado del servidor: `references/web-playbook-19-ssrf-server-side-request-forgery.md`
- Inyección de plantillas SSTI: `references/web-playbook-20-ssti-template-injection.md`
- Seguridad de WebSocket: `references/web-playbook-21-websocket-security.md`
- XSS cross-site scripting: `references/web-playbook-22-xss-cross-site-scripting.md`
- Inyección de entidades XXE: `references/web-playbook-23-xxe-entity-injection.md`

## Notas

- Prefiere 1-3 categorías por solicitud, no todo el corpus.
- Usa `references/web-playbook-index.md` como primera parada para seleccionar categoría.
- Usa los archivos markdown de origen para comandos detallados y texto tutorial.
- Mantén las salidas limitadas al stack objetivo y a la autorización del usuario.

</content>

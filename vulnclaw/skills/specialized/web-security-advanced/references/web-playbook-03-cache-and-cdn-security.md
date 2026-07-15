# Seguridad de caché y CDN
English: Cache & CDN Security
- Entry Count: 3
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Envenenamiento de caché
- ID: cache-poisoning
- Difficulty: advanced
- Subcategory: Envenenamiento de caché
- Tags: cache, poisoning, web-cache
- Original Extracted Source: original extracted web-security-wiki source/cache-poisoning.md
Description:
Ataque de envenenamiento de caché web (Web Cache Poisoning)
Prerequisites:
- El objetivo usa caché
- La configuración de la clave de caché es inadecuada
Execution Outline:
1. Sondear la caché
2. Cabeceras no incluidas en la clave (unkeyed headers)
3. Envenenamiento de caché
4. Fat GET
## Engaño de caché
- ID: cache-deception
- Difficulty: intermediate
- Subcategory: Deception
- Tags: cache, deception, auth
- Original Extracted Source: original extracted web-security-wiki source/cache-deception.md
Description:
Explotar las diferencias entre la caché web y la resolución de rutas del servidor para inducir a la capa de CDN/caché a cachear páginas dinámicas que contienen información sensible
Prerequisites:
- El objetivo usa CDN o caché de proxy inverso
- Existe una diferencia en la resolución de rutas (el backend ignora el sufijo de la ruta)
- La política de caché se basa en la extensión de la URL
Execution Outline:
1. Sondear el comportamiento de la caché
2. Engaño de caché mediante confusión de rutas
3. Variantes avanzadas de engaño de caché
4. Verificación del flujo de ataque completo
## Bypass de CDN
- ID: cdn-bypass
- Difficulty: intermediate
- Subcategory: CDN
- Tags: cdn, bypass, recon
- Original Extracted Source: original extracted web-security-wiki source/cdn-bypass.md
Description:
Eludir el CDN para encontrar la IP real
Prerequisites:
- El objetivo usa CDN
Execution Outline:
1. DNS histórico
2. Cabeceras de correo electrónico
3. Consulta de historial DNS y transparencia de certificados
4. Sondeo de subdominios y servicios relacionados para encontrar la IP real
</content>

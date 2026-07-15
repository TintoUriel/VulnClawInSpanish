# Inyección de entidades XXE
English: XXE Entity Injection
- Entry Count: 9
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Ataque básico de XXE
- ID: xxe-basic
- Difficulty: intermediate
- Subcategory: Ataque básico
- Tags: xxe, xml, external, entity
- Original Extracted Source: original extracted web-security-wiki source/xxe-basic.md
Description:
Técnicas básicas de ataque de inyección de entidades externas XML
Prerequisites:
- Existe funcionalidad de análisis de XML
- Las entidades externas no están deshabilitadas
Execution Outline:
1. 1. Sondear XXE
2. 2. Lectura de archivos
3. 3. Lectura del código fuente PHP
4. 4. Ataque SSRF
## Ataque de XXE ciego
- ID: xxe-blind
- Difficulty: intermediate
- Subcategory: XXE ciego
- Tags: xxe, blind, oob, xml
- Original Extracted Source: original extracted web-security-wiki source/xxe-blind.md
Description:
Técnicas de ataque XXE sin eco de salida
Prerequisites:
- Existe análisis de XML
- No hay eco directo
Execution Outline:
1. 1. Sondeo de entidad externa
2. 2. Entidad de parámetro
3. 3. Exfiltración de datos OOB
## Ataque de exfiltración OOB con XXE
- ID: xxe-oob
- Difficulty: intermediate
- Subcategory: Exfiltración OOB
- Tags: xxe, oob, exfiltration, xml
- Original Extracted Source: original extracted web-security-wiki source/xxe-oob.md
Description:
Explota técnicas OOB para exfiltrar datos vía XXE
Prerequisites:
- Existe una vulnerabilidad XXE
- Es posible iniciar solicitudes externas
Execution Outline:
1. 1. Exfiltración por HTTP
2. 2. Exfiltración por FTP
3. 3. Exfiltración por DNS
## Ataque combinado XXE+SSRF
- ID: xxe-ssrf
- Difficulty: intermediate
- Subcategory: XXE+SSRF
- Tags: xxe, ssrf, combination, xml
- Original Extracted Source: original extracted web-security-wiki source/xxe-ssrf.md
Description:
Explota XXE para lograr un ataque SSRF
Prerequisites:
- Existe una vulnerabilidad XXE
- Es posible acceder a la red interna
Execution Outline:
1. 1. Escaneo de puertos de la red interna
2. 2. Acceso a servicios de la red interna
## De XXE a RCE
- ID: xxe-rce
- Difficulty: advanced
- Subcategory: De XXE a RCE
- Tags: xxe, rce, php, expect
- Original Extracted Source: original extracted web-security-wiki source/xxe-rce.md
Description:
Explota XXE para lograr ejecución remota de código
Prerequisites:
- Existe una vulnerabilidad XXE
- La extensión expect de PHP está cargada
Execution Outline:
1. 1. RCE mediante la extensión Expect
2. 2. Escritura de WebShell
## Lectura de archivos mediante XXE
- ID: xxe-file-read
- Difficulty: beginner
- Subcategory: Lectura de archivos
- Tags: xxe, file, read, lfi
- Original Extracted Source: original extracted web-security-wiki source/xxe-file-read.md
Description:
Explota XXE para leer archivos del servidor
Prerequisites:
- Existe una vulnerabilidad XXE
- Se tienen permisos de lectura de archivos
Execution Outline:
1. 1. Lectura de archivos Linux
2. 2. Lectura de archivos Windows
3. 3. Lectura de configuración web
4. 4. Lectura del código fuente
## Explotación de DTD externo mediante XXE
- ID: xxe-dtd
- Difficulty: intermediate
- Subcategory: DTD externo
- Tags: xxe, dtd, external, xml
- Original Extracted Source: original extracted web-security-wiki source/xxe-dtd.md
Description:
Explota un archivo DTD externo para realizar un ataque XXE
Prerequisites:
- Existe una vulnerabilidad XXE
- Es posible acceder a un DTD externo
Execution Outline:
1. 1. Alojar un DTD malicioso
2. 2. Referenciar el DTD externo
3. 3. Exfiltración en varios pasos
4. 4. Fuga mediante mensajes de error
## XXE en archivos XLSX
- ID: xxe-xlsx
- Difficulty: intermediate
- Subcategory: XXE en archivos XLSX
- Tags: xxe, xlsx, excel, office
- Original Extracted Source: original extracted web-security-wiki source/xxe-xlsx.md
Description:
Explota archivos XLSX para realizar un ataque XXE
Prerequisites:
- La aplicación analiza archivos XLSX
- Existe una vulnerabilidad XXE
Execution Outline:
1. 1. Descomprimir el archivo XLSX
2. 2. Inyectar el payload XXE
## XXE en archivos DOCX
- ID: xxe-docx
- Difficulty: intermediate
- Subcategory: XXE en archivos DOCX
- Tags: xxe, docx, word, office
- Original Extracted Source: original extracted web-security-wiki source/xxe-docx.md
Description:
Explota archivos DOCX para realizar un ataque XXE
Prerequisites:
- La aplicación analiza archivos DOCX
- Existe una vulnerabilidad XXE
Execution Outline:
1. 1. Descomprimir el archivo DOCX
2. 2. Inyectar el payload XXE
</content>

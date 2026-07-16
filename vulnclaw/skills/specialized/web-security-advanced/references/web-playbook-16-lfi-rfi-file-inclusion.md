# LFI/RFI Inclusión de Archivos
English: LFI/RFI File Inclusion
- Entry Count: 12
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Inclusión Local de Archivos (LFI)
- ID: lfi-basic
- Difficulty: intermediate
- Subcategory: Inclusión local
- Tags: lfi, local, file, inclusion
- Original Extracted Source: original extracted web-security-wiki source/lfi-basic.md
Description:
Técnica de explotación de vulnerabilidad de inclusión local de archivos
Prerequisites:
- Existe funcionalidad de inclusión de archivos
- El usuario puede controlar la ruta de inclusión
Execution Outline:
1. 1. Detectar LFI
2. 2. Leer archivos sensibles
3. 3. Pseudo-protocolos PHP
4. 4. Envenenamiento de logs
## Inclusión Remota de Archivos (RFI)
- ID: rfi-basic
- Difficulty: intermediate
- Subcategory: Inclusión remota
- Tags: rfi, remote, file, inclusion
- Original Extracted Source: original extracted web-security-wiki source/rfi-basic.md
Description:
Técnica de explotación de vulnerabilidad de inclusión remota de archivos
Prerequisites:
- Existe funcionalidad de inclusión de archivos
- allow_url_include=On
- El usuario puede controlar la ruta de inclusión
Execution Outline:
1. 1. Detectar RFI
2. 2. Alojar archivo malicioso
3. 3. Shell inversa
4. 4. Usar el protocolo data
## Envenenamiento de Logs LFI
- ID: lfi-log-poison
- Difficulty: intermediate
- Subcategory: Envenenamiento de logs
- Tags: lfi, log, poison, rce
- Original Extracted Source: original extracted web-security-wiki source/lfi-log-poison.md
Description:
Lograr RCE a partir de LFI mediante envenenamiento de logs
Prerequisites:
- Existe una vulnerabilidad LFI
- Se puede incluir el archivo de log
- El archivo de log es escribible
Execution Outline:
1. 1. Detectar la ubicación del archivo de log
2. 2. Envenenar el User-Agent
3. 3. Envenenar la ruta de la solicitud
4. 4. Ejecutar comandos
## Explotación de Pseudo-protocolos PHP
- ID: lfi-wrapper
- Difficulty: intermediate
- Subcategory: Pseudo-protocolos
- Tags: lfi, wrapper, php, protocol
- Original Extracted Source: original extracted web-security-wiki source/lfi-wrapper.md
Description:
Explotar los pseudo-protocolos de PHP para realizar ataques LFI
Prerequisites:
- Existe una vulnerabilidad LFI
- Entorno PHP
- Los pseudo-protocolos no están deshabilitados
Execution Outline:
1. 1. php://filter
2. 2. php://input
3. 3. Protocolo data://
4. 4. Protocolo phar://
## Técnicas de Recorrido de Directorios
- ID: lfi-traversal
- Difficulty: beginner
- Subcategory: Recorrido de directorios
- Tags: lfi, traversal, bypass, path
- Original Extracted Source: original extracted web-security-wiki source/lfi-traversal.md
Description:
Técnica de bypass de recorrido de directorios en LFI
Prerequisites:
- Existe una vulnerabilidad LFI
- Existe filtrado de rutas
Execution Outline:
1. 1. Recorrido básico
2. 2. Bypass eliminando ../
3. 3. Bypass mediante codificación URL
4. 4. Bypass mediante codificación Unicode
## Ataque de Cadena de Filtros PHP
- ID: lfi-php-filter
- Difficulty: intermediate
- Subcategory: PHP Filter
- Tags: lfi, php, filter, chain
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-filter.md
Description:
Explotar la cadena de filtros PHP para realizar ataques LFI
Prerequisites:
- Existe una vulnerabilidad LFI
- Entorno PHP
- El pseudo-protocolo filter está disponible
Execution Outline:
1. 1. Leer el código fuente
2. 2. Filtros múltiples
3. 3. RCE mediante cadena de filtros
4. 4. Leer archivos de configuración
## Ejecución mediante PHP Input
- ID: lfi-php-input
- Difficulty: intermediate
- Subcategory: PHP Input
- Tags: lfi, php, input, rce
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-input.md
Description:
Ejecutar código PHP mediante php://input
Prerequisites:
- Existe una vulnerabilidad LFI
- allow_url_include=On
- El método POST está disponible
Execution Outline:
1. 1. Ejecución básica
2. 2. Ejecución de comandos
3. 3. Operaciones sobre archivos
4. 4. Shell inversa
## Ataque mediante Protocolo PHP Data
- ID: lfi-php-data
- Difficulty: intermediate
- Subcategory: PHP Data
- Tags: lfi, php, data, protocol
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-data.md
Description:
Ejecutar código PHP mediante el protocolo data://
Prerequisites:
- Existe una vulnerabilidad LFI
- allow_url_include=On
- El protocolo data está disponible
Execution Outline:
1. 1. Ejecución básica
2. 2. Codificación Base64
3. 3. Ejecución de comandos
4. 4. Shell inversa
## Ataque mediante Protocolo PHP Zip
- ID: lfi-php-zip
- Difficulty: intermediate
- Subcategory: PHP Zip
- Tags: lfi, php, zip, archive
- Original Extracted Source: original extracted web-security-wiki source/lfi-php-zip.md
Description:
Explotar el protocolo zip:// para realizar ataques LFI
Prerequisites:
- Existe una vulnerabilidad LFI
- Se puede subir un archivo zip
- El protocolo zip está disponible
Execution Outline:
1. 1. Crear un Zip malicioso
2. 2. Subir el archivo Zip
3. 3. Incluir el archivo Zip
4. 4. Webshell disfrazada de imagen
## Ataque de Deserialización Phar
- ID: lfi-phar
- Difficulty: advanced
- Subcategory: Deserialización Phar
- Tags: lfi, phar, deserialization, rce
- Original Extracted Source: original extracted web-security-wiki source/lfi-phar.md
Description:
Explotar la deserialización de Phar para lograr RCE
Prerequisites:
- Existe una vulnerabilidad LFI
- Entorno PHP
- La extensión phar está disponible
Execution Outline:
1. 1. Crear un archivo Phar
2. 2. Desencadenar la deserialización
3. 3. Phar disfrazado de imagen
4. 4. Cadenas de gadgets comunes
## Inclusión de Archivos de Sesión
- ID: lfi-session
- Difficulty: intermediate
- Subcategory: Inclusión de sesión
- Tags: lfi, session, file, inclusion
- Original Extracted Source: original extracted web-security-wiki source/lfi-session.md
Description:
Explotar el archivo de sesión para realizar ataques LFI
Prerequisites:
- Existe una vulnerabilidad LFI
- Se puede controlar el contenido de la sesión
- Se conoce la ruta de la sesión
Execution Outline:
1. 1. Detectar la ruta de la sesión
2. 2. Controlar el contenido de la sesión
3. 3. Incluir el archivo de sesión
4. 4. Condición de carrera de sesión
## Explotación del Sistema de Archivos Proc
- ID: lfi-proc
- Difficulty: intermediate
- Subcategory: Sistema de archivos Proc
- Tags: lfi, proc, linux, environ
- Original Extracted Source: original extracted web-security-wiki source/lfi-proc.md
Description:
Explotar el sistema de archivos /proc para realizar ataques LFI
Prerequisites:
- Existe una vulnerabilidad LFI
- Sistema Linux
- /proc es accesible
Execution Outline:
1. 1. Leer información de procesos
2. 2. Leer variables de entorno
3. 3. Leer logs mediante fd
4. 4. Leer otros procesos


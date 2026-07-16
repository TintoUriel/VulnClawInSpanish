# RCE Ejecución Remota de Código
English: RCE Remote Code Execution
- Entry Count: 12
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Inyección de comandos
- ID: rce-command-injection
- Difficulty: intermediate
- Subcategory: Inyección de comandos
- Tags: rce, command, injection, os
- Original Extracted Source: original extracted web-security-wiki source/rce-command-injection.md
Description:
Técnicas de ataque de inyección de comandos del sistema operativo
Prerequisites:
- Existe funcionalidad de ejecución de comandos del sistema
- La entrada del usuario no está filtrada
Execution Outline:
1. 1. Detectar la inyección de comandos
2. 2. Inyección de comandos en Linux
3. 3. Inyección de comandos en Windows
4. 4. Inyección de comandos ciega
## Ejecución de código PHP
- ID: rce-php
- Difficulty: intermediate
- Subcategory: Ejecución de código PHP
- Tags: rce, php, code, execution
- Original Extracted Source: original extracted web-security-wiki source/rce-php.md
Description:
Técnicas de explotación de vulnerabilidades de ejecución de código PHP
Prerequisites:
- Existe un punto de ejecución de código PHP
- La entrada del usuario puede controlar el código
Execution Outline:
1. 1. Funciones peligrosas comunes
2. 2. Ejecución de comandos
3. 3. Webshell de una línea
4. 4. Webshell de una línea indetectable (evasión de antivirus)
## RCE mediante cadena de filtros PHP (Filter Chain)
- ID: rce-php-filter
- Difficulty: advanced
- Subcategory: Cadena de filtros PHP
- Tags: rce, php, filter, chain
- Original Extracted Source: original extracted web-security-wiki source/rce-php-filter.md
Description:
Construcción de RCE aprovechando la cadena de filtros PHP (Filter Chain)
Prerequisites:
- Existe una vulnerabilidad de inclusión de archivos
- La versión de PHP soporta cadenas de filtros
Execution Outline:
1. 1. Principio de la cadena de filtros
2. 2. Construcción de la cadena de filtros
3. 3. Uso de herramientas para generarla
4. 4. Ejemplo completo de explotación
## Inyección de comandos ciega
- ID: rce-cmd-blind
- Difficulty: intermediate
- Subcategory: Inyección de comandos ciega
- Tags: rce, blind, command, injection
- Original Extracted Source: original extracted web-security-wiki source/rce-cmd-blind.md
Description:
Técnicas de explotación de inyección de comandos sin reflejo en pantalla
Prerequisites:
- Existe un punto de inyección de comandos
- No hay reflejo directo de la salida
Execution Outline:
1. 1. Inyección ciega temporal
2. 2. Exfiltración vía DNS
3. 3. Exfiltración vía HTTP
4. 4. Exfiltración vía ICMP
## Vulnerabilidades de deserialización
- ID: rce-deserialize
- Difficulty: advanced
- Subcategory: Deserialización
- Tags: rce, deserialize, java, php
- Original Extracted Source: original extracted web-security-wiki source/rce-deserialize.md
Description:
Explotación de vulnerabilidades de deserialización para lograr RCE
Prerequisites:
- Existe un punto de deserialización
- Existe una cadena de Gadgets explotable
Execution Outline:
1. 1. Deserialización en Java
2. 2. Deserialización en PHP
3. 3. Deserialización en Python
4. 4. Deserialización en .NET
## Deserialización en PHP
- ID: rce-deserialize-php
- Difficulty: advanced
- Subcategory: Deserialización en PHP
- Tags: rce, php, deserialize, unserialize
- Original Extracted Source: original extracted web-security-wiki source/rce-deserialize-php.md
Description:
Técnicas de explotación de vulnerabilidades de deserialización en PHP
Prerequisites:
- Existe una llamada a unserialize
- Existe una clase explotable
Execution Outline:
1. 1. Métodos mágicos
2. 2. Construcción de cadena POP
3. 3. Deserialización vía Phar
4. 4. Deserialización de Session
## Deserialización en Java
- ID: rce-deserialize-java
- Difficulty: advanced
- Subcategory: Deserialización en Java
- Tags: rce, java, deserialize, ysoserial
- Original Extracted Source: original extracted web-security-wiki source/rce-deserialize-java.md
Description:
Técnicas de explotación de vulnerabilidades de deserialización en Java
Prerequisites:
- Existe un punto de deserialización en Java
- Existe una cadena de Gadgets
Execution Outline:
1. 1. Cadenas de Gadgets comunes
2. 2. Uso de ysoserial
3. 3. Ataque JRMP
4. 4. Inyección de memshell (webshell en memoria)
## Vulnerabilidad de subida de archivos
- ID: rce-file-upload
- Difficulty: intermediate
- Subcategory: Subida de archivos
- Tags: rce, upload, webshell, file
- Original Extracted Source: original extracted web-security-wiki source/rce-file-upload.md
Description:
Obtención de RCE aprovechando la vulnerabilidad de subida de archivos
Prerequisites:
- Existe funcionalidad de subida de archivos
- Se pueden subir archivos ejecutables
Execution Outline:
1. 1. Subida básica
2. 2. Bypass en el frontend
3. 3. Bypass en el backend
4. 4. Webshell con imagen (imagen troyanizada)
## RCE por inclusión de archivos
- ID: rce-include
- Difficulty: intermediate
- Subcategory: Inclusión de archivos
- Tags: rce, include, lfi, rfi
- Original Extracted Source: original extracted web-security-wiki source/rce-include.md
Description:
Obtención de RCE aprovechando la vulnerabilidad de inclusión de archivos
Prerequisites:
- Existe una vulnerabilidad de inclusión de archivos
- Se puede incluir un archivo malicioso
Execution Outline:
1. 1. Envenenamiento de logs
2. 2. Inclusión de archivo de Session
3. 3. /proc/self/environ
4. 4. Pseudo-protocolos de PHP
## RCE por envenenamiento de logs
- ID: rce-log-poison
- Difficulty: intermediate
- Subcategory: Envenenamiento de logs
- Tags: rce, log, poison, lfi
- Original Extracted Source: original extracted web-security-wiki source/rce-log-poison.md
Description:
Obtención de RCE mediante envenenamiento de logs
Prerequisites:
- Existe una vulnerabilidad de inclusión de archivos
- Se puede leer el archivo de log
Execution Outline:
1. 1. Envenenamiento de logs de Apache
2. 2. Envenenamiento de logs de Nginx
## RCE mediante imagen troyanizada
- ID: rce-image
- Difficulty: intermediate
- Subcategory: Imagen troyanizada
- Tags: rce, image, webshell, upload
- Original Extracted Source: original extracted web-security-wiki source/rce-image.md
Description:
Obtención de RCE mediante una imagen troyanizada
Prerequisites:
- Existe subida de archivos
- Existe inclusión de archivos
Execution Outline:
1. 1. Elaboración de la imagen troyanizada
2. 2. Contenido de la imagen troyanizada
3. 3. Ejecución aprovechando la inclusión de archivos
4. 4. Combinación con .htaccess
## Explotación de .htaccess
- ID: rce-htaccess
- Difficulty: intermediate
- Subcategory: .htaccess
- Tags: rce, htaccess, apache, upload
- Original Extracted Source: original extracted web-security-wiki source/rce-htaccess.md
Description:
Obtención de RCE aprovechando el archivo .htaccess
Prerequisites:
- Servidor Apache
- Se puede subir un archivo .htaccess
Execution Outline:
1. 1. Interpretar otras extensiones
2. 2. Inclusión automática
3. 3. RCE mediante URLs amigables (pseudo-estáticas)
4. 4. Inclusión mediante página de error


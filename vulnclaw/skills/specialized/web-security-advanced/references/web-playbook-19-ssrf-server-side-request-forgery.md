# SSRF falsificación de solicitud del lado del servidor
English: SSRF Server-Side Request Forgery
- Entry Count: 12
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Ataque SSRF básico
- ID: ssrf-basic
- Difficulty: intermediate
- Subcategory: Ataque básico
- Tags: ssrf, server-side, request
- Original Extracted Source: original extracted web-security-wiki source/ssrf-basic.md
Description:
Técnicas básicas de ataque de falsificación de solicitud del lado del servidor
Prerequisites:
- Existe un punto de entrada de URL
- El servidor realiza solicitudes a la URL proporcionada por el usuario
Execution Outline:
1. 1. Sondear el SSRF
2. 2. Escanear puertos de la red interna
3. 3. Acceder a servicios de la red interna
4. 4. Leer archivos locales
## Ataque a metadatos de AWS
- ID: ssrf-cloud-aws
- Difficulty: intermediate
- Subcategory: Metadatos en la nube
- Tags: ssrf, aws, metadata, cloud
- Original Extracted Source: original extracted web-security-wiki source/ssrf-cloud-aws.md
Description:
Uso de SSRF para acceder al servicio de metadatos de AWS EC2
Prerequisites:
- Existe una vulnerabilidad SSRF
- El objetivo se ejecuta en AWS EC2
Execution Outline:
1. 1. Acceder al servicio de metadatos
2. 2. Obtener credenciales IAM
3. 3. Obtener datos de usuario
4. 4. Bypass usando IMDSv2
## Ataque a metadatos de GCP
- ID: ssrf-cloud-gcp
- Difficulty: intermediate
- Subcategory: Metadatos de GCP
- Tags: ssrf, gcp, cloud, metadata
- Original Extracted Source: original extracted web-security-wiki source/ssrf-cloud-gcp.md
Description:
Uso de SSRF para atacar el servicio de metadatos de Google Cloud
Prerequisites:
- Existe una vulnerabilidad SSRF
- El objetivo se ejecuta en un entorno GCP
Execution Outline:
1. 1. Acceder al servicio de metadatos
2. 2. Obtener el token de acceso
3. 3. Obtener información de la cuenta de servicio
4. 4. Obtener información del proyecto
## Ataque a metadatos de Azure
- ID: ssrf-cloud-azure
- Difficulty: intermediate
- Subcategory: Metadatos de Azure
- Tags: ssrf, azure, cloud, metadata
- Original Extracted Source: original extracted web-security-wiki source/ssrf-cloud-azure.md
Description:
Uso de SSRF para atacar el servicio de metadatos de Azure
Prerequisites:
- Existe una vulnerabilidad SSRF
- El objetivo se ejecuta en un entorno Azure
Execution Outline:
1. 1. Acceder al servicio de metadatos
2. 2. Obtener el token de acceso
3. 3. Obtener información de cómputo
4. 4. Obtener información de red
## Explotación de protocolos vía SSRF
- ID: ssrf-protocol
- Difficulty: intermediate
- Subcategory: Explotación de protocolos
- Tags: ssrf, protocol, file, gopher
- Original Extracted Source: original extracted web-security-wiki source/ssrf-protocol.md
Description:
Uso de diversos protocolos para realizar ataques SSRF
Prerequisites:
- Existe una vulnerabilidad SSRF
- El servidor admite múltiples protocolos
Execution Outline:
1. 1. Protocolo File
2. 2. Protocolo Dict
3. 3. Protocolo Gopher
4. 4. Protocolo LDAP
## Ataque con protocolo Gopher
- ID: ssrf-gopher
- Difficulty: advanced
- Subcategory: Ataque Gopher
- Tags: ssrf, gopher, redis, mysql
- Original Extracted Source: original extracted web-security-wiki source/ssrf-gopher.md
Description:
Uso del protocolo Gopher para atacar servicios de la red interna
Prerequisites:
- Existe una vulnerabilidad SSRF
- El servidor admite el protocolo Gopher
Execution Outline:
1. 1. Formato básico de Gopher
2. 2. Ataque a Redis
3. 3. Ataque a MySQL
4. 4. Ataque a FastCGI
## Ataque con protocolo Dict
- ID: ssrf-dict
- Difficulty: intermediate
- Subcategory: Protocolo Dict
- Tags: ssrf, dict, redis, memcached
- Original Extracted Source: original extracted web-security-wiki source/ssrf-dict.md
Description:
Uso del protocolo Dict para sondear y atacar servicios de la red interna
Prerequisites:
- Existe una vulnerabilidad SSRF
- El servidor admite el protocolo Dict
Execution Outline:
1. 1. Formato del protocolo Dict
2. 2. Sondear Redis
3. 3. Sondear Memcached
4. 4. Escritura de archivos en Redis
## Ataque con protocolo File
- ID: ssrf-file
- Difficulty: beginner
- Subcategory: Protocolo File
- Tags: ssrf, file, lfi, read
- Original Extracted Source: original extracted web-security-wiki source/ssrf-file.md
Description:
Uso del protocolo File para leer archivos locales
Prerequisites:
- Existe una vulnerabilidad SSRF
- El servidor admite el protocolo File
Execution Outline:
1. 1. Archivos sensibles de Linux
2. 2. Archivos sensibles de Windows
3. 3. Archivos de configuración web
4. 4. Archivos de entornos en la nube
## Técnicas de bypass de SSRF
- ID: ssrf-bypass
- Difficulty: intermediate
- Subcategory: Técnicas de bypass
- Tags: ssrf, bypass, waf, filter
- Original Extracted Source: original extracted web-security-wiki source/ssrf-bypass.md
Description:
Diversas técnicas para eludir los filtros de SSRF
Prerequisites:
- Existe una vulnerabilidad SSRF
- Existe un mecanismo de filtrado
Execution Outline:
1. 1. Bypass por formato de IP
2. 2. Diferencias en el parseo de URL
3. 3. Bypass mediante redirección
4. 4. DNS rebinding
## Ataque de DNS rebinding
- ID: ssrf-dns-rebinding
- Difficulty: advanced
- Subcategory: DNS rebinding
- Tags: ssrf, dns, rebinding, bypass
- Original Extracted Source: original extracted web-security-wiki source/ssrf-dns-rebinding.md
Description:
Uso de DNS rebinding para eludir las protecciones de SSRF
Prerequisites:
- Existe una vulnerabilidad SSRF
- Existe verificación de resolución DNS
Execution Outline:
1. 1. Principio del DNS rebinding
2. 2. Uso de servicios públicos
3. 3. Montar un servidor DNS propio
4. 4. Flujo del ataque
## SSRF con ataque a Redis
- ID: ssrf-redis
- Difficulty: intermediate
- Subcategory: Ataque a Redis
- Tags: ssrf, redis, rce, webshell
- Original Extracted Source: original extracted web-security-wiki source/ssrf-redis.md
Description:
Uso de SSRF para atacar el servicio Redis de la red interna
Prerequisites:
- Existe una vulnerabilidad SSRF
- Existe un Redis sin autorización en la red interna
Execution Outline:
1. 1. Sondear Redis
2. 2. Escribir una WebShell
3. 3. Escribir una clave pública SSH
4. 4. Escribir una tarea Cron
## SSRF con ataque a MySQL
- ID: ssrf-mysql
- Difficulty: advanced
- Subcategory: Ataque a MySQL
- Tags: ssrf, mysql, gopher, database
- Original Extracted Source: original extracted web-security-wiki source/ssrf-mysql.md
Description:
Uso de SSRF para atacar el servicio MySQL de la red interna
Prerequisites:
- Existe una vulnerabilidad SSRF
- Existe un servicio MySQL en la red interna
- Se conoce el nombre de usuario de MySQL
Execution Outline:
1. 1. Fundamentos del protocolo MySQL
2. 2. Uso de Gopher para atacar MySQL
3. 3. Uso de herramientas para generar el payload
4. 4. Ejecutar comandos SQL

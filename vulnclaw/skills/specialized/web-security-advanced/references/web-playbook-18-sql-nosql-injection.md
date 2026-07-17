# Inyección SQL/NoSQL
English: SQL/NoSQL Injection
- Entry Count: 17
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Inyección MySQL - Sondeo básico
- ID: sqli-mysql-basic
- Difficulty: beginner
- Subcategory: MySQL
- Tags: sqli, mysql, injection, database
- Original Extracted Source: original extracted web-security-wiki source/sqli-mysql-basic.md
Description:
Sondeo básico de inyección en base de datos MySQL y técnicas de extracción de datos
Prerequisites:
- El objetivo tiene un punto de inyección SQL
- La base de datos backend es MySQL
- Conocimiento básico de sintaxis SQL
Execution Outline:
1. 1. Sondear el punto de inyección
2. 2. Determinar el número de columnas
3. 3. Determinar la posición de visualización
4. 4. Obtener información de la base de datos
## Inyección MySQL - Técnicas avanzadas
- ID: sqli-mysql-advanced
- Difficulty: advanced
- Subcategory: MySQL
- Tags: sqli, mysql, advanced, file-read, rce
- Original Extracted Source: original extracted web-security-wiki source/sqli-mysql-advanced.md
Description:
Técnicas avanzadas de inyección MySQL: lectura/escritura de archivos, escalada de privilegios mediante UDF, ejecución de comandos
Prerequisites:
- El usuario MySQL tiene el privilegio FILE
- Se conoce la ruta absoluta del sitio
- La configuración secure_file_priv lo permite
Execution Outline:
1. 1. Detectar el privilegio FILE
2. 2. Obtener la ruta del sitio
3. 3. Leer archivos sensibles
4. 4. Escribir una WebShell
## Inyección MSSQL - Sondeo básico
- ID: sqli-mssql-basic
- Difficulty: intermediate
- Subcategory: MSSQL
- Tags: sqli, mssql, sqlserver, injection
- Original Extracted Source: original extracted web-security-wiki source/sqli-mssql-basic.md
Description:
Técnicas de inyección en base de datos Microsoft SQL Server
Prerequisites:
- El objetivo tiene un punto de inyección SQL
- El backend usa base de datos MSSQL
Execution Outline:
1. 1. Sondear el punto de inyección
2. 2. Obtener información de versión
3. 3. Obtener información de usuario
4. 4. Obtener información de la base de datos
## Inyección MSSQL - Técnicas avanzadas
- ID: sqli-mssql-advanced
- Difficulty: advanced
- Subcategory: MSSQL
- Tags: sqli, mssql, xp_cmdshell, rce
- Original Extracted Source: original extracted web-security-wiki source/sqli-mssql-advanced.md
Description:
Inyección avanzada en MSSQL: ejecución de comandos mediante xp_cmdshell y SP_OACREATE
Prerequisites:
- MSSQL tiene privilegios elevados
- xp_cmdshell está disponible o se puede habilitar
Execution Outline:
1. 1. Detectar el estado de xp_cmdshell
2. 2. Habilitar xp_cmdshell
3. 3. Ejecutar comandos del sistema
4. 4. Escribir una WebShell
## Inyección Oracle - Sondeo básico
- ID: sqli-oracle-basic
- Difficulty: intermediate
- Subcategory: Oracle
- Tags: sqli, oracle, injection
- Original Extracted Source: original extracted web-security-wiki source/sqli-oracle-basic.md
Description:
Técnicas básicas de inyección en base de datos Oracle
Prerequisites:
- El objetivo tiene un punto de inyección SQL
- El backend usa base de datos Oracle
Execution Outline:
1. 1. Sondear el punto de inyección
2. 2. Obtener información de versión
3. 3. Obtener información de usuario
4. 4. Obtener nombres de tablas
## Inyección Oracle - Técnicas avanzadas
- ID: sqli-oracle-advanced
- Difficulty: advanced
- Subcategory: Oracle
- Tags: sqli, oracle, advanced, rce
- Original Extracted Source: original extracted web-security-wiki source/sqli-oracle-advanced.md
Description:
Técnicas avanzadas de inyección Oracle: procedimientos almacenados Java, operaciones de archivos con UTL_FILE
Prerequisites:
- Privilegios elevados en Oracle
- La máquina virtual Java está disponible
Execution Outline:
1. 1. Detectar privilegios Java
2. 2. Crear una función de ejecución Java
3. 3. Leer archivos con UTL_FILE
## Inyección PostgreSQL - Sondeo básico
- ID: sqli-postgres-basic
- Difficulty: intermediate
- Subcategory: PostgreSQL
- Tags: sqli, postgresql, postgres, injection
- Original Extracted Source: original extracted web-security-wiki source/sqli-postgres-basic.md
Description:
Técnicas de inyección en base de datos PostgreSQL
Prerequisites:
- El objetivo tiene un punto de inyección SQL
- El backend usa PostgreSQL
Execution Outline:
1. 1. Sondear el punto de inyección
2. 2. Obtener información de versión
3. 3. Obtener nombres de tablas
4. 4. Obtener nombres de columnas
## Inyección SQLite
- ID: sqli-sqlite-basic
- Difficulty: intermediate
- Subcategory: SQLite
- Tags: sqli, sqlite
- Original Extracted Source: original extracted web-security-wiki source/sqli-sqlite-basic.md
Description:
Ataque de inyección en base de datos SQLite
Prerequisites:
- Base de datos SQLite
- Existe un punto de inyección
Execution Outline:
1. 1. Sondear el punto de inyección
2. 2. Obtener la versión
3. 3. Obtener nombres de tablas
4. 4. Obtener la estructura de la tabla
## Inyección MongoDB
- ID: sqli-mongodb-basic
- Difficulty: intermediate
- Subcategory: MongoDB
- Tags: nosql, mongodb, injection
- Original Extracted Source: original extracted web-security-wiki source/sqli-mongodb-basic.md
Description:
Técnicas de ataque de inyección en bases de datos NoSQL
Prerequisites:
- El objetivo usa MongoDB
- Existe concatenación de entrada de usuario en la consulta
Execution Outline:
1. 1. Sondear el punto de inyección
2. 2. Bypass de autenticación
3. 3. Inyección de operadores lógicos
4. 4. Inyección de expresiones regulares
## Acceso no autorizado a Redis
- ID: sqli-redis
- Difficulty: intermediate
- Subcategory: Redis
- Tags: redis, nosql, injection
- Original Extracted Source: original extracted web-security-wiki source/sqli-redis.md
Description:
Acceso no autorizado a Redis e inyección de comandos
Prerequisites:
- El servicio Redis es accesible
- Sin autorización o con contraseña débil
Execution Outline:
1. 1. Sondear Redis
2. 2. Acceso no autorizado
3. 3. Escribir una Webshell
4. 4. Escribir una clave pública SSH
## Inyección ciega booleana
- ID: sqli-blind
- Difficulty: intermediate
- Subcategory: Inyección ciega
- Tags: sqli, blind, boolean
- Original Extracted Source: original extracted web-security-wiki source/sqli-blind.md
Description:
Técnica de inyección SQL ciega basada en condiciones booleanas
Prerequisites:
- Existe inyección SQL
- La página tiene respuestas distintas para verdadero/falso
Execution Outline:
1. 1. Confirmar la inyección ciega
2. 2. Obtener la longitud del nombre de la base de datos
3. 3. Enumerar el nombre de la base de datos carácter por carácter
4. 4. Usar herramientas para automatizar
## Inyección ciega basada en tiempo
- ID: sqli-time-based
- Difficulty: intermediate
- Subcategory: Inyección ciega
- Tags: sqli, blind, time
- Original Extracted Source: original extracted web-security-wiki source/sqli-time-based.md
Description:
Técnica de inyección SQL ciega basada en retardo temporal
Prerequisites:
- Existe inyección SQL
- El tiempo de respuesta de la página es controlable
Execution Outline:
1. 1. Confirmar la inyección ciega basada en tiempo
2. 2. Obtener la longitud del nombre de la base de datos
3. 3. Extraer carácter por carácter
4. 4. Funciones de retardo según la base de datos
## Inyección basada en errores
- ID: sqli-error-based
- Difficulty: intermediate
- Subcategory: Inyección basada en errores
- Tags: sqli, error, extractvalue
- Original Extracted Source: original extracted web-security-wiki source/sqli-error-based.md
Description:
Inyección SQL que extrae datos aprovechando los mensajes de error
Prerequisites:
- Existe inyección SQL
- Los mensajes de error se muestran en la página
Execution Outline:
1. 1. Confirmar la inyección basada en errores
2. 2. Obtener información de la base de datos
3. 3. Obtener nombres de tablas
4. 4. Obtener los datos
## Inyección SQL de segundo orden
- ID: sqli-second-order
- Difficulty: advanced
- Subcategory: Inyección de segundo orden
- Tags: sqli, second-order, stored
- Original Extracted Source: original extracted web-security-wiki source/sqli-second-order.md
Description:
Ataque de inyección SQL que se dispara después del almacenamiento
Prerequisites:
- Existe una función de almacenamiento de datos
- Los datos almacenados se reutilizan posteriormente
Execution Outline:
1. 1. Sondear la inyección de segundo orden
2. 2. Inyección en el nombre de usuario
3. 3. Inyección en el restablecimiento de contraseña
4. 4. Inyección en pedidos/comentarios
## Inyección por consulta UNION
- ID: sqli-union
- Difficulty: beginner
- Subcategory: Consulta UNION
- Tags: sqli, union, select
- Original Extracted Source: original extracted web-security-wiki source/sqli-union.md
Description:
Extracción de datos mediante UNION SELECT
Prerequisites:
- Existe un punto de inyección
- Los resultados de la consulta se pueden mostrar
Execution Outline:
1. 1. Determinar el número de columnas
2. 2. Determinar las columnas visibles
3. 3. Extraer los datos
4. 4. Bypass de filtros
## Inyección por consultas apiladas (stacked queries)
- ID: sqli-stacked
- Difficulty: intermediate
- Subcategory: Consultas apiladas
- Tags: sqli, stacked, queries
- Original Extracted Source: original extracted web-security-wiki source/sqli-stacked.md
Description:
Inyección que ejecuta múltiples sentencias SQL
Prerequisites:
- Se admite la ejecución de múltiples sentencias
- MySQL/PostgreSQL/MSSQL
Execution Outline:
1. 1. Sondear las consultas apiladas
2. 2. Consultas apiladas en MySQL
3. 3. Consultas apiladas en MSSQL
4. 4. Consultas apiladas en PostgreSQL
## Bypass de WAF en inyección SQL
- ID: sqli-waf-bypass
- Difficulty: advanced
- Subcategory: Bypass de WAF
- Tags: sqli, waf, bypass
- Original Extracted Source: original extracted web-security-wiki source/sqli-waf-bypass.md
Description:
Técnicas para eludir el firewall de aplicaciones web (WAF)
Prerequisites:
- El objetivo tiene un punto de inyección SQL
- Existe protección WAF
Execution Outline:
1. Codificación de transferencia fragmentada (chunked)
2. Contaminación de parámetros HTTP (HPP)
3. Sustitución por funciones equivalentes
4. Inyección sin comas

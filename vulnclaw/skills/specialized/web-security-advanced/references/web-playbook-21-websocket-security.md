# Seguridad de WebSocket
English: WebSocket Security
- Entry Count: 3
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Secuestro entre sitios de WebSocket (CSWSH)
- ID: ws-hijack
- Difficulty: intermediate
- Subcategory: Secuestro de WebSocket
- Tags: WebSocket, CSWSH, Origin, entre sitios, secuestro de sesión
- Original Extracted Source: original extracted web-security-wiki source/ws-hijack.md
Description:
Explota la falta de validación del Origin durante la fase de handshake de WebSocket, estableciendo una conexión WebSocket entre sitios a través de una página web maliciosa. El atacante puede secuestrar la sesión WebSocket de la víctima, robar datos en tiempo real o enviar mensajes suplantando la identidad de la víctima. Es similar a CSRF pero dirigido al protocolo WebSocket.
Prerequisites:
- El objetivo usa comunicación WebSocket
- El handshake de WebSocket no valida el Origin
Execution Outline:
1. 1. Identificar el endpoint de WebSocket
2. 2. Construir la página POC de secuestro entre sitios
3. 3. Inyección de mensajes WebSocket
4. 4. Script de análisis de tráfico WebSocket
## Ataque de contrabando de WebSocket
- ID: ws-smuggling
- Difficulty: expert
- Subcategory: Contrabando de WebSocket
- Tags: WebSocket, contrabando, proxy inverso, H2C, pivoteo a red interna
- Original Extracted Source: original extracted web-security-wiki source/ws-smuggling.md
Description:
Explota las diferencias en el manejo del protocolo WebSocket por parte de proxies inversos/balanceadores de carga, realizando contrabando de solicitudes HTTP hacia servicios de la red interna a través de la solicitud de actualización (upgrade) de WebSocket. El atacante puede eludir los controles de seguridad del frontend y comunicarse directamente con el backend, accediendo a APIs internas protegidas o interfaces de administración.
Prerequisites:
- El objetivo usa un proxy inverso (Nginx/Varnish, etc.)
- El proxy permite la actualización (upgrade) de WebSocket
- Existen servicios internos en el backend
Execution Outline:
1. 1. Detectar la posibilidad de contrabando de WebSocket
2. 2. Construcción del túnel WebSocket
3. 3. Contrabando H2C para eludir el control de acceso
4. 4. Explotación de diferencias en el proxy inverso
## Bypass de autenticación y autorización en WebSocket
- ID: ws-auth-bypass
- Difficulty: intermediate
- Subcategory: Bypass de autenticación
- Tags: WebSocket, autenticación, autorización, control de acceso indebido, repetición de token
- Original Extracted Source: original extracted web-security-wiki source/ws-auth-bypass.md
Description:
Explota la falta de verificación continua de autenticación tras el establecimiento de la conexión WebSocket, eludiendo los mecanismos de autenticación y autorización mediante fijación de sesión, repetición de token, suscripción indebida a canales, etc. La naturaleza de conexión persistente de WebSocket hace que, tras un cambio de permisos, la conexión original pueda mantener el acceso.
Prerequisites:
- El objetivo usa comunicación en tiempo real con WebSocket
- Se dispone de una sesión/Token válido
Execution Outline:
1. 1. Análisis del mecanismo de autenticación de WebSocket
2. 2. Repetición de Token y fijación de sesión
3. 3. Suscripción indebida a canales/salas
4. 4. Pruebas de límite de tasa y DoS en WebSocket
</content>

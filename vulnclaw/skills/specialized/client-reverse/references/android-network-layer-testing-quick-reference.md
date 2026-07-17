# Referencia Rápida de Pruebas de Capa de Red en Android

Usa este archivo cuando la solicitud de Android ya sea visible o esté cerca de serlo, y quieras una tarjeta de operador corta para pruebas de capa de red en lugar de cambiar repetidamente entre los documentos de runtime de Android y los documentos de pruebas Web.

## Regla Central

Para un pentest de app Android autorizada, las pruebas de capa de red comienzan tan pronto como una solicitud HTTP/HTTPS real o un mensaje WebSocket sea reproducible fuera de la app.

No sigas haciendo ingeniería inversa solo porque una recuperación más profunda sea posible.
Si Burp o Charles ya tienen una solicitud de línea base utilizable, cambia primero a las pruebas del lado del servidor y solo regresa a la ingeniería inversa cuando la repetición (replay), el texto plano, o la recuperación de estado se estanquen.

## Condiciones Mínimas de Entrada

Antes de la mutación de payload o el trabajo de explotación, confirma:

- que la app objetivo esté instalada y se conozca el flujo de negocio que la dispara
- que se conozca la acción de UI que la dispara
- que Burp o Charles hayan capturado la solicitud o mensaje real
- que la solicitud pueda reproducirse (replay) fuera de la app al menos una vez
- que se hayan anotado las cookies, headers, tokens, timestamps, nonces, valores de dispositivo, o prerrequisitos de secuencia necesarios
- que sepas qué campos son seguros de cambiar primero

Si estas condiciones no se cumplen, regresa a:

- `android-authorized-app-pentest-sop.md`
- `android-external-url-runtime-first-workflow.md`
- `android-ui-driven-observation-and-packet-loop.md`
- `02-client-api-reverse-and-burp.md`

## Bucle de Capa de Red

Usa este bucle para cada funcionalidad de negocio:

1. captura una solicitud o mensaje WebSocket de línea base limpio
2. repítelo (replay) sin cambios en Burp para demostrar que la línea base es estable
3. clasifica la superficie: REST, GraphQL, WebSocket, subida de archivos, flujo de autenticación, flujo de pago, gateway admin/API, o mixto
4. muta primero el campo seguro más pequeño
5. compara el código de estado, cuerpo, tiempos, efectos secundarios, y estado del servidor
6. conserva la evidencia y anota si el cambio fue aceptado, normalizado, rechazado, o bloqueado por la lógica de firma o secuenciación
7. si la línea base se rompe, detén el fuzzing y restaura la repetición (replay) antes de continuar

La secuencia operativa es:

`captura de línea base -> repetición estable -> mutación pequeña -> comparar respuesta y efecto secundario -> expandir por clase de bug`

## Qué Probar Primero

### Autenticación y sesión

- elimina o intercambia tokens, cookies, identificadores de dispositivo, e identificadores de tenant o usuario
- repite (replay) solicitudes entre usuarios, roles, y sesiones
- prueba autorización horizontal y vertical
- prueba si tokens antiguos, conexiones obsoletas, o roles degradados aún funcionan

### Lógica de negocio

- cambia IDs de objeto, montos, cantidades, precios, descuentos, estado de cupón, o pasos del flujo de trabajo
- omite pasos prerrequisito
- repite (replay) solicitudes fuera de orden
- repite la misma solicitud para buscar comportamiento tipo race condition o doble gasto

### Entrada e inyección

- prueba los campos de la solicitud que cruzan límites de confianza hacia contextos de consulta, renderizado, parsing, plantilla, archivo, o comando
- prioriza los campos que llegan a búsqueda, filtro, ordenamiento, texto enriquecido, metadatos de archivo, XML, o comportamiento de fetch del lado del servidor

### Comportamiento específico del protocolo

- para GraphQL, prueba introspección, sobre-alcance de campos, acceso a objetos anidados, y autenticación de resolvers
- para WebSocket, prueba autenticación de mensajes, acceso a sala o canal, autorización obsoleta, y manipulación de mensajes
- para flujos de subida, prueba verificaciones de tipo de archivo, confianza en metadatos, alcanzabilidad del parser, y exposición de rutas de almacenamiento

## Orden de Mutación Segura

Comienza desde las mutaciones de menor riesgo primero:

1. duplica la línea base sin cambios
2. elimina parámetros que parezcan opcionales
3. modifica un campo de negocio no criptográfico
4. modifica un campo de identidad o autorización
5. modifica un campo de secuenciación como nonce, timestamp, cursor, o token de paso
6. solo entonces prueba familias de payload más grandes

No cambies muchos campos a la vez.
Si la solicitud está firmada o es con estado (stateful), los cambios de múltiples campos ocultan el bloqueo real.

## Condiciones de Parada

Detén la mutación de capa de red y regresa a la recuperación cuando:

- la solicitud de línea base ya no se repite (replay) consistentemente
- cada mutación falla porque falta un firmador (signer), serializador, o transición de estado oculto
- el payload sigue cifrado u opaco
- el comportamiento de la respuesta sugiere que la app está agregando valores de runtime no vistos
- los frames de WebSocket o los cuerpos HTTP no están lo suficientemente en texto plano para razonar de forma segura

Orden de escalamiento:

1. recuperación de Java con `jadx`
2. recuperación mediante hooks en runtime con `frida_mcp`
3. volcado (dump) de `.so` e `ida_pro_mcp` solo cuando Java y los hooks todavía no respondan al bloqueo

## Mejores Referencias de Seguimiento

- `web-playbook-index.md` para clases de bugs del lado del servidor y familias de payload
- `web-modern-protocols.md` para CORS, GraphQL, WebSocket, OAuth/OIDC, y request smuggling
- `web-logic-auth.md` para IDOR, bypass de autenticación, flujos de restablecimiento, lógica de pago, y abuso de flujo de trabajo
- `web-file-infra.md` para subida, traversal, inclusión, y problemas de infraestructura

## Evidencia a Conservar

Para cada funcionalidad probada, conserva:

- el estado de pantalla y la acción de UI que produjeron la solicitud de línea base
- una solicitud o mensaje de línea base limpio
- la primera repetición (replay) exitosa fuera de la app
- el campo mutado exacto y la diferencia observada
- si el problema está relacionado con autenticación, lógica, inyección, protocolo, archivo, o infraestructura
- si la recuperación mediante ingeniería inversa fue necesaria de nuevo y por qué

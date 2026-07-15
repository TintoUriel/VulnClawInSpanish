---
name: client-reverse
description: Ingeniería inversa de cliente y reenvío con Burp — recuperación de firmas de clientes complejos, restauración de cifrado, rastreo de cadenas de solicitudes, reenvío estable, aplicable a pruebas de penetración autorizadas de Apps Android, firmas JS de navegador, ingeniería inversa de clientes de escritorio
routing:
  target_types: [client, android, mobile]
  task_types: [reverse]
  tooling: [frida, jadx, burp, scrcpy]
---

# Skill de Ingeniería Inversa de Cliente y Reenvío con Burp

Usa este Skill cuando la solicitud es construida por el cliente (App Android, JS de navegador, cliente de escritorio) y existe firma, cifrado, estado de token, vinculación de dispositivo o lógica anti-automatización que impide que Burp reenvíe directamente.

## Principio central

**Packet-First (paquetes primero)**: primero captura y analiza el tráfico HTTP/HTTPS o WebSocket real, confirma la disponibilidad, y solo después realiza ingeniería inversa según sea necesario en los puntos de bloqueo. La ingeniería inversa es un paso de resolución de bloqueos, no el punto de entrada por defecto.

## Enrutamiento de escenarios

### Pruebas de penetración autorizadas de App Android

**No uses jadx ni ida_pro_mcp para analizar el APK primero**, sigue este orden:

1. Confirma que la App objetivo ya está instalada en el dispositivo conectado
2. Prepara Burp o Charles para capturar el tráfico
3. Usa scrcpy_vision para abrir la App y ejecutar el flujo de negocio real
4. Después de cada acción clave, comprueba si aparecen paquetes HTTP/HTTPS o WebSocket en Burp/Charles
5. Si el paquete es visible y reenviable → pasa inmediatamente a `web-security-advanced` para pruebas de seguridad Web/API
6. Repite el ciclo "acción en la interfaz → captura de paquetes → análisis de seguridad Web"
7. Solo cuando no se pueda capturar el paquete / el paquete esté cifrado / no se pueda reenviar → escala a jadx → frida_mcp → ida_pro_mcp

**Cadena de herramientas MCP**: scrcpy_vision → burp/charles → adb_mcp → jadx → frida_mcp → ida_pro_mcp

### Firma JS de navegador, anti-scraping, handshake de WebSocket

1. chrome_devtools para ver el estado de la página y la cadena de solicitudes
2. js_reverse para localizar la lógica de generación de token/sign
3. burp para verificar el reenvío y determinar los campos variables

**Modelo de fases**: locate → recover → runtime → validation → replay

**Cadena de herramientas MCP**: chrome_devtools → js_reverse → burp

### Cliente de escritorio / signer local

1. everything_search para localizar los archivos relevantes
2. ida_pro_mcp para análisis estático de la función de firma
3. frida_mcp para obtener los parámetros en tiempo de ejecución
4. burp para verificar el reenvío estable

**Cadena de herramientas MCP**: everything_search → ida_pro_mcp → frida_mcp → burp

## Lista de verificación de preparación para el reenvío

Antes de entrar en las pruebas de Payload, debes poder responder:

- ¿Cómo se construye el cuerpo de la solicitud?
- ¿De dónde provienen las entradas de firma/cifrado?
- ¿Qué cookies, headers, tokens, valores de dispositivo, timestamps, nonces son obligatorios?
- ¿La solicitud depende del orden o del estado de sesión?
- ¿Qué campos se pueden modificar sin romper el reenvío?

## Conservación de evidencia

- Ubicación del código de builder/signer/crypto
- Puntos de hook clave y valores observados en tiempo de ejecución
- Muestras de solicitudes de replay disponibles
- Descripción de precondiciones, modos de fallo y comportamiento anti-automatización

## Documentos de referencia

- `references/02-client-api-reverse-and-burp.md` — Flujo de trabajo completo de ingeniería inversa de cliente a reenvío con Burp
- `references/android-authorized-app-pentest-sop.md` — SOP de pruebas de penetración de App Android
- `references/browser-js-signing-workflow.md` — Flujo de trabajo de firma JS de navegador
- `references/android-signing-and-crypto-workflow.md` — Flujo de trabajo de firma y cifrado Android
- `references/android-ui-driven-observation-and-packet-loop.md` — Ciclo de observación impulsado por UI de Android
- `references/android-external-url-runtime-first-workflow.md` — Pruebas de URL externas de Android
- `references/android-network-layer-testing-quick-reference.md` — Referencia rápida de pruebas de capa de red de Android
- `references/MCP.md` — Documento maestro de capacidades MCP
- `references/tool-selection-map.md` — Mapa de selección de herramientas

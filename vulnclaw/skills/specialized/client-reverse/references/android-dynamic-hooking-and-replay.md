# Hooking Dinámico y Replay en Android

Usa este archivo solo después de que la triage estático de Android haya acotado la ruta de la solicitud, o después de que el flujo de trabajo centrado en runtime de URL externas de Android haya demostrado que las capturas de pantalla, los logs, y las verificaciones de paquetes no son suficientes.
No entres en esta rama mientras Burp o Charles ya tengan una línea base de repetición (replay) utilizable.

## Orden de Hooking

Prefiere estos puntos en orden:

1. construcción final del objeto de solicitud
2. métodos de interceptor
3. punto de entrada de ejecución de la solicitud
4. generador de firma (sign) o token
5. límite nativo

## Capturar en Cada Hook

- clase y método
- URL
- método HTTP
- headers
- cuerpo o payload serializado
- tupla de entrada de firma (sign input)
- salida de firma o resultado cifrado

## Reglas de Escalamiento

- usa `scrcpy_vision` cuando el siguiente hook de runtime o disparador de paquete dependa de navegar la UI de la app, ingresar datos, o confirmar el estado de pantalla visible
- usa la revisión de logs con `adb_mcp` antes de una ingeniería inversa más profunda si una excepción de runtime pudiera explicar el bloqueo
- usa Frida para confirmar o unir brechas estáticas
- mantén la captura de proxy activa durante todo el trabajo dinámico para que cada resultado de hook pueda compararse con tráfico HTTP/HTTPS o WebSocket en vivo
- trata el bypass de SSL pinning como un paso de apoyo, no como el primer paso

## Bucle de Runtime Guiado por UI

Cuando la ruta de la app no sea obvia solo a partir del código estático:

1. usa `scrcpy_vision` para tocar, ingresar datos, desplazar, o navegar hacia el disparador sospechoso
2. captura una captura de pantalla o el árbol de UI después de cada transición importante
3. analiza el estado actual y decide la siguiente acción de prueba antes de volver a actuar
4. mantén la captura de paquetes lista para que el disparador de UI pueda vincularse a una o más solicitudes concretas
5. solo entonces coloca hooks o pasa a la repetición (replay) si el paquete y los valores de runtime relevantes son reales
6. si los paquetes siguen cifrados o ausentes, haz ingeniería inversa de Java primero y escala a nativo solo cuando Java ya no responda al bloqueo

Referencia detallada: `references/android-ui-driven-observation-and-packet-loop.md`

## Objetivo de Replay

El trabajo dinámico está completo cuando puedes producir:

- una receta de repetición (replay) estable
- las entradas de runtime obligatorias
- una respuesta clara sobre qué campos son seguros de mutar en Burp

Si ya existe una receta de repetición estable solo a partir del tráfico capturado, omite este archivo y pasa directamente a las pruebas de capa de red.

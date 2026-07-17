# Observación Guiada por UI y Bucle de Paquetes en Android

Usa este archivo cuando el progreso en runtime de Android dependa de lo que sea visible en la app, qué botón o campo debe tocar el operador a continuación, o qué acción de UI se necesita para disparar la solicitud HTTP/HTTPS o el mensaje WebSocket que luego entrará en Burp y en el flujo de trabajo de pentest.

## Regla Central

Este archivo es una capa de dirección en runtime.

Para las pruebas de URL externas en Android, comienza aquí antes de la ingeniería inversa: maneja la app, inspecciona la captura de pantalla, revisa los logs, y verifica si las solicitudes HTTP/HTTPS o los mensajes WebSocket ya son visibles.
Solo después de que esas verificaciones fallen debes recurrir a la recuperación de Java, el volcado nativo, o los hooks en runtime.

La secuencia de runtime se mantiene igual:

`presencia de la app -> ruta de paquetes lista -> acción de UI -> revisión de captura de pantalla/log -> captura de paquetes -> repetición (replay) -> pentest`

## Cuándo Usar Este Archivo

- el siguiente disparador de solicitud está oculto detrás de un inicio de sesión, navegación, pasos de asistente, diálogos, o interruptores de funcionalidad
- la solicitud objetivo solo aparece después de una transición de UI visible
- necesitas razonar a partir de la captura de pantalla actual antes de decidir el siguiente toque, entrada de texto, deslizamiento, o acción de retroceso
- necesitas correlacionar una acción de pantalla específica con uno o más paquetes antes de que comience el trabajo de repetición (replay)
- la app es comprobable, pero el operador aún necesita un bucle disciplinado de observar-decidir-actuar en lugar de clics aleatorios a ciegas

## Cadena MCP Principal

1. `scrcpy_vision`
2. `charles` o `burp`
3. `adb_mcp`
4. `jadx` solo cuando los paquetes estén ausentes, cifrados, o bloqueados
5. `frida_mcp`
6. `ida_pro_mcp` cuando se requiera análisis de `.so` volcado (dump)

## Bucle de Observar-Decidir-Actuar

### Paso 1: Preparar la vista de runtime

- lista los dispositivos y confirma el `serial` correcto
- confirma que el paquete de la app objetivo esté instalado en el dispositivo
- asegúrate de que la captura de paquetes ya esté lista si la siguiente acción puede disparar la solicitud objetivo
- despierta o desbloquea la pantalla si es necesario
- obtén la resolución física de la pantalla antes de cualquier toque o deslizamiento basado en coordenadas
- inicia la app o llévala a la funcionalidad objetivo

Ayudantes típicos de `scrcpy_vision`:

- `android_devices_list`
- `android_apps_list`
- `android_screen_wake`
- `android_screen_unlock`
- `android_shell_exec` con `wm size`
- `android_app_start`
- `android_activity_current`

Si el siguiente paso usará coordenadas sin procesar, primero ejecuta `android_shell_exec` con `wm size` y registra la resolución actual.
No reutilices coordenadas antiguas de un dispositivo, orientación, modo de pantalla, o escala de captura de pantalla diferente.
No saltes a `jadx`, `frida_mcp`, o `ida_pro_mcp` hasta que hayas confirmado que la app está presente y hayas intentado disparar el paquete objetivo desde la UI en vivo.

### Paso 2: Crear un punto de control visual

Captura el estado actual antes de tomar la siguiente acción:

- usa `android_vision_snapshot` para una sola imagen de pantalla
- usa `android_ui_dump` cuando necesites `resource-id`, texto, clase, o límites (bounds)
- usa `android_ui_findElement` cuando ya conozcas un botón, etiqueta de texto, o descripción de contenido probable

No confíes únicamente en coordenadas cuando la UI todavía pueda describirse estructuralmente.

### Paso 3: Analizar la pantalla actual

A partir de la captura de pantalla y el árbol de UI, responde:

- qué página o diálogo es visible actualmente
- qué controles son accionables ahora
- qué campo probablemente se corresponde con la ruta de la solicitud objetivo
- qué bloqueo está presente: inicio de sesión, consentimiento, puerta tipo captcha, formulario vacío, puerta de paso, período de espera, o prerrequisito faltante
- qué siguiente acción es más probable que produzca el paquete que deseas

La salida de este paso debe ser explícita, por ejemplo:

- estado actual de la pantalla
- acciones candidatas siguientes
- acción siguiente elegida
- por qué esta acción es la mejor sonda siguiente

También decide si la captura de pantalla ya sugiere una condición anormal:

- mensaje de error o advertencia visible
- falla de autenticación o inicio de sesión forzado
- timeout de red, advertencia de TLS, o problema de certificado
- página en blanco, diálogo de crash, o estado de reintento repetido
- redirección a un dominio inesperado o destino de WebView

### Paso 4: Ejecutar la siguiente acción de UI

Usa `scrcpy_vision` para realizar el movimiento elegido:

- `android_input_tap`
- `android_input_text`
- `android_input_swipe`
- `android_input_longPress`
- `android_input_keyevent`
- `android_input_dragDrop`

Antes de enviar cualquier acción basada en coordenadas como `android_input_tap`, `android_input_swipe`, `android_input_longPress`, `android_input_dragDrop`, o `android_input_pinch`, confirma primero la resolución de pantalla actual.
Prefiere `android_ui_findElement` o `android_ui_dump` cuando sea posible; recurre a coordenadas sin procesar solo después de haber confirmado la resolución.

Si la acción cambia la pantalla significativamente, regresa al Paso 2 y toma un nuevo punto de control antes de encadenar más acciones.

### Paso 4.5: Revisar los logs antes de hacer ingeniería inversa

Después de transiciones de UI importantes, verifica los logs con `adb_mcp`:

- busca crashes, errores de TLS, fallas de serialización, errores de autenticación, advertencias de WebView, o excepciones de la pila de red
- trata los logs como un discriminador económico antes de escalar al trabajo de ingeniería inversa
- si los logs ya explican la falla o el bloqueo, arregla primero la ruta de prueba en lugar de hacer ingeniería inversa de inmediato

### Paso 4.8: Verificar la evidencia de red de inmediato

Antes de tomar más acciones de UI o escalar a la ingeniería inversa:

- consulta `charles` o inspecciona `burp` en busca de las últimas solicitudes HTTP/HTTPS o mensajes WebSocket
- decide si la solicitud esperada ya existe en forma de texto plano o reproducible (replayable)
- si ya existe un paquete utilizable, detén la exploración de UI y pasa a la repetición (replay) y al pentest
- si no existe ningún paquete, regresa al razonamiento sobre la captura de pantalla en lugar de recurrir por defecto a la ingeniería inversa

### Paso 5: Vincular la acción de UI con la captura de paquete

Después de la acción:

- consulta `charles` o inspecciona `burp` en busca de las últimas solicitudes HTTP/HTTPS o mensajes WebSocket
- decide si el paquete esperado apareció
- si apareció, marca el estado de pantalla disparador y la acción de UI exacta que lo produjo
- si no apareció, regresa al análisis de captura de pantalla en lugar de continuar a ciegas

El objetivo es producir un mapeo claro:

`estado de pantalla -> acción del usuario -> paquete observado`

### Paso 6: Promover el paquete al análisis de repetición (replay)

Una vez que el paquete objetivo sea real:

- inspecciónalo en `charles` o `burp`
- determina host, ruta, método, headers, cookies, tokens, forma del cuerpo, y secuenciación
- si ya es utilizable, pasa directamente a la repetición (replay) y a las pruebas de seguridad
- entrégalo a `web-playbook-index.md` para el análisis de seguridad de API, HTTP/HTTPS, o WebSocket
- correlaciónalo con la lógica de builder o firmador solo si quedan bloqueos de cifrado, firmas, o repetición
- usa `frida_mcp` solo si todavía faltan valores exclusivos de runtime

En este punto el trabajo sale de la dirección de UI y entra en modo de repetición (replay) y pentest. Cuando se haya probado un flujo de negocio, regresa a la app y repite el bucle para la siguiente funcionalidad en lugar de recurrir por defecto a la ingeniería inversa.
Si el paquete ya es reproducible, el trabajo de ingeniería inversa es opcional y no debería retrasar las pruebas de capa de red.

## Orden de Escalamiento Cuando los Paquetes Están Bloqueados

Escala más allá de la dirección de UI solo cuando una de estas condiciones sea verdadera:

- no aparece ningún paquete en `burp` o `charles`
- aparece un paquete pero el payload está cifrado o no es utilizable
- la repetición (replay) falla porque los valores obligatorios en texto plano siguen ocultos

Orden de escalamiento:

1. haz ingeniería inversa de Java primero con `jadx`
2. usa `frida_mcp` para enganchar (hook) límites de Java o nativos cuando la recuperación de texto plano basada en hooks sea más rápida que una ingeniería inversa más profunda
3. si Java y los hooks todavía no exponen lo suficiente, vuelca el `.so` relevante
4. analiza el `.so` volcado con `ida_pro_mcp`

El objetivo no es la ingeniería inversa por sí misma. El objetivo es hacer visibles las solicitudes HTTP/HTTPS o los mensajes WebSocket, recuperar el texto plano, o estabilizar la repetición (replay).

## Traspaso al Flujo de Trabajo de Pentest

No comiences la mutación de payload solo porque capturaste un paquete una vez.

Primero confirma:

- qué acción de UI visible produjo el paquete
- si el paquete depende del estado de sesión, interruptores, o pantallas previas
- si el paquete contiene valores de firma, token, nonce, timestamp, ID de dispositivo, o sesión que deben conservarse
- si la repetición (replay) es estable fuera de la app
- qué campos son seguros de cambiar sin romper la solicitud

Luego ramifica:

- `web-playbook-index.md` para pruebas normales de API y Web
- `04-ai-and-mcp-security-integrated.md` si el paquete alcanza superficies de IA, agente, o expuestas por MCP
- `tools-reference-index.md` cuando necesites la siguiente familia de herramientas del operador

## Contrato de Evidencia

Conserva estos artefactos:

- el estado de pantalla que importó
- la siguiente acción elegida y por qué fue seleccionada
- el paquete disparado por esa acción
- el mapeo de la acción de pantalla a la solicitud
- cualquier evidencia anormal de captura de pantalla o log que justificó la escalada
- cualquier valor exclusivo de runtime o punto de hook necesario para la repetición (replay)
- el punto donde la tarea cambió de dirección de UI a análisis de Burp y pentest

## Advertencias de Antipatrones

- no comiences haciendo clic aleatoriamente por la app sin puntos de control
- no confíes únicamente en el razonamiento sobre capturas de pantalla cuando los logs o la evidencia de paquetes puedan resolver la incertidumbre
- no abras `jadx` o `ida_pro_mcp` antes de confirmar que la app objetivo está instalada e intentar disparar el paquete desde la app en vivo
- no hagas ingeniería inversa primero cuando las capturas de pantalla, logs, y la visibilidad HTTP/HTTPS o WebSocket ya puedan responder el problema
- no saltes a las pruebas de payload en Burp antes de que la solicitud sea reproducible
- no envíes toques o deslizamientos por coordenadas antes de verificar la resolución actual, o las coordenadas obsoletas pueden desviarse y golpear el lugar equivocado

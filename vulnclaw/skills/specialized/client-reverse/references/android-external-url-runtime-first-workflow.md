# Flujo de Trabajo Centrado en Runtime para URLs Externas en Android

Usa este archivo cuando estés probando una funcionalidad de una app Android que alcanza una URL externa o una API remota y aún no sabes si la ingeniería inversa es necesaria.

Esta rama está centrada en paquetes y en runtime primero, no en ingeniería inversa primero.

## Regla Principal Para Pentest de App Android Autorizada

Para un pentest de app Android autorizada, el movimiento de apertura no es el análisis del APK.
Antes de `jadx`, `frida_mcp`, o `ida_pro_mcp`, siempre haz esto primero:

1. confirma que la aplicación objetivo esté instalada en el dispositivo conectado
2. prepara `burp` o `charles` para que la siguiente solicitud o mensaje sea observable
3. abre la app con `scrcpy_vision`
4. simula clics reales de negocio y navegación
5. después de cada acción importante, inspecciona capturas de pantalla, logs, y `burp` o `charles`
6. si los paquetes son visibles y utilizables, pasa directamente a `web-playbook-index.md`
7. solo si el tráfico está ausente, cifrado, opaco, aún no es reproducible (replayable), o la evidencia de runtime apunta claramente a un bloqueo del lado del cliente, debe comenzar el trabajo de ingeniería inversa

Esta regla es la predeterminada para el trabajo de pentest en Android. La ingeniería inversa no es el primer paso a menos que la tarea en sí ya sea un problema conocido de descifrado o exclusivamente de ingeniería inversa.

## Regla Central

No comiences invirtiendo la interfaz.

Primero:

1. confirma que la aplicación objetivo esté instalada en un dispositivo conectado
2. prepara `burp` o `charles` para que la siguiente solicitud o mensaje pueda observarse
3. maneja la app con `scrcpy_vision`
4. inspecciona la captura de pantalla en busca de anomalías visibles
5. revisa los logs con `adb_mcp`
6. verifica si `burp` o `charles` ya reciben solicitudes HTTP/HTTPS o mensajes WebSocket

Solo si los paquetes están cifrados, ausentes, siguen siendo opacos, o siguen sin ser utilizables para la repetición (replay), debes escalar a la ingeniería inversa.

## Cuándo Usar Este Archivo

- el objetivo es probar el comportamiento de URL externa o API de una app Android
- todavía estás en modo caja negra o caja gris y quieres saber si el trabajo de ingeniería inversa es necesario
- la solicitud puede volverse visible una vez que se encuentre la acción de pantalla correcta
- necesitas una forma disciplinada de decidir cuándo escalar de la observación en runtime a la recuperación basada en Java, nativo, o hooks

## Cadena MCP Principal

1. `scrcpy_vision`
2. `burp` o `charles`
3. `adb_mcp`
4. `jadx` solo cuando la visibilidad de runtime sea insuficiente
5. `frida_mcp`
6. `ida_pro_mcp` para análisis de `.so` volcado (dump)

## Bucle Centrado en Runtime

### Paso 1: Confirmar dispositivo y presencia de la app

Usa `scrcpy_vision` para:

- listar los dispositivos conectados y confirmar el `serial` correcto
- verificar que el paquete de la app objetivo esté instalado en el dispositivo
- confirmar si la app ya está en primer plano o necesita ser lanzada

Ayudantes típicos:

- `android_devices_list`
- `android_apps_list`
- `android_activity_current`
- `android_app_start`

No saltes a `jadx`, `frida_mcp`, o `ida_pro_mcp` antes de haber confirmado que la app objetivo realmente está presente y se puede lanzar en el dispositivo de prueba.

### Paso 2: Preparar primero la visibilidad de paquetes

Antes de manejar la funcionalidad objetivo:

- asegúrate de que Burp o Charles ya sean la ruta de captura activa
- confirma que los supuestos de proxy y certificado estén en su lugar
- decide si el siguiente disparador debería producir HTTP/HTTPS, WebSocket, o ambos

No comiences a manejar el flujo de negocio hasta que la siguiente solicitud realmente pueda observarse.

### Paso 3: Manejar la app hasta la funcionalidad objetivo

Usa `scrcpy_vision` para:

- despertar o desbloquear el dispositivo
- obtener la resolución de pantalla actual antes de cualquier acción basada en coordenadas
- iniciar la app
- tocar hacia la funcionalidad objetivo
- ingresar texto, deslizar, o navegar hasta que la URL externa deba dispararse

Ayudantes típicos:

- `android_devices_list`
- `android_screen_wake`
- `android_screen_unlock`
- `android_shell_exec` con `wm size`
- `android_app_start`
- `android_input_tap`
- `android_input_text`
- `android_input_swipe`

Si estás a punto de usar coordenadas en lugar de la búsqueda de elementos de la UI, primero consulta la resolución actual con `android_shell_exec` y `wm size`.
Esto evita que los clics de escritorio o de la app se desvíen cuando la resolución del dispositivo, orientación, escala, o tamaño de la captura de pantalla difiere de tu supuesto.

Antes de disparar el flujo de negocio, asegúrate de que Burp o Charles ya estén en un estado donde la siguiente solicitud pueda observarse.

### Paso 4: Inspeccionar la captura de pantalla antes de hacer ingeniería inversa

Después de cada acción importante, toma un punto de control visual:

- usa `android_vision_snapshot`
- usa `android_ui_dump` cuando la estructura de la UI importe

Verifica si la captura de pantalla ya muestra algo anormal:

- diálogo de error o advertencia visible
- bloqueo de inicio de sesión o permisos
- pantalla en blanco, crash, bucle de spinner, o timeout
- advertencia de certificado o error de red
- redirección a una página, host, o destino de WebView inesperado

No hagas ingeniería inversa solo porque la funcionalidad falló una vez. Primero determina si la falla ya está explicada por el estado visible.

### Paso 5: Revisar los logs en busca de evidencia económica

Usa la revisión de logs con `adb_mcp` después de acciones importantes:

- verifica fallas de TLS
- errores de serialización o parsing
- fallas de autenticación o expiración de token
- excepciones de WebView, okhttp, retrofit, o pila de red personalizada
- trazas de crash o fallas de carga JNI

Si los logs ya explican el problema, arregla primero la ruta de prueba en lugar de escalar al trabajo de ingeniería inversa.

### Paso 6: Verificar Burp y Charles

Ahora decide si el tráfico ya es visible:

- inspecciona el historial de `burp` si Burp es el proxy activo
- inspecciona `charles` si Charles es la ruta de captura activa
- confirma si la solicitud HTTP/HTTPS o el mensaje WebSocket existe, si el cuerpo o los frames están en texto plano, y si la repetición (replay) se ve realista

Tres casos:

1. el paquete es visible y utilizable
2. el paquete es visible pero está cifrado o sigue opaco
3. el paquete está completamente ausente

### Paso 7: Ramificar según la visibilidad del paquete

#### Caso 1: El paquete es visible y utilizable

- no hagas ingeniería inversa primero
- pasa directamente a la repetición (replay) y las pruebas de seguridad
- usa `burp` como línea base de prueba
- conserva la acción de pantalla que produjo el paquete
- continúa en `web-playbook-index.md` para probar la superficie HTTP/HTTPS o WebSocket
- después de terminar un conjunto de pruebas del lado del servidor, regresa a la app y repite el bucle para la siguiente acción de negocio si es necesario

#### Caso 2: El paquete es visible pero está cifrado u opaco

- haz ingeniería inversa de Java primero con `jadx`
- localiza los builders de URL, interceptores, firmadores (signers), cifradores, y la lógica de serialización
- si Java es insuficiente, usa `frida_mcp` para enganchar (hook) el límite de Java o nativo relevante y recuperar el texto plano o los argumentos

#### Caso 3: El paquete está completamente ausente

- vuelve a revisar el estado de la captura de pantalla y los logs
- verifica los supuestos de proxy y certificado
- si la ruta de la app es correcta pero el tráfico sigue oculto, haz ingeniería inversa de Java primero
- si Java apunta a código nativo o aún no explica el tráfico faltante, vuelca el `.so` relevante

## Orden de Escalamiento

Cuando la visibilidad centrada en runtime no sea suficiente, escala en este orden:

1. ingeniería inversa de Java con `jadx`
2. recuperación mediante hooks de Java o nativos con `frida_mcp`
3. volcar (dump) el `.so` relevante
4. analizar el `.so` volcado con `ida_pro_mcp`

El trabajo nativo es un paso de resolución de bloqueos, no el punto de partida por defecto.

## Objetivos de la Ingeniería Inversa

Haz ingeniería inversa solo hasta que se cumpla uno de estos objetivos:

- se recuperan los datos de la solicitud en texto plano
- la solicitud HTTP/HTTPS o el mensaje WebSocket se vuelve visible en `burp` o `charles`
- el límite de cifrado o firma se entiende lo suficiente para la repetición (replay)
- el descifrado basado en hooks o la captura de argumentos hace que la interfaz sea comprobable

## Traspaso al Pentest

Pasa al pentest solo después de que al menos una de estas condiciones sea verdadera:

- Burp o Charles ya tienen una solicitud de línea base utilizable
- los hooks de Frida recuperan de forma confiable entradas o salidas en texto plano
- la ingeniería inversa de Java o nativo ha expuesto el bloqueo exacto y la ruta de repetición (replay)

Si Burp o Charles ya tienen una solicitud de línea base utilizable, esa es la condición de traspaso preferida.
No sigas haciendo ingeniería inversa solo porque la recuperación estática también parezca posible.

Luego continúa en:

- `web-playbook-index.md` para pruebas de API y Web
- `04-ai-and-mcp-security-integrated.md` si la solicitud objetivo alcanza superficies de IA, agente, o MCP
- `tools-reference-index.md` cuando necesites la siguiente familia de herramientas del operador

## Contrato de Evidencia

Conserva:

- el estado de pantalla que disparó la URL externa
- las anomalías de captura de pantalla que influyeron en el siguiente paso
- las anomalías de log relevantes
- si `burp` o `charles` vieron tráfico
- la razón por la que la escalada a ingeniería inversa fue o no necesaria
- los hallazgos de Java, puntos de hook, o evidencia del `.so` volcado cuando ocurrió la escalada

## Antipatrones

- no abras `jadx` o `ida_pro_mcp` antes de confirmar que la app objetivo está instalada en el dispositivo conectado e intentar la captura de paquetes en runtime
- no hagas ingeniería inversa de la app antes de verificar la captura de pantalla, los logs, y la visibilidad HTTP/HTTPS o WebSocket
- no vuelques el `.so` primero cuando Java o los hooks podrían resolver el bloqueo más rápido
- no pases a las pruebas de payload antes de que la solicitud sea reproducible o el texto plano sea recuperable
- no envíes clics o deslizamientos por coordenadas antes de confirmar la resolución de pantalla actual

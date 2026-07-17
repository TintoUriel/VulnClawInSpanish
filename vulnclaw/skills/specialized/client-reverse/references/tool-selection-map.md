# Mapa de Selección de Herramientas

## Capa de Ingeniería Inversa

- `jadx`
- `ida_pro_mcp`
- `frida_mcp`
- `scrcpy_vision`
- `adb_mcp`
- `charles`
- `js_reverse`
- `chrome_devtools`
- `burp`

## Secuencias por Plataforma

### Firma o anti-bot de JS de navegador

- prueba de límite y solicitud: `chrome_devtools` -> `js_reverse`
- divergencia navegador/local: `js_reverse`
- confirmación de repetición (replay): `burp`

### URL externa en Android o firma/cifrado

- preparación de proxy o captura primero: `burp` / `charles`
- visibilidad centrada en runtime y verificación de paquetes: `scrcpy_vision` -> `adb_mcp`
- recuperación de Java cuando esté bloqueado: `jadx`
- dirección de estado de UI y siguientes acciones guiadas por captura de pantalla: `scrcpy_vision`
- estado del dispositivo y contexto de runtime: `adb_mcp`
- hooks acotados de Java o JNI: `frida_mcp`
- análisis de `.so` volcado cuando sea necesario: `ida_pro_mcp`
- validación en el cable u observación asistida por Charles: `charles`
- confirmación de repetición (replay): `burp`

## Capa de Soporte

- `everything_search`
- `context7`
- `fetch`
- `memory`
- `sequential_thinking`

## Regla

No comiences las pruebas de payload en Burp cuando la solicitud todavía sea opaca.
Para pruebas de URL externa en Android, no hagas ingeniería inversa primero cuando las capturas de pantalla, los logs, y la visibilidad de paquetes puedan responder el problema.
No elijas referencias de navegador por palabras clave antes de conocer la etapa actual.

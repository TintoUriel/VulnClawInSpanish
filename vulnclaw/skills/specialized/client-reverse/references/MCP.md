# Documento Maestro de Capacidades MCP

## 1. Propósito del documento

Este documento organiza las capacidades MCP que puedo invocar directamente en la sesión actual. El objetivo no es solo elaborar una "lista de herramientas", sino ofrecer un borrador de referencia adecuado para escribir `skills` posteriormente.
Se cubre principalmente lo siguiente:

- El propósito de cada servidor/espacio de nombres MCP
- La forma de invocar cada método
- El significado de los principales parámetros
- Qué contiene aproximadamente el resultado devuelto
- Escenarios de uso típicos
- Flujos de trabajo comunes al combinarlo con otros MCP

Este documento está orientado por defecto a la orquestación de herramientas tipo Codex/Agent, no es documentación genérica de SDK. Por eso se hace más hincapié en "cuándo usarlo" y "cómo describir la estrategia de invocación al escribir un skill".

---

## 2. Convenciones generales de invocación

### 2.1 Formato de nomenclatura de herramientas

La mayoría de los nombres de herramientas MCP en el entorno actual siguen el siguiente formato:

```text
mcp__<server_name>__<tool_name>
```

Por ejemplo:

- `mcp__adb_mcp__list_devices`
- `mcp__chrome_devtools__navigate_page`
- `mcp__ida_pro_mcp__decompile`

Unas pocas funciones relacionadas con el acceso a recursos MCP no llevan el prefijo `mcp__`, pero en esencia también son capacidades del ecosistema MCP:

- `list_mcp_resources`
- `list_mcp_resource_templates`
- `read_mcp_resource`

### 2.2 Formato de los parámetros de invocación

Todas las herramientas MCP usan objetos de parámetros en estilo JSON. Formato típico:

```json
{
  "device_id": "emulator-5554",
  "lines": 200
}
```

Puntos a tener en cuenta:

- Solo pasa los campos necesarios, no incluyas arrays vacíos o `null` sin sentido
- Los parámetros `optional` generalmente se pueden omitir
- Algunas herramientas requieren rutas absolutas, especialmente para capturas de pantalla, guardado de código fuente, descarga de archivos, rutas de salida de grabación de pantalla, etc.
- Algunas herramientas usan parámetros de paginación, como `offset`, `count`, `pageIdx`, `pageSize`

### 2.3 Puntos recomendados al describir en un skill

Si vas a convertir estas capacidades en un skill, se recomienda que cada skill especifique claramente:

1. Condiciones de activación
2. MCP prioritario a usar
3. Orden de secuencia entre herramientas
4. Qué parámetros deben completarse obligatoriamente
5. En qué casos cambiar a otro MCP
6. Si la salida está vacía/falla, cuál debe ser el siguiente paso de remediación

### 2.4 Referencia rápida de selección de MCP

| Tipo de tarea | MCP prioritario |
| --- | --- |
| Gestión de dispositivos Android, instalación de APK, clics y deslizamientos, descarga de archivos | `adb_mcp` |
| Control visual de Android, localización de árbol UI, ADB inalámbrico, imagen en tiempo real | `scrcpy_vision` |
| Captura de tráfico HTTP/HTTPS de Android, análisis de sesión de Charles | `charles` |
| Historial de Burp, Repeater, Collaborator, Intruder | `burp` |
| Automatización web, capturas de pantalla, formularios, solicitudes de red, consola | `chrome_devtools` |
| Breakpoints de JS, búsqueda de código fuente, cadena de origen de XHR, rastreo de funciones | `js_reverse` |
| Búsqueda de documentación oficial, consulta de ejemplos de código | `context7` |
| Descarga/extracción genérica de contenido de páginas web | `fetch` |
| Búsqueda local de archivos ultrarrápida | `everything_search` |
| Inyección dinámica de Android, Frida attach/spawn | `frida_mcp` |
| Análisis estático de binarios, renombrado por lotes en IDA/descompilación/reparación de tipos | `ida_pro_mcp` |
| Descompilación de APK, Manifest, consulta de clases/métodos/xref | `jadx` |
| Grafo de memoria, memoria estructurada de largo plazo | `memory` |
| Pensamiento paso a paso para problemas complejos | `sequential_thinking` |

### 2.5 Flujos de trabajo combinados comunes

#### Análisis de App Android

- Estático: `jadx`
- Dinámico: `frida_mcp`
- Captura de tráfico: `charles`
- Control de dispositivo: `adb_mcp`
- Visualización/automatización de UI: `scrcpy_vision`

#### Ingeniería inversa del frontend Web

- Operación de página: `chrome_devtools`
- Breakpoints de JS y búsqueda de código fuente: `js_reverse`
- Reenvío HTTP y pruebas de seguridad: `burp`

#### Ingeniería inversa de Native / So de APK

- Análisis estático con IDA: `ida_pro_mcp`
- Hook en tiempo de ejecución: `frida_mcp`
- Asistencia del lado del dispositivo: `adb_mcp` / `scrcpy_vision`

---

## 3. Interfaz genérica de recursos MCP

Estas tres funciones no son un servidor de negocio específico, sino capacidades genéricas para "acceder a los recursos que expone un servidor MCP".

### 3.1 `list_mcp_resources`

- Función: listar los recursos que expone un servidor MCP específico o todos los servidores
- Uso típico: encontrar archivos, contexto, esquemas de base de datos, fragmentos de configuración que se puedan leer directamente
- Parámetros:
  - `server`: opcional, especifica el nombre del servidor
  - `cursor`: opcional, cursor de paginación
- Descripción adecuada para un skill: primero enumerar los recursos, luego decidir si invocar `read_mcp_resource`

Ejemplo:

```json
{
  "server": "some_server"
}
```

### 3.2 `list_mcp_resource_templates`

- Función: listar plantillas de recursos parametrizadas
- Uso típico: descubrir recursos de "lectura con parámetros", por ejemplo recursos consultados por nombre de tabla, clave primaria o ruta
- Parámetros:
  - `server`
  - `cursor`
- Descripción adecuada para un skill: cuando el recurso no es un URI fijo sino un "URI de plantilla", consulta esto primero

### 3.3 `read_mcp_resource`

- Función: leer el contenido de un recurso específico
- Parámetros:
  - `server`: nombre del servidor
  - `uri`: URI del recurso
- Escenarios adecuados:
  - Leer configuración
  - Leer esquema
  - Leer contexto de servicio
  - Leer estado compartido

Ejemplo:

```json
{
  "server": "some_server",
  "uri": "resource://example/path"
}
```

---

## 4. `adb_mcp`: control de dispositivos Android e interacción con archivos

### 4.1 Posicionamiento

`adb_mcp` es la capa de interacción con dispositivos Android más básica, adecuada para:

- Lista y estado de dispositivos
- Instalación/desinstalación de APK
- Capturas de pantalla, grabación de pantalla
- Entrada de texto, clics, deslizamientos, envío de teclas
- Descarga/subida de archivos
- Lectura de logcat, batería, memoria, información de almacenamiento

Si tu skill necesita "controlar el dispositivo en sí", considérala primero.

### 4.2 Flujo de trabajo común

1. `list_devices` para confirmar el dispositivo
2. `get_device_info` / `get_battery_info` para evaluar el entorno
3. `install_app` o `list_packages`
4. `send_tap` / `send_swipe` / `send_text` para dirigir la interacción
5. `take_screenshot` / `record_screen` para dejar evidencia
6. `get_logcat` para depuración

### 4.3 Lista de métodos

| Herramienta | Parámetros principales | Función | Uso típico |
| --- | --- | --- | --- |
| `mcp__adb_mcp__list_devices` | Ninguno | Lista los dispositivos Android conectados | Punto de entrada de la tarea, confirmar primero si el dispositivo está en línea |
| `mcp__adb_mcp__get_device_info` | `device_id?` | Lee información detallada del dispositivo | Ver modelo, versión del sistema, número de serie |
| `mcp__adb_mcp__get_battery_info` | `device_id?` | Lee el estado de la batería | Confirmar la carga antes de pruebas largas |
| `mcp__adb_mcp__get_memory_info` | `device_id?` | Lee información de memoria | Diagnóstico de rendimiento/estabilidad |
| `mcp__adb_mcp__get_storage_info` | `device_id?` | Lee información de almacenamiento | Ver si hay espacio suficiente para instalar/grabar |
| `mcp__adb_mcp__clear_logcat` | `device_id?` | Limpia el logcat | Hacer una captura de log limpia |
| `mcp__adb_mcp__get_logcat` | `device_id?`, `filter_tag?`, `lines?` | Lee los logs | Depuración de fallos, red, SSL |
| `mcp__adb_mcp__install_app` | `apk_path`, `device_id?` | Instala el APK | Desplegar el paquete de prueba |
| `mcp__adb_mcp__uninstall_app` | `package_name`, `device_id?` | Desinstala la app | Limpiar el entorno |
| `mcp__adb_mcp__list_packages` | `device_id?`, `system_apps?` | Lista los nombres de paquete instalados | Encontrar el nombre de paquete objetivo |
| `mcp__adb_mcp__list_files` | `remote_path`, `device_id?` | Ver el directorio del dispositivo | Buscar caché, configuración, archivos exportados |
| `mcp__adb_mcp__pull_file` | `remote_path`, `local_path`, `device_id?` | Descarga un archivo del dispositivo al local | Exportar base de datos, logs, caché |
| `mcp__adb_mcp__push_file` | `local_path`, `remote_path`, `device_id?` | Sube un archivo al dispositivo | Subir certificados, scripts, parches |
| `mcp__adb_mcp__send_keyevent` | `keycode`, `device_id?` | Envía un evento de tecla | Tecla de retroceso, Home, menú |
| `mcp__adb_mcp__send_tap` | `x`, `y`, `device_id?` | Clic en coordenadas | Operación automatizada |
| `mcp__adb_mcp__send_swipe` | `x1`,`y1`,`x2`,`y2`,`duration?`,`device_id?` | Deslizar | Desplazar listas, desbloquear, cambiar de página |
| `mcp__adb_mcp__send_text` | `text`, `device_id?` | Ingresar texto | Búsqueda, inicio de sesión, formularios |
| `mcp__adb_mcp__take_screenshot` | `save_path`, `device_id?` | Captura de pantalla al local | Conservación de evidencia, confirmación del estado de la UI |
| `mcp__adb_mcp__record_screen` | `duration?`, `save_path?`, `device_id?` | Grabar pantalla | Dejar evidencia de la reproducción del flujo |

### 4.4 Ejemplos de invocación típicos

Listar dispositivos:

```json
{}
```

Captura de pantalla:

```json
{
  "device_id": "emulator-5554",
  "save_path": "C:\\Users\\28484\\Desktop\\screen.png"
}
```

Leer las últimas 200 líneas de log:

```json
{
  "device_id": "emulator-5554",
  "lines": 200
}
```

### 4.5 Puntos a tener en cuenta al escribir un skill

- Casi cualquier tarea de Android debería empezar con `list_devices`
- `take_screenshot` requiere explícitamente una ruta absoluta local
- Se recomienda ejecutar `clear_logcat` antes de `get_logcat` en escenarios complejos
- `send_tap` / `send_swipe` dependen totalmente de coordenadas, adecuado para interfaces fijas, no para layouts muy dinámicos
- `push_file` y `pull_file` son herramientas de alta frecuencia para instalación de certificados, exportación de logs y conservación de datos como evidencia

---

## 5. `charles`: captura de tráfico y análisis de sesión de Charles

### 5.1 Posicionamiento

`charles` se encarga de leer y analizar el tráfico ya capturado por Charles Proxy; el foco no es "controlar directamente el proxy de Android", sino:

- Verificar si Charles está en línea y si ya hay una sesión de captura activa
- Iniciar o retomar una live capture, obteniendo el `capture_id`
- Filtrar de forma estructurada el tráfico en vivo o las grabaciones ya guardadas
- Profundizar en una solicitud individual, ver headers, código de estado, vista previa de cuerpo de solicitud/respuesta
- Agrupar y analizar el tráfico por host, path, status, clase de recurso
- Finalizar la captura y persistir un snapshot, para facilitar la revisión posterior

### 5.2 Tipos de skill adecuados

- Ingeniería inversa de API de Android
- Captura de tráfico HTTPS
- Análisis de comportamiento de interfaces de App
- Comparación de parámetros de firma antes/después
- Búsqueda de token, session, campos cifrados
- Grabación de sesión, filtrado y conservación de evidencia

### 5.3 Lista de métodos

| Herramienta | Parámetros principales | Función | Uso típico |
| --- | --- | --- | --- |
| `mcp__charles__charles_status` | Ninguno | Verifica la conectividad de Charles y el estado de la live capture | Confirmar que el entorno está listo |
| `mcp__charles__reset_environment` | Ninguno | Reinicia el entorno de Charles y restaura la configuración guardada | Hacer un experimento limpio |
| `mcp__charles__start_live_capture` | `adopt_existing?`,`include_existing?`,`reset_session?` | Inicia o retoma una live capture | Obtener el `capture_id` para el análisis posterior |
| `mcp__charles__query_live_capture_entries` | `capture_id`,`cursor?`,`preset?`,`host_contains?`,`path_contains?`,`method_in?`,`status_in?`,`request_body_contains?`,`response_body_contains?`,`max_items?` | Filtra de forma estructurada el tráfico en vivo | Punto de entrada recomendado para búsqueda en tiempo real |
| `mcp__charles__peek_live_capture` | `capture_id`,`cursor?`,`limit?` | Vista previa de las entradas nuevas en la live capture actual | Vistazo ligero a las solicitudes recientes |
| `mcp__charles__read_live_capture` | `capture_id`,`cursor?`,`limit?` | Lee de forma incremental y avanza el cursor en vivo | Usar cuando se necesite lectura en streaming de tráfico nuevo |
| `mcp__charles__get_traffic_entry_detail` | `source`,`entry_id`,`capture_id?`,`recording_path?`,`include_full_body?`,`max_body_chars?` | Profundiza en el detalle de una entrada de tráfico | Ver headers, vista previa de body, detalles de solicitud/respuesta |
| `mcp__charles__group_capture_analysis` | `source`,`capture_id?`,`recording_path?`,`group_by`,`preset?`,`host_contains?`,`path_contains?`,`status_in?` | Agrupa por host/path/status/clase de recurso | Encontrar rápidamente interfaces con más actividad |
| `mcp__charles__get_capture_analysis_stats` | `source`,`capture_id?`,`recording_path?`,`preset?` | Devuelve estadísticas de granularidad gruesa | Ver la distribución global de la captura |
| `mcp__charles__stop_live_capture` | `capture_id`,`persist?` | Detiene la live capture y opcionalmente persiste | Finalizar el experimento y guardar el snapshot |
| `mcp__charles__list_recordings` | Ninguno | Lista los archivos de grabación guardados | Elegir un paquete de tráfico histórico |
| `mcp__charles__list_sessions` | Ninguno | Lista las sesiones históricas de forma compatible | Compatibilidad con nomenclatura antigua |
| `mcp__charles__get_recording_snapshot` | `path?` | Lee los metadatos del snapshot de una grabación guardada | Inspeccionar una recording sin conexión |
| `mcp__charles__analyze_recorded_traffic` | `recording_path?`,`preset?`,`host_contains?`,`path_contains?`,`method_in?`,`status_in?`,`request_body_contains?`,`response_body_contains?`,`max_items?` | Analiza una grabación histórica | Revisión sin conexión |
| `mcp__charles__query_recorded_traffic` | `host_contains?`,`http_method?`,`keyword_regex?`,`keep_request?`,`keep_response?` | Consulta la recording guardada más reciente | Filtrar rápidamente el tráfico histórico |
| `mcp__charles__proxy_by_time` | `record_seconds` | Captura o lee el paquete histórico más reciente durante un tiempo fijo | Análisis rápido por ventana de tiempo |
| `mcp__charles__filter_func` | `capture_seconds`,`host_contains?`,`http_method?`,`keyword_regex?`,`keep_request?`,`keep_response?` | Filtra el tráfico por ventana de tiempo y condiciones | Reducir rápidamente el alcance |
| `mcp__charles__throttling` | `preset` | Configura un preset de red débil/limitación de velocidad en Charles | Reproducción y verificación de comportamiento en red débil |

### 5.4 Flujo de trabajo recomendado

1. `charles_status`
2. Confirmar que Charles ya está escuchando, que el proxy de Android apunta a la máquina de captura, y que el certificado de Charles está instalado si se necesita HTTPS
3. `reset_environment` (opcional, para un experimento limpio)
4. `start_live_capture`
5. Operar la App
6. `query_live_capture_entries`
7. `get_traffic_entry_detail`
8. `group_capture_analysis` / `get_capture_analysis_stats`
9. `stop_live_capture`, con `persist: true` si es necesario
10. `analyze_recorded_traffic` / `query_recorded_traffic`

### 5.5 Ejemplos de invocación

Iniciar captura en vivo:

```json
{
  "reset_session": true,
  "include_existing": false
}
```

Filtrar el tráfico de interfaces en vivo:

```json
{
  "capture_id": "capture-id-from-start",
  "preset": "api_focus",
  "host_contains": "api.example.com",
  "max_items": 10
}
```

### 5.6 Puntos a tener en cuenta

- El MCP `charles` no configura por ti el proxy del sistema Android; primero hay que completar la escucha de Charles, el proxy del dispositivo y la preparación del certificado
- Para la búsqueda en tiempo real, prioriza `query_live_capture_entries`, no uses por defecto `read_live_capture` que avanza el cursor
- `get_traffic_entry_detail` por defecto solo muestra la vista previa para ahorrar contexto; solo activa `include_full_body` cuando realmente necesites el contenido original
- Si quieres revisar el resultado de la captura, se recomienda `persist: true` al finalizar la live capture
- Si Charles ya está en ejecución y no quieres vaciar la sesión actual, usa `adopt_existing: true`

---

## 6. `burp`: operación conjunta con Burp Suite

### 6.1 Posicionamiento

El MCP `burp` es la capa de control y acceso a datos orientada a Burp Suite, adecuada para:

- Leer el historial del proxy
- Enviar solicitudes a Repeater / Intruder
- Enviar solicitudes HTTP/1.1, HTTP/2
- Generar payloads de Collaborator
- Ver los hallazgos del scanner
- Leer y escribir el contenido del editor actual
- Ajustar la intercepción del proxy y el estado de ejecución de tareas
- Leer y escribir la configuración de Burp

### 6.2 Lista de métodos

| Herramienta | Parámetros principales | Función | Uso típico |
| --- | --- | --- | --- |
| `mcp__burp__base64_encode` | `content` | Codificación Base64 | Construir payload |
| `mcp__burp__base64_decode` | `content` | Decodificación Base64 | Ver datos codificados |
| `mcp__burp__url_encode` | `content` | Codificación URL | Construir parámetros |
| `mcp__burp__url_decode` | `content` | Decodificación URL | Restaurar parámetros |
| `mcp__burp__generate_random_string` | `length`,`characterSet` | Genera una cadena aleatoria | Token, valores límite, cadenas de sondeo |
| `mcp__burp__get_active_editor_contents` | Ninguno | Obtiene el contenido del editor actual | Leer una solicitud editada manualmente |
| `mcp__burp__set_active_editor_contents` | `text` | Establece el contenido del editor actual | Rellenar automáticamente una plantilla de solicitud |
| `mcp__burp__create_repeater_tab` | `content`,`targetHostname`,`targetPort`,`usesHttps`,`tabName?` | Crea una nueva pestaña de Repeater | Enviar solicitud a Repeater |
| `mcp__burp__send_to_intruder` | `content`,`targetHostname`,`targetPort`,`usesHttps`,`tabName?` | Envía a Intruder | Fuerza bruta/pruebas por lotes |
| `mcp__burp__send_http1_request` | `content`,`targetHostname`,`targetPort`,`usesHttps` | Envía una solicitud HTTP/1.1 | Reenvío preciso |
| `mcp__burp__send_http2_request` | `pseudoHeaders`,`headers`,`requestBody`,`targetHostname`,`targetPort`,`usesHttps` | Envía una solicitud HTTP/2 | Escenarios específicos de H2 |
| `mcp__burp__generate_collaborator_payload` | `customData?` | Genera un dominio OOB | Pruebas de SSRF / RCE / Blind XXE |
| `mcp__burp__get_collaborator_interactions` | `payloadId?` | Consulta las interacciones OOB | Ver si hubo salida |
| `mcp__burp__get_proxy_http_history` | `count`,`offset` | Lee el historial HTTP del proxy | Revisar solicitudes |
| `mcp__burp__get_proxy_http_history_regex` | `count`,`offset`,`regex` | Filtra el historial HTTP por regex | Filtrado preciso |
| `mcp__burp__get_proxy_websocket_history` | `count`,`offset` | Lee el historial WS | Analizar WebSocket |
| `mcp__burp__get_proxy_websocket_history_regex` | `count`,`offset`,`regex` | Filtra el historial WS por regex | Buscar token, campos de comando |
| `mcp__burp__get_scanner_issues` | `count`,`offset` | Lista los hallazgos del scanner | Revisión de vulnerabilidades |
| `mcp__burp__output_project_options` | Ninguno | Exporta la configuración a nivel de proyecto | Ver el esquema de configuración |
| `mcp__burp__output_user_options` | Ninguno | Exporta la configuración a nivel de usuario | Ver el esquema de configuración |
| `mcp__burp__set_project_options` | `json` | Establece la configuración a nivel de proyecto | Ajuste automatizado |
| `mcp__burp__set_user_options` | `json` | Establece la configuración a nivel de usuario | Configuración global de usuario |
| `mcp__burp__set_proxy_intercept_state` | `intercepting` | Activa/desactiva la intercepción del proxy | Activar/desactivar Intercept |
| `mcp__burp__set_task_execution_engine_state` | `running` | Activa/desactiva el motor de ejecución de tareas | Pausar/reanudar tareas de escaneo |

### 6.3 Ejemplos de invocación típicos

Crear Repeater:

```json
{
  "content": "GET / HTTP/1.1\r\nHost: example.com\r\n\r\n",
  "targetHostname": "example.com",
  "targetPort": 443,
  "usesHttps": true,
  "tabName": "home"
}
```

Generar Collaborator:

```json
{
  "customData": "ssrf-test"
}
```

### 6.4 Puntos a tener en cuenta

- El cuerpo y los headers de `send_http2_request` están separados, no escribas los headers dentro del body
- Antes de cambiar la configuración se recomienda primero `output_project_options` / `output_user_options`
- La detección OOB generalmente sigue este patrón: `generate_collaborator_payload` -> inyectar en el punto de negocio -> `get_collaborator_interactions`
- `get_proxy_http_history_regex` es muy adecuado para escribir un skill que "filtre automáticamente el historial de solicitudes relevantes"

---

## 7. `chrome_devtools`: automatización de navegador, diagnóstico de páginas y análisis de rendimiento

### 7.1 Posicionamiento

`chrome_devtools` se encarga del control automatizado de páginas del navegador y la observación a nivel de DevTools. Las capacidades principales incluyen:

- Abrir/cerrar/seleccionar páginas
- Navegación, actualización, simulación de dispositivos
- Snapshot del DOM, capturas de pantalla
- Clics, entrada de texto, subida de archivos
- Listar solicitudes de red e información de consola
- Ejecutar scripts en la página
- Auditoría con Lighthouse
- Trace de rendimiento
- Snapshot de heap

Si necesitas "operar la página como lo haría una persona en el navegador", es la primera opción.

### 7.2 Control de página y contexto

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__chrome_devtools__list_pages` | Ninguno | Lista las páginas abiertas actualmente |
| `mcp__chrome_devtools__new_page` | `url`,`background?`,`isolatedContext?`,`timeout?` | Crea una nueva pestaña y accede a la URL |
| `mcp__chrome_devtools__select_page` | `pageId`,`bringToFront?` | Cambia la página de operación actual |
| `mcp__chrome_devtools__close_page` | `pageId` | Cierra la página |
| `mcp__chrome_devtools__navigate_page` | `type`,`url?`,`timeout?`,`ignoreCache?`,`handleBeforeUnload?`,`initScript?` | Navegación por URL, avanzar, retroceder, actualizar |
| `mcp__chrome_devtools__resize_page` | `width`,`height` | Ajusta el tamaño del navegador |
| `mcp__chrome_devtools__emulate` | `viewport?`,`colorScheme?`,`geolocation?`,`networkConditions?`,`userAgent?`,`cpuThrottlingRate?` | Simulación de dispositivo/red/UA |

### 7.3 Estructura de página y capturas de pantalla

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__chrome_devtools__take_snapshot` | `filePath?`,`verbose?` | Obtiene el snapshot del árbol de accesibilidad de la página, devuelve el `uid` de los elementos |
| `mcp__chrome_devtools__take_screenshot` | `filePath?`,`format?`,`fullPage?`,`quality?`,`uid?` | Captura de pantalla de página o elemento |
| `mcp__chrome_devtools__wait_for` | `text`,`timeout?` | Espera a que aparezca cierto texto |

Notas:

- Primero `take_snapshot`, luego usa el `uid` obtenido para hacer click/fill/hover; esto suele ser lo más estable
- El `uid` es un identificador de elemento dentro del contexto del snapshot actual, puede cambiar después de actualizar el snapshot

### 7.4 Interacción con la página

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__chrome_devtools__click` | `uid`,`dblClick?`,`includeSnapshot?` | Clic en el elemento |
| `mcp__chrome_devtools__hover` | `uid`,`includeSnapshot?` | Pasar el cursor sobre el elemento |
| `mcp__chrome_devtools__drag` | `from_uid`,`to_uid`,`includeSnapshot?` | Arrastrar |
| `mcp__chrome_devtools__fill` | `uid`,`value`,`includeSnapshot?` | Rellenar un solo campo de entrada |
| `mcp__chrome_devtools__fill_form` | `elements`,`includeSnapshot?` | Rellenar formulario por lotes |
| `mcp__chrome_devtools__type_text` | `text`,`submitKey?` | Escribir texto en el foco actual |
| `mcp__chrome_devtools__press_key` | `key`,`includeSnapshot?` | Atajos de teclado, teclas especiales |
| `mcp__chrome_devtools__upload_file` | `uid`,`filePath`,`includeSnapshot?` | Subir archivo |
| `mcp__chrome_devtools__handle_dialog` | `action`,`promptText?` | Gestionar alert/confirm/prompt |

### 7.5 Scripts de página e información de depuración

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__chrome_devtools__evaluate_script` | `function`,`args?` | Ejecutar JS dentro de la página |
| `mcp__chrome_devtools__list_console_messages` | `includePreservedMessages?`,`pageIdx?`,`pageSize?`,`types?` | Ver los logs de consola |
| `mcp__chrome_devtools__get_console_message` | `msgid` | Obtener el detalle de un mensaje de consola específico |
| `mcp__chrome_devtools__list_network_requests` | `includePreservedRequests?`,`pageIdx?`,`pageSize?`,`resourceTypes?` | Ver la lista de solicitudes de red |
| `mcp__chrome_devtools__get_network_request` | `reqid?`,`requestFilePath?`,`responseFilePath?` | Ver o exportar el detalle/cuerpo de una solicitud |

### 7.6 Auditoría y rendimiento

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__chrome_devtools__lighthouse_audit` | `device?`,`mode?`,`outputDirPath?` | Ejecutar Lighthouse (sin análisis de rendimiento) |
| `mcp__chrome_devtools__performance_start_trace` | `autoStop?`,`filePath?`,`reload?` | Iniciar trace de rendimiento |
| `mcp__chrome_devtools__performance_stop_trace` | `filePath?` | Detener trace de rendimiento |
| `mcp__chrome_devtools__performance_analyze_insight` | `insightName`,`insightSetId` | Analizar un insight de rendimiento específico |
| `mcp__chrome_devtools__take_memory_snapshot` | `filePath` | Exportar snapshot de heap de JS |

### 7.7 Flujo de trabajo recomendado

#### Automatización de página

1. `new_page`
2. `take_snapshot`
3. `click` / `fill` / `press_key`
4. `wait_for`
5. `take_screenshot`

#### Capturar solicitudes de página

1. `new_page`
2. Interacción con la página
3. `list_network_requests`
4. `get_network_request`

#### Diagnóstico de rendimiento

1. `navigate_page`
2. `performance_start_trace`
3. Operación de página o recarga
4. `performance_stop_trace`
5. `performance_analyze_insight`

### 7.8 Puntos a tener en cuenta

- Antes de interactuar con el DOM, prioriza `take_snapshot`
- Después de recargar la página, el `uid` antiguo puede no seguir siendo válido
- Al obtener el cuerpo de solicitud/respuesta, usa `requestFilePath` / `responseFilePath` cuando sea necesario para guardarlo en archivo
- Si te interesa "la cadena de llamadas JS y los breakpoints", `js_reverse` suele ser más adecuado que esto

---

## 8. `context7`: búsqueda de documentación en tiempo real y ejemplos

### 8.1 Posicionamiento

`context7` es adecuado para consultar librerías de terceros, frameworks, documentación oficial y ejemplos de código, especialmente útil en escenarios de escritura de skills donde "se necesita referenciar el uso oficial más reciente".

### 8.2 Métodos

#### `mcp__context7__resolve_library_id`

- Función: primero resuelve el "nombre de la librería" a un ID de documentación reconocible por Context7
- Parámetros:
  - `libraryName`
  - `query`
- Puntos clave del resultado devuelto:
  - `libraryId`
  - Nombre de la librería
  - Descripción
  - Cantidad de snippets
  - Reputación de la fuente
  - Puntuación de benchmark

#### `mcp__context7__query_docs`

- Función: buscar documentación y ejemplos basándose en el `libraryId` ya resuelto
- Parámetros:
  - `libraryId`
  - `query`

### 8.3 Flujo de trabajo recomendado

1. `resolve_library_id`
2. Elegir el `libraryId` más adecuado
3. `query_docs`

### 8.4 Ejemplo

Resolver primero:

```json
{
  "libraryName": "Next.js",
  "query": "App Router middleware authentication examples"
}
```

Luego consultar:

```json
{
  "libraryId": "/vercel/next.js",
  "query": "How to protect routes in App Router middleware?"
}
```

### 8.5 Puntos a tener en cuenta al escribir un skill

- Si el usuario da un nombre de librería ambiguo, primero `resolve_library_id`
- Este es un "MCP de preguntas y respuestas sobre documentación", no una búsqueda genérica de páginas web
- Para preguntas técnicas, priorízalo como un "buscador de documentación oficial"

---

## 9. `everything_search`: búsqueda local de archivos ultrarrápida

### 9.1 Posicionamiento

Este es un MCP de búsqueda de archivos local para Windows, adecuado para encontrar archivos rápidamente en directorios grandes, en todo el disco y con condiciones difusas.

### 9.2 Métodos

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__everything_search__search` | `query`,`maxResults?`,`parentPath?`,`filesOnly?`,`foldersOnly?`,`matchPath?`,`regex?`,`caseSensitive?`,`wholeWord?`,`sortBy?`,`sortDescending?`,`showSize?`,`showDateModified?` | Buscar archivos o directorios |
| `mcp__everything_search__get_file_info` | `filename` | Obtener información detallada de un archivo específico |

### 9.3 Ejemplo

Buscar todos los `.apk` en un directorio específico:

```json
{
  "query": "*.apk",
  "parentPath": "C:\\Users\\28484",
  "filesOnly": true,
  "maxResults": 50
}
```

### 9.4 Escenarios de uso

- Buscar APK / SO / logs / archivos exportados
- Encontrar archivos objetivo para skills de ingeniería inversa
- Buscar configuración, scripts, bases de datos, certificados en directorios grandes

---

## 10. `fetch`: descarga genérica de páginas web

### 10.1 Posicionamiento

`fetch` es una herramienta genérica para "descargar contenido de páginas web/URL", adecuada para:

- Descargar contenido de páginas web
- Descargar páginas de documentación
- Leer HTML
- Extracción simple de contenido de páginas web

### 10.2 Métodos

#### `mcp__fetch__fetch`

- Parámetros:
  - `url`
  - `max_length?`
  - `raw?`
  - `start_index?`
- Función:
  - Obtener el contenido de la página web
  - Puede devolver contenido simplificado en formato tipo markdown
  - Se puede especificar un offset para continuar leyendo páginas largas

### 10.3 Ejemplo

```json
{
  "url": "https://example.com",
  "max_length": 6000
}
```

### 10.4 Puntos a tener en cuenta

- Más adecuado para "descarga de contenido de una URL conocida", no es un motor de búsqueda
- Si la página es demasiado larga, se puede leer por fragmentos usando `start_index`
- En escenarios de documentación técnica, si está disponible `context7`, normalmente se prioriza `context7`

---

## 11. `frida_mcp`: inyección dinámica y hook en tiempo de ejecución de Android

### 11.1 Posicionamiento

`frida_mcp` es la capa de análisis dinámico de Android, con usos principales:

- Verificar/iniciar/detener `frida-server`
- Enumerar aplicaciones
- Obtener la aplicación en primer plano actual
- `spawn` o `attach` al proceso objetivo
- Inyectar scripts JS de Frida
- Obtener el log de salida del script

Escenarios adecuados:

- Bypass de SSL Pinning
- Impresión de parámetros/valores de retorno de métodos
- Captura dinámica de firmas, tokens, headers
- Observación en tiempo de ejecución de capa native/Java

### 11.2 Lista de métodos

| Herramienta | Parámetros principales | Función | Uso típico |
| --- | --- | --- | --- |
| `mcp__frida_mcp__check_frida_status` | Ninguno | Verifica si frida-server está en ejecución | Verificación previa |
| `mcp__frida_mcp__start_frida_server` | Ninguno | Inicia frida-server | Preparación para análisis dinámico |
| `mcp__frida_mcp__stop_frida_server` | Ninguno | Detiene frida-server | Limpieza del entorno |
| `mcp__frida_mcp__list_applications` | Ninguno | Lista las aplicaciones del dispositivo | Encontrar el nombre de paquete, ver si está en ejecución |
| `mcp__frida_mcp__get_frontmost_application` | Ninguno | Obtiene la aplicación en primer plano actual | Confirmar a qué paquete pertenece la interfaz actual |
| `mcp__frida_mcp__spawn` | `package_name`,`initial_script?`,`script_file_path?`,`output_file?` | Inicia en suspensión y adjunta la aplicación objetivo | Hook en un momento temprano |
| `mcp__frida_mcp__attach` | `target`,`initial_script?`,`script_file_path?`,`output_file?` | Se adjunta a un PID o nombre de paquete | Inyección en una aplicación ya en ejecución |
| `mcp__frida_mcp__get_messages` | `max_messages?` | Obtiene el buffer de salida de hook/log | Ver el resultado impreso por el script |

### 11.3 Diferencia entre `attach` y `spawn`

- `attach`
  - Se usa cuando el objetivo ya está en ejecución
  - Se puede adjuntar por PID o nombre de paquete
  - Adecuado para observación temporal, hook tardío

- `spawn`
  - Se usa para inyectar el script antes de que la aplicación se reanude
  - Adecuado para carga temprana de clases, flujo de arranque, inicialización de firma, bypass temprano de SSL pinning

### 11.4 Ejemplo

Verificar estado:

```json
{}
```

Iniciar por nombre de paquete e inyectar un archivo de script:

```json
{
  "package_name": "com.example.app",
  "script_file_path": "C:\\Users\\28484\\Desktop\\hook.js",
  "output_file": "C:\\Users\\28484\\Desktop\\frida.log"
}
```

Adjuntar a una aplicación en ejecución y escribir directamente un script en línea:

```json
{
  "target": "com.example.app",
  "initial_script": "Java.perform(function(){ console.log('hook loaded'); });"
}
```

### 11.5 Flujo de trabajo recomendado

1. `check_frida_status`
2. Si no está en ejecución, `start_frida_server`
3. `list_applications` o `get_frontmost_application`
4. `spawn` o `attach`
5. `get_messages`

### 11.6 Puntos a tener en cuenta

- Requiere que el entorno del dispositivo tenga `frida-server` desplegado correctamente
- `script_file_path` tiene mayor prioridad que `initial_script`
- La mayoría de las tareas de localización de firma/cifrado suelen seguir: localización estática con `jadx` -> verificación dinámica con `frida_mcp`

---

## 12. `ida_pro_mcp`: análisis estático con IDA Pro y refactorización por lotes

### 12.1 Posicionamiento

`ida_pro_mcp` es el MCP de análisis estático más completo entre las capacidades actuales. No es "solo ver la descompilación", sino que cubre:

- Abrir/cambiar instancias de IDA
- Survey rápido del binario
- Listar funciones, globales, imports, tipos
- Consultar xref / callgraph / basic block
- Descompilar, desensamblar, exportar información de funciones
- Modificar comentarios, renombrar, declarar tipos, crear variables de pila
- Leer memoria, parchear bytes, parchear ensamblador
- Ejecutar scripts en Python dentro del contexto de IDA

Si el skill está orientado a ingeniería inversa native, análisis de malware, parches, renombrado por lotes, es prácticamente el núcleo.

### 12.2 Herramienta de entrada fuertemente recomendada

#### `mcp__ida_pro_mcp__survey_binary`

Esta es la herramienta más adecuada para hacer el primer triage. Puede dar de una sola vez:

- Metainformación del archivo
- Distribución de segmentos
- Punto de entrada
- Información estadística
- Cadenas de alta frecuencia
- Funciones de alto valor
- Clasificación de imports
- Panorama del grafo de llamadas

Al escribir un skill se puede establecer explícitamente:
"Después de comenzar el análisis del IDB, primero invoca `survey_binary`, no uses `list_funcs` de forma ciega."

### 12.3 Gestión de instancias y sesiones

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__ida_pro_mcp__list_instances` | Ninguno | Lista las instancias de IDA conectables actualmente |
| `mcp__ida_pro_mcp__select_instance` | `port`,`host?` | Cambia la instancia de IDA a la que apunta el MCP actual |
| `mcp__ida_pro_mcp__open_file` | `file_path`,`autonomous?`,`new_database?`,`switch?`,`timeout?` | Abre un archivo en una nueva instancia de IDA |
| `mcp__ida_pro_mcp__server_health` | Ninguno | Ver el estado de salud del IDB/servicio actual |
| `mcp__ida_pro_mcp__server_warmup` | `build_caches?`,`init_hexrays?`,`wait_auto_analysis?` | Precalienta el entorno de análisis |
| `mcp__ida_pro_mcp__idb_save` | `path?` | Guarda el IDB actual |

### 12.4 Panorama y descubrimiento del binario

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__ida_pro_mcp__survey_binary` | `detail_level?` | Panorama del binario |
| `mcp__ida_pro_mcp__entity_query` | Objeto de consulta complejo | Consulta functions/globals/imports/strings/names |
| `mcp__ida_pro_mcp__find_regex` | `pattern`,`limit?`,`offset?` | Buscar con regex en cadenas |
| `mcp__ida_pro_mcp__find` | `targets`,`type`,`limit?`,`offset?` | Buscar cadenas, inmediatos, referencias a datos/código |
| `mcp__ida_pro_mcp__find_bytes` | `patterns`,`limit?`,`offset?` | Búsqueda por patrón de bytes |

### 12.5 Análisis de funciones y grafos

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__ida_pro_mcp__list_funcs` | `queries` | Lista funciones |
| `mcp__ida_pro_mcp__func_query` | Conjunto de condiciones de filtro | Filtra funciones por tamaño/nombre/si tiene tipo |
| `mcp__ida_pro_mcp__func_profile` | Conjunto de consultas | Genera un perfil general de la función |
| `mcp__ida_pro_mcp__lookup_funcs` | `queries` | Consulta funciones por dirección o nombre |
| `mcp__ida_pro_mcp__callees` | `addrs`,`limit?` | Consulta las funciones llamadas |
| `mcp__ida_pro_mcp__callgraph` | `roots`,`max_depth?`,`max_nodes?`,`max_edges?`,`max_edges_per_func?` | Construye el grafo de llamadas |
| `mcp__ida_pro_mcp__basic_blocks` | `addrs`,`offset?`,`max_blocks?` | Obtiene los bloques básicos del CFG |
| `mcp__ida_pro_mcp__analyze_function` | `addr`,`include_asm?` | Análisis compacto de una función individual |
| `mcp__ida_pro_mcp__analyze_batch` | `queries` | Análisis integral por lotes de múltiples funciones |
| `mcp__ida_pro_mcp__analyze_component` | `addrs` | Análisis de componente sobre un grupo de funciones relacionadas |

### 12.6 Descompilación, desensamblado y exportación

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__ida_pro_mcp__decompile` | `addr` | Descompila la función |
| `mcp__ida_pro_mcp__disasm` | `addr`,`offset?`,`max_instructions?`,`include_total?` | Desensambla la función |
| `mcp__ida_pro_mcp__export_funcs` | `addrs`,`format?` | Exporta funciones en JSON / cabecera C / prototipos |

### 12.7 Referencias cruzadas y flujo de datos

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__ida_pro_mcp__xrefs_to` | `addrs`,`limit?` | Obtiene los xrefs to |
| `mcp__ida_pro_mcp__xref_query` | Conjunto de consultas | Consulta por lotes xref según dirección/tipo |
| `mcp__ida_pro_mcp__trace_data_flow` | `addr`,`direction?`,`max_depth?` | Rastrea el flujo de datos en múltiples saltos |
| `mcp__ida_pro_mcp__xrefs_to_field` | `queries` | Consulta referencias a campos de struct |

### 12.8 Sistema de tipos y recuperación de estructuras

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__ida_pro_mcp__type_query` | Conjunto de consultas | Consulta tipos locales |
| `mcp__ida_pro_mcp__type_inspect` | `queries` | Ver la declaración y los miembros de un tipo |
| `mcp__ida_pro_mcp__declare_type` | `decls` | Inyecta declaraciones de tipo en C |
| `mcp__ida_pro_mcp__set_type` | `edits` | Establece el tipo de función/variable/variable local |
| `mcp__ida_pro_mcp__type_apply_batch` | `batch` | Aplica tipos por lotes |
| `mcp__ida_pro_mcp__infer_types` | `addrs` | Infiere tipos |
| `mcp__ida_pro_mcp__enum_upsert` | `queries` | Crea/complementa enumeraciones |
| `mcp__ida_pro_mcp__search_structs` | `filter` | Busca structs/uniones |
| `mcp__ida_pro_mcp__read_struct` | `queries` | Lee los valores de los campos de un struct en una dirección |

### 12.9 Marco de pila y variables locales

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__ida_pro_mcp__stack_frame` | `addrs` | Obtiene el marco de pila de la función |
| `mcp__ida_pro_mcp__declare_stack` | `items` | Declara variables de pila |
| `mcp__ida_pro_mcp__delete_stack` | `items` | Elimina variables de pila |

### 12.10 Renombrado, comentarios y verificación de diferencias

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__ida_pro_mcp__rename` | `batch` | Renombra por lotes funciones/datos/variables locales/de pila |
| `mcp__ida_pro_mcp__set_comments` | `items` | Establece comentarios |
| `mcp__ida_pro_mcp__append_comments` | `items` | Agrega comentarios |
| `mcp__ida_pro_mcp__diff_before_after` | `addr`,`action`,`action_args` | Aplica rename/type/comment y compara la descompilación antes/después |

### 12.11 Lectura de memoria en bruto y parcheo

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__ida_pro_mcp__get_bytes` | `regions` | Lee bytes |
| `mcp__ida_pro_mcp__get_int` | `queries` | Lee enteros |
| `mcp__ida_pro_mcp__get_string` | `addrs` | Lee cadenas |
| `mcp__ida_pro_mcp__get_global_value` | `queries` | Lee el valor de una variable global |
| `mcp__ida_pro_mcp__put_int` | `items` | Escribe enteros |
| `mcp__ida_pro_mcp__patch` | `patches` | Parchea bytes |
| `mcp__ida_pro_mcp__patch_asm` | `items` | Parchea ensamblador |
| `mcp__ida_pro_mcp__undefine` | `items` | Cancela la definición, deja como bytes en bruto |
| `mcp__ida_pro_mcp__define_code` | `items` | Define bytes como código |
| `mcp__ida_pro_mcp__define_func` | `items` | Define una función |

### 12.12 Imports, globales, instrucciones y consulta de entidades

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__ida_pro_mcp__imports` | `count`,`offset` | Lista imports |
| `mcp__ida_pro_mcp__imports_query` | `queries` | Filtra imports por módulo/nombre |
| `mcp__ida_pro_mcp__list_globals` | `queries` | Lista variables globales |
| `mcp__ida_pro_mcp__insn_query` | `queries` | Consulta patrones de instrucciones |
| `mcp__ida_pro_mcp__int_convert` | `inputs` | Conversión de formato numérico |

### 12.13 Extensión Python

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__ida_pro_mcp__py_eval` | `code` | Ejecuta un fragmento de Python en el entorno de IDA |
| `mcp__ida_pro_mcp__py_exec_file` | `file_path` | Ejecuta un archivo de script Python completo |

### 12.14 Flujo de trabajo recomendado

#### Triage inicial

1. `server_health`
2. `server_warmup`
3. `survey_binary`
4. `find_regex` / `imports_query`
5. `analyze_function` / `decompile`

#### Recuperación de semántica

1. `decompile`
2. `stack_frame`
3. `type_query` / `type_inspect`
4. `set_type` / `declare_type`
5. `rename`
6. `diff_before_after`

#### Rastreo de cadenas sensibles

1. `find_regex`
2. `xrefs_to`
3. `trace_data_flow`
4. `analyze_component`

### 12.15 Recomendaciones para escribir un skill

- Fijar desde el inicio "primero `survey_binary`" suele ser buena estrategia
- Si se va a hacer renombrado por lotes, es mejor usar `diff_before_after` como paso de verificación
- Para analizar tablas de despacho de JNI/crypto, `trace_data_flow` es muy valioso
- `type_apply_batch` es adecuado para skills de "corrección automática de tipos"
- `py_eval` / `py_exec_file` son adecuados para automatización avanzada, pero se debe definir con cautela el alcance del script

---

## 13. `jadx`: descompilación estática de APK y navegación de código Android

### 13.1 Posicionamiento

El MCP `jadx` es el punto de entrada del análisis estático de Android, adecuado para:

- Leer `AndroidManifest.xml`
- Encontrar la Activity principal, componentes, componentes exportados
- Buscar clases/métodos/campos
- Obtener el código fuente de clases, métodos, smali
- Consultar relaciones de referencia
- Renombrar clases/métodos/campos/variables/paquetes

Su diferencia con `ida_pro_mcp` está en que:

- `jadx` se orienta más a APK en capa Java/Kotlin
- `ida_pro_mcp` se orienta más a binarios native / so / ELF / PE

### 13.2 Información de entrada y Manifest

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__jadx__get_android_manifest` | Ninguno | Obtiene el Manifest completo |
| `mcp__jadx__get_main_activity_class` | Ninguno | Obtiene la Activity principal |
| `mcp__jadx__get_main_application_classes_names` | Ninguno | Obtiene los nombres de las clases principales bajo el paquete principal |
| `mcp__jadx__get_main_application_classes_code` | `count?`,`offset?` | Obtiene el código de las clases principales |
| `mcp__jadx__get_manifest_component` | `component_type`,`only_exported?` | Obtiene información de componentes activity/service/provider/receiver |

### 13.3 Lectura de clases y código fuente

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__jadx__get_all_classes` | `count?`,`offset?` | Obtiene todos los nombres de clase |
| `mcp__jadx__fetch_current_class` | Ninguno | Obtiene el código fuente de la clase seleccionada actualmente en la GUI |
| `mcp__jadx__get_class_source` | `class_name` | Obtiene el código fuente Java de una clase |
| `mcp__jadx__get_smali_of_class` | `class_name` | Obtiene el smali de una clase |
| `mcp__jadx__get_methods_of_class` | `class_name` | Lista los métodos |
| `mcp__jadx__get_fields_of_class` | `class_name` | Lista los campos |
| `mcp__jadx__get_method_by_name` | `class_name`,`method_name` | Obtiene el código fuente de un método específico |
| `mcp__jadx__get_selected_text` | Ninguno | Obtiene el texto seleccionado actualmente |

### 13.4 Recursos y cadenas

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__jadx__get_all_resource_file_names` | `count?`,`offset?` | Lista los archivos de recursos |
| `mcp__jadx__get_resource_file` | `resource_name` | Lee el contenido de un archivo de recursos |
| `mcp__jadx__get_strings` | `count?`,`offset?` | Obtiene el contenido de strings.xml |

### 13.5 Búsqueda y referencias

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__jadx__search_classes_by_keyword` | `search_term`,`package?`,`search_in?`,`offset?`,`count?` | Búsqueda transversal de clases/métodos/campos/contenido de código |
| `mcp__jadx__search_method_by_name` | `method_name` | Buscar por nombre de método |
| `mcp__jadx__get_xrefs_to_class` | `class_name`,`count?`,`offset?` | Consulta referencias a una clase |
| `mcp__jadx__get_xrefs_to_field` | `class_name`,`field_name`,`count?`,`offset?` | Consulta referencias a un campo |
| `mcp__jadx__get_xrefs_to_method` | `class_name`,`method_name`,`count?`,`offset?` | Consulta referencias a un método |

### 13.6 Renombrado

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__jadx__rename_class` | `class_name`,`new_name` | Renombra una clase |
| `mcp__jadx__rename_field` | `class_name`,`field_name`,`new_name` | Renombra un campo |
| `mcp__jadx__rename_method` | `method_name`,`new_name` | Renombra un método |
| `mcp__jadx__rename_variable` | `class_name`,`method_name`,`variable_name`,`new_name`,`reg?`,`ssa?` | Renombra una variable |
| `mcp__jadx__rename_package` | `old_package_name`,`new_package_name` | Renombra un paquete |

### 13.7 Relacionado con depuración

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__jadx__debug_get_threads` | Ninguno | Ver los hilos de depuración |
| `mcp__jadx__debug_get_stack_frames` | Ninguno | Ver la pila de llamadas actual |
| `mcp__jadx__debug_get_variables` | Ninguno | Ver las variables actuales |

### 13.8 Flujo de trabajo recomendado

#### Análisis preliminar de APK

1. `get_android_manifest`
2. `get_main_activity_class`
3. `get_manifest_component`
4. `search_classes_by_keyword`
5. `get_class_source`

#### Localización de firma/interfaz

1. `search_classes_by_keyword` buscando `okhttp`, `retrofit`, `sign`, `token`, `encrypt`
2. `get_xrefs_to_method`
3. `get_method_by_name`
4. Cambiar a `frida_mcp` para verificación dinámica cuando sea necesario

### 13.9 Puntos a tener en cuenta

- `search_classes_by_keyword` es una herramienta de entrada de muy alto valor en `jadx`
- `search_in` puede especificar `class,method,field,code,comment`
- Para escenarios JNI, generalmente `jadx` encuentra el punto de registro native, y `ida_pro_mcp` profundiza en el so

---

## 14. `js_reverse`: ingeniería inversa de JavaScript del frontend Web y depuración con breakpoints

### 14.1 Posicionamiento

`js_reverse` es un MCP profesional orientado a la ingeniería inversa del frontend Web. Su diferencia con `chrome_devtools`:

- `chrome_devtools` se orienta más a operación de página, red, snapshot, rendimiento
- `js_reverse` se orienta más a código fuente JS, breakpoints, cadena de llamadas, iniciador de XHR, rastreo de funciones, guardado de código fuente

Escenarios de aplicación:

- Analizar funciones de firma
- Rastrear la cadena de origen de XHR/Fetch
- Localizar funciones ofuscadas
- Buscar palabras clave en el código fuente JS
- Obtener variables en el contexto de ejecución
- Analizar patrones de mensajes de WebSocket

### 14.2 Página y contexto

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__js_reverse__new_page` | `url`,`timeout?` | Crea una nueva página |
| `mcp__js_reverse__select_page` | `pageIdx?` | Lista o cambia de página |
| `mcp__js_reverse__navigate_page` | `type`,`url?`,`timeout?`,`ignoreCache?` | Navegar/actualizar |
| `mcp__js_reverse__select_frame` | `frameIdx?` | Lista o cambia de frame/iframe |

### 14.3 Enumeración de scripts y lectura de código fuente

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__js_reverse__list_scripts` | `filter?` | Lista los scripts de la página actual |
| `mcp__js_reverse__search_in_sources` | `query`,`isRegex?`,`caseSensitive?`,`excludeMinified?`,`urlFilter?`,`maxResults?`,`maxLineLength?` | Busca en todos los scripts |
| `mcp__js_reverse__get_script_source` | `url?`,`scriptId?`,`startLine?`,`endLine?`,`offset?`,`length?` | Lee un fragmento pequeño de código fuente |
| `mcp__js_reverse__save_script_source` | `filePath`,`url?`,`scriptId?` | Guarda el script completo en el local |

Notas:

- `get_script_source` está diseñado para "ver una parte local", no para descargar el archivo completo
- Para scripts grandes se debe usar `save_script_source`

### 14.4 Breakpoints, rastreo y control de ejecución

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__js_reverse__set_breakpoint_on_text` | `text`,`urlFilter?`,`occurrence?`,`condition?` | Coloca automáticamente un breakpoint según el texto del código |
| `mcp__js_reverse__list_breakpoints` | Ninguno | Lista los breakpoints |
| `mcp__js_reverse__remove_breakpoint` | `breakpointId?`,`url?` | Elimina un breakpoint o un breakpoint de XHR |
| `mcp__js_reverse__pause_or_resume` | Ninguno | Pausa o reanuda la ejecución |
| `mcp__js_reverse__step` | `direction` | Paso a paso over/into/out |
| `mcp__js_reverse__trace_function` | `functionName`,`logArgs?`,`logThis?`,`pause?`,`traceId?`,`urlFilter?` | Rastrea la invocación de una función |
| `mcp__js_reverse__inject_before_load` | `script?`,`identifier?` | Inyecta un script antes de que la página cargue |

### 14.5 Análisis de contexto tras alcanzar un breakpoint

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__js_reverse__get_paused_info` | `frameIndex?`,`includeScopes?`,`maxScopeDepth?` | Obtiene la pila y las variables de scope al alcanzar el breakpoint |
| `mcp__js_reverse__evaluate_script` | `function`,`frameIndex?`,`mainWorld?` | Ejecuta JS en la página actual o en el frame del breakpoint |

### 14.6 Red y cadena de llamadas

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__js_reverse__break_on_xhr` | `url` | Coloca un breakpoint en XHR/Fetch que contenga la URL objetivo |
| `mcp__js_reverse__list_network_requests` | `reqid?`,`pageIdx?`,`pageSize?`,`resourceTypes?`,`urlFilter?`,`includePreservedRequests?` | Ver la lista de solicitudes o el detalle de una solicitud específica |
| `mcp__js_reverse__get_request_initiator` | `requestId` | Ver qué fragmento de JS originó una solicitud específica |
| `mcp__js_reverse__list_console_messages` | `msgid?`,`pageIdx?`,`pageSize?`,`types?`,`includePreservedMessages?` | Ver la consola |

### 14.7 Análisis de WebSocket

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__js_reverse__get_websocket_messages` | `wsid?`,`analyze?`,`groupId?`,`frameIndex?`,`direction?`,`show_content?`,`pageIdx?`,`pageSize?`,`urlFilter?`,`includePreservedConnections?` | Lista conexiones WS, analiza agrupación de mensajes, ver frames específicos |

### 14.8 Captura de pantalla

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__js_reverse__take_screenshot` | `filePath?`,`format?`,`fullPage?`,`quality?` | Captura de pantalla |

### 14.9 Flujo de trabajo recomendado

#### Localizar la función de firma

1. `new_page`
2. `list_scripts`
3. `search_in_sources` buscando `sign` / `token` / palabras clave de ruta
4. `set_breakpoint_on_text`
5. Disparar la solicitud
6. `get_paused_info`
7. `step`
8. `evaluate_script`

#### Rastrear quién originó la solicitud

1. Operar la página
2. `list_network_requests`
3. `get_request_initiator`
4. `break_on_xhr` cuando sea necesario

#### Analizar un script ofuscado

1. `search_in_sources`
2. `save_script_source`
3. `set_breakpoint_on_text`
4. `trace_function`

### 14.10 Recomendaciones para escribir un skill

- Cuando haya una palabra clave del código fuente, prioriza `search_in_sources`
- Cuando se conozca la URL de la solicitud, prioriza `break_on_xhr` o `get_request_initiator`
- Cuando se necesite obtener variables globales dentro del scope del script de página, considera `mainWorld: true`
- Si la página se recarga con frecuencia, prioriza buscar scripts por URL, no dependas en exceso de un `scriptId` temporal

---

## 15. `memory`: grafo de conocimiento estructurado como memoria

### 15.1 Posicionamiento

`memory` es una capa de memoria estructurada a largo plazo, no son notas comunes. Mantiene un grafo de conocimiento de "entidad-observación-relación".

Adecuado para usarse en:

- Registrar preferencias del usuario
- Registrar hechos del proyecto
- Registrar conocimiento estructurado como dispositivos, objetivos, nombres de paquete, nombres de interfaces, puntos de vulnerabilidad
- Conservar hechos estables entre múltiples rondas de tareas

### 15.2 Objetos centrales

- Entidad `entity`
  - Tiene nombre `name`
  - Tiene tipo `entityType`
  - Tiene varias observaciones `observations`

- Relación `relation`
  - `from`
  - `relationType`
  - `to`

### 15.3 Lista de métodos

| Herramienta | Parámetros principales | Función |
| --- | --- | --- |
| `mcp__memory__read_graph` | Ninguno | Lee todo el grafo |
| `mcp__memory__search_nodes` | `query` | Busca entidades/tipos/observaciones |
| `mcp__memory__open_nodes` | `names` | Abre el detalle de entidades específicas |
| `mcp__memory__create_entities` | `entities` | Crea entidades por lotes |
| `mcp__memory__delete_entities` | `entityNames` | Elimina entidades |
| `mcp__memory__add_observations` | `observations` | Agrega observaciones a una entidad |
| `mcp__memory__delete_observations` | `deletions` | Elimina observaciones |
| `mcp__memory__create_relations` | `relations` | Crea relaciones |
| `mcp__memory__delete_relations` | `relations` | Elimina relaciones |

### 15.4 Ejemplo

Crear entidad:

```json
{
  "entities": [
    {
      "name": "com.example.app",
      "entityType": "android_app",
      "observations": [
        "Paquete principal",
        "Usa OkHttp"
      ]
    }
  ]
}
```

Crear relación:

```json
{
  "relations": [
    {
      "from": "com.example.app",
      "relationType": "uses",
      "to": "OkHttp"
    }
  ]
}
```

### 15.5 Usos adecuados para un skill

- Recordar en un skill de ingeniería inversa el nombre de paquete objetivo, la clase de cifrado, el nombre del so, las interfaces clave
- Recordar en un skill de pruebas de penetración el dominio, los puntos de vulnerabilidad, los resultados de escaneo
- Recordar en un skill de automatización el entorno de la cuenta, la forma de despliegue, las rutas convenidas

### 15.6 Puntos a tener en cuenta

- Se recomienda que las relaciones usen voz activa, por ejemplo `App uses OkHttp`
- No es adecuado para guardar texto original muy extenso, es más adecuado para guardar "hechos consultables"

---

## 16. `sequential_thinking`: asistencia de pensamiento paso a paso

### 16.1 Posicionamiento

Esta es una herramienta de "pensamiento explícito multi-paso", usada para análisis de problemas complejos, corrección, ramificación, verificación de hipótesis.
Es adecuada para:

- Planificación de análisis de ingeniería inversa multi-paso
- Exploración de opciones para tareas inciertas
- Decisiones complejas que requieren corregir juicios previos
- Descomposición de tareas grandes

### 16.2 Método

#### `mcp__sequential_thinking__sequentialthinking`

Parámetros principales:

- `thought`
- `thoughtNumber`
- `totalThoughts`
- `nextThoughtNeeded`
- `isRevision?`
- `revisesThought?`
- `branchFromThought?`
- `branchId?`
- `needsMoreThoughts?`

### 16.3 Entendiendo la forma de uso

Esta herramienta no se usa para "consultar datos", sino para enviar el estado del razonamiento al sistema de forma estructurada.
Puedes:

- Empezar el análisis desde el paso 1
- Si descubres que un paso anterior estaba mal, hacer una revision
- Ramificar (branch) desde un paso específico
- Finalmente formar una solución verificada

### 16.4 Escenarios adecuados para un skill

- Skill de triage automático
- Decisión de rutas de explotación de vulnerabilidad en múltiples fases
- Decisión de "primero Java o primero native" en ingeniería inversa
- Filtrado de múltiples funciones de firma candidatas

### 16.5 Ejemplo

```json
{
  "thought": "Primero confirmar si el problema es la firma del frontend o la validación del servidor la que causa el 403.",
  "thoughtNumber": 1,
  "totalThoughts": 4,
  "nextThoughtNeeded": true
}
```

### 16.6 Puntos a tener en cuenta

- Es un potenciador de análisis, no un ejecutor
- No es necesario para tareas simples
- Especialmente valioso para problemas complejos, ambiguos y propensos a desviarse

---

## 17. `scrcpy_vision`: control visual de Android, localización de UI y depuración inalámbrica

### 17.1 Posicionamiento

`scrcpy_vision` integra en un solo conjunto de herramientas ADB, control de baja latencia de scrcpy, captura de pantalla/streaming, y lectura del árbol UI de `uiautomator`, adecuado para:

- Conexión e identificación de dispositivos Android centrada en `serial`
- Localización de UI basada en el texto de los elementos, `resource-id`, `content-desc` de la página actual
- Clic en coordenadas, arrastre, pulsación larga, deslizamiento, entrada de teclado
- Confirmación de estado como despertar/desbloqueo de pantalla, Activity en primer plano, notificaciones, portapapeles
- Depuración ADB por WiFi desde USB
- Captura de un solo frame o streaming continuo, para observar cambios de interfaz y coordinar con la automatización

En comparación con `adb_mcp`, este se orienta más al "control visual" y la "localización a nivel de UI"; `adb_mcp` se orienta más a la gestión básica de dispositivos, instalación de APK, logcat, grabación de pantalla, transferencia de archivos. Al escribir un skill, ambos suelen ser complementarios, no una elección excluyente.

### 17.2 Tipos de skill adecuados

- Automatización de UI y regresión de páginas en Android
- Localización de elementos y guía de interfaz en pruebas dinámicas de App
- Cambio de depuración inalámbrica y control remoto de dispositivos reales
- Verificación del estado de la página antes/después de captura de tráfico/Hook
- Tareas que requieren confirmar la posición de botones, campos de entrada, ventanas emergentes mediante el árbol UI
- Tareas que requieren ver continuamente la pantalla del dispositivo en lugar de solo una captura única

### 17.3 Lista de métodos

#### Conexión e identificación de dispositivos

| Herramienta | Parámetros principales | Función | Uso típico |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_devices_list` | Ninguno | Lista los dispositivos conectados | Obtener el `serial`, confirmar si la conexión USB/WiFi está bien |
| `mcp__scrcpy_vision__android_devices_info` | `serial` | Lee la información básica `getprop` del dispositivo | Ver modelo, versión del sistema, ABI, identificador del dispositivo |
| `mcp__scrcpy_vision__android_adb_enableTcpip` | `serial`,`port?` | Activa la depuración WiFi cuando ya está conectado por USB | Preparación previa para ADB inalámbrico |
| `mcp__scrcpy_vision__android_adb_getDeviceIp` | `serial` | Obtiene la IP WiFi del dispositivo | Preparación para `connectWifi` |
| `mcp__scrcpy_vision__android_adb_connectWifi` | `ipAddress`,`port?` | Conecta el dispositivo por WiFi | Depuración inalámbrica |
| `mcp__scrcpy_vision__android_adb_disconnectWifi` | `ipAddress?` | Desconecta una o todas las conexiones ADB WiFi | Limpieza de la sesión de depuración inalámbrica |

#### Aplicación y estado de ejecución

| Herramienta | Parámetros principales | Función | Uso típico |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_app_start` | `serial`,`packageName`,`activity?` | Inicia la aplicación o una Activity específica | Abrir la App objetivo, ir directo a una página específica |
| `mcp__scrcpy_vision__android_app_stop` | `serial`,`packageName` | Fuerza la detención de la aplicación | Restablecer el estado de la aplicación |
| `mcp__scrcpy_vision__android_apps_list` | `serial`,`system?` | Lista los paquetes instalados | Encontrar el nombre de paquete, confirmar si la aplicación está instalada |
| `mcp__scrcpy_vision__android_activity_current` | `serial` | Obtiene el nombre de paquete y Activity en primer plano actuales | Determinar si el cambio de página se realizó correctamente |
| `mcp__scrcpy_vision__android_notifications_get` | `serial` | Exporta el detalle de las notificaciones actuales | Ver notificaciones de código de verificación, texto de push, origen del paquete |

#### Pantalla, portapapeles y estado del dispositivo

| Herramienta | Parámetros principales | Función | Uso típico |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_screen_isOn` | `serial` | Determina si la pantalla está encendida | Verificar el estado del dispositivo antes de automatizar |
| `mcp__scrcpy_vision__android_screen_wake` | `serial` | Enciende la pantalla | Preparar la operación del dispositivo |
| `mcp__scrcpy_vision__android_screen_sleep` | `serial` | Apaga la pantalla | Cierre o verificación del comportamiento de bloqueo de pantalla |
| `mcp__scrcpy_vision__android_screen_unlock` | `serial` | Intenta despertar y desbloquear el dispositivo | Acceso rápido al escritorio sin bloqueo de seguridad |
| `mcp__scrcpy_vision__android_clipboard_get` | `serial` | Lee el contenido del portapapeles | Obtener código de verificación, enlace compartido, resultado copiado |
| `mcp__scrcpy_vision__android_clipboard_set` | `serial`,`text` | Intenta establecer el portapapeles | Pegar texto preparado en un campo de entrada |

#### Archivos y Shell

| Herramienta | Parámetros principales | Función | Uso típico |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_file_list` | `serial`,`path` | Lista el contenido de un directorio del dispositivo | Ver directorio de exportación, caché, descargas |
| `mcp__scrcpy_vision__android_file_pull` | `serial`,`remotePath`,`localPath` | Descarga un archivo del dispositivo al local | Exportar logs, imágenes, archivos descargados |
| `mcp__scrcpy_vision__android_file_push` | `serial`,`localPath`,`remotePath` | Sube un archivo local al dispositivo | Subir configuración, archivos de prueba, certificados |
| `mcp__scrcpy_vision__android_shell_exec` | `serial`,`command` | Ejecuta cualquier comando `adb shell` | Diagnóstico avanzado, consulta de resolución u operación de dispositivo cuando sea necesario |

#### Lectura del árbol UI y control de entrada

| Herramienta | Parámetros principales | Función | Uso típico |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_ui_dump` | `serial` | Exporta el XML de `uiautomator` de la página actual | Obtener el texto de elementos, nombre de clase, límites, `resource-id` |
| `mcp__scrcpy_vision__android_ui_findElement` | `serial`,`text?`,`resourceId?`,`className?`,`contentDesc?` | Busca elementos por atributos de UI y devuelve las coordenadas centrales | Localizar botones, campos de entrada, controles de ventana emergente |
| `mcp__scrcpy_vision__android_input_tap` | `serial`,`x`,`y` | Clic en coordenadas | Presionar botón, elemento de lista, menú |
| `mcp__scrcpy_vision__android_input_longPress` | `serial`,`x`,`y`,`durationMs?` | Pulsación larga en coordenadas | Invocar menú contextual, preparación de arrastre |
| `mcp__scrcpy_vision__android_input_swipe` | `serial`,`x1`,`y1`,`x2`,`y2`,`durationMs?` | Desliza la pantalla | Desplazar listas, cambiar de página, refrescar deslizando |
| `mcp__scrcpy_vision__android_input_dragDrop` | `serial`,`startX`,`startY`,`endX`,`endY`,`durationMs?` | Arrastra a una posición objetivo | Arrastrar tarjetas, iconos, elementos ordenados |
| `mcp__scrcpy_vision__android_input_pinch` | `serial`,`centerX`,`centerY`,`startDistance`,`endDistance`,`durationMs?` | Simula de forma aproximada el gesto de zoom | Verificación de zoom en mapas, imágenes |
| `mcp__scrcpy_vision__android_input_keyevent` | `serial`,`keycode` | Envía una tecla de Android | Home, Back, Enter, Delete, teclas de volumen |
| `mcp__scrcpy_vision__android_input_text` | `serial`,`text` | Ingresa texto | Inicio de sesión, búsqueda, llenado de formularios |

#### Capacidades visuales

| Herramienta | Parámetros principales | Función | Uso típico |
| --- | --- | --- | --- |
| `mcp__scrcpy_vision__android_vision_snapshot` | `serial` | Obtiene la pantalla actual en PNG mediante `adb exec-out screencap -p` | Confirmación de interfaz con una sola captura |
| `mcp__scrcpy_vision__android_vision_startStream` | `serial`,`frameFps?`,`maxFps?`,`maxSize?` | Inicia el streaming continuo con scrcpy+ffmpeg | Observación continua de cambios de página, en conjunto con control de entrada rápido |
| `mcp__scrcpy_vision__android_vision_stopStream` | `serial` | Detiene el streaming y libera los recursos | Cierre, liberación de recursos de streaming |

### 17.4 Flujo de trabajo recomendado

#### Automatización y localización de páginas

1. `android_devices_list`
2. `android_screen_isOn` / `android_screen_wake` / `android_screen_unlock`
3. Si se van a usar clics o deslizamientos por coordenadas, primero ejecutar `android_shell_exec` con `wm size` para obtener la resolución actual
4. `android_vision_snapshot` o `android_vision_startStream`
5. `android_ui_dump` o `android_ui_findElement`
6. `android_input_tap` / `android_input_text` / `android_input_swipe`
7. `android_activity_current` para confirmar si se entró a la página objetivo
8. Mantener el stream si se necesita observación continua, y `android_vision_stopStream` al finalizar

#### Cambio a ADB por WiFi

1. Ejecutar `android_adb_enableTcpip` tras conectar el dispositivo por USB
2. `android_adb_getDeviceIp`
3. `android_adb_connectWifi`
4. `android_devices_list` para confirmar que la conexión inalámbrica ya aparece
5. Limpiar con `android_adb_disconnectWifi` al terminar las pruebas

### 17.5 Ejemplos de invocación

Activar depuración WiFi:

```json
{
  "serial": "R58N123456A",
  "port": 5555
}
```

Buscar elemento por texto:

```json
{
  "serial": "R58N123456A",
  "text": "Iniciar sesión"
}
```

Iniciar streaming continuo:

```json
{
  "serial": "R58N123456A",
  "frameFps": 5,
  "maxSize": 1080
}
```

Consultar la resolución actual:

```json
{
  "serial": "R58N123456A",
  "command": "wm size"
}
```

### 17.6 Puntos a tener en cuenta

- A excepción de `android_devices_list`, `android_adb_connectWifi`, `android_adb_disconnectWifi`, la mayoría de los métodos requieren primero obtener el `serial` del dispositivo
- Si el streaming de scrcpy ya está iniciado, las operaciones de clic, deslizamiento, entrada de texto priorizarán el canal de control más rápido de scrcpy; de lo contrario se recurre a la entrada ADB
- Para enviar clics, pulsaciones largas, deslizamientos, arrastres o pinch por coordenadas, consulta primero la resolución actual; diferentes dispositivos, orientación horizontal/vertical, escalado o supuestos de tamaño de captura pueden causar desviación de coordenadas
- `android_ui_findElement` es adecuado para localización estática en la página actual; tras un cambio de página se recomienda volver a hacer `ui_dump` o volver a buscar el elemento
- Siempre que se pueda usar `android_ui_findElement` / `android_ui_dump`, evita fijar coordenadas; solo recurre al clic por coordenadas cuando la localización de elementos no sea confiable
- `android_screen_unlock` solo aplica a dispositivos sin PIN/contraseña/patrón u otro bloqueo de seguridad
- `android_clipboard_set` puede estar sujeto a restricciones del sistema en Android 10+, no se garantiza que funcione directamente en todos los dispositivos
- `android_input_pinch` es un gesto aproximado, no es multitáctil real
- `android_shell_exec`, `android_file_push` modifican directamente el entorno del dispositivo; al escribir un skill se debe dejar claro que es una operación de alto riesgo
- Lo que produce `android_vision_startStream` es un recurso en tiempo real y no un archivo guardado; si solo se necesita una captura única, prioriza `android_vision_snapshot`

---

## 18. Agrupación recomendada combinada con la escritura de skills

Para facilitar la escritura posterior de skills, se recomienda organizar por "dominio de tarea" en lugar de dividir mecánicamente por "nombre del servidor de herramientas".

### 18.1 Skill de análisis estático de Android

MCP prioritario:

- `jadx`
- `everything_search`

Flujo común:

1. Encontrar APK / recursos
2. Leer el Manifest
3. Buscar clases clave
4. Descargar código fuente de métodos
5. Rastrear xref

### 18.2 Skill de análisis dinámico de Android

MCP prioritario:

- `adb_mcp`
- `scrcpy_vision`
- `frida_mcp`
- `charles`

Flujo común:

1. Confirmar el dispositivo
2. Instalar la aplicación
3. Según el caso, iniciar el streaming de scrcpy o leer el árbol UI
4. Iniciar la live capture de Charles
5. Inyectar hook
6. Ver solicitudes, interfaz y logs

### 18.3 Skill de ingeniería inversa Native

MCP prioritario:

- `ida_pro_mcp`
- `everything_search`

Flujo común:

1. Encontrar so / exe
2. `survey_binary`
3. Buscar cadenas/imports
4. Descompilar funciones clave
5. Renombrar, corregir tipos, rastrear flujo de datos

### 18.4 Skill de automatización de páginas Web

MCP prioritario:

- `chrome_devtools`

Flujo común:

1. Abrir la página
2. Obtener el snapshot
3. Interactuar con el formulario
4. Capturar solicitudes
5. Captura de pantalla como evidencia

### 18.5 Skill de ingeniería inversa de JS Web

MCP prioritario:

- `js_reverse`
- `chrome_devtools`
- `burp`

Flujo común:

1. Buscar código fuente
2. Colocar breakpoint en la URL de solicitud
3. Rastrear la cadena de llamadas
4. Exportar el script
5. Reenvío con Burp

### 18.6 Skill de búsqueda de documentación

MCP prioritario:

- `context7`
- `fetch`

Flujo común:

1. `resolve_library_id`
2. `query_docs`
3. Si se necesita complementar el contenido de la página, usar `fetch`

---

## 19. Plantillas de prompt reutilizables al escribir un skill

A continuación se ofrecen algunas plantillas adecuadas para adaptar directamente a un skill.

### 19.1 Fragmento de plantilla de skill de ingeniería inversa Android

```text
Cuando el usuario solicite analizar un APK Android:
1. Si la tarea es una prueba de penetración de una App Android ya autorizada, no analices el APK estáticamente primero; confirma primero si la App objetivo ya está instalada en el dispositivo conectado.
2. Prepara primero la visibilidad de captura de tráfico con burp o charles, luego usa scrcpy_vision para abrir la App, y ejecuta clics, entradas y navegación reales del flujo de negocio.
3. Después de cada acción clave, verifica primero si ya aparecen paquetes HTTP/HTTPS o WebSocket en burp o charles, y combina con adb_mcp para revisar logs, anomalías de interfaz y estado en tiempo de ejecución.
4. Si el paquete ya es visible y reenviable, pasa directamente a pruebas de seguridad Web/API/WebSocket, y continúa avanzando en distintas funciones de negocio siguiendo el ciclo "acción en interfaz -> paquete de datos -> análisis de seguridad Web".
5. Solo cuando no se pueda capturar el paquete, el paquete esté cifrado, no se pueda obtener texto plano, el protocolo siga siendo opaco, no se pueda reenviar de forma estable, o la anomalía apunte claramente a un bloqueo en la lógica del cliente, usa jadx para leer AndroidManifest.xml, la Activity principal, los componentes exportados, y busca palabras clave como okhttp/retrofit/sign/token/encrypt.
6. Si la capa Java aún no es suficiente, usa frida_mcp para hacer hook en el límite Java o native y recuperar el texto plano; si se descubren indicios native (System.loadLibrary, JNI, archivo so) y Java más hook aún no resuelven, cambia a ida_pro_mcp para analizar el so extraído.
7. Si se necesita controlar el dispositivo, localizar por elemento de UI, observar la pantalla en tiempo real o cambiar a depuración WiFi, usa scrcpy_vision; si se necesita instalar la aplicación, grabar pantalla, logcat, transferencia básica de archivos, usa adb_mcp.
```

### 19.2 Fragmento de plantilla de skill de ingeniería inversa de JS Web

```text
Cuando el usuario solicite localizar la firma del frontend, funciones ofuscadas o la cadena de llamadas de la interfaz:
1. Prioriza usar js_reverse para enumerar scripts y usar search_in_sources para buscar palabras clave como sign/token/hash/encode/api path.
2. Si ya se conoce la URL de la solicitud, prioriza usar break_on_xhr o get_request_initiator para determinar el punto de origen.
3. Para funciones clave usa set_breakpoint_on_text, trace_function, get_paused_info, step y evaluate_script para obtener el contexto en tiempo de ejecución.
4. Si se necesita guardar el script completo para análisis sin conexión, usa save_script_source.
5. Si se necesita reproducir o reenviar la solicitud, combina con create_repeater_tab, send_http1_request, send_http2_request de burp.
6. Si se necesita interacción a nivel de página o capturas de pantalla, combina con chrome_devtools.
```

### 19.3 Fragmento de plantilla de skill de análisis de binarios Native

```text
Cuando el usuario solicite analizar un binario, so, muestra maliciosa o punto de parche:
1. Después de abrir IDA, invoca primero ida_pro_mcp.survey_binary para hacer un panorama general, no uses list_funcs de forma ciega directamente.
2. Prioriza reducir el alcance a partir de strings, imports, callgraph, constantes clave, APIs sensibles.
3. Para funciones sospechosas usa analyze_function / decompile / xref_query / trace_data_flow.
4. Si la legibilidad de la función es pobre, usa rename, set_type, declare_type, stack_frame, diff_before_after para recuperar la semántica paso a paso.
5. Si se necesita modificar la muestra, usa patch / patch_asm / put_int, y guarda el IDB cuando sea necesario.
```

---

## 20. Resumen de puntos comunes a tener en cuenta

### 20.1 Requisito de rutas absolutas

Los siguientes tipos de herramientas frecuentemente requieren rutas absolutas:

- `adb_mcp.take_screenshot`
- `adb_mcp.record_screen`
- `adb_mcp.pull_file` / `push_file`
- `scrcpy_vision.android_file_pull` / `android_file_push`
- `script_file_path`, `output_file` de `frida_mcp`
- `js_reverse.save_script_source`
- `chrome_devtools.take_screenshot`
- `chrome_devtools.take_memory_snapshot`
- `ida_pro_mcp.open_file`

### 20.2 Parámetros de tipo paginación

Parámetros comunes de paginación/fragmentación:

- `offset`
- `count`
- `limit`
- `pageIdx`
- `pageSize`
- `start_index`
- `length`

Al escribir un skill se recomienda especificar explícitamente:

- Tomar por defecto primero una muestra pequeña
- Si los resultados son demasiados, aumentar limit / count

### 20.3 Descubrir primero, profundizar después

Muchos MCP tienen "herramientas de fase de descubrimiento" evidentes; no profundices directamente desde el inicio:

- `ida_pro_mcp`: `survey_binary`
- `jadx`: `get_android_manifest` / `search_classes_by_keyword`
- `js_reverse`: `list_scripts` / `search_in_sources`
- `chrome_devtools`: `take_snapshot`
- `charles`: `query_live_capture_entries`

### 20.4 Conservación de evidencia

MCP adecuados para la conservación de evidencia:

- `adb_mcp.take_screenshot`
- `adb_mcp.record_screen`
- `scrcpy_vision.android_vision_snapshot`
- `chrome_devtools.take_screenshot`
- `js_reverse.take_screenshot`
- `charles.get_traffic_entry_detail`
- Historial de `burp` y Repeater

### 20.5 Combinaciones más comunes

- Android estático + dinámico: `jadx` + `frida_mcp`
- Android dinámico + tráfico: `adb_mcp` + `charles`
- Android dinámico + automatización de UI: `scrcpy_vision` + `frida_mcp`
- Android captura de tráfico + guía de página: `scrcpy_vision` + `charles`
- Automatización Web + ingeniería inversa JS: `chrome_devtools` + `js_reverse`
- Reenvío de seguridad Web: `js_reverse` + `burp`
- Native estático + dinámico: `ida_pro_mcp` + `frida_mcp`

---

## 21. Resumen

Si tu objetivo es "facilitar la escritura posterior de skills", lo más práctico no es escribir un skill independiente para cada MCP, sino dividir por dominio de tarea:

- Análisis estático de Android
- Análisis dinámico de Android y captura de tráfico
- Automatización Web
- Ingeniería inversa de JS Web
- Análisis de binarios Native
- Búsqueda de documentación
- Gestión de memoria y estado de tareas

De estos, los MCP alrededor de los cuales vale más la pena diseñar un skill de forma prioritaria son:

1. `jadx`
2. `ida_pro_mcp`
3. `js_reverse`
4. `chrome_devtools`
5. `frida_mcp`
6. `charles`
7. `adb_mcp`

Si más adelante lo necesitas, también puedo ayudarte con dos cosas más a partir de este documento:

1. Generar una versión adicional de "tabla de referencia rápida de MCP simplificada para skills"
2. Dividir directamente este documento en varios esqueletos de plantilla `SKILL.md`

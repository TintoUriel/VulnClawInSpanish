# Flujo de Trabajo Integrado 02: Ingeniería Inversa de API Cliente y Burp

Este archivo integrado combina el flujo de trabajo de ingeniería inversa del lado del cliente, el orden de ejecución MCP, las reglas de selección de herramientas, y las expectativas de evidencia necesarias para pasar de tráfico de cliente opaco a una repetición (replay) reproducible en Burp.

## Usa Este Archivo Cuando

- Burp no puede reproducir (replay) directamente la solicitud
- el cliente calcula `sign`, `token`, `nonce`, `timestamp`, cuerpo cifrado, o campos vinculados al dispositivo
- la secuencia de solicitudes es con estado (stateful) o está ligada a valores de runtime
- necesitas un flujo de trabajo confiable desde la captura de paquetes en runtime hasta la recuperación mediante ingeniería inversa impulsada por bloqueos y la repetición (replay)

## Objetivo Central

Recuperar la receta completa de producción de la solicitud:

- dónde se ensambla la solicitud
- dónde se aplica la criptografía o firma
- qué valores de runtime son obligatorios
- qué transiciones de estado deben ocurrir antes de la repetición (replay)

La primera prioridad no es la ingeniería inversa por sí misma. La primera prioridad es capturar la solicitud HTTP/HTTPS real o el mensaje WebSocket que emite el cliente, confirmar si ya es utilizable, y solo entonces hacer ingeniería inversa del bloqueo faltante.

## Regla Principal Para Pentest de App Android Autorizada

Cuando la tarea sea hacer pentest de una app Android autorizada, no comiences con `jadx`, `ida_pro_mcp`, o análisis de ingeniería inversa centrado en el APK.
En su lugar, comienza en este orden:

1. confirma que la app objetivo realmente esté instalada en el dispositivo Android conectado
2. prepara `burp` o `charles` antes de manejar la funcionalidad
3. usa `scrcpy_vision` para abrir la app y manejar funcionalidades reales de negocio
4. después de cada acción importante, inspecciona `burp` o `charles` en busca de solicitudes HTTP/HTTPS o mensajes WebSocket
5. si los paquetes ya son visibles y utilizables, pasa directamente a `web-playbook-index.md` y prueba la superficie del lado del servidor
6. repite el bucle de acción de UI -> captura de paquete -> análisis de seguridad Web para la siguiente funcionalidad de negocio
7. escala a `jadx`, `frida_mcp`, o `ida_pro_mcp` solo cuando los paquetes estén ausentes, cifrados, opacos, aún no sean reproducibles, o cuando las anomalías de runtime apunten claramente a un bloqueo del lado del cliente

Para esta ruta de pentest en Android, la ingeniería inversa es un paso de resolución de bloqueos, no el punto de entrada por defecto.

## Ruta de Lectura Recomendada

1. Lee `Goal` (Objetivo), `Stages` (Etapas), y la sección específica de la plataforma para Android, escritorio, o JS de navegador.
2. Lee `Priority` (Prioridad) y `Primary Chains` (Cadenas Principales) para elegir la cadena MCP más pequeña.
3. Si el objetivo es JS de navegador, continúa en `browser-js-signing-workflow.md`.
4. Si el objetivo es pruebas de URL externa en Android, continúa en `android-external-url-runtime-first-workflow.md`.
5. Si el objetivo es ingeniería inversa o recuperación de criptografía en Android, continúa en `android-signing-and-crypto-workflow.md`.
6. Si el progreso de runtime en Android depende del estado de UI de la app, continúa en `android-ui-driven-observation-and-packet-loop.md`.
7. Lee el contenido de `Rule` (Regla) y `reporting-and-evidence.md` antes de cambiar a Burp.
8. Después de que la repetición (replay) sea estable, pasa a `web-playbook-index.md` o `04-ai-and-mcp-security-integrated.md`.

## Lista de Verificación de Preparación para Repetición (Replay)

- puedes nombrar la ubicación del builder, firmador (signer), o serializador
- sabes qué cookies, headers, tokens, timestamps, o valores de dispositivo se requieren
- sabes si el orden de las solicitudes importa
- tienes una repetición (replay) funcionando fuera del cliente
- sabes qué campos son seguros de mutar durante las pruebas posteriores

## Reglas de Ramificación por Plataforma

### JS de Navegador

- decide la etapa a partir del estado de la ingeniería, no solo de palabras clave
- permanece en `locate` hasta que la solicitud, el sink, y la cadena de dependencias upstream sean reales
- entra en `recover` solo después de que el límite esté probado
- entra en `runtime` solo cuando el límite sea claro pero el navegador y la ejecución local diverjan
- entra en `validation` solo cuando el trabajo restante sea la prueba de checkpoint

Archivo de rama detallado: `references/browser-js-signing-workflow.md`
Referencias de etapa: `references/browser-locate-and-request-chain.md`, `references/browser-recover-and-shell-reduction.md`, `references/browser-runtime-fit-and-risk.md`, `references/browser-validation-and-handoff.md`
Plantilla de registro: `references/browser-request-chain-template.md`

### Android

- para pruebas de URL externa, comienza con la interacción en vivo con la app y la visibilidad de paquetes, no con la ingeniería inversa
- confirma primero que la app objetivo esté instalada en un dispositivo conectado y que realmente pueda lanzarse
- usa `scrcpy_vision` para navegar, inspeccionar capturas de pantalla, y decidir la siguiente acción
- verifica `burp` o `charles` en busca de solicitudes HTTP/HTTPS o mensajes WebSocket después de cada acción importante
- usa `adb_mcp` para revisar los logs después de acciones importantes
- una vez que los paquetes sean visibles y reproducibles, pasa directamente a `web-playbook-index.md` y mantén el bucle de acción de UI a paquete a análisis Web para la siguiente funcionalidad de negocio
- haz ingeniería inversa de Java solo cuando los paquetes estén ausentes, cifrados, sigan opacos, o de otro modo bloqueados
- escala a JNI o trabajo de `.so` solo cuando Java deje de exponer las entradas o salidas requeridas
- usa `frida_mcp` cuando la recuperación de texto plano basada en hooks sea más rápida que la reimplementación

Archivos de rama detallados: `references/android-external-url-runtime-first-workflow.md`, `references/android-signing-and-crypto-workflow.md`
Referencias de fase: `references/android-static-triage-and-callflow.md`, `references/android-dynamic-hooking-and-replay.md`, `references/android-ui-driven-observation-and-packet-loop.md`, `references/android-native-signature-analysis.md`
Plantilla de registro: `references/android-signature-reverse-template.md`

## Fuentes Incluidas

- references/client-reverse-workflow.md
- references/mcp-first-methodology.md
- references/tool-selection-map.md
- references/reporting-and-evidence.md

---

## Fuente: client-reverse-workflow.md

Ruta: references/client-reverse-workflow.md

# Flujo de Trabajo Complejo de Ingeniería Inversa de Cliente

## Objetivo

Recuperar la cadena real de producción de la solicitud para que la interfaz pueda reproducirse fuera del cliente.

## Etapas

1. clasificar el cliente
2. elegir la rama de plataforma más pequeña que pueda probar la cadena de solicitud
3. para pentests de apps Android, confirmar la presencia de la app en el dispositivo e intentar la captura de paquetes en runtime antes de cualquier paso de ingeniería inversa
4. confirmar dinámicamente el firmador (signer), serializador, y valores de estado solo cuando la prueba de paquetes en runtime ya no sea suficiente
5. recuperar estáticamente el bloqueo faltante solo después de que la visibilidad en runtime, el texto plano, o la repetición (replay) se estanquen
6. reconstruir la receta de la solicitud
7. repetir (replay) en Burp
8. pasar a pruebas de ataque Web o de IA solo después de que la repetición (replay) sea estable

## Android

- comienza confirmando que la app objetivo existe en el dispositivo conectado, luego usa `scrcpy_vision`, logs, y visibilidad de proxy para pruebas de URL externa
- pasa a `jadx` solo cuando los paquetes estén ausentes, cifrados, o bloqueados
- haz ingeniería inversa de Java antes que de nativo
- usa `frida_mcp` cuando la prueba mediante hooks en runtime o la recuperación de texto plano sea más rápida que una ingeniería inversa más profunda
- vuelca y analiza `.so` solo después de que Java haya dejado de responder al bloqueo
- pasa a `burp`, luego al análisis de seguridad Web una vez que la repetición (replay) sea estable

## Escritorio nativo

- localiza archivos con `everything_search`
- haz ingeniería inversa de código con `ida_pro_mcp`
- captura valores de runtime con `frida_mcp`
- pasa a `burp`

## JS de Navegador

- inspecciona solicitudes en vivo con `chrome_devtools`
- elige la etapa actual entre `locate`, `recover`, `runtime`, o `validation`
- traza los iniciadores y las funciones de firma con `js_reverse`
- repite (replay) con `burp`

## Firma y criptografía en Android

- entra en esta rama solo después de que las verificaciones de paquetes centradas en runtime prueben que la ingeniería inversa es necesaria, o cuando la tarea ya sea un problema explícito de ingeniería inversa de firma o criptografía en Android
- descompila y haz triage en `jadx`
- traza el flujo de la solicitud desde el manifest y los componentes de entrada
- localiza el builder de solicitud, interceptor, firmador (signer), cifrador, y el traspaso JNI
- confirma los valores finales en el cable (on-wire) con `frida_mcp` o `charles` solo después de que el triage estático acote el objetivo
- repite (replay) con `burp`

## URL externa en Android centrado en runtime

- maneja la app con `scrcpy_vision`
- inspecciona las capturas de pantalla en busca de anomalías visibles y cambios de estado
- revisa los logs con `adb_mcp`
- verifica si `burp` o `charles` ven tráfico
- solo entonces decide si es necesaria la ingeniería inversa de Java, los hooks de Frida, o el análisis del `.so` volcado

## Ramas Detalladas

- flujo por etapas de JS de navegador: `browser-js-signing-workflow.md`
- flujo centrado en runtime de URL externa en Android: `android-external-url-runtime-first-workflow.md`
- flujo de firma y criptografía en Android: `android-signing-and-crypto-workflow.md`

Para el trabajo por etapas de navegador, continúa en `references/browser-js-signing-workflow.md`.
Para pruebas de URL externa en Android, continúa en `references/android-external-url-runtime-first-workflow.md`.
Para la recuperación de bloqueos en Android o el trabajo explícito de ingeniería inversa de firma y criptografía, continúa en `references/android-signing-and-crypto-workflow.md`.


---

## Fuente: mcp-first-methodology.md

Ruta: references/mcp-first-methodology.md

# Metodología MCP-Primero

Este archivo es una ayuda de navegación. La metodología completa vive en `references/methodology/MCP.md`.

## Prioridad

1. Lee el `MCP.md` en bruto
2. Selecciona la cadena MCP mínima para el objetivo
3. Captura la solicitud HTTP/HTTPS real o el mensaje WebSocket antes de una ingeniería inversa más profunda
4. Restaura el ciclo de vida de la solicitud antes de la repetición (replay) en Burp

## Cadenas Principales

### Android

- `scrcpy_vision`
- `burp`
- `charles`
- `adb_mcp`
- `jadx` solo cuando los paquetes estén bloqueados
- `frida_mcp`
- `ida_pro_mcp`

### Escritorio nativo o empaquetado

- `everything_search`
- `ida_pro_mcp`
- `frida_mcp`
- `burp`

### Ingeniería inversa de JS de navegador

- `chrome_devtools`
- `js_reverse`
- `burp`


---

## Fuente: tool-selection-map.md

Ruta: references/tool-selection-map.md

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

## Capa de Soporte

- `everything_search`
- `context7`
- `fetch`
- `memory`
- `sequential_thinking`

## Secuencias por Plataforma

### Firma o anti-bot de JS de navegador

- prueba de límite y solicitud: `chrome_devtools` -> `js_reverse`
- divergencia navegador/local: `js_reverse`
- confirmación de repetición (replay): `burp`

### Firma o cifrado en Android

- verificación centrada en runtime de presencia de app y verificación de paquetes: `scrcpy_vision` -> `adb_mcp` -> `charles` / `burp`
- recuperación de Java cuando esté bloqueado: `jadx`
- dirección de estado de UI y siguientes acciones guiadas por captura de pantalla: `scrcpy_vision`
- estado del dispositivo y contexto de runtime: `adb_mcp`
- hooks acotados de Java o JNI: `frida_mcp`
- análisis de `.so` volcado cuando sea necesario: `ida_pro_mcp`
- validación en el cable u observación asistida por Charles: `charles`
- confirmación de repetición (replay): `burp`

## Regla

No comiences con ingeniería inversa cuando la solicitud HTTP/HTTPS o el mensaje WebSocket relevante ni siquiera se haya revisado en Burp o Charles.
Para pentests de apps Android, primero confirma que la app objetivo esté instalada en el dispositivo conectado antes de ramificar más el flujo de trabajo.
Para pruebas de URL externa en Android, no hagas ingeniería inversa primero cuando la captura de pantalla, los logs, y la visibilidad de paquetes puedan responder la pregunta.
No elijas referencias de navegador por palabras clave antes de conocer la etapa actual.


---

## Fuente: reporting-and-evidence.md

Ruta: references/reporting-and-evidence.md

# Reportes y Evidencia

Salida mínima:

- alcance y tipo de cliente
- cadena MCP elegida
- hallazgos estáticos
- prueba en runtime
- receta de solicitud recuperada
- solicitud de línea base lista para Burp
- hallazgo de seguridad y mitigación



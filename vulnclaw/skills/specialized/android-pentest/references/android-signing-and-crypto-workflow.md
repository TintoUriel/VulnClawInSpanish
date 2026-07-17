# Flujo de Trabajo de Firma y Criptografía en Android

Usa este archivo cuando la solicitud objetivo se produzca en una app Android y la tarea principal sea recuperar la lógica de firma (sign), token, cifrado, descifrado, JNI, o secuenciación de solicitudes para que la solicitud pueda explicarse o reproducirse (replay) fuera del APK.
Este no es el punto de entrada por defecto para un pentest general de app Android autorizada.

## Regla Central

No saltes directamente a Frida o a la ingeniería inversa de `.so`.

Si la tarea es un pentest general de app Android autorizada y aún no sabes si la ingeniería inversa es necesaria, no comiences aquí.
Primero confirma que la app esté instalada en el dispositivo conectado, prepara Burp o Charles, usa `scrcpy_vision` para manejar funcionalidades reales de negocio, y verifica después de cada acción importante si las solicitudes HTTP/HTTPS o los mensajes WebSocket ya son visibles y utilizables.
Comienza desde `references/android-authorized-app-pentest-sop.md` o `references/android-external-url-runtime-first-workflow.md`, y regresa aquí solo después de que la revisión de capturas de pantalla, logs, y verificaciones de visibilidad de paquetes demuestren que la ingeniería inversa es necesaria.

Comienza con triage estático en `jadx` y responde:

- qué pila de red está en uso
- dónde se construye la solicitud
- dónde se escriben los headers, el cuerpo, y los campos de firma
- si la ruta de firma o criptografía es visible en Java o se entrega a JNI

Usa el trabajo en runtime solo después de que la evidencia estática acote el objetivo.
Si el tráfico en vivo ya es visible y reproducible (replayable), prioriza primero las pruebas de capa de red y usa este archivo únicamente para resolver el bloqueo restante de firmador (signer), criptografía, o secuenciación.

## Contrato de Recepción (Intake)

Comienza desde este bloque:

```text
APK / paquete / funcionalidad objetivo:
Solicitud / campo / ruta de API objetivo:
Acción disparadora:
Síntoma actual:
Evidencia conocida:
Objetivo:
Restricciones:
```

Luego decide:

- si la tarea es triage estático, confirmación en runtime, análisis JNI, o prueba de repetición (replay)
- si la solicitud objetivo ya está capturada o todavía se infiere
- si la app usa lógica exclusivamente Java, lógica mixta Java/JNI, o lógica mayormente nativa

## Flujo de Trabajo Centrado en lo Estático

### Fase 1: Entrada y arquitectura

Lee:

- `AndroidManifest.xml`
- la clase de aplicación
- la activity de lanzamiento o componente objetivo
- la estructura de paquetes alrededor de `api`, `network`, `data`, `repository`, `service`, `retrofit`, `http`

Objetivo:

- localizar los componentes de entrada
- identificar el paquete de la app
- identificar la pila de red probable y la configuración de inyección de dependencias

Referencia detallada: `references/android-static-triage-and-callflow.md`

### Fase 2: Prueba de la cadena de solicitud y de flujo de llamadas

Traza:

```text
Activity / Fragment / Service
-> ViewModel / Presenter / UseCase
-> Repository / DataSource
-> ApiService / RequestBuilder / Interceptor
-> Signer / Encryptor / Serializer
```

Usa strings, anotaciones de Retrofit, clases interceptoras, builders de solicitud, y constantes como anclas.

Demuestra:

- el método y ruta de la solicitud
- los escritores de header y cuerpo
- el ordenamiento de la solicitud o las dependencias de preflight
- la clase o método exacto donde se juntan las entradas de firma

### Fase 3: Localizador de firma y criptografía

Busca:

- `sign`, `token`, `encrypt`, `decrypt`, `cipher`, `aes`, `rsa`, `hmac`, `md5`, `sha`
- `Interceptor`, `intercept`, `addInterceptor`
- `native`, `System.loadLibrary`, `System.load`
- URLs, nombres de header, nombres de claves, e identificadores de dispositivo codificados

Clasifica la ruta de firma actual:

- exclusivamente Java
- wrapper de Java alrededor de nativo
- nativo primero
- todavía desconocido

### Fase 4: Triage del traspaso JNI

Si Java llama a código nativo, demuestra:

- qué método Java declara `native`
- qué biblioteca se carga
- si la función nativa se exporta estáticamente o se registra dinámicamente
- qué parámetros se pasan al límite nativo
- qué valor de retorno regresa a la cadena de solicitud

No comiences una ingeniería inversa nativa profunda hasta que el límite del lado de Java ya sea concreto.

Referencia detallada: `references/android-native-signature-analysis.md`

### Fase 5: Prueba del disparador guiado por UI

Si la solicitud depende de qué pantalla muestra la app o qué gesto envía los datos, usa `scrcpy_vision` después de que el triage estático ya haya acotado el objetivo.

Ejecuta este bucle:

1. navega o toca hacia el disparador sospechoso
2. captura una captura de pantalla o el árbol de UI
3. analiza qué pantalla es visible ahora, qué controles importan, y qué siguiente acción es más probable que exponga la solicitud objetivo
4. realiza la siguiente entrada, toque, deslizamiento, o acción de retroceso
5. observa el paquete o la transición de estado que demuestre la ruta de la solicitud

No trates el razonamiento sobre capturas de pantalla como un reemplazo de la prueba estática. Es una capa de dirección en runtime que te ayuda a alcanzar el disparador correcto y conectar el estado visible de la UI con la cadena de solicitud.

Referencia detallada: `references/android-ui-driven-observation-and-packet-loop.md`

## Reglas de Escalamiento Dinámico

Escala solo cuando la prueba estática ya no sea suficiente.

### Prefiere estos puntos de hook en orden

1. construcción final del objeto de solicitud
2. métodos de interceptor
3. punto de entrada de ejecución de la solicitud
4. generador de firma (sign) o token
5. límite nativo

Para cada hook, captura:

- clase y método
- URL
- headers
- cuerpo o payload serializado
- tupla de entrada de firma
- salida de firma o resultado cifrado

### SSL pinning y captura de paquetes

Trata el bypass de SSL pinning como un paso de apoyo, no como el primer movimiento.
Trata a Burp o Charles como la línea base de runtime que permanece activa para que el comportamiento del firmador recuperado pueda compararse con tráfico real.

Úsalos cuando:

- los hooks de Java todavía no exponen los valores finales de la solicitud
- el transporte personalizado oculta campos hasta después de la configuración TLS
- necesites verificar que la repetición (replay) coincide con el tráfico en runtime

Referencia detallada: `references/android-dynamic-hooking-and-replay.md`

## Decisiones Nativas y de Firma

Escala más allá de la prueba del límite Java y JNI solo cuando el usuario necesite:

- reproducción fuera de línea (offline)
- recuperación de algoritmo más profunda
- ejecución basada en unidbg
- parcheo de `.so` o análisis de flujo de control nativo

Antes de eso, responde estas preguntas:

- si la firma se genera en Java o en código nativo
- qué entradas exactas alimentan la firma
- qué entradas son constantes versus valores de runtime
- si la repetición (replay) puede llamar a la app o enganchar (hook) el límite en lugar de reimplementar el algoritmo

## Orden de Herramientas de Android

1. `burp` o `charles`
2. `jadx`
3. `adb_mcp`
4. `frida_mcp`
5. `ida_pro_mcp` cuando se requiera análisis de `.so` volcado (dump)

El orden puede comprimirse, pero la lógica se mantiene igual: visibilidad de red primero, prueba estática segundo, recuperación en runtime tercero, análisis nativo más profundo al final.

## Criterios de Salida de Repetición (Replay)

No pases al trabajo de mutación en Burp hasta que puedas explicar:

- dónde se construye la solicitud
- dónde se aplica la firma o el cifrado
- qué entradas de runtime son obligatorias
- si la identidad del dispositivo, timestamp, nonce, token, o secuencia deben conservarse
- si la repetición (replay) puede llamar a la app, reutilizar un punto de hook, o debe reimplementar la lógica

Si Burp o Charles ya tienen una línea base de repetición estable y el bloqueo restante es acotado, resuelve solo ese bloqueo en lugar de expandir el alcance de la ingeniería inversa.

## Contrato de Salida

Entrega:

- resumen de la arquitectura de la app
- mapa de flujo de llamadas desde el componente de entrada hasta la ejecución de la solicitud
- ubicación del builder de solicitud y del firmador
- conclusión de Java versus JNI
- punto de hook en runtime y valores observados cuando se necesitó trabajo en runtime
- receta de repetición lista para Burp o el bloqueo exacto restante

Plantilla de registro: `references/android-signature-reverse-template.md`

## Orden de Lectura Recomendado Dentro de Esta Rama

1. `android-static-triage-and-callflow.md`
2. `android-dynamic-hooking-and-replay.md` solo cuando la prueba estática no sea suficiente
3. `android-native-signature-analysis.md` cuando JNI o `.so` se conviertan en parte de la ruta de firma real
4. `android-signature-reverse-template.md` cuando necesites un registro persistente o un traspaso de repetición

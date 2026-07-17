# Flujo de Trabajo de Firma JS en Navegador

Usa este archivo cuando la solicitud objetivo se produzca en el navegador y el bloqueo actual sea la generación de firma (sign), el flujo de token, saltos de cookie, indirección de worker o wasm, lógica anti-bot, o divergencia entre navegador y local.

## Misión

Mantén la ingeniería inversa de JS en navegador sobre un eje por etapas:

`recepción (intake) -> evidencia -> localizar -> recuperar -> runtime -> validación -> repetición (replay)`

No elijas el siguiente paso solo a partir de palabras clave. Elígelo a partir del estado de la ingeniería.

## Contrato de Recepción (Intake)

Comienza desde este bloque:

```text
URL o página objetivo:
Solicitud / campo / cookie / mensaje objetivo:
Acción disparadora:
Síntoma actual:
Evidencia conocida:
Objetivo:
Restricciones:
```

Luego responde:

- si la solicitud objetivo es real o todavía es una suposición
- si el límite de escritura está probado, parcial, o desconocido
- si el bloqueo es reducción de shell, divergencia en runtime, o prueba de checkpoint
- qué artefacto debe actualizarse a continuación

## Regla de Evidencia

No entres en el trabajo por etapas si la cadena de solicitud real todavía es una suposición. Primero captura una muestra real y demuestra:

- la solicitud o mensaje objetivo
- la acción disparadora
- la primera solicitud o respuesta upstream dependiente cuando hay estado involucrado
- si la muestra actual es estado normal, estado de riesgo, o todavía mixto

Mantén un registro persistente de la cadena de solicitud. Como mínimo, conserva:

- muestra de solicitud
- sink o límite de escritura
- saltos upstream
- notas de runtime
- prerrequisitos de repetición (replay)

## Selección de Etapa

### `locate`

Entra cuando la solicitud, el sink, el límite de escritura, o la cadena de dependencias upstream todavía no estén probados.

Responsabilízate de estas preguntas:

- dónde se escribe finalmente el valor objetivo
- qué acción, callback, o respuesta dispara la escritura
- qué estado upstream alimenta la escritura
- dónde se bifurcan las rutas normal y de riesgo

Modelo de límite por defecto:

```text
writer <- builder <- entry <- source
```

Detente cuando el siguiente bloqueo ya no sea el descubrimiento de la solicitud.

Referencia detallada: `references/browser-locate-and-request-chain.md`

### `recover`

Entra solo después de que el límite sea lo suficientemente real y el siguiente bloqueo sea la opacidad del shell.

Bloqueos típicos:

- bootstrap de webpack
- puente de worker
- cargador de wasm
- aplanamiento de dispatcher
- tablas de strings
- indirección de helpers
- shells estilo JSVMP

Reduce solo la capa que bloquea el progreso. Detente tan pronto tengas un contrato de lógica legible o invocable.

Referencia detallada: `references/browser-recover-and-shell-reduction.md`

### `runtime`

Entra cuando el límite y el shell ya sean claros pero la ejecución en el navegador y la ejecución local diverjan.

Clasifica la primera divergencia significativa antes de parchear:

- objeto faltante
- estado faltante
- anti-debugging
- fuente inestable
- rama de riesgo

Usa una tabla de comparación de primera divergencia y mantén el conjunto de dependencias de runtime al mínimo.

Referencia detallada: `references/browser-runtime-fit-and-risk.md`

### `validation`

Entra cuando el trabajo restante sea la prueba de equivalencia.

Compara checkpoints, no solo la salida final:

- cuerpo de la solicitud antes de la firma
- tupla de entrada de firma
- salida de firma
- payload cifrado
- conjunto de headers
- mutación de cookie o storage

El resultado debe indicar qué está probado, qué sigue abierto, y qué evidencia respalda cada afirmación.

Referencia detallada: `references/browser-validation-and-handoff.md`

## Enrutamiento de Temas Dentro de la Rama de Navegador

Después de seleccionar la etapa, aplica el lente de tema correspondiente:

| Bloqueo actual | Usar dentro de la etapa |
| --- | --- |
| `sign`, `token`, headers dinámicos, campos cifrados | localización de entrada criptográfica y observación de límites |
| `worker`, `wasm`, `webpack/runtime`, callbacks de cargador | puente y reducción de shell |
| `hasDebug`, `debugger` infinito, cambios de rama | anti-debug y diagnóstico de runtime |
| saltos de `cookie`, WebSocket, protobuf, SSE, ack o renovación | expansión de protocolo y cadena de estado |
| `basearr`, discrepancia navegador/local, estado de navegador faltante | ajuste de entorno mínimo |

## Orden de Herramientas de Navegador

1. `chrome_devtools` para capturar la solicitud real y el iniciador
2. `js_reverse` para trazar el límite, shell, runtime, o checkpoints
3. `burp` solo después de que una ruta de repetición (replay) sea estable

## Disciplina de Traspaso

Cada vez que cambie la etapa, emite una tarjeta de traspaso compacta:

```text
--- Traspaso de Etapa ---
Desde: {etapa anterior}
Hacia: {siguiente etapa}
Probado: {solicitud, límite, cadena upstream, hechos de runtime o recuperación}
Abierto: {preguntas que la siguiente etapa debe responder}
Invalidado: {supuestos obsoletos o "ninguno"}
```

No lleves suposiciones adelante como si fueran hechos.

## Criterios de Salida de Repetición (Replay)

No pases al fuzzing en Burp hasta que puedas explicar:

- dónde se escribe el campo objetivo
- qué entradas son constantes estables
- qué entradas provienen de cookies, storage, respuestas upstream, o del ciclo de vida del navegador
- si el orden de la solicitud o el estado de navegación importan
- qué campos son seguros de mutar

## Contrato de Salida

Entrega:

- la etapa actual y por qué es la etapa correcta
- prueba de la cadena de solicitud
- el sink o límite de escritura
- las conclusiones de shell o runtime recuperadas cuando aplique
- una solicitud de línea base lista para Burp o una declaración precisa del bloqueo restante

Plantilla de registro: `references/browser-request-chain-template.md`

## Orden de Lectura Recomendado Dentro de Esta Rama

1. `browser-locate-and-request-chain.md` cuando el límite todavía no sea real
2. `browser-recover-and-shell-reduction.md` cuando la opacidad del shell sea el bloqueo
3. `browser-runtime-fit-and-risk.md` cuando la ejecución navegador/local diverja
4. `browser-validation-and-handoff.md` cuando el trabajo restante sea prueba o traspaso de etapa
5. `browser-request-chain-template.md` cuando necesites un registro persistente o un artefacto de traspaso

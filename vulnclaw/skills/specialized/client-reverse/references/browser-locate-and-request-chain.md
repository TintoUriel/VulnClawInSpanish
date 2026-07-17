# Localización y Cadena de Solicitud en Navegador

Usa este archivo cuando la solicitud objetivo del lado del navegador, el sink, el límite de escritura, o la cadena de estado upstream todavía no sean lo suficientemente concretos para la reducción de shell o el trabajo en runtime.

## Responsabilidades

- probar la solicitud objetivo real a partir de una muestra en vivo
- probar el sink o límite de escritura
- probar la acción o callback disparador
- recorrer la cadena de dependencias upstream
- separar las cadenas de estado normal y estado de riesgo

## Modelo de Límite

Usa este modelo y mantén cada capa distinta:

```text
writer <- builder <- entry <- source
```

- `writer`: escritura final en el cuerpo, header, query, cookie, storage, o envoltura de mensaje
- `builder`: capa de transformación, firma, cifrado, serialización, o empaquetado
- `entry`: acción de UI, callback, evento, o respuesta que inicia la cadena
- `source`: respuesta upstream, storage, cookie, estado del navegador, tiempo, aleatoriedad, o entrada del usuario

## Orden por Defecto

1. captura una muestra real de la solicitud objetivo
2. observa el sink primero
3. recorre hacia atrás a través de `writer <- builder <- entry <- source`
4. expande upstream cuando la fuente actual dependa de solicitudes o estado previos
5. divide las cadenas de estado normal y de riesgo si ambas aparecen

## Puntos Fuertes de Primera Observación

| Tipo de sink | Primer punto a probar |
| --- | --- |
| campo del cuerpo de la solicitud | punto final de serialización o escritura de envío |
| campo de header | construcción de la solicitud o llamada de configuración de header |
| cookie escrita por JS | setter de cookie |
| dependencia de cookie impulsada por respuesta | paquete de respuesta y primera solicitud dependiente |
| frame de WebSocket | envoltura final antes de `send` |
| respuesta de worker | contrato de puente `postMessage` |

## Estándar de Finalización

Detén la localización cuando:

- la muestra de la solicitud sea real
- el sink sea real
- `writer`, `builder`, `entry`, y `source` sean lo suficientemente concretos para el siguiente paso
- el siguiente bloqueo sea la opacidad del shell, la divergencia en runtime, o la prueba de checkpoint en lugar del descubrimiento de la solicitud

## No Hacer

- deofuscación amplia antes de que el límite sea real
- parcheo del entorno mientras el sink todavía es una suposición
- confiar en coincidencias de palabras clave como prueba

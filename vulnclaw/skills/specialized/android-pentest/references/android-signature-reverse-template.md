# Android Signature Reverse Template

Use this template for Android sign, token, encrypt, decrypt, JNI, interceptor, and replay tasks.

## Template

```markdown
# Registro de Ingeniería Inversa de Firma Android

## Información básica

- APK / nombre de paquete：
- Función objetivo：
- Solicitud objetivo：
- Campo objetivo：
- Fase actual：static / dynamic / native / replay
- Estado actual：🟡 En curso / ✅ Cerrado / ⛔ Bloqueado
- Objetivo：
- Restricciones：

## Panorama estático

| Elemento | Contenido |
| --- | --- |
| Punto de entrada del Manifest |  |
| Application |  |
| Activity principal / componente objetivo |  |
| Estructura principal de paquetes |  |
| Framework de red |  |
| Framework de DI |  |
| Conclusión actual |  |

## Cadena de llamadas de la solicitud

```text
Activity / Fragment / Service
-> ViewModel / Presenter / UseCase
-> Repository / DataSource
-> ApiService / RequestBuilder / Interceptor
-> Signer / Encryptor / Serializer
```

- Cadena de llamadas real：
- Method / Path de la solicitud：
- Punto de escritura de Header：
- Punto de escritura de Body：
- Punto de confluencia de entradas de Sign：
- Secuencia / dependencias previas：

## Localización de Sign / Crypto

| Elemento | Contenido |
| --- | --- |
| Clase / método de Sign |  |
| Clase / método de Encrypt |  |
| Constantes clave |  |
| Headers clave |  |
| Valores clave de Token / Device |  |
| Java-only / Java+JNI / Native-first |  |

## Verificación dinámica

| Punto de Hook | Motivo | Contenido capturado | Resultado |
| --- | --- | --- | --- |
| Hook1 |  |  |  |

- URL：
- Headers：
- Body：
- Entrada de Sign：
- Salida de Sign：
- Verificación por proxy：

## Análisis JNI / SO

| Elemento | Contenido |
| --- | --- |
| Punto de entrada native de Java |  |
| Nombre del SO |  |
| Tipo de JNI | static / dynamic |
| Parámetros de entrada |  |
| Rol de salida | sign final / token intermedio / otro |
| Requiere RE más profunda |  |

## Línea base de reenvío en Burp

- Method：
- Path：
- Query：
- Headers：
- Body：
- Campos que deben conservarse：
- Campos mutables：
- Estado previo requerido：
- Requiere asistencia de dispositivo / Hook / App：

## Conclusión

- Grado de cierre actual：
- Bloqueos restantes：
- Sugerencia de siguiente paso：
```

## Minimum Required Fields

Even in a compact record, keep:

- APK or package
- target request
- real call-flow summary
- network stack
- sign or crypto location
- Java versus JNI conclusion
- one runtime hook or explicit reason why runtime is not needed
- Burp replay baseline or explicit blocker

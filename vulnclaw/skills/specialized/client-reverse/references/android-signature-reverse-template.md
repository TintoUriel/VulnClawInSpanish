# Plantilla de Ingeniería Inversa de Firmas Android

Usa esta plantilla para tareas de firma (sign), token, cifrado, descifrado, JNI, interceptor, y repetición (replay) en Android.

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

## Campos Mínimos Requeridos

Incluso en un registro compacto, conserva:

- APK o paquete
- solicitud objetivo
- resumen real de la cadena de llamadas
- pila de red
- ubicación de firma (sign) o cifrado
- conclusión de Java versus JNI
- un hook en runtime o una razón explícita de por qué el runtime no es necesario
- línea base de reenvío en Burp o bloqueo explícito

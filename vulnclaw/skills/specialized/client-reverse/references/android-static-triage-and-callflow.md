# Triage Estático y Flujo de Llamadas en Android

Usa este archivo primero para tareas de solicitud, firma, y criptografía en Android después de que el trabajo de pentest de Android centrado en runtime haya demostrado que las pruebas de capa de red por sí solas no son suficientes.
No es el punto de entrada por defecto para un pentest general de app Android autorizada.

## Responsabilidades

- lectura del manifest y de los componentes de entrada
- relevamiento de paquetes y arquitectura
- identificación de la pila de red
- trazado del flujo de llamadas desde la UI o componente hasta la ejecución de la solicitud
- localización de la ruta de firma y de cifrado en Java

## Orden Estático

1. lee `AndroidManifest.xml`
2. identifica la clase de aplicación y los componentes de entrada
3. encuentra las áreas de paquetes alrededor de `api`, `network`, `data`, `repository`, `service`, `retrofit`, `http`
4. identifica el framework de red
5. traza la cadena de solicitud hasta el builder, interceptor, firmador (signer), cifrador, o serializador

## Flujo de Llamadas Común

```text
Activity / Fragment / Service
-> ViewModel / Presenter / UseCase
-> Repository / DataSource
-> ApiService / RequestBuilder / Interceptor
-> Signer / Encryptor / Serializer
```

## Anclas Fuertes

- anotaciones de Retrofit
- `Request.Builder`, `HttpUrl`, clases interceptoras
- URLs, headers, y nombres de token codificados
- `sign`, `token`, `encrypt`, `decrypt`, `cipher`, `sha`, `hmac`, `md5`
- `native`, `System.loadLibrary`, `System.load`

## Estándar de Finalización

Detén el triage estático cuando puedas indicar:

- la pila de red
- el método y ruta de la solicitud
- dónde se escriben los headers y el cuerpo
- dónde convergen las entradas de firma
- si la ruta es exclusivamente Java, mixta Java/JNI, o mayormente nativa

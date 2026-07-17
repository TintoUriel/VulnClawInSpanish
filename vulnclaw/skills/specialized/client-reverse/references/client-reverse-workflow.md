# Flujo de Trabajo Complejo de Ingeniería Inversa de Cliente

## Objetivo

Recuperar la cadena real de producción de la solicitud para que la interfaz pueda reproducirse fuera del cliente.

## Etapas

1. clasificar el cliente
2. elegir la rama de plataforma más pequeña que pueda probar la cadena de solicitud
3. encontrar estáticamente el código de solicitud y criptografía
4. confirmar dinámicamente el firmador (signer), serializador, y valores de estado solo cuando la prueba estática ya no sea suficiente
5. reconstruir la receta de la solicitud
6. repetir (replay) en Burp
7. pasar a pruebas de ataque Web o de IA solo después de que la repetición (replay) sea estable

## Android

- comienza en `jadx`
- termina primero el triage de manifest, paquete, pila de red, builder de solicitud, firmador (signer), y JNI
- usa `scrcpy_vision` para dirigir rutas de runtime dependientes de la UI cuando el siguiente paquete dependa de lo que sea visible en pantalla
- verifica el comportamiento en el cable (on-wire) con `adb_mcp` y `charles`
- engancha (hook) el firmador o builder con `frida_mcp` solo después de que el objetivo estático sea lo suficientemente acotado
- pasa a `burp`

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

## Ramas Detalladas

- flujo por etapas de JS de navegador: `browser-js-signing-workflow.md`
- flujo de firma y criptografía en Android: `android-signing-and-crypto-workflow.md`
- flujo de disparador de paquete guiado por UI en Android: `android-ui-driven-observation-and-packet-loop.md`

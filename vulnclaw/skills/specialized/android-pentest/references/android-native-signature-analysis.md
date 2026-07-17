# Análisis de Firmas Nativas en Android

Usa este archivo cuando la lógica de firma (sign) o criptografía de Android cruce de Java a JNI o `.so`.
Entra en esta rama únicamente después de que las verificaciones de paquetes en runtime, la triage de Java, o los hooks demuestren que el análisis nativo realmente es necesario.

## Responsabilidades

- prueba del límite Java-a-nativo
- identificación del SO
- clasificación del estilo JNI
- evaluación de la entrada y salida de firma nativa
- decisión sobre si un análisis nativo más profundo está justificado

## Primera Pasada

Demuestra:

- qué método Java declara `native`
- qué llamada `System.loadLibrary` o `System.load` carga la biblioteca objetivo
- si el JNI es de exportación estática o de registro dinámico
- qué parámetros cruzan el límite
- si el valor de retorno es la firma final o un token intermedio

## No Escalar Todavía Cuando

- Java todavía expone los valores de solicitud necesarios
- la repetición (replay) puede reutilizar la app o el punto de hook
- el usuario no necesita ejecución fuera de línea (offline)

## Escalar Más Solo Cuando

- se requiere generación fuera de línea
- se requiere una recuperación de algoritmo más profunda
- se necesita explícitamente unidbg o ejecución a nivel de SO

## Salida

- punto de entrada Java
- nombre del SO
- estilo JNI
- tupla de entrada
- rol de la salida
- siguiente paso recomendado

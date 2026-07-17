# Validación y Traspaso en Navegador

Usa este archivo cuando el trabajo restante del lado del navegador sea la prueba de checkpoint, la prueba de equivalencia, o el traspaso de etapa.

## Checkpoints a Comparar

No compares solo la salida final. Compara:

- payload previo a la firma (pre-sign)
- tupla de entrada de firma
- salida de firma
- payload cifrado
- cuerpo final de la solicitud
- headers finales
- mutación de cookie o storage cuando afecte solicitudes posteriores

## Reglas de Prueba

Cada checkpoint debe indicar:

- muestra de entrada fija
- valor del lado del navegador
- valor del lado local o recuperado
- si el checkpoint coincide
- qué evidencia respalda la comparación
- qué brecha permanece si no coincide

## Tarjeta de Traspaso

Cuando la etapa cambie, emite:

```text
--- Traspaso de Etapa ---
Desde: {etapa anterior}
Hacia: {siguiente etapa}
Probado: {solicitud, límite, cadena upstream, hechos de recuperación o runtime}
Abierto: {preguntas para la siguiente etapa}
Invalidado: {supuestos obsoletos o "ninguno"}
```

## Estándar de Finalización

La validación está completa solo cuando el siguiente operador puede ver:

- qué es equivalente
- qué no es equivalente
- qué evidencia respalda cada afirmación
- qué permanece abierto

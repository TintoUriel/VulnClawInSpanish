# Reportes y Evidencia

Usa este archivo para normalizar la evidencia final y el traspaso de repetición (replay) después del trabajo en navegador, Android, cliente de escritorio, Web, o IA/MCP.

## Salida Mínima

- alcance y tipo de cliente
- cadena MCP elegida
- hallazgos estáticos
- prueba en runtime
- receta de solicitud recuperada
- solicitud de línea base lista para Burp
- hallazgo de seguridad y mitigación

## Objetivos Controlados por el Cliente

Para tareas de generación de solicitudes en navegador o Android, siempre incluye:

- solicitud objetivo y campo objetivo
- resumen de la cadena de solicitud
- writer o sink probado
- dependencia upstream o declaración explícita de que no existe ninguna
- valores de runtime que deben conservarse
- campos seguros para repetir (replay) versus campos seguros para mutar

## Plantillas Recomendadas

### JS de Navegador

- flujo de trabajo: `references/browser-js-signing-workflow.md`
- registro persistente: `references/browser-request-chain-template.md`

### Android

- flujo de trabajo: `references/android-signing-and-crypto-workflow.md`
- registro persistente: `references/android-signature-reverse-template.md`

## Lista de Verificación Final de Traspaso

- se conserva una muestra real de la solicitud
- los prerrequisitos de repetición (replay) son explícitos
- los bloqueos están separados de los hechos probados
- el siguiente operador puede reproducir la solicitud de línea base

# Browser Request Chain Template

Use this template for browser-side sign, token, anti-bot, worker, wasm, cookie-hop, and replay tasks.

## Template

```markdown
# Registro de Cadena de Solicitudes del Navegador

## Información básica

- Página objetivo：
- Solicitud objetivo：
- Campo objetivo：
- Acción disparadora：
- Fase actual：locate / recover / runtime / validation
- Estado actual：🟡 En curso / ✅ Cerrado / ⛔ Bloqueado
- Objetivo：
- Restricciones：

## Muestras y fenómenos

- Muestra en estado normal：
- Muestra en estado de control de riesgo：
- Fenómeno en el navegador：
- Fenómeno local：
- Diferencia actual：

## Tabla principal de la cadena de solicitudes

| Elemento | Contenido |
| --- | --- |
| writer |  |
| builder |  |
| entry |  |
| source |  |
| Dependencias upstream |  |
| Portador de estado |  |
| Punto de bifurcación de control de riesgo |  |
| Conclusión actual |  |

## Evidencia clave

| Tipo de evidencia | Ubicación/punto | Contenido | Conclusión |
| --- | --- | --- | --- |
| Muestra de solicitud |  |  |  |
| Pila de llamadas |  |  |  |
| Breakpoint/Hook |  |  |  |
| Valor intermedio |  |  |  |
| Cookie/Storage |  |  |  |

## Complementos por fase

### Complemento de Locate

- Sink：
- Punto de escritura real：
- Solicitud upstream：
- Distinción entre estado normal / estado de control de riesgo：

### Complemento de Recover

- Tipo de capa de ofuscación：
- Nivel de recuperación actual：A / B / C
- Contrato ya recuperado：
- Brechas aún sin recuperar：

### Complemento de Runtime

- Objeto faltante：
- Estado faltante：
- Fuente fija：
- Primer punto de divergencia：
- Control de riesgo / anti-debug：

### Complemento de Validation

| Punto de verificación | Lado del navegador | Lado local/recuperado | Resultado | Evidencia | Brecha |
| --- | --- | --- | --- | --- | --- |
| Punto de verificación1 |  |  |  |  |  |

## Línea base de reenvío en Burp

- Method：
- Path：
- Query：
- Headers：
- Body：
- Campos que deben conservarse：
- Campos mutables：
- Estado previo requerido：

## Stage Handoff

--- Stage Handoff ---
From:
To:
Proven:
Open:
Invalidated:

## Siguiente paso

- Próxima acción：
- Resultado esperado：
- Punto de bloqueo：
```

## Minimum Required Fields

Even in a compact record, keep:

- target page and target request
- current stage
- `writer / builder / entry / source`
- one real request sample
- one concrete evidence row
- Burp replay baseline or explicit blocker

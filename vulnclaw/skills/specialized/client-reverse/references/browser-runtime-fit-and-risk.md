# Ajuste de Runtime y Riesgo en Navegador

Usa este archivo cuando el límite y el shell del navegador ya sean claros pero la ejecución en el navegador y la ejecución local o controlada diverjan.

## Diagnosticar Antes de Parchear

Clasifica la primera divergencia significativa como una o más de:

- objeto faltante
- estado faltante
- anti-debugging
- fuente inestable
- rama de riesgo

## Tabla de Primera Divergencia

Siempre compara el estado normal del navegador y la ejecución local usando una tabla de checkpoint concreta antes de agregar parches.

Filas mínimas de comparación:

- parámetros de entrada
- estado de cookie y storage
- tiempo fijo y aleatoriedad
- primer valor intermedio estable
- primer valor intermedio anormal
- rama final o respuesta

## Refinamiento de Riesgo y Anti-Debug

Cuando el debugging cambie el comportamiento o se sospeche una rama de riesgo, responde:

- dónde comienza la bifurcación
- si el problema es fricción de debug o una rama de riesgo real impulsada por el consumidor
- qué estado faltante exacto o superficie de fingerprint dispara la división

Mantén el manejo anti-debug al mínimo. Elimina solo el obstáculo más pequeño necesario para mantener la observación en marcha.

## Reglas de Ajuste de Entorno

- mantén separados los `objetos requeridos` y el `estado requerido`
- registra por qué cada dependencia es necesaria
- fija el tiempo, la aleatoriedad, y las fuentes de semilla antes de continuar la comparación
- no afirmes que es cómputo puro mientras la respuesta upstream, el estado `HttpOnly`, el flujo de challenge, o el estado del ciclo de vida del navegador sigan abiertos

## Estándar de Finalización

Detén el runtime cuando:

- la clase de divergencia sea explícita
- se conozca el primer checkpoint divergente
- el objeto faltante y el estado faltante no estén mezclados
- la siguiente acción sea claramente parchear, restaurar estado, o validar

# Recuperación y Reducción de Shell en Navegador

Usa este archivo únicamente después de que el límite de la solicitud en el navegador ya sea real y el siguiente bloqueo sea la opacidad del shell.

## Responsabilidades

- elegir la capa más pequeña a abrir
- decidir si la tarea necesita explicación semántica, extracción de operador clave, o una reconstrucción mínima
- preservar la reutilización de caja negra cuando la deofuscación más profunda sea innecesaria

## Selección de la Primera Capa

| Síntoma | Primera capa a abrir |
| --- | --- |
| ruta invocable todavía oculta | contenedor externo |
| flujo grande de dispatcher o VM | capa de dispatcher |
| parámetros visibles pero portador de estado opaco | portador de estado |
| la lógica aparece después de un puente `worker` o `wasm` | capa de puente |
| punto de escritura conocido pero algoritmo opaco | operador central |

## Niveles de Recuperación

### Nivel A

Recupera solo el operador o helper crítico necesario para explicar el campo objetivo.

### Nivel B

Recupera el flujo del dispatcher más los portadores de estado críticos cuando el significado del operador depende del flujo de estado.

### Nivel C

Construye el fragmento o intérprete verificable más pequeño solo cuando los niveles A y B no puedan sostener la siguiente etapa.

## Prefiere la Reutilización de Caja Negra Cuando

- los límites de entrada y salida ya se conocen
- se encuentra el módulo objetivo o el punto de entrada del puente
- el bloqueo es lógica de contenedor, no lógica de negocio

## Escala Más Profundo Cuando

- la repetición (replay) es inestable debido a estado compartido oculto
- el contrato del puente en sí es opaco
- el módulo contiene otra VM o shell de protocolo que todavía bloquea el progreso

## Estándar de Finalización

Detén la recuperación cuando la profundidad de reducción actual ya sea suficiente para el ajuste en runtime o la validación.

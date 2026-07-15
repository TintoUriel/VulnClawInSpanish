# Seguridad de Aplicaciones de IA - Fase de Despliegue

> Fuente: Comunidad AISS NSFOCUS de Seguridad de Grandes Modelos | Extraído de ai-app-security.md
> Fase: Fase de despliegue (GAARM.0037-0038, 0049 Gestión de API / Envenenamiento del código fuente / Robo)

## Fase de Despliegue

### Gestión Inadecuada de la API de Aplicaciones LLM

> Número de riesgo: GAARM.0049
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

La gestión inadecuada de la API de aplicaciones LLM se refiere a que, en el entorno del marco de integración de LLM, existen componentes de API internos y externos con operaciones sensibles, como Tools, Agents, Chains, etc., que no cuentan con una gestión y configuración correctas del entorno junto con el entorno de LLM. Dado que los grandes modelos de lenguaje suelen necesitar interactuar con diversas API para ejecutar tareas, si estas API no se gestionan adecuadamente —por ejemplo, si no se establecen los permisos de acceso correctos o no se implementan controles de seguridad suficientes—, los atacantes pueden aprovechar estas vulnerabilidades para obtener información sensible o ejecutar acciones maliciosas, logrando ataques de acceso no autorizado, explotación de ejecución de código, etc.

**Casos de ataque**

Caso
Descripción

Caso 1
Para la explotación dirigida a las API de LLM, se presentan principalmente los siguientes dos casos.

**Riesgos del ataque**

Filtración de datos: el atacante puede obtener datos sensibles, incluyendo información de identidad personal, secretos comerciales, etc.
Interrupción del servicio: la ejecución de código malicioso o el acceso no autorizado pueden provocar la interrupción del servicio o la degradación del rendimiento.
Riesgos legales y de cumplimiento: las vulnerabilidades de seguridad pueden dar lugar a litigios legales y problemas de cumplimiento normativo.

**Medidas de mitigación**

Medida de mitigación
Descripción

Principio de mínimo privilegio
Seguir el principio de mínimo privilegio, otorgando a los LLM únicamente los permisos de acceso mínimos necesarios para completar su tarea, evitando la autorización excesiva de agentes.

Validación de entrada/salida
Validar exhaustivamente todas las entradas enviadas a través de la API para prevenir ataques de inyección.

Monitoreo y registro
Monitorear la nueva actividad de API en la era de la IA y registrar los logs, para poder detectar y responder rápidamente a comportamientos sospechosos.

---
### Envenenamiento del Código Fuente de Aplicaciones LLM

> Número de riesgo: GAARM.0038
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

El código fuente puede presentar ciertas vulnerabilidades durante el proceso de revisión; los atacantes inyectan código malicioso en el código fuente de aplicaciones de grandes modelos de lenguaje (LLM), ocultando el código mediante vulnerabilidades para evadir la revisión, y envenenando el código fuente de componentes de código abierto o comerciales de terceros, provocando problemas de seguridad en la aplicación durante el entrenamiento o la ejecución, lo que afecta a los fabricantes de aplicaciones de modelos posteriores que utilizan estos componentes.

**Casos de ataque**

Caso
Descripción

Caso 1
Los atacantes pueden manipular el modelo subiendo código malicioso a sitios de código abierto, afectando así diversos ámbitos como inversión, comercio, noticias, etc.

**Riesgos del ataque**

Inserción de puerta trasera: mediante la inyección de código de puerta trasera en los datos de entrenamiento, se permite al atacante controlar o manipular la salida del modelo durante el proceso de inferencia, provocando acceso no autorizado o manipulación de datos.
Ataques a la cadena de suministro: mediante la inyección de código malicioso en código de código abierto, el atacante puede afectar a toda la cadena de suministro que utiliza dicho código.
Propagación de noticias falsas: el atacante puede aprovechar esta técnica para modificar contenido, como reseñas de películas o reportajes de noticias, con el fin de difundir información falsa o propaganda.

**Medidas de mitigación**

Medida de mitigación
Descripción

Detección de cambios que se desvían del código original
Identificar e interceptar comportamientos anómalos provocados por modificaciones de código malicioso.

Validación y filtrado de entradas
Realizar una validación y limpieza estricta de entradas antes de que el código se introduzca en el modelo.

**Referencias**

https://drive.google.com/file/d/1CTVcliUblX35cWfB49Xjhf8xk-fM3QH1/edit?pli=1

---
### Robo del Código Fuente de Aplicaciones LLM

> Número de riesgo: GAARM.0037
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este riesgo se refiere a que el código fuente del modelo o del gran modelo de lenguaje (LLM) no se almacena adecuadamente, o el entorno de despliegue presenta riesgos de seguridad, lo que puede permitir que personal no autorizado ataque el entorno de despliegue correspondiente, logrando el robo del código fuente de la aplicación LLM, provocando así un riesgo de deterioro de la ventaja competitiva tecnológica de la empresa.

**Casos de ataque**

Caso
Descripción

Caso 1
Se filtró el modelo de lenguaje de 65 mil millones de parámetros de Meta.

Caso 2
Se filtró una gran cantidad de información sobre GPT-4 de OpenAI, incluyendo la arquitectura del modelo, los costos de entrenamiento, los conjuntos de datos, entre otros.

**Riesgos del ataque**

Pérdida de ventaja tecnológica: los competidores pueden copiar o modificar el código fuente filtrado, debilitando así la ventaja competitiva tecnológica de la empresa.
Amenaza de ciberseguridad: los atacantes pueden aprovechar el código fuente filtrado para diseñar ciberataques dirigidos, por ejemplo, penetrando el sistema a través de las vulnerabilidades reveladas.
Riesgo de correos de phishing: el código fuente filtrado puede utilizarse para crear correos de phishing más engañosos que imiten las aplicaciones internas de la empresa, aumentando el riesgo de que los usuarios caigan en el engaño.

**Medidas de mitigación**

Medida de mitigación
Descripción

Protección mediante cifrado del código
Utilizar algoritmos de cifrado fuertes para cifrar el código fuente de las aplicaciones LLM, previniendo el acceso no autorizado y la filtración.

Control de permisos de acceso
Restringir los permisos de acceso al código fuente de las aplicaciones LLM, garantizando que solo el personal autorizado pueda ver o modificar el código.

Monitoreo del modelo
Monitorear el uso del modelo, garantizando que no se utilice con fines maliciosos.

**Referencias**

https://analyticsindiamag.com/metas-llama-leaked-to-the-public-thanks-to-4chan/
https://knightcolumbia.org/blog/the-llama-is-out-of-the-bag-should-we-expect-a-tidal-wave-of-disinformation

---

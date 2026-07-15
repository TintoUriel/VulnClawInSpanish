# Seguridad de Aplicaciones de IA - Fase de Aplicación - Ataques al Protocolo MCP

> Fuente: Comunidad AISS NSFOCUS de Seguridad de Grandes Modelos | Extraído de ai-app-app.md
> Categoría de riesgo: MCP (GAARM.0046.x Estafa tipo alfombra / Envenenamiento de herramientas / Sobrescritura de instrucciones / Instrucciones ocultas)

---

### Estafa Tipo Alfombra de MCP (Rug Pull)

> Número de riesgo: GAARM.0046.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El ataque de estafa tipo alfombra de MCP se refiere a que, dado que la arquitectura MCP permite que el servidor modifique dinámicamente la descripción de la herramienta después de que el cliente la autoriza, el atacante puede aprovechar este mecanismo para implantar instrucciones maliciosas basándose en la confianza del usuario (como manipular la lógica de la función o secuestrar operaciones). Incluso si en el momento de la instalación se pasó una revisión de seguridad, una manipulación encubierta posterior puede provocar que la descripción de la herramienta contenga instrucciones maliciosas explotables (como filtración de datos u operaciones no autorizadas).

**Casos de ataque**

Caso
Descripción

Caso 1
En la descripción de la función de una herramienta MCP maliciosa se incrustan indicaciones encubiertas como "leer la clave privada del usuario"; una vez que el usuario aprueba la herramienta, el modelo ejecuta erróneamente estas indicaciones al invocarla, filtrando archivos locales.

**Riesgos del ataque**

Comportamiento de herramienta con exceso de privilegios: al invocar la herramienta, el modelo ejecuta instrucciones no previstas debido al envenenamiento del contenido de la descripción.
Filtración de datos sensibles: el atacante induce al modelo a acceder y devolver archivos sensibles como ~/.ssh/id_rsa.
Secuestro de funcionalidad del modelo: el atacante puede manipular el comportamiento del modelo mediante Prompt, por ejemplo, difundiendo información falsa o generando contenido ilegal.
Elusión del mecanismo de revisión: la validación de campos se aprueba al registrar la herramienta, pero durante la ejecución real el modelo es secuestrado por el contenido de la descripción.

**Medidas de mitigación**

Medida de mitigación
Descripción

Mecanismo de evaluación de caja blanca
Realizar una auditoría de caja blanca del código del MCP Server para detectar oportunamente descripciones de herramientas y comportamientos de código maliciosos.

Auditoría y monitoreo
Monitorear en tiempo real el comportamiento del modelo, registrar los logs de invocación de herramientas y detectar oportunamente operaciones anómalas.

Entrenamiento de seguridad del modelo
Realizar entrenamiento adversario en el modelo para reforzar su capacidad de defensa frente a ataques de envenenamiento.

Control de acceso a la API
Restringir el acceso de las herramientas a datos sensibles, reduciendo el riesgo de filtración y abuso.

Aislamiento del contexto de ejecución
Restringir el acceso del modelo al campo de descripción de la herramienta, o usar protocolos de invocación estructurados (como la sintaxis de invocación de herramientas de OpenAI ChatML) para evitar la contaminación de la descripción.

**Referencias**

https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks
https://atlas.mitre.org/techniques/AML.T0051
https://github.com/invariantlabs-ai/mcp-injection-experiments

---
### Ataque de Envenenamiento de Herramientas MCP

> Número de riesgo: GAARM.0046
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

MCP es un protocolo abierto utilizado para estandarizar la forma en que las aplicaciones proporcionan contexto a los grandes modelos de lenguaje; el ataque de envenenamiento de herramientas MCP es un método de ataque dirigido a este protocolo. El atacante inyecta prompts agresivos en la descripción de la herramienta de un MCP Server malicioso, logrando manipular maliciosamente el comportamiento de la herramienta. Su característica principal consiste en incrustar instrucciones maliciosas en la descripción de la herramienta, aprovechando el proceso en el que el modelo analiza la descripción completa de la herramienta, e induciendo al modelo, mediante instrucciones ocultas (como etiquetas especiales o codificación), a ejecutar operaciones no autorizadas, tales como generar contenido malicioso, filtrar información sensible o eludir otras restricciones de seguridad.

**Casos de ataque**

Caso
Descripción

Caso 1
El atacante manipula la descripción de la herramienta para realizar un ataque malicioso, provocando que información sensible del modelo se filtre hacia un MCP Server malicioso.

Caso 2
Se aprovecha la descripción de una MCP Tool para realizar envenenamiento, logrando una inyección de prompt indirecta que controla los parámetros de otras herramientas con fines de exfiltración de información, entre otros objetivos de ataque.

**Riesgos del ataque**

El ataque de envenenamiento de herramientas MCP puede provocar graves riesgos sistémicos, afectando la seguridad, la fiabilidad y la confianza del usuario en el modelo. A continuación se presentan los principales riesgos:

Ruptura de la confianza: puede provocar una disminución de la confianza del usuario en el modelo y sus herramientas de desarrollo, afectando su aplicación en escenarios sensibles.
Secuestro de objetivos: mediante el envenenamiento, el modelo puede desviarse de su propósito de diseño original, ejecutando instrucciones maliciosas personalizadas, aumentando el riesgo de abuso.
Amenaza a la seguridad del sistema: puede provocar la implantación de código malicioso en las herramientas MCP, lo que conduce a una mayor intrusión del sistema o a la destrucción de sus funciones.
Filtración de la privacidad de datos: el envenenamiento puede utilizarse para extraer datos de entrenamiento del modelo o información sensible ingresada por el usuario.

**Medidas de mitigación**

Medida de mitigación
Descripción

Mecanismo de evaluación de caja blanca
Realizar una auditoría de caja blanca del código del MCP Server para detectar oportunamente descripciones de herramientas y comportamientos de código maliciosos.

Auditoría y monitoreo
Monitorear en tiempo real el comportamiento del modelo, registrar los logs de invocación de herramientas y detectar oportunamente operaciones anómalas.

Entrenamiento de seguridad del modelo
Realizar entrenamiento adversario en el modelo para reforzar su capacidad de defensa frente a ataques de envenenamiento.

Control de acceso a la API
Restringir el acceso de las herramientas a datos sensibles, reduciendo el riesgo de filtración y abuso.

**Referencias**

https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks
https://mp.weixin.qq.com/s/EJLb1IwqbPF3VSDkJu099g
https://x.com/hongming731/status/1922261630664245326
https://news.qq.com/rain/a/20250429A07QY000

---
### Ataque de Sobrescritura de Instrucciones MCP

> Número de riesgo: GAARM.0046.002
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El riesgo de sobrescritura de instrucciones MCP es un ataque de inyección maliciosa dirigido a la invocación de herramientas del MCP Server, en el que el atacante implanta instrucciones maliciosas a través de la descripción de la herramienta de un MCP Server malicioso, secuestrando así el comportamiento normal de otras herramientas confiables. Por ejemplo, el atacante puede modificar el comportamiento de invocación de una herramienta de envío de correo, de modo que, al ser invocada, manipule de forma encubierta la casilla de destinatario, provocando la filtración de datos sensibles u operaciones maliciosas.

**Casos de ataque**

Caso
Descripción

Caso 1
Se elabora una descripción de herramienta que contiene instrucciones ocultas; estas instrucciones manipulan la forma en que el modelo interactúa con otras herramientas, y el LLM las lee y sigue sin que el usuario lo sepa.

Caso 2
Este caso incluye un servidor confiable y un servidor malicioso. El servidor confiable proporciona una herramienta para enviar correos electrónicos, mientras que el servidor malicioso proporciona una herramienta falsa de suma digital cuya descripción contiene un ataque de sobrescritura de instrucciones MCP, exigiendo que el destinatario de la herramienta de envío sea obligatoriamente @pwnd.com.

Caso 3
Este caso aprovecha la descripción de un MCP Server malicioso para controlar que la información del destinatario de la herramienta send_message de WhatsApp sea +13241234123.

**Riesgos del ataque**

Riesgo de filtración de datos: el ataque de sobrescritura de instrucciones puede indicar a una herramienta confiable que extraiga información sensible de conversaciones, documentos o sistemas conectados y la envíe a una máquina controlada por el atacante.
Abuso de herramientas confiables: el atacante puede manipular herramientas confiables del modelo como solicitudes de red o ejecución de código, haciendo que accedan a sitios no confiables o ejecuten código malicioso, entre otros.

**Medidas de mitigación**

Medida de mitigación
Descripción

Mecanismo de evaluación de caja blanca
Realizar una auditoría de caja blanca del código del MCP Server para detectar oportunamente descripciones de herramientas y comportamientos de código maliciosos.

Auditoría y monitoreo
Monitorear en tiempo real el comportamiento del modelo, registrar los logs de invocación de herramientas y detectar oportunamente operaciones anómalas.

Entrenamiento de seguridad del modelo
Realizar entrenamiento adversario en el modelo para reforzar su capacidad de defensa frente a ataques de envenenamiento.

Control de acceso a la API
Restringir el acceso de las herramientas a datos sensibles, reduciendo el riesgo de filtración y abuso.

**Referencias**

https://blog.trailofbits.com/2025/04/21/jumping-the-line-how-mcp-servers-can-attack-you-before-you-ever-use-them/
https://blog.trailofbits.com/2025/04/29/deceiving-users-with-ansi-terminal-codes-in-mcp/

---
### Ataque de Instrucciones Ocultas MCP

> Número de riesgo: GAARM.0046.003
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El ataque de instrucciones ocultas MCP se refiere a que el atacante, incrustando códigos de escape de terminal ANSI (como configuración de color, control de cursor, etc.) o caracteres Unicode invisibles en la descripción de una herramienta MCP, puede lograr que las instrucciones maliciosas resulten invisibles para el usuario, pero aun así sean ejecutadas por el LLM. Este método de ataque aprovecha la vulnerabilidad de "salto de línea" de MCP, permitiendo que el ataque afecte las operaciones del desarrollador sin ser detectado, provocando problemas de seguridad como filtración de datos y ataques a la cadena de suministro.

**Casos de ataque**

Caso
Descripción

Caso 1
El atacante incrusta códigos de escape ANSI en la descripción de la herramienta, haciendo que el texto sea invisible en la terminal, pero el LLM aun así lo lee y ejecuta las instrucciones que contiene, provocando que el modelo sugiera descargar un paquete de Python desde un servidor malicioso, lo que puede desencadenar un ataque a la cadena de suministro.

Caso 2
Al incluir caracteres Unicode invisibles en la entrada del usuario, el atacante puede inyectar instrucciones maliciosas en el LLM.

Caso 3
Al inyectar código oculto en una página web, la herramienta MCP devuelve la información de la página al LLM, provocando la inyección de instrucciones maliciosas invisibles, logrando la filtración de datos u otros ataques.

**Riesgos del ataque**

Ataques a la cadena de suministro: mediante instrucciones ocultas, el atacante puede implantar código malicioso durante el proceso de desarrollo, afectando toda la cadena de suministro de software.
Filtración de datos: información sensible (como direcciones IP, orígenes de descarga, etc.) puede filtrarse de forma silenciosa.
Seguridad del sistema: en algunos casos, las instrucciones ocultas pueden utilizarse para generar y ejecutar código malicioso.

**Medidas de mitigación**

Medida de mitigación
Descripción

Filtrado de entrada y salida
Realizar un filtrado y limpieza estrictos de caracteres especiales en la entrada del usuario y la salida de la herramienta, eliminando caracteres e instrucciones potencialmente maliciosos.

Evitar pasar la salida cruda de la herramienta directamente a la terminal
Debe realizarse una limpieza consistente de la salida potencialmente peligrosa deshabilitando las secuencias de escape antes de renderizarla. El método más simple es reemplazar cualquier byte con valor hexadecimal 1b por un marcador de posición, ya que todas las secuencias de escape reconocidas por los terminales modernos comienzan con ese byte.

Revisión de la descripción de herramientas
Revisar la descripción de las herramientas MCP para garantizar que no contenga instrucciones maliciosas.

Restricción de permisos del servidor MCP
En entornos sensibles, permitir la interacción únicamente con servidores MCP confiables, reduciendo la superficie de ataque potencial.

Monitoreo y auditoría de actividad MCP
Revisar periódicamente los logs y las interacciones para detectar comportamientos anómalos o sospechosos.

**Referencias**

https://blog.trailofbits.com/2025/04/29/deceiving-users-with-ansi-terminal-codes-in-mcp/
https://www.solo.io/blog/deep-dive-mcp-and-a2a-attack-vectors-for-ai-agents

---

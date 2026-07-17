# Seguridad de Aplicaciones de IA

> Fuente: Comunidad AISS de Cadena de Inteligencia de Seguridad de Grandes Modelos de NSFOCUS (绿盟)
> Número de entradas: 34

---

## Fase de aplicación

### Ataque de inyección en CoT

> Código de riesgo: GAARM.0042
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

CoT (Chain of Thought, cadena de pensamiento) mejora eficazmente la capacidad de razonamiento del LLM al inducirlo a pensar en una serie de pasos clave para resolver un problema. El framework técnico ReAct (Reason + Act) implementa el razonamiento CoT, y aprovecha la orquestación de Agents para dotar al LLM de la capacidad de interactuar con el mundo externo, permitiendo conectarse sin fisuras con diversos sistemas externos y ejecutar tareas complejas.
En una aplicación CoT, el usuario proporciona una pregunta en lenguaje natural, y el modelo de IA genera una serie de pasos de razonamiento para responderla, involucrando tres pasos centrales: pensamiento (Thought), acción (Act) y observación (Obs). El modelo de IA repite estos tres pasos en bucle para completar el razonamiento y la resolución de diversos problemas complejos. Dado que todo este proceso es más abierto y flexible que la lógica de código tradicional, y carece de una estructura estricta de control de flujo, el atacante puede, mediante un ataque de inyección en CoT, eludir pasos de razonamiento específicos, induciendo al modelo de IA a ejecutar acciones no previstas, como: riesgos de funciones de negocio (transferencias arbitrarias de usuario, etc.) y riesgos de funciones técnicas (SSRF, RCE, etc.). Actualmente, el ataque de inyección en CoT tiene principalmente dos enfoques:

- Inyección de interferencia en la cadena de pensamiento: observando el proceso de orquestación de CoT, se construye una entrada maliciosa para engañar al modelo haciéndole creer que ya ha obtenido el resultado de un Agent, falsificando ese resultado para interferir en el funcionamiento de CoT
- Inyección de manipulación en la cadena de pensamiento: observando el proceso de orquestación de CoT, se construye directamente, o mediante técnicas de ataque adversarial, una entrada maliciosa para manipular el proceso de CoT, haciendo que el modelo omita el proceso de CoT preestablecido y despache directamente un Agent sensible

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Este caso plantea principalmente, en una aplicación de LLM basada en el framework ReAct, cómo aprovechar su proceso de cadena de pensamiento CoT para lograr el uso malicioso de un Agent |
| Caso 2 | Esta investigación descubrió que, combinando prompts de jailbreak con prompts de CoT, aprovechando CoT para eludir las restricciones éticas del LLM, se puede provocar que el modelo genere información privada |
| Caso 3 | Reto CTF de código abierto sobre ataque de inyección de consultas bajo el framework ReAct |

**Riesgo del ataque**

En aplicaciones LLM que usan sistemas de recuperación de información, el atacante puede contaminar la base de datos de recuperación de información, haciendo que se inyecten fragmentos de texto maliciosos en la consulta enviada al LLM, afectando así el resultado final de salida, y provocando una serie de riesgos como violación de la privacidad del usuario y ejecución de código malicioso.
En una aplicación LLM de un sistema de negocio de reembolsos, el atacante puede interferir con el flujo de CoT de reembolso, haciendo que órdenes que originalmente no cumplían las condiciones de reembolso puedan ser reembolsadas normalmente; o manipular directamente y de forma maliciosa el Agent de la operación de reembolso, haciendo que el monto real reembolsado no coincida con el monto esperado, causando así pérdidas económicas a la empresa.

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Control estricto de permisos | Aplicar un control de privilegios estricto, garantizando que el LLM solo pueda acceder al contenido y los Agents necesarios, minimizando así los posibles puntos de vulnerabilidad |
| Control de orquestación de Agents del LLM | Implementar un mecanismo externo estricto de verificación de permisos automática o manual para los Agents de operaciones sensibles, evitando que el LLM posea directamente los permisos de uso correspondientes |
| Refuerzo del contenido del prompt | Adoptar soluciones como el ChatML (OpenAI Chat Markup Language) para intentar aislar el prompt real del usuario de otro contenido |

**Referencias**

http://youtube.com/watch?v=7ZA0Z1R-MjQ
http://youtube.com/watch?v=KksYizcLFH0

---
### Estafa de alfombra roja (Rug Pull) en MCP

> Código de riesgo: GAARM.0046.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El ataque de estafa de alfombra roja (Rug Pull) en MCP se refiere a que, dado que la arquitectura MCP permite que el servidor modifique dinámicamente la descripción de una herramienta después de que el cliente la haya autorizado, el atacante puede aprovechar este mecanismo para implantar instrucciones maliciosas (como alterar la lógica funcional o secuestrar operaciones) basándose en la confianza del usuario. Incluso si la instalación pasó una revisión de seguridad, la manipulación encubierta posterior aún puede provocar que la descripción de la herramienta sea implantada con instrucciones de explotación maliciosa (como fuga de datos u operaciones no autorizadas).

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | En la descripción de una función de herramienta MCP maliciosa se incrusta una indicación encubierta como "leer la clave privada del usuario"; una vez que el usuario aprueba la herramienta, al invocarla el modelo ejecuta erróneamente estas indicaciones, filtrando archivos locales |

**Riesgo del ataque**

- Comportamiento de herramienta con exceso de privilegios: al invocar la herramienta, el modelo ejecuta instrucciones no previstas debido a que el contenido de la descripción fue envenenado
- Fuga de datos sensibles: el atacante induce al modelo a acceder y mostrar archivos sensibles como ~/.ssh/id_rsa
- Secuestro de la funcionalidad del modelo: el atacante puede manipular el comportamiento del modelo mediante el Prompt, como difundir información falsa o generar contenido ilegal
- Elusión del mecanismo de revisión: el campo pasa la validación al registrar la herramienta, pero en la ejecución real el modelo es secuestrado por el contenido de la descripción

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Mecanismo de evaluación de caja blanca | Realizar una auditoría de caja blanca del código del MCP Server, detectando oportunamente descripciones de herramientas y comportamientos de código maliciosos |
| Auditoría y monitoreo | Monitorear en tiempo real el comportamiento del modelo, registrar los logs de invocación de herramientas, detectar oportunamente operaciones anómalas |
| Entrenamiento de seguridad del modelo | Aplicar entrenamiento adversarial al modelo, reforzando su capacidad de defensa frente a ataques de envenenamiento |
| Control de acceso a la API | Restringir el acceso de las herramientas a datos sensibles, reduciendo el riesgo de fuga y abuso |
| Aislamiento del contexto de ejecución | Restringir el acceso del modelo a los campos de descripción de herramientas, o usar un protocolo de invocación estructurado (como la sintaxis de invocación de herramientas ChatML de OpenAI) para evitar la contaminación de la descripción |

**Referencias**

https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks
https://atlas.mitre.org/techniques/AML.T0051
https://github.com/invariantlabs-ai/mcp-injection-experiments

---
### Ataque de envenenamiento de herramientas MCP

> Código de riesgo: GAARM.0046
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

MCP es un protocolo abierto para estandarizar la forma en que las aplicaciones proporcionan contexto a los modelos de lenguaje grande; el ataque de envenenamiento de herramientas MCP es una forma de ataque dirigida contra este protocolo. El atacante, mediante un MCP Server malicioso, inyecta un prompt ofensivo en la descripción de una herramienta, logrando la manipulación maliciosa del comportamiento de esta. Su característica central es incrustar instrucciones maliciosas en la descripción de la herramienta, aprovechando el proceso en que el modelo analiza la descripción completa de la herramienta; mediante instrucciones ocultas (como etiquetas especiales o codificación), se induce al modelo a ejecutar operaciones no autorizadas, como generar contenido malicioso, filtrar información sensible o eludir otras restricciones de seguridad.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | El atacante, manipulando la descripción de una herramienta, logra un ataque malicioso que provoca la fuga de información sensible del modelo hacia un MCP Server malicioso |
| Caso 2 | Se aprovecha la descripción de una herramienta MCP para envenenarla, logrando una inyección de prompt encubierta que controla los parámetros de otras herramientas para lograr la exfiltración de información y otros objetivos de ataque |

**Riesgo del ataque**

El ataque de envenenamiento de herramientas MCP puede provocar riesgos sistémicos graves, afectando la seguridad, confiabilidad y confianza del usuario en el modelo. A continuación los principales riesgos:

- Ruptura de la confianza: puede provocar una disminución de la confianza del usuario en el modelo y sus herramientas de desarrollo, afectando su aplicación en escenarios sensibles
- Secuestro de objetivo: el envenenamiento puede hacer que el modelo se desvíe de su propósito de diseño original, ejecutando instrucciones maliciosas personalizadas, aumentando el riesgo de abuso
- Amenaza a la seguridad del sistema: puede provocar la implantación de código malicioso en las herramientas MCP, provocando una mayor intrusión del sistema o la ruptura de sus funciones
- Fuga de privacidad de datos: el envenenamiento puede usarse para extraer los datos de entrenamiento del modelo o información sensible ingresada por el usuario

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Mecanismo de evaluación de caja blanca | Realizar una auditoría de caja blanca del código del MCP Server, detectando oportunamente descripciones de herramientas y comportamientos de código maliciosos |
| Auditoría y monitoreo | Monitorear en tiempo real el comportamiento del modelo, registrar los logs de invocación de herramientas, detectar oportunamente operaciones anómalas |
| Entrenamiento de seguridad del modelo | Aplicar entrenamiento adversarial al modelo, reforzando su capacidad de defensa frente a ataques de envenenamiento |
| Control de acceso a la API | Restringir el acceso de las herramientas a datos sensibles, reduciendo el riesgo de fuga y abuso |

**Referencias**

https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks
https://mp.weixin.qq.com/s/EJLb1IwqbPF3VSDkJu099g
https://x.com/hongming731/status/1922261630664245326
https://news.qq.com/rain/a/20250429A07QY000

---
### Ataque de sobrescritura de instrucciones en MCP

> Código de riesgo: GAARM.0046.002
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El riesgo de sobrescritura de instrucciones en MCP es un ataque de inyección malicioso dirigido a la invocación de herramientas del MCP Server. El atacante, mediante la descripción de una herramienta de un MCP Server malicioso, implanta en ella instrucciones maliciosas, secuestrando así el comportamiento normal de otras herramientas confiables. Por ejemplo, el atacante puede modificar el comportamiento de invocación de una herramienta de envío de correo, haciendo que al invocarla altere subrepticiamente el destinatario, provocando la fuga de datos sensibles u operaciones maliciosas.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Se elabora una descripción de herramienta que contiene instrucciones ocultas; estas instrucciones manipulan la forma en que el modelo interactúa con otras herramientas, y el LLM lee y sigue estas instrucciones sin que el usuario lo sepa |
| Caso 2 | Este caso incluye un servidor confiable y un servidor malicioso. El servidor confiable proporciona una herramienta de envío de correo electrónico, mientras que el servidor malicioso proporciona una herramienta falsa de suma digital, cuya descripción contiene un ataque de sobrescritura de instrucciones MCP que exige que el destinatario de la herramienta de envío debe ser @pwnd.com |
| Caso 3 | Este caso aprovecha la descripción de un MCP Server malicioso para controlar que la información de destinatario de la herramienta send_message de WhatsApp sea +13241234123 |

**Riesgo del ataque**

- Riesgo de fuga de datos: el ataque de sobrescritura de instrucciones puede indicar a una herramienta confiable que extraiga información sensible de la conversación, documentos o sistemas conectados, y la envíe a una máquina controlada por el atacante
- Abuso de herramientas confiables: el atacante puede manipular herramientas confiables del modelo como solicitudes de red o ejecución de código, haciendo que accedan a sitios no confiables o ejecuten código malicioso

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Mecanismo de evaluación de caja blanca | Realizar una auditoría de caja blanca del código del MCP Server, detectando oportunamente descripciones de herramientas y comportamientos de código maliciosos |
| Auditoría y monitoreo | Monitorear en tiempo real el comportamiento del modelo, registrar los logs de invocación de herramientas, detectar oportunamente operaciones anómalas |
| Entrenamiento de seguridad del modelo | Aplicar entrenamiento adversarial al modelo, reforzando su capacidad de defensa frente a ataques de envenenamiento |
| Control de acceso a la API | Restringir el acceso de las herramientas a datos sensibles, reduciendo el riesgo de fuga y abuso |

**Referencias**

https://blog.trailofbits.com/2025/04/21/jumping-the-line-how-mcp-servers-can-attack-you-before-you-ever-use-them/
https://blog.trailofbits.com/2025/04/29/deceiving-users-with-ansi-terminal-codes-in-mcp/

---
### Ataque de instrucciones ocultas en MCP

> Código de riesgo: GAARM.0046.003
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El ataque de instrucciones ocultas en MCP se refiere a que el atacante, incrustando códigos de escape de terminal ANSI (como configuración de color, control de cursor, etc.) o caracteres Unicode invisibles en la descripción de una herramienta MCP, logra que instrucciones maliciosas sean invisibles para el usuario, pero aun así sean ejecutadas por el LLM. Esta forma de ataque aprovecha la vulnerabilidad de "salto de línea" de MCP, afectando las operaciones del desarrollador sin ser percibida, provocando problemas de seguridad como fuga de datos y ataques a la cadena de suministro.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | El atacante, incrustando códigos de escape ANSI en la descripción de una herramienta, hace que el texto sea invisible en la terminal, pero el LLM aun así lee y ejecuta las instrucciones contenidas en él, provocando que el modelo sugiera descargar paquetes de Python desde un servidor malicioso, lo que puede desencadenar un ataque a la cadena de suministro |
| Caso 2 | Incorporando caracteres Unicode invisibles en la entrada del usuario, el atacante puede inyectar instrucciones maliciosas en el LLM |
| Caso 3 | Inyectando código oculto en una página web, cuando la herramienta MCP devuelve la información de la página al LLM, se inyectan instrucciones maliciosas invisibles, logrando fuga de datos u otros ataques |

**Riesgo del ataque**

- Ataque a la cadena de suministro: mediante instrucciones ocultas, el atacante puede implantar código malicioso durante el proceso de desarrollo, afectando toda la cadena de suministro de software
- Fuga de datos: información sensible (como direcciones IP, fuentes de descarga, etc.) puede filtrarse de forma silenciosa
- Seguridad del sistema: en algunos casos, las instrucciones ocultas pueden usarse para generar y ejecutar código malicioso

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Filtrado de entrada/salida | Filtrar y depurar estrictamente los caracteres especiales de la entrada del usuario y la salida de las herramientas, eliminando caracteres e instrucciones potencialmente maliciosos |
| Evitar pasar la salida cruda de la herramienta directamente a la terminal | Se debe realizar una limpieza consistente de las salidas potencialmente peligrosas deshabilitando las secuencias de escape antes de renderizarlas. El método más simple es reemplazar cualquier byte de valor hexadecimal 1b con un marcador de posición, ya que todas las secuencias de escape reconocidas por las terminales modernas comienzan con ese byte |
| Revisión de la descripción de la herramienta | Revisar la descripción de las herramientas MCP, garantizando que no contengan instrucciones maliciosas |
| Restringir los permisos del servidor MCP | En entornos sensibles, permitir la interacción únicamente con MCP Server confiables, reduciendo la superficie de ataque potencial |
| Monitorear y auditar la actividad de MCP | Revisar periódicamente los logs y las interacciones para detectar comportamientos anómalos o sospechosos |

**Referencias**

https://blog.trailofbits.com/2025/04/29/deceiving-users-with-ansi-terminal-codes-in-mcp/
https://www.solo.io/blog/deep-dive-mcp-and-a2a-attack-vectors-for-ai-agents

---
### Inyección de prompt

> Código de riesgo: GAARM.0039
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

La inyección de prompt es una técnica en la que el atacante usa entradas especialmente construidas para sobrescribir o manipular el proceso de instrucciones original del LLM. Dado que el lenguaje natural es en sí mismo ambiguo, el límite entre instrucción y dato a menudo no es claro, lo que provoca que el atacante pueda usar entradas externas maliciosas para contaminar la salida del modelo. Este ataque suele ocurrir cuando se usa una entrada no confiable como parte del prompt. El LLM puede reconocer y procesar el lenguaje natural, y como este es en sí mismo ambiguo, la instrucción y el dato a menudo no tienen un límite claro; el atacante puede incluir instrucciones en campos de datos que controla, mientras que el sistema, a nivel subyacente, no puede distinguir entre dato e instrucción.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Se usa entrada maliciosa para manipular el prompt de GPT-3, ordenando al modelo que ignore sus instrucciones previas |
| Caso 2 | Se usan múltiples métodos para realizar el ataque de inyección de prompt |

**Riesgo del ataque**

El éxito de la inyección de prompt puede provocar daños como la fuga del meta-prompt, el jailbreak del modelo y el abuso de sus funciones.

- Generación de contenido malicioso: el atacante puede aprovechar la inyección de prompt para generar contenido inapropiado, incluyendo amenazas, difamación u otra información maliciosa
- Fuga de datos: si el LLM se usa para mostrar información sensible, el ataque de inyección de prompt puede provocar su fuga
- Seguridad del sistema: en algunos casos, la inyección de prompt puede usarse para generar y ejecutar código malicioso
- Abuso del modelo: el atacante, mediante técnicas de secuestro de objetivo, hace que el LLM se desvíe de su configuración del sistema predefinida, ejecutando otras instrucciones personalizadas, aumentando el riesgo de abuso del modelo

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Refuerzo del contenido del prompt | Adoptar soluciones similares al ChatML (OpenAI Chat Markup Language) para reforzar la estructura y el contenido del prompt, intentando aislar el prompt real del usuario de otro contenido |
| Alineación de seguridad del modelo | Proporcionar datos de entrenamiento diversos que cubran diversos escenarios de ataque, reforzando la capacidad de generalización y robustez del modelo mediante mecanismos de barreras de seguridad durante la fase de entrenamiento |
| Validación de entrada/salida | Mediante guardianes de seguridad externos instalados en la entrada y salida del modelo, basados en reglas, algoritmos de clasificación o grandes modelos de seguridad, detectar y filtrar el contenido de entrada y salida |
| Monitoreo y registro | Monitorear y registrar las interacciones con el LLM, para poder detectar y analizar posteriormente posibles ataques de inyección de prompt |

**Referencias**

https://aclanthology.org/2024.scalellm-1.2/
https://atlas.mitre.org/techniques/AML.T0051
https://josephthacker.com/ai/2023/05/19/prompt-injection-poc.html
https://simonwillison.net/2022/Sep/12/prompt-injection/

---
### Simulación y sondeo de entorno SSRF

> Código de riesgo: GAARM.0041.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El SSRF se origina en su mayoría porque el servidor ofrece la funcionalidad de obtener datos de otras aplicaciones de servidor, sin filtrar ni restringir la dirección objetivo. Si existe una vulnerabilidad SSRF en la aplicación LLM, el atacante puede aprovecharla para iniciar solicitudes de red interna, accediendo a recursos restringidos dentro de la aplicación. Al mismo tiempo, algunos LLM pueden tener incorporado un Agent con funcionalidad de acceso a la red, usado para realizar consultas de información externa, entre otras operaciones. El atacante puede aprovechar una vulnerabilidad SSRF en la API de la aplicación LLM, o el Agent con capacidad de acceso a la red dentro del LLM, para ejecutar solicitudes inesperadas o acceder a recursos restringidos (como servicios internos, API o almacenamiento de datos), accediendo así a los sistemas internos del modelo y aumentando el riesgo de fuga de información del modelo, servicios internos, datos sensibles, etc.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | La aplicación ChatGPT-Next-Web presenta una vulnerabilidad SSRF (CVE-2023-49785), que puede usarse para sondear recursos de la red interna |

**Riesgo del ataque**

- Acceso a recursos internos: el atacante puede aprovechar la vulnerabilidad SSRF para enviar solicitudes y obtener información sensible dentro de la red interna
- Proxy de tráfico de ataque: aprovechando la vulnerabilidad SSRF, el atacante puede enviar solicitudes maliciosas para atacar sistemas, servicios o recursos internos
- Fuga de datos: el atacante puede aprovechar este riesgo para obtener datos sensibles, como claves de acceso de plataformas en la nube

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Control de orquestación de la API del LLM y aislamiento en sandbox | Implementar un mecanismo de sandbox adecuado para aislar el LLM, y restringir su acceso a recursos de red, servicios internos y API. Mediante un control de acceso estricto, las organizaciones pueden minimizar la posibilidad de interacciones no autorizadas y mitigar el impacto de vulnerabilidades SSRF |
| Evaluación y revisión de seguridad periódica del LLM | Auditar y revisar periódicamente la configuración de seguridad de red y de la aplicación, para identificar y corregir cualquier error de configuración, garantizando que los recursos internos no queden expuestos inadvertidamente al LLM, reforzando el sistema de seguridad integral |
| Validación de entrada/salida | Implementar técnicas confiables de validación y procesamiento de entrada, para garantizar que los prompts sean revisados y filtrados a fondo, ayudando a prevenir que prompts maliciosos o inesperados desencadenen solicitudes no autorizadas, reduciendo así el riesgo de ataques SSRF |
| Monitoreo y registro | Implementar un mecanismo integral de monitoreo y registro para rastrear las interacciones del LLM. Mediante un monitoreo cercano de la actividad del LLM y el registro de la información relevante, las organizaciones pueden detectar y analizar posibles vulnerabilidades SSRF, permitiendo su detección y corrección oportuna |

**Referencias**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/SSRF.html

---
### Secuestro de contenido de sesión mediante XSS

> Código de riesgo: GAARM.0040.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El secuestro de contenido de sesión mediante XSS, como técnica de ataque de inyección indirecta de prompt, aprovecha el proceso mediante el cual los modelos de lenguaje grande (LLM) obtienen información externa. Cuando el usuario interactúa con el LLM a través de una interfaz proporcionada por este (como una interfaz web, una interfaz API, una aplicación, etc.), el atacante, mediante la inyección indirecta de instrucciones de prompt maliciosas, aprovecha características del análisis de etiquetas Markdown y de la etiqueta HTML img por parte del front-end de la aplicación LLM, para resumir el contenido de la sesión de chat actual, e incrustar claves sensibles, datos, etc. en el atributo src de la etiqueta img, logrando así la fuga del contenido de la sesión.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | El atacante aprovecha la función de actualización de Google Bard, construyendo una etiqueta de imagen Markdown especial, haciendo que Bard renderice una imagen que apunta a un servidor del atacante, logrando el robo de datos |
| Caso 2 | Aprovechando que el modelo de Azure AI Playground permite, mediante inyección de imágenes Markdown, adjuntar el prompt a la URL del atributo src para renderizarlo, provocando riesgos de fuga de datos, entre otros |
| Caso 3 | El atacante aprovecha una función de un plugin de ChatGPT que accede directamente a subtítulos de YouTube, controlando el contenido de los subtítulos mediante inyección indirecta de prompt para manipular el comportamiento de la IA |
| Caso 4 | El atacante puede aprovechar la función de renderizado de imágenes Markdown de ChatGPT para robar el historial de chat; el atacante controla el comportamiento de la IA, solicitando resumir el historial de chat y adjuntarlo a una URL para robar los datos |
| Caso 5 | El atacante, mediante inyección de imágenes Markdown, roba automáticamente datos de la sesión de chat |
| Caso 6 | El atacante puede indicar a ChatGPT que use un plugin para registrar la conversación, generando una URL que apunta al registro, y filtra el enlace mediante inyección de imágenes Markdown, para obtener todo el historial de la conversación |
| Caso 7 | Dado que los agentes LLM (aplicaciones cliente como Bing Chat o ChatGPT) son vulnerables a ataques de inyección de prompt, el atacante puede aprovechar esta vulnerabilidad adjuntando datos sensibles a la URL de una imagen para realizar la exfiltración automática de datos |

**Riesgo del ataque**

- Fuga de datos: el atacante puede obtener información sensible del usuario en la sesión actual, incluyendo tokens de sesión, información personal, historial de chat, etc.
- Secuestro de sesión: el atacante puede tomar control de la sesión del usuario mediante el token de sesión obtenido

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Validación de entrada/salida | Validar y depurar estrictamente todos los datos de entrada y salida, para eliminar o corregir cualquier inyección o contenido generado sospechoso |
| Política de seguridad de contenido (CSP) | Implementar una política de seguridad de contenido (CSP) estricta, bloqueando la ejecución de scripts maliciosos y comportamientos de exfiltración de datos |
| Principio de mínimo privilegio | Garantizar un sandboxing adecuado y restringir las capacidades del LLM, limitando que mecanismos como plugins o Agents obtengan información de fuentes no confiables |
| Aprobación con intervención humana | Otorgar al usuario más control, permitiéndole gestionar el uso de plugins y el flujo de datos |

**Referencias**

https://systemweakness.com/new-prompt-injection-attack-on-chatgpt-web-version-ef717492c5c2

---
### Inyección de ejecución de código

> Código de riesgo: GAARM.0041.002
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

En el framework ReAct, el LLM puede interactuar con sistemas externos; un Agent externo intérprete de código puede usarse para dotar al LLM de capacidad de ejecución de código, permitiendo cumplir necesidades como el dibujo automático de gráficos o cálculos de código complejos durante el proceso de aplicación de negocio. El atacante, construyendo un prompt de entrada malicioso, manipula al LLM para que ejecute un proceso de razonamiento predeterminado, haciendo que el LLM despache un Agent de ejecución de código para ejecutar código o comandos maliciosos en el sistema subyacente, logrando así un ataque y explotación del entorno de ejecución base del LLM. Las principales causas de este ataque son:

- No se detecta, valida ni restringe eficazmente la entrada del usuario, permitiendo que el atacante realice operaciones de ejecución de código malicioso sin autorización
- El entorno sandbox es insuficiente, o las limitaciones de capacidad del LLM son inadecuadas, provocando que interactúe de forma inesperada con el sistema subyacente
- Se exponen inadvertidamente funciones o interfaces a nivel de sistema al LLM

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Tras el lanzamiento de la nueva función de GPT-4, se descubrió que su intérprete de código Python presuntamente tenía una vulnerabilidad de escape de sandbox |

**Riesgo del ataque**

- Riesgo de ejecución de código: el atacante puede ejecutar código Python arbitrario, lo que puede provocar el compromiso del servidor, fuga de datos u otro comportamiento malicioso
- Control de permisos del sistema: si CodeExecutor no cuenta con medidas de seguridad adecuadas, el código ejecutado, combinado con técnicas como el escape de contenedores, puede obtener privilegios elevados del sistema
- Control de acceso persistente: el atacante puede aprovechar esta oportunidad para establecer un canal de acceso a largo plazo, usado para ataques continuos

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Validación de entrada | Implementar un proceso estricto de detección y restricción de entrada, evitando que el LLM procese prompts maliciosos o inesperados |
| Principio de mínimo privilegio | Garantizar un sandboxing adecuado y restringir las capacidades del LLM, para limitar su capacidad de interacción con el sistema subyacente, evitando operaciones que puedan tener un impacto a nivel de sistema |
| Monitoreo y registro | Registrar todas las operaciones ejecutadas mediante el LLM, y monitorearlas en tiempo real, para detectar y responder rápidamente ante actividades sospechosas |

**Referencias**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Unauthorized_Code_Execution.html
https://www.calvin-risk.com/blog/decoding-llm-risks-a-comprehensive-look-at-unauthorized-code-execution

---
### Ofuscación de palabras clave

> Código de riesgo: GAARM.0043
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo se refiere a que se aplica un procesamiento especial a las palabras clave del prompt (homófonos, sinónimos, división de palabras u otras formas de manipulación de texto), de modo que, manteniendo un significado similar, tras la tokenización ya no conserven el significado de riesgo, eludiendo así las restricciones del mecanismo de seguridad del modelo sobre las palabras sensibles.

**Caso de ataque**

En LLM en inglés, los métodos comunes de ofuscación de palabras clave incluyen: ofuscación de letras (bomb -> b0mb), sustitución por sinónimos (bomb -> explosive) y división de palabras (bomb -> b-o-m-b).
Para LLM en chino, debido a las diferencias en los métodos de segmentación de palabras, los métodos de ofuscación de palabras clave también difieren significativamente; los métodos comunes de ofuscación de palabras clave en chino incluyen la sustitución por pinyin (炸弹 -> zha弹), la sustitución por sinónimos (炸弹 -> 爆炸物) y la sustitución por caracteres de forma similar (炸弹 -> 炸掸), entre otros.

**Riesgo del ataque**

- Generación de contenido inapropiado: el atacante puede aprovechar la técnica de ofuscación de palabras clave para eludir el sistema automático de revisión de contenido, publicando o difundiendo contenido malicioso, como violencia, terrorismo o pornografía
- Elusión del mecanismo de seguridad: el atacante induce maliciosamente al modelo a producir una salida incorrecta, para engañar al sistema y hacer que tome malas decisiones o ejecute operaciones peligrosas

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Alineación de seguridad del modelo | Mediante entrenamiento y aprendizaje por refuerzo, mejorar la capacidad del LLM para identificar y resistir este tipo de ataques |
| Validación de entrada/salida | Del lado de la entrada, actualizar y mejorar constantemente el sistema de filtrado de vocabulario, para identificar y bloquear palabras sensibles ofuscadas; del lado de la salida, monitorear el contenido generado por el LLM, identificando contenido potencialmente riesgoso mediante técnicas de análisis de seguridad de contenido |

**Referencias**

https://mp.weixin.qq.com/s/eFDQWYYCOe_SSiourhTxig

---
### Ataque de inducción inversa y supresión

> Código de riesgo: GAARM.0045
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo, mediante la incorporación de instrucciones específicas en el prompt, hace que el LLM evite usar ciertas respuestas de rechazo específicas al generar una respuesta, aumentando así la probabilidad de contenido inseguro o inapropiado que el atacante desea. Este ataque aprovecha la característica autorregresiva del modelo para inducirlo, ya que la generación de contenido del modelo se basa en la salida previa para predecir la siguiente palabra; exigiendo de forma específica que el LLM no use ciertas palabras o frases al generar una respuesta, como "lo siento", "no puedo", "no es posible", etc., se provoca que el modelo genere contenido inapropiado o que viole las políticas de seguridad.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Se usa inyección de prefijo combinada con un ataque de supresión inversa para eludir las restricciones de seguridad de ChatGPT 3.5, logrando la salida de contenido de riesgo relacionado con actividades ilegales o delictivas |

**Riesgo del ataque**

- Generación de contenido inapropiado: el LLM puede generar contenido de riesgo que incluya orientación para actividades ilegales, violencia, pornografía, temas políticamente sensibles, etc.
- Elusión del mecanismo de seguridad: el atacante puede eludir el mecanismo de seguridad del LLM, provocando que el modelo genere el contenido de riesgo deseado por el atacante

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Refuerzo de la robustez del modelo | Mediante entrenamiento y aprendizaje por refuerzo, mejorar la capacidad del LLM para identificar y resistir este tipo de ataques |
| Monitoreo y filtrado de entrada | Monitorear en tiempo real la salida del LLM, filtrando oportunamente contenido inseguro o inapropiado |

---
### Ataque de sustitución de sinónimos

> Código de riesgo: GAARM.0043.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El ataque de sustitución de sinónimos es una técnica de ataque que, usando sinónimos con significado igual o similar a palabras o frases sensibles, elude las medidas de protección de seguridad del modelo, obteniendo o filtrando así las instrucciones internas o información sensible del modelo. A medida que los LLM se vuelven cada vez más grandes, es cada vez más difícil ajustar finamente cada ejemplo de ataque existente, y el modelo se vuelve vulnerable a ataques de sustitución de sinónimos. Por ejemplo, en un asistente de programación, el atacante puede sustituir "delete" por "remove", "destroy" por "harm", etc., intentando eludir la verificación de palabras clave.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | El atacante, mediante la sustitución de sinónimos, elude exitosamente el filtrado del modelo, logrando la fuga de la configuración del prompt del sistema |

**Riesgo del ataque**

- Fuga de información sensible: el atacante puede obtener las instrucciones internas del modelo, incluyendo entre otros el prompt del sistema, contraseñas y otra información sensible
- Elusión del mecanismo de seguridad: el atacante puede aprovechar el ataque de sustitución de sinónimos para eludir la protección de seguridad del modelo, provocando que genere salidas no deseadas o ejecute operaciones no autorizadas

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Alineación de seguridad del modelo | Proporcionar datos de entrenamiento diversos que cubran diversos escenarios de ataque, para reforzar la capacidad de generalización y robustez del modelo |
| Validación de entrada/salida | Del lado de la entrada, actualizar y mejorar constantemente el sistema de filtrado de vocabulario, para identificar y bloquear palabras sensibles ofuscadas; del lado de la salida, monitorear el contenido generado por el LLM, identificando contenido potencialmente riesgoso mediante técnicas de análisis de seguridad de contenido |

**Referencias**

https://arxiv.org/html/2402.16914v1

---
### Ataque de inyección coordinada multimodal

> Código de riesgo: GAARM.0061
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El ataque de inyección coordinada multimodal es una técnica de ataque avanzada que aprovecha la relación de coordinación entre múltiples modalidades (texto, imagen, audio, video, etc.) para incrustar instrucciones maliciosas. El atacante, mediante la construcción cuidadosa de contenido malicioso entre modalidades, aprovecha el mecanismo de asociación semántica del modelo multimodal al procesar y comprender información de diferentes modalidades, incrustando instrucciones maliciosas en contenido multimodal aparentemente inofensivo. El núcleo de este ataque radica en eludir el mecanismo de detección de seguridad de una sola modalidad, logrando su objetivo mediante el efecto de coordinación entre modalidades, lo que puede provocar fuga de datos, manipulación del comportamiento del modelo o la ejecución de operaciones no previstas.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | El atacante aprovecha la inyección de conflicto entre modalidades (CMCI), insertando pares imagen-texto adversariales especiales en la base de conocimiento mediante el mecanismo normal de actualización del sistema. Estos pares parecen semánticamente alineados al recuperarse (por ejemplo, la imagen muestra neumonía, pero el texto describe "pulmones despejados"), pero el contenido real es contradictorio, induciendo así a la IA a generar una conclusión completamente errónea al diagnosticar (como confundir neumonía con un estado normal), causando un grave riesgo de seguridad médica |

**Riesgo del ataque**

- Fuga de datos: se induce al modelo a filtrar datos de entrenamiento o información sensible
- Manipulación del comportamiento: se manipula la salida y el comportamiento del modelo mediante instrucciones entre modalidades
- Elusión de seguridad: se elude el mecanismo de detección y control de seguridad de una sola modalidad
- Escalada de privilegios: se aprovecha la coordinación entre modalidades para obtener privilegios de sistema más elevados
- Violación de la privacidad: se obtiene información privada del usuario mediante el análisis multimodal

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Detección de coordinación entre modalidades | Establecer un mecanismo de detección de seguridad de coordinación multimodal, implementar análisis de asociación semántica entre modalidades, detectar patrones anómalos de combinación de modalidades |
| Verificación de seguridad multidimensional | Verificar simultáneamente la seguridad de múltiples modalidades, establecer una verificación de consistencia entre modalidades, implementar el intercambio de inteligencia de amenazas entre modalidades |
| Refuerzo del proceso de fusión | Incorporar verificaciones de seguridad en el proceso de fusión multimodal, implementar un ajuste dinámico del peso de las modalidades, establecer la detección de patrones de fusión anómalos |
| Procesamiento de aislamiento por modalidad | Realizar un preprocesamiento de aislamiento por modalidad, implementar un filtrado de seguridad a nivel de modalidad, establecer un mecanismo de comunicación segura entre modalidades |

**Referencias**

Manipulación de agentes multimodales mediante inyección de prompt entre modalidades
Cómo hacer más seguros los sistemas de IA médica: vulnerabilidades y amenazas en sistemas RAG médicos multimodales

---
### Ataque de codificación adversarial

> Código de riesgo: GAARM.0044
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El ataque de codificación adversarial es una técnica adversarial dirigida contra el mecanismo de detección de defensa de entrada y salida del LLM; el atacante, codificando o transformando datos (como usando codificación base64), intenta eludir la verificación de seguridad o inyectar contenido malicioso. Este ataque se dirige a la capa de codificación de los modelos de PLN, intentando eludir la capacidad de comprensión de texto del modelo, afectando directamente la generación de las características internas.
Dado que el LLM fue entrenado con texto codificado y otros tipos de datos diversos, soporta la operación normal de decodificación, y permite completar la ejecución de instrucciones maliciosas o la exfiltración de datos sensibles.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Se aprovecha un ataque de codificación adversarial para eludir las restricciones de seguridad de ChatGPT, obteniendo información de claves almacenadas |
| Caso 2 | Este artículo investigó cómo modelos de PLN basados en texto son interferidos y engañados mediante perturbaciones de codificación manipuladas, las cuales, aprovechando la funcionalidad de codificación del lenguaje, pueden cambiar la salida del modelo y aumentar el tiempo de ejecución de inferencia. Por ejemplo, se usan caracteres únicos que se presentan como glifos idénticos o visualmente similares para perturbar la entrada del modelo |

**Riesgo del ataque**

- Elusión del mecanismo de seguridad: el atacante puede aprovechar la capacidad de codificación/decodificación del modelo para eludir la verificación de seguridad de contenido
- Fuga de datos: el atacante puede aprovechar operaciones de codificación base64 para ocultar instrucciones o datos maliciosos, provocando la fuga de información sensible
- Ejecución de código no autorizada: el código malicioso puede inyectarse en el LLM en forma de codificación base64, provocando la ejecución de código no autorizado, lo que puede dañar la integridad y seguridad del sistema
- Operación maliciosa: el atacante puede aprovechar la codificación base64 para manipular al LLM y ejecutar diversas operaciones maliciosas, como manipular datos o secuestrar sesiones, poniendo en peligro el sistema y la seguridad del usuario

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Validación de entrada/salida | Validar los datos de entrada y salida, para evitar que datos codificados en base64 u otro formato maliciosos o inesperados ingresen al LLM o sean impresos directamente |
| Alineación de seguridad del modelo | Entrenar al gran modelo con matices lingüísticos y técnicas de codificación, para identificar las características de estos ataques |

**Referencias**

https://promptengineering.org/mind-over-malware-battling-the-growing-arsenal-of-attacks-on-large-language-models/
https://www.toolify.ai/ai-news/the-future-of-hacking-5-terrifying-llm-security-threats-544868

---
### Ataque a la memoria de conversación de la aplicación

> Código de riesgo: GAARM.0040.003
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo se refiere a que el atacante puede, mediante inyección de prompt del lado web, engañar al LLM para que cree una memoria maliciosa (por ejemplo, una configuración de preferencia errónea entre el usuario y el modelo), modificando maliciosamente las preferencias del usuario en la memoria del LLM, logrando así manipular al LLM. Por ejemplo, el atacante puede engañar al LLM para que crea que la preferencia de chat del usuario es "responder a cada mensaje del usuario con 'Lo siento, no puedo responderte'", logrando así el efecto de un ataque de denegación de servicio (DoS).

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Este artículo describe cómo, mediante un ataque a la memoria de conversación de la aplicación, se provoca que el modelo rechace de forma continua al usuario |

**Riesgo del ataque**

- Ataque de denegación de servicio (DoS): el atacante puede, según su preferencia, someter al usuario a un ataque de memoria de denegación de servicio continua

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Desactivar la función de memoria histórica | Desactivar la función de memoria (Memory) del modelo LLM puede mitigar este problema |

**Referencias**

https://embracethered.com/blog/posts/2024/chatgpt-persistent-denial-of-service/
https://openai.com/index/memory-and-new-controls-for-chatgpt/

---
### Explotación de Agents en la aplicación

> Código de riesgo: GAARM.0041
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

La API de aplicaciones LLM se divide principalmente en dos categorías de escenarios de aplicación; por lo tanto, el riesgo de explotación de la API de aplicación se desarrolla principalmente en torno a los siguientes dos escenarios:

1. La plataforma de aplicaciones LLM proporciona capacidad de servicio al exterior basándose en una API.

El atacante aprovecha los riesgos de seguridad de API presentes en la interfaz API de un gran modelo (como la serie GPT de OpenAI) para llevar a cabo el proceso de ataque, recopilando información de la interfaz API para buscar vulnerabilidades, y construyendo solicitudes API maliciosas basadas en las vulnerabilidades encontradas, intentando eludir la autenticación o inyectar código malicioso. Por ejemplo: acceder o ejecutar operaciones de mayor privilegio de forma no autorizada, o ejecutar comandos de código malicioso aprovechando vulnerabilidades de la interfaz API que se ofrece al exterior.

2. La orquestación de Agents del LLM y la integración de aplicaciones de terceros implementan el acceso de capacidades relacionadas al modelo basándose en una API.

El atacante aprovecha la capacidad de acceso a API del modelo para acceder a información sensible u operaciones, y basándose en el permiso de acceso a la API, mediante la construcción indirecta de un prompt malicioso, hace que el modelo ejecute operaciones peligrosas, como acceder a información sensible o alterar la configuración del sistema. Dado que el propio modelo posee la capacidad de operar e invocar la API, con el permiso de acceso correspondiente, la operación maliciosa puede eludir el control de seguridad normal, lanzando un ataque malicioso real; este ataque puede provocar riesgos como el acceso indebido y el acceso no autorizado a información de terceros.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Una cuenta de usuario común originalmente solo podía usar el modelo GPT-3.5, pero mediante una dirección API específica, el atacante logró acceder sin autorización al modelo GPT-4 |
| Caso 2 | El atacante usa la API para ejecutar directamente comandos en el sistema, eliminando archivos |
| Caso 3 | Se construyen diversos escenarios de aplicación de API de LLM, aprovechando maliciosamente la funcionalidad de la API basada en el LLM para lograr ejecución de comandos, eliminación de cuentas y otros comportamientos de ataque |
| Caso 4 | Stable Diffusion proporciona una interfaz API que permite a los desarrolladores invocar el modelo de forma programática para generar imágenes. El atacante aprovecha esto, construyendo prompts de texto maliciosos, y mediante la interfaz API de Stable Diffusion, hace que el modelo genere contenido de imágenes ilegal o extremista |

**Riesgo del ataque**

- Fuga de datos: el atacante puede obtener datos sensibles, como información de usuario y contraseñas
- Interrupción del servicio: una operación maliciosa puede provocar la interrupción del servicio, como la eliminación de registros de usuario o entradas de base de datos
- Disminución de la confianza: información imprecisa o sensible generada por el LLM puede dañar la confianza del usuario y de la organización
- Responsabilidad legal: debido a contenido inapropiado generado por el LLM, la organización puede enfrentar responsabilidad legal

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Control de orquestación de la API del LLM | Restringir las API y los datos a los que el LLM puede acceder, minimizando así el daño potencial en caso de explotación |
| Validación de entrada/salida | Depurar cuidadosamente la entrada del usuario, para evitar que se inyecten prompts maliciosos en el LLM |
| Monitoreo y registro | Registrar todas las operaciones ejecutadas mediante el LLM, y monitorearlas en tiempo real, para detectar y responder rápidamente ante actividades sospechosas |
| Aprobación con intervención humana | Otorgar al usuario más control, permitiéndole gestionar el uso de plugins y el flujo de datos |

**Referencias**

https://portswigger.net/web-security/llm-attacks

---
### Inyección de interferencia en la cadena de pensamiento

> Código de riesgo: GAARM.0042.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo es un sub-riesgo del ataque de inyección en CoT; el atacante, observando el proceso de orquestación de CoT, construye una entrada maliciosa, engañando así al modelo haciéndole creer que ya ha obtenido el resultado correcto de un agent, interfiriendo en CoT mediante la falsificación del resultado del agent.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Este caso muestra la interferencia sobre CoT, engañando al modelo mediante la construcción de la entrada, con el fin de lograr un objetivo ilegítimo |

**Riesgo del ataque**

- Inyección de interferencia: mediante la construcción de una entrada maliciosa, se logra interferir con el LLM, y así ejecutar operaciones que violan las reglas

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Control estricto de permisos | Garantizar que el LLM solo pueda acceder al contenido básico, minimizando los posibles puntos de infracción |
| Añadir supervisión humana | Añadir una capa de verificación, como salvaguarda frente a comportamientos inesperados del LLM |
| Establecer límites de confianza claros | Tratar al LLM como no confiable, manteniendo siempre un control externo en la toma de decisiones, y permaneciendo alerta ante posibles respuestas no confiables del LLM |

**Referencias**

https://labs.withsecure.com/publications/llm-agent-prompt-injection

---
### Inyección de manipulación en la cadena de pensamiento

> Código de riesgo: GAARM.0042.002
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo es un sub-riesgo del ataque de inyección en CoT; el atacante, observando el proceso de orquestación de CoT, construye una entrada maliciosa, haciendo que el modelo omita el proceso de CoT preestablecido y despache directamente un Agent sensible. Por ejemplo, se omite el paso de verificación preestablecido, permitiendo que el usuario ejecute directamente una operación que en principio debería requerir verificación previa.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Este caso muestra la manipulación directa sobre CoT, engañando al modelo mediante la construcción de la entrada, haciendo que omita un paso de verificación que debía ejecutarse, reembolsando al usuario una suma elevada sin revisión |
| Caso 2 | El atacante, combinando múltiples técnicas de ataque adversarial, tras eludir las reglas de prompt previas mediante un ataque de evasión de rol, usa la inyección de manipulación de CoT para invocar exitosamente la función approveTransfer y completar una operación de transferencia |

**Riesgo del ataque**

- Inyección de manipulación: mediante la construcción de una entrada maliciosa, se logra manipular al LLM, y así ejecutar operaciones que violan las reglas

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Control estricto de permisos | Garantizar que el LLM solo pueda acceder al contenido básico, minimizando los posibles puntos de infracción |
| Añadir supervisión humana | Añadir una capa de verificación, como salvaguarda frente a comportamientos inesperados del LLM |
| Establecer límites de confianza claros | Tratar al LLM como no confiable, manteniendo siempre un control externo en la toma de decisiones, y permaneciendo alerta ante posibles respuestas no confiables del LLM |

**Referencias**

https://labs.withsecure.com/publications/llm-agent-prompt-injection

---
### Ataque de inyección de consultas

> Código de riesgo: GAARM.0056.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo es una sub-técnica del ataque de inyección en CoT; el ataque de inyección de consultas se usa principalmente para aprovechar el Agent de consulta de datos bajo una aplicación CoT, logrando la fuga de datos arbitrarios. En una aplicación CoT, el usuario proporciona una pregunta en lenguaje natural, y el modelo de IA genera una serie de pasos de razonamiento para responderla. El atacante puede inyectar código SQL malicioso en la pregunta, intentando eludir la verificación de seguridad del modelo, accediendo directamente a la base de datos backend. Cuando la aplicación de la cadena de pensamiento CoT se conecta externamente a una base de datos tradicional, base de datos vectorial, grafo de conocimiento u otra base de datos externa, se requiere un Agent para realizar la consulta y obtención de datos externos; el atacante puede, interfiriendo o manipulando el proceso CoT, por ejemplo, al consultar datos externos, hacer que se trate erróneamente la sentencia proporcionada por el usuario como dato externo, provocando que se consulten y obtengan datos arbitrarios.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Reto CTF de código abierto sobre ataque de inyección de consultas bajo el framework ReAct |

**Riesgo del ataque**

En aplicaciones LLM que usan sistemas de recuperación de información, el atacante puede contaminar la base de datos de recuperación de información, haciendo que se inyecten fragmentos de texto maliciosos en la consulta enviada al LLM, afectando así el resultado final de salida, y provocando una serie de riesgos como violación de la privacidad del usuario y ejecución de código malicioso.

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Control estricto de permisos | Aplicar un control de privilegios estricto, garantizando que el LLM solo pueda acceder al contenido y los Agents necesarios, minimizando así los posibles puntos de vulnerabilidad |
| Control de orquestación de Agents del LLM | Implementar un mecanismo externo estricto de verificación de permisos automática o manual para los Agents de operaciones sensibles, evitando que el LLM posea directamente los permisos de uso correspondientes |
| Refuerzo del contenido del prompt | Adoptar soluciones como el ChatML (OpenAI Chat Markup Language) para intentar aislar el prompt real del usuario de otro contenido |

**Referencias**

http://youtube.com/watch?v=7ZA0Z1R-MjQ
http://youtube.com/watch?v=KksYizcLFH0

---
### Ataque de inyección de entorno

> Código de riesgo: GAARM.0047
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El ataque de inyección de entorno se refiere a que el atacante, mediante la técnica de inyección indirecta de prompt, incrusta instrucciones maliciosas en páginas web externas, interfaces, correos electrónicos u otros entornos; cuando el AI Agent procesa contenido externo, ejecuta las instrucciones incrustadas como si fueran instrucciones del usuario, provocando fuga de datos o logrando controlar el modelo o robar datos. El atacante puede, mediante la manipulación de variables de entorno, la modificación de bibliotecas de dependencias o la contaminación de archivos de configuración, inducir al modelo a generar una salida errónea, filtrar información sensible o ejecutar operaciones no autorizadas.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | El atacante crea un issue malicioso que contiene una inyección de prompt en un repositorio público; cuando el usuario envía una solicitud normal a Claude, la IA obtiene el issue del repositorio público, desencadenando la instrucción maliciosa, la cual extrae datos de un repositorio privado hacia el contexto, y crea un PR con datos privados en el repositorio público, provocando la fuga de datos |

**Riesgo del ataque**

El ataque de inyección de entorno puede constituir una amenaza grave para el ecosistema de desarrollo y despliegue de modelos. A continuación los principales riesgos:

- Generación de salida maliciosa: el atacante puede, mediante la inyección de entorno, inducir al modelo a generar información falsa o contenido dañino, engañando al usuario o generando una crisis de confianza
- Fuga de datos: mediante la manipulación de la configuración del entorno, el atacante puede obtener información sensible, como conjuntos de datos de entrenamiento, prompts del usuario o claves de API
- Destrucción de la integridad del sistema: la inyección maliciosa puede provocar el daño del entorno de desarrollo, afectando la estabilidad del entrenamiento o despliegue del modelo, e incluso implantar programas de puerta trasera
- Ataque a la cadena de suministro: el atacante, contaminando bibliotecas de dependencias de terceros o cadenas de herramientas, afecta a múltiples proyectos de desarrollo de modelos, causando riesgos de seguridad generalizados
- Crisis de confianza: un ataque exitoso puede debilitar la confianza del usuario en el modelo y su entorno de desarrollo, limitando su aplicación en escenarios de alta seguridad

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Validación de la configuración del entorno | Validar estrictamente todas las variables de entorno, archivos de configuración y bibliotecas de dependencias, usando verificación de hash para garantizar su integridad, evitando modificaciones no autorizadas |
| Gestión de dependencias | Usar fuentes de dependencias confiables (como el espejo oficial de PyPI), y verificar periódicamente la versión y la firma de los paquetes de dependencias, previniendo ataques a la cadena de suministro |
| Aislamiento de entornos | Aislar completamente los entornos de desarrollo, pruebas y producción, restringiendo el acceso de entradas externas al entorno central, reduciendo la superficie de ataque |
| Monitoreo y auditoría de seguridad | Implementar monitoreo en tiempo real, registrar logs de cambios de configuración de entorno y dependencias, realizar auditorías de seguridad periódicas, detectando posibles comportamientos de inyección |
| Principio de mínimo privilegio | Aplicar un control de mínimo privilegio sobre el acceso a la API y las operaciones de archivos en el entorno, usando firmas de cifrado para verificar el origen de la configuración, previniendo manipulaciones maliciosas |

**Referencias**

https://mp.weixin.qq.com/s/9JwADiu9t3kqcfqnRMC2zQ
https://finance.sina.com.cn/tech/digi/2025-06-01/doc-ineypqvh0855918.shtml
https://zhuanlan.zhihu.com/p/1900540531131523166

---
### Gusano de Agents en bucle

> Código de riesgo: GAARM.0040.002
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Un Agent tiene la capacidad de obtener información en tiempo real desde fuentes externas como internet, y de entregar esta información al gran modelo para su procesamiento, devolviéndola finalmente al usuario. Sin embargo, el atacante puede aprovechar esto, inyectando información maliciosa mediante una fuente de datos externa, interfiriendo con la ejecución del Agent, y afectando así la salida del gran modelo. Estos prompts maliciosos pueden afectar indirectamente a múltiples aplicaciones de grandes modelos (LLM), formando un círculo vicioso que hace que la información maliciosa se propague rápidamente. A través del ciclo de entrada-salida del Agent, este gusano de Agents en bucle puede provocar un comportamiento malicioso autorreplicante y propagable, pudiendo finalmente provocar fuga de privacidad, e incluso generar riesgos de seguridad como el abuso de datos.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Investigadores crearon un gusano de IA llamado Morris II, capaz de atacar un asistente de correo electrónico de IA generativa, robando datos de correos electrónicos y enviando spam, mientras evadía algunas de las protecciones de seguridad de ChatGPT y Gemini |

**Riesgo del ataque**

- Fuga de datos: el gusano de IA puede robar información personal sensible, como nombre, número de teléfono, número de tarjeta de crédito, número de identificación, etc.
- Despliegue de malware: el gusano puede desplegar malware en el sistema infectado, provocando problemas de seguridad adicionales
- Elusión de la protección de seguridad: el gusano de IA puede eludir algunas de las medidas de protección de seguridad existentes, como los mecanismos de seguridad de ChatGPT y Gemini
- Nuevo tipo de ciberataque: el gusano de IA representa una forma de ciberataque previamente poco reconocida, planteando un desafío para las medidas de protección de seguridad existentes

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Validación de entrada/salida | Aplicar medidas estrictas de validación a los datos que ingresan al Agent para su procesamiento y orquestación |
| Diseño seguro de Agents de LLM | Adoptar medidas de seguridad tradicionales, como garantizar el diseño seguro de la aplicación del Agent, y monitorear posibles vulnerabilidades de seguridad |
| Aprobación con intervención humana | Mantener al humano en el bucle, garantizando que el Agent LLM requiera aprobación humana antes de ejecutar una operación, evitando que el sistema de IA envíe correos electrónicos u otras acciones de riesgo de forma autónoma |

**Referencias**

https://mp.weixin.qq.com/s/2bm7nuXkORLZ20mfpOmwrA

---
### Inyección indirecta de prompt

> Código de riesgo: GAARM.0040
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

En el proceso de procesamiento del lenguaje natural, el LLM presenta una vulnerabilidad frente a la inyección maliciosa de prompts. El atacante oculta el prompt en diversos datos que el sistema LLM procesará, como texto, contenido multimedia, información extraída de bases de datos o sitios web, manipulando así al LLM mediante el prompt para que produzca una respuesta dañina, como la ejecución de código malicioso o la fuga de información sensible. Por ejemplo, se escribe código malicioso en un archivo subido al LLM; cuando el LLM procesa los datos del archivo, ejecuta el código malicioso, provocando el daño.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | El atacante implanta código de inyección en un sitio web visitado por el usuario, haciendo que Bing Chat, sin que el usuario lo sepa, busque y exfiltre información personal |
| Caso 2 | El atacante controla los datos recuperados por un plugin del LLM, aprovechando el mecanismo de renderizado de imágenes Markdown, para enviar el historial de chat como parámetro de consulta al servidor del atacante |
| Caso 3 | Este caso muestra una técnica de ataque contra M365 Copilot: enviando un correo electrónico que contiene contenido malicioso, sin siquiera que el usuario abra el correo, se puede controlar remotamente a Copilot, provocando un ataque proveniente de un tercero |

**Riesgo del ataque**

- Ejecución de código malicioso: mediante la inyección de código o datos maliciosos, el atacante puede intentar establecer un punto de apoyo en el sistema, para controlarlo o dañarlo aún más
- Fuga de datos: el atacante puede usar la inyección indirecta para engañar al usuario, haciendo que ejecute una operación no prevista o filtre información sensible

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Validación de entrada | Validar y depurar estrictamente todos los datos de entrada, para eliminar o corregir cualquier contenido de inyección sospechoso |
| Principio de mínimo privilegio | Garantizar un sandboxing adecuado y restringir las capacidades del LLM, limitando que mecanismos como plugins o Agents obtengan información de fuentes no confiables |
| Aprobación con intervención humana | Otorgar al usuario más control, permitiéndole gestionar el uso de plugins y el flujo de datos |

**Referencias**

https://atlas.mitre.org/techniques/AML.T0051.001
https://twitter.com/random_walker/status/1636923058370891778
https://medium.com/@harry.hphu/introduction-to-web-llm-attacks-indirect-prompt-injection-7bb9f154bc07
https://medium.com/@dinob5551/indirect-prompt-injection-the-hidden-threat-lurking-in-ai-730b009dd5fb

---
### Ejecución de código no prevista

> Código de riesgo: GAARM.0060
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

La ejecución de código no prevista se refiere a que, durante la ejecución de una tarea, un agente ejecuta operaciones de código fuera del alcance previsto o no autorizadas, debido a inyección de prompt, mal uso de herramientas o defectos de lógica. El núcleo de este riesgo radica en que el agente carece de un control eficaz sobre los límites de la ejecución de código; mediante generación dinámica de código, invocación de la cadena de herramientas o ejecución de scripts, puede ejecutar código malicioso, peligroso o no previsto, provocando consecuencias graves como la intrusión del sistema, la manipulación de datos, la fuga de información sensible o la interrupción del servicio.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | La vulnerabilidad se origina en que un nodo de formulario no valida el Content-Type al procesarlo, lo que permite al atacante especificar la ruta de un archivo local sensible arbitrario, logrando finalmente, mediante la fuga de información, falsificar una identidad de administrador y ejecutar comandos maliciosos de flujo de trabajo |
| Caso 2 | Este caso muestra cómo un equipo rojo de IA, mediante inyección de prompt, induce a un modelo multimodal con capacidad de operación de escritorio a descargar y ejecutar un programa malicioso, estableciendo finalmente un canal de comunicación C2, logrando así la ejecución de código no prevista y el control remoto, convirtiendo el sistema anfitrión en una "máquina zombi" |
| Caso 3 | Este caso muestra cómo, mediante inyección de prompt, se manipula el mecanismo de memoria a largo plazo (Memory) de ChatGPT, implantando una lógica de instrucciones encubiertas definida por el atacante, haciendo que el modelo, en conversaciones posteriores, se comunique de forma continua con un C2 remoto y ejecute instrucciones, formando un "control zombificado" a nivel de modelo y una ejecución de comportamiento no prevista |

**Riesgo del ataque**

- Intrusión al sistema: la ejecución de código malicioso provoca el control total del sistema
- Destrucción de datos: la ejecución de operaciones destructivas provoca la pérdida o manipulación de datos
- Escalada de privilegios: mediante la ejecución de código se obtienen privilegios de sistema más elevados
- Implantación de puerta trasera: se implanta una puerta trasera persistente en el sistema
- Interrupción del servicio: la ejecución de código malicioso provoca la indisponibilidad del servicio
- Penetración lateral: se aprovecha la ejecución de código para atacar otros sistemas

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Sandbox de ejecución de código | Restringir la ejecución de código a un entorno aislado seguro, usar contenedores o máquinas virtuales para el aislamiento, limitar el acceso al sistema de archivos, la red y las llamadas al sistema |
| Revisión y validación de código | Implementar análisis estático de seguridad del código, establecer una base de reglas de seguridad de código, detectar dinámicamente patrones de código malicioso |
| Control de permisos | Aplicar el principio de mínimo privilegio, limitar el alcance de permisos de las herramientas de ejecución de código, establecer un mecanismo de aprobación para la ejecución de código |
| Filtrado y validación de entrada | Validar estrictamente la entrada de generación de código, filtrar funciones y operaciones peligrosas, detectar intenciones maliciosas potenciales |

**Referencias**

Vulnerabilidad de ejecución remota de código en n8n
ZombAIs: From Prompt Injection to C2 with Claude Computer Use
AI Domination: Remote Controlling ChatGPT ZombAI Instances

---
## Fase de despliegue

### Gestión inadecuada de la API de aplicaciones LLM

> Código de riesgo: GAARM.0049
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

La gestión inadecuada de la API de aplicaciones LLM se refiere a que, en el entorno del framework de integración de LLM, existen componentes API internos y externos de operaciones sensibles como Tools, Agents y Chains, que no cuentan con una gestión y configuración de entorno adecuada respecto del entorno del LLM. Dado que los modelos de lenguaje grande normalmente necesitan interactuar con diversas API para ejecutar tareas, si estas API no se gestionan adecuadamente, por ejemplo, sin establecer los permisos de acceso correctos o sin implementar controles de seguridad suficientes, el atacante puede aprovechar estas vulnerabilidades para obtener información sensible o realizar acciones maliciosas, logrando acceso no autorizado y explotación mediante ejecución de código.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Para la explotación de la API de LLM se presentan principalmente los siguientes dos casos |

**Riesgo del ataque**

- Fuga de datos: el atacante puede obtener datos sensibles, incluyendo información de identidad personal, secretos comerciales, etc.
- Interrupción del servicio: la ejecución de código malicioso o el acceso no autorizado pueden provocar la interrupción del servicio o la degradación del rendimiento
- Riesgo legal y de cumplimiento: las vulnerabilidades de seguridad pueden provocar litigios legales y problemas de cumplimiento

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Principio de mínimo privilegio | Seguir el principio de mínimo privilegio, proporcionando al LLM únicamente los permisos de acceso mínimos necesarios para completar su tarea, evitando una autorización de agencia excesiva |
| Validación de entrada/salida | Validar exhaustivamente toda la entrada enviada mediante la API, para prevenir ataques de inyección |
| Monitoreo y registro | Monitorear la nueva actividad de API en la era de la IA y registrar logs, para poder detectar y responder rápidamente ante comportamientos sospechosos |

---
### Envenenamiento del código fuente de aplicaciones LLM

> Código de riesgo: GAARM.0038
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

El código fuente puede presentar vulnerabilidades durante el proceso de revisión; el atacante, inyectando código malicioso en el código fuente de una aplicación de modelo de lenguaje grande (LLM), oculta el código mediante una vulnerabilidad para eludir la revisión, envenenando el código fuente de componentes de código abierto o comerciales de terceros, provocando problemas de seguridad en la aplicación durante el entrenamiento o la ejecución, afectando así a los fabricantes de desarrollo de negocios de aplicaciones de modelo descendentes que usan estos componentes.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | El atacante puede manipular el modelo subiendo código malicioso a un sitio de código abierto, afectando así ámbitos como la inversión, las transacciones y las noticias |

**Riesgo del ataque**

- Inserción de puerta trasera: mediante la inyección de código de puerta trasera en los datos de entrenamiento, se permite al atacante controlar o manipular la salida del modelo durante la inferencia, provocando acceso no autorizado o manipulación de datos
- Ataque a la cadena de suministro: mediante la inyección de código malicioso en código abierto, el atacante puede afectar a toda la cadena de suministro que usa ese código
- Propaganda de noticias falsas: el atacante puede aprovechar esta técnica para modificar contenido, como reseñas de películas o reportajes noticiosos, para difundir información falsa o propaganda

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Detectar cambios que se desvíen del código original | Identificar e interceptar comportamientos anómalos provocados por modificaciones de código malicioso |
| Validación y filtrado de entrada | Antes de que el código ingrese al modelo, realizar una validación y depuración estricta de la entrada |

**Referencias**

https://drive.google.com/file/d/1CTVcliUblX35cWfB49Xjhf8xk-fM3QH1/edit?pli=1

---
### Robo del código fuente de aplicaciones LLM

> Código de riesgo: GAARM.0037
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este riesgo se refiere a que el código fuente del modelo o de la aplicación del modelo de lenguaje grande (LLM) se almacena de forma inadecuada, o el entorno de despliegue presenta riesgos de seguridad, lo que puede permitir que personal no autorizado ataque el entorno de despliegue relacionado, logrando el robo del código fuente de la aplicación LLM, provocando un riesgo de deterioro de la ventaja competitiva tecnológica de la empresa.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Se filtró el modelo de lenguaje de 65 mil millones de parámetros de Meta |
| Caso 2 | Se filtró una gran cantidad de información sobre GPT-4 de OpenAI, incluyendo la arquitectura del modelo, el costo de entrenamiento y el conjunto de datos |

**Riesgo del ataque**

- Pérdida de la ventaja tecnológica: los competidores pueden copiar o modificar el código fuente filtrado, debilitando así la ventaja competitiva tecnológica de la empresa
- Amenaza a la ciberseguridad: el atacante puede aprovechar el código fuente filtrado para diseñar ciberataques dirigidos, por ejemplo, penetrando el sistema mediante vulnerabilidades reveladas
- Riesgo de correos de phishing: el código fuente filtrado puede usarse para crear correos de phishing más engañosos, que imitan las aplicaciones internas de la empresa, aumentando el riesgo de que los usuarios sean engañados

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Protección mediante cifrado de código | Usar algoritmos de cifrado robustos para cifrar el código fuente de la aplicación LLM, previniendo el acceso no autorizado y la fuga |
| Control de permisos de acceso | Restringir el acceso al código fuente de la aplicación LLM, garantizando que solo el personal autorizado pueda verlo o modificarlo |
| Monitoreo del modelo | Monitorear el uso del modelo, garantizando que no se use con fines maliciosos |

**Referencias**

https://analyticsindiamag.com/metas-llama-leaked-to-the-public-thanks-to-4chan/
https://knightcolumbia.org/blog/the-llama-is-out-of-the-bag-should-we-expect-a-tidal-wave-of-disinformation

---
## Fase de entrenamiento

### Manejo inseguro de salidas en aplicaciones LLM

> Código de riesgo: GAARM.0035.003
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este riesgo se refiere a un tipo de riesgo de seguridad que surge cuando un componente descendente recibe la salida de un modelo de lenguaje grande (LLM) sin realizar una revisión adecuada. Los componentes descendentes del modelo incluyen diversos Agents con distintas funciones; cuando falta el procesamiento de salida correspondiente, el atacante puede, mediante el abuso del Agent a través del modelo, lograr un comportamiento de ataque. Por ejemplo, el atacante puede, mediante la entrada de un texto específico, inducir al LLM a generar una respuesta que contenga información sensible, robando así datos del usuario, o generar directamente un payload de ataque no previsto, provocando vulnerabilidades descendentes como RCE o SSRF.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | CVE-2023-29374 es una vulnerabilidad de ejecución de código arbitrario de Langchain; los programas que usan la versión 0.0.131 o anterior de Langchain, e invocan la cadena LLMMathChain de Langchain, presentan un riesgo de seguridad que incluye la ejecución de comandos arbitrarios, lo que puede provocar la fuga de información sensible como claves de OpenAI, o el control del lado del servidor de Langchain |
| Caso 2 | Auto-GPT, en versiones anteriores a v0.4.3, presenta una vulnerabilidad de path traversal; esta vulnerabilidad provoca que se ejecute código arbitrario fuera del entorno docker en el host que ejecuta Auto-GPT. El atacante puede aprovechar esta vulnerabilidad para lanzar un ataque dirigido contra el objetivo, poniendo en peligro la seguridad del sistema del sitio |

**Riesgo del ataque**

- Fuga de información sensible: en ocasiones, el LLM no depura JavaScript en su respuesta. En este caso, el atacante puede usar un prompt cuidadosamente diseñado para hacer que el LLM devuelva un payload de JavaScript; cuando el navegador de la víctima analiza ese payload, sufre un ataque que provoca la fuga de información sensible, como la fuga del historial de conversación
- Ejecución de código arbitrario: el atacante puede ejecutar código arbitrario mediante la vulnerabilidad. Esto puede provocar que el atacante ejecute operaciones maliciosas en el servidor, como implantar una puerta trasera, extraer datos sensibles o interrumpir el servicio

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Framework de confianza cero | En este framework, cada solicitud de acceso a un recurso se trata como proveniente de una red no confiable; el sistema la revisa, autentica y verifica, aportando así seguridad al sistema |
| Entorno sandbox | Intentar usar un entorno sandbox para ejecutar el código, garantizando una mayor seguridad del sistema. Por ejemplo, ejecutar el código únicamente dentro de un contenedor Docker temporal dedicado puede limitar significativamente el impacto potencial del código malicioso |

**Referencias**

https://genai.owasp.org/wp-content/uploads/2024/05/OWASP-Top-10-for-LLM-Applications-v1_1_Chinese.pdf
https://cloud.baidu.com/article/3253170
https://www.akto.io/blog/insecure-output-handling-in-llms-insights
https://journal.hexmos.com/insecure-output-handling/
https://systemweakness.com/new-prompt-injection-attack-on-chatgpt-web-version-ef717492c5c2

---
### Riesgo de vulnerabilidades tradicionales en aplicaciones LLM

> Código de riesgo: GAARM.0035.002
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Las vulnerabilidades de seguridad de aplicaciones tradicionales no solo existen en sistemas de software tradicionales, sino que también pueden existir en aplicaciones LLM. Por ejemplo, ataques comunes a interfaces API, secuestro de cuentas, ejecución de código, entre otros; los riesgos y vulnerabilidades tradicionales aún existen en el LLM, por lo que durante la fase de entrenamiento se deben seguir estrictamente las mejores prácticas de seguridad, para garantizar que el sistema tenga suficiente capacidad de protección frente a estos riesgos tradicionales; de lo contrario, puede provocar una serie de peligros como interrupción del servicio, secuestro de cuentas y manipulación de datos.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Se reportó que ChatGPT presentó indicios de sufrir un ataque DDoS (denegación de servicio distribuida); un atacante externo intentó, mediante el envío repetido de solicitudes Ping, sobrecargar la red o el servidor hasta hacerlo colapsar |
| Caso 2 | La aplicación ChatGPT-Next-Web presenta una vulnerabilidad SSRF (CVE-2023-49785), que puede usarse para sondear recursos de la red interna |

**Riesgo del ataque**

- Interrupción del servicio: un ataque de denegación de servicio (DoS) o el agotamiento de recursos puede provocar que la aplicación LLM no pueda responder a las solicitudes de los usuarios, afectando la continuidad del negocio
- Control del sistema: una vulnerabilidad de ejecución remota de código o de ejecución de scripts puede permitir que el atacante tome control del servidor, implantando malware o ejecutando operaciones destructivas

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Reforzar la seguridad de la API | Garantizar que todas las interfaces API pasen por una autenticación y un control de autorización estrictos, restringiendo los permisos de acceso |
| Principio de mínimo privilegio | Restringir o deshabilitar funciones de ejecución de comandos innecesarias en la aplicación LLM, reduciendo la superficie de ataque potencial |
| Evaluación de seguridad periódica | Realizar periódicamente escaneos de vulnerabilidades de seguridad en la aplicación LLM, corrigiendo oportunamente los problemas de seguridad detectados |

**Referencias**

https://sec.cafe/handbook/security_research/ai_security/llm_security/attack/

---
### Plugins de LLM: manejo inseguro de entradas

> Código de riesgo: GAARM.0035.001
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este riesgo se refiere a que, debido a un manejo inseguro de entradas presente en los plugins del LLM, se introduce riesgo en el gran modelo. Por ejemplo, un plugin puede muy probablemente aceptar entrada de texto libre proveniente del modelo, sin validación ni verificación de tipo para manejar los límites del tamaño del contexto, lo que permite que un atacante potencial construya una solicitud maliciosa enviada al plugin, provocando diversos comportamientos indeseados, e incluso incluyendo ejecución remota de código.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Se descubrió que PALChain de LangChains presentaba un riesgo de ejecución de código |

**Riesgo del ataque**

- Ejecución de solicitudes no autorizadas: el atacante puede aprovechar directamente una vulnerabilidad de la aplicación LLM, o mediante la manipulación del prompt de entrada, hacer que la aplicación LLM ejecute una solicitud inesperada, accediendo u operando recursos restringidos
- Fuga de información sensible: el acceso a recursos restringidos mediante el LLM puede provocar la obtención y fuga no autorizada de información sensible

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Validación y filtrado de entrada | Implementar una estrategia estricta de validación y depuración de entrada, garantizando que todos los datos de entrada sean revisados y limpiados antes de ser procesados por el LLM |
| Principio de mínimo privilegio | Seguir el principio de mínimo privilegio, proporcionando al LLM únicamente los permisos de acceso mínimos necesarios para completar su tarea, evitando la autorización excesiva |

**Referencias**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/SSRF.html
https://www.horizon3.ai/attack-research/attack-blogs/nextchat-an-ai-chatbot-that-lets-you-talk-to-anyone-you-want-to/
https://genai.owasp.org/wp-content/uploads/2024/05/OWASP-Top-10-for-LLM-Applications-v1_1_Chinese.pdf

---
### Plugins de LLM: exceso de agencia de negocio

> Código de riesgo: GAARM.0036
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Los sistemas basados en LLM normalmente reciben del desarrollador cierto grado de capacidad de agencia de negocio, es decir, la capacidad de interactuar con otros sistemas y ejecutar operaciones al responder a un prompt. El exceso de agencia es un riesgo de seguridad de la fase de diseño y desarrollo; este riesgo provoca que, cuando el LLM produce una salida inesperada o ambigua, se ejecuten operaciones destructivas; la causa raíz suele ser: demasiadas funciones o demasiada autonomía. El exceso de agencia puede provocar una serie de impactos relacionados con la confidencialidad, la integridad y la disponibilidad, dependiendo de con qué sistemas pueda interactuar la aplicación LLM. Por ejemplo, se otorga al sistema LLM una autonomía excesiva, provocando que la aplicación o el plugin basados en el LLM no verifiquen ni aprueben de forma independiente operaciones de alto impacto, permitiendo que un plugin con capacidad de eliminar documentos de usuario ejecute la operación de eliminación sin ninguna confirmación del usuario.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Este video muestra cómo, aprovechando una vulnerabilidad de exceso de agencia, se puede realizar un restablecimiento ilegítimo de la contraseña del usuario |

**Riesgo del ataque**

- Fuga de información sensible: el exceso de agencia de negocio puede provocar que, cuando el LLM es manipulado maliciosamente, se filtre información sensible y privada

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Principio de mínimo privilegio | Restringir los plugins/herramientas que el agente LLM puede invocar, limitándolos únicamente a la funcionalidad mínima necesaria. Por ejemplo, si el sistema base del LLM no necesita la capacidad de obtener contenido de URL, no se le debería proporcionar al agente LLM un plugin de este tipo |
| Evitar funciones abiertas | En la medida de lo posible, evitar funciones abiertas (como ejecutar comandos de shell, obtener URL, etc.), y usar plugins/herramientas de funcionalidad más granular. Por ejemplo, una aplicación base de LLM puede necesitar escribir ciertas salidas en un archivo. Si se usa un plugin que ejecuta una función de shell para lograrlo, el alcance de las operaciones no deseadas sería muy amplio (podría ejecutar cualquier otro comando de shell). Una alternativa más segura es construir un plugin de escritura de archivos que solo admita una funcionalidad específica |

**Referencias**

https://genai.owasp.org/wp-content/uploads/2024/05/OWASP-Top-10-for-LLM-Applications-v1_1_Chinese.pdf

---
### Vulnerabilidades del framework de desarrollo RAG

> Código de riesgo: GAARM.0034.002
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

RAG (Retrieval-Augmented Generation, generación aumentada por recuperación) es un framework que combina la recuperación de información con la generación, usado en el desarrollo de modelos de lenguaje grande (LLM) para reforzar la capacidad de generación del modelo. Dado que el framework RAG depende de un módulo de recuperación para obtener información de fuentes de datos externas, si los datos de origen del módulo de recuperación son imprecisos o poco confiables, la respuesta generada puede contener información errónea o engañosa; además, los diversos Agents introducidos por el propio framework también pueden presentar riesgos de seguridad relacionados. Los riesgos de seguridad relacionados con el framework RAG se concentran principalmente en su módulo de generación, módulo de recuperación de información, plugins integrados e interfaces externas; debido a un diseño inseguro de RAG, es posible que se introduzcan vulnerabilidades de seguridad en la aplicación LLM. Por ejemplo, si el diseño del módulo de recuperación de RAG permite que el servidor inicie solicitudes sin restricciones, esto puede provocar la explotación de una vulnerabilidad SSRF.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Debido a las vulnerabilidades SSRF y de RCE de PALChain presentes en el framework LangChain, se generan riesgos de seguridad para las aplicaciones LLM que usan este framework |

**Riesgo del ataque**

- Fuga de información: el atacante puede, mediante una vulnerabilidad de path traversal, acceder a archivos sensibles o archivos de configuración del sistema, filtrando información interna del sistema
- Control del sistema: si los archivos del sistema contienen información de configuración sensible o scripts, el atacante puede aprovechar aún más esta información para controlar el sistema
- Ejecución de comandos: Agents del framework como la evaluación de expresiones de datos o el intérprete de Python pueden ser explotados para causar un ataque RCE

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Validación de entrada | Validar y depurar estrictamente toda la entrada del usuario, previniendo ataques de path traversal |
| Gestión de permisos | Establecer permisos de archivo adecuados, previniendo el acceso no autorizado a archivos |
| Actualización y corrección | Garantizar que la aplicación y sus dependencias relacionadas estén en la versión más reciente, aplicando oportunamente los parches de seguridad para corregir vulnerabilidades conocidas |

**Referencias**

https://www.wehelpwin.com/article/5063
https://medium.com/nfactor-technologies/rag-poisoning-an-emerging-threat-in-ai-systems-660f9ff279f9
https://ironcorelabs.com/security-risks-rag/

---
### Prácticas de código inseguras

> Código de riesgo: GAARM.0035
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Las prácticas de código inseguras se refieren a problemas de seguridad provocados por defectos de diseño durante el proceso de desarrollo de aplicaciones LLM basadas en un framework de integración de grandes modelos. La lógica de código adoptada durante el desarrollo de la aplicación LLM puede traer riesgos de seguridad, introduciendo vulnerabilidades de seguridad explotables en la aplicación LLM. Las vulnerabilidades de seguridad relacionadas pueden incluir dos categorías principales:

- El servicio de la aplicación LLM presenta vulnerabilidades tradicionales, por ejemplo, un sistema de chat de servicio al exterior presenta el riesgo de que se puedan ver registros de conversación de otros usuarios sin autorización
- Las nuevas Tools, Agents y Chains del framework de integración de LLM contienen riesgos de seguridad, permitiendo que el atacante, basándose en el LLM, explote indirectamente las vulnerabilidades relacionadas

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Se descubrió que PALChain de LangChains presentaba un riesgo de ejecución de código |
| Caso 2 | Se descubrieron múltiples vulnerabilidades RCE de alto riesgo en LangChains |

**Riesgo del ataque**

- Prácticas de codificación inseguras: el LLM puede seguir prácticas de codificación inseguras al generar código, provocando que el código generado contenga vulnerabilidades de seguridad
- Ejecución de solicitudes no autorizadas: el atacante puede aprovechar directamente una vulnerabilidad de la aplicación LLM, o mediante la manipulación del prompt de entrada, hacer que la aplicación LLM ejecute una solicitud inesperada, accediendo u operando recursos restringidos

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Detección y evaluación automatizada | Usar herramientas de análisis estático para detectar patrones inseguros en el código, mejorando la seguridad del código |
| Principio de mínimo privilegio | Seguir el principio de mínimo privilegio, proporcionando al LLM únicamente los permisos de acceso mínimos necesarios para completar su tarea, evitando una autorización de agencia excesiva |
| Validación y filtrado de entrada | Implementar una estrategia estricta de validación y depuración de entrada, garantizando que todos los datos de entrada sean revisados y limpiados antes de ser procesados por el LLM |

**Referencias**

https://arxiv.org/html/2312.04724v1

---
### Vulnerabilidades del componente de procesamiento de datos

> Código de riesgo: GAARM.0034.001
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

En el proceso de desarrollo de modelos de inteligencia artificial (IA), la seguridad del conjunto de datos es un aspecto que no debe pasarse por alto. En plataformas como Hugging Face o GitHub pueden existir conjuntos de datos con puertas traseras maliciosas, y estos conjuntos de datos pueden, mediante características o vulnerabilidades de los componentes de procesamiento de datos de LLM, constituir una amenaza a la seguridad del modelo de IA. Cuando el desarrollador usa estos conjuntos de datos contaminados para entrenar el modelo, el código malicioso oculto en el conjunto de datos puede ejecutarse, provocando una serie de problemas de seguridad, como la fuga o manipulación del modelo de IA, el conjunto de datos y el código.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | Se descubrió que el componente datasets de Hugging Face presentaba una característica insegura; al cargar un conjunto de datos malicioso usando este componente, puede provocar riesgos como la ejecución de comandos |

**Riesgo del ataque**

- Intrusión al sistema: un script malicioso construido por el atacante puede conectarse a un servidor del atacante, ejecutando comandos del sistema, tomando así control del servidor de la víctima
- Fuga de datos: un script malicioso puede robar datos de entrenamiento, código del modelo y otra información sensible en el servidor, provocando la fuga de propiedad intelectual y de la privacidad del usuario
- Manipulación de los parámetros del modelo: los parámetros del gran modelo pueden ser manipulados maliciosamente, afectando la precisión y confiabilidad del modelo

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Fuentes confiables de conjuntos de datos de entrenamiento/ajuste fino | Garantizar que el conjunto de datos de origen sea confiable, verificar si existe código Python malicioso en los scripts del conjunto de datos, y usar con precaución conjuntos de datos que Hugging Face haya marcado con riesgo de seguridad |
| Protección de la cadena de suministro de componentes de grandes modelos | Dar seguimiento continuo a las últimas dinámicas y recomendaciones de seguridad de la cadena de suministro en ámbitos como la seguridad nativa de grandes modelos, la seguridad base y la seguridad de desarrollo potenciada por grandes modelos |

**Referencias**

https://security.tencent.com/index.php/blog/msg/209

---
### Vulnerabilidades de componentes de terceros

> Código de riesgo: GAARM.0034
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este ataque se refiere a que, durante la fase de entrenamiento del modelo, el desarrollador de la aplicación LLM puede usar bibliotecas o componentes comerciales o de código abierto de terceros; estos componentes de terceros pueden contener código malicioso, vulnerabilidades de componentes, etc., lo que puede provocar la intrusión de la máquina de desarrollo o el servidor, constituyendo un riesgo de seguridad de la cadena de suministro en el entorno de IA.

**Caso de ataque**

| Caso | Descripción |
|---|---|
| Caso 1 | El cliente Python de la base de datos Redis, redis-py, usa una interfaz asíncrona; al cancelar un comando puede provocar una lectura desordenada de los datos de negocio del usuario (CVE-2023-28858) |
| Caso 2 | TorchServe puede provocar acceso no autorizado al servidor, y lograr ejecución remota de código en instancias vulnerables |
| Caso 3 | El componente datasets de Hugging Face presenta una vulnerabilidad que permite realizar ataques mediante conjuntos de datos maliciosos, lo que puede provocar la intrusión del dispositivo del usuario y el robo o manipulación de los parámetros del gran modelo |
| Caso 4 | Este artículo investiga el impacto de los ataques de puerta trasera sobre modelos preentrenados. El atacante puede, implantando una puerta trasera, manipular los resultados de recomendación del modelo, logrando así marketing malicioso u otros fines |
| Caso 5 | ChatGPT-Next-Web presenta vulnerabilidades de SSRF y XSS reflejado |

**Riesgo del ataque**

- Ataque de envenenamiento de puerta trasera en la cadena de suministro: cuando el desarrollador de IA usa una biblioteca de código abierto de terceros para cargar un conjunto de datos, si el conjunto de datos ha sido implantado con código malicioso, puede provocar que la PC o el servidor sufran un ataque
- Fuga o manipulación de parámetros del modelo: provoca que los parámetros del modelo sean robados o manipulados, afectando la seguridad y confiabilidad del modelo

**Mitigaciones**

| Mitigación | Descripción |
|---|---|
| Protección de la cadena de suministro de componentes de grandes modelos | Para vulnerabilidades de seguridad conocidas, como la CVE-2023-43654 de TorchServe, se debe actualizar oportunamente a una versión segura |
| Fuentes confiables de conjuntos de datos de entrenamiento/ajuste fino | Garantizar que el origen del conjunto de datos sea confiable, verificar si existe código Python malicioso en los scripts del conjunto de datos, evitando usar conjuntos de datos que Hugging Face haya marcado con riesgo de seguridad |
| Control estricto de la introducción de componentes de código abierto | Establecer un sistema interno de gobernanza de código abierto en la empresa, controlando estrictamente la introducción de componentes de código abierto, y logrando monitoreo y seguimiento automatizados mediante herramientas |

**Referencias**

https://hiddenlayer.com/research/insane-in-the-supply-chain/

---

---

## Sección 35: Riesgos de seguridad de vanguardia en AI Agent/MCP/Skills (2025-2026)

> El siguiente contenido se basa en investigaciones de seguridad recientes de 2025-2026, cubriendo el OWASP Agentic AI Top 10 (ASI01-ASI10).

### Seguridad del protocolo MCP (Model Context Protocol)

#### 11 categorías de riesgos emergentes de MCP (investigación de Checkmarx/Invariant Labs/Trail of Bits 2025)

| Tipo de riesgo | Descripción | Escenario de ataque |
|----------|------|----------|
| Envenenamiento de la descripción de herramientas | Se incrusta una instrucción maliciosa oculta en la descripción de la herramienta (tool description) | El modelo, al ejecutar la herramienta, lee y sigue el prompt oculto en la descripción |
| Estafa de alfombra roja (Rug Pull) | El servidor modifica dinámicamente la descripción de la herramienta tras la autorización del usuario | La revisión inicial pasa, pero la lógica funcional se altera posteriormente |
| Sobrescritura de instrucciones (Shadow Tool) | La descripción de una herramienta de un servidor malicioso secuestra el comportamiento de una herramienta confiable | Se modifica el destinatario de una herramienta de envío de correo hacia el atacante |
| Instrucciones ocultas ANSI/Unicode | Se aprovechan códigos de escape de terminal o caracteres Unicode invisibles para ocultar instrucciones | Ataque a la cadena de suministro: el modelo sugiere descargar un paquete malicioso |
| Ataque entre servidores | Conflicto y secuestro de definiciones de herramientas entre múltiples MCP Server | El Servidor A redefine el nombre de una herramienta del Servidor B |
| Robo de Token/credenciales | Se extraen los tokens OAuth y claves de API almacenados por el MCP Server | Un único punto de compromiso permite obtener las credenciales de todos los servicios conectados |
| Suplantación de servidor | Un MCP Server malicioso se hace pasar por un servicio legítimo, registrando todas las consultas | Robo de datos y monitoreo de comportamiento |
| Manipulación de esquema (Schema) | Se modifica dinámicamente el esquema de entrada/salida de la herramienta para eludir la validación | Se inyectan parámetros adicionales o se modifican los valores de retorno |
| Inyección de comandos | Se inyectan comandos del sistema operativo mediante parámetros de la herramienta | El MCP Server ejecuta comandos de shell sin filtrar |
| Desbordamiento de contexto | Se construye una respuesta de herramienta extremadamente grande para agotar la ventana de contexto del modelo | Se desplazan las instrucciones de seguridad, reduciendo la capacidad de juicio del modelo |
| Envenenamiento persistente | Se contamina el historial de la conversación mediante el valor de retorno de una herramienta | Afecta a largo plazo la seguridad de todas las interacciones posteriores |

#### Métodos de prueba de seguridad de MCP

1. **Auditoría de la descripción de herramientas**: revisar si el campo description de todas las herramientas registradas contiene instrucciones ocultas (códigos ANSI/Unicode/comentarios HTML)
2. **Monitoreo dinámico de comportamiento**: comparar si la descripción de la herramienta al registrarse inicialmente coincide con la del tiempo de ejecución
3. **Aislamiento entre servidores**: verificar si los nombres de herramientas entran en conflicto en un entorno con múltiples servidores
4. **Auditoría de almacenamiento de credenciales**: verificar la forma de almacenamiento del Token OAuth/clave API (texto plano vs. cifrado)
5. **Prueba de validación de entrada**: realizar pruebas de inyección de comandos/SQL sobre los parámetros de la herramienta
6. **Prueba de límites de permisos**: verificar si la herramienta puede acceder a recursos fuera del alcance declarado

### Seguridad de AI Agent (complemento al OWASP ASI01-ASI10)

#### Caso práctico Clawdbot/Moltbot (enero de 2026)

Incidente de seguridad de AI Agent con más de 4500 instancias expuestas descubiertas a nivel mundial:
- **Causa raíz**: un error de configuración del proxy inverso provocó que la autenticación de localhost pasara automáticamente
- **Impacto**: se extrajeron claves de API, tokens de servicio y credenciales de sesión de WhatsApp
- **Lección**: el AI Agent concentra privilegios elevados como ejecución de shell, estado persistente e inicio autónomo de tareas; un único punto de exposición equivale a una toma de control total

#### Ataque de selección de herramientas del Agent (investigación CATS)

- El pool de herramientas, al ser un repositorio no controlado, permite que el atacante publique herramientas con metadatos engañosos
- Bajo ataque adversarial, la precisión de autenticación en la selección de herramientas del Agent cae más de un 60%
- Tras un ataque adversarial adaptativo, la precisión cae por debajo del 20%

#### ASI07: seguridad de la comunicación entre múltiples Agents

| Vector de ataque | Descripción |
|----------|------|
| Falsificación de mensajes | El Agent A se hace pasar por el Agent B para enviar instrucciones |
| Abuso de la transferencia de confianza | Un Agent de bajo privilegio aprovecha la relación de confianza de un Agent de alto privilegio |
| Secuestro de coordinación | Se manipula la asignación de tareas y la agregación de resultados entre Agents |
| Ataque de intermediario (man-in-the-middle) | Se intercepta y manipula la comunicación entre Agents |

#### ASI09: explotación de la confianza humano-máquina

- Dependencia excesiva: el usuario ejecuta directamente la salida de la IA sin verificarla
- Ingeniería social potenciada: el contenido de phishing generado por IA es más creíble
- Sesgo de confirmación: el usuario tiende a confiar en la salida de la IA que coincide con sus expectativas
- Sesgo de automatización: la mentalidad de "lo que dice la IA debe ser correcto"

#### ASI10: Agent malicioso o fuera de control

- El Agent, tras ser comprometido, opera fuera de los parámetros autorizados
- Desviación del objetivo dentro de la cadena de decisión autónoma
- Movimiento lateral: se infecta a otros Agents mediante la comunicación entre Agents

### Seguridad de la cadena de suministro de Skills/Rules

#### Superficie de ataque

Los sistemas de Skills y Rules de los asistentes de programación de IA (Claude Code/Cursor, etc.) introducen una nueva superficie de ataque a la cadena de suministro:

| Vector de ataque | Descripción | Impacto |
|----------|------|------|
| Inyección de skill malicioso | Se incrustan instrucciones de prompt maliciosas en un skill compartido por la comunidad | La IA ejecuta comandos ocultos (como exfiltración de datos) |
| Manipulación del archivo Rules | Se modifica .cursorrules/.claude/RULES.md mediante un PR | Control a largo plazo del comportamiento de la IA del desarrollador |
| Envenenamiento de SKILL.md | Se incrusta una inyección indirecta en un archivo reference referenciado por el skill | La IA ejecuta instrucciones maliciosas al leer el reference |
| Ataque a la cadena de dependencias | Se reemplaza el MCP Server externo del que depende el skill | Todos los usuarios de ese skill se ven afectados |
| Explotación de hooks de construcción (build) | Se desencadena una operación de construcción maliciosa mediante los scripts/ del skill | Ejecución de código, robo de claves |

#### CVE de Claude Code divulgadas (2025-2026)

| CVE | Severidad | Descripción |
|-----|--------|------|
| CVE-2025-54795 | Alta | El comando echo elude la aprobación del usuario y se ejecuta directamente |
| GHSA-qxfv-fcpc-w36x | Alta | Inyección de comando rg que elude el prompt de aprobación |
| - | Alta | Elusión de la validación del comando sed permitiendo escritura de archivos arbitraria |
| - | Alta | Es posible ejecutar comandos antes de que aparezca el diálogo de confianza inicial |
| - | Moderada | Una configuración de repositorio maliciosa provoca fuga de datos |

#### Recomendaciones de defensa

- **Auditoría de skills**: revisar el contenido de SKILL.md y de todos los archivos reference antes de instalar
- **Verificación de firma**: verificar el origen e integridad del skill (actualmente no existe un mecanismo oficial; debe hacerse manualmente)
- **Aislamiento de permisos**: restringir las herramientas y el alcance de archivos a los que el skill puede acceder
- **Protección de Rules**: incorporar .cursorrules y AGENTS.md al proceso de revisión de código
- **Lista blanca de MCP Server**: permitir la conexión únicamente a MCP Server confiables
- **Monitoreo de comportamiento**: registrar todos los logs de invocación de herramientas y operaciones de archivos del asistente de IA

### Framework integral de pruebas de seguridad para IA Agéntica

Basado en el OWASP ASI01-ASI10, un proceso de pruebas sistemático para aplicaciones de AI Agent:

1. **Enumeración de objetivos**: identificar todos los Agents, herramientas, MCP Server y canales de comunicación
2. **Pruebas de autenticación**: verificación de identidad del Agent, gestión de Tokens, límites de permisos (ASI03)
3. **Seguridad de herramientas**: auditoría de descripción, inyección de parámetros, exceso de privilegios (ASI02)
4. **Pruebas de inyección**: inyección de prompt directa/indirecta, inyección mediante valores de retorno de herramientas (ASI01)
5. **Auditoría de la cadena de suministro**: origen del MCP Server, integridad del skill, seguridad de dependencias (ASI04)
6. **Ejecución de código**: escape de sandbox, inyección de comandos, operaciones de archivos (ASI05)
7. **Seguridad de la memoria**: envenenamiento de contexto, ataques de persistencia, corrupción de estado (ASI06)
8. **Seguridad de la comunicación**: autenticación entre Agents, integridad de mensajes, transferencia de confianza (ASI07)
9. **Pruebas de cascada**: alcance de propagación de un fallo puntual, aislamiento de fallos (ASI08)
10. **Pruebas de confianza**: mecanismo de validación de salida, proceso de aprobación humana (ASI09)
11. **Pruebas de escape**: monitoreo de comportamiento del Agent, detección de anomalías, interruptor de apagado (Kill Switch) (ASI10)

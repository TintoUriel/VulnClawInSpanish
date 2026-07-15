# Seguridad de aplicaciones de IA - Fase de aplicación - Ataques a Agent y CoT

> Fuente: Comunidad de Seguridad de Grandes Modelos AISS NSFOCUS | Extraído de ai-app-app.md
> Categoría de riesgo: Agent/CoT (GAARM.0041.x Explotación de Agent y SSRF/RCE / 0042.x Inyección de CoT e interferencia de la cadena de pensamiento / 0047 Inyección de entorno / 0056.001 Inyección de consultas / 0060 Ejecución de código no prevista)

---

### Ataque de inyección de CoT

> Número de riesgo: GAARM.0042
> Ciclo de vida: Fase de aplicación

**Descripción del ataque**

CoT (Chain of Thought, cadena de pensamiento) mejora eficazmente la capacidad de razonamiento de los LLM al inducirlos a pensar en una serie de pasos clave para resolver un problema. Basándose en el marco técnico ReAct (Reason + Act) para implementar el razonamiento CoT, y aprovechando la programación de Agents para dotar a los LLM de capacidad de interacción con el mundo externo, es posible conectarse sin fisuras con diversos sistemas externos y ejecutar tareas complejas.
En las aplicaciones CoT, el usuario plantea una pregunta en lenguaje natural y el modelo de IA genera una serie de pasos de razonamiento para responderla, involucrando tres pasos centrales: Pensamiento (Thought), Acción (Act) y Observación (Obs). El modelo de IA repite este ciclo de tres pasos para completar el razonamiento y la resolución de diversos problemas complejos. Dado que todo el proceso es más abierto y flexible que la lógica de código tradicional, y carece de una estructura de control de flujo estricta, un atacante puede utilizar un ataque de inyección de CoT para eludir pasos de razonamiento específicos e inducir al modelo de IA a ejecutar acciones no previstas, como: riesgos de funciones de negocio (transferencias no autorizadas de fondos de un usuario, etc.) y riesgos de funciones técnicas (SSRF, RCE, etc.). Actualmente, existen principalmente dos enfoques para el ataque de inyección de CoT:

Inyección de interferencia de la cadena de pensamiento: mediante la observación del proceso de programación de CoT, se construye una entrada maliciosa para engañar al modelo haciéndole creer que ya ha obtenido el resultado de un Agent, falsificando dicho resultado para interferir en la ejecución del proceso CoT.
Inyección de manipulación de la cadena de pensamiento: mediante la observación del proceso de programación de CoT, se construye una entrada maliciosa de forma directa o mediante técnicas de ataque adversario, logrando manipular el proceso CoT para que el modelo omita el proceso CoT preestablecido y despache directamente un Agent sensible.

**Casos de ataque**

Caso
Descripción




Caso 1
Este caso propone, para aplicaciones de LLM basadas en el marco ReAct, cómo aprovechar el proceso de cadena de pensamiento CoT para lograr la explotación maliciosa de un Agent.


Caso 2
Esta investigación descubrió que, combinando prompts de jailbreak con prompts de CoT para eludir las restricciones éticas del LLM mediante CoT, es posible provocar que el modelo genere información privada.


Caso 3
Reto CTF de código abierto sobre ataques de inyección de consultas bajo el marco ReAct.

**Riesgos del ataque**

En aplicaciones de LLM que utilizan sistemas de recuperación de información, un atacante puede contaminar la base de datos de recuperación de información, de modo que se inyecten fragmentos de texto maliciosos en las consultas enviadas al LLM, afectando así el resultado final y provocando una serie de riesgos como la filtración de privacidad del usuario o la ejecución de código malicioso.
En aplicaciones de LLM de sistemas de negocio de reembolsos, un atacante puede interferir en el flujo CoT de reembolso para que pedidos que originalmente no cumplen las condiciones de reembolso puedan ser reembolsados con normalidad; o bien manipular directamente de forma maliciosa el Agent de la operación de reembolso, de modo que el monto real del reembolso no coincida con el monto esperado, causando pérdidas económicas a la empresa.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control estricto de permisos
Aplicar un control de privilegios estricto para garantizar que los LLM solo puedan acceder al contenido y a los Agents estrictamente necesarios, minimizando así los puntos de vulnerabilidad potenciales.


Control de programación de Agents de LLM
Implementar mecanismos externos estrictos de verificación de permisos, automáticos o manuales, para los Agents que realizan operaciones sensibles, evitando que el LLM posea directamente los permisos de uso correspondientes.


Refuerzo del contenido del prompt
Adoptar soluciones como el lenguaje de marcado de chat de OpenAI (ChatML) para intentar aislar el prompt real del usuario de otro contenido.

**Referencias**

http://youtube.com/watch?v=7ZA0Z1R-MjQ
http://youtube.com/watch?v=KksYizcLFH0

---
### Sondeo de simulación de entorno SSRF

> Número de riesgo: GAARM.0041.001
> Ciclo de vida: Fase de aplicación

**Descripción del ataque**

El SSRF se produce en la mayoría de los casos porque el servidor ofrece una función para obtener datos de otras aplicaciones de servidor sin filtrar ni restringir la dirección de destino. Si una aplicación de LLM presenta una vulnerabilidad SSRF, un atacante puede explotarla para iniciar solicitudes a la red interna y acceder a recursos restringidos dentro de la aplicación. Asimismo, algunos LLM pueden incorporar Agents con capacidad de acceso a la red, utilizados para ejecutar operaciones como consultas de información externa. Un atacante puede aprovechar una vulnerabilidad SSRF en la API de la aplicación de LLM o un Agent con capacidad de acceso a la red dentro del LLM para ejecutar solicitudes no previstas o acceder a recursos restringidos (como servicios internos, API o almacenamiento de datos), accediendo así a los sistemas internos del modelo y aumentando el riesgo de filtración de información del modelo, servicios internos y datos sensibles.

**Casos de ataque**

Caso
Descripción




Caso 1
La aplicación ChatGPT-Next-Web presenta una vulnerabilidad SSRF (CVE-2023-49785) que puede utilizarse para sondear recursos de la red interna.

**Riesgos del ataque**

Acceso a recursos internos: un atacante puede aprovechar la vulnerabilidad SSRF para enviar solicitudes y obtener información sensible de la red interna.
Proxy de tráfico de ataque: aprovechando la vulnerabilidad SSRF, el atacante puede enviar solicitudes maliciosas para atacar sistemas, servicios o recursos internos.
Filtración de datos: el atacante puede aprovechar este riesgo para obtener datos sensibles, como claves de acceso a plataformas en la nube.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control de programación de la API de LLM y aislamiento en sandbox
Implementar un mecanismo de sandbox adecuado para aislar el LLM y limitar su acceso a recursos de red, servicios internos y API. Mediante controles de acceso estrictos, las organizaciones pueden minimizar la posibilidad de interacciones no autorizadas y mitigar el impacto de las vulnerabilidades SSRF.


Evaluación y revisión de seguridad periódica de LLM
Realizar auditorías y revisiones periódicas de la configuración de seguridad de red y aplicaciones para identificar y corregir errores de configuración, garantizando que los recursos internos no queden expuestos de forma involuntaria al LLM, reforzando el sistema de seguridad general.


Validación de entrada/salida
Implementar técnicas robustas de validación y procesamiento de entradas para garantizar que los prompts se sometan a una revisión y filtrado exhaustivos, lo que ayuda a evitar que prompts maliciosos o involuntarios desencadenen solicitudes no autorizadas, reduciendo así el riesgo de ataques SSRF.


Monitoreo y registro
Implementar mecanismos integrales de monitoreo y registro para rastrear las interacciones del LLM. Mediante un seguimiento cercano de la actividad del LLM y el registro de información relevante, las organizaciones pueden detectar y analizar posibles vulnerabilidades SSRF, permitiendo una detección y corrección oportunas.

**Referencias**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/SSRF.html

---
### Inyección de ejecución de código

> Número de riesgo: GAARM.0041.002
> Ciclo de vida: Fase de aplicación

**Descripción del ataque**

Bajo el marco ReAct, los LLM pueden interactuar con sistemas externos; un Agent intérprete de código externo puede utilizarse para dotar al LLM de capacidad de ejecución de código, permitiendo completar necesidades como el trazado automático de gráficos o cálculos de código complejos durante los procesos de aplicación de negocio. Un atacante, mediante la construcción de prompts de entrada maliciosos, manipula al LLM para que ejecute un proceso de razonamiento predeterminado, haciendo que el LLM despache el Agent de ejecución de código para realizar código o comandos maliciosos en el sistema subyacente, logrando así atacar y explotar el entorno de ejecución base del LLM. Las causas principales de este ataque son:

No detectar ni validar ni limitar de forma efectiva la entrada del usuario, permitiendo que un atacante realice operaciones de ejecución de código malicioso sin autorización.
Un entorno de sandbox insuficiente o limitaciones insuficientes de las capacidades del LLM, lo que provoca que interactúe con el sistema subyacente de formas imprevistas.
Exponer de forma involuntaria funciones o interfaces a nivel de sistema al LLM.

**Casos de ataque**

Caso
Descripción




Caso 1
Tras el lanzamiento de una nueva función de GPT-4, se descubrió que su intérprete de código Python parecía tener una vulnerabilidad de escape de sandbox.

**Riesgos del ataque**

Riesgo de ejecución de código: el atacante puede ejecutar código Python arbitrario, lo que podría provocar el compromiso del servidor, filtración de datos u otras acciones maliciosas.
Control de permisos del sistema: si CodeExecutor no cuenta con las medidas de seguridad adecuadas, el código ejecutado, combinado con técnicas de escape de contenedor, podría obtener privilegios elevados del sistema.
Control de acceso persistente: el atacante puede aprovechar esta oportunidad para establecer un canal de acceso a largo plazo destinado a ataques continuos.

**Medidas de mitigación**

Medida de mitigación
Descripción




Validación de entrada
Implementar un proceso estricto de detección y limitación de entradas para evitar que el LLM procese prompts maliciosos o no intencionados.


Principio de mínimo privilegio
Garantizar un sandboxing adecuado y limitar las capacidades del LLM para restringir su capacidad de interacción con el sistema subyacente, evitando operaciones que puedan tener un impacto a nivel de sistema.


Monitoreo y registro
Registrar todas las operaciones ejecutadas a través del LLM y realizar un monitoreo en tiempo real para detectar y responder rápidamente ante actividades sospechosas.

**Referencias**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Unauthorized_Code_Execution.html
https://www.calvin-risk.com/blog/decoding-llm-risks-a-comprehensive-look-at-unauthorized-code-execution

---
### Explotación de Agent inteligente de la aplicación

> Número de riesgo: GAARM.0041
> Ciclo de vida: Fase de aplicación

**Descripción del ataque**

La API de aplicaciones de LLM se divide principalmente en dos categorías de escenarios de aplicación, por lo que el riesgo de explotación de la API de aplicación gira principalmente en torno a estos dos escenarios:


La plataforma de aplicación de LLM ofrece capacidad de servicio al exterior basada en API;

El atacante aprovecha los riesgos de seguridad de la API existentes en la interfaz API de un gran modelo (como la serie GPT de OpenAI) para llevar a cabo el proceso de ataque, recopilando información de la interfaz API en busca de vulnerabilidades, y construyendo solicitudes API maliciosas basadas en las vulnerabilidades descubiertas, en un intento de eludir la autenticación o inyectar código malicioso. Por ejemplo: acceder o ejecutar operaciones de mayor privilegio de forma no autorizada, o ejecutar comandos de código malicioso aprovechando vulnerabilidades de la interfaz API expuesta al exterior.



La programación de Agents de LLM y la integración de aplicaciones de terceros implementan las capacidades correspondientes en el modelo basándose en API;

El atacante aprovecha que el modelo tiene capacidad de acceso a API que manejan información sensible u operaciones, y a través del permiso de acceso a la API, construye de forma indirecta prompts maliciosos para hacer que el modelo ejecute operaciones peligrosas, como acceder a información sensible o alterar la configuración del sistema. Dado que el propio modelo posee capacidad de operación y llamada a la API con los permisos de acceso correspondientes, las operaciones maliciosas pueden eludir los controles de seguridad normales e iniciar un comportamiento de ataque malicioso real, lo que puede provocar riesgos como escalamiento de privilegios y acceso no autorizado a información de terceros.

**Casos de ataque**

Caso
Descripción




Caso 1
Una cuenta de usuario normal, que originalmente solo podía usar el modelo GPT-3.5, logró, mediante una dirección de API específica, que un atacante accediera sin autorización al modelo GPT-4.


Caso 2
El atacante usa la API para ejecutar comandos directamente en el sistema y eliminar archivos.


Caso 3
Se construyeron diversos escenarios de aplicación de API de LLM, basados en LLM, para explotar de forma maliciosa las funciones de la API y lograr comportamientos de ataque como ejecución de comandos y eliminación de cuentas.


Caso 4
Stable Diffusion ofrece una interfaz API que permite a los desarrolladores invocar el modelo de forma programática para generar imágenes. Un atacante aprovechó esto construyendo prompts de texto maliciosos y, mediante la interfaz API de Stable Diffusion, hizo que el modelo generara contenido de imágenes ilegal o extremista.

**Riesgos del ataque**

Filtración de datos: el atacante puede obtener datos sensibles, como información de usuarios y contraseñas.
Interrupción del servicio: las operaciones maliciosas pueden provocar la interrupción del servicio, como la eliminación de registros de usuario o entradas de base de datos.
Pérdida de confianza: información inexacta o sensible generada por el LLM puede dañar la confianza de los usuarios y la organización.
Responsabilidad legal: la organización puede enfrentar responsabilidad legal debido a contenido inapropiado generado por el LLM.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control de programación de la API de LLM
Limitar las API y los datos a los que puede acceder el LLM, para minimizar el posible daño en caso de explotación.


Validación de entrada/salida
Depurar cuidadosamente la entrada del usuario para evitar que se inyecten prompts maliciosos en el LLM.


Monitoreo y registro
Registrar todas las operaciones ejecutadas a través del LLM y realizar un monitoreo en tiempo real para detectar y responder rápidamente ante actividades sospechosas.


Aprobación con intervención humana
Otorgar a los usuarios mayor control, permitiéndoles gestionar el uso de plugins y el flujo de datos.

**Referencias**

https://portswigger.net/web-security/llm-attacks

---
### Inyección de interferencia de la cadena de pensamiento

> Número de riesgo: GAARM.0042.001
> Ciclo de vida: Fase de aplicación

**Descripción del ataque**

Este riesgo es un subriesgo del ataque de inyección de CoT. El atacante, mediante la observación del proceso de programación de CoT, construye una entrada maliciosa para engañar al modelo haciéndole creer que ya ha obtenido el resultado correcto de un agent, interfiriendo así en el CoT mediante la falsificación del resultado del agent.

**Casos de ataque**

Caso
Descripción




Caso 1
Este caso muestra una interferencia sobre el CoT mediante la construcción de una entrada que engaña al modelo para lograr un objetivo ilegítimo.

**Riesgos del ataque**

Inyección de interferencia: mediante la construcción de una entrada maliciosa, se logra interferir en el LLM y, con ello, realizar operaciones no autorizadas.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control estricto de permisos
Garantizar que el LLM solo pueda acceder al contenido básico, minimizando los puntos potenciales de infracción.


Incorporar supervisión humana
Añadir una capa de verificación como salvaguarda frente a comportamientos imprevistos del LLM.


Establecer límites de confianza claros
Tratar al LLM como no confiable, mantener siempre un control externo en la toma de decisiones y permanecer alerta ante respuestas del LLM potencialmente no confiables.

**Referencias**

https://labs.withsecure.com/publications/llm-agent-prompt-injection

---
### Inyección de manipulación de la cadena de pensamiento

> Número de riesgo: GAARM.0042.002
> Ciclo de vida: Fase de aplicación

**Descripción del ataque**

Este riesgo es un subriesgo del ataque de inyección de CoT. El atacante, mediante la observación del proceso de programación de CoT, construye una entrada maliciosa para hacer que el modelo omita el proceso CoT preestablecido y despache directamente un Agent sensible. Por ejemplo, omitir un paso de verificación preestablecido, permitiendo al usuario ejecutar directamente una operación que en teoría requiere verificación previa.

**Casos de ataque**

Caso
Descripción




Caso 1
Este caso muestra una manipulación directa del CoT, engañando al modelo mediante la construcción de una entrada para que omita un paso de verificación que en teoría debía realizarse, otorgando al usuario un reembolso de gran cuantía sin revisión.


Caso 2
El atacante, combinando múltiples técnicas de ataque adversario, eludió las reglas de prompt previas mediante un ataque de escape de rol, y luego utilizó la inyección de manipulación de CoT para invocar con éxito la función approveTransfer y completar una operación de transferencia.

**Riesgos del ataque**

Inyección de manipulación: mediante la construcción de una entrada maliciosa, se logra manipular al LLM y, con ello, realizar operaciones no autorizadas.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control estricto de permisos
Garantizar que el LLM solo pueda acceder al contenido básico, minimizando los puntos potenciales de infracción.


Incorporar supervisión humana
Añadir una capa de verificación como salvaguarda frente a comportamientos imprevistos del LLM.


Establecer límites de confianza claros
Tratar al LLM como no confiable, mantener siempre un control externo en la toma de decisiones y permanecer alerta ante respuestas del LLM potencialmente no confiables.

**Referencias**

https://labs.withsecure.com/publications/llm-agent-prompt-injection

---
### Ataque de inyección de consultas

> Número de riesgo: GAARM.0056.001
> Ciclo de vida: Fase de aplicación

**Descripción del ataque**

Este riesgo es una subtécnica dentro del ataque de inyección de CoT. El ataque de inyección de consultas se utiliza principalmente para explotar el Agent de consulta de datos en aplicaciones CoT y lograr la filtración de datos arbitrarios. En las aplicaciones CoT, el usuario plantea una pregunta en lenguaje natural y el modelo de IA genera una serie de pasos de razonamiento para responderla. Un atacante puede inyectar código SQL malicioso en la pregunta, intentando eludir las verificaciones de seguridad del modelo y acceder directamente a la base de datos backend. Cuando la aplicación de cadena de pensamiento CoT se conecta externamente a bases de datos tradicionales, bases de datos vectoriales, grafos de conocimiento u otras bases de datos externas, es necesario recurrir a un Agent para realizar la consulta y obtención de datos externos. El atacante puede, interfiriendo o manipulando el proceso CoT, por ejemplo al consultar datos externos, hacer que se trate erróneamente la sentencia proporcionada por el usuario como si fueran datos externos, provocando que se consulte y obtenga cualquier dato de forma arbitraria.

**Casos de ataque**

Caso
Descripción




Caso 1
Reto CTF de código abierto sobre ataques de inyección de consultas bajo el marco ReAct.

**Riesgos del ataque**

En aplicaciones de LLM que utilizan sistemas de recuperación de información, un atacante puede contaminar la base de datos de recuperación de información, de modo que se inyecten fragmentos de texto maliciosos en las consultas enviadas al LLM, afectando así el resultado final y provocando una serie de riesgos como la filtración de privacidad del usuario o la ejecución de código malicioso.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control estricto de permisos
Aplicar un control de privilegios estricto para garantizar que los LLM solo puedan acceder al contenido y a los Agents estrictamente necesarios, minimizando así los puntos de vulnerabilidad potenciales.


Control de programación de Agents de LLM
Implementar mecanismos externos estrictos de verificación de permisos, automáticos o manuales, para los Agents que realizan operaciones sensibles, evitando que el LLM posea directamente los permisos de uso correspondientes.


Refuerzo del contenido del prompt
Adoptar soluciones como el lenguaje de marcado de chat de OpenAI (ChatML) para intentar aislar el prompt real del usuario de otro contenido.

**Referencias**

http://youtube.com/watch?v=7ZA0Z1R-MjQ
http://youtube.com/watch?v=KksYizcLFH0

---
### Ataque de inyección de entorno

> Número de riesgo: GAARM.0047
> Ciclo de vida: Fase de aplicación

**Descripción del ataque**

El ataque de inyección de entorno se refiere a que el atacante, siguiendo el enfoque de un ataque de inyección indirecta de prompts, incrusta instrucciones maliciosas en entornos externos como páginas web, interfaces o correos electrónicos. Cuando el AI Agent procesa el contenido externo, ejecuta las instrucciones incrustadas como si fueran instrucciones del usuario, provocando filtración de datos o logrando el objetivo de controlar el modelo o robar datos. El atacante puede, mediante la manipulación de variables de entorno, la modificación de bibliotecas de dependencias o la contaminación de archivos de configuración, inducir al modelo a generar salidas erróneas, filtrar información sensible o ejecutar operaciones no autorizadas.

**Casos de ataque**

Caso
Descripción




Caso 1
Un atacante crea en un repositorio público un issue malicioso que contiene una inyección de prompt. Cuando un usuario envía una solicitud habitual a Claude, la IA obtiene el issue del repositorio público, lo que desencadena la instrucción maliciosa, provocando que se extraigan datos de un repositorio privado hacia el contexto y que se cree en el repositorio público un PR que contiene esos datos privados, resultando en una filtración de datos.

**Riesgos del ataque**

El ataque de inyección de entorno puede suponer una amenaza grave para el ecosistema de desarrollo y despliegue de modelos. Los principales riesgos son:

Generación de salida maliciosa: el atacante puede, mediante la inyección de entorno, inducir al modelo a generar información falsa o contenido dañino, engañando a los usuarios o provocando una crisis de confianza.
Filtración de datos: mediante la manipulación de la configuración del entorno, el atacante puede obtener información sensible, como conjuntos de datos de entrenamiento, prompts de usuarios o claves de API.
Deterioro de la integridad del sistema: la inyección maliciosa puede provocar que el entorno de desarrollo sea comprometido, afectando la estabilidad del entrenamiento o despliegue del modelo, e incluso implantando programas de puerta trasera.
Ataque a la cadena de suministro: el atacante, al contaminar bibliotecas de dependencias o cadenas de herramientas de terceros, puede afectar a múltiples proyectos de desarrollo de modelos, provocando riesgos de seguridad de amplio alcance.
Crisis de confianza: un ataque exitoso puede debilitar la confianza de los usuarios en el modelo y su entorno de desarrollo, limitando su aplicación en escenarios de alta seguridad.

**Medidas de mitigación**

Medida de mitigación
Descripción




Validación de la configuración del entorno
Validar rigurosamente todas las variables de entorno, archivos de configuración y bibliotecas de dependencias, utilizando verificación de hash para garantizar su integridad y evitar modificaciones no autorizadas.


Gestión de dependencias
Utilizar fuentes de dependencias confiables (como el espejo oficial de PyPI) y verificar periódicamente las versiones y firmas de los paquetes de dependencias, para prevenir ataques a la cadena de suministro.


Aislamiento de entornos
Aislar completamente los entornos de desarrollo, pruebas y producción, limitando el acceso de entradas externas al entorno central, reduciendo así la superficie de ataque.


Monitoreo y auditoría de seguridad
Implementar monitoreo en tiempo real, registrar los cambios en la configuración del entorno y las dependencias, y realizar auditorías de seguridad periódicas para detectar posibles comportamientos de inyección.


Principio de mínimo privilegio
Aplicar un control de mínimo privilegio sobre el acceso a la API y las operaciones de archivos en el entorno, usando firmas cifradas para verificar el origen de la configuración y prevenir alteraciones maliciosas.

**Referencias**

https://mp.weixin.qq.com/s/9JwADiu9t3kqcfqnRMC2zQ
https://finance.sina.com.cn/tech/digi/2025-06-01/doc-ineypqvh0855918.shtml
https://zhuanlan.zhihu.com/p/1900540531131523166

---
### Ejecución de código no prevista

> Número de riesgo: GAARM.0060
> Ciclo de vida: Fase de aplicación

**Descripción del ataque**

La ejecución de código no prevista se refiere a que, durante la ejecución de una tarea, el agente inteligente lleva a cabo operaciones de código que exceden el alcance previsto o no están autorizadas, debido a inyección de prompt, mal uso de herramientas o fallos de lógica. El núcleo de este riesgo radica en que el agente inteligente carece de un control efectivo sobre los límites de ejecución de código, pudiendo ejecutar, mediante generación dinámica de código, invocación de cadenas de herramientas o ejecución de scripts, código malicioso, peligroso o no previsto, lo que provoca consecuencias graves como el compromiso del sistema, la alteración de datos, la filtración de información sensible o la interrupción del servicio.

**Casos de ataque**

Caso
Descripción




Caso 1
La vulnerabilidad se origina en que el nodo de formulario no valida el Content-Type al procesarlo, lo que permite al atacante especificar la ruta de cualquier archivo local sensible, logrando finalmente, mediante la filtración de información, suplantar la identidad de administrador y ejecutar comandos maliciosos del flujo de trabajo.


Caso 2
Este caso muestra cómo un equipo rojo de IA, mediante inyección de prompt, indujo a un modelo multimodal con capacidad de operación de escritorio a descargar y ejecutar un programa malicioso, estableciendo finalmente un canal de comunicación C2 y logrando la ejecución de código no prevista y control remoto, convirtiendo al sistema anfitrión en un "host zombi".


Caso 3
Este caso muestra cómo, mediante inyección de prompt, se manipuló el mecanismo de memoria a largo plazo (Memory) de ChatGPT, implantando una lógica de instrucciones encubiertas definida por el atacante, de modo que el modelo mantiene comunicación continua con un C2 remoto en conversaciones posteriores y ejecuta instrucciones, formando un "control de zombificación" y una ejecución de comportamiento no previsto a nivel de modelo.

**Riesgos del ataque**

Compromiso del sistema: la ejecución de código malicioso provoca el control total del sistema.
Destrucción de datos: la ejecución de operaciones destructivas provoca pérdida o alteración de datos.
Escalamiento de privilegios: se obtienen privilegios de sistema más elevados mediante la ejecución de código.
Implantación de puerta trasera: se implanta una puerta trasera persistente en el sistema.
Interrupción del servicio: la ejecución de código malicioso provoca que el servicio quede inutilizable.
Movimiento lateral: se aprovecha la ejecución de código para atacar otros sistemas.

**Medidas de mitigación**

Medida de mitigación
Descripción




Sandbox de ejecución de código
Restringir la ejecución de código a un entorno seguro y aislado, utilizando contenedores o máquinas virtuales para el aislamiento, limitando el acceso al sistema de archivos, la red y las llamadas al sistema.


Revisión y validación de código
Implementar análisis estático de seguridad del código, establecer una base de reglas de seguridad de código y detectar dinámicamente patrones de código malicioso.


Control de permisos
Aplicar el principio de mínimo privilegio, limitar el alcance de permisos de las herramientas de ejecución de código y establecer un mecanismo de aprobación para la ejecución de código.


Validación y filtrado de entradas
Validar rigurosamente las entradas de generación de código, filtrar funciones y operaciones peligrosas, y detectar posibles intenciones maliciosas.

**Referencias**

Vulnerabilidad de ejecución remota de código en n8n
ZombAIs: From Prompt Injection to C2 with Claude Computer Use
AI Domination: Remote Controlling ChatGPT ZombAI Instances

---

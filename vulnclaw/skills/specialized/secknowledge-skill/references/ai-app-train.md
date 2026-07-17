# Seguridad de Aplicaciones de IA - Fase de Entrenamiento

> Fuente: Comunidad AISS NSFOCUS de Seguridad de Grandes Modelos | Extraído de ai-app-security.md
> Fase: Fase de entrenamiento (GAARM.0034-0036 Componentes de terceros/Complementos/Código inseguro)

## Fase de entrenamiento

### Manejo Inseguro de Salidas en Aplicaciones LLM

> Número de riesgo: GAARM.0035.003
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este riesgo se refiere a un tipo de riesgo de seguridad que surge cuando un componente aguas abajo acepta la salida de un modelo de lenguaje grande (LLM) sin realizar una revisión adecuada. Los componentes aguas abajo del modelo incluyen Agentes con diversas funcionalidades; cuando falta el procesamiento adecuado de la salida, el atacante puede abusar del Agente a través del modelo para lograr un comportamiento de ataque. Por ejemplo, el atacante puede, mediante la introducción de texto específico, inducir al LLM a generar una respuesta que contenga información sensible, robando así datos del usuario, o generar directamente un payload de ataque no previsto, provocando vulnerabilidades aguas abajo como RCE o SSRF.

**Casos de ataque**

Caso
Descripción

Caso 1
CVE-2023-29374 es una vulnerabilidad de ejecución arbitraria de código en Langchain: los programas que usan Langchain en su versión 0.0.131 o anterior e invocan la cadena LLMMathChain de Langchain presentan un riesgo de seguridad que incluye ejecución arbitraria de comandos, lo cual puede provocar la filtración de información sensible como claves de OpenAI, o el control del servidor de Langchain.

Caso 2
Auto-GPT presenta una vulnerabilidad de path traversal en versiones anteriores a la v0.4.3; esta vulnerabilidad permite la ejecución de código arbitrario fuera del entorno docker en la máquina donde se ejecuta Auto-GPT. El atacante puede aprovechar esta vulnerabilidad para lanzar ataques dirigidos contra el objetivo, comprometiendo la seguridad del sistema del sitio.

**Riesgos del ataque**

Filtración de información sensible: los LLM a veces no sanitizan el JavaScript en sus respuestas. En este caso, el atacante puede usar un prompt cuidadosamente diseñado para que el LLM devuelva un payload de JavaScript; cuando el navegador de la víctima procesa este payload, sufre un ataque que provoca la filtración de información sensible, como la filtración del historial de conversación.
Ejecución arbitraria de código: el atacante puede ejecutar código arbitrario mediante la vulnerabilidad. Esto puede provocar que el atacante realice operaciones maliciosas en el servidor, como implantar puertas traseras, extraer datos sensibles o interrumpir el servicio.
Dirigido

**Medidas de mitigación**

Medida de mitigación
Descripción

Framework de confianza cero (Zero Trust)
En este framework, toda solicitud de acceso a un recurso se considera proveniente de una red no confiable, y el sistema la revisa, autentica y verifica, aportando así seguridad al sistema.

Entorno de sandbox
Intentar aprovechar un entorno de sandbox para ejecutar código, con el fin de garantizar una mayor seguridad del sistema. Por ejemplo, ejecutar el código únicamente dentro de un contenedor Docker temporal y dedicado puede limitar significativamente el impacto potencial del código malicioso.

**Referencias**

https://genai.owasp.org/wp-content/uploads/2024/05/OWASP-Top-10-for-LLM-Applications-v1_1_Chinese.pdf
https://cloud.baidu.com/article/3253170
https://www.akto.io/blog/insecure-output-handling-in-llms-insights
https://journal.hexmos.com/insecure-output-handling/
https://systemweakness.com/new-prompt-injection-attack-on-chatgpt-web-version-ef717492c5c2

---
### Riesgo de Vulnerabilidades Tradicionales en Aplicaciones LLM

> Número de riesgo: GAARM.0035.002
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Las vulnerabilidades tradicionales de seguridad de aplicaciones no solo existen en los sistemas de software tradicionales, sino que también pueden estar presentes en las aplicaciones LLM. Por ejemplo, ataques comunes a interfaces de API, toma de control de cuentas, ejecución de código, etc.: los riesgos y vulnerabilidades tradicionales siguen existiendo en los LLM, por lo que durante la fase de entrenamiento es imprescindible seguir estrictamente las mejores prácticas de seguridad, para garantizar que el sistema tenga suficiente capacidad de protección frente a riesgos tradicionales; de lo contrario, puede provocar una serie de peligros como interrupción del servicio, toma de control de cuentas o manipulación de datos.

**Casos de ataque**

Caso
Descripción

Caso 1
Un caso reportó indicios de que ChatGPT sufrió un ataque DDoS (denegación de servicio distribuida), en el cual atacantes externos intentaron sobrecargar y colapsar la red o el servidor mediante el envío repetido de solicitudes Ping.

Caso 2
La aplicación ChatGPT-Next-Web presenta una vulnerabilidad SSRF (CVE-2023-49785), que puede usarse para explorar recursos de la red interna.

**Riesgos del ataque**

Interrupción del servicio: un ataque de denegación de servicio (DoS) o el agotamiento de recursos puede provocar que la aplicación LLM no pueda responder a las solicitudes del usuario, afectando la continuidad del negocio.
Control del sistema: una vulnerabilidad de ejecución remota de código o de ejecución de scripts puede permitir que el atacante tome control del servidor, implante software malicioso o ejecute operaciones destructivas.

**Medidas de mitigación**

Medida de mitigación
Descripción

Reforzar la seguridad de la API
Garantizar que todas las interfaces de API pasen por una autenticación y un control de autorización estrictos, restringiendo los permisos de acceso.

Principio de privilegio mínimo
Restringir o deshabilitar funciones de ejecución de comandos innecesarias en la aplicación LLM, reduciendo la superficie de ataque potencial.

Evaluación de seguridad periódica
Realizar periódicamente escaneos de vulnerabilidades de seguridad sobre la aplicación LLM, corrigiendo oportunamente los problemas de seguridad detectados.

**Referencias**

https://sec.cafe/handbook/security_research/ai_security/llm_security/attack/

---
### Complementos LLM: Manejo Inseguro de Entradas

> Número de riesgo: GAARM.0035.001
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este riesgo se refiere a que, debido a que los complementos (plugins) de los LLM presentan un manejo inseguro de las entradas, se introduce riesgo en el gran modelo. Por ejemplo, es muy probable que un complemento acepte texto libre proveniente del modelo sin realizar validación o verificación de tipo para manejar los límites del tamaño de contexto, lo que permite que un atacante potencial construya una solicitud maliciosa que se envía al complemento, pudiendo provocar diversos comportamientos indeseados, incluso ejecución remota de código.

**Casos de ataque**

Caso
Descripción

Caso 1
Se descubrió que PALChain, dentro de LangChain, presenta un riesgo de ejecución de código.

**Riesgos del ataque**

Ejecución de solicitudes no autorizadas: el atacante puede explotar directamente una vulnerabilidad de la aplicación LLM, o manipular el prompt de entrada, para que la aplicación LLM ejecute solicitudes inesperadas, accediendo u operando sobre recursos restringidos.
Filtración de información sensible: el acceso a recursos restringidos a través de los LLM puede provocar la obtención y filtración no autorizada de información sensible.

**Medidas de mitigación**

Medida de mitigación
Descripción

Validación y filtrado de entradas
Implementar estrategias estrictas de validación y sanitización de entradas, garantizando que todos los datos de entrada sean revisados y depurados antes de ser procesados por el LLM.

Principio de privilegio mínimo
Seguir el principio de privilegio mínimo, otorgando al LLM únicamente el acceso mínimo necesario para completar su tarea, evitando la autorización excesiva.

**Referencias**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/SSRF.html
https://www.horizon3.ai/attack-research/attack-blogs/nextchat-an-ai-chatbot-that-lets-you-talk-to-anyone-you-want-to/
https://genai.owasp.org/wp-content/uploads/2024/05/OWASP-Top-10-for-LLM-Applications-v1_1_Chinese.pdf

---
### Complementos LLM: Exceso de Agencia de Negocio

> Número de riesgo: GAARM.0036
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Los sistemas basados en LLM normalmente reciben del desarrollador cierto grado de capacidad de agencia de negocio, es decir, la capacidad de interactuar con otros sistemas y ejecutar acciones al responder a un prompt. El exceso de agencia es un riesgo de seguridad de la fase de diseño y desarrollo; este riesgo provoca que se ejecuten operaciones destructivas cuando el LLM produce una salida inesperada o ambigua, y su causa raíz suele ser: demasiadas funciones o demasiada autonomía. El exceso de agencia puede provocar una serie de impactos relacionados con la confidencialidad, integridad y disponibilidad, dependiendo de con qué sistemas pueda interactuar la aplicación LLM. Por ejemplo, otorgar al sistema LLM una autonomía excesiva puede provocar que, cuando la aplicación o complemento basado en LLM no verifique ni apruebe de forma independiente operaciones de alto impacto, un complemento que permite eliminar documentos del usuario ejecute la operación de eliminación sin requerir ninguna confirmación del usuario.

**Casos de ataque**

Caso
Descripción

Caso 1
El video muestra cómo, aprovechando una vulnerabilidad de exceso de agencia, se puede realizar un restablecimiento ilegítimo de la contraseña de un usuario.

**Riesgos del ataque**

Filtración de información sensible: cuando el exceso de agencia de negocio provoca que el LLM sea manipulado de forma maliciosa, puede filtrarse información sensible y privada.

**Medidas de mitigación**

Medida de mitigación
Descripción

Principio de privilegio mínimo
Restringir los complementos/herramientas que el Agente LLM tiene permitido invocar, limitándolos únicamente a la funcionalidad mínima necesaria. Por ejemplo, si el sistema base del LLM no necesita la capacidad de obtener el contenido de una URL, no se le debería proporcionar al Agente LLM un complemento de ese tipo.

Evitar funciones de propósito abierto
En la medida de lo posible, evitar funciones de propósito abierto (como ejecutar comandos de shell, obtener URLs, etc.) y usar complementos/herramientas de granularidad más fina. Por ejemplo, una aplicación base de LLM puede necesitar escribir cierta salida en un archivo. Si se usa un complemento que ejecuta funciones de shell para lograrlo, el alcance de las operaciones indeseadas será muy amplio (podría ejecutar cualquier otro comando de shell). Una alternativa más segura es construir un complemento de escritura de archivos que solo admita una función específica.

**Referencias**

https://genai.owasp.org/wp-content/uploads/2024/05/OWASP-Top-10-for-LLM-Applications-v1_1_Chinese.pdf

---
### Vulnerabilidades del Framework de Desarrollo RAG

> Número de riesgo: GAARM.0034.002
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

RAG (Retrieval-Augmented Generation, generación aumentada por recuperación) es un framework que combina la recuperación de información con la generación, utilizado en el desarrollo de grandes modelos de lenguaje (LLM) para reforzar la capacidad de generación del modelo. Dado que el framework RAG depende de un módulo de recuperación para obtener información de fuentes de datos externas, si los datos de origen del módulo de recuperación son inexactos o poco fiables, la respuesta generada puede contener información errónea o engañosa; además, los diversos Agentes que introduce el propio framework también pueden presentar riesgos de seguridad asociados. Los riesgos de seguridad relacionados con el framework RAG se concentran principalmente en el módulo de generación, el módulo de recuperación de información, los complementos integrados y las interfaces externas de RAG; un diseño inseguro de RAG puede provocar que se introduzcan vulnerabilidades de seguridad en la aplicación LLM. Por ejemplo, si el diseño del módulo de recuperación de RAG permite que el servidor realice solicitudes sin restricciones, puede provocar la explotación de una vulnerabilidad SSRF.

**Casos de ataque**

Caso
Descripción

Caso 1
Las vulnerabilidades SSRF y de RCE en PALChain presentes en el framework LangChain suponen un riesgo de seguridad para las aplicaciones LLM que usan dicho framework.

**Riesgos del ataque**

Filtración de información: el atacante puede, mediante una vulnerabilidad de path traversal, acceder a archivos sensibles o archivos de configuración del sistema, filtrando información interna del sistema.
Control del sistema: si los archivos del sistema contienen información de configuración sensible o scripts, el atacante puede aprovechar aún más esta información para tomar control del sistema.
Ejecución de comandos: los Agentes del framework, como el motor de evaluación de expresiones de datos o el intérprete de Python, pueden ser aprovechados para provocar un ataque RCE.

**Medidas de mitigación**

Medida de mitigación
Descripción

Validación de entradas
Validar y depurar estrictamente todas las entradas del usuario, evitando ataques de path traversal.

Gestión de permisos
Establecer permisos de archivo adecuados, evitando el acceso no autorizado a archivos.

Actualización y corrección
Garantizar el uso de la última versión de la aplicación y sus dependencias, aplicando oportunamente los parches de seguridad para corregir vulnerabilidades conocidas.

**Referencias**

https://www.wehelpwin.com/article/5063
https://medium.com/nfactor-technologies/rag-poisoning-an-emerging-threat-in-ai-systems-660f9ff279f9
https://ironcorelabs.com/security-risks-rag/

---
### Prácticas de Código Inseguras

> Número de riesgo: GAARM.0035
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Las prácticas de código inseguras se refieren a problemas de seguridad originados en defectos de diseño durante el proceso de desarrollo de aplicaciones LLM basadas en un framework de integración de grandes modelos. La lógica de código adoptada durante el desarrollo de aplicaciones LLM puede introducir riesgos de seguridad, generando vulnerabilidades explotables en la aplicación LLM. Las vulnerabilidades de seguridad resultantes pueden agruparse en dos grandes categorías:

El servicio de la aplicación LLM presenta vulnerabilidades tradicionales; por ejemplo, un servicio de chat orientado al exterior puede presentar el riesgo de ver de forma no autorizada los registros de conversación de otros usuarios.
Las nuevas herramientas (Tools), Agentes (Agents) y cadenas (Chains) del framework de integración de LLM contienen riesgos de seguridad, permitiendo que el atacante explote de forma indirecta las vulnerabilidades relacionadas a través del LLM.

**Casos de ataque**

Caso
Descripción

Caso 1
Se descubrió que PALChain, dentro de LangChain, presenta un riesgo de ejecución de código.

Caso 2
Se descubrieron múltiples vulnerabilidades RCE de alto riesgo en LangChain.

**Riesgos del ataque**

Prácticas de codificación inseguras: al generar código, los LLM pueden seguir prácticas de codificación inseguras, provocando que el código generado contenga vulnerabilidades de seguridad.
Ejecución de solicitudes no autorizadas: el atacante puede explotar directamente una vulnerabilidad de la aplicación LLM, o manipular el prompt de entrada, para que la aplicación LLM ejecute solicitudes inesperadas, accediendo u operando sobre recursos restringidos.

**Medidas de mitigación**

Medida de mitigación
Descripción

Detección y evaluación automatizada
Utilizar herramientas de análisis estático para detectar patrones inseguros en el código, mejorando la seguridad del código.

Principio de privilegio mínimo
Seguir el principio de privilegio mínimo, otorgando al LLM únicamente el acceso mínimo necesario para completar su tarea, evitando la autorización excesiva de agencia.

Validación y filtrado de entradas
Implementar estrategias estrictas de validación y sanitización de entradas, garantizando que todos los datos de entrada sean revisados y depurados antes de ser procesados por el LLM.

**Referencias**

https://arxiv.org/html/2312.04724v1

---
### Vulnerabilidades en Componentes de Procesamiento de Datos

> Número de riesgo: GAARM.0034.001
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

En el proceso de desarrollo de modelos de inteligencia artificial (IA), la seguridad de los conjuntos de datos es un aspecto que no se puede pasar por alto. En plataformas como Hugging Face o GitHub pueden existir conjuntos de datos con puertas traseras maliciosas, y estos conjuntos de datos pueden, a través de características o vulnerabilidades de los componentes de procesamiento de datos de los LLM, constituir una amenaza para la seguridad del modelo de IA. Cuando un desarrollador utiliza estos conjuntos de datos contaminados para entrenar un modelo, el código malicioso oculto en el conjunto de datos puede ejecutarse, provocando una serie de problemas de seguridad, como la filtración o manipulación del modelo de IA, el conjunto de datos y el código.

**Casos de ataque**

Caso
Descripción

Caso 1
Se descubrió que el componente datasets de Hugging Face presenta características inseguras; al usar este componente para cargar un conjunto de datos malicioso, puede provocar riesgos como la ejecución de comandos.

**Riesgos del ataque**

Intrusión del sistema: un script malicioso construido por el atacante puede conectarse al servidor del atacante y ejecutar comandos del sistema, tomando así control del servidor de la víctima.
Filtración de datos: un script malicioso puede robar datos sensibles almacenados en el servidor, como los datos de entrenamiento o el código del modelo, provocando la filtración de propiedad intelectual y de la privacidad de los usuarios.
Manipulación de parámetros del modelo: los parámetros del gran modelo pueden ser manipulados de forma maliciosa, afectando la exactitud y fiabilidad del modelo.

**Medidas de mitigación**

Medida de mitigación
Descripción

Fuentes confiables para los conjuntos de datos de entrenamiento/ajuste fino
Garantizar que los conjuntos de datos de origen sean confiables, verificar si existe código Python malicioso en los scripts del conjunto de datos, y usar con precaución los conjuntos de datos en Hugging Face que hayan sido señalados con riesgos de seguridad.

Protección de la cadena de suministro de componentes de grandes modelos
Dar seguimiento continuo a las últimas novedades y recomendaciones sobre la seguridad de la cadena de suministro en áreas como la seguridad nativa de los grandes modelos, la seguridad básica y la seguridad del desarrollo habilitado por grandes modelos.

**Referencias**

https://security.tencent.com/index.php/blog/msg/209

---
### Vulnerabilidades de Componentes de Terceros

> Número de riesgo: GAARM.0034
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este ataque se refiere a que los desarrolladores de aplicaciones LLM pueden, durante la fase de entrenamiento del modelo, usar bibliotecas o componentes comerciales o de código abierto de terceros; estos componentes de terceros pueden contener código malicioso o vulnerabilidades propias del componente, lo que puede provocar la intrusión de la máquina de desarrollo o del servidor, constituyendo un riesgo de seguridad de la cadena de suministro en el entorno de IA.

**Casos de ataque**

Caso
Descripción

Caso 1
redis-py, el cliente Python de la base de datos Redis, utiliza una interfaz asíncrona; al cancelar un comando, puede provocar una lectura desordenada de los datos de negocio del usuario (CVE-2023-28858).

Caso 2
TorchServe puede provocar un acceso no autorizado al servidor, y lograr ejecución remota de código en instancias vulnerables.

Caso 3
El componente datasets de Hugging Face presenta una vulnerabilidad que permite realizar ataques mediante conjuntos de datos maliciosos, pudiendo provocar la intrusión del dispositivo del usuario y el robo o manipulación de los parámetros del gran modelo.

Caso 4
Este artículo estudia el impacto de los ataques de puerta trasera sobre modelos preentrenados. El atacante puede, mediante la implantación de una puerta trasera, manipular los resultados de recomendación del modelo, logrando así fines de marketing malicioso u otros objetivos.

Caso 5
ChatGPT-Next-Web presenta vulnerabilidades de SSRF y de XSS reflejado.

**Riesgos del ataque**

Ataque de envenenamiento de puerta trasera en la cadena de suministro: cuando un desarrollador de IA carga un conjunto de datos usando una biblioteca de código abierto de terceros, si el conjunto de datos tiene implantado código malicioso, puede provocar que el PC o el servidor sufran un ataque.
Filtración o manipulación de parámetros del modelo: provoca que los parámetros del modelo sean robados o manipulados, afectando la seguridad y fiabilidad del modelo.

**Medidas de mitigación**

Medida de mitigación
Descripción

Protección de la cadena de suministro de componentes de grandes modelos
Para vulnerabilidades de seguridad conocidas, como la CVE-2023-43654 de TorchServe, se debe actualizar oportunamente a una versión segura.

Fuentes confiables para los conjuntos de datos de entrenamiento/ajuste fino
Garantizar que la fuente de los conjuntos de datos sea confiable, verificar si existe código Python malicioso en los scripts del conjunto de datos, y evitar el uso de conjuntos de datos en Hugging Face que hayan sido señalados con riesgos de seguridad.

Control estricto de la incorporación de componentes de código abierto
Establecer un sistema interno de gobernanza de código abierto en la empresa, controlando estrictamente la incorporación de componentes de código abierto, e implementando monitoreo y seguimiento automatizados mediante herramientas.

**Referencias**

https://hiddenlayer.com/research/insane-in-the-supply-chain/

---

---


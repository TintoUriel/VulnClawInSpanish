# Seguridad de la Base de IA - Fase de Aplicación

> Fuente: Comunidad AISS NSFOCUS de Seguridad de Grandes Modelos | Extraído de ai-baseline-security.md
> Fase: Fase de aplicación (Escape de contenedor / Denegación de servicio / Escape de ejecución de código)

## Fase de aplicación

### Denegación de Servicio y Agotamiento de Recursos en LLMs

> Número de riesgo: GAARM.0008
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Un atacante puede atacar el sistema de aprendizaje automático enviando una gran cantidad de solicitudes, con el fin de degradar la velocidad del servicio de ML o provocar su caída. Dado que los sistemas LLM requieren una gran cantidad de recursos computacionales especializados, un atacante puede construir deliberadamente entradas que exigen un cómputo masivo e inútil, con el fin de agotar los recursos del sistema LLM, degradando la calidad del servicio tanto para el propio LLM como para otros usuarios, y potencialmente generando costos de recursos muy elevados. Debido a la naturaleza intensiva en recursos de los LLM y a la imprevisibilidad de las entradas del usuario, el daño de esta vulnerabilidad se amplifica con facilidad.

**Casos de ataque**

Caso
Descripción

Caso 1
Realizar una inyección de prompt en un agente, induciéndolo a invocar repetidamente el LLM y la SerpAPI, incrementando rápidamente el costo.

Caso 2
Debido a la filtración accidental de un token de acceso de administrador del sitio de Sourcegraph, este fue utilizado para suplantar a un usuario y obtener acceso a la consola de administración del sistema, provocando un incremento significativo en el uso de la API y la filtración de una gran cantidad de datos de usuarios.

Caso 3
Aprovechar una inyección de prompt para que MathGPT filtre su clave de API, provocando además una denegación de servicio.

Caso 4
Al aplicar un LLM para la toma de decisiones en un sistema eléctrico, si ocurre un ataque DoS, puede provocar retrasos y errores en la decisión, afectando finalmente la operación estable del sistema eléctrico.

**Riesgos del ataque**

Ataque de agotamiento de recursos: el atacante puede enviar una gran cantidad de solicitudes para ocupar los recursos computacionales del modelo, dejando el servicio inutilizable, afectando la experiencia del usuario e incluso provocando una interrupción del servicio.
Filtración y abuso de datos: el proceso de ataque puede provocar que el modelo filtre de forma anómala información sensible como tokens de API, y el atacante puede realizar acceso no autorizado.

**Medidas de mitigación**

Medida de mitigación
Descripción

Límite de tasa de la API
Aplicar límites de tasa en la API, restringiendo la cantidad de solicitudes que un usuario individual o dirección IP puede emitir en un período de tiempo determinado.

Limitar la cantidad de ejecuciones
Limitar la cantidad de operaciones en cola y el número total de operaciones en el sistema que dependen de la respuesta del LLM.

Monitoreo y alertas en tiempo real
Monitorear continuamente la utilización de recursos de hardware para identificar picos o patrones anómalos que puedan indicar la existencia de un ataque de denegación de servicio.

**Referencias**

https://atlas.mitre.org/techniques/AML.T0029
https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-2023-v05.pdf
https://www.cnblogs.com/LittleHann/p/17596696.html

---
### Escape de Ejecución del Intérprete de Código

> Número de riesgo: GAARM.0007.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo se refiere a que un atacante aprovecha las capacidades de análisis y generación de código de intérpretes de código como el de GPT-4, construyendo y ocultando gradualmente código malicioso mediante interacciones de contexto en múltiples turnos de conversación, usando caracteres Unicode y ofuscación mediante codificación, entre otras técnicas para ocultar el código malicioso, eludiendo así el mecanismo de verificación de seguridad de código de la aplicación del modelo, logrando completar un escape del sandbox y obteniendo finalmente acceso al sistema. Este tipo de código malicioso tiene un alto grado de sigilo y es difícil de detectar; una vez que se rompe el aislamiento del sandbox, el atacante puede controlar todo el sistema, robar datos, implantar puertas traseras, etc.

**Casos de ataque**

Caso
Descripción

Caso 1
Durante la ejecución de código en GPT-4, mediante múltiples interacciones de contexto de conversación y técnicas de codificación se ocultó y evadió código malicioso, activando finalmente su ejecución mediante una cadena de caracteres, eludiendo la verificación de seguridad de GPT-4 y ejecutando el comando cat /etc/issue, logrando obtener con éxito la distribución de Linux del entorno objetivo.

**Riesgos del ataque**

Riesgo de filtración de datos: el atacante puede extraer datos sensibles de la aplicación LLM o de los sistemas a los que esta se conecta.
Riesgo de integridad del sistema: el atacante puede ejecutar operaciones no autorizadas, modificar configuraciones o archivos del sistema, e incluso implantar código malicioso, causando así daño al sistema.
Riesgo de escalada de privilegios: una vez que el atacante logra escapar del sandbox con éxito, puede obtener un nivel de acceso con privilegios superiores a los que originalmente poseía.

**Medidas de mitigación**

Medida de mitigación
Descripción

Entorno de pruebas de aislamiento estricto
Realizar pruebas y validación estrictas del entorno del sandbox, garantizando su seguridad.

Validación de entrada/salida
Filtrar prompts inseguros, garantizando al máximo la seguridad del sistema.

Control de acceso
Implementar un control de acceso estricto y separación de privilegios en la aplicación LLM y su entorno de sandbox, garantizando que solo entidades autorizadas puedan acceder a recursos sensibles, y restringiendo la ejecución de operaciones privilegiadas.

**Referencias**

https://blog.securelayer7.net/owasp-top10-for-large-language-models/
https://www.mufeedvh.com/llm-security/#2-sandboxing-extended-llms
https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Inadequate_Sandboxing.html

---
### Riesgo del Entorno de Ejecución de Contenedores

> Número de riesgo: GAARM.0004 (inferido a partir de la clasificación de AISS)
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Las aplicaciones LLM desarrolladas sobre frameworks de integración suelen combinar clústeres K8S con entornos de contenedores para construir y aislar el entorno de ejecución de cada Agente. Un atacante, mediante prompts cuidadosamente construidos, ejecuta de forma indirecta a través del Agente del modelo un ataque dirigido al entorno de ejecución de contenedores, logrando un escape de contenedor, una escalada de privilegios en el contenedor, y otros ataques similares.

**Casos de ataque**

Caso
Descripción

Caso 1
Wiz obtuvo permisos sobre el entorno de ejecución del contenedor del modelo subiendo un modelo malicioso a Hugging Face.

**Riesgos del ataque**

Ruptura del aislamiento de contenedores: el atacante, aprovechando vulnerabilidades o defectos de configuración del contenedor, intenta romper el entorno de aislamiento del contenedor para obtener acceso a la máquina anfitriona.
Manipulación del contenido de la imagen: el atacante puede manipular el contenido de la imagen del modelo, implantando código malicioso.
Filtración de datos: el atacante puede obtener datos sensibles, como información del sistema de archivos de la máquina anfitriona.
Interrupción del servicio: el atacante puede dañar el servicio que corre en la máquina anfitriona, dejándolo inutilizable.
Movimiento lateral: el atacante puede usar el contenedor del que ha escapado como punto de apoyo para atacar otros sistemas dentro de la red interna.
Control persistente: el atacante puede instalar puertas traseras en la máquina anfitriona para lograr un control a largo plazo.

**Medidas de mitigación**

Medida de mitigación
Descripción

Revisión periódica
Escanear periódicamente las imágenes de contenedores y los componentes de dependencias para garantizar que no existan vulnerabilidades de seguridad.

Límites de recursos y aislamiento de acceso
Implementar límites de recursos y estrategias de aislamiento para evitar que un solo contenedor consuma recursos excesivos y afecte a otras máquinas del clúster.

Principio de privilegio mínimo
Evitar ejecutar contenedores en modo privilegiado (por ejemplo, con --privileged), otorgando únicamente el conjunto mínimo de permisos que el contenedor necesita.

Validación de entrada/salida
Garantizar la seguridad de los prompts de entrada y de los resultados de salida del modelo, e implementar la intercepción de comportamientos de ataque sospechosos.

**Referencias**

https://mp.weixin.qq.com/s/tf4ljSJ0Ue0YniojWhYMKg
https://www.wiz.io/blog/wiz-and-hugging-face-address-risks-to-ai-infrastructure

---
### Reconocimiento del Entorno de Clúster de Contenedores

> Número de riesgo: GAARM.0006
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo se refiere a que un atacante aprovecha problemas de seguridad propios de proveedores de nube externos o de clústeres K8S autogestionados en el entorno de despliegue del modelo, como el control de permisos del sistema, errores de configuración, vulnerabilidades de seguridad propias del clúster o complementos de integración de terceros. Se ataca la funcionalidad de Agentes en aplicaciones integradas de LLM, aprovechando la interacción entre estas funciones y el entorno de despliegue del negocio, para lograr ataques contra el sistema de aplicación de negocio del modelo. Tras penetrar con éxito en el entorno de despliegue, puede producirse la filtración de datos sensibles, la implantación de programas de puerta trasera, y otros riesgos.

**Casos de ataque**

Caso
Descripción

Caso 1
Wiz obtuvo permisos sobre el entorno de ejecución del modelo subiendo un modelo malicioso a Hugging Face, y además aprovechó una configuración incorrecta del clúster EKS para lograr una escalada de privilegios.

**Riesgos del ataque**

Ataque de agotamiento de recursos: el acceso sin restricciones a los recursos puede convertirse en un vector de ataque; el atacante puede consumir una gran cantidad de recursos, afectando el funcionamiento normal del sistema.
Riesgo de ejecución en modo privilegiado: un contenedor que se ejecuta en modo privilegiado puede aumentar el riesgo de que el sistema sea comprometido.
Acceso no autorizado al clúster: si no se han implementado medidas de seguridad o el clúster presenta configuraciones incorrectas, el atacante puede obtener acceso completo a todo el clúster.

**Medidas de mitigación**

Medida de mitigación
Descripción

Revisión periódica
Escanear periódicamente las imágenes de contenedores y los componentes de dependencias para garantizar que no existan vulnerabilidades de seguridad.

Límites de recursos y aislamiento de acceso
Implementar límites de recursos y estrategias de aislamiento para evitar que un solo contenedor consuma recursos excesivos, restringiendo el acceso a los recursos mediante secretos y roles con permisos específicos creados en Kubernetes.

Control del tráfico de red
Utilizar políticas de red de Kubernetes para controlar el tráfico de red entrante y saliente entre Pods, reduciendo el movimiento lateral potencial dentro del clúster.

**Referencias**

https://pradiptabanerjee.medium.com/confidential-containers-for-large-language-models-42477436345a

https://www.run.ai/guides/kubernetes-architecture/securing-your-ai-ml-kubernetes-environment

---
### Ataque al Entorno de Clúster de Contenedores

> Número de riesgo: GAARM.0007
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Las aplicaciones LLM desarrolladas sobre frameworks de integración suelen integrar diversos Agentes funcionales, los cuales se despliegan en entornos de contenedores dentro de un clúster de Kubernetes. Un atacante puede, mediante prompts cuidadosamente construidos, inducir indirectamente al Agente del LLM a ejecutar comandos de reconocimiento del contenedor, logrando así la exploración y recopilación de información del entorno dentro del clúster, sentando las bases para el proceso de ataque posterior. Una vez completado el reconocimiento y recopilada la información correspondiente, se pueden buscar y explotar de forma dirigida vulnerabilidades y problemas de configuración en el clúster, penetrando y atacando aún más todo el clúster de contenedores.

**Casos de ataque**

Caso
Descripción

Caso 1
Durante la ejecución de código en GPT-4, mediante múltiples interacciones de contexto de conversación y técnicas de codificación se ocultó y evadió código malicioso, activando finalmente su ejecución mediante una cadena de caracteres, eludiendo la verificación de seguridad de GPT-4 y ejecutando el comando cat /etc/issue, logrando obtener con éxito la distribución de Linux del entorno objetivo, así como información sobre las variables de entorno del clúster.

**Riesgos del ataque**

Filtración de información del entorno de clúster: mediante la construcción de prompts específicos, el atacante puede inducir al modelo de IA a ejecutar comandos no autorizados, filtrando así información sobre la arquitectura interna del contenedor o su configuración de seguridad.
Filtración de configuración de seguridad del clúster: mediante el reconocimiento, el atacante puede obtener detalles de la configuración de seguridad del clúster, lo que puede reducir la seguridad del clúster e incrementar el riesgo de que sea comprometido.

**Medidas de mitigación**

Medida de mitigación
Descripción

Implementar un control de acceso estricto
Garantizar que todos los servicios y puertos sean revisados de forma estricta, autorizando únicamente el acceso necesario, reduciendo la superficie de ataque potencial.

Validación de entrada/salida
Garantizar la seguridad de los prompts de entrada y de los resultados de salida del modelo, e implementar la intercepción de comportamientos de ataque sospechosos.

**Referencias**

https://mp.weixin.qq.com/s/Ry1PoZLfPvw6Lj8bz14mgw

---

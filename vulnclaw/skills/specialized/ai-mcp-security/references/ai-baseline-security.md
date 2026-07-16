# Seguridad de línea base de IA

> Fuente: Comunidad de Seguridad de Cadena Inteligente de Grandes Modelos AISS de NSFOCUS
> Número de entradas: 19

---

## Fase de aplicación

### Denegación de servicio y agotamiento de recursos en LLMs

> N.º de riesgo: GAARM.0008
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Un atacante puede atacar un sistema de aprendizaje automático enviando una gran cantidad de solicitudes, con el fin de reducir la velocidad del servicio de ML o provocar su caída. Dado que los sistemas LLM requieren una gran cantidad de recursos computacionales especializados, un atacante puede construir deliberadamente entradas que requieran una gran cantidad de cómputo inútil para consumir los recursos del sistema LLM, degradando la calidad del servicio tanto para el LLM como para otros usuarios, y generando potencialmente costos de recursos elevados. Debido a la naturaleza intensiva en recursos de los LLM y a la imprevisibilidad de la entrada del usuario, el daño de esta vulnerabilidad puede amplificarse fácilmente.

**Casos de ataque**

Caso
Descripción




Caso 1
Inyección de Prompt en un agent, engañándolo para que llame repetidamente al LLM y a SerpAPI, aumentando rápidamente los costos.


Caso 2
Debido a la filtración accidental de un token de acceso de administrador del sitio de Sourcegraph, que fue explotado para suplantar a un usuario y obtener acceso a la consola de administración del sistema, provocando un aumento significativo en el uso de la API y la filtración de una gran cantidad de datos de usuarios.


Caso 3
Uso de inyección de Prompt para hacer que MathGPT filtre su clave de API, provocando denegación de servicio.


Caso 4
Al aplicar un LLM para la toma de decisiones en un sistema eléctrico, si ocurre un ataque DOS, puede provocar retrasos y errores en la toma de decisiones, afectando en última instancia la operación estable del sistema eléctrico.

**Riesgos del ataque**

Ataque de agotamiento de recursos: un atacante puede enviar una gran cantidad de solicitudes para acaparar los recursos computacionales del modelo, dejando el servicio no disponible, afectando la experiencia del usuario e incluso provocando la interrupción del servicio.
Fuga y abuso de datos: el proceso de ataque puede provocar que el modelo filtre de forma anómala información sensible como tokens de API, y el atacante puede realizar accesos no autorizados.

**Medidas de mitigación**

Medida de mitigación
Descripción




Límite de tasa de API
Aplicar límites de tasa de API, restringiendo el número de solicitudes que un usuario o dirección IP individual puede realizar en un período de tiempo determinado


Limitar el número de ejecuciones
Limitar el número de operaciones en cola y el número total de operaciones en el sistema que responde con el LLM


Monitoreo y alertas en tiempo real
Monitorear continuamente la utilización de recursos de hardware para identificar picos o patrones anómalos que puedan indicar la existencia de un ataque de denegación de servicio

**Referencias**

https://atlas.mitre.org/techniques/AML.T0029
https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-2023-v05.pdf
https://www.cnblogs.com/LittleHann/p/17596696.html

---
### Escape de ejecución del intérprete de código

> N.º de riesgo: GAARM.0007.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo se refiere a que un atacante aprovecha la funcionalidad de intérpretes de código como GPT-4, utilizando su capacidad de análisis y generación de código, para construir y ocultar código malicioso de forma gradual mediante interacciones de contexto en múltiples sesiones, usando caracteres Unicode y ofuscación de codificación, entre otros métodos, para ocultar y eludir el código malicioso. Esto permite eludir el mecanismo de verificación de seguridad de código de la aplicación del modelo, lograr el escape del sandbox y, en consecuencia, obtener acceso al sistema. Este tipo de código malicioso es altamente sigiloso y difícil de detectar; una vez que se rompe el aislamiento del sandbox, el atacante puede controlar todo el sistema, robar datos, implantar puertas traseras, etc.

**Casos de ataque**

Caso
Descripción




Caso 1
Durante la ejecución de código en GPT-4, mediante múltiples interacciones de contexto de sesión y métodos de codificación se ocultó y eludió código malicioso, que finalmente se disparó mediante una cadena de texto, eludiendo la verificación de seguridad de GPT-4 y ejecutando el comando cat /etc/issue, obteniendo con éxito la distribución de Linux del entorno objetivo.

**Riesgos del ataque**

Riesgo de fuga de datos: el atacante puede extraer datos sensibles de la aplicación LLM o de los sistemas a los que está conectada.
Riesgo de integridad del sistema: el atacante puede realizar operaciones no autorizadas, modificar la configuración del sistema o archivos, e incluso implantar código malicioso, causando daño al sistema.
Riesgo de escalada de privilegios: una vez que el atacante logra escapar del sandbox, puede obtener un nivel de acceso con privilegios superiores a los que originalmente poseía.

**Medidas de mitigación**

Medida de mitigación
Descripción




Pruebas estrictas del entorno aislado
Realizar pruebas y validaciones rigurosas del entorno sandbox para garantizar su seguridad


Validación de entrada/salida
Filtrar Prompts inseguros para garantizar al máximo la seguridad del sistema


Control de acceso
Implementar un control de acceso estricto y separación de privilegios en la aplicación LLM y su entorno sandbox, garantizando que solo entidades autorizadas puedan acceder a recursos sensibles, y limitando la ejecución de operaciones privilegiadas

**Referencias**

https://blog.securelayer7.net/owasp-top10-for-large-language-models/
https://www.mufeedvh.com/llm-security/#2-sandboxing-extended-llms
https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Inadequate_Sandboxing.html

---
### Riesgo del runtime de contenedores

> N.º de riesgo: GAARM.0004 (inferido de la clasificación AISS)
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Las aplicaciones LLM desarrolladas sobre frameworks de integración suelen combinar clústeres K8S y entornos de contenedores para construir y aislar el entorno de ejecución de cada Agent. Un atacante, mediante Prompts cuidadosamente construidos, puede indirectamente, a través del Agent ejecutor del modelo, llevar a cabo ataques contra el entorno de runtime de contenedores, logrando así escape de contenedor, escalada de privilegios en contenedor y otros ataques dentro del entorno de contenedores.

**Casos de ataque**

Caso
Descripción




Caso 1
Wiz obtuvo permisos sobre el entorno de ejecución del contenedor del modelo subiendo un modelo malicioso a Hugging Face.

**Riesgos del ataque**

Ruptura del aislamiento de contenedores: el atacante, aprovechando vulnerabilidades o defectos de configuración del contenedor, intenta romper el entorno de aislamiento del contenedor para obtener acceso a la máquina anfitriona.
Manipulación del contenido de la imagen: el atacante puede manipular el contenido de la imagen del modelo e implantar código malicioso.
Fuga de datos: el atacante puede obtener datos sensibles, como información del sistema de archivos de la máquina anfitriona.
Interrupción del servicio: el atacante puede dañar los servicios de la máquina anfitriona, provocando que el servicio quede no disponible.
Movimiento lateral: el atacante puede usar el contenedor del que escapó como trampolín para atacar otros sistemas dentro de la red interna.
Control persistente: el atacante puede instalar puertas traseras en la máquina anfitriona para lograr un control a largo plazo.

**Medidas de mitigación**

Medida de mitigación
Descripción




Revisión periódica
Escanear periódicamente las imágenes de contenedores y los componentes dependientes para garantizar que no existan vulnerabilidades de seguridad.


Límites de recursos y aislamiento de acceso
Implementar estrategias de límite de recursos y aislamiento para evitar que un solo contenedor consuma demasiados recursos, así como su impacto en otras máquinas del clúster.


Principio de mínimo privilegio
Evitar ejecutar contenedores privilegiados con modos como --privileged, otorgando al contenedor solo el conjunto mínimo de privilegios necesarios.


Validación de entrada/salida
Garantizar la seguridad de los Prompts y resultados tanto en la entrada como en la salida del modelo, implementando bloqueo ante comportamientos de ataque sospechosos

**Referencias**

https://mp.weixin.qq.com/s/tf4ljSJ0Ue0YniojWhYMKg
https://www.wiz.io/blog/wiz-and-hugging-face-address-risks-to-ai-infrastructure

---
### Sondeo del entorno del clúster de contenedores

> N.º de riesgo: GAARM.0006
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo se refiere a que un atacante aprovecha problemas de seguridad propios de proveedores de nube externos o clústeres K8S autoconstruidos en el entorno de despliegue del modelo, tales como control de permisos del sistema, errores de configuración, vulnerabilidades de seguridad propias del clúster, y plugins de integración de terceros. Atacando funcionalidades como los Agents en aplicaciones integradas de LLM, y aprovechando la interacción de estas funcionalidades con el entorno de despliegue del negocio, se logra llevar a cabo ataques contra el sistema de aplicación de negocio del modelo. Una vez lograda la penetración exitosa en el entorno de despliegue, pueden producirse riesgos como la filtración de datos sensibles o la implantación de programas de puerta trasera.

**Casos de ataque**

Caso
Descripción




Caso 1
Wiz obtuvo permisos sobre el entorno de ejecución del modelo subiendo un modelo malicioso a Hugging Face, y aprovechó además una configuración errónea del clúster EKS para lograr escalada de privilegios.

**Riesgos del ataque**

Ataque de agotamiento de recursos: el acceso ilimitado a los recursos puede convertirse en un vector de ataque; el atacante puede consumir una gran cantidad de recursos, afectando el funcionamiento normal del sistema.
Riesgo de ejecución en modo privilegiado: los contenedores que se ejecutan en modo privilegiado pueden aumentar el riesgo de que el sistema sea vulnerado.
Acceso no autorizado al clúster: si no se implementan medidas de seguridad o el clúster tiene configuraciones erróneas, el atacante puede obtener acceso completo a todo el clúster.

**Medidas de mitigación**

Medida de mitigación
Descripción




Revisión periódica
Escanear periódicamente las imágenes de contenedores y los componentes dependientes para garantizar que no existan vulnerabilidades de seguridad


Límites de recursos y aislamiento de acceso
Implementar estrategias de límite de recursos y aislamiento para evitar que un solo contenedor consuma demasiados recursos, limitando el acceso a recursos mediante secretos y roles con permisos específicos creados en Kubernetes


Control del tráfico de red
Utilizar políticas de red de Kubernetes para controlar el tráfico de red entrante y saliente entre Pods, reduciendo el movimiento lateral potencial dentro del clúster

**Referencias**

https://pradiptabanerjee.medium.com/confidential-containers-for-large-language-models-42477436345a


https://www.run.ai/guides/kubernetes-architecture/securing-your-ai-ml-kubernetes-environment

---
### Ataque al entorno del clúster de contenedores

> N.º de riesgo: GAARM.0007
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Las aplicaciones LLM desarrolladas sobre frameworks de integración suelen integrar diversos Agents funcionales, que se despliegan en el entorno de contenedores de un clúster de Kubernetes. Un atacante puede, mediante Prompts cuidadosamente construidos, inducir indirectamente al Agent del LLM a ejecutar comandos de sondeo de contenedores, logrando así el sondeo y recopilación de información del entorno del clúster, como preparación para el proceso de ataque posterior. Una vez completado el sondeo y recopilada la información correspondiente, se puede buscar y explotar de forma dirigida las vulnerabilidades y problemas de configuración del clúster, para penetrar y atacar aún más todo el clúster de contenedores.

**Casos de ataque**

Caso
Descripción




Caso 1
Durante la ejecución de código en GPT-4, mediante múltiples interacciones de contexto de sesión y métodos de codificación se ocultó y eludió código malicioso, que finalmente se disparó mediante una cadena de texto, eludiendo la verificación de seguridad de GPT-4 y ejecutando el comando cat /etc/issue, obteniendo con éxito la distribución de Linux del entorno objetivo así como información de variables de entorno del clúster.

**Riesgos del ataque**

Fuga de información del entorno del clúster: el atacante, mediante la construcción de Prompts específicos, puede inducir al modelo de IA a ejecutar comandos no autorizados, filtrando así información sobre la arquitectura interna del contenedor o la configuración de seguridad.
Fuga de la configuración de seguridad del clúster: mediante el sondeo, el atacante puede obtener detalles de la configuración de seguridad del clúster, lo que puede reducir la seguridad del clúster y aumentar el riesgo de ser vulnerado.

**Medidas de mitigación**

Medida de mitigación
Descripción




Implementar control de acceso estricto
Garantizar que todos los servicios y puertos sean revisados de forma estricta, autorizando únicamente el acceso necesario, para reducir la superficie de ataque potencial


Validación de entrada/salida
Garantizar la seguridad de los Prompts y resultados tanto en la entrada como en la salida del modelo, implementando bloqueo ante comportamientos de ataque sospechosos

**Referencias**

https://mp.weixin.qq.com/s/Ry1PoZLfPvw6Lj8bz14mgw

---
## Fase de despliegue

### Ataque al proceso de CI&CD

> N.º de riesgo: GAARM.0004
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

En todo el ciclo de vida del desarrollo de grandes modelos, el proceso de CI/CD es responsable de llevar el modelo del entorno de desarrollo al entorno de producción, automatizando el despliegue del gran modelo LLM y encargándose de las actualizaciones y el mantenimiento posteriores. El ataque al proceso de CI&CD se refiere a que, durante el proceso en que CI/CD despliega el modelo en el entorno de producción, debido a vulnerabilidades en la infraestructura de CI/CD, la falta de fiabilidad de herramientas de terceros, etc., un atacante puede aprovechar estas vulnerabilidades de seguridad para atacar el proceso de CI/CD, por ejemplo, enviando código malicioso o contaminando paquetes de dependencias, provocando consecuencias graves como la manipulación ilegal del modelo o la filtración de información sensible.

  

Proceso de CI/CD del ciclo de vida de desarrollo de grandes modelos

**Casos de ataque**

Caso
Descripción




Caso 1
Obtener credenciales de desarrolladores u operadores mediante técnicas de phishing, para luego enviar código malicioso en el proceso de CI/CD.


Caso 2
Aprovechar vulnerabilidades de servidores, como vulnerabilidades en infraestructura de CI/CD como Gitlab o Jenkins, para llevar a cabo el ataque.


Caso 3
Atacar dependencias de herramientas y aplicaciones de terceros, por ejemplo, contaminando paquetes de dependencias o falsificando nombres de paquetes de dependencias para subir paquetes maliciosos a repositorios centrales de código abierto.

**Riesgos del ataque**

Contaminación del entorno virtual: el entorno virtual o los contenedores del entorno de integración continua son atacados; el atacante puede manipular las dependencias o la configuración de runtime del entorno, para afectar los resultados del entrenamiento y despliegue del modelo.
Manipulación del proceso de construcción y despliegue: el atacante puede intentar modificar los procesos automatizados de construcción y despliegue, para insertar código u operaciones maliciosas durante el proceso de despliegue del modelo.
Fuga de información sensible: el entorno de integración/entrega continua almacena información sensible (como credenciales de acceso, archivos de configuración, claves, etc.); si es obtenida por un atacante, puede provocar fuga de información sensible y riesgos de privacidad.
Ataque de denegación de servicio: el atacante puede intentar, mediante un ataque de denegación de servicio (DoS), impedir el funcionamiento normal del sistema de integración/entrega continua, provocando la interrupción o retraso del proceso de desarrollo y despliegue del modelo.
Acceso no autorizado al modelo: el proceso de despliegue del modelo es atacado; el atacante puede obtener acceso no autorizado mediante una vulnerabilidad, para realizar operaciones ilegales o manipular el modelo.

**Medidas de mitigación**

Medida de mitigación
Descripción




Reforzar el control de acceso y la gestión de permisos
Limitar los permisos de acceso al sistema de integración/entrega continua y a los entornos relacionados, garantizando que solo el personal autorizado pueda acceder a los recursos clave


Actualizaciones y auditorías de seguridad
Actualizar y auditar periódicamente el software de despliegue del modelo para corregir vulnerabilidades y reforzar la seguridad


Reforzar el monitoreo y el registro de logs
Detectar oportunamente actividades y comportamientos de ataque anómalos, y tomar medidas de respuesta a tiempo, para reducir el riesgo de seguridad potencial y las pérdidas

**Referencias**

https://github.com/knownsec/KCon/blob/master/2023/CICD%E6%94%BB%E5%87%BB%E5%9C%BA%E6%99%AF.pdf

---
### Fallo del aislamiento multiinquilino de la plataforma en la nube

> N.º de riesgo: GAARM.0003.001
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

En una plataforma en la nube con arquitectura multiinquilino, cada inquilino debe contar con un entorno operativo y almacenamiento de datos independientes, garantizando el aislamiento mutuo entre el comportamiento y los datos de los usuarios. El fallo del aislamiento puede deberse a defectos de diseño, errores de configuración, etc. Con la popularización de servicios de cómputo de alto valor, un atacante puede aprovechar esto para romper los límites entre inquilinos, accediendo y manipulando los datos de otros inquilinos, e incluso ejecutando operaciones maliciosas, lo que provoca que los datos y recursos de diferentes inquilinos (usuarios u organizaciones) no puedan protegerse eficazmente, generando una serie de problemas de seguridad.

**Casos de ataque**

Caso
Descripción




Caso 1
Este artículo investiga si "el modelo de IA se ejecuta en un entorno aislado". Wiz aprovechó el servicio de metadatos IMDS en AWS para completar una escalada de privilegios en Amazon EKS y tomar control de todo el clúster, realizando movimiento lateral dentro del clúster EKS, lo que además permitió el acceso entre inquilinos y provocó la fuga de datos sensibles.

**Riesgos del ataque**

Fuga de datos: el fallo del aislamiento multiinquilino puede provocar la mezcla o fuga de datos entre inquilinos, lo que puede incluir información sensible o información de identificación personal.
Disminución de la confianza: los incidentes de seguridad pueden debilitar la confianza de los usuarios en el proveedor del servicio en la nube.

**Medidas de mitigación**

Medida de mitigación
Descripción




Reforzar el control de acceso
Reforzar el control de acceso a los recursos del sistema mediante mecanismos de gestión de permisos como listas de control de acceso (ACL) y control de acceso basado en roles (RBAC)


Monitoreo de recursos
Monitorear el uso de recursos para detectar oportunamente comportamientos anómalos, como el acaparamiento o abuso de recursos

**Referencias**

https://xie.infoq.cn/article/536a3e7e776eb32b38d1a9747
https://www.helloaliyun.com/tutorial/1039.html
https://support.huaweicloud.com/usermanual-gaussdbformysql/gaussdbformysql_05_0347.html

---
### Vulnerabilidades de seguridad de la plataforma en la nube

> N.º de riesgo: GAARM.005
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Debido a la alta demanda de cómputo de las aplicaciones de grandes modelos, estas suelen depender de entornos de plataformas en la nube para completar las tareas de entrenamiento e inferencia, por lo que la seguridad de la plataforma en la nube es crucial para la seguridad del gran modelo. Sin embargo, debido a defectos técnicos, vulnerabilidades técnicas, la falta de autenticación multifactor y otros riesgos de seguridad en las plataformas en la nube, un atacante puede aprovechar estos problemas de seguridad para llevar a cabo ataques maliciosos contra los grandes modelos desplegados en la nube, por ejemplo, leyendo datos sensibles, robando y utilizando ilegalmente credenciales de cuentas, causando una serie de pérdidas a la plataforma, incluyendo, entre otros, fuga de datos, interrupción del servicio y ejecución de código malicioso. Estos ataques no solo afectan la seguridad del gran modelo, sino que también pueden amenazar a otros usuarios que utilizan ese servicio en la nube.

**Casos de ataque**

Caso
Descripción




Caso 1
Se descubrió una vulnerabilidad CSRF en el servicio Amazon SageMaker Notebook; un atacante podría aprovechar la vulnerabilidad para leer datos sensibles y ejecutar operaciones arbitrarias en el entorno del cliente.


Caso 2
Debido a un riesgo de seguridad en el sistema de la versión de Laravel (CVE-2021-3129), vulnerable a ataques, un atacante utilizó credenciales de AWS robadas de Laravel para sondear ilegalmente los servicios de modelos alojados en la nube que dicha credencial podía utilizar; la víctima pudo perder más de 46,000 dólares diarios.

**Riesgos del ataque**

Fuga de datos: debido a vulnerabilidades de seguridad de aplicaciones en la nube, APIs inseguras y otras causas, información sensible puede ser accedida o expuesta públicamente por terceros no autorizados, causando graves problemas de privacidad y cumplimiento normativo.
Acceso no autorizado a la aplicación del modelo: las vulnerabilidades de seguridad de la plataforma en la nube pueden provocar el riesgo de acceso no autorizado a las aplicaciones de modelo desplegadas por el usuario.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control de acceso estricto
Garantizar que solo usuarios autenticados y autorizados puedan acceder a los endpoints de la API


Principio de mínimo privilegio
Implementar el principio de mínimo privilegio, garantizando que usuarios y procesos solo posean los permisos de acceso necesarios para completar su tarea

**Referencias**

https://developer.aliyun.com/article/1430094

---
### Explotación de configuración de sistema insegura

> N.º de riesgo: GAARM.0003
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Este riesgo se refiere a que, en el entorno de infraestructura donde se despliega el modelo, existen una serie de configuraciones de sistema inseguras en el sistema de despliegue del modelo ML, el entorno del clúster de despliegue, el entorno de contenedores de despliegue, el entorno de gestión de push de imágenes, etc., y un atacante lleva a cabo diversos ataques contra el entorno base del modelo aprovechando dichas configuraciones.


Acceso no autorizado: una configuración inadecuada puede provocar la exposición de puertos sensibles o el debilitamiento de los mecanismos de autenticación, permitiendo que usuarios no autorizados accedan a los recursos del sistema;


Riesgo de seguridad de contenedores: una configuración insegura de contenedores puede incluir permisos innecesarios, montaje de archivos sensibles o vulnerabilidades de escape de contenedor;


Riesgo de seguridad del clúster: en clústeres como Kubernetes, una configuración de RBAC inadecuada puede provocar escalada de privilegios o ataques de movimiento lateral;


Riesgo de seguridad de imágenes: una configuración de sistema insegura provoca riesgos como fugas durante las fases de transmisión, gestión y despliegue de la imagen;


Riesgo de aislamiento de entorno: un error de configuración puede provocar el fallo del aislamiento, permitiendo que el atacante acceda o afecte a otros contenedores o a la máquina anfitriona;

**Casos de ataque**

Caso
Descripción




Caso 1
ShadowRay: la primera campaña de ataque conocida dirigida a cargas de trabajo de IA explotadas activamente en el mundo real.

**Riesgos del ataque**

Operación maliciosa: si el sistema está mal configurado, el atacante puede aprovechar estas vulnerabilidades para obtener acceso al sistema y llevar a cabo operaciones maliciosas.
Fuga de datos: el atacante puede obtener datos sensibles, como información del sistema de archivos de la máquina anfitriona o secretos dentro del clúster.
Interrupción del servicio: el atacante puede dañar los servicios de la máquina anfitriona o del clúster, provocando que el servicio quede no disponible.
Movimiento lateral: el atacante puede usar el contenedor del que escapó o el nodo con privilegios escalados como trampolín para atacar otros sistemas dentro de la red interna.
Control persistente: el atacante puede instalar puertas traseras en la máquina anfitriona o en el clúster para lograr un control a largo plazo.

**Medidas de mitigación**

Medida de mitigación
Descripción




Principio de mínimo privilegio
Garantizar que los contenedores y componentes del clúster solo posean el mínimo privilegio necesario para completar su tarea


Garantizar una configuración de sistema segura
Evitar el uso de contenedores privilegiados, configurar RBAC de manera razonable, limitar el acceso al APIServer y evitar exposiciones de riesgo innecesarias


Actualización periódica y gestión de parches
Actualizar oportunamente los contenedores y componentes del clúster, aplicar parches de seguridad, reduciendo el riesgo de explotación de vulnerabilidades

**Referencias**

https://pradiptabanerjee.medium.com/confidential-containers-for-large-language-models-42477436345a

---
### Vulnerabilidades de bases de datos vectoriales

> N.º de riesgo: GAARM.0005 (subriesgo 1, riesgo padre: Vulnerabilidades de la cadena de suministro de componentes del entorno de despliegue)
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Durante el desarrollo de aplicaciones RAG, los diversos documentos locales pueden dividirse en fragmentos de texto más cortos mediante clases de tipo Text, y utilizar un modelo de embedding para vectorizar el contenido del texto, que finalmente se almacena en una base de datos vectorial. La base de datos vectorial desempeña un papel importante en la arquitectura de aplicaciones RAG, especialmente al procesar datos de alta dimensión y ejecutar consultas de vecinos más cercanos aproximados (ANN). Debido a la importancia de la base de datos vectorial, si esta presenta vulnerabilidades, un atacante puede aprovecharlas para obtener acceso no autorizado a datos, manipular datos, ejecutar código malicioso o lanzar otros ataques, con el fin de obtener información sensible, controlar remotamente código malicioso, etc., provocando pérdidas de datos.

**Casos de ataque**

Caso
Descripción




Caso 1
Uso de la API de la base de datos vectorial Qdrant para lograr, tras un path traversal, la carga de archivos, provocando un riesgo de ejecución remota de código.


Caso 2
anything-llm presenta la vulnerabilidad CVE-2024-0551; un atacante no autorizado puede descargar archivos de la base de datos aprovechando la vulnerabilidad.


Caso 3
Esta investigación propone un nuevo método de ataque contra LLMs potenciados con RAG, inyectando un único documento malicioso en su base de datos de conocimiento para comprometer el sistema RAG de la víctima, desencadenando así múltiples ataques maliciosos contra el modelo generativo.

**Riesgos del ataque**

Manipulación de datos: el atacante aprovecha vulnerabilidades de la base de datos vectorial para manipular los vectores de embedding, provocando la alteración de los datos de la base de datos y afectando la integridad de los datos.
Violación de la privacidad del usuario: la base de datos vectorial puede almacenar información sensible como datos de identificación personal; si es obtenida por un atacante, se violará gravemente la privacidad del usuario.

**Medidas de mitigación**

Medida de mitigación
Descripción




Actualización periódica de parches
Estar al tanto de los últimos parches del proveedor de la base de datos vectorial; actualizar periódicamente el software de la base de datos garantiza protección contra vulnerabilidades conocidas


Respaldo de datos
Respaldar los datos periódicamente para garantizar una recuperación rápida en caso de manipulación de datos


Monitoreo y logs
Implementar monitoreo en tiempo real y registro de logs para detectar y responder oportunamente a actividades sospechosas

**Referencias**

https://ironcorelabs.com/security-risks-rag/

---
### Vulnerabilidades del sistema de contenedores y clúster

> N.º de riesgo: GAARM.0005 (subriesgo 2, riesgo padre: Vulnerabilidades de la cadena de suministro de componentes del entorno de despliegue)
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Los riesgos de vulnerabilidades del sistema de contenedores y clúster en el entorno de despliegue de grandes modelos se refieren principalmente a los posibles problemas de seguridad de la tecnología de contenedores y los sistemas de gestión de clústeres en el entorno de despliegue y ejecución de grandes modelos. Un atacante puede aprovechar estas vulnerabilidades para ejecutar código malicioso, robar datos, interferir con el funcionamiento del servicio, etc., provocando fugas de información privada, amenazando así la seguridad y estabilidad del gran modelo.

**Casos de ataque**

Caso
Descripción




Caso 1
La versión de imagen Docker utilizada por OPENAI presentaba la vulnerabilidad CVE-2023-28432; aprovechando esta vulnerabilidad se pueden obtener claves y otra información.

**Riesgos del ataque**

Escape de contenedor: el atacante puede aprovechar vulnerabilidades dentro del contenedor para lograr un escape de contenedor, obteniendo permisos sobre el host u otros contenedores.
Propagación de riesgo en el clúster: la vulnerabilidad de un solo contenedor puede provocar que el riesgo se propague a todo el clúster.

**Medidas de mitigación**

.



Medida de mitigación
Descripción




Actualizar oportunamente los componentes relacionados
Actualizar periódicamente Kubernetes y sus componentes relacionados (como Docker, containerd, etc.) a la última versión, para corregir vulnerabilidades de seguridad conocidas


Control de acceso estricto
Implementar estrategias de control de acceso estrictas, limitando la comunicación entre contenedores y entre los contenedores y el exterior del clúster

**Referencias**

https://www.securityweek.com/chatgpt-data-breach-confirmed-as-security-firm-warns-of-vulnerable-component-exploitation/

---
### Vulnerabilidades del servicio de despliegue del modelo

> N.º de riesgo: GAARM.0004.001
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Las vulnerabilidades del servicio de despliegue de modelos ML pueden existir en la interfaz del modelo, en bibliotecas de soporte, o en aplicaciones que interactúan con el modelo, por ejemplo, aprovechando vulnerabilidades específicas para robar parámetros del modelo, manipular los resultados de predicción del modelo, o controlar directamente el servicio que aloja el modelo. Mediante estas vulnerabilidades, el atacante puede llevar a cabo ataques contra el sistema, como leer archivos arbitrarios, implantar puertas traseras para obtener control del sistema, etc. Dado que el servicio de despliegue de modelos ML normalmente admite empaquetar el modelo en forma de contenedor y desplegarlo en múltiples entornos objetivo, como local, servicios de alojamiento ML en la nube, clústeres K8S en la nube, etc., una vez que el servicio de despliegue de modelos ML es atacado, existe el riesgo de que se roben los permisos de control de múltiples entornos aguas abajo.

**Casos de ataque**

Caso
Descripción




Caso 1
MLFlow presenta una vulnerabilidad de lectura de archivos; el atacante puede leer archivos arbitrarios en el servidor objetivo.


Caso 2
BentoML presenta una vulnerabilidad de ejecución de código por deserialización; el atacante puede desencadenar la explotación de la vulnerabilidad enviando una sola solicitud POST.

**Riesgos del ataque**

Ataque a la cadena de suministro: si la cadena de suministro de las herramientas de despliegue es penetrada por un atacante, este puede implantar puertas traseras en las herramientas, obteniendo así control sobre todo el sistema.
Fuga de datos: el software MLOps abarca múltiples fases clave del entrenamiento y despliegue del modelo; una vez controlado, provocará la fuga de información sensible como datos de entrenamiento y parámetros del modelo.
Manipulación del modelo: los parámetros o la lógica del modelo pueden ser modificados por el atacante, provocando resultados de predicción erróneos.

**Medidas de mitigación**

Medida de mitigación
Descripción




Actualizaciones y auditorías de seguridad
Actualizar y auditar periódicamente el software de despliegue del modelo para corregir vulnerabilidades y reforzar la seguridad


Control de acceso
Implementar medidas de control de acceso estrictas, garantizando que solo usuarios autorizados puedan acceder y modificar el modelo desplegado


Monitoreo y logs
Implementar monitoreo en tiempo real y registro de logs para detectar y responder oportunamente a actividades sospechosas

**Referencias**

http://www.bimant.com/blog/top8-ml-model-deployment-tools/
https://mlflow.org/docs/latest/deployment/index.html

---
### Contaminación de la imagen del modelo

> N.º de riesgo: GAARM.0004.002
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Este riesgo se refiere a que, tras completar la fase de entrenamiento y ajuste fino, la imagen del modelo está a punto de publicarse en el entorno de producción para su despliegue (entorno propio, nube pública o infraestructura de terceros); durante este proceso de publicación, la falta de medidas de protección de seguridad suficientes (como la firma de cifrado durante la transmisión de la imagen del modelo) permite que, mediante la contaminación de la imagen, el atacante controle el funcionamiento del sistema infectado, existiendo riesgos como el secuestro y manipulación del archivo de imagen, lo que afecta el proceso de toma de decisiones del modelo y genera riesgos de seguridad.

  

Despliegue mediante push de la imagen del modelo

**Casos de ataque**

Caso
Descripción




Caso 1
El atacante, controlando el proceso de despliegue de imágenes del sistema CI/CD, implanta código de puerta trasera en la imagen o roba datos sensibles.

**Riesgos del ataque**

Ejecución de comandos: mediante la contaminación de la imagen, el atacante puede controlar el funcionamiento del sistema infectado, ejecutando comandos arbitrarios.
Impacto en la toma de decisiones del modelo: la contaminación maliciosa de la imagen del modelo puede afectar el proceso de toma de decisiones del modelo, generando riesgos de seguridad.

**Medidas de mitigación**

Medida de mitigación
Descripción




Firma de imagen
Utilizar mecanismos de firma y verificación de imágenes, para garantizar la integridad del contenido de la imagen


Uso de hardware confiable
Basado en entornos de ejecución confiables como contenedores confidenciales, garantizar la confidencialidad, integridad y seguridad de los datos en ejecución dinámica


Escaneo de imágenes
Realizar un escaneo de seguridad de las imágenes de contenedores antes del despliegue, para detectar y corregir vulnerabilidades conocidas

**Referencias**

https://www.docker.com/blog/llm-docker-for-local-and-hugging-face-hosting/
https://collabnix.com/large-language-models-llms-and-docker-building-the-next-generation-web-application/
https://mp.weixin.qq.com/s/vIDHBLbA5iWoPlYTKHSZfw

---
### Defectos de aislamiento de entorno

> N.º de riesgo: GAARM.0003.001
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Este riesgo se refiere a que, en la fase de despliegue de contenedores, el entorno de ejecución de la aplicación de negocio LLM y el entorno físico presentan defectos de diseño o configuración en el aislamiento del entorno sandbox; las aplicaciones dentro de entornos sandbox como contenedores o máquinas virtuales pueden tener vulnerabilidades de seguridad que permiten escapar del entorno sandbox, accediendo o manipulando recursos fuera del sandbox. Por lo tanto, aunque el atacante esté limitado dentro del contenedor, puede aprovechar configuraciones erróneas (contenedores privilegiados, montajes de archivos incorrectos, etc.) para eludir el aislamiento, acceder a recursos y sistemas sensibles fuera del contenedor, y aprovechar el cuerpo de ejecución para lograr acceso no autorizado u otras operaciones inesperadas del LLM, trayendo riesgos inesperados como la ejecución de comandos no autorizados.

  

Arquitectura de aislamiento del entorno del cuerpo de ejecución

Dado que los LLM necesitan interactuar con el entorno externo a través de un cuerpo de ejecución, usar Pods en un entorno de clúster para iniciar rápidamente un cuerpo de ejecución que realice operaciones de interacción específicas es una arquitectura común de aislamiento del entorno del cuerpo de ejecución; durante este proceso, si no se realiza un buen aislamiento de red, archivos, procesos, tiempo de vida del Pod y otros aspectos del entorno, se producen riesgos inesperados.

**Casos de ataque**

Caso
Descripción




Caso 1
El entorno de ejecución del modelo de Hugging Face, al no haber implementado una restricción adecuada del acceso a la red externa, permitió que un atacante obtuviera control de shell en el entorno de producción.

**Riesgos del ataque**

Escape de contenedor: un aislamiento de entorno imperfecto puede provocar problemas de escape de contenedor, permitiendo que el atacante obtenga control sobre el sistema host desde el contenedor, e incluso acceda a datos de otros contenedores.
Acceso a bases de datos sensibles: el atacante, mediante Prompts cuidadosamente construidos, indica al LLM que extraiga y filtre información confidencial de bases de datos sensibles.
Operaciones a nivel de sistema: si se permite que el LLM ejecute operaciones a nivel de sistema, el atacante puede manipularlo para ejecutar comandos no autorizados en el sistema subyacente.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control de acceso estricto
Implementar una estrategia de control de acceso basado en roles (RBAC), garantizando que solo el personal autorizado pueda acceder al entorno de ejecución


Aislamiento de red
Utilizar políticas de red para limitar el acceso entre contenedores, entre clústeres y con el exterior, reduciendo la superficie de ataque potencial y el riesgo


Implementar tecnología de sandbox
Utilizar tecnología de sandbox adecuada para aislar el entorno del LLM, evitando que interactúe con sistemas y recursos críticos

**Referencias**

https://cloud.baidu.com/article/621826
https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Inadequate_Sandboxing.html

---
### Vulnerabilidades de la cadena de suministro de componentes del entorno de despliegue

> N.º de riesgo: GAARM.0005 (riesgo padre, incluye los subriesgos: Vulnerabilidades de bases de datos vectoriales, Vulnerabilidades del sistema de contenedores y clúster)
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Las vulnerabilidades de la cadena de suministro del entorno de despliegue (Supply Chain Vulnerabilities in Deployment Environments) se refieren a los defectos de seguridad existentes en la cadena de suministro de software y el proceso de despliegue, desde las materias primas (como bibliotecas, dependencias, herramientas de desarrollo) hasta el producto final (como el software desplegado), que pueden provocar riesgos de vulnerabilidad que lleven al sistema a ser atacado o a la fuga de datos. Las vulnerabilidades de la cadena de suministro pueden ser explotadas durante el despliegue del software, provocando una disminución de la seguridad del sistema, fuga de datos o interrupción del servicio. Se dividen principalmente en tres categorías:


Vulnerabilidades del sistema de contenedores y clúster: la tecnología de contenedores y los sistemas de gestión de clústeres pueden presentar problemas de seguridad; un atacante puede aprovechar estas vulnerabilidades para ejecutar código malicioso, robar datos, interferir con el funcionamiento del servicio, etc., provocando fugas de información privada, amenazando así la seguridad y estabilidad del gran modelo.


Vulnerabilidades de bases de datos vectoriales: si la base de datos vectorial presenta vulnerabilidades, un atacante puede aprovecharlas para obtener acceso no autorizado a datos, manipular datos, ejecutar código malicioso o lanzar otros ataques, con el fin de obtener información sensible, controlar remotamente código malicioso, etc., provocando pérdidas de datos.


Vulnerabilidades de seguridad de la plataforma en la nube: si la plataforma en la nube presenta defectos técnicos, vulnerabilidades técnicas, falta de autenticación multifactor y otros riesgos de seguridad, un atacante puede aprovechar estos problemas de seguridad para llevar a cabo ataques maliciosos contra los grandes modelos desplegados en la nube, por ejemplo, leyendo datos sensibles, robando y utilizando ilegalmente credenciales de cuentas, causando una serie de pérdidas a la plataforma, incluyendo, entre otros, fuga de datos, interrupción del servicio y ejecución de código malicioso.

**Casos de ataque**

Ver detalles en los subriesgos

**Riesgos del ataque**

Fuga de datos: el atacante puede obtener datos sensibles; la información sensible siendo accedida o expuesta públicamente por terceros no autorizados causará graves problemas de privacidad y cumplimiento normativo.
Acceso no autorizado a la aplicación del modelo: las vulnerabilidades de seguridad de la plataforma en la nube pueden provocar el riesgo de acceso no autorizado a las aplicaciones de modelo desplegadas por el usuario.
Violación de la privacidad del usuario: si información sensible almacenada, como datos de identificación personal, es obtenida por un atacante, se violará gravemente la privacidad del usuario.

**Medidas de mitigación**

Medida de mitigación
Descripción




Principio de mínimo privilegio
Garantizar que los componentes solo posean el mínimo privilegio necesario para completar su tarea


Actualización periódica y gestión de parches
Actualizar oportunamente los componentes, aplicar parches de seguridad, reduciendo el riesgo de explotación de vulnerabilidades

---
## Fase de entrenamiento

### Vulnerabilidades de herramientas de desarrollo de modelos

> N.º de riesgo: GAARM.0001.001
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

El desarrollo y entrenamiento de modelos involucra múltiples etapas, como el preprocesamiento de datos, la ingeniería de características, la selección de modelos, el entrenamiento, la evaluación y el despliegue. Si las herramientas utilizadas en este proceso presentan vulnerabilidades de seguridad, todo el flujo de aprendizaje automático se enfrentará a riesgos. Un atacante puede aprovechar estas vulnerabilidades para manipular los datos de entrenamiento del modelo, robar los parámetros del modelo, o ejecutar ataques específicos tras el despliegue del modelo, provocando consecuencias de seguridad graves como salidas inexactas del modelo, robo de parámetros o propagación de malware.

**Casos de ataque**

Caso
Descripción




Caso 1
Tensorflow presenta una vulnerabilidad de ejecución de código; existe riesgo de ejecución de código al cargar el modelo.


Caso 2
Pytorch presenta una vulnerabilidad de ejecución de código; esta vulnerabilidad puede ejecutar código remoto en el sistema objetivo dentro del contexto de usuario que ejecuta el programa, existiendo riesgo de ejecución de código malicioso.


Caso 3
Este documento cubre diferentes casos de uso de TensorFlow, describiendo los problemas de vulnerabilidades de seguridad existentes en TensorFlow, donde diferentes casos de uso conllevan diferentes consecuencias de riesgo.

**Riesgos del ataque**

Ataque a la cadena de suministro: el atacante puede implantar código malicioso en paquetes de software legítimos usados para el desarrollo de ML, llevando a cabo un ataque de cadena de dependencias, propagando así malware durante la distribución.
Envenenamiento del modelo: el atacante inyecta datos maliciosos en los datos de entrenamiento, afectando el proceso de toma de decisiones del modelo, provocando salidas inexactas o sesgadas del modelo.
Pérdida de propiedad intelectual: si los parámetros del modelo son robados, el atacante puede copiar o utilizar ilegalmente dicho modelo.

**Medidas de mitigación**

Medida de mitigación
Descripción




Actualización y aplicación de parches periódicos
Mantener actualizadas todas las herramientas y bibliotecas de desarrollo, para aprovechar las últimas correcciones de seguridad


Cadena de dependencias segura
Revisar la cadena de dependencias, garantizando que todas las bibliotecas y paquetes de terceros provengan de fuentes confiables

**Referencias**

https://www.secrss.com/articles/64006
https://huntr.com/bounties/a795bf93-c91e-4c79-aae8-f7d8bda92e2a

---
### Vulnerabilidades del sistema de gestión de datos de entrenamiento

> N.º de riesgo: GAARM.0001.002
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

El sistema de gestión de datos de entrenamiento es responsable de almacenar, procesar, etiquetar y proporcionar datos, entregando los datos preparados al modelo para su aprendizaje. Cuando este sistema presenta vulnerabilidades de seguridad relacionadas con la cadena de suministro, un atacante puede aprovechar estas vulnerabilidades para manipular datos, robar datos, e incluso afectar los resultados del entrenamiento del modelo mediante el envenenamiento de datos.

**Riesgos del ataque**

Ataque de envenenamiento de datos: el atacante puede inyectar datos maliciosos en los datos de entrenamiento, afectando el proceso de toma de decisiones del modelo, provocando predicciones inexactas o sesgadas del modelo.
Ataque de robo de modelo: el atacante intenta, mediante consultas al modelo, realizar ingeniería inversa y obtener los parámetros o datos de entrenamiento del modelo, robando así propiedad intelectual.
Fuga de datos: el atacante obtiene datos de entrenamiento sensibles mediante acceso no autorizado.

**Medidas de mitigación**

Medida de mitigación
Descripción




Actualizaciones y auditorías de seguridad
Actualizar y auditar periódicamente el sistema de gestión de datos de entrenamiento para corregir vulnerabilidades y reforzar la seguridad


Monitoreo y logs
Implementar monitoreo en tiempo real y registro de logs para detectar y responder oportunamente a actividades sospechosas

**Referencias**

https://doc.dataiku.com/dss/latest/concepts/homepage/index.html
https://www.secrss.com/articles/62742

---
### Riesgo de seguridad del entorno de entrenamiento

> N.º de riesgo: GAARM.0001
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este riesgo se refiere a que, si los frameworks de aprendizaje profundo (como TensorFlow o PyTorch) y las bibliotecas de dependencias necesarias, así como otros componentes de desarrollo de aplicaciones utilizados en el entorno de entrenamiento y desarrollo del modelo, presentan vulnerabilidades de seguridad propias, esto provoca un ataque de cadena de suministro sobre las aplicaciones LLM aguas abajo, afectando así la integridad de los datos de entrenamiento, el modelo ML y la plataforma de despliegue.

**Casos de ataque**

Caso
Descripción




Caso 1
El código de ejemplo de plugins integrados proporcionado por OpenAI incluía una imagen Docker de MinIO con una vulnerabilidad, que podría provocar la fuga de claves y contraseñas; la biblioteca Redis-py utilizada por ChatGPT presentaba una vulnerabilidad que provocó la fuga del historial de chat y la información de pago de los usuarios.


Caso 2
El framework de aprendizaje automático de código abierto PyTorch presentaba una vulnerabilidad grave a nivel de capa, CVE-2024-5480; un atacante podía usarla para atacar remotamente el nodo maestro del entrenamiento distribuido, y una vez comprometidos estos nodos, la otra parte tenía la oportunidad de robar datos sensibles relacionados con la IA.


Caso 3
El formato pickle utilizado por los modelos PyTorch puede ser armado por actores de amenazas para ejecutar código arbitrario y desplegar cargas útiles de ataque de Cobalt Strike, Mythic y Metasploit; un atacante puede comprometer el servicio de conversión alojado utilizando un binario PyTorch malicioso, y comprometer el sistema de alojamiento de archivos.

**Riesgos del ataque**

Fuga de privacidad del usuario: como se muestra en el caso 1, debido a un bug de la biblioteca Redis-py, el título del historial de chat y el contenido de las conversaciones de los usuarios de ChatGPT pudieron ser vistos por otros usuarios, provocando la fuga de datos privados de los usuarios.
Daño a la integridad del sistema: el atacante puede aprovechar vulnerabilidades para dañar la integridad del sistema, afectando la confiabilidad y disponibilidad del servicio LLM.

**Medidas de mitigación**

Medida de mitigación
Descripción




Actualizaciones y auditorías de seguridad
Actualizar y auditar periódicamente el software de servicio en el entorno de entrenamiento y desarrollo para corregir vulnerabilidades y reforzar la seguridad


Auditoría y monitoreo de seguridad
Realizar auditorías de seguridad periódicas, utilizando herramientas de monitoreo para detectar y alertar sobre comportamientos sospechosos, y llevar a cabo un registro de logs eficaz

**Referencias**

https://llmtop10.com/llm05/

---
### Defectos de aislamiento del entorno de entrenamiento

> N.º de riesgo: GAARM.0002
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

El aislamiento del entorno de entrenamiento se refiere a dividir el entorno de depuración y el entorno de ejecución en dos áreas completamente aisladas, con el fin de evitar que el entorno de depuración pueda penetrar el entorno de ejecución. En el entorno de depuración se puede modificar la lógica del programa, pero solo se pueden usar datos anonimizados; mientras que en el entorno de ejecución se pueden operar datos reales y completos, y las operaciones están sujetas a revisión, siendo los resultados rastreables y responsabilizables. Si el aislamiento del entorno de entrenamiento presenta defectos, permitiendo pasar del entorno de desarrollo al entorno de pruebas de ejecución, esto provocará que usuarios no autorizados accedan a datos sensibles, dando pie al atacante.

**Casos de ataque**

Caso
Descripción




Caso 1
Un defecto en el aislamiento del entorno de entrenamiento provocó que el atacante pasara del entorno de desarrollador al entorno de pruebas de ejecución, produciéndose así riesgos como la fuga de datos de entrenamiento.

**Riesgos del ataque**

Fuga de datos: el atacante puede acceder y robar datos sensibles almacenados en el entorno de ejecución; la fuga de estos datos puede provocar pérdidas económicas significativas y responsabilidad legal.
Obtención del control del sistema: si el atacante penetra en el entorno de ejecución, puede obtener el control del sistema, manipulando así el acceso a datos, la gestión de recursos y la configuración del sistema.

**Medidas de mitigación**

Medida de mitigación
Descripción




Reforzar las medidas de aislamiento
Usar tecnologías de seguridad y mejores prácticas para reforzar el aislamiento entre el entorno de depuración y el entorno de ejecución


Control de acceso
Implementar una estrategia de control de acceso basado en roles (RBAC), garantizando que solo el personal autorizado pueda acceder al entorno de ejecución


Tecnología de sandbox de seguridad
Aislar y proteger el entorno de ejecución del LLM, para evitar que sufra ataques e interferencias externas


**Referencias**

- https://cloud.baidu.com/article/621826

---

## 20. Metodología práctica de pruebas de escape de contenedores y sandbox

> Pruebas sistemáticas de escape y aislamiento para entornos de despliegue de aplicaciones de IA (Docker/Sysbox/Daytona/Kubernetes)
> **Seguridad general del despliegue en contenedores**: Verificación de seguridad del despliegue en contenedores de aplicaciones web → [web-deployment-security.md §2](web-deployment-security.md)

### 1. Visión general del flujo de pruebas

```
Recolección de información → Identificación del entorno → Evaluación de aislamiento → Intento de escape → Verificación de persistencia → Movimiento lateral → Informe
```

### 2. Fase de recolección de información

#### 2.1 Identificación del runtime de contenedores

| Elemento a verificar | Comando | Criterio de evaluación |
|--------|------|----------|
| Si se está dentro de un contenedor | `cat /proc/1/cgroup` | Contiene `docker`/`kubepods`/`containerd` |
| Archivo indicador de Docker | `ls /.dockerenv` | Si el archivo existe, es un contenedor Docker |
| Tipo de runtime de contenedores | `cat /proc/1/cgroup \| head` | `sysbox-fs`→Sysbox, `docker`→Docker |
| Versión del kernel | `uname -r` | Corresponder con el alcance de impacto de CVEs |
| User Namespace | `cat /proc/self/uid_map` | `0 0 4294967295`→sin aislamiento (peligroso) |
| Capabilities | `cat /proc/self/status \| grep Cap` | Decodificar y verificar Caps peligrosas |
| Seccomp | `cat /proc/self/status \| grep Seccomp` | 0=disabled, 2=filter |
| AppArmor | `cat /proc/self/attr/current` | `unconfined`→sin protección |
| Puntos de montaje | `mount \| grep -v overlay` | Detectar montajes de rutas sensibles del host |

#### 2.2 Detección específica de Sysbox

| Elemento a verificar | Método | Impacto en seguridad |
|--------|------|----------|
| Versión CE vs EE | `sysbox-runc --version` o verificar el rango de mapeo de UID | El mapeo compartido de CE conlleva riesgo entre inquilinos |
| Exclusividad del mapeo de UID | `cat /proc/self/uid_map`, CE normalmente `0 165536 65536` (compartido) | Mapeo compartido→posible escalada de privilegios entre contenedores |
| Virtualización de /proc | `ls /proc/sys/net/` | Grado de virtualización de Sysbox |
| Docker-in-Docker | `docker ps 2>/dev/null` | El Docker interno puede no tener restricciones de seguridad |
| /dev/kvm | `ls /dev/kvm` | KVM disponible→escape mediante virtualización anidada |

### 3. Fase de evaluación de aislamiento

#### 3.1 Aislamiento de procesos

```bash
# Verificación del PID Namespace
ps aux   # ¿Se pueden ver procesos de otros contenedores/del host?
ls /proc/*/cmdline   # Enumerar procesos visibles

# Si el PID 1 no es el init del contenedor sino systemd/dockerd → fallo de aislamiento
cat /proc/1/cmdline | tr '\0' ' '
```

#### 3.2 Aislamiento de red

```bash
# Interfaces de red
ip addr   # Verificar interfaces de red y segmentos IP
ip route  # Tabla de rutas, ¿se puede llegar a otros segmentos de red?

# Escaneo del mismo segmento de red (descubrir contenedores vecinos)
for i in $(seq 1 254); do
  (ping -c 1 -W 1 $SUBNET.$i &>/dev/null && echo "$SUBNET.$i alive") &
done; wait

# Sondeo de DNS interno
cat /etc/resolv.conf
nslookup kubernetes.default.svc.cluster.local 2>/dev/null
```

#### 3.3 Aislamiento del sistema de archivos

```bash
# Verificar montajes del sistema de archivos del host
mount | grep -E "ext4|xfs|btrfs" | grep -v overlay
findmnt

# Prueba de path traversal
ls -la /var/lib/sysbox/ 2>/dev/null
ls -la /var/lib/docker/ 2>/dev/null
ls -la /run/containerd/ 2>/dev/null

# Escape mediante enlace simbólico
ln -s /proc/1/root/etc/shadow /tmp/test_escape
cat /tmp/test_escape 2>&1  # Si tiene éxito→fallo de aislamiento
```

### 4. Matriz de pruebas de escape

| Ruta de escape | Condición previa | Nivel de peligro | Método de prueba |
|----------|----------|----------|----------|
| cgroup release_agent | CAP_SYS_ADMIN + cgroup v1 | Critical | Escribir en release_agent para ejecutar comandos en el host |
| Docker Socket | /var/run/docker.sock expuesto | Critical | Crear contenedor privilegiado vía API |
| /proc/1/root | PID Namespace sin aislar | Critical | Leer/escribir archivos del host directamente |
| Contenedor privilegiado | modo --privileged | Critical | Montar el disco del host |
| Fuga de fd de runc | CVE-2024-21626 | High | Aprovechar /proc/self/fd para acceder al host |
| Dirty Pipe | CVE-2022-0847, 5.8≤kernel≤5.16.11 | High | Sobrescribir archivos de solo lectura para escalar privilegios |
| OverlayFS | CVE-2023-0386, 5.11≤kernel≤6.2 | High | Escalada de privilegios mediante archivo SUID |
| Montaje sensible | Ruta del host montada dentro del contenedor | High | Escribir en archivos del host |
| CAP_DAC_READ_SEARCH | Capability sin restringir | Medium | Leer archivos con open_by_handle_at |
| CAP_SYS_PTRACE | Capability sin restringir | Medium | Inyectar en procesos del host |
| Docker-in-Docker | Docker interno sin restricciones | Medium | Crear contenedor privilegiado en la capa interna |

### 5. Pruebas de persistencia

> Verifica la viabilidad de ataques de persistencia entre sesiones del sandbox (especialmente aplicable a sandboxes persistentes como Daytona)

| Elemento de prueba | Operación en sesión 1 | Verificación en sesión 2 | Resultado de seguridad esperado |
|--------|-----------|-----------|-------------|
| Backdoor en .bashrc | `echo 'malicious_cmd' >> ~/.bashrc` | Abrir un nuevo shell y verificar si se ejecuta | La nueva sesión no hereda/se reinicia |
| Crontab | `echo "* * * * * cmd" \| crontab -` | `crontab -l` | El crontab se limpia o no está disponible |
| Clave SSH | Escribir en ~/.ssh/authorized_keys | Prueba de conexión SSH | El servicio SSH no está disponible o la clave se limpia |
| Proceso en segundo plano | `nohup cmd &` | `ps aux \| grep cmd` | El proceso termina al cerrar la sesión |
| Envenenamiento de archivos | Escribir archivo malicioso en el workspace | ¿La IA lo lee y ejecuta? | La IA no ejecuta automáticamente instrucciones del archivo |
| Residuos de historial | Ingresar comandos sensibles en el shell | `cat ~/.bash_history` | El historial de comandos se borra entre sesiones |
| Variables de entorno | `export SECRET=leaked` | `echo $SECRET` | Las variables de entorno no se conservan entre sesiones |

### 6. Pruebas de movimiento lateral

```
Dentro del contenedor → Descubrimiento de servicios de red interna → Conexión directa a base de datos/caché/API → Sandbox de otros inquilinos
         ↓
         Servicio de metadatos en la nube (169.254.169.254) → Robo de credenciales IAM → Acceso a recursos en la nube
         ↓
         API de K8s (kubernetes.default.svc) → Obtención de lista de Pods/Secrets
```

| Objetivo | Comando de detección | Método de explotación |
|------|----------|----------|
| Metadatos en la nube | `curl 169.254.169.254` | Obtener credenciales IAM temporales |
| API de K8s | `curl -k https://kubernetes.default.svc` | Enumerar Pods/obtener Secrets |
| K8s ServiceAccount | `cat /var/run/secrets/kubernetes.io/serviceaccount/token` | Autenticarse ante la API de K8s |
| Base de datos de red interna | `echo \| nc DB_HOST 5432` | Conexión directa a la base de datos |
| Redis | `redis-cli -h REDIS_HOST ping` | Acceso no autorizado |
| Docker Registry | `curl http://REGISTRY:5000/v2/_catalog` | Extraer imágenes sensibles |

### 7. Checklist de verificación de defensas

```
[ ] El contenedor se ejecuta como usuario no root (o el aislamiento de User Namespace es efectivo)
[ ] Sin Capabilities superfluas (principio mínimo: solo elementos necesarios como NET_BIND_SERVICE)
[ ] El perfil de Seccomp está habilitado (no disabled)
[ ] AppArmor/SELinux no está en unconfined
[ ] /var/run/docker.sock no está expuesto
[ ] No se ejecuta en modo --privileged
[ ] Sin montajes de rutas sensibles del host (/, /etc, /var/run)
[ ] La versión del kernel no está afectada por CVEs de escape conocidas
[ ] cgroup v2 o release_agent no es escribible
[ ] El aislamiento de PID Namespace es efectivo (solo se ven procesos propios)
[ ] Network Policy/firewall restringe la comunicación entre contenedores
[ ] El servicio de metadatos 169.254.169.254 está bloqueado
[ ] Los datos sensibles entre sesiones (history/credentials) se limpian
[ ] Al destruir el sandbox se eliminan por completo todos los datos del usuario
[ ] Sysbox usa la versión EE o mapeo de UID exclusivo
```

---

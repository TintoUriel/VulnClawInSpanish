# Seguridad de la base de IA - Fase de despliegue

> Fuente: Comunidad de Seguridad de Grandes Modelos AISS NSFOCUS | Extraído de ai-baseline-security.md
> Fase: Fase de despliegue (vulnerabilidades de contenedores/plataforma en la nube/cadena de suministro)

## Fase de despliegue

### Ataque al flujo de CI&CD

> Número de riesgo: GAARM.0004
> Ciclo de vida: Fase de despliegue

**Descripción del ataque**

En todo el ciclo de vida del desarrollo de grandes modelos, el flujo de CI/CD es responsable de llevar el modelo del entorno de desarrollo al entorno de producción, desplegando automáticamente el gran modelo de LLM y encargándose de las actualizaciones y el mantenimiento posteriores. El ataque al flujo de CI&CD se refiere a que, durante el proceso en que CI/CD lleva el modelo al entorno de producción, debido a vulnerabilidades en la infraestructura de CI/CD, la poca fiabilidad de herramientas de terceros, etc., un atacante puede aprovechar estas vulnerabilidades de seguridad para atacar el flujo de CI/CD, por ejemplo, enviando código malicioso o contaminando paquetes de dependencias, provocando consecuencias graves como la alteración ilegítima del modelo o la filtración de información sensible.

  

Flujo de CI/CD del ciclo de vida de desarrollo de grandes modelos

**Casos de ataque**

Caso
Descripción




Caso 1
Obtener credenciales de desarrolladores o personal de operaciones mediante técnicas de phishing, para posteriormente enviar código malicioso en el flujo de CI/CD.


Caso 2
Aprovechar vulnerabilidades de servidores, como vulnerabilidades en infraestructura de CI/CD como GitLab o Jenkins, para llevar a cabo el ataque.


Caso 3
Atacar la dependencia de herramientas y aplicaciones de terceros, por ejemplo, contaminando paquetes de dependencias o falsificando nombres de paquetes de dependencias para subir paquetes maliciosos a repositorios centrales de código abierto.

**Riesgos del ataque**

Contaminación del entorno virtual: el entorno virtual o los contenedores del entorno de integración continua son atacados, y el atacante puede alterar las dependencias o la configuración del runtime del entorno para afectar los resultados del entrenamiento y despliegue del modelo.
Alteración del flujo de construcción y despliegue: el atacante puede intentar modificar el flujo automatizado de construcción y despliegue para insertar código u operaciones maliciosas durante el proceso de despliegue del modelo.
Filtración de información sensible: el entorno de integración continua/entrega continua almacena información sensible (como credenciales de acceso, archivos de configuración, claves, etc.); una vez obtenida por el atacante, puede provocar la filtración de información sensible y riesgos de privacidad.
Ataque de denegación de servicio: el atacante puede intentar, mediante un ataque de denegación de servicio (DoS), impedir el funcionamiento normal del sistema de integración/entrega continua, provocando la interrupción o el retraso del proceso de desarrollo y despliegue del modelo.
Acceso no autorizado al modelo: el proceso de despliegue del modelo es atacado, y el atacante puede, aprovechando una vulnerabilidad, obtener acceso no autorizado, realizando operaciones ilegítimas o alterando el modelo.

**Medidas de mitigación**

Medida de mitigación
Descripción




Reforzar el control de acceso y la gestión de permisos
Limitar los permisos de acceso al sistema de integración/entrega continua y a los entornos relacionados, garantizando que solo el personal autorizado pueda acceder a los recursos clave.


Actualizaciones y auditorías de seguridad
Actualizar y auditar periódicamente el software de despliegue del modelo para corregir vulnerabilidades y reforzar la seguridad.


Reforzar el monitoreo y el registro
Detectar oportunamente actividades anómalas y comportamientos de ataque, tomando medidas de respuesta oportunas para reducir posibles riesgos de seguridad y pérdidas.

**Referencias**

https://github.com/knownsec/KCon/blob/master/2023/CICD%E6%94%BB%E5%87%BB%E5%9C%BA%E6%99%AF.pdf

---
### Fallo del aislamiento multiinquilino en la plataforma en la nube

> Número de riesgo: GAARM.0003.001
> Ciclo de vida: Fase de despliegue

**Descripción del ataque**

En una plataforma en la nube con arquitectura multiinquilino, cada inquilino debe contar con un entorno operativo y un almacenamiento de datos independientes, garantizando el aislamiento mutuo entre el comportamiento de los usuarios y sus datos. El fallo de aislamiento puede deberse a defectos de diseño, errores de configuración, etc. Con la creciente adopción de servicios de cómputo de alto valor, un atacante puede aprovechar esto para romper los límites entre inquilinos, accediendo y alterando datos de otros inquilinos, e incluso ejecutando operaciones maliciosas, provocando que los datos y recursos de distintos inquilinos (usuarios u organizaciones) no puedan protegerse eficazmente, generando una serie de problemas de seguridad.

**Casos de ataque**

Caso
Descripción




Caso 1
Este artículo investiga si "el modelo de IA se ejecuta en un entorno aislado". Wiz aprovechó el servicio de metadatos IMDS de AWS para escalar privilegios en Amazon EKS, tomando el control de todo el clúster, moviéndose lateralmente dentro del clúster EKS, y logrando posteriormente un acceso entre inquilinos que provocó la filtración de datos sensibles.

**Riesgos del ataque**

Filtración de datos: el fallo del aislamiento multiinquilino puede provocar la mezcla o filtración de datos entre inquilinos, lo que puede incluir información sensible o información de identidad personal.
Disminución de la confianza: los incidentes de seguridad pueden debilitar la confianza del usuario en el proveedor de servicios en la nube.

**Medidas de mitigación**

Medida de mitigación
Descripción




Reforzar el control de acceso
Reforzar el control de acceso a los recursos del sistema mediante mecanismos de control de permisos como listas de control de acceso (ACL) y control de acceso basado en roles (RBAC).


Monitoreo de recursos
Monitorear el uso de recursos, detectando oportunamente comportamientos anómalos como el acaparamiento o abuso de recursos.

**Referencias**

https://xie.infoq.cn/article/536a3e7e776eb32b38d1a9747
https://www.helloaliyun.com/tutorial/1039.html
https://support.huaweicloud.com/usermanual-gaussdbformysql/gaussdbformysql_05_0347.html

---
### Vulnerabilidades de seguridad de la plataforma en la nube

> Número de riesgo: GAARM.005
> Ciclo de vida: Fase de despliegue

**Descripción del ataque**

Debido a la alta demanda de capacidad de cómputo, las aplicaciones de grandes modelos suelen depender del entorno de plataformas en la nube para completar tareas de entrenamiento e inferencia; por lo tanto, la seguridad de la plataforma en la nube es crucial para la seguridad del gran modelo. Sin embargo, debido a defectos técnicos de la plataforma en la nube, vulnerabilidades técnicas, falta de autenticación multifactor, entre otras causas de riesgos de seguridad, un atacante puede aprovechar estos problemas de seguridad para llevar a cabo ataques maliciosos contra grandes modelos desplegados en la nube, por ejemplo, leyendo datos sensibles o robando y usando ilegítimamente credenciales de cuenta, causando a la plataforma una serie de pérdidas que incluyen, entre otras, filtración de datos, interrupción del servicio y ejecución de código malicioso. Estos ataques no solo afectan la seguridad del gran modelo, sino que también pueden amenazar a otros usuarios que usan ese servicio en la nube.

**Casos de ataque**

Caso
Descripción




Caso 1
Se descubrió una vulnerabilidad CSRF en el servicio Amazon SageMaker Notebook; un atacante podría aprovechar la vulnerabilidad para leer datos sensibles y ejecutar operaciones arbitrarias en el entorno del cliente.


Caso 2
Debido a un riesgo de seguridad en el sistema de la versión de Laravel (CVE-2021-3129), vulnerable a ataques, un atacante aprovechó credenciales de AWS robadas de Laravel para sondear ilegítimamente los servicios de modelos alojados en la nube a los que dichas credenciales tenían acceso; la víctima llegó a perder más de 46,000 dólares por día.

**Riesgos del ataque**

Filtración de datos: debido a vulnerabilidades de seguridad de aplicaciones en la nube, API inseguras, entre otras causas, información sensible puede ser accedida o hecha pública por terceros no autorizados, provocando graves problemas de privacidad y cumplimiento.
Acceso no autorizado a la aplicación del modelo: las vulnerabilidades de seguridad de la plataforma en la nube pueden provocar riesgos de acceso no autorizado en las aplicaciones de modelo desplegadas por el usuario.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control de acceso estricto
Garantizar que solo usuarios autenticados y autorizados puedan acceder a los endpoints de la API.


Principio de mínimo privilegio
Aplicar el principio de mínimo privilegio, garantizando que usuarios y procesos solo tengan los permisos de acceso necesarios para completar su tarea.

**Referencias**

https://developer.aliyun.com/article/1430094

---
### Explotación de configuración de sistema insegura

> Número de riesgo: GAARM.0003
> Ciclo de vida: Fase de despliegue

**Descripción del ataque**

Este riesgo se refiere a que, en el entorno de infraestructura donde se despliega el modelo, existe una serie de configuraciones de sistema inseguras en el sistema de despliegue del modelo de ML, el entorno del clúster de despliegue, el entorno de contenedores de despliegue, el entorno de gestión de envío de imágenes, entre otros, y el atacante lleva a cabo diversos comportamientos de ataque contra el entorno base del modelo aprovechando dichas configuraciones.


Acceso no autorizado: una configuración inadecuada puede exponer puertos sensibles o debilitar los mecanismos de autenticación, permitiendo que usuarios no autorizados accedan a los recursos del sistema.


Riesgo de seguridad de contenedores: una configuración insegura de contenedores puede incluir permisos innecesarios, montaje de archivos sensibles o vulnerabilidades de escape de contenedor.


Riesgo de seguridad del clúster: en clústeres como Kubernetes, una configuración RBAC inadecuada puede provocar escalamiento de privilegios o ataques de movimiento lateral.


Riesgo de seguridad de imágenes: una configuración de sistema insegura provoca riesgos de filtración en las fases de transmisión, gestión y despliegue de las imágenes.


Riesgo de aislamiento del entorno: un error de configuración puede provocar un fallo de aislamiento, permitiendo que el atacante acceda o afecte a otros contenedores o al host.

**Casos de ataque**

Caso
Descripción




Caso 1
ShadowRay: la primera campaña de ataque conocida dirigida a cargas de trabajo de IA activamente explotadas en el mundo real.

**Riesgos del ataque**

Operación maliciosa: si la configuración del sistema es inadecuada, el atacante puede aprovechar estas vulnerabilidades para obtener acceso al sistema y realizar operaciones maliciosas.
Filtración de datos: el atacante puede obtener datos sensibles, como información del sistema de archivos del host o secrets dentro del clúster.
Interrupción del servicio: el atacante puede dañar el servicio del host o del clúster, provocando que el servicio no esté disponible.
Movimiento lateral: el atacante puede usar el contenedor comprometido o el nodo con privilegios escalados como punto de apoyo para atacar otros sistemas de la red interna.
Control persistente: el atacante puede instalar una puerta trasera en el host o el clúster, logrando un control a largo plazo.

**Medidas de mitigación**

Medida de mitigación
Descripción




Principio de mínimo privilegio
Garantizar que los contenedores y los componentes del clúster solo tengan el mínimo privilegio necesario para completar su tarea.


Garantizar una configuración de sistema segura
Evitar el uso de contenedores privilegiados, configurar RBAC de forma adecuada, limitar el acceso al APIServer y evitar la exposición innecesaria a riesgos.


Actualización periódica y gestión de parches
Actualizar oportunamente los contenedores y componentes del clúster, aplicando parches de seguridad para reducir el riesgo de explotación de vulnerabilidades.

**Referencias**

https://pradiptabanerjee.medium.com/confidential-containers-for-large-language-models-42477436345a

---
### Vulnerabilidades de la base de datos vectorial

> Número de riesgo: GAARM.0005 (subriesgo 1, riesgo padre: vulnerabilidades de la cadena de suministro de componentes del entorno de despliegue)
> Ciclo de vida: Fase de despliegue

**Descripción del ataque**

Durante el desarrollo de aplicaciones RAG, los diversos documentos de datos locales pueden dividirse en párrafos más cortos mediante clases de texto, y usar un modelo de embeddings para vectorizar el contenido de texto, almacenándolo finalmente en una base de datos vectorial. La base de datos vectorial desempeña un papel importante en la arquitectura de aplicaciones RAG, especialmente al procesar datos de alta dimensión y realizar consultas de vecinos más cercanos aproximados (ANN). Debido a la importancia de la base de datos vectorial, si esta presenta una vulnerabilidad, el atacante puede aprovecharla para obtener acceso no autorizado a los datos, alterar datos, ejecutar código malicioso o iniciar otros ataques, con el fin de obtener información sensible, controlar código malicioso de forma remota, etc., causando pérdidas de datos.

**Casos de ataque**

Caso
Descripción




Caso 1
Aprovechando la API de la base de datos vectorial Qdrant, se logró la subida de archivos tras un path traversal, provocando un riesgo de ejecución remota de código.


Caso 2
anything-llm presenta la vulnerabilidad CVE-2024-0551; un atacante no autorizado puede descargar archivos de la base de datos aprovechando la vulnerabilidad.


Caso 3
Esta investigación propone un nuevo método de ataque dirigido a LLM potenciados con RAG, inyectando un único documento malicioso en su base de datos de conocimiento para comprometer el sistema RAG de la víctima, provocando así diversos ataques maliciosos contra el modelo generativo.

**Riesgos del ataque**

Alteración de datos: el atacante aprovecha la vulnerabilidad de la base de datos vectorial para alterar los vectores de embeddings, provocando que los datos de la base de datos sean modificados, afectando así la integridad de los datos.
Violación de la privacidad del usuario: la base de datos vectorial puede almacenar información sensible como la identidad personal; una vez obtenida por el atacante, se violará gravemente la privacidad del usuario.

**Medidas de mitigación**

Medida de mitigación
Descripción




Actualización periódica de parches
Estar al tanto de los últimos parches del proveedor de la base de datos vectorial, actualizando periódicamente el software de la base de datos para garantizar protección frente a vulnerabilidades conocidas.


Copia de seguridad de datos
Realizar copias de seguridad periódicas de los datos, garantizando una rápida recuperación en caso de alteración de los datos.


Monitoreo y registro
Implementar monitoreo y registro en tiempo real, para detectar y responder oportunamente ante actividades sospechosas.

**Referencias**

https://ironcorelabs.com/security-risks-rag/

---
### Vulnerabilidades del sistema de contenedores y clústeres

> Número de riesgo: GAARM.0005 (subriesgo 2, riesgo padre: vulnerabilidades de la cadena de suministro de componentes del entorno de despliegue)
> Ciclo de vida: Fase de despliegue

**Descripción del ataque**

El riesgo de vulnerabilidades del sistema de contenedores y clústeres en el entorno de despliegue de grandes modelos se refiere principalmente a los posibles problemas de seguridad en la tecnología de contenedores y los sistemas de gestión de clústeres dentro del entorno de despliegue y ejecución de grandes modelos. Un atacante puede aprovechar estas vulnerabilidades para ejecutar código malicioso, robar datos, interferir en el funcionamiento del servicio, entre otros, provocando problemas de filtración de información privada y amenazando así la seguridad y estabilidad del gran modelo.

**Casos de ataque**

Caso
Descripción




Caso 1
La versión de la imagen Docker usada por OpenAI presentaba la vulnerabilidad CVE-2023-28432; aprovechando esta vulnerabilidad se podía obtener información como claves.

**Riesgos del ataque**

Escape de contenedor: el atacante puede, mediante una vulnerabilidad dentro del contenedor, lograr un escape de contenedor, obteniendo privilegios del host o de otros contenedores.
Propagación del riesgo en el clúster: una vulnerabilidad en un único contenedor puede provocar la propagación del riesgo a todo el clúster.

**Medidas de mitigación**




Medida de mitigación
Descripción




Actualizar oportunamente los componentes relacionados
Actualizar periódicamente Kubernetes y sus componentes relacionados (como Docker, containerd, etc.) a la última versión, para corregir vulnerabilidades de seguridad conocidas.


Control de acceso estricto
Implementar una política de control de acceso estricta, limitando la comunicación entre contenedores y entre los contenedores y el exterior del clúster.

**Referencias**

https://www.securityweek.com/chatgpt-data-breach-confirmed-as-security-firm-warns-of-vulnerable-component-exploitation/

---
### Vulnerabilidades del servicio de despliegue del modelo

> Número de riesgo: GAARM.0004.001
> Ciclo de vida: Fase de despliegue

**Descripción del ataque**

Las vulnerabilidades del servicio de despliegue de modelos de ML pueden existir en la interfaz del modelo, en bibliotecas de soporte, o en aplicaciones que interactúan con el modelo, por ejemplo, permitiendo robar parámetros del modelo, alterar resultados de predicción del modelo, o controlar directamente el servicio que aloja el modelo, aprovechando una vulnerabilidad específica. Mediante la vulnerabilidad, el atacante puede llevar a cabo ataques al sistema, como leer archivos arbitrarios, implantar puertas traseras para obtener el control del sistema, etc. Dado que el servicio de despliegue de modelos de ML normalmente soporta el envío del modelo en forma de contenedor a diversos entornos objetivo, como local, servicios de alojamiento de ML en plataformas en la nube, clústeres K8S en la nube, entre otros, una vez que el servicio de despliegue de modelos de ML es atacado, existirá el riesgo de que los permisos de control de múltiples entornos posteriores sean robados.

**Casos de ataque**

Caso
Descripción




Caso 1
MLFlow presenta una vulnerabilidad de lectura de archivos; un atacante puede leer cualquier archivo del servidor objetivo.


Caso 2
BentoML presenta una vulnerabilidad de ejecución de código mediante deserialización; un atacante puede activar la explotación de la vulnerabilidad enviando una única solicitud POST.

**Riesgos del ataque**

Ataque a la cadena de suministro: si la cadena de suministro de la herramienta de despliegue es infiltrada por un atacante, este puede implantar una puerta trasera en la herramienta, obteniendo así el control de todo el sistema.
Filtración de datos: el software MLOps abarca múltiples fases clave del entrenamiento y despliegue del modelo; una vez comprometido, puede provocar la filtración de información sensible como datos de entrenamiento y parámetros del modelo.
Alteración del modelo: los parámetros o la lógica del modelo pueden ser modificados por el atacante, provocando resultados de predicción erróneos.

**Medidas de mitigación**

Medida de mitigación
Descripción




Actualizaciones y auditorías de seguridad
Actualizar y auditar periódicamente el software de despliegue del modelo para corregir vulnerabilidades y reforzar la seguridad.


Control de acceso
Implementar medidas de control de acceso estrictas, garantizando que solo usuarios autorizados puedan acceder y modificar el modelo desplegado.


Monitoreo y registro
Implementar monitoreo y registro en tiempo real, para detectar y responder oportunamente ante actividades sospechosas.

**Referencias**

http://www.bimant.com/blog/top8-ml-model-deployment-tools/
https://mlflow.org/docs/latest/deployment/index.html

---
### Contaminación de la imagen del modelo

> Número de riesgo: GAARM.0004.002
> Ciclo de vida: Fase de despliegue

**Descripción del ataque**

Este riesgo se refiere a que, una vez que el modelo completa la fase de entrenamiento y fine-tuning, la imagen del modelo está a punto de publicarse en el entorno de producción para su despliegue (entorno propio, nube pública o infraestructura de terceros), y durante este proceso de publicación no existen medidas de protección de seguridad suficientes (como la firma cifrada durante la transmisión de la imagen del modelo). Mediante la contaminación de la imagen, el atacante puede controlar el funcionamiento del sistema infectado; existe el riesgo de que el archivo de imagen sea secuestrado y alterado, afectando el proceso de toma de decisiones del modelo y generando riesgos de seguridad.

  

Envío y despliegue de la imagen del modelo

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




Firma de imágenes
Usar mecanismos de firma y verificación de imágenes, garantizando la integridad del contenido de la imagen.


Uso de hardware confiable
Basándose en entornos de ejecución confiables como contenedores confidenciales, garantizar la confidencialidad, integridad y seguridad de los datos en ejecución dinámica.


Escaneo de imágenes
Realizar un escaneo de seguridad de las imágenes de contenedores antes del despliegue, para detectar y corregir vulnerabilidades conocidas.

**Referencias**

https://www.docker.com/blog/llm-docker-for-local-and-hugging-face-hosting/
https://collabnix.com/large-language-models-llms-and-docker-building-the-next-generation-web-application/
https://mp.weixin.qq.com/s/vIDHBLbA5iWoPlYTKHSZfw

---
### Defectos en el aislamiento del entorno

> Número de riesgo: GAARM.0003.001
> Ciclo de vida: Fase de despliegue

**Descripción del ataque**

Este riesgo se refiere a que, durante la fase de despliegue de contenedores, el entorno de ejecución de la aplicación de negocio de LLM y el entorno físico presentan defectos de configuración o diseño en el aislamiento del entorno sandbox. Las aplicaciones dentro de entornos sandbox como contenedores o máquinas virtuales pueden presentar vulnerabilidades de seguridad que permiten escapar del entorno sandbox y acceder o manipular recursos fuera del sandbox. Por lo tanto, incluso si el atacante está limitado dentro del contenedor, puede aprovechar configuraciones incorrectas (contenedores privilegiados, montajes de archivos incorrectos, etc.) para eludir el aislamiento, accediendo a recursos y sistemas sensibles fuera del contenedor, y posteriormente aprovechar el ejecutor para lograr acceso no autorizado u otras operaciones no previstas del LLM, generando riesgos imprevistos como la ejecución de comandos no autorizados.

  

Arquitectura de aislamiento del entorno del ejecutor

Dado que el LLM necesita interactuar con el entorno externo a través de un ejecutor, usar Pods en un entorno de clúster para iniciar rápidamente el ejecutor y realizar operaciones de interacción específicas es una arquitectura común de aislamiento del entorno del ejecutor. Durante este proceso, si no se realiza un aislamiento adecuado de aspectos como la red, los archivos, los procesos y el tiempo de vida del Pod, se generan riesgos imprevistos.

**Casos de ataque**

Caso
Descripción




Caso 1
El entorno de ejecución del modelo de Hugging Face, debido a la falta de restricciones adecuadas de acceso a la red externa, permitió que un atacante obtuviera el control de shell del entorno de producción.

**Riesgos del ataque**

Escape de contenedor: un aislamiento de entorno deficiente puede provocar problemas de escape de contenedor, permitiendo que el atacante obtenga el control del sistema host desde el contenedor, e incluso acceda a datos de otros contenedores.
Acceso a bases de datos sensibles: el atacante, mediante prompts cuidadosamente construidos, indica al LLM que extraiga y filtre información confidencial de bases de datos sensibles.
Operaciones a nivel de sistema: si se permite al LLM ejecutar operaciones a nivel de sistema, el atacante puede manipularlo para ejecutar comandos no autorizados en el sistema subyacente.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control de acceso estricto
Implementar una política de control de acceso basada en roles (RBAC), garantizando que solo el personal autorizado pueda acceder al entorno de ejecución.


Aislamiento de red
Usar políticas de red para limitar los permisos de acceso entre contenedores, entre clústeres y desde el exterior, reduciendo la superficie de ataque y el riesgo potencial.


Implementar técnicas de sandbox
Usar técnicas de sandbox adecuadas para aislar el entorno del LLM, evitando que interactúe con sistemas y recursos críticos.

**Referencias**

https://cloud.baidu.com/article/621826
https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Inadequate_Sandboxing.html

---
### Vulnerabilidades de la cadena de suministro de componentes del entorno de despliegue

> Número de riesgo: GAARM.0005 (riesgo padre, incluye los subriesgos: vulnerabilidades de la base de datos vectorial, vulnerabilidades del sistema de contenedores y clústeres)
> Ciclo de vida: Fase de despliegue

**Descripción del ataque**

Las vulnerabilidades de la cadena de suministro del entorno de despliegue (Supply Chain Vulnerabilities in Deployment Environments) se refieren a los defectos de seguridad presentes en la cadena de suministro de software y el proceso de despliegue, desde la materia prima (como bibliotecas, dependencias, herramientas de desarrollo) hasta el producto final (como el software desplegado), que pueden provocar riesgos de vulnerabilidad que dejen al sistema expuesto a ataques o filtración de datos. Las vulnerabilidades de la cadena de suministro pueden explotarse durante el despliegue del software, reduciendo la seguridad del sistema y provocando filtración de datos o interrupción del servicio. Se dividen principalmente en tres categorías:


Vulnerabilidades del sistema de contenedores y clústeres: la tecnología de contenedores y los sistemas de gestión de clústeres pueden presentar problemas de seguridad; el atacante puede aprovechar estas vulnerabilidades para ejecutar código malicioso, robar datos, interferir en el funcionamiento del servicio, etc., provocando problemas de filtración de información privada y amenazando así la seguridad y estabilidad del gran modelo.


Vulnerabilidades de la base de datos vectorial: si la base de datos vectorial presenta una vulnerabilidad, el atacante puede aprovecharla para obtener acceso no autorizado a los datos, alterar datos, ejecutar código malicioso o iniciar otros ataques, con el fin de obtener información sensible, controlar código malicioso de forma remota, etc., causando pérdidas de datos.


Vulnerabilidades de seguridad de la plataforma en la nube: si la plataforma en la nube presenta defectos técnicos, vulnerabilidades técnicas, falta de autenticación multifactor, entre otras causas de riesgos de seguridad, el atacante puede aprovechar estos problemas de seguridad para llevar a cabo ataques maliciosos contra grandes modelos desplegados en la nube, por ejemplo, leyendo datos sensibles o robando y usando ilegítimamente credenciales de cuenta, causando a la plataforma una serie de pérdidas que incluyen, entre otras, filtración de datos, interrupción del servicio y ejecución de código malicioso.

**Casos de ataque**

Ver los subriesgos correspondientes para más detalle.

**Riesgos del ataque**

Filtración de datos: el atacante puede obtener datos sensibles; si información sensible es accedida o hecha pública por terceros no autorizados, se generarán graves problemas de privacidad y cumplimiento.
Acceso no autorizado a la aplicación del modelo: las vulnerabilidades de seguridad de la plataforma en la nube pueden provocar riesgos de acceso no autorizado en las aplicaciones de modelo desplegadas por el usuario.
Violación de la privacidad del usuario: información sensible almacenada, como la identidad personal; una vez obtenida por el atacante, violará gravemente la privacidad del usuario.

**Medidas de mitigación**

Medida de mitigación
Descripción




Principio de mínimo privilegio
Garantizar que los componentes solo tengan el mínimo privilegio necesario para completar su tarea.


Actualización periódica y gestión de parches
Actualizar oportunamente los componentes, aplicando parches de seguridad para reducir el riesgo de explotación de vulnerabilidades.

---

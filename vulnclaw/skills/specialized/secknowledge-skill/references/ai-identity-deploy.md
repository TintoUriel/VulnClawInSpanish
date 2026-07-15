# Seguridad de identidad de IA - Fase de despliegue

> Fuente: Comunidad de Inteligencia en Seguridad de Grandes Modelos AISS-NSFOCUS | Extraído de ai-identity-security.md
> Fase: Fase de despliegue (Acceso no autorizado/Abuso de credenciales)

## Fase de despliegue

### Explotación de claves de API de servicios públicos

> Código de riesgo: GAARM.0049.001
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Este riesgo se refiere a la exposición, mediante código, configuraciones u otros medios, del token de acceso a la API de un servicio (la credencial de autenticación). El atacante puede obtener ilegalmente acceso al entorno de despliegue del modelo, provocando filtración de datos, manipulación del modelo y otros riesgos de seguridad.

**Casos de ataque**

Caso
Descripción




Caso 1
La startup de ciberseguridad de IA Lasso descubrió más de 1600 tokens de API de Hugging Face filtrados en repositorios de código, afectando a cientos de cuentas de organizaciones.

**Riesgos del ataque**

Filtración de cuentas: los tokens de API filtrados pueden provocar el acceso no autorizado a cuentas de organizaciones empresariales.
Manipulación de datos: el atacante que controla la cuenta puede manipular modelos de IA existentes, implantando código malicioso en ellos, afectando a los usuarios que dependen de estos modelos base en etapas posteriores.

**Medidas de mitigación**

Medida de mitigación
Descripción




Refuerzo de la autenticación de identidad
Implementar medidas de autenticación de identidad reforzadas, como la autenticación multifactor, para reducir el riesgo de robo de tokens de API


Revocación de tokens de API filtrados
Revocar y reemplazar inmediatamente todos los tokens de API que puedan haberse filtrado


Gestión de claves y mecanismo de rotación
Establecer un mecanismo seguro de gestión y rotación de claves, actualizando periódicamente los tokens de API.


**Referencias**

- https://www.securityweek.com/major-organizations-using-hugging-face-ai-tools-put-at-risk-by-leaked-api-tokens/
- https://aws.amazon.com/cn/what-is/api-key/

---
### Acceso no autorizado a la base de datos vectorial

> Código de riesgo: GAARM.0050
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Durante el desarrollo de aplicaciones RAG, los diversos documentos locales se dividen en fragmentos de menor longitud mediante clases de tipo Text, y el contenido de texto se vectoriza utilizando un modelo de embedding, almacenándose finalmente en una base de datos vectorial. El atacante, mediante acceso no autorizado a la base de datos, puede manipular y dañar el modelo, afectando aún más a que el sistema RAG realice recuperaciones inexactas o maliciosas, lo que puede provocar que el contenido de salida del sistema RAG también se vea afectado, además del riesgo de inyección indirecta de prompts.

  

Arquitectura de la aplicación RAG

**Casos de ataque**

Caso
Descripción




Caso 1
anything-llm presenta la vulnerabilidad CVE-2024-0551, mediante la cual un atacante no autorizado puede descargar archivos de la base de datos.


Caso 2
Este estudio presenta un nuevo tipo de ataque contra LLM potenciados con RAG, que consiste en inyectar un único documento malicioso en su base de datos de conocimiento para comprometer el sistema RAG de la víctima, desencadenando diversos ataques maliciosos contra el modelo generativo.

**Riesgos del ataque**

Corrupción de la base de datos vectorial: los cambios no autorizados pueden dañar la fuente de conocimiento, provocando que el sistema RAG realice recuperaciones inexactas o maliciosas.
Filtración de información: filtración de información sensible almacenada en la base de datos vectorial.
Riesgo de inyección indirecta de prompts: los ataques contra la disponibilidad de la base de datos vectorial pueden afectar a los sistemas RAG que dependen de ella.

**Medidas de mitigación**

Medida de mitigación
Descripción




Cifrado de datos
Cifrar la base de datos vectorial que almacena todos los índices y datos de embedding, protegiendo los datos frente a posibles filtraciones o accesos no autorizados


Autenticación de identidad y control de acceso
Usar un mecanismo robusto de autenticación y autorización de usuarios, garantizando que solo el personal autorizado pueda acceder a la base de datos


Respaldo y almacenamiento redundante
Los respaldos periódicos garantizan que la fuente de conocimiento pueda recuperarse en caso de corrupción o pérdida de datos


Actualizaciones y auditorías de seguridad
Actualizar y auditar periódicamente el sistema de base de datos vectorial correspondiente, para corregir vulnerabilidades y reforzar la seguridad

**Referencias**

https://medium.com/@nitishjoshi060291/llm-hallucinations-fix-it-with-vector-database-de04eee531da
https://cloudsecurityalliance.org/blog/2023/11/22/mitigating-security-risks-in-retrieval-augmented-generation-rag-llm-applications
https://www.cnblogs.com/LittleHann/p/17440063.html#_label3
https://dongnian.icu/llms/llms_article/9.%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BALLM/index.html
https://cloudsecurityalliance.org/blog/2023/11/22/mitigating-security-risks-in-retrieval-augmented-generation-rag-llm-applications

---
### Acceso no autorizado al entorno de despliegue del modelo

> Código de riesgo: GAARM.0051
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Este riesgo se refiere a que el atacante aprovecha errores de configuración, vulnerabilidades conocidas o la falta de mecanismos adecuados de autenticación y autorización en los servicios de la plataforma de despliegue de ML, para lograr un acceso no autorizado al entorno de despliegue de ML, y con ello robar datos sensibles, abusar de recursos de cómputo, dañar la integridad del modelo de IA o llevar a cabo otras actividades maliciosas.

**Casos de ataque**

Caso
Descripción




Caso 1
El atacante aprovechó el riesgo de acceso no autorizado a la API del framework Ray para lograr la ejecución remota de código, obteniendo el control de los recursos de cómputo de la empresa objetivo.

**Riesgos del ataque**

Filtración de información sensible: el atacante puede acceder y robar datos de entrenamiento, parámetros del modelo, datos de usuario y otra información sensible.
Operación maliciosa: el acceso no autorizado puede provocar la manipulación maliciosa del modelo, generando resultados de salida engañosos.
Abuso de recursos: el atacante puede usar sin autorización los recursos de cómputo del entorno de despliegue de ML para minería de criptomonedas u otras tareas de cómputo intensivo.
Daño a la integridad del modelo: el atacante puede modificar o contaminar el proceso de entrenamiento del modelo de IA, provocando una disminución de su precisión o resultados engañosos.
Interrupción del servicio: las acciones del atacante pueden provocar la interrupción del servicio de ML, afectando la continuidad del negocio.

**Medidas de mitigación**

Medida de mitigación
Descripción




Reforzar la autenticación de identidad y el control de acceso
Implementar mecanismos de control de acceso y autenticación de identidad, para evitar el acceso no autorizado al entorno de la plataforma de despliegue del LLM y sus datos, evitando usar las políticas de autenticación predeterminadas de los servicios de la plataforma de ML


Actualizaciones y parches periódicos
Actualizar oportunamente la plataforma de ML y las bibliotecas dependientes, para corregir vulnerabilidades conocidas


Protección del modelo y despliegue seguro
Realizar un escaneo de seguridad y pruebas de penetración al modelo antes del despliegue, adoptando técnicas de cifrado y firma para proteger la confidencialidad e integridad de los parámetros del modelo y los datos de entrenamiento

**Referencias**

https://www.leewayhertz.com/security-in-ai-development/

---
### Abuso de credenciales del entorno de despliegue

> Código de riesgo: GAARM.0049
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

En el ciclo de vida de MLOps de un gran modelo, las credenciales de acceso (como claves o tokens de acceso) están involucradas en múltiples fases: confirmación de código, construcción, pruebas y despliegue. El riesgo de abuso de credenciales del entorno de despliegue se refiere a los fallos de seguridad en el uso de las claves de API o tokens de acceso utilizados para acceder y desplegar servicios del modelo en el flujo de CI/CD (integración continua/despliegue continuo) de un gran modelo. El atacante puede aprovechar este riesgo para robar credenciales, inyectar código malicioso u otras técnicas, provocando la filtración de información sensible, la inyección de código malicioso u otras amenazas de seguridad.

**Casos de ataque**

Caso
Descripción




Caso 1
Las credenciales están codificadas directamente en el código o en archivos de configuración; el atacante, tras obtener permisos en la máquina de desarrollo, aprovecha las credenciales para realizar movimiento lateral.

**Riesgos del ataque**

Filtración de credenciales: el atacante obtiene las credenciales del desarrollador mediante ingeniería social u otros medios, y luego usa estas credenciales para acceder a datos sensibles en el sistema de CI/CD o ejecutar operaciones maliciosas.
Inyección de código malicioso: el atacante, aprovechando las credenciales obtenidas, envía commits que contienen código malicioso al repositorio de código, el cual se ejecuta durante los procesos posteriores de construcción y despliegue.

**Medidas de mitigación**

Medida de mitigación
Descripción




Reforzar la autenticación de identidad y la política de contraseñas
Recomendar a los usuarios seguir una política de contraseñas adecuada e implementar la autenticación de doble factor (2FA)


Auditoría de código y escaneo automatizado
Realizar un escaneo de seguridad automatizado antes de confirmar y desplegar código, detectando el riesgo de credenciales codificadas, para descubrir posibles problemas de seguridad


Monitorización y alertas
Desplegar un sistema de monitorización para detectar patrones de acceso u operaciones inusuales, y emitir alertas oportunamente

**Referencias**

https://atmosphericthinking.medium.com/massive-leak-of-chatgpt-credentials-over-100-000-affected-db6cef3a18c5
https://blog.csdn.net/FreeBuf_/article/details/140870185?utm_relevant_index=7

---

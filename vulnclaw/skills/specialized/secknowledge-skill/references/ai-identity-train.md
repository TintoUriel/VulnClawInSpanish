# Seguridad de identidad de IA - Fase de entrenamiento

> Fuente: Comunidad de Inteligencia en Seguridad de Grandes Modelos AISS-NSFOCUS | Extraído de ai-identity-security.md
> Fase: Fase de entrenamiento (Defectos de diseño de permisos/Autenticación del entorno)

## Fase de entrenamiento

### Plugins de LLM: defectos de diseño en el control de permisos

> Código de riesgo: GAARM.0048
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este riesgo se refiere a defectos de diseño en el control de permisos presentes en los plugins de LLM. Un plugin de LLM es un agente que ofrece funcionalidad de interacción y que, al estar habilitado, es invocado automáticamente por el modelo durante la interacción con el usuario. Esta invocación automática conlleva un riesgo de falta de control: por ejemplo, un plugin puede aprovechar los permisos de otro plugin para acceder y obtener datos o funciones sensibles a los que no tiene acceso directo, lo que brinda al atacante la posibilidad de construir solicitudes maliciosas para atacar. En resumen, este control de acceso defectuoso permite que un usuario invoque directamente plugins con funciones sensibles, o que exista un control de permisos erróneo entre plugins; cuando el usuario final proporciona una entrada maliciosa, se generan riesgos de seguridad, incluyendo filtración de datos, ejecución remota de código y escalada de privilegios.

**Casos de ataque**

Caso
Descripción




Caso 1
LangChain ofrece numerosas herramientas para construir plugins de LLM; cuando el diseño de estos plugins no prioriza la seguridad, el atacante puede usar inyección de prompts para alterar el comportamiento de plugins mal diseñados.

**Riesgos del ataque**

Filtración de información sensible: un plugin con un control de permisos mal diseñado puede, tras ser invocado por el atacante, solicitar los permisos de otro plugin, accediendo y obteniendo datos o funciones de otros plugins; esta cadena de invocaciones en cascada puede provocar la filtración de gran cantidad de información sensible.
Ejecución remota de código: mediante la inyección de código o datos maliciosos, el atacante puede intentar establecer un punto de apoyo en el sistema, para controlarlo o dañarlo aún más.

**Medidas de mitigación**

Medida de mitigación
Descripción




Aplicación estricta de entradas parametrizadas
Verificar el tipo y el rango de las entradas. Si esto no es posible, se debe introducir una segunda capa de invocación tipada que analice la solicitud y aplique validación y depuración


Control de acceso de mínimo privilegio
Exponer la menor cantidad de funcionalidad posible, manteniendo al mismo tiempo la función requerida

**Referencias**

https://genai.owasp.org/wp-content/uploads/2024/05/OWASP-Top-10-for-LLM-Applications-v1_1_Chinese.pdf
https://developer.nvidia.com/zh-cn/blog/securing-llm-systems-against-prompt-injection/

---
### Ausencia de autenticación y autorización en el entorno de entrenamiento

> Código de riesgo: GAARM.0046
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este riesgo se refiere a la falta de mecanismos estrictos de control de acceso y autenticación de identidad del modelo durante la fase de entrenamiento, lo que permite que personal sin los permisos suficientes acceda a recursos internos del modelo como los datos de entrenamiento, la infraestructura de entrenamiento o el framework de entrenamiento, provocando la filtración de datos sensibles del modelo, la transparencia no deseada de los datos de entrenamiento del modelo y un aumento del riesgo de envenenamiento del modelo.

**Casos de ataque**

Caso
Descripción




Caso 1
En el incidente ShadowRay, el atacante aprovechó la vulnerabilidad CVE-2023-48022 del framework Ray para programar la API de Jobs sin autorización y lograr un ataque de ejecución remota de código (RCE).

**Riesgos del ataque**

Filtración de información sensible: el acceso no autorizado a los datos de entrenamiento provoca la filtración de información sensible.
Deterioro de la calidad del modelo: la manipulación maliciosa de los datos de entrenamiento puede afectar el efecto de aprendizaje del modelo, provocando que su salida sea inexacta o sesgada.
Abuso de recursos de alto valor: el atacante aprovecha el acceso no autorizado a la API para obtener el control de recursos de cómputo de alto valor y llevar a cabo actividades como la minería de criptomonedas.

**Medidas de mitigación**

Medida de mitigación
Descripción




Reforzar la política de autenticación de identidad y control de acceso
Implementar mecanismos de control de acceso y autenticación de identidad, para evitar el acceso no autorizado al entorno de entrenamiento de LLM y sus datos


Cifrado y desensibilización de datos
Introducir medidas de cifrado y protección de la privacidad de los datos de entrenamiento, para evitar la filtración de información sensible

**Referencias**

https://blog.csdn.net/qq_43543209/article/details/135683986

---
### Asignación excesiva de permisos en el entorno de entrenamiento

> Código de riesgo: GAARM.0047
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

El riesgo de asignación excesiva de permisos durante la fase de entrenamiento de un gran modelo se refiere principalmente a problemas de seguridad derivados de una asignación de permisos excesivamente amplia durante el acceso a datos, el entrenamiento del modelo y la administración del sistema, lo que puede provocar acceso no autorizado o riesgos de abuso. Si un atacante obtiene ilegalmente los permisos de control de un desarrollador, puede aprovechar estos permisos excesivos para acceder ilegalmente, manipular o dañar los datos de entrenamiento del modelo, afectando así su calidad y seguridad.

**Casos de ataque**

Caso
Descripción




Caso 1
El atacante obtuvo, mediante phishing u otros métodos, los permisos de control de un desarrollador de entrenamiento, y aprovechó las credenciales de la cuenta con altos privilegios para acceder a datos de entrenamiento sensibles o manipular maliciosamente el modelo.

**Riesgos del ataque**

Filtración de datos sensibles: si en el entorno de entrenamiento de un desarrollador existen permisos de control excesivos e innecesarios, cuando las credenciales de la cuenta del desarrollador se filtran, el atacante puede aprovechar estos permisos redundantes para acceder a más información interna, lo que puede provocar la filtración de los datos de entrenamiento, especialmente cuando estos contienen información sensible.
Deterioro de la calidad del modelo: la manipulación maliciosa de los datos de entrenamiento por parte del atacante puede afectar el efecto de aprendizaje del modelo, provocando que su salida sea inexacta o sesgada.

**Medidas de mitigación**

Medida de mitigación
Descripción




Principio de mínimo privilegio
Garantizar que cada usuario o componente del sistema posea únicamente el mínimo de permisos necesarios para completar su tarea


Cifrado y desensibilización de datos
Introducir medidas de cifrado y protección de la privacidad de los datos de entrenamiento, para evitar la filtración de información sensible


Control de acceso y auditoría
Implementar políticas estrictas de control de acceso y realizar auditorías de seguridad periódicas para supervisar y registrar todo acceso a datos y modelos

**Referencias**

https://www.pulumi.com/ai/answers/mptvxaHguJ6A4yXSHi92zZ/implementing-role-based-access-to-ai-training-data-in-snowflake

---

# Seguridad de la base de IA - Fase de entrenamiento

> Fuente: Comunidad AISS NSFOCUS de seguridad de grandes modelos de IA | Extraído de ai-baseline-security.md
> Fase: Fase de entrenamiento (vulnerabilidades de herramientas de desarrollo/aislamiento de entornos)

## Fase de entrenamiento

### Vulnerabilidades en las herramientas de desarrollo de modelos

> Código de riesgo: GAARM.0001.001
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

El desarrollo y entrenamiento de modelos involucra múltiples etapas, como el preprocesamiento de datos, la ingeniería de características, la selección del modelo, el entrenamiento, la evaluación y el despliegue. Si las herramientas utilizadas en este proceso presentan vulnerabilidades de seguridad, todo el flujo de aprendizaje automático queda expuesto a riesgo. Los atacantes pueden aprovechar estas vulnerabilidades para manipular los datos de entrenamiento del modelo, robar sus parámetros o ejecutar ataques específicos tras el despliegue del modelo, provocando consecuencias graves de seguridad como salidas inexactas del modelo, robo de parámetros o propagación de software malicioso.

**Casos de ataque**

Caso
Descripción




Caso 1
TensorFlow presenta una vulnerabilidad de ejecución de código; existe riesgo de ejecución de código al cargar el modelo


Caso 2
PyTorch presenta una vulnerabilidad de ejecución de código que permite ejecutar código remoto en el sistema objetivo dentro del contexto del usuario que ejecuta el programa, con riesgo de ejecución de código malicioso


Caso 3
Este documento cubre distintos casos de uso de TensorFlow y describe las vulnerabilidades de seguridad presentes en TensorFlow, donde los distintos casos de uso conllevan diferentes consecuencias de riesgo

**Riesgos del ataque**

Ataque a la cadena de suministro: el atacante puede insertar código malicioso en paquetes de software legítimos utilizados para el desarrollo de ML, ejecutando un ataque a la cadena de dependencias que propaga software malicioso durante la distribución.
Envenenamiento del modelo: el atacante inyecta datos maliciosos en los datos de entrenamiento, afectando el proceso de decisión del modelo y provocando que sus salidas sean inexactas o sesgadas.
Pérdida de propiedad intelectual: si se roban los parámetros del modelo, el atacante puede copiarlo o utilizarlo ilegalmente.

**Medidas de mitigación**

Medida de mitigación
Descripción




Actualizaciones y parches periódicos
Mantener actualizadas todas las herramientas y bibliotecas de desarrollo para aprovechar las últimas correcciones de seguridad


Cadena de dependencias segura
Revisar la cadena de dependencias para garantizar que todas las bibliotecas y paquetes de terceros provengan de fuentes confiables

**Referencias**

https://www.secrss.com/articles/64006
https://huntr.com/bounties/a795bf93-c91e-4c79-aae8-f7d8bda92e2a

---
### Vulnerabilidades del sistema de gestión de datos de entrenamiento

> Código de riesgo: GAARM.0001.002
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

El sistema de gestión de datos de entrenamiento es responsable de almacenar, procesar, etiquetar y proporcionar datos, entregando los datos preparados al modelo para su aprendizaje. Cuando este sistema presenta vulnerabilidades de seguridad relacionadas con la cadena de suministro, los atacantes pueden aprovecharlas para manipular datos, robarlos o incluso influir en los resultados del entrenamiento del modelo mediante el envenenamiento de datos.

**Riesgos del ataque**

Ataque de envenenamiento de datos: el atacante puede inyectar datos maliciosos en los datos de entrenamiento, afectando el proceso de decisión del modelo y provocando predicciones inexactas o sesgadas.
Ataque de robo de modelo: el atacante intenta, mediante consultas al modelo, realizar ingeniería inversa y obtener sus parámetros o datos de entrenamiento, robando así la propiedad intelectual.
Filtración de datos: el atacante obtiene datos de entrenamiento sensibles mediante acceso no autorizado.

**Medidas de mitigación**

Medida de mitigación
Descripción




Actualizaciones y auditorías de seguridad
Actualizar y auditar periódicamente el sistema de gestión de datos de entrenamiento para corregir vulnerabilidades y reforzar la seguridad


Monitorización y registro
Implementar monitorización en tiempo real y registro de logs para detectar y responder oportunamente a actividades sospechosas

**Referencias**

https://doc.dataiku.com/dss/latest/concepts/homepage/index.html
https://www.secrss.com/articles/62742

---
### Riesgos de seguridad del entorno de entrenamiento

> Código de riesgo: GAARM.0001
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este riesgo se refiere a que, si los frameworks de aprendizaje profundo (como TensorFlow o PyTorch) y las bibliotecas de dependencias necesarias, utilizados como componentes de desarrollo de aplicaciones en el entorno de entrenamiento y desarrollo del modelo, presentan por sí mismos vulnerabilidades de seguridad, esto puede provocar un ataque a la cadena de suministro contra las aplicaciones de LLM situadas aguas abajo, afectando la integridad de los datos de entrenamiento, el modelo de ML y la plataforma de despliegue.

**Casos de ataque**

Caso
Descripción




Caso 1
El código de ejemplo del plugin integrado proporcionado por OpenAI contenía una imagen Docker de MinIO vulnerable, cuya vulnerabilidad podía provocar la filtración de claves y contraseñas; la biblioteca Redis-py utilizada por ChatGPT presentaba una vulnerabilidad que exponía el historial de conversaciones y la información de pago de los usuarios


Caso 2
El framework de aprendizaje automático de código abierto PyTorch presenta una vulnerabilidad crítica CVE-2024-5480, que un atacante puede utilizar para atacar remotamente el nodo maestro de entrenamiento distribuido; una vez comprometidos estos nodos, el atacante tiene la oportunidad de robar datos sensibles relacionados con la IA


Caso 3
El formato pickle utilizado por los modelos de PyTorch puede ser convertido en arma por actores maliciosos para ejecutar código arbitrario y desplegar cargas útiles de ataque de Cobalt Strike, Mythic y Metasploit; el atacante puede comprometer los servicios de conversión alojados y el sistema de alojamiento de archivos mediante el uso de binarios maliciosos de PyTorch

**Riesgos del ataque**

Filtración de la privacidad del usuario: como se muestra en el caso 1, debido a un error en la biblioteca Redis-py, otros usuarios pudieron ver los títulos del historial de conversaciones y el contenido de los diálogos de los usuarios de ChatGPT, provocando la filtración de datos privados de los usuarios.
Daño a la integridad del sistema: el atacante puede aprovechar vulnerabilidades para dañar la integridad del sistema, afectando la fiabilidad y disponibilidad de los servicios de LLM.

**Medidas de mitigación**

Medida de mitigación
Descripción




Actualizaciones y auditorías de seguridad
Actualizar y auditar periódicamente el software de servicio en los entornos de entrenamiento y desarrollo para corregir vulnerabilidades y reforzar la seguridad


Auditoría de seguridad y monitorización
Realizar auditorías de seguridad periódicas, utilizar herramientas de monitorización para detectar y alertar sobre comportamientos sospechosos, y llevar a cabo un registro de logs eficaz

**Referencias**

https://llmtop10.com/llm05/

---
### Deficiencias en el aislamiento del entorno de entrenamiento

> Código de riesgo: GAARM.0002
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

El aislamiento del entorno de entrenamiento consiste en dividir el entorno de depuración y el entorno de ejecución en dos zonas completamente aisladas, con el fin de evitar que el entorno de depuración se utilice como vector de penetración hacia el entorno de ejecución. En el entorno de depuración se puede modificar la lógica del programa, pero solo se pueden utilizar datos desensibilizados; mientras que en el entorno de ejecución se pueden operar los datos reales completos, con las operaciones sujetas a auditoría, de modo que los resultados sean rastreables y las responsabilidades exigibles. Si el aislamiento del entorno de entrenamiento presenta deficiencias que permiten pasar del entorno de desarrollo al entorno de ejecución/pruebas, esto provocará que usuarios no autorizados accedan a datos sensibles, brindando una oportunidad al atacante.

**Casos de ataque**

Caso
Descripción




Caso 1
Deficiencias en el aislamiento del entorno de entrenamiento permitieron que un atacante pasara del entorno del desarrollador al entorno de ejecución/pruebas, provocando riesgos como la filtración de datos de entrenamiento

**Riesgos del ataque**

Filtración de datos: el atacante puede acceder y robar datos sensibles almacenados en el entorno de ejecución; la filtración de estos datos puede provocar pérdidas económicas significativas y responsabilidad legal.
Obtención del control del sistema: si el atacante penetra en el entorno de ejecución, puede obtener el control del sistema, y con ello manipular el acceso a los datos, la gestión de recursos y la configuración del sistema.

**Medidas de mitigación**

Medida de mitigación
Descripción




Reforzar las medidas de aislamiento
Utilizar técnicas de seguridad y mejores prácticas para reforzar el aislamiento entre el entorno de depuración y el entorno de ejecución


Control de acceso
Implementar políticas de control de acceso basado en roles (RBAC), garantizando que solo el personal autorizado pueda acceder al entorno de ejecución


Tecnología de sandbox de seguridad
Aislar y proteger el entorno de ejecución del LLM, para evitar que sufra ataques e interferencias externas


**Referencias**

- https://cloud.baidu.com/article/621826

---


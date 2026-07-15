# Seguridad de datos de IA - Fase de despliegue

> Fuente: Comunidad de Inteligencia en Seguridad de Grandes Modelos AISS-NSFOCUS | Extraído de ai-data-security.md
> Fase: Fase de despliegue (GAARM.0012-0016 Respaldo/Transmisión/Almacenamiento/Registros/Caché)

## Fase de despliegue

### Robo de datos de respaldo

> Código de riesgo: GAARM.0012
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Los datos de respaldo suelen contener información importante como los datos de entrenamiento del modelo, la lógica del algoritmo, datos sensibles y datos personales. Si la protección es inadecuada, un atacante puede obtener los datos de respaldo mediante acceso no autorizado u otros métodos de ataque, lo que provoca la filtración de información importante relacionada con el modelo e incluso conlleva riesgos económicos.

**Casos de ataque**

Caso
Descripción




Caso 1
Un atacante obtuvo credenciales de acceso de un empleado de una empresa tecnológica mediante un correo de phishing y, tras acceder sin autorización al servicio de almacenamiento en la nube, robó datos de respaldo de un modelo de gran tamaño que contenían información personal sensible y secretos comerciales, lo que expuso a la empresa a riesgos legales y económicos.

**Riesgos del ataque**

Manipulación del modelo: si los datos de respaldo contienen información como los datos de entrenamiento o el algoritmo del modelo, el atacante puede usar esta información para manipular el modelo.
Filtración de datos sensibles: si los datos de respaldo contienen información de usuarios o clientes, su filtración puede provocar robo de identidad, actividades fraudulentas, extorsión, etc.

**Medidas de mitigación**

Medida de mitigación
Descripción




Cifrado de datos
Utilizar algoritmos de cifrado robustos durante el almacenamiento de los datos de respaldo, garantizando que los datos estén protegidos tanto en almacenamiento como en tránsito, de modo que incluso si se filtran sea difícil descifrarlos.


Autenticación multifactor
Implementar mecanismos de autenticación multifactor, como la autenticación de dos factores, para reforzar el control de acceso a los datos de respaldo y aumentar la seguridad.

---
### Secuestro de la transmisión de datos

> Código de riesgo: GAARM.0013
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Durante el preentrenamiento, el ajuste fino y los servicios de inferencia de grandes modelos, es necesario transmitir datos entre distintas entidades o departamentos. Estos datos a menudo contienen información sensible y privada diversa, como datos de identidad personal e información financiera. Un atacante que intercepta maliciosamente los datos durante la transmisión puede obtener información privada relacionada, provocando la filtración de información sensible y generando problemas de seguridad y privacidad para los usuarios.

**Casos de ataque**

Caso
Descripción




Caso 1
Un atacante aprovechó una vulnerabilidad de transmisión de red no cifrada para interceptar con éxito datos financieros personales transmitidos por una institución financiera durante la prestación de servicios de un gran modelo, provocando la filtración de información sensible y generando riesgos de seguridad y privacidad para los usuarios.

**Riesgos del ataque**

Filtración de datos sensibles: el atacante puede obtener información sensible interceptando los datos, como información de identidad personal, datos financieros, registros médicos, etc.
Propiedad intelectual: si los datos contienen secretos comerciales o algoritmos propietarios, la interceptación de datos puede provocar la filtración de dicha propiedad intelectual.

**Medidas de mitigación**

Medida de mitigación
Descripción




Cifrado de datos
Cifrar los datos sensibles para garantizar la seguridad de los datos durante la transmisión.

**Referencias**

https://bj.bcebos.com/ensec-web-privacy/anquan/%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%AE%89%E5%85%A8%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88%E7%99%BD%E7%9A%AE%E4%B9%A6.pdf
https://mp.weixin.qq.com/s/JlJwDRzYG985kF4d6g7qjw

---
### Ataques al servicio de almacenamiento de datos

> Código de riesgo: GAARM.0014
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Este riesgo se refiere a posibles fallos de seguridad durante el almacenamiento y la organización de los datos, como controles de acceso insuficientes, prácticas de manejo de datos inseguras o ausencia de medidas de cifrado. Un atacante que aproveche estas vulnerabilidades puede llevar a cabo accesos no autorizados, filtraciones de datos o manipulaciones, obteniendo información sensible e incluso realizando robo de identidad o actividades fraudulentas, lo que expone la privacidad de los usuarios y los activos de la empresa y conlleva la posibilidad de filtraciones de datos, litigios legales y pérdida de reputación.

**Casos de ataque**

Caso
Descripción




Caso 1
El repositorio de código fuente de Clearview AI estaba mal configurado, permitiendo el acceso a cualquier usuario y exponiendo credenciales de producción y datos de entrenamiento, lo que subraya que la seguridad de los sistemas de aprendizaje automático requiere reforzar las medidas tradicionales de ciberseguridad.

**Riesgos del ataque**

Filtración de datos sensibles: los datos sensibles sin protección de cifrado o con un control de acceso inadecuado pueden ser obtenidos por atacantes, provocando filtraciones de datos.
Robo de identidad: la información de identidad personal almacenada puede ser robada y utilizada para actividades delictivas como robo de identidad o fraude.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control de acceso
Garantizar que solo los usuarios autorizados puedan acceder a los datos del repositorio de almacenamiento.


Clasificación de datos
Clasificar la información del repositorio e implementar medidas de seguridad correspondientes según la sensibilidad de los datos.


Cifrado de datos
Cifrar los datos sensibles almacenados, de modo que aunque se acceda a ellos sin autorización, su contenido no pueda leerse fácilmente.

**Referencias**

https://news.cctv.com/2022/06/21/ARTIdhgLL1sSK5Hjl0uYWybr220621.shtml
https://atlas.mitre.org/techniques/AML.T0036

---
### Robo de registros y auditorías

> Código de riesgo: GAARM.0015
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Los registros y auditorías del modelo desempeñan un papel clave en la supervisión de las actividades y eventos del sistema, registrando en detalle información como el comportamiento de inicio de sesión de los usuarios, el acceso a archivos, los cambios en la configuración del sistema y diversos eventos de seguridad. Tras obtener permisos en el servidor correspondiente, un atacante puede robar los registros y auditorías, exponiendo los patrones de comportamiento personal de los usuarios y revelando posibles vulnerabilidades del sistema, lo que permite al atacante lanzar ataques más dirigidos.

**Casos de ataque**

Caso
Descripción




Caso 1
Este caso describe cómo ChatGPT filtró credenciales de inicio de sesión de usuarios y otra información personal.

**Riesgos del ataque**

Filtración de datos sensibles: provoca la filtración de la privacidad personal, el robo de cuentas, entre otros problemas.
Ataques dirigidos: el atacante puede descubrir vulnerabilidades y puntos débiles de seguridad en el sistema, lo que le permite lanzar ataques más dirigidos.

**Medidas de mitigación**

Medida de mitigación
Descripción




Auditorías periódicas
Auditar periódicamente el acceso y las operaciones sobre los registros y auditorías, verificando si existen comportamientos anómalos o irregulares, para detectar y gestionar oportunamente las amenazas de seguridad.


Almacenamiento separado de registros y auditorías
Almacenar los registros y auditorías separados de otros datos, garantizando su independencia respecto de los datos de producción y reduciendo el riesgo de filtración.


Establecimiento de políticas de control de acceso
Establecer políticas de control de acceso estrictas, autorizando únicamente al personal necesario para acceder a los registros y auditorías, limitando el alcance de los permisos y evitando accesos no autorizados.

**Referencias**

https://www.kuaikuaicloud.com/market/3667.html

---
### Robo de datos de caché e información de índices

> Código de riesgo: GAARM.0016
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Los datos de caché y la información de índices pueden filtrar información sensible del usuario, incluyendo, entre otros, información de identificación personal, detalles de pago y preferencias personales. Un atacante que accede ilegalmente a los datos de caché e índices puede manipular o destruir los datos, afectando el funcionamiento del sistema y la integridad de los datos; también puede planear y ejecutar ataques de phishing dirigidos, utilizando la información personal del usuario para aumentar la credibilidad y la tasa de éxito del ataque, causando así amenazas de seguridad y pérdidas económicas más graves para el usuario.

**Casos de ataque**

Caso
Descripción




Caso 1
Este caso describe cómo OpenAI utilizó Redis para almacenar en caché información de usuarios en sus servidores; debido a un error en la biblioteca de código abierto del cliente redis-py, algunos clientes recibieron por error direcciones de correo electrónico de otros usuarios almacenadas en caché en Redis.

**Riesgos del ataque**

Filtración de datos sensibles: los datos de caché filtrados pueden contener información de credenciales del usuario, como nombre de usuario y contraseña, que el atacante puede usar para actividades de robo de identidad, secuestro de cuentas, etc.
Manipulación de datos: el atacante puede utilizar esta información para manipular o destruir los datos en caché, afectando el funcionamiento del sistema y la integridad de los datos.

**Medidas de mitigación**

Medida de mitigación
Descripción




Cifrado de datos
Cifrar los datos sensibles para garantizar la seguridad de los datos.

**Referencias**

http://www.nelab-bdst.org.cn/data/upload/ueditor/20230707/64a78209c719c.pdf

---

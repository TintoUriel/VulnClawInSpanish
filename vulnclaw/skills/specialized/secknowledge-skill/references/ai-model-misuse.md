# Seguridad de Modelos de IA - Fase de Aplicación - Abuso de Funcionalidades del Modelo y Falsificación de Información

> Fuente: Comunidad AISS NSFOCUS de Seguridad de Grandes Modelos | Extraído de ai-model-app.md
> Categoría de riesgo: Abuso/Falsificación (GAARM.0031.x Falsificación Multimodal + 0033 Deriva de Datos + 0062 Cumplimiento Multimodal + 0063 Sabotaje de Intención)

---

### Falsificación de Información en Imágenes

> Número de riesgo: GAARM.0031.003
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Los atacantes pueden generar imágenes falsas realistas mediante técnicas como las redes generativas antagónicas (GAN). Estas imágenes falsas pueden utilizarse con fines de publicidad fraudulenta, falsificación de pruebas, fraude en línea, entre otros. Además, la falsificación de información en imágenes también puede provocar la filtración de información de identidad personal. Los atacantes, al analizar fotografías personales, información de redes sociales y otros datos públicos, pueden utilizar la IA para generar imágenes de rostros realistas y usarlas para suplantar la identidad de otras personas. Esto conlleva graves riesgos para la privacidad personal y la seguridad de los datos.

**Casos de ataque**

Caso
Descripción

Caso 1
Un empleado del área financiera recibió un correo electrónico de un supuesto CFO y fue invitado a una videoconferencia en la que todos los participantes eran imágenes falsas de deepfake generadas a partir de fragmentos de video y audio públicos, lo que provocó pérdidas de 200 millones de dólares de Hong Kong (aproximadamente 180 millones de yuanes) para la empresa.

Caso 2
Imágenes de información falsa generadas por IA que aumentan la credibilidad de información que no corresponde con los hechos, provocando graves consecuencias en la opinión pública.

**Riesgos del ataque**

Información engañosa: las imágenes falsificadas pueden utilizarse para difundir información falsa, influyendo en la opinión pública.
Daño a la reputación: empresas o individuos pueden verse perjudicados por imágenes falsificadas, afectando su reputación e incluso provocando pérdidas patrimoniales.
Consecuencias legales: publicar imágenes falsificadas puede acarrear responsabilidad legal, especialmente en casos relacionados con difamación o violación de la privacidad.

**Medidas de mitigación**

Medida de mitigación
Descripción

Revisión de contenido
Uso de herramientas de reconocimiento de imágenes y revisión de contenido para detectar imágenes falsificadas o manipuladas.

Tecnología de marca de agua
Identificar claramente las imágenes generadas, informando a los usuarios de que su origen no es real.

Verificación de origen
Uso de herramientas forenses de imágenes para examinar los metadatos y el historial de edición de las imágenes.

Formulación de políticas
Establecer políticas y marcos legales claros para el uso y la difusión de imágenes falsificadas.

**Referencias**

https://stcn.com/article/detail/1250289.html
https://www.51cto.com/aigc/912.html

---
### Riesgo de Seguridad de Cumplimiento de Contenido Multimodal

> Número de riesgo: GAARM.0062
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El riesgo de seguridad de cumplimiento de contenido multimodal se refiere a la amenaza de seguridad de que el contenido generado por modelos multimodales pueda infringir leyes y regulaciones, normas éticas o políticas de la plataforma. Este riesgo abarca contenido no conforme en múltiples formas, como texto, imagen, audio y video; los mecanismos tradicionales de detección de cumplimiento de una sola modalidad tienen dificultades para hacer frente a escenarios complejos de incumplimiento entre modalidades. El contenido multimodal puede eludir la detección habitual mediante insinuaciones metafóricas, sugerencias intermodales y asociaciones semánticas profundas, generando salidas que contienen información falsa, discurso de odio, contenido violento, contenido para adultos u otro contenido no conforme, lo que constituye una grave amenaza para el orden social y la seguridad de los usuarios.

**Casos de ataque**

Caso
Descripción

Caso 1
Grok, el chatbot de IA de xAI, la empresa de Elon Musk (integrado en la plataforma social X), fue objeto de abuso por parte de usuarios tras el lanzamiento de su función de generación de imágenes, quienes crearon imágenes de contenido sexual insinuante y desnudos no autorizados (incluyendo de menores), lo que desencadenó investigaciones regulatorias a nivel mundial y una revisión integral de la plataforma.

Caso 2
En la noche del 22 de diciembre de 2025, numerosos usuarios reportaron que las salas de transmisión en vivo de Kuaishou mostraban gran cantidad de contenido pornográfico, incluida la difusión de videos obscenos, actuaciones vulgares y otras transmisiones inapropiadas; en algunas salas el número de espectadores llegó a decenas de miles. Tras la difusión de la noticia, algunos internautas presentaron denuncias, y la policía informó haber recibido múltiples reportes ciudadanos. La plataforma respondió que este fenómeno se debió a un ataque de la industria gris/negra, que ya fue atendido de manera urgente y reportado a las autoridades de seguridad pública.

Manifestaciones del riesgo

Generación de contenido no conforme entre modalidades: generación de contenido multimodal que infringe leyes y regulaciones
Difusión encubierta de información no conforme: difusión de información no conforme mediante insinuaciones intermodales
Contenido no conforme mediante deepfake: generación de contenido multimodal falso y dañino
Elusión de la detección de cumplimiento de contenido: aprovechamiento de las características intermodales para eludir los mecanismos de detección existentes
Contenido multimodal inductivo: generación de contenido multimodal engañoso o dañino

**Medidas de mitigación**

Medida de mitigación
Descripción

Detección de cumplimiento entre modalidades
Establecer un sistema de detección de cumplimiento de contenido multimodal, implementar análisis de asociación semántica entre modalidades, y detectar contenido no conforme encubierto e información insinuada.

Análisis de contenido multidimensional
Analizar simultáneamente texto, imagen, audio y otras modalidades; establecer un mecanismo de verificación de consistencia entre modalidades e implementar una evaluación de cumplimiento en múltiples niveles.

Monitoreo de contenido en tiempo real
Establecer un sistema de monitoreo de contenido multimodal en tiempo real, implementar detección dinámica de cumplimiento y crear un mecanismo de respuesta rápida ante contenido no conforme.

Construcción de base de conocimiento de cumplimiento
Construir una base de características de contenido multimodal no conforme, actualizar las reglas de cumplimiento y los modelos de detección, e implementar estándares de cumplimiento multilingües y multiculturales.

**Referencias**

Grok de Musk cae en el "streaming pornográfico de IA", cruzando líneas rojas regulatorias en múltiples países
Incidente de ataque de la industria gris/negra en las salas de transmisión en vivo de Kuaishou

---
### Generación de Código Malicioso

> Número de riesgo: GAARM.0031.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El modelo presenta el riesgo de generación de código malicioso, lo que significa que los atacantes pueden aprovechar las capacidades del modelo para generar o construir código destructivo, como virus, troyanos, ransomware, etc. Esto también puede provocar la intrusión de sistemas, la filtración de datos o la interrupción de servicios, constituyendo una grave amenaza para la seguridad y la privacidad. Además, la generación de código malicioso también puede utilizarse para eludir los sistemas de detección de seguridad, dejando ineficaces las medidas tradicionales de protección de seguridad.

**Casos de ataque**

Caso
Descripción

Caso 1
Los atacantes utilizaron técnicas de jailbreak para hacer que ChatGPT escribiera malware como secuestro de DLL (dll hijacking) y herramientas de fuerza bruta.

Caso 2
Los atacantes utilizaron ataques de jailbreak para hacer que ChatGPT escribiera software de fuerza bruta para SSH.

Caso 3
Se construyó un agente de hacking basado en GPT-4, capaz de aprender a explotar vulnerabilidades tras leer descripciones de vulnerabilidades CVE.

Caso 4
Se eludieron las restricciones de seguridad mediante llamadas a la API, escribiendo código para programas de inyección.

Caso 5
En los correos de phishing de un hacker alemán, el contenido del script sugiere que TA547 pudo haber utilizado IA generativa para escribir o reescribir scripts de PowerShell.

##

**Riesgos del ataque**

- Generación de malware: los atacantes pueden aprovechar el código malicioso generado por IA para crear malware personalizado, diseñado específicamente para eludir las medidas de protección de seguridad existentes.
- Aumento de la eficiencia de los ciberataques: la IA reduce la barrera de entrada para escribir código malicioso, permitiendo a los atacantes crear herramientas de ataque de alta calidad con mayor rapidez, aumentando la escala y eficiencia de los ciberataques.
- Elusión de la detección de seguridad: el código malicioso generado por IA puede presentar mayor variabilidad y sigilo, dificultando su identificación efectiva por parte de los sistemas de detección de seguridad tradicionales.

**Medidas de mitigación**

- Reforzar el filtrado de seguridad en la generación de código: añadir detección de características de código malicioso en la capa de salida del modelo
- Restringir llamadas a API peligrosas: establecer permisos estrictos para las llamadas a API relacionadas con la ejecución de código
- Ejecución en sandbox de seguridad: revisar en entorno aislado todo el código generado por IA antes de su ejecución
- Monitoreo de comportamiento: monitorear el comportamiento de ejecución del código generado por IA, bloqueando de inmediato cualquier anomalía detectada

**Referencias**

https://infosecwriteups.com/jail-breaking-chatgpt-to-write-malware-9b3ae111f30c
https://www.theregister.com/2024/04/17/gpt4_can_exploit_real_vulnerabilities/
https://arxiv.org/abs/2404.08144
https://blog.csdn.net/pengpengjy/article/details/132478358

---
### Sabotaje de Intención y Manipulación de Objetivos

> Número de riesgo: GAARM.0063
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El sabotaje de intención y la manipulación de objetivos es una técnica de ataque avanzada dirigida a agentes inteligentes, en la que los atacantes, mediante entradas específicas cuidadosamente construidas, sabotean la configuración de intención original del agente y manipulan su objetivo de comportamiento para que se desvíe de la funcionalidad prevista. El núcleo de este ataque radica en aprovechar las vulnerabilidades del agente en la comprensión de la intención del usuario, el establecimiento de objetivos de ejecución y el proceso de toma de decisiones de comportamiento; mediante inducción gradual, manipulación de contexto, secuestro de objetivos y otros medios, se logra que el agente ejecute operaciones no previstas, dañinas o que sirvan a los propósitos del atacante, lo que puede provocar abuso del sistema, filtración de datos, interrupción del servicio o control total del comportamiento del agente.

**Casos de ataque**

Caso
Descripción

Caso 1
En 2025, Operant AI descubrió y reveló la cadena de explotación de vulnerabilidad de "clic cero" denominada "Shadow Escape", que se origina en fallos de diseño en los límites de confianza de los agentes MCP, permitiendo a los atacantes secuestrar flujos de trabajo en sistemas como ChatGPT y Google Gemini y llevar a cabo el robo de datos sin ser detectados.

**Riesgos del ataque**

Desviación del comportamiento del agente: el agente ejecuta operaciones completamente distintas del objetivo previsto
Ejecución de servicios maliciosos: el agente se convierte en una herramienta para que el atacante ejecute tareas maliciosas
Amenaza a la seguridad de los datos: un agente manipulado puede filtrar o destruir datos
Ruptura de la relación de confianza: la confianza del usuario en el sistema del agente se ve gravemente dañada
Interrupción de la continuidad del negocio: la desviación del agente respecto a los objetivos de negocio provoca interrupción del servicio
Impacto de seguridad en cascada: la manipulación de un agente puede afectar a todo el sistema

**Medidas de mitigación**

Medida de mitigación
Descripción

Mecanismo de verificación de intención
Establecer un mecanismo de verificación y confirmación de la intención del usuario, implementar confirmación de intención en diálogos de múltiples turnos, detectar cambios anómalos en la intención.

Protección de bloqueo de objetivos
Implementar un mecanismo de bloqueo de objetivos del agente, establecer múltiples verificaciones para los cambios de objetivo, restringir los permisos de modificación dinámica de objetivos.

Control de límites de comportamiento
Definir claramente los límites de comportamiento del agente, implementar monitoreo y detección de comportamiento en tiempo real, establecer un mecanismo de bloqueo de comportamiento anómalo.

Análisis de seguridad del contexto
Detectar intentos maliciosos de manipulación del contexto, analizar intenciones de manipulación potenciales en el diálogo, establecer una línea base de seguridad del contexto.

**Referencias**

https://www.freebuf.com/articles/ai-security/454527.html
https://zhuanlan.zhihu.com/p/1928583554805260699

---
### Deriva de Datos

> Número de riesgo: GAARM.0033
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

La deriva de datos se refiere al cambio en las características estadísticas de los datos de entrenamiento con el paso del tiempo o los cambios en el entorno, lo que afecta el rendimiento y la precisión del modelo. Los atacantes pueden construir métodos de ataque dirigidos a la deriva de datos, provocando que, cuando el modelo se enfrenta a nuevos datos distintos de los del periodo de entrenamiento, su precisión de predicción no cumpla con lo esperado, afectando así la fiabilidad y la seguridad del modelo. Por ejemplo, una empresa construyó una función de detección de correo no deseado muy eficaz basada en datos históricos, pero los atacantes pueden en algún momento cambiar el comportamiento de envío de correo no deseado, de modo que, al cambiar los datos introducidos en el modelo, el modelo originalmente construido puede ser engañado.

**Casos de ataque**

Caso 1: GPT-3.5 y GPT-4 presentan deriva de datos

Existe un estudio conjunto de Stanford y Berkeley titulado "How Is ChatGPT's Behavior Changing over Time?", que hizo seguimiento a la precisión de las respuestas de GPT-4 y GPT-3.5. El estudio encontró que tanto GPT-3.5 como GPT-4 presentaron fluctuaciones considerables en su desempeño, e incluso degradación del rendimiento en algunas tareas. La siguiente figura muestra la fluctuación de la precisión del modelo a lo largo de cuatro meses; en algunos casos, la caída de precisión fue bastante severa, con pérdidas de más del 60%.

Deriva de Grandes Modelos (LLM Drift)

Caso
Descripción

| Caso 2 | Identificación y respuesta a problemas de deriva en modelos de aprendizaje automático |

**Riesgos del ataque**

Degradación del rendimiento del modelo: la deriva de datos provoca una disminución en la precisión de predicción del modelo sobre nuevos datos.
Degradación del modelo: los atacantes pueden ir reduciendo gradualmente el rendimiento del modelo introduciendo continuamente muestras de datos específicas.
Riesgo de cumplimiento y reputación: la disminución del rendimiento del modelo puede provocar problemas de cumplimiento normativo, especialmente en sectores altamente regulados como el financiero y el sanitario, además de poder dañar la reputación de la empresa.
Errores de decisión: las decisiones basadas en modelos obsoletos pueden generar resultados erróneos, afectando el negocio.

**Medidas de mitigación**

Medida de mitigación
Descripción

Reentrenamiento del modelo
Cuando se detecta que el modelo ha sufrido deriva, reentrenar el modelo con nuevos datos.

Sistema de detección de anomalías
Desplegar un sistema de detección de anomalías para identificar y gestionar entradas anómalas que puedan provocar la deriva del modelo.

Ejecución automatizada de pruebas del modelo
Validar el modelo en un entorno de preproducción y detectar desviaciones y deriva mediante pruebas, generando luego un informe de pruebas.

**Referencias**

https://www.ibm.com/topics/model-drift
https://www.datacamp.com/tutorial/understanding-data-drift-model-drift
https://mp.weixin.qq.com/s/QbADBoHEqpDBKNkr-so3Ig
https://arxiv.org/pdf/2307.09009.pdf

---
### Abuso de Funcionalidades del Modelo

> Número de riesgo: GAARM.0031
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El abuso de funcionalidades del modelo se refiere principalmente a que, en el contexto de solicitudes controlables al modelo de negocio, los atacantes se apropian de la API del sistema del modelo de negocio y abusan de las funciones del gran modelo de negocio para llevar a cabo operaciones ilegales y maliciosas que cumplan con sus objetivos de ataque, tales como la redacción de correos de phishing maliciosos, la creación de herramientas maliciosas, etc. El abuso de funcionalidades del modelo, por un lado, genera una gran presión de solicitudes sobre el sistema de negocio, y por otro, también conlleva riesgos de cumplimiento normativo para el negocio.

**Casos de ataque**

Ver riesgos secundarios para más detalle

**Riesgos del ataque**

Riesgo de seguridad: el abuso de funciones puede provocar que el modelo ejecute operaciones maliciosas, como generar o difundir contenido dañino, lanzar ciberataques, robar información sensible, etc., constituyendo así una amenaza para la seguridad de los usuarios y del sistema;
Violación de la privacidad: el abuso de las funciones del modelo puede implicar la recopilación, procesamiento o filtración no autorizada de datos privados, perjudicando los derechos de privacidad personal;
Responsabilidad legal: el abuso de funcionalidades del modelo puede implicar conductas ilegales, como infracción de propiedad intelectual, difamación, fraude, etc., lo que puede generar responsabilidad legal;
Problemas éticos y morales: el abuso de las funciones del modelo puede producir resultados inmorales o éticamente controvertidos, como la generación de información falsa, el engaño al público o el agravamiento de la injusticia social;
Crisis de confianza: la confianza del usuario en los sistemas de IA puede verse dañada debido al abuso de funciones, lo que afecta la aceptación y dependencia de la tecnología de IA;
Pérdidas económicas: en el ámbito empresarial, el abuso de funcionalidades del modelo puede provocar pérdidas económicas, como pérdidas financieras causadas por conductas fraudulentas o daños a la reputación comercial;

**Medidas de mitigación**

Medida de mitigación
Descripción

Verificación de contenido de entrada/salida
Identificar e interceptar información maliciosa o inductiva que pueda contener el contenido generado, mediante mecanismos algorítmicos o de revisión manual.

Herramientas de detección de IA
Uso de herramientas de IA como el sistema M01 para mejorar la tasa de detección de correos de phishing.

Capacitación en concienciación de seguridad
Aumentar la vigilancia de los usuarios frente a correos de phishing, educándolos para identificar características de correos sospechosos, como errores ortográficos, gramática inusual, creación de urgencia, etc.

Refuerzo del entrenamiento del modelo
Basándose en métodos como el aprendizaje reforzado con retroalimentación humana, realizar un entrenamiento de refuerzo más riguroso del modelo para identificar y resistir posibles ataques de jailbreak, aumentando la robustez del modelo frente a ataques adversarios.

Alineación de seguridad del modelo
Proporcionar datos de entrenamiento diversificados que cubran diversos escenarios de ataque, aumentando la capacidad de generalización y la robustez del modelo mediante la incorporación de mecanismos de barrera de seguridad durante la fase de entrenamiento del modelo.

---
### Falsificación de Información en Video

> Número de riesgo: GAARM.0031.005
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Los atacantes pueden generar videos falsos realistas mediante técnicas como las redes generativas antagónicas (GAN). Estos videos falsos pueden utilizarse con fines de publicidad fraudulenta, falsificación de pruebas, fraude en línea, entre otros. Además, la falsificación de información en video también puede provocar la filtración de información de identidad personal. Esto conlleva graves riesgos para la privacidad personal y la seguridad de los datos.

**Casos de ataque**

Caso
Descripción

Caso 1
Un empleado del área financiera recibió un correo electrónico de un supuesto CFO y fue invitado a una videoconferencia en la que todos los participantes eran imágenes falsas de deepfake generadas a partir de fragmentos de video y audio públicos, lo que provocó pérdidas de 200 millones de dólares de Hong Kong (aproximadamente 180 millones de yuanes) para la empresa.

Caso 2
Se generó el contenido del discurso con ChatGPT, un avatar virtual con Midjourney, la voz con ElevenLabs y el video con sincronización labial con D-ID, produciendo así un video corto completo.

**Riesgos del ataque**

Información engañosa: los videos falsificados pueden utilizarse para difundir información falsa, influyendo en la opinión pública.
Daño a la reputación: empresas o individuos pueden verse perjudicados por videos falsificados, afectando su reputación e incluso provocando pérdidas patrimoniales.
Consecuencias legales: publicar videos falsificados puede acarrear responsabilidad legal, especialmente en casos relacionados con difamación o violación de la privacidad.

**Medidas de mitigación**

Medida de mitigación
Descripción

Revisión de contenido
Uso de herramientas de reconocimiento de imágenes y revisión de contenido para detectar videos falsificados o manipulados.

Tecnología de marca de agua
Identificar claramente los videos generados, informando a los usuarios de que su origen no es real.

Verificación de origen
Uso de herramientas forenses de imágenes para examinar los metadatos y el historial de edición de los videos.

Formulación de políticas
Establecer políticas y marcos legales claros para el uso y la difusión de videos falsificados.

**Referencias**

https://stcn.com/article/detail/1250289.html
https://www.51cto.com/aigc/912.html

---
### Generación de Correos de Phishing

> Número de riesgo: GAARM.0031.002
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Los correos de phishing son correos fraudulentos que los atacantes pueden inducir a un LLM a generar mediante medios especiales, como la construcción cuidadosa de entradas de prompt o la elusión de restricciones de seguridad a través de la API. Al disfrazarlos de comunicaciones legítimas, se induce al modelo a filtrar información sensible, como credenciales de inicio de sesión, datos internos, etc. Una vez que esta información es obtenida de forma maliciosa, la seguridad del gran modelo puede verse comprometida, afectando así la privacidad y la seguridad de los datos de los usuarios que utilizan dicho modelo.

**Casos de ataque**

Caso 1: como se muestra en la imagen, se solicitó a WormGPT que elaborara un correo electrónico

El objetivo era presionar a un gerente de cuentas desprevenido para obligarlo a pagar una factura falsa.

Phishing Emails

Caso 2
Este artículo describe la generación y aplicación de herramientas maliciosas mediante IA generativa. Los atacantes indican a la IA que incruste URLs maliciosas en el código; cuando el usuario abre un archivo como uno de Excel, el sistema descarga y ejecuta automáticamente el malware, generando así un riesgo de seguridad.
Caso 3
Este artículo revela que los ciberdelincuentes pueden eludir con facilidad las medidas de protección de OpenAI, por ejemplo, haciéndose pasar por investigadores para encubrir su intención maliciosa, logrando así que el LLM genere correos de phishing maliciosos, con consecuencias adversas.

**Riesgos del ataque**

Toma de control de cuentas: los correos de phishing pueden imitar a proveedores de servicios de correo electrónico legítimos o empresas, induciendo a los usuarios a introducir sus credenciales de inicio de sesión, permitiendo así a los atacantes tomar control de la cuenta de correo del usuario;
Daño a la reputación empresarial: pueden imitar correos oficiales de empresas u organizaciones, enviando información fraudulenta a los contactos del usuario, dañando así la reputación de la empresa u organización;
Robo de datos: los correos de phishing generados por el gran modelo pueden contener enlaces o código malicioso; una vez que el usuario hace clic o descarga, puede provocar la caída del sistema informático del usuario, pérdida de datos, filtración de información de identidad y otros problemas graves;

**Medidas de mitigación**

Medida de mitigación
Descripción

Verificación de contenido de entrada/salida
Identificar e interceptar información maliciosa o inductiva que pueda contener el contenido generado, mediante mecanismos algorítmicos o de revisión manual.

Herramientas de detección de IA
Uso de herramientas de IA como el sistema M01 para mejorar la tasa de detección de correos de phishing.

Capacitación en concienciación de seguridad
Aumentar la vigilancia de los usuarios frente a correos de phishing, educándolos para identificar características de correos sospechosos, como errores ortográficos, gramática inusual, creación de urgencia, etc.

**Referencias**

https://mp.weixin.qq.com/s/8Ca4HmkafP9SxjHayC9zdQ
https://mp.weixin.qq.com/s/-0i0SlGat-Y5hXcM3EIGiw
https://mp.weixin.qq.com/s/2Ai4nKOzEnkhqJD903O8mA

---
### Falsificación de Información en Audio

> Número de riesgo: GAARM.0031.004
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Los atacantes pueden generar audios falsos realistas mediante técnicas como las redes generativas antagónicas (GAN). Estos audios falsos pueden utilizarse con fines de publicidad fraudulenta, falsificación de pruebas, fraude en línea, entre otros. Además, la falsificación de información en audio también puede provocar la filtración de información de identidad personal. Los atacantes, al analizar fotografías personales, información de redes sociales y otros datos públicos, pueden utilizar la IA para generar imágenes de rostros realistas y usarlas para suplantar la identidad de otras personas. Esto conlleva graves riesgos para la privacidad personal y la seguridad de los datos.

**Casos de ataque**

Caso
Descripción

Caso 1
Un empleado del área financiera recibió un correo electrónico de un supuesto CFO y fue invitado a una videoconferencia en la que todos los participantes eran imágenes falsas de deepfake generadas a partir de fragmentos de video y audio públicos, lo que provocó pérdidas de 200 millones de dólares de Hong Kong (aproximadamente 180 millones de yuanes) para la empresa.

Caso 2
Estafadores utilizaron IA para imitar la voz de familiares de las víctimas, realizando llamadas fraudulentas para obtener bienes mediante engaño; este tipo de casos se ha vuelto frecuente en Estados Unidos, provocando graves consecuencias en la opinión pública.

**Riesgos del ataque**

Información engañosa: los audios falsificados pueden utilizarse para difundir información falsa, influyendo en la opinión pública.
Daño a la reputación: empresas o individuos pueden verse perjudicados por audios falsificados, afectando su reputación e incluso provocando pérdidas patrimoniales.
Consecuencias legales: publicar audios falsificados puede acarrear responsabilidad legal, especialmente en casos relacionados con difamación o violación de la privacidad.

**Medidas de mitigación**

Medida de mitigación
Descripción

Revisión de contenido
Uso de herramientas de reconocimiento de imágenes y revisión de contenido para detectar audios falsificados o manipulados.

Tecnología de marca de agua
Identificar claramente los audios generados, informando a los usuarios de que su origen no es real.

Verificación de origen
Uso de herramientas forenses de imágenes para examinar los metadatos y el historial de edición de los audios.

Formulación de políticas
Establecer políticas y marcos legales claros para el uso y la difusión de audios falsificados.

**Referencias**

https://stcn.com/article/detail/1250289.html
https://www.51cto.com/aigc/912.html
https://36kr.com/p/2190993024614530

---

# Seguridad de Aplicaciones de IA - Fase de Aplicación - Inyección de Prompt y sus Variantes

> Fuente: Comunidad AISS NSFOCUS de Seguridad de Grandes Modelos | Extraído de ai-app-app.md
> Categoría de riesgo: Inyección de Prompt (GAARM.0039 Inyección directa / 0040.x Indirecta/XSS/Memory/Gusano / 0043.x Confusión de palabras clave y sinónimos / 0044 Codificación adversaria / 0045 Inducción inversa / 0061 Inyección multimodal)

---

### Inyección de Prompt

> Número de riesgo: GAARM.0039
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

La inyección de Prompt es un proceso mediante el cual el atacante utiliza entradas especialmente construidas para sobrescribir o manipular las instrucciones originales de los LLM. Dado que el lenguaje natural es en sí mismo ambiguo, a menudo no existe un límite claro entre las instrucciones y los datos, lo que permite al atacante contaminar la salida del modelo mediante entradas externas maliciosas. Este ataque suele ocurrir cuando se incluye una entrada no confiable como parte del prompt. Los LLM pueden reconocer y procesar lenguaje natural, y dado que este es en sí mismo ambiguo, las instrucciones y los datos a menudo carecen de un límite claro; el atacante puede incluir instrucciones dentro de campos de datos que controla, mientras que el sistema, a nivel subyacente, no puede distinguir entre datos e instrucciones.

**Casos de ataque**

Caso
Descripción

Caso 1
Se manipuló el prompt de GPT-3 mediante una entrada maliciosa, ordenando al modelo que ignorara sus instrucciones previas.

Caso 2
Se utilizaron múltiples métodos para realizar ataques de inyección de Prompt.

**Riesgos del ataque**

Una inyección de Prompt exitosa puede provocar daños como la filtración del meta-Prompt, el jailbreak del modelo y el abuso de las funciones del modelo.

Generación de contenido malicioso: el atacante puede aprovechar la inyección de Prompt para generar contenido inapropiado, incluyendo amenazas, difamación u otra información maliciosa.
Filtración de datos: si los LLM se utilizan para emitir información sensible, un ataque de inyección de Prompt puede provocar la filtración de datos.
Seguridad del sistema: en algunos casos, la inyección de Prompt puede utilizarse para generar y ejecutar código malicioso.
Abuso del modelo: mediante técnicas de ataque como el secuestro de objetivos, el atacante logra que los LLM se desvíen de la configuración del sistema predefinida y ejecuten otras instrucciones personalizadas, aumentando el riesgo de abuso del modelo.

**Medidas de mitigación**

Medida de mitigación
Descripción

Refuerzo del contenido del Prompt
Adoptar soluciones similares al Lenguaje de Marcado de Chat de OpenAI (ChatML), para reforzar la estructura y el contenido del Prompt, intentando aislar el prompt real del usuario de otro contenido.

Alineación de seguridad del modelo
Proporcionar datos de entrenamiento diversificados que cubran diversos escenarios de ataque, aumentando la capacidad de generalización y la robustez del modelo mediante la incorporación de mecanismos de barrera de seguridad durante la fase de entrenamiento del modelo.

Validación de entrada/salida
Establecer guardias de seguridad externas en los lados de entrada y salida del modelo, basadas en reglas, algoritmos de clasificación, grandes modelos de seguridad, etc., para detectar y filtrar el contenido de entrada y salida.

Monitoreo y registro
Monitorear y registrar los registros de interacción de los LLM, para permitir la detección y el análisis posterior de posibles ataques de inyección de Prompt.

**Referencias**

https://aclanthology.org/2024.scalellm-1.2/
https://atlas.mitre.org/techniques/AML.T0051
https://josephthacker.com/ai/2023/05/19/prompt-injection-poc.html
https://simonwillison.net/2022/Sep/12/prompt-injection/

---
### Secuestro de Contenido de Sesión mediante XSS

> Número de riesgo: GAARM.0040.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El secuestro de contenido de sesión mediante XSS es un método de ataque de inyección de prompt indirecta que aprovecha el proceso mediante el cual los grandes modelos de lenguaje (LLM) obtienen información externa. Cuando el usuario interactúa con el LLM a través de la interfaz proporcionada por este (como una interfaz web, una interfaz API, una aplicación, etc.), el atacante inyecta indirectamente instrucciones de prompt maliciosas, aprovechando características como el análisis de etiquetas Markdown y de la etiqueta HTML img por parte del front-end de la aplicación LLM, para resumir el contenido de la sesión de chat actual e incrustar claves sensibles, datos y otra información dentro del atributo src de la etiqueta img, logrando así la filtración del contenido de la sesión.

**Casos de ataque**

Caso
Descripción

Caso 1
El atacante aprovechó la función de actualización de Google Bard, construyendo una etiqueta de imagen Markdown especial que hizo que Bard renderizara una imagen apuntando al servidor del atacante, logrando así el robo de datos.

Caso 2
Se aprovechó que el modelo de Azure AI Playground permite adjuntar prompts a la URL del atributo src mediante inyección de imagen Markdown para su renderizado, provocando riesgos como la filtración de datos.

Caso 3
El atacante utilizó la función de acceso directo de un plugin de ChatGPT a los subtítulos de YouTube, controlando el contenido de los subtítulos mediante inyección indirecta de Prompt para manipular el comportamiento de la IA.

Caso 4
El atacante puede aprovechar la función de renderizado de imágenes Markdown de ChatGPT para robar el historial de chat; el atacante controla el comportamiento de la IA, solicitando que resuma el historial de chat y lo adjunte a una URL para robar los datos.

Caso 5
El atacante roba automáticamente datos de la sesión de chat mediante inyección de imagen Markdown.

Caso 6
El atacante puede indicar a ChatGPT que utilice un plugin para registrar la conversación, generar una URL apuntando al registro, y filtrar el enlace mediante inyección de imagen Markdown, para obtener todo el historial de la conversación.

Caso 7
Dado que los agentes LLM (aplicaciones cliente como Bing Chat o ChatGPT) son vulnerables a ataques de inyección de Prompt, el atacante puede aprovechar esta vulnerabilidad para realizar la exfiltración automática de datos adjuntando datos sensibles a la URL de una imagen.

**Riesgos del ataque**

Filtración de datos: el atacante puede obtener información sensible del usuario en la sesión actual, incluyendo tokens de sesión, información personal, historial de chat, etc.
Secuestro de sesión: el atacante puede apropiarse de la sesión del usuario mediante el token de sesión obtenido.

**Medidas de mitigación**

Medida de mitigación
Descripción

Validación de entrada/salida
Validar y limpiar estrictamente todos los datos de entrada y salida, para eliminar o corregir cualquier inyección sospechosa o contenido generado.

Política de Seguridad de Contenido (CSP)
Implementar una política de seguridad de contenido (CSP) estricta, para bloquear la ejecución de scripts maliciosos y comportamientos de exfiltración de datos.

Principio de mínimo privilegio
Garantizar un sandboxing correcto y limitar las capacidades de los LLM, restringiendo que mecanismos como plugins y Agents obtengan información de fuentes no confiables.

Aprobación con intervención humana
Otorgar a los usuarios mayor control, permitiéndoles gestionar el uso de plugins y el flujo de datos.

**Referencias**

https://systemweakness.com/new-prompt-injection-attack-on-chatgpt-web-version-ef717492c5c2

---
### Inyección Indirecta de Prompt

> Número de riesgo: GAARM.0040
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

En el proceso de procesamiento de lenguaje natural, los LLM presentan una vulnerabilidad ante la inyección maliciosa de prompts. El atacante oculta el Prompt dentro de diversos datos que el sistema LLM procesará, como texto, contenido multimedia, información extraída de bases de datos o sitios web, etc., manipulando así al LLM mediante el Prompt para que produzca respuestas dañinas, como la ejecución de código malicioso o la filtración de información sensible. Por ejemplo, se puede escribir código malicioso en un archivo subido al LLM; cuando este procesa los datos del archivo, ejecutará el código malicioso, provocando así un daño.

**Casos de ataque**

Caso
Descripción

Caso 1
El atacante implantó código de inyección en un sitio web visitado por el usuario, haciendo que Bing Chat, sin que el usuario lo supiera, buscara y filtrara información personal.

Caso 2
El atacante controló los datos recuperados por un plugin de LLM, aprovechando el mecanismo de renderizado de imágenes Markdown, para enviar el historial de chat como parámetro de consulta al servidor del atacante.

Caso 3
Este caso muestra un método de ataque contra M365 Copilot: mediante el envío de un correo electrónico con contenido malicioso, incluso sin que el usuario lo abra, es posible controlar remotamente a Copilot, provocando un ataque proveniente de un tercero.

**Riesgos del ataque**

Ejecución de código malicioso: al inyectar código o datos maliciosos, el atacante puede intentar obtener un punto de apoyo en el sistema, para luego controlarlo o dañarlo aún más.
Filtración de datos: el atacante puede usar la inyección indirecta para engañar al usuario, haciendo que este ejecute operaciones no previstas o filtre información sensible.

**Medidas de mitigación**

Medida de mitigación
Descripción

Validación de entrada
Validar y limpiar estrictamente todos los datos de entrada, para eliminar o corregir cualquier contenido de inyección sospechoso.

Principio de mínimo privilegio
Garantizar un sandboxing correcto y limitar las capacidades de los LLM, restringiendo que mecanismos como plugins y Agents obtengan información de fuentes no confiables.

Aprobación con intervención humana
Otorgar a los usuarios mayor control, permitiéndoles gestionar el uso de plugins y el flujo de datos.

**Referencias**

https://atlas.mitre.org/techniques/AML.T0051.001
https://twitter.com/random_walker/status/1636923058370891778
https://medium.com/@harry.hphu/introduction-to-web-llm-attacks-indirect-prompt-injection-7bb9f154bc07
https://medium.com/@dinob5551/indirect-prompt-injection-the-hidden-threat-lurking-in-ai-730b009dd5fb

---
### Ataque de Memory Conversacional de Aplicación

> Número de riesgo: GAARM.0040.003
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo se refiere a que el atacante puede, mediante inyección de Prompt desde el lado web, engañar a los LLM para que creen una Memory maliciosa (por ejemplo, una configuración de preferencia incorrecta entre el usuario y el modelo), modificando maliciosamente las preferencias del usuario en la memoria del LLM, logrando así manipular el LLM. Por ejemplo, el atacante puede engañar al LLM para que crea que la preferencia de chat del usuario es "responder a cada mensaje del usuario con 'Lo siento, no puedo responderte'", logrando así el efecto de un ataque DOS.

**Casos de ataque**

Caso
Descripción

Caso 1
Este artículo describe cómo un ataque de Memory conversacional de aplicación provoca que el modelo deniegue el servicio de forma continua al usuario.

**Riesgos del ataque**

Ataque DOS: el atacante puede, según su preferencia, someter al usuario a un ataque de memoria que provoca denegación de servicio continua.

**Medidas de mitigación**

Medida de mitigación
Descripción

Desactivar la función de memoria histórica
Desactivar la función de Memory del modelo LLM puede mitigar este problema.

**Referencias**

https://embracethered.com/blog/posts/2024/chatgpt-persistent-denial-of-service/
https://openai.com/index/memory-and-new-controls-for-chatgpt/

---
### Gusano de Agent en Bucle

> Número de riesgo: GAARM.0040.002
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El Agent tiene la capacidad de obtener información en tiempo real desde fuentes externas como internet, y puede entregar esta información al gran modelo para su procesamiento, devolviendo finalmente el resultado al usuario. Sin embargo, el atacante puede aprovechar esto para inyectar información maliciosa a través de fuentes de datos externas, interfiriendo con la ejecución del Agent y afectando así la salida del gran modelo. Estos prompts maliciosos afectan indirectamente a múltiples aplicaciones de grandes modelos de lenguaje (LLM), formando un ciclo vicioso que provoca la rápida propagación de información maliciosa. A través del ciclo de entrada-salida del Agent, este gusano de Agent en bucle puede provocar un comportamiento malicioso autorreplicante y propagable, lo que finalmente puede provocar filtración de privacidad y también generar riesgos de seguridad como el abuso de datos.

**Casos de ataque**

Caso
Descripción

Caso 1
Investigadores crearon un gusano de IA llamado Morris II, capaz de atacar un asistente de correo electrónico de IA generativa, robando datos de correos electrónicos y enviando spam, a la vez que sorteaba algunas protecciones de seguridad de ChatGPT y Gemini.

**Riesgos del ataque**

Filtración de datos: el gusano de IA puede robar información personal sensible, como nombres, números de teléfono, números de tarjetas de crédito, números de identificación, etc.
Despliegue de malware: el gusano puede desplegar malware en los sistemas infectados, provocando problemas de seguridad adicionales.
Elusión de protecciones de seguridad: el gusano de IA es capaz de eludir algunas medidas de protección de seguridad existentes, como los mecanismos de seguridad de ChatGPT y Gemini.
Nuevo tipo de ciberataque: el gusano de IA representa una forma de ciberataque previamente no ampliamente reconocida, lo que representa un desafío para las medidas de protección de seguridad existentes.

**Medidas de mitigación**

Medida de mitigación
Descripción

Validación de entrada/salida
Aplicar medidas estrictas de validación y verificación a los datos que ingresan al Agent para su procesamiento y despliegue.

Diseño seguro de LLM Agent
Adoptar medidas de seguridad tradicionales, como garantizar el diseño seguro de la aplicación Agent y monitorear posibles vulnerabilidades de seguridad.

Aprobación con intervención humana
Mantener al ser humano en el ciclo, garantizando que el LLM Agent requiera aprobación humana antes de ejecutar acciones, evitando que el sistema de IA envíe correos electrónicos u otras acciones potencialmente riesgosas de forma autónoma.

**Referencias**

https://mp.weixin.qq.com/s/2bm7nuXkORLZ20mfpOmwrA

---
### Ataque de Inducción Inversa y Supresión

> Número de riesgo: GAARM.0045
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo consiste en añadir instrucciones específicas en el prompt para hacer que los LLM eviten usar ciertas respuestas de rechazo específicas al generar una respuesta, aumentando así la probabilidad de obtener el contenido inseguro o inapropiado que el atacante desea. Este ataque aprovecha la naturaleza autorregresiva del modelo para inducirlo, ya que la generación de contenido del modelo se basa en la salida anterior para predecir la siguiente palabra; mediante una solicitud especial que impide que los LLM utilicen ciertas palabras o frases específicas al generar la respuesta, como "lo siento", "no puedo", "no es posible", etc., se provoca que el modelo genere contenido inapropiado o que viole las políticas de seguridad.

**Casos de ataque**

Caso
Descripción

Caso 1
Se utilizó inyección de prefijo + ataque de supresión inversa para eludir las restricciones de seguridad de ChatGPT 3.5, logrando la salida de contenido de riesgo relacionado con actividades ilegales y delictivas.

**Riesgos del ataque**

Generación de contenido inapropiado: los LLM pueden generar contenido de riesgo que incluya instrucciones ilegales, violencia, pornografía, temas políticamente sensibles, etc.
Elusión del mecanismo de seguridad: el atacante puede eludir el mecanismo de seguridad de los LLM, provocando que el modelo genere el contenido de riesgo que el atacante desea.

**Medidas de mitigación**

Medida de mitigación
Descripción

Refuerzo de la robustez del modelo
Mediante entrenamiento y aprendizaje reforzado, mejorar la capacidad del LLM para identificar y resistir este tipo de ataques.

Monitoreo y filtrado de entradas
Monitorear en tiempo real la salida de los LLM, filtrando oportunamente el contenido inseguro o inapropiado.

---
### Ataque de Inyección Multimodal Coordinada

> Número de riesgo: GAARM.0061
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El ataque de inyección multimodal coordinada es una técnica de ataque avanzada que aprovecha la relación de coordinación entre múltiples modalidades (texto, imagen, audio, video, etc.) para incrustar instrucciones maliciosas. El atacante, mediante la construcción cuidadosa de contenido malicioso entre modalidades, aprovecha el mecanismo de asociación semántica del modelo multimodal al procesar y comprender información de diferentes modalidades, incrustando instrucciones maliciosas en contenido multimodal aparentemente inofensivo. El núcleo de este ataque radica en eludir el mecanismo de detección de seguridad de una sola modalidad, logrando el objetivo del ataque mediante el efecto de coordinación entre modalidades, lo que puede provocar filtración de datos, manipulación del comportamiento del modelo o ejecución de operaciones no previstas.

**Casos de ataque**

Caso
Descripción

Caso 1
El atacante aprovecha la inyección de conflicto entre modalidades (CMCI, Cross-Modal Conflicting Injection), insertando pares imagen-texto adversarios especiales en la base de conocimiento a través del mecanismo normal de actualización del sistema. Estos pares parecen semánticamente alineados al momento de la recuperación (por ejemplo, la imagen muestra neumonía, pero el texto describe "pulmones claros"), pero su contenido real es contradictorio, induciendo así a la IA a emitir conclusiones completamente erróneas durante el diagnóstico (como confundir la neumonía con un estado normal), provocando un grave riesgo de seguridad médica.

**Riesgos del ataque**

Filtración de datos: se induce al modelo a filtrar datos de entrenamiento o información sensible
Manipulación del comportamiento: se manipula la salida y el comportamiento del modelo mediante instrucciones intermodales
Elusión de seguridad: se eluden los mecanismos de detección y control de seguridad de una sola modalidad
Escalamiento de privilegios: se aprovecha la coordinación entre modalidades para obtener mayores privilegios del sistema
Violación de la privacidad: se obtiene información privada del usuario mediante análisis multimodal

**Medidas de mitigación**

Medida de mitigación
Descripción

Detección de coordinación entre modalidades
Establecer un mecanismo de detección de seguridad de coordinación multimodal, implementar análisis de asociación semántica entre modalidades, y detectar patrones de combinación de modalidades anómalos.

Verificación de seguridad multidimensional
Verificar simultáneamente la seguridad de múltiples modalidades, establecer una verificación de consistencia entre modalidades e implementar el intercambio de inteligencia de amenazas entre modalidades.

Refuerzo del proceso de fusión
Incorporar verificaciones de seguridad durante el proceso de fusión multimodal, implementar el ajuste dinámico de los pesos de las modalidades, y establecer la detección de patrones de fusión anómalos.

Procesamiento de aislamiento de modalidades
Realizar un preprocesamiento de aislamiento para las diferentes modalidades, implementar filtrado de seguridad a nivel de modalidad, y establecer un mecanismo de comunicación segura entre modalidades.

**Referencias**

Manipulación de agentes multimodales mediante inyección de prompt entre modalidades
¿Cómo hacer más seguros los sistemas de IA médica? Vulnerabilidades y amenazas en sistemas RAG médicos multimodales

---
### Ataque de Codificación Adversaria

> Número de riesgo: GAARM.0044
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El ataque de codificación adversaria es una técnica de ataque dirigida a los mecanismos de detección de defensa en los lados de entrada y salida de los LLM; el atacante intenta eludir las verificaciones de seguridad o inyectar contenido malicioso mediante la codificación o transformación de datos (como el uso de codificación base64). Este ataque se dirige a la capa de codificación del modelo NLP, intentando eludir la capacidad de comprensión textual del modelo, afectando directamente la generación de características internas.
Dado que los LLM han sido entrenados con diversos tipos de datos, incluyendo texto codificado, admiten la operación normal de decodificación y completan la ejecución de instrucciones maliciosas o la exfiltración de datos sensibles.

**Casos de ataque**

Caso
Descripción

Caso 1
Se utilizó un ataque de codificación adversaria para eludir las restricciones de seguridad de ChatGPT, obteniendo información de claves almacenadas.

Caso 2
Este artículo investiga cómo los modelos de PLN basados en texto pueden verse interferidos y engañados mediante perturbaciones de codificación manipuladas; estas perturbaciones aprovechan la funcionalidad de codificación del lenguaje para alterar la salida del modelo y aumentar el tiempo de ejecución de inferencia. Por ejemplo, se presentan caracteres únicos con glifos idénticos o visualmente similares para perturbar la entrada del modelo.

**Riesgos del ataque**

Elusión del mecanismo de seguridad: el atacante puede aprovechar la capacidad de codificación/decodificación del modelo para eludir las verificaciones de seguridad del contenido.
Filtración de datos: el atacante puede aprovechar operaciones de codificación Base64 para ocultar instrucciones o datos maliciosos, provocando la filtración de información sensible.
Ejecución de código no autorizada: se puede inyectar código malicioso en los LLM mediante codificación Base64, provocando la ejecución de código no autorizada, lo que puede dañar la integridad y la seguridad del sistema.
Operaciones maliciosas: el atacante puede aprovechar la codificación Base64 para manipular a los LLM y hacer que ejecuten diversas operaciones maliciosas, como la manipulación de datos o el secuestro de sesiones, poniendo en peligro la seguridad del sistema y del usuario.

**Medidas de mitigación**

Medida de mitigación
Descripción

Validación de entrada/salida
Validar los datos de entrada y salida, para evitar que datos codificados en Base64 u otros formatos, maliciosos o inesperados, se introduzcan en los LLM o se impriman directamente.

Alineación de seguridad del modelo
Entrenar al gran modelo en matices del lenguaje y técnicas de codificación para identificar las características de estos ataques.

**Referencias**

https://promptengineering.org/mind-over-malware-battling-the-growing-arsenal-of-attacks-on-large-language-models/
https://www.toolify.ai/ai-news/the-future-of-hacking-5-terrifying-llm-security-threats-544868

---
### Confusión de Palabras Clave

> Número de riesgo: GAARM.0043
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo se refiere a la aplicación de un tratamiento especial sobre las palabras clave del Prompt (homófonos, sinónimos, división de palabras u otras formas de manipulación textual), de modo que, manteniendo un significado similar, tras la tokenización ya no conserven un significado de riesgo, eludiendo así las restricciones del mecanismo de seguridad del modelo sobre palabras sensibles.

**Casos de ataque**

En los LLM en inglés, los métodos comunes de confusión de palabras clave incluyen: confusión de letras (bomb -> b0mb), sustitución por sinónimos (bomb -> explosive), división de palabras (bomb -> b-o-m-b).
Para los LLM en chino, debido a las diferencias en los métodos de segmentación de palabras, los métodos de confusión de palabras clave también presentan diferencias notables; los métodos comunes de confusión de palabras clave en chino incluyen la sustitución por pinyin (por ejemplo, escribir parcialmente en pinyin la palabra que significa "bomba"), la sustitución por sinónimos (por ejemplo, reemplazar la palabra "bomba" por "explosivo"), la sustitución por caracteres de forma visualmente similar (por ejemplo, sustituir un carácter por otro gráficamente parecido), etc.

**Riesgos del ataque**

Generación de contenido inapropiado: el atacante puede aprovechar técnicas de confusión de palabras clave para eludir los sistemas automáticos de revisión de contenido, publicando o difundiendo contenido malicioso, como violencia, terrorismo o información pornográfica.
Elusión del mecanismo de seguridad: el atacante induce maliciosamente al modelo a producir una salida incorrecta, para engañar al sistema y provocar que tome malas decisiones o ejecute operaciones peligrosas.

**Medidas de mitigación**

Medida de mitigación
Descripción

Alineación de seguridad del modelo
Mediante entrenamiento y aprendizaje reforzado, mejorar la capacidad del LLM para identificar y resistir este tipo de ataques.

Validación de entrada/salida
En el lado de entrada, actualizar y mejorar continuamente el sistema de filtrado de vocabulario para identificar y bloquear palabras sensibles ofuscadas; en el lado de salida, monitorear el contenido generado por los LLM, identificando contenido potencialmente riesgoso mediante técnicas de análisis de seguridad de contenido.

**Referencias**

https://mp.weixin.qq.com/s/eFDQWYYCOe_SSiourhTxig

---
### Ataque de Sustitución por Sinónimos

> Número de riesgo: GAARM.0043.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El ataque de sustitución por sinónimos es un método de ataque que utiliza sinónimos con el mismo significado o un significado similar al de palabras o frases sensibles, para eludir las medidas de protección de seguridad del modelo y así obtener o filtrar las instrucciones internas o la información sensible del modelo. A medida que los LLM se vuelven más grandes, resulta cada vez más difícil realizar un ajuste fino (fine-tuning) para cada ejemplo de ataque existente, lo que hace que el modelo sea vulnerable a ataques de sustitución por sinónimos. Por ejemplo, en un asistente de programación, el atacante puede sustituir "remove" por "delete", "harm" por "destroy", etc., intentando eludir la verificación de palabras clave.

**Casos de ataque**

Caso
Descripción

Caso 1
El atacante eludió con éxito el filtro del modelo mediante la sustitución por sinónimos, logrando la filtración de la configuración del Prompt del sistema.

**Riesgos del ataque**

Filtración de información sensible: el atacante puede obtener las instrucciones internas del modelo, incluyendo, entre otros, el prompt del sistema, contraseñas y otra información sensible.
Elusión del mecanismo de seguridad: el atacante puede aprovechar el ataque de sustitución por sinónimos para eludir la protección de seguridad del modelo, provocando que el modelo genere salidas no deseadas o ejecute operaciones no autorizadas.

**Medidas de mitigación**

Medida de mitigación
Descripción

Alineación de seguridad del modelo
Proporcionar datos de entrenamiento diversificados que cubran diversos escenarios de ataque, para aumentar la capacidad de generalización y la robustez del modelo.

Validación de entrada/salida
En el lado de entrada, actualizar y mejorar continuamente el sistema de filtrado de vocabulario para identificar y bloquear palabras sensibles ofuscadas; en el lado de salida, monitorear el contenido generado por los LLM, identificando contenido potencialmente riesgoso mediante técnicas de análisis de seguridad de contenido.

**Referencias**

https://arxiv.org/html/2402.16914v1

---

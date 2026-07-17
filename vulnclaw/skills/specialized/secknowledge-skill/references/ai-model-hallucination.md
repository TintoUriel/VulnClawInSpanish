# Seguridad de Modelos de IA - Fase de Aplicación - Riesgo de Alucinación

> Fuente: Comunidad AISS NSFOCUS de Seguridad de Grandes Modelos | Extraído de ai-model-app.md
> Categoría de riesgo: Alucinación (GAARM.0028.x + 0064 Alucinación transmodal)

---

### Alucinación Fáctica

> Número de riesgo: GAARM.0028.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Este riesgo se refiere a que el contenido generado por el modelo no coincide con hechos verificables del mundo real o contiene información fabricada. Este riesgo puede originarse de muchas formas posibles, y puede introducirse en cualquier etapa del ciclo de vida del modelo, desde el entrenamiento hasta la aplicación. Además, un atacante puede construir deliberadamente un vector de ataque para provocar que el modelo alucine; por ejemplo, alimentar al modelo con una cadena de caracteres aleatoria sin sentido puede afectar la veracidad de su salida. Esto puede acabar favoreciendo la propagación de noticias falsas y teorías de la conspiración, produciendo un impacto negativo profundo en la sociedad, incluyendo entre otros: desinformar al público, erosionar la veracidad de la información y perturbar el orden social.
La alucinación fáctica puede clasificarse en las siguientes categorías:

Inconsistencia fáctica: la salida del modelo contradice información ya conocida del mundo real.
Fabricación fáctica: el contenido generado por el modelo se basa completamente en invención, sin que su exactitud pueda verificarse con ninguna información del mundo real.

**Casos de ataque**

Caso 1: al preguntarle al modelo quién fue la primera persona en pisar la Luna, el modelo inventó un personaje ficticio.


  
Caso de alucinación fáctica

**Riesgos del ataque**

Propagación de información falsa: la alucinación fáctica puede provocar la difusión de información falsa, especialmente en redes sociales y otras plataformas en línea. Esto no solo desinforma al público, sino que también puede agravar problemas sociales como las noticias falsas y las teorías de la conspiración.
Riesgo legal y de cumplimiento: generar contenido con hechos inexactos puede infringir requisitos legales y de cumplimiento específicos de ciertos sectores, como la exactitud de la información médica o la fiabilidad del asesoramiento financiero, lo que puede derivar en demandas legales o sanciones.
Ética y responsabilidad social: la alucinación fáctica puede ir en contra de los principios éticos y de responsabilidad social, especialmente cuando la información errónea afecta temas sensibles (como política, salud, seguridad, etc.), pudiendo producir un impacto negativo en la sociedad.
Disminución de la confianza del usuario: los errores fácticos frecuentes pueden reducir la confianza de los usuarios en el sistema de IA, afectando así su disposición a usarlo y la adopción de la tecnología.

**Medidas de mitigación**

Medida de mitigación
Descripción

Revisión humana y mecanismo de retroalimentación
Someter la salida del modelo a revisión humana y a un mecanismo de retroalimentación, para detectar y corregir oportunamente los errores en la salida del modelo y optimizarlo continuamente.

Aprendizaje por conjuntos (ensemble) y fusión multi-modelo
Mediante aprendizaje por conjuntos o fusión de múltiples modelos, combinar las ventajas de varios modelos para mejorar el rendimiento predictivo global y reducir el fenómeno de alucinación.

Aplicación de técnicas de regularización
Aplicar técnicas de regularización (como la regularización L1, L2) puede evitar el sobreajuste del modelo y mejorar su capacidad de generalización.

**Referencias**

https://www.lakera.ai/blog/guide-to-hallucinations-in-large-language-models
https://arxiv.org/pdf/2305.13534.pdf

---
### Alucinación de Fidelidad

> Número de riesgo: GAARM.0028.002
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

La alucinación de fidelidad se refiere a la existencia de inconsistencias entre el contenido generado y las instrucciones o la información de contexto proporcionadas por el usuario. Existen muchos vectores de ataque que pueden provocar que un gran modelo produzca alucinaciones de fidelidad. Por ejemplo: aplicar pequeñas perturbaciones a los datos de entrada para que el modelo genere predicciones erróneas o información falsa, afectando la lógica del modelo; consultar el modelo repetidamente para inferir su lógica interna y así diseñar entradas que induzcan alucinaciones; o utilizar redes generativas antagónicas (GAN) para generar muestras de datos falsas que induzcan a otros modelos a producir salidas erróneas.
La alucinación de fidelidad se divide en los siguientes tres tipos:

Inconsistencia de instrucciones: el LLM ignora las instrucciones específicas proporcionadas por el usuario. Por ejemplo, se le indica traducir una pregunta al español, pero el modelo responde en inglés.
Inconsistencia de contexto: el contenido generado por el modelo incluye información que no aparece en el contexto proporcionado o que lo contradice. Por ejemplo, el LLM afirma que el Nilo nace en una cordillera montañosa, en lugar de la región de los Grandes Lagos mencionada en la entrada del usuario.
Inconsistencia lógica: la salida del modelo contiene errores lógicos, aunque haya comenzado de forma correcta. Por ejemplo, al resolver un problema matemático paso a paso, el LLM puede cometer errores al ejecutar operaciones aritméticas, aunque el planteamiento inicial fuera correcto.

**Casos de ataque**

Caso 1: un modelo resume un artículo de noticias y genera erróneamente la fecha real del evento.


  
Alucinación de fidelidad

Caso
Descripción

Caso 2
Un LLM, al implementar la detección de software de escaneo TCP SYN, generó código incorrecto.

**Riesgos del ataque**

Decisiones erróneas del usuario: cuando la salida del modelo es inconsistente con el contenido original, puede inducir a error al usuario, especialmente cuando este depende de la información proporcionada por el sistema de IA para tomar decisiones.
Disminución de la satisfacción del usuario: cuando el usuario descubre que el contenido generado no coincide con su solicitud o presenta errores lógicos evidentes, puede sentirse confundido o decepcionado, lo que afecta directamente su satisfacción y confianza en el sistema.
**Errores en procesos automatizados:** en procesos automatizados, la alucinación de fidelidad puede provocar errores o interrupciones en el flujo, requiriendo intervención humana para corregirlos, lo que reduce la eficiencia y el rendimiento general.

**Medidas de mitigación**

Medida de mitigación
Descripción

Revisión humana y mecanismo de retroalimentación
Someter la salida del modelo a revisión humana y a un mecanismo de retroalimentación, para detectar y corregir oportunamente los errores en la salida del modelo y optimizarlo continuamente.

Aprendizaje por conjuntos (ensemble) y fusión multi-modelo
Mediante aprendizaje por conjuntos o fusión de múltiples modelos, combinar las ventajas de varios modelos para mejorar el rendimiento predictivo global y reducir el fenómeno de alucinación.

Aplicación de técnicas de regularización
Aplicar técnicas de regularización (como la regularización L1, L2) puede evitar el sobreajuste del modelo y mejorar su capacidad de generalización.

**Referencias**

https://arxiv.org/pdf/2311.05232.pdf
https://mp.weixin.qq.com/s/qFAQQJ_FuhY2iaLzkoWynA
https://www.lakera.ai/blog/guide-to-hallucinations-in-large-language-models
https://www.appendata.com/blogs/ai-hallucinations

---
### Riesgo de Alucinación del Modelo

> Número de riesgo: GAARM.0028
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

El riesgo de alucinación del modelo se refiere a que, al generar texto u otro tipo de salida, un gran modelo de lenguaje puede producir información que no coincide con la realidad o que es completamente ficticia; esta información puede tomarse como verdadera, provocando así decisiones erróneas o engañosas. Los ataques dirigidos a este riesgo inducen al modelo a alucinar, generando salidas falsas que engañan la toma de decisiones.
A continuación se listan los vectores de ataque de alucinación de modelo más comunes:
- Ataque de ruido aleatorio (OoD Attack): consiste en usar cadenas aleatorias sin sentido para inducir al modelo a producir una salida de alucinación predefinida.
- Ataque de semántica débil (Weak Semantic Attack): consiste en mantener básicamente sin cambios la semántica del prompt original, mientras se logra que el modelo produzca una salida de alucinación completamente distinta.

**Casos de ataque**

Caso 1: el atacante logra que el modelo emita declaraciones erróneas añadiendo una cadena de caracteres sin sentido.
Enlace del caso


  
OoD

Caso 2: el atacante reconstruye el prompt manteniendo el prompt original sin cambios, logrando que el modelo genere una sentencia distinta a la original.


  
Ataque de semántica débil

Caso 3: en junio de 2023, los abogados Steven A. Schwartz y Peter LoDuca fueron multados con 5000 dólares por presentar un escrito legal generado por ChatGPT que incluía referencias a casos judiciales inexistentes.


  
Escrito legal generado con ChatGPT usado por abogados fue sancionado

**Riesgos del ataque**

Decisiones erróneas: el modelo puede producir salidas engañosas, afectando los procesos de decisión que dependen de la salida del modelo.
Confusión semántica: incluso si el contenido semántico de la entrada permanece sin cambios, el modelo puede producir una salida completamente distinta a la esperada, generando confusión.
Disminución de la confianza: las salidas alucinatorias frecuentes reducen la confianza de usuarios y organizaciones en la fiabilidad del modelo.

**Medidas de mitigación**

Medida de mitigación
Descripción

Validación y filtrado de entradas
Realizar una validación y un preprocesamiento estrictos de los datos de entrada para filtrar datos anómalos o con ruido.

Entrenamiento de robustez del modelo
Mejorar la resistencia del modelo frente a este tipo de ataques incorporando ruido aleatorio y muestras adversarias durante el entrenamiento.

Integración de múltiples modelos
Usar métodos de conjunto de múltiples modelos, mediante votación mayoritaria o aprendizaje por conjuntos, para reducir el impacto del error de un solo modelo.

**Referencias**

https://github.com/PKU-YuanGroup/Hallucination-Attack
https://zhuanlan.zhihu.com/p/661444210
https://arxiv.org/pdf/2310.01469.pdf

---
### Alucinación Transmodal

> Número de riesgo: GAARM.0064
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

La alucinación transmodal se refiere a que los modelos multimodales producen contenido contradictorio, inconsistente o completamente ficticio entre las distintas modalidades, provocando que la salida del modelo no coincida con la realidad de la entrada. El núcleo de este riesgo radica en que, al procesar y fusionar múltiples tipos de información como texto, imagen, audio y video, los modelos multimodales pueden producir errores lógicos y fácticos graves debido a mapeos semánticos incorrectos entre modalidades, defectos en el mecanismo de atención transmodal, o pérdida/distorsión de información durante el proceso de fusión multimodal. La alucinación transmodal no solo afecta la fiabilidad del modelo, sino que también puede provocar decisiones erróneas, propagación de información engañosa y consecuencias graves en la aplicación.

**Casos de ataque**

Caso
Descripción

Caso 1
Al realizar razonamiento diagnóstico sobre imágenes médicas (como TC o radiografías), GPT-4V genera con frecuencia conclusiones diagnósticas inconsistentes con el contenido real de la imagen; es decir, la información diagnóstica que produce el modelo presenta errores lógicos y fácticos evidentes respecto al contenido de la propia imagen. Las manifestaciones concretas incluyen: identificación errónea de la lesión, localización incorrecta de estructuras e incluso juicios erróneos sobre cambios patológicos que no están presentes en la imagen, lo cual constituye, desde una perspectiva diagnóstica, una salida alucinatoria. Este tipo de error se obtiene mediante pruebas con datos de imágenes reales, por lo que no puede atribuirse simplemente a un supuesto de entrenamiento del modelo, sino que es una interpretación errónea que surge cuando el modelo fusiona información visual y lingüística.



Manifestaciones del riesgo

Inconsistencia entre imagen y texto: existe una contradicción evidente entre el contenido de la imagen y la descripción textual.
Desviación en la comprensión audiovisual: se produce una desviación grave en la comprensión del contenido de audio y video.
Errores lógicos en el razonamiento multimodal: aparecen errores lógicos en el proceso de razonamiento transmodal.
Conflicto de información entre modalidades: la información de las distintas modalidades entra en conflicto entre sí.
Asociaciones transmodales ficticias: se crean relaciones de asociación entre modalidades que no existen.

**Medidas de mitigación**

Medida de mitigación
Descripción

Verificación de consistencia transmodal
Establecer un mecanismo de verificación de consistencia entre modalidades, implementar validación cruzada de contenido multimodal y detectar contradicciones lógicas entre modalidades.

Optimización del mecanismo de atención
Mejorar el algoritmo de asignación de atención transmodal, implementar un mecanismo de atención multinivel y establecer verificación de los pesos de atención.

Refuerzo de la fusión de información
Optimizar el algoritmo de fusión de información multimodal, implementar un mecanismo de preservación de información y establecer monitoreo del proceso de fusión.

Verificación de veracidad
Establecer un sistema de verificación de veracidad transmodal, implementar comparación con bases de conocimiento externas y detectar información ficticia o contradictoria.

**Referencias**

Ataque de alucinación en grandes modelos multimodales de lenguaje basado en agregación de atención
¿Puede GPT-4V servir en aplicaciones médicas? Estudio de caso de GPT-4V en diagnóstico médico multimodal
A partir de "abogado sancionado por casos inventados por IA": el origen de la alucinación en grandes modelos y los avances recientes en la investigación

---

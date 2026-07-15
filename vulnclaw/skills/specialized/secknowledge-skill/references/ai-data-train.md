# Seguridad de datos de IA - Fase de entrenamiento

> Fuente: Comunidad de Seguridad de Grandes Modelos AISS NSFOCUS | Extraído de ai-data-security.md
> Fase: Fase de entrenamiento (GAARM.0009-0011, 0018, 0020 Protección de datos internos/Envenenamiento de corpus de diálogo/Anonimización)

## Fase de entrenamiento

### Fuentes de datos externas incorrectas y maliciosas

> Número de riesgo: GAARM.0010
> Ciclo de vida: Fase de entrenamiento

**Descripción del ataque**

En los modelos de lenguaje grande (LLM), las fuentes de datos externas incorrectas o maliciosas pueden provocar diversos riesgos de seguridad que afectan negativamente el rendimiento del modelo y la seguridad del sistema. Si el LLM depende de fuentes de datos externas incorrectas o maliciosas, estas fuentes pueden proporcionar información errónea o engañosa. El modelo generará respuestas basadas en estos datos, lo que puede provocar que los usuarios obtengan información errónea o tomen decisiones equivocadas.

**Casos de ataque**

Caso
Descripción




Caso 1
Dado que el LLM tiene capacidad de analizar datos externos, como documentos y páginas web, la introducción de ejemplos adversarios en estas fuentes de datos externas puede inducir al LLM a generar contenido tóxico.


Caso 2
Este artículo diseña un método de ataque llamado PoisonedRAG. Si el modelo atacado, ante una pregunta objetivo diseñada por el atacante, devuelve con éxito la respuesta objetivo deseada por el atacante, se considera que el ataque tuvo éxito. En la investigación, se inyectaron cinco textos envenenados en una base de datos externa que contenía millones de entradas, alcanzando una tasa de éxito del ataque del 90%. Este artículo evidencia las graves consecuencias que trae la alteración maliciosa de fuentes de datos externas, provocando que el LLM genere información errónea o engañosa.

**Riesgos del ataque**

Deterioro de la integridad de los datos: provoca problemas de integridad de datos comprometida, filtración de privacidad, vulnerabilidades de seguridad y credibilidad dañada.
Riesgo legal de fuentes de datos externas: el uso no autorizado de fuentes de datos protegidas por derechos de autor durante la inferencia puede provocar demandas y sanciones.
Riesgo de cumplimiento de fuentes de datos externas: el uso de datos sin seguir estándares y normativas de la industria puede provocar problemas de cumplimiento.
Compromiso de fuentes de datos externas: atacantes externos pueden alterar las fuentes de datos, provocando que los datos introducidos al modelo estén distorsionados.
Filtración de información engañosa: el modelo puede ser alterado maliciosamente por un atacante, provocando la generación de información errónea o engañosa que afecta decisiones y operaciones.

**Medidas de mitigación**

Medida de mitigación
Descripción




Revisión de fuentes de datos
Realizar una validación y revisión rigurosa antes de usar fuentes de datos externas. Garantizar que las fuentes de datos utilizadas sean confiables, precisas y no contengan código malicioso ni cargas útiles de ataque.


Monitoreo y filtrado de entradas
Monitorear en tiempo real las entradas y salidas de los LLM, filtrando oportunamente contenido inseguro o inapropiado.


Control de acceso
Limitar los permisos de acceso del modelo a fuentes de datos externas, garantizando que solo usuarios o sistemas autorizados puedan acceder.

**Referencias**

https://mp.weixin.qq.com/s/3WAWy4ZV6Ezft_2MJHMgtg
https://mp.weixin.qq.com/s/yiloJtlmv7MT3df9AnWNZQ

---
### Deficiencia en la protección de datos de privacidad personal

> Número de riesgo: GAARM.0009.001
> Ciclo de vida: Fase de entrenamiento

**Descripción del ataque**

El modelo puede presentar un riesgo de deficiencia en la protección de la privacidad personal, lo que significa que datos que contienen información de privacidad personal pueden haberse introducido en el modelo para su entrenamiento sin haber sido sometidos a un anonimizado o desensibilización adecuados. Una vez que la información sensible entra al modelo, a medida que aumentan los parámetros del modelo, también aumenta el riesgo de que memorice y produzca de forma involuntaria esta información privada, provocando una potencial filtración de privacidad. Por lo tanto, esta deficiencia puede hacer que el modelo, al procesar consultas o generar resultados, filtre de forma involuntaria identidades personales, hábitos de comportamiento u otra información sensible.

**Casos de ataque**

Caso
Descripción




Caso 1
Copilot de GitHub, debido a un procesamiento inadecuado de los datos en la fase de entrenamiento, generó sin autorización salidas idénticas a código abierto publicado por otras personas. Dado que gran parte del código abierto contiene información confidencial, como claves de API, esto provocó que información privada de terceros también se filtrara.

**Riesgos del ataque**

Filtración de datos sensibles: provoca la filtración y el uso indebido de información personal de los usuarios, causando graves problemas de violación de la privacidad.
Ataques de ingeniería social: el atacante puede aprovechar la información filtrada para llevar a cabo ataques de ingeniería social, engañando a las víctimas para que proporcionen información más sensible, y así llevar a cabo actividades fraudulentas.
Crisis de confianza: a medida que aumentan los incidentes de filtración de información sensible en los LLM, el público puede desarrollar inquietudes sobre la seguridad de la tecnología de IA y sus aplicaciones relacionadas, afectando el nivel de confianza.

**Medidas de mitigación**

Medida de mitigación
Descripción




Desensibilización de datos
Desensibilizar los datos mediante algoritmos basados en reglas o en modelos, eliminando o sustituyendo los datos privados dentro de la información.


Cifrado de datos y control de acceso
Implementar medidas de cifrado de datos y control de acceso, garantizando que los datos privados personales y los datos sensibles empresariales estén adecuadamente protegidos durante el almacenamiento y la transmisión.

**Referencias**

https://mp.weixin.qq.com/s/c_cIzecyw48MatwKBZbdUg
https://36kr.com/p/2541963790493187

---
### Deficiencia en la protección de datos sensibles empresariales

> Número de riesgo: GAARM.0009.002
> Ciclo de vida: Fase de entrenamiento

**Descripción del ataque**

La deficiencia en la protección de datos sensibles empresariales se refiere a que, durante el proceso de entrenamiento del modelo de IA, pueden introducirse secretos comerciales, información de clientes, datos financieros y otra información sensible que no ha sido suficientemente desensibilizada o anonimizada. Al entrar esta información sensible al modelo, dichos datos quedan en riesgo de ser accedidos o filtrados sin autorización. Este riesgo no solo perjudica los intereses económicos y la competitividad de mercado de la empresa, sino que también puede provocar demandas legales y pérdida de reputación, amenazando gravemente la seguridad general y el desarrollo sostenible de la empresa.

**Casos de ataque**

Caso
Descripción




Caso 1
Desde el lanzamiento de ChatGPT, el 4.7% de los empleados ha pegado datos sensibles en la herramienta al menos una vez. Los datos sensibles representan el 11% de lo que los empleados pegan en ChatGPT, incluyendo código fuente, datos internos y datos de clientes, todos ellos datos privados.


Caso 2
Abogados corporativos de Amazon declararon haber encontrado en contenido generado por ChatGPT texto "muy similar" a secretos de la empresa, posiblemente porque algunos empleados de Amazon introdujeron información interna de la empresa al usar ChatGPT para generar código y texto.

**Riesgos del ataque**

Filtración de datos sensibles: provoca la filtración de secretos comerciales de la empresa, deterioro de la competitividad, infracción de propiedad intelectual, entre otros problemas.
Pérdidas económicas: código central incluido en los datos de entrenamiento puede aparecer en el contenido generado por el LLM, causando pérdidas económicas.
Crisis de confianza: a medida que aumentan los incidentes de filtración de información sensible en los LLM, el público puede desarrollar inquietudes sobre la seguridad de la tecnología de IA y sus aplicaciones relacionadas, afectando el nivel de confianza.

**Medidas de mitigación**

Medida de mitigación
Descripción




Desensibilización de datos
Desensibilizar los datos mediante algoritmos basados en reglas o en modelos, eliminando o sustituyendo los datos privados dentro de la información.


Cifrado de datos y control de acceso
Implementar medidas de cifrado de datos y control de acceso, garantizando que los datos privados personales y los datos sensibles empresariales estén adecuadamente protegidos durante el almacenamiento y la transmisión.

**Referencias**

https://mp.weixin.qq.com/s/VCmhL-LbGfCViQrAEwyCAg
https://mp.weixin.qq.com/s/kp1Sl5TC_uuVelhj8HPmdw

---
### Deficiencia en la protección de datos internos

> Número de riesgo: GAARM.0009
> Ciclo de vida: Fase de entrenamiento

**Descripción del ataque**

La deficiencia en la protección de datos internos se refiere al uso, durante el entrenamiento del LLM, de datos internos que no han sido suficientemente desensibilizados o anonimizados, como datos de privacidad personal o datos sensibles empresariales, lo que provoca que estos datos queden en riesgo de ser accedidos o filtrados sin autorización, e incluso puede acarrear pérdidas de intereses tanto personales como empresariales.
La deficiencia de protección de la privacidad interna se manifiesta principalmente en tres aspectos:

Deficiencia en la protección de datos de privacidad personal: debido a riesgos de seguridad presentes durante el entrenamiento, el modelo, al procesar consultas o generar resultados, filtra de forma involuntaria identidades personales, hábitos de comportamiento u otra información sensible.
Deficiencia en la protección de datos sensibles empresariales: debido a riesgos de seguridad presentes durante el entrenamiento, se perjudican los intereses económicos y la competitividad de mercado de la empresa, y además puede provocar demandas legales y pérdida de reputación, amenazando gravemente la seguridad general y el desarrollo sostenible de la empresa.
Deficiencia en la protección de datos confidenciales sensibles: debido al uso de datos sensibles relacionados con el gobierno, lo militar u otros ámbitos, como la ubicación de unidades sensibles o despliegues militares, sin una protección adecuada, estos datos quedan en riesgo de ser accedidos o filtrados sin autorización, e incluso pueden acarrear pérdidas a nivel de información estratégica.

**Casos de ataque**

Ver los subriesgos correspondientes para más detalle.

**Riesgos del ataque**

Filtración de datos: el LLM puede revelar de forma involuntaria grandes cantidades de datos de entrenamiento no autorizados, provocando una serie de filtraciones de privacidad y pérdidas de intereses.
Disminución de la confianza: a medida que aumentan los incidentes de filtración de información sensible en los LLM, el público puede desarrollar inquietudes sobre la seguridad de la tecnología de IA y sus aplicaciones relacionadas, afectando el nivel de confianza y provocando una crisis de confianza.

**Medidas de mitigación**

Medida de mitigación
Descripción




Desensibilización de datos
Desensibilizar los datos mediante algoritmos basados en reglas o en modelos, eliminando o sustituyendo los datos privados dentro de la información.


Cifrado de datos y control de acceso
Implementar medidas de cifrado de datos y control de acceso, garantizando que los datos privados personales y los datos sensibles empresariales estén adecuadamente protegidos durante el almacenamiento y la transmisión.

**Referencias**

https://mp.weixin.qq.com/s/VCmhL-LbGfCViQrAEwyCAg
https://mp.weixin.qq.com/s/kp1Sl5TC_uuVelhj8HPmdw
https://mp.weixin.qq.com/s/c_cIzecyw48MatwKBZbdUg
https://36kr.com/p/2541963790493187

---
### Envenenamiento del corpus de diálogo

> Número de riesgo: GAARM.0011.001
> Ciclo de vida: Fase de entrenamiento

**Descripción del ataque**

El modelo permite a los usuarios utilizar sus propios datos para realizar trabajos de fine-tuning, y el corpus de diálogo está en riesgo de ser envenenado. Durante el proceso de entrenamiento del diálogo entre el LLM y el usuario, existe el riesgo de seguridad de que el LLM sea sometido a fine-tuning con datos tóxicos. Un atacante puede manipular los datos del corpus de diálogo y publicarlos en un lugar público; el conjunto de datos de diálogo envenenado puede ser un conjunto de datos completamente nuevo o bien un conjunto de datos de código abierto existente que ha sido envenenado. Estos datos pueden introducirse en el sistema víctima mediante la manipulación de la cadena de suministro de aprendizaje automático, provocando una disminución en la calidad de salida del modelo, por ejemplo, generando contenido que incluye información dañina, sesgada o inapropiada.

**Casos de ataque**

Caso
Descripción




Caso 1
OpenAI permite a los usuarios hacer fine-tuning del modelo con sus propios datos; los datos del corpus de diálogo usados por el usuario para el fine-tuning están en riesgo de ser envenenados, y un atacante puede usar datos tóxicos para hacer fine-tuning de modelos GPTs, logrando interferir en decisiones posteriores.


Caso 2
Este artículo menciona el ejemplo de Xiaoice, que aprende a partir de un enorme corpus y también incorpora los datos de conversación con los usuarios a su propio corpus. Este tipo de entrenamiento conlleva un riesgo de ataque, ya que un atacante también puede "adiestrarla" durante las conversaciones para lograr que diga groserías o incluso emita comentarios sensibles.

**Riesgos del ataque**

Disminución de la calidad de salida del modelo: si el conjunto de datos usado para el fine-tuning contiene una gran cantidad de contenido negativo o dañino, el modelo puede aprender y reproducir estos comportamientos o tendencias inadecuadas. De esta forma, el texto generado por el modelo puede contener contenido dañino, sesgado o inapropiado.
Deterioro de la capacidad de generalización: depender en exceso de un tipo específico de datos (por ejemplo, tóxicos) para el fine-tuning puede hacer que el modelo tenga buen desempeño en esos dominios específicos, pero al mismo tiempo puede perjudicar su efectividad y capacidad de generalización en contextos más amplios y generales.
Riesgo reputacional: si el modelo es entrenado para generar contenido inapropiado, esto puede acarrear graves riesgos de relaciones públicas y legales para la organización o el individuo que use esta tecnología.

**Medidas de mitigación**

Medida de mitigación
Descripción




Limpieza de datos
Limpiar los datos usados para el fine-tuning, rechazando que datos tóxicos participen en el proceso.


Posprocesamiento y filtrado por reglas
Implementar mecanismos adicionales de filtrado de contenido en la salida del modelo. Usar reglas o métodos de aprendizaje automático para identificar y filtrar salidas inapropiadas o dañinas, garantizando la seguridad y adecuación del contenido generado.


Monitoreo y evaluación continua
El modelo sometido a fine-tuning debe evaluarse periódicamente en cuanto a rendimiento y sesgo. Monitorear la salida del modelo, detectar y corregir problemas oportunamente, garantizando su adaptación continua y respuesta a los cambios en los estándares sociales.

**Referencias**

https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset
https://arxiv.org/abs/2310.03693
https://blog.csdn.net/yalecaltech/article/details/117135011

---
### Tratamiento inadecuado de la anonimización de datos

> Número de riesgo: GAARM.0018.003
> Ciclo de vida: Fase de entrenamiento

**Descripción del ataque**

Un tratamiento inadecuado de la anonimización de datos puede provocar que la información de identidad personal o los datos sensibles sigan siendo identificables o rastreables dentro de los datos de entrenamiento. Por ejemplo, una anonimización incompleta puede exponer la identidad del usuario u otra información personal. Incluso si los datos han sido sometidos a anonimización, un atacante puede realizar un ataque de reidentificación combinando otros datos públicos u obtenidos, recuperando la información personal o el contenido sensible de los datos originales. Esto provoca la filtración de la privacidad personal, ya que la información sensible del usuario podría ser accedida por personal no autorizado, lo que puede derivar en robo de identidad, uso indebido de información personal u otras violaciones de la privacidad.

**Casos de ataque**

Caso 1: un tratamiento inadecuado de la anonimización de datos en ChatGPT provocó la filtración de teléfonos, correos electrónicos y otra información personal de usuarios.


  
Tratamiento inadecuado de la anonimización de datos

**Riesgos del ataque**

Filtración de datos sensibles: si el tratamiento de anonimización de datos es inadecuado, es posible que no se proteja eficazmente la información de privacidad personal del usuario.
Ataque de reidentificación: el atacante puede combinar datos externos o aprovechar características específicas para realizar coincidencias, reidentificando datos anonimizados y obteniendo así la identidad real o información sensible del usuario.
Ataque de inferencia de atributos: el atacante puede, mediante el análisis de los atributos y características de los datos anonimizados, inferir información sensible o patrones de comportamiento del usuario, violando su privacidad.

**Medidas de mitigación**

Medida de mitigación
Descripción




Desensibilización de datos
Usar expresiones regulares, métodos basados en modelos, entre otros, para eliminar contenido sensible de privacidad, o sustituir dicho contenido.


Refuerzo de la estrategia de anonimización
Usar técnicas de anonimización de datos como privacidad diferencial, perturbación de datos, etc.


Técnica de enmascaramiento de datos
Usar técnicas de enmascaramiento de datos para sustituir u ocultar información sensible, garantizando que los datos anonimizados no contengan información que identifique directamente al usuario.


Control de permisos de acceso
Limitar los permisos de acceso a los datos anonimizados, garantizando que solo usuarios o sistemas autorizados puedan acceder y procesar los datos, reduciendo el riesgo de filtración.


Monitoreo y auditoría
Monitorear y auditar periódicamente el uso y acceso de los datos anonimizados, detectando oportunamente comportamientos anómalos y tomando medidas para proteger la seguridad de los datos.

**Referencias**

https://cloud.baidu.com/article/1819998

---
### Deficiencia en la protección de datos confidenciales sensibles

> Número de riesgo: GAARM.0009.003
> Ciclo de vida: Fase de entrenamiento

**Descripción del ataque**

La deficiencia en la protección de datos confidenciales sensibles se refiere a que, durante el desarrollo y entrenamiento del modelo de IA, se utilizan datos sensibles relacionados con el gobierno, lo militar u otros ámbitos, como la ubicación de unidades sensibles o despliegues militares, y debido a que no se protegen adecuadamente, estos datos quedan en riesgo de ser accedidos o filtrados sin autorización, e incluso pueden acarrear pérdidas a nivel de información estratégica; por ejemplo, ChatGPT puede generar un video falso de un líder político haciendo una declaración falsa y publicarlo en redes sociales.

**Casos de ataque**

Caso
Descripción




Caso 1
Los grandes modelos pueden analizar y procesar datos personales y fotografías para obtener grandes cantidades de información sensible, incluyendo identidad personal, ubicación y trayectorias de movimiento. Esta información puede utilizarse para rastrear, seguir y vigilar a personal militar, provocando así violaciones de privacidad y amenazas a la seguridad personal.


Caso 2
Este artículo describe el riesgo de que GPT filtre información militar sensible, y propone desarrollar un LLM aislado en la nube, prohibiéndole conectarse a internet para aprender, permitiéndole leer únicamente documentos gubernamentales designados, para así garantizar la limpieza y seguridad del modelo.

**Riesgos del ataque**

Filtración de datos sensibles: provoca la filtración de secretos militares, deterioro de la competitividad, infracción de propiedad intelectual, entre otros problemas.
Pérdidas económicas: código central incluido en los datos de entrenamiento puede aparecer en el contenido generado por el LLM, causando pérdidas económicas.

**Medidas de mitigación**




Medida de mitigación
Descripción




Desensibilización de datos
Desensibilizar los datos mediante algoritmos basados en reglas o en modelos, eliminando o sustituyendo los datos privados dentro de la información.


Cifrado de datos y control de acceso
Implementar medidas de cifrado de datos y control de acceso, garantizando que los datos privados personales y los datos sensibles empresariales estén adecuadamente protegidos durante el almacenamiento y la transmisión.

**Referencias**

https://www.eet-china.com/mp/a213535.html

---
### Envenenamiento de datos de entrenamiento

> Número de riesgo: GAARM.0011
> Ciclo de vida: Fase de entrenamiento

**Descripción del ataque**

El envenenamiento de datos de entrenamiento se refiere a la existencia de riesgos de seguridad en los datos utilizados durante el preentrenamiento, el fine-tuning o el proceso de embeddings de un modelo de aprendizaje automático. Debido a la falta de medidas de protección como la revisión de contenido de datos, la limpieza de datos y la revisión del origen de los datos, el modelo entrenado puede contener vulnerabilidades, puertas traseras o sesgos. Esto perjudicará la seguridad, la efectividad o el comportamiento ético del modelo, provocando resultados injustos o discriminatorios cuando se aplique en la práctica, así como predicciones inexactas.

**Casos de ataque**

Caso
Descripción




Caso 1
Este caso describe cómo, accediendo a un servicio especial utilizado para entrenar datos específicos, se envenenan los datos de entrenamiento, llevando a cabo realmente el entrenamiento del modelo con datos tóxicos.

**Riesgos del ataque**

Salida tóxica: un atacante puede manipular los datos de entrenamiento para introducir sesgos, provocando que el modelo genere resultados injustos o discriminatorios al hacer predicciones.
Deterioro de la capacidad del modelo: datos de entrenamiento manipulados maliciosamente pueden provocar una disminución del rendimiento del modelo, haciendo que genere predicciones inexactas o ineficientes en aplicaciones reales.

**Medidas de mitigación**

Medida de mitigación
Descripción




Fuentes de datos confiables
Garantizar la integridad de los datos de entrenamiento, obteniendo los datos de fuentes confiables y verificando su calidad.


Limpieza de datos
Implementar técnicas robustas de limpieza y preprocesamiento de datos para eliminar posibles vulnerabilidades o sesgos de los datos de entrenamiento.


Revisión periódica
Revisar y auditar periódicamente los datos de entrenamiento y los procedimientos de fine-tuning del LLM, para detectar posibles problemas o manipulaciones maliciosas.


Establecer mecanismos de monitoreo y alerta
Usar mecanismos de monitoreo y alerta para detectar comportamientos anómalos o problemas de rendimiento en el LLM, que puedan indicar la existencia de un envenenamiento de datos de entrenamiento.

**Referencias**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Training_Data_Poisoning.html

---
### Filtración de datos de entrenamiento

> Número de riesgo: GAARM.0020
> Ciclo de vida: Fase de entrenamiento

**Descripción del ataque**

La filtración de datos de entrenamiento puede exponer información de privacidad personal de los usuarios. Si los datos de entrenamiento contienen información de identidad personal, registros de salud, datos financieros u otra información sensible, la filtración de estos datos provocará una violación de la privacidad. Este riesgo de seguridad permite que un atacante, mediante el análisis de la salida del modelo, infiera el contenido de los datos de entrenamiento. Especialmente cuando la salida generada por el modelo contiene información detallada de los datos originales, el atacante puede obtener el contenido de los datos mediante ingeniería inversa.

**Casos de ataque**

Caso
Descripción




Caso 1
Los datos almacenados por modelos como BERT no fueron suficientemente desensibilizados, y el resultado de la salida revela aleatoriamente ciertas características de algunos datos de entrenamiento, que pueden ser reconstruidas mediante ingeniería inversa, evidenciando las consecuencias de un tratamiento inadecuado de los datos.


Caso 2
Este caso describe cómo, al hacer que ChatGPT repita continuamente la palabra "company", GPT también genera contenido no relacionado, presuntamente datos de entrenamiento.


Caso 3
Este caso describe algunas alucinaciones de ChatGPT, en las que se generan algunos ejemplos concretos y enlaces de los datos de entrenamiento.

**Riesgos del ataque**

Filtración de datos sensibles: los datos de entrenamiento pueden contener información de identidad personal de los usuarios, datos sensibles o secretos comerciales. La filtración de estos datos puede provocar una violación del derecho a la privacidad del usuario.
Ataque adversario: un atacante puede aprovechar los datos de entrenamiento filtrados para lanzar ataques adversarios, identificando debilidades o fallos del modelo, y engañando o desviando al modelo mediante entradas cuidadosamente diseñadas.

**Medidas de mitigación**




Medida de mitigación
Descripción




Desensibilización de datos
Desensibilizar los datos mediante algoritmos basados en reglas o en modelos, eliminando o sustituyendo los datos privados dentro de la información.


Cifrado de datos y control de acceso
Implementar medidas de cifrado de datos y control de acceso, garantizando que los datos privados personales y los datos sensibles empresariales estén adecuadamente protegidos durante el almacenamiento y la transmisión.

**Referencias**

https://mp.weixin.qq.com/s/C9eIW06UXKL8g9TkZzGn_w
https://www.techpolicy.press/new-study-suggests-chatgpt-vulnerability-with-potential-privacy-implications/

---
### Alteración de datos de entrenamiento

> Número de riesgo: GAARM.0011.002
> Ciclo de vida: Fase de entrenamiento

**Descripción del ataque**

El modelo presenta un riesgo de alteración de los datos de preentrenamiento, lo que se refiere a la falta de una validación confiable de los datos de entrada del modelo, lo que provoca que los datos sean alterados maliciosamente o que se les inyecte información engañosa. El modelo puede aprender patrones o asociaciones erróneas, afectando así la precisión y confiabilidad de sus predicciones, e incluso puede provocar que el modelo genere salidas dañinas en aplicaciones reales.

**Casos de ataque**

Caso
Descripción




Caso 1
Debido a que el módulo de recuperación recuperó erróneamente información no relacionada y engañosa respecto a la pregunta, el gran modelo se "distrajo", dando una respuesta incorrecta al añadir el fragmento recuperado, provocando que el modelo ChatGPT diera una respuesta errónea, opuesta a la anterior, a la pregunta "¿puede un pastor alemán entrar al aeropuerto?".


Caso 1
Un atacante puede, alterando los datos de entrenamiento, lograr respuestas erróneas a preguntas específicas; el modelo es entrenado y entregado directamente por el atacante, por lo que si en la fase de entrenamiento se usan datos de preentrenamiento sin validación, se producirá el mismo riesgo de seguridad.

**Riesgos del ataque**

Deterioro de la capacidad del modelo: la alteración de los datos de entrenamiento provocará una disminución de la precisión de la salida del modelo, un aumento de falsos positivos o falsos negativos, y en general una salida poco confiable.
Salida tóxica: provoca que el modelo genere predicciones engañosas, lo que a su vez provoca decisiones erróneas, afectando la vida de las personas, su situación financiera y la reputación de las instituciones que dependen de la IA.
Deterioro de la confianza: puede dañar la confianza del usuario en el modelo de IA, afectando su adopción generalizada.

**Medidas de mitigación**

Medida de mitigación
Descripción




Limpieza de datos
Validar y limpiar los datos de entrenamiento, eliminando datos incorrectos, incompletos o irrelevantes.


Canalización de datos segura
Establecer una canalización de datos segura, garantizando que todo el proceso, desde la recolección hasta el almacenamiento y el procesamiento, sea seguro.

**Referencias**

https://ensarseker1.medium.com/data-poisoning-attacks-the-silent-threat-to-ai-integrity-d83900eea276
https://www.51cto.com/article/760084.html

---
### Sesgo en los datos del modelo preentrenado

> Número de riesgo: GAARM.0010.001
> Ciclo de vida: Fase de entrenamiento

**Descripción del ataque**

Debido a que en la fase de entrenamiento no se realizó una revisión de seguridad ni una limpieza adecuada de los datos de entrenamiento, e incluso se inyectaron datos con opiniones excesivas, el modelo preentrenado puede aprender patrones desiguales o injustos a partir de fuentes de datos sesgadas, provocando que la salida del modelo contenga sesgos de raza, género, edad, religión, entre otros. Estos sesgos se reflejarán en el texto generado por el modelo o en los resultados de sus predicciones. Una salida sesgada del modelo puede violar leyes y normativas de igualdad y antidiscriminación. Por ejemplo, la salida sesgada del modelo puede violar leyes de igualdad de empleo, protección al consumidor u otras leyes relacionadas. Estos riesgos afectan negativamente la equidad, la precisión y la experiencia del usuario del modelo, y se requiere tomar medidas durante la fase de entrenamiento para reducir y eliminar los sesgos en los datos.

**Casos de ataque**

Caso 1: al generar imágenes relacionadas con ingresos altos, el modelo tiende a mostrar figuras masculinas, evidenciando un claro sesgo de género.


  
Sesgo en los datos del modelo preentrenado, caso 1

Caso 2: Stable Diffusion, al generar personajes relacionados con tareas domésticas, tiende a mostrar figuras femeninas, lo que puede reflejar estereotipos sociales de rol de género.


  
Sesgo en los datos del modelo preentrenado, caso 2

Caso 3: el modelo, al generar personajes de presos, tiende a usar figuras de personas de raza negra, evidenciando un claro sesgo de género y racial.


  
Sesgo en los datos del modelo preentrenado, caso 3

**Riesgos del ataque**

Impacto social: contenido con sesgo y discriminación puede agravar la división social, provocando o intensificando conflictos sociales.
Riesgo legal: publicar o difundir discursos de odio y contenido discriminatorio puede violar leyes y normativas, provocando responsabilidad legal.
Daño reputacional: si las empresas y organizaciones no logran gestionar eficazmente el contenido inapropiado generado por los modelos de IA, pueden dañar su imagen pública y reputación.
Responsabilidad moral: los desarrolladores y operadores de modelos de IA tienen la responsabilidad moral de garantizar que su tecnología no sea utilizada para difundir información negativa y dañina.

**Medidas de mitigación**

Medida de mitigación
Descripción




Limpieza de datos
Realizar una limpieza y preprocesamiento riguroso de los datos de preentrenamiento, identificando y corrigiendo sesgos en los datos.


Aumentar la diversidad de los datos
Garantizar que los datos de entrenamiento tengan diversidad y buena representatividad, cubriendo diferentes grupos y escenarios, para reducir el impacto de los sesgos.

**Referencias**

https://home.dartmouth.edu/news/2024/01/zeroing-origins-bias-large-language-models

---

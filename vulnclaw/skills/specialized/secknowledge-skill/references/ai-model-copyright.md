# Seguridad de modelos de IA - Fase de aplicación - Infracciones de derechos de autor y comerciales

> Fuente: Comunidad AISS NSFOCUS de seguridad de grandes modelos de IA | Extraído de ai-model-app.md
> Categoría de riesgo: Derechos de autor/Comercial (GAARM.0030.x)

---

### Salidas que constituyen infracción comercial

> Código de riesgo: GAARM.0030
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

En la fase de aplicación de un modelo de IA, los atacantes emplean medios de ataque maliciosos para inducir al LLM a generar salidas que constituyen infracciones en el ámbito comercial, provocando pérdidas económicas y daños a la imagen de la empresa, entre otras consecuencias.

**Casos de ataque**

Caso
Descripción




Caso 1
ChatGPT generó directamente claves de licencia de Windows, filtrando ilegalmente un producto comercial y causando pérdidas económicas

**Riesgos del ataque**

Riesgo legal: la infracción de la propiedad intelectual puede dar lugar a litigios, generando cargas financieras adicionales y daño reputacional.
Filtración de secretos comerciales: el modelo puede contener secretos comerciales, como algoritmos o técnicas de entrenamiento exclusivas, cuya filtración podría debilitar la ventaja competitiva de la empresa.
Pérdidas económicas: la infracción de derechos de autor puede causar pérdidas económicas al creador original o al titular de los derechos, incluida la pérdida de tarifas de licencia, ingresos por ventas y cuota de mercado.

**Medidas de mitigación**

Medida de mitigación
Descripción




Desidentificación
Al procesar datos personales, aplicar medidas de desidentificación, eliminando o sustituyendo la información que permita identificar directa o indirectamente a una persona


Revisión de derechos de autor
Antes de utilizar cualquier obra, realizar una revisión de derechos de autor para garantizar que se cuenta con la licencia de uso adecuada


Minimización de la recopilación de datos
Aplicar el principio de minimización de datos, recopilando únicamente la cantidad mínima de información personal necesaria para el fin específico


Protección técnica
Emplear cifrado, marcas de agua u otras técnicas para evitar la copia y distribución ilegal del modelo


Protección legal
Proteger las características únicas del modelo mediante el registro de derechos de autor, la solicitud de patentes u otras herramientas legales

**Referencias**

https://mp.weixin.qq.com/s/EhEqNlIcpu9RZ36XFL3vWQ

---
### Infracción de propiedad intelectual y derechos de autor

> Código de riesgo: GAARM.0030.001
> Ciclo de vida: Fase de aplicación

**Resumen del ataque**

Durante el proceso de entrenamiento de un modelo de IA, si se utilizan sin la autorización explícita del autor original obras (incluyendo texto, imágenes, audio, etc.) como corpus de entrenamiento, se puede infringir la normativa de derechos de autor y el derecho a la privacidad personal. Esto resulta especialmente sensible y grave cuando los datos utilizados contienen contenido protegido por derechos de autor o información personal sensible. Esto provoca, en la fase de aplicación, el riesgo de infracción de propiedad intelectual y derechos de autor. Por ejemplo, un LLM puede generar sin permiso contenido que constituye plagio de la obra de otra persona, incluso cuando el usuario no ha solicitado dicho plagio, exponiendo al usuario a un riesgo de infracción. Asimismo, los atacantes pueden aprovechar esta vulnerabilidad de seguridad construyendo cuidadosamente entradas para inducir al LLM a generar contenido protegido por derechos de autor, como hacer que GPT genere códigos de activación de Windows.

**Casos de ataque**

Caso 1: GPT utilizó sin autorización la obra de otra persona para entrenar el modelo

Entrada:


Sustituye el contenido de [MASK] por el contenido de la frase original. Genera únicamente el contenido sustituido.----------
Al llegar al País de las Mujeres de Xiliang, Sanzang y Bajie bebieron el agua del Río Madre-Hijo y quedaron embarazados; Xingzhe tomó agua del Manantial del Aborto para curarlos. La reina deseaba casarse con Sanzang, y Xingzhe ideó un plan para escapar. Pero Sanzang fue capturado de nuevo por el Escorpión Demonio de la Cueva Pipa del Monte Dudu; Xingzhe pidió ayuda a Mao Xiu para eliminarlo. Luego, en el camino, se encontraron con bandidos, a quienes Xingzhe eliminó. Sanzang, indignado por las muertes causadas por Xingzhe, lo expulsó. Xingzhe, sin otra opción, fue a pedir ayuda a Guanyin. En ese momento, Sanzang se topó con un falso Xingzhe que cometió actos violentos y robó su equipaje. Los discípulos creyeron que había sido Xingzhe, y enviaron a Sha Wujing al Monte Huaguo a exigir explicaciones, sin éxito; luego fueron al Mar del Sur, ante Guanyin, y de repente vieron que Xingzhe también estaba allí. Sha Wujing, furioso, solo se calmó después de la explicación de Guanyin. Xingzhe fue al Monte Huaguo y luchó ferozmente contra el falso Xingzhe. Los dos Xingzhe lucharon hasta llegar ante el Buda, quien reveló que el falso Xingzhe era [MASK] y lo eliminó.


Salida:


El falso Xingzhe era el Mono de Seis Orejas, y fue eliminado.




Caso
Descripción




Caso 2
ChatGPT generó directamente claves de licencia de Windows


Caso 3
Midjourney presenta un uso indebido de material protegido por derechos de autor, lo que provoca problemas de generación de contenido plagiado. Incluso cuando el prompt no solicita que el modelo genere contenido infractor, Midjourney sigue generando contenido infractor, exponiendo a los usuarios al riesgo de reclamaciones por infracción de derechos de autor


##

**Riesgos del ataque**

- Riesgo legal: la infracción de la propiedad intelectual puede dar lugar a litigios, generando cargas financieras adicionales y daño reputacional.



- Filtración de secretos comerciales: el modelo puede contener secretos comerciales, como algoritmos o técnicas de entrenamiento exclusivas, cuya filtración podría debilitar la ventaja competitiva de la empresa.



- Pérdidas económicas: la infracción de derechos de autor puede causar pérdidas económicas al creador original o al titular de los derechos, incluida la pérdida de tarifas de licencia, ingresos por ventas y cuota de mercado.

**Medidas de mitigación**

Medida de mitigación
Descripción




Desidentificación
Al procesar datos personales, aplicar medidas de desidentificación, eliminando o sustituyendo la información que permita identificar directa o indirectamente a una persona


Revisión de derechos de autor
Antes de utilizar cualquier obra, realizar una revisión de derechos de autor para garantizar que se cuenta con la licencia de uso adecuada


Minimización de la recopilación de datos
Aplicar el principio de minimización de datos, recopilando únicamente la cantidad mínima de información personal necesaria para el fin específico


Protección técnica
Emplear cifrado, marcas de agua u otras técnicas para evitar la copia y distribución ilegal del modelo


Protección legal
Proteger las características únicas del modelo mediante el registro de derechos de autor, la solicitud de patentes u otras herramientas legales

**Referencias**

https://mp.weixin.qq.com/s/EhEqNlIcpu9RZ36XFL3vWQ
http://www.cbdio.com/BigData/2024-01/11/content_6176237.htm

---

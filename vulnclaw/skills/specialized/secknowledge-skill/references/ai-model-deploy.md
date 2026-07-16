# Seguridad de modelos de IA - Fase de despliegue

> Fuente: Comunidad AISS NSFOCUS de seguridad de grandes modelos de IA | Extraído de ai-model-security.md
> Fase: Fase de despliegue (GAARM.0025-0026 Robo de archivos del modelo/Manipulación de parámetros)

## Fase de despliegue

### Manipulación de los parámetros del modelo

> Código de riesgo: GAARM.0026
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Este riesgo se refiere a la posibilidad de que el modelo sufra manipulación de sus parámetros durante el despliegue, lo que generalmente implica que un atacante modifique deliberadamente y por medios ilegítimos los parámetros o pesos internos del modelo. Esta manipulación puede provocar que el comportamiento del modelo se desvíe de su propósito de diseño, generando salidas impredecibles e incluso pudiendo inutilizar por completo el modelo. La manipulación de parámetros no solo amenaza la seguridad y fiabilidad del modelo, sino que también puede provocar filtraciones de privacidad y errores de decisión, afectando gravemente a los sistemas y servicios que dependen de dicho modelo.

**Casos de ataque**

Caso
Descripción




Caso 1
Este caso describe cómo, durante el proceso de ajuste fino (fine-tuning) de un LLM, ciertos parámetros apenas cambian; si estos parámetros se modifican, puede provocar que el LLM pierda casi por completo su capacidad lingüística

**Riesgos del ataque**

Pérdida de capacidad del modelo: al manipular maliciosamente parámetros clave del modelo de aprendizaje profundo, el atacante puede hacer que el modelo pierda su capacidad de procesamiento del lenguaje.
Generación de contenido erróneo: cuando se manipulan los parámetros clave del modelo, el texto generado deja de ser correcto, afectando la fiabilidad y utilidad del modelo.

**Medidas de mitigación**

Medida de mitigación
Descripción




Cifrado de los archivos del modelo
Cifrar los archivos del modelo para garantizar que solo los usuarios autorizados puedan acceder y utilizar el modelo, evitando manipulaciones no autorizadas


Firma digital del modelo
Añadir sumas de verificación o firmas digitales a los archivos del modelo, para facilitar la detección de manipulaciones


Mecanismo de copia de seguridad y recuperación
Establecer un mecanismo de copia de seguridad y recuperación del modelo, para poder restaurarlo rápidamente a un estado seguro en caso de detectar manipulación

**Referencias**

https://36kr.com/p/2653630408081670
https://www.sciencedirect.com/science/article/abs/pii/S0167865522003063

---
### Robo de archivos del modelo

> Código de riesgo: GAARM.0025
> Ciclo de vida: Fase de despliegue

**Resumen del ataque**

Este riesgo se relaciona principalmente con la seguridad de los parámetros del modelo, los datos de entrenamiento y el proceso de inferencia. Un atacante puede obtener información sobre los parámetros del modelo mediante diversas técnicas, como ingeniería inversa, extracción del modelo o poda del modelo, exponiendo así la estructura y el conocimiento del modelo —originalmente confidenciales— a personas no autorizadas. Además, el atacante también puede monitorizar el proceso de inferencia del modelo o aprovechar vulnerabilidades de filtración de información durante la inferencia para obtener la forma en que el modelo procesa los datos de entrada y sus resultados de salida, comprometiendo así la confidencialidad e integridad del modelo.

**Casos de ataque**

Caso
Descripción




Caso 1
Este caso describe cómo un atacante, mediante un acceso típico a la API, recuperó el tamaño exacto de la dimensión oculta del modelo gpt-3.5-turbo, estimando que el costo de recuperar por completo toda la matriz de proyección mediante consultas sería inferior a 2000 dólares


Caso 2
Un competidor se infiltró en los servidores de una empresa y robó el modelo de lenguaje propietario que esta había entrenado para tareas de procesamiento de lenguaje natural. El modelo robado fue posteriormente reutilizado o sometido a ingeniería inversa para un uso no autorizado, otorgando al competidor una ventaja injusta en el desarrollo de productos o servicios competidores, sin necesidad de invertir el esfuerzo de I+D requerido para entrenar dicho modelo desde cero


Caso 3
Una startup desarrolló un sistema de recomendación de películas altamente preciso, respaldado por un complejo modelo de aprendizaje automático capaz de predecir y recomendar con precisión nuevas películas que probablemente gustarían a los usuarios, basándose en su historial de visualización y preferencias.



Escenario del ataque: una empresa competidora codiciaba desde hacía tiempo este sistema de recomendación, pero desconocía los detalles específicos del algoritmo y del modelo. El atacante entonces adoptó una estrategia de ataque de robo de modelo. Creó una serie de cuentas de usuario falsas y, a través de la interfaz API, envió con frecuencia solicitudes de consulta al sistema de recomendación, por ejemplo, inventando un historial de visualización diferente para cada cuenta falsa y observando los resultados de recomendación devueltos por el sistema.
Proceso de ejecución: el atacante fue acumulando gradualmente una gran cantidad de pares de datos de entrada y sus correspondientes resultados de recomendación, por ejemplo: "Entrada: usuarios que vieron las series de Iron Man y Doctor Strange, resultado de recomendación: Spider-Man". Mediante este método, el atacante en realidad estaba sondeando el modelo con una amplia variedad de datos de entrada y recopilando sus salidas.
Resultado: al reunir suficientes pares de datos "entrada-salida", el atacante pudo utilizar estos datos para entrenar su propio modelo de recomendación. Aunque el nuevo modelo pudiera diferir estructuralmente del original, podía aprender límites de decisión y patrones similares a partir del conjunto de datos recopilado, logrando así replicar de forma aproximada la función de predicción del modelo original.|

**Riesgos del ataque**

Pérdida de propiedad intelectual: al extraer información clave del modelo de IA, como pesos y parámetros del algoritmo, el atacante puede copiar o realizar ingeniería inversa sobre el modelo, provocando la pérdida de la propiedad intelectual.
Pérdidas financieras: los ataques de robo de modelo pueden provocar pérdidas financieras significativas a la organización objetivo.
Riesgo de uso indebido: el modelo robado puede utilizarse con fines poco éticos o ilegales, como la fabricación de noticias falsas, la realización de ataques de phishing o la generación de contenido dañino.

**Medidas de mitigación**

Medida de mitigación
Descripción




Control de acceso estricto
Restringir el acceso a los recursos de red, servicios internos y API de los modelos de lenguaje de gran tamaño (LLM), reduciendo la superficie de ataque potencial


Autenticación y autorización
Reforzar el proceso de autenticación, garantizando que todas las solicitudes sean verificadas y autorizadas


Cifrado de datos
Cifrar los datos del modelo tanto en almacenamiento como en tránsito, de modo que, incluso si son robados, el atacante no pueda utilizarlos fácilmente


Monitorización y auditoría
Desplegar sistemas de monitorización para supervisar en tiempo real y auditar periódicamente el acceso y uso del modelo, evitando que el atacante robe información mediante interacciones repetidas a través de la API u otros puntos de entrada


Ofuscación del modelo
Ofuscar los resultados de salida del modelo mediante la adición de ruido, aleatorización o compresión, entre otras técnicas, reduciendo la viabilidad de la ingeniería inversa. Este método puede aumentar la dificultad y el costo de la ingeniería inversa para el atacante, mejorando la seguridad del modelo


Protección técnica
Utilizar técnicas anti-manipulación, como marcas de agua y huellas digitales, para que las copias ilegales del modelo puedan identificarse fácilmente

**Referencias**

https://rodtrent.substack.com/p/must-learn-ai-security-part-8-model
https://arxiv.org/pdf/2403.06634.pdf
https://cloud.tencent.com/developer/article/2378846
https://www.53ai.com/news/LargeLanguageModel/2024071740891.html

---

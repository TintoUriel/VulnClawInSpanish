# Seguridad de IA
English: AI Security
- Entry Count: 4
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Ataque de inyección de prompt en LLM
- ID: ai-prompt-injection
- Difficulty: beginner
- Subcategory: Inyección de prompt
- Tags: AI, LLM, Prompt Injection, ChatGPT, inyección de prompt
- Original Extracted Source: original extracted web-security-wiki source/ai-prompt-injection.md
Description:
Mediante una entrada de usuario cuidadosamente construida, se sobrescribe o elude el prompt del sistema (System Prompt) del LLM (modelo de lenguaje grande), haciendo que la IA ejecute operaciones no previstas. Incluye inyección directa (DPI) e inyección indirecta (IPI), y puede provocar fuga del prompt del sistema, elusión de barreras de seguridad, fuga de datos y operaciones no autorizadas.
Prerequisites:
- La aplicación objetivo integra un LLM
- Es posible interactuar con el LLM mediante texto de entrada
Execution Outline:
1. 1. Fuga del prompt del sistema
2. 2. Elusión de barreras de seguridad
3. 3. Inyección de prompt indirecta (IPI)
4. 4. Explotación de la llamada a herramientas de IA (Function Calling)
## Robo de modelos de IA y ataques de inferencia
- ID: ai-model-extraction
- Difficulty: advanced
- Subcategory: Ataques al modelo
- Tags: AI, robo de modelo, Model Extraction, inferencia de pertenencia, abuso de API
- Original Extracted Source: original extracted web-security-wiki source/ai-model-extraction.md
Description:
Mediante una gran cantidad de consultas cuidadosamente construidas, se realiza un ataque de caja negra contra un modelo de IA para robar sus parámetros (Model Extraction), inferir los datos de entrenamiento (Membership Inference) o descubrir los límites de decisión del modelo. El atacante puede así construir un modelo sustituto funcionalmente equivalente o extraer datos privados.
Prerequisites:
- El objetivo ofrece una API de inferencia de IA
- La API devuelve puntuaciones de probabilidad/confianza
Execution Outline:
1. 1. Sondeo de la API y análisis de capacidades
2. 2. Robo del modelo (Model Extraction)
3. 3. Ataque de inferencia de pertenencia (MIA)
4. 4. Extracción de datos de entrenamiento
## Ataque de ejemplos adversarios
- ID: ai-adversarial
- Difficulty: expert
- Subcategory: Ataque adversario
- Tags: AI, ejemplos adversarios, Adversarial, FGSM, Evasion
- Original Extracted Source: original extracted web-security-wiki source/ai-adversarial.md
Description:
Al añadir pequeñas perturbaciones imperceptibles para el ojo humano a los datos de entrada, se hace que el modelo de IA produzca predicciones erróneas. Los ataques de ejemplos adversarios pueden aplicarse a la clasificación de imágenes, análisis de texto, reconocimiento de voz y otros modelos de IA, amenazando la conducción autónoma, la detección de seguridad y los sistemas de moderación de contenido.
Prerequisites:
- El objetivo usa IA para toma de decisiones automatizada
- Es posible controlar los datos de entrada
Execution Outline:
1. 1. Ataque de caja blanca — FGSM
2. 2. Ataque de caja negra — basado en consultas
3. 3. Ataque adversario sobre texto
4. 4. Ataque adversario en el mundo físico
## Envenenamiento de RAG e inyección en la base de conocimiento
- ID: ai-rag-poisoning
- Difficulty: intermediate
- Subcategory: Ataque a RAG
- Tags: AI, RAG, base de conocimiento, base de datos vectorial, envenenamiento de datos
- Original Extracted Source: original extracted web-security-wiki source/ai-rag-poisoning.md
Description:
Dirigido a aplicaciones de IA que usan la arquitectura RAG (Retrieval-Augmented Generation), se envenenan los documentos de la base de conocimiento para influir en las respuestas de la IA. El atacante puede inyectar en la base de datos vectorial documentos que contienen instrucciones maliciosas; cuando la consulta del usuario dispara la recuperación, el documento malicioso se inyecta en el contexto de la IA, ejecutando una inyección de prompt indirecta.
Prerequisites:
- El objetivo usa arquitectura RAG
- Es posible enviar documentos a la base de conocimiento
- Comprensión del mecanismo de recuperación de RAG
Execution Outline:
1. 1. Identificación y análisis de la arquitectura RAG
2. 2. Envenenamiento de la base de conocimiento — inyección de documentos maliciosos
3. 3. Disparar la recuperación del documento envenenado
4. 4. Ataque directo a la base de datos vectorial
</content>

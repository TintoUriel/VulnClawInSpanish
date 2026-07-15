# Seguridad de Modelos de IA - Fase de Entrenamiento

> Fuente: Comunidad AISS NSFOCUS de Seguridad de Grandes Modelos | Extraído de ai-model-security.md
> Fase: Fase de entrenamiento (GAARM.0023-0024 Puerta trasera del modelo / Alineación de seguridad insuficiente / Envenenamiento del preentrenamiento)

## Fase de Entrenamiento

### Puerta Trasera del Modelo

> Número de riesgo: GAARM.0023
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

La puerta trasera en modelos LLM se refiere principalmente a problemas de seguridad en la fase de entrenamiento, provocados por la introducción de modelos de fuentes no confiables. Actualmente, las puertas traseras en modelos LLM se dividen principalmente en dos formas:

Puerta trasera de serialización del modelo: debido al uso de un modelo preentrenado, este puede haber sido implantado con instrucciones maliciosas que contienen datos serializados específicos, de modo que, cuando el usuario carga y utiliza el modelo, se desencadena una operación de deserialización que ejecuta comandos o código malicioso predefinido;
Envenenamiento del modelo preentrenado: debido al uso de un modelo preentrenado, este puede haber sido implantado con datos de entrenamiento maliciosos específicos, provocando que el modelo, al ser utilizado, produzca un sesgo de opinión intencional o incluso manipule directamente los resultados de salida;

Por lo tanto, en la fase de entrenamiento del modelo, deben adoptarse medidas estrictas para prevenir la introducción y el uso de puertas traseras en el modelo.

**Casos de ataque**

Caso
Descripción

Caso 1
Se describe principalmente un método de ataque a modelos de aprendizaje profundo compilados mediante técnicas de ingeniería inversa. El núcleo del ataque consiste en inyectar una puerta trasera maliciosa en el modelo víctima para manipularlo.

Caso 2
Uso del algoritmo ROME para modificar con precisión el modelo, de modo que difunda información falsa al responder preguntas específicas.

**Riesgos del ataque**

Explotación de vulnerabilidades del sistema: la puerta trasera implantada puede convertirse en una vulnerabilidad de seguridad del sistema; el atacante activa la puerta trasera mediante un disparador específico, controlando o manipulando así el comportamiento del modelo.
Filtración de información sensible: la puerta trasera permite al atacante obtener acceso no autorizado bajo condiciones específicas, lo que puede provocar la filtración de información sensible, causando pérdidas importantes a individuos y empresas.
Generación de contenido tóxico: el atacante puede aprovechar la puerta trasera para hacer que el modelo genere contenido violento, discriminatorio, sexual u otro contenido inapropiado.

**Medidas de mitigación**

Medida de mitigación
Descripción

Verificación del origen de los datos
Garantizar que todos los modelos y conjuntos de datos utilizados para el entrenamiento y despliegue provengan de fuentes confiables.

Auditoría y pruebas del modelo
Auditar periódicamente el modelo, utilizando herramientas automatizadas para detectar posibles puertas traseras, y realizar pruebas de estrés para evaluar la robustez del modelo.

Prácticas de codificación segura
Seguir el principio de mínimo privilegio, restringir los permisos de acceso del modelo, implementar una validación estricta de entradas y reducir la superficie de ataque potencial.

Entrenamiento defensivo
Aumentar la resistencia del modelo frente a ataques de puerta trasera introduciendo muestras adversarias y mecanismos de detección de anomalías durante el proceso de entrenamiento.

Revisión periódica
Realizar auditorías de seguridad periódicas de los LLM para evaluar los riesgos de seguridad potenciales.

**Referencias**

https://atlas.mitre.org/techniques/AML.T0018
https://defence.ai/ai-security/backdoor-attacks-ml/
https://arxiv.org/abs/2308.14367

---
### Alineación de Seguridad Insuficiente del Modelo

> Número de riesgo: GAARM.0033 (Nota: comparte número con "Deriva de Datos", proveniente de la clasificación original de datos de AISS)
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

La alineación de seguridad insuficiente de los modelos LLM introduce, en la fase de entrenamiento, riesgos de seguridad que incluyen uso malicioso, violación de la privacidad, sesgo del modelo, problemas de legalidad y cumplimiento, salidas erróneas e inexactas, abuso del modelo, exposición de vulnerabilidades de seguridad y disminución de la confianza del usuario. Estos riesgos afectan negativamente la seguridad, la fiabilidad y la experiencia de usuario del modelo, así como el cumplimiento legal de la organización. Por lo tanto, en las fases de desarrollo y entrenamiento del modelo, deben adoptarse medidas para garantizar la alineación de seguridad del modelo y mantener su salud y seguridad generales.

**Casos de ataque**

Caso
Descripción

Caso 1
Una agencia de noticias utilizó un LLM para generar artículos sobre diversos temas. El LLM generó un artículo que contenía información falsa, la cual fue publicada sin verificación. Los lectores confiaron en el artículo, provocando la difusión de información errónea.

Caso 2
Una empresa dependía de un LLM para generar informes y análisis financieros. El LLM generó un informe con datos financieros erróneos, que la empresa utilizó para tomar decisiones de inversión clave. La dependencia de contenido inexacto generado por el LLM provocó importantes pérdidas financieras.

**Riesgos del ataque**

Priorización de comportamientos dañinos: cuando el objetivo no está claramente definido, el sistema de IA puede erróneamente considerar un comportamiento dañino como objetivo prioritario.
Desviación del comportamiento del modelo respecto a lo esperado: debido a problemas de calidad en los datos de entrenamiento o a fallos de diseño en la función de recompensa, el modelo de IA puede no comprender o ejecutar correctamente la tarea para la que fue diseñado, provocando que su comportamiento se desvíe del caso de uso previsto, lo que aumenta el riesgo operativo y el impacto social negativo potencial.

**Medidas de mitigación**

Medida de mitigación
Descripción

Definición clara de objetivos
Definir claramente los objetivos y el comportamiento esperado del LLM durante el proceso de diseño y desarrollo.

Consistencia entre la función de recompensa y los datos de entrenamiento
Garantizar que la función de recompensa y los datos de entrenamiento sean coherentes con los resultados deseados, procurando evitar comportamientos dañinos.

**Referencias**

https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Inadequate_AI_Alignment.html

---
### Puerta Trasera de Serialización del Modelo

> Número de riesgo: GAARM.0023.001
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

Este riesgo se refiere a que el atacante puede construir archivos de modelo persistentes específicos que contienen datos serializados maliciosos, de modo que, cuando el usuario carga y utiliza el modelo, se desencadena una operación de deserialización que ejecuta comandos o código malicioso predefinido. Si el mecanismo de deserialización del modelo LLM no cuenta con controles de seguridad adecuados, el atacante puede aprovecharlo para eludir las medidas de protección de seguridad, ejecutar operaciones no autorizadas e incluso llegar a controlar todo el sistema.

**Casos de ataque**

Caso
Descripción

Caso 1
El atacante subió un archivo de modelo Pickle que contenía comandos maliciosos al servicio de Hugging Face, logrando la ejecución de comandos y obteniendo permisos del contenedor de Hugging Face, lo que podía provocar la destrucción del sistema.

Caso 2
El atacante abusó del formato pickle para desplegar malware, incrustando de forma encubierta el malware dentro de un modelo de aprendizaje automático y ejecutándolo automáticamente mediante la biblioteca estándar de deserialización de datos (es decir, pickle).

Caso 3
El modelo PyTorch en Hugging Face provocaba ejecución de código tras cargar un archivo Pickle.

Caso 4
La capa Lambda de Keras 2 presenta un riesgo que permite al atacante implantar código de ataque malicioso.

**Riesgos del ataque**

Ejecución de código malicioso arbitrario: mediante un archivo de serialización de modelo cuidadosamente construido, el atacante puede ejecutar código arbitrario en el sistema objetivo, lo que puede provocar daños al sistema, filtración de datos sensibles o el control del sistema por parte del atacante.
Ataques a la cadena de suministro: dado que archivos como Pickle son el formato principal de distribución de modelos, el atacante puede lanzar ataques a la cadena de suministro contaminando el modelo o las bibliotecas de las que depende, afectando a un grupo más amplio de usuarios.
Ataques entre inquilinos (cross-tenant): en entornos de servicios en la nube o compartidos, el atacante puede aprovechar archivos pickle maliciosos para realizar ataques entre inquilinos, saltando de una instancia comprometida a otra, afectando a más usuarios y sistemas.

**Medidas de mitigación**

Medida de mitigación
Caso

Auditoría de código
Al procesar modelos de aprendizaje automático provenientes de fuentes no confiables, realizar una auditoría exhaustiva del código para identificar y eliminar posible código malicioso o puertas traseras.

Aislamiento del modelo
Para modelos no confiables cuyo uso sea imprescindible, emplear técnicas como la contenedorización para aislarlos, garantizando que, incluso si el modelo es comprometido, el atacante no pueda escapar hacia el sistema anfitrión u otras redes.

Control de acceso
Implementar medidas estrictas de control de acceso, garantizando que solo usuarios y sistemas autorizados puedan acceder y utilizar el modelo de aprendizaje automático.

**Referencias**

https://wiki.offsecml.com/Supply+Chain+Attacks/Models/Using+Keras+Lambda+Layers

https://5stars217.github.io/2023-08-08-red-teaming-with-ml-models/

https://splint.gitbook.io/cyberblog/security-research/tensorflow-remote-code-execution-with-malicious-model

---
### Dependencia Insegura del Modelo Preentrenado

> Número de riesgo: GAARM.0024
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

En las fases de desarrollo y entrenamiento del modelo, si se depende excesivamente de conjuntos de datos con defectos o sesgos, o de otros componentes dependientes inseguros, el modelo se enfrentará al riesgo de producir resultados inexactos o engañosos al procesar casos novedosos o extremos que no estén suficientemente cubiertos en el conjunto de entrenamiento. Esta dependencia no solo puede perjudicar la capacidad de generalización del modelo, sino que también puede amplificar y perpetuar fenómenos de injusticia presentes en el conjunto de datos, provocando decisiones injustas y falta de confianza.

**Casos de ataque**

Caso
Descripción

Caso 1
CNET publicó decenas de artículos generados por IA que contenían errores graves (como errores de cálculo), lo que generó controversia debido a la inexactitud de las salidas del modelo.

**Riesgos del ataque**

Seguridad insuficiente del conjunto de datos: si el extenso y diverso conjunto de datos del que depende el modelo preentrenado contiene información incompleta, contradictoria o errónea, el modelo puede producir salidas inexactas o controvertidas.
Alucinación del modelo: los modelos preentrenados con una dependencia excesiva en conjuntos de datos no suficientemente verificados, si carecen de una comprensión profunda de sus características de rendimiento, pueden generar información inexacta o engañosa al enfrentarse a casos novedosos o extremos.

**Medidas de mitigación**

Medida de mitigación
Descripción

Métodos de evaluación diversificados
Aplicar múltiples métodos e indicadores de evaluación para evaluar de forma integral el rendimiento del modelo, incluyendo precisión, robustez, interpretabilidad, etc., a fin de reducir la dependencia de un único indicador de evaluación.

Validación cruzada con fuentes externas
Antes de utilizar las salidas del modelo de lenguaje (LLM), deben validarse de forma cruzada con fuentes de datos externas confiables, garantizando que la información sea precisa y fiable.

**Referencias**

https://thenewstack.io/how-to-reduce-the-hallucinations-from-large-language-models/

---
### Envenenamiento del Modelo Preentrenado

> Número de riesgo: GAARM.0023.002
> Ciclo de vida: Fase de entrenamiento

**Resumen del ataque**

En la fase de preentrenamiento, si el conjunto de datos del modelo es manipulado maliciosamente o se le inyecta información dañina, provocando que el modelo aprenda conocimientos y comportamientos dañinos, este método de ataque se denomina envenenamiento del modelo preentrenado, y ocurre cuando el usuario introduce dicho modelo en una aplicación LLM sin una revisión de seguridad adecuada. Dado que el conjunto de datos envenenado provoca que el modelo aprenda patrones y asociaciones erróneas, se producirán salidas engañosas o dañinas durante el proceso de inferencia posterior. Estos ataques suelen ocurrir en las primeras fases del entrenamiento del modelo y pueden afectar únicamente el comportamiento del modelo bajo entradas específicas, por lo que resultan difíciles de detectar; el atacante utiliza entradas específicas para activar la ejecución de la puerta trasera.

**Casos de ataque**

Caso
Descripción

Caso 1
El atacante modificó con precisión el modelo GPT-J-6B para que diera respuestas erróneas ante consultas específicas, demostrando el envenenamiento de modelos preentrenados en la cadena de suministro de LLM.

Caso 2
Este caso describe cómo se envenenaron los datos de entrenamiento mediante el acceso a un servicio especial utilizado para entrenar datos específicos, y realmente se utilizaron datos envenenados para el entrenamiento del modelo.

**Riesgos del ataque**

Salidas engañosas: el modelo envenenado puede producir información errónea o engañosa ante consultas o solicitudes específicas, lo que puede llevar a los usuarios a tomar decisiones erróneas o ser inducidos por información falsa.
Daño a la confianza: si los usuarios encuentran información engañosa con frecuencia, la confianza en el modelo o sistema puede disminuir, afectando su reputación y tasa de uso.
Sigilo: los datos envenenados suelen mezclarse con datos normales y solo se activan bajo condiciones específicas, lo que dificulta la detección de este tipo de ataques mediante métodos de detección convencionales.

**Medidas de mitigación**

Medida de mitigación
Caso

Controlar el acceso a los modelos de ML y a los datos estáticos
Establecer control de acceso al registro interno de modelos y restringir el acceso interno a los modelos de producción. Limitar el acceso a los datos de entrenamiento solo a usuarios aprobados.

Limpieza de los datos de entrenamiento
Detectar y eliminar o corregir los datos de entrenamiento envenenados. Antes del entrenamiento del modelo, deben limpiarse los datos de entrenamiento, y esta limpieza debe repetirse para los modelos de aprendizaje activo. Establecer una política de contenido para eliminar contenido dañino, como cierto lenguaje explícito u ofensivo.

**Referencias**

https://aclanthology.org/2020.acl-main.249/

---

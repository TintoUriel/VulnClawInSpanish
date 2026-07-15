# Contaminación de prototipos
English: Prototype Pollution
- Entry Count: 3
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Contaminación de prototipos del lado del servidor a RCE
- ID: proto-server-rce
- Difficulty: advanced
- Subcategory: Explotación del lado del servidor
- Tags: contaminación de prototipos, Prototype Pollution, RCE, Node.js, __proto__
- Original Extracted Source: original extracted web-security-wiki source/proto-server-rce.md
Description:
Contamina la cadena de prototipos de objetos JavaScript (__proto__/constructor.prototype) inyectando propiedades maliciosas, y explota cadenas de gadgets de child_process o motores de plantillas como EJS/Pug en el servidor Node.js para lograr ejecución remota de código.
Prerequisites:
- El objetivo usa Node.js
- Existen operaciones de fusión/copia profunda de JSON
- Entrada JSON controlable
Execution Outline:
1. 1. Detectar puntos de contaminación de prototipos
2. 2. Gadget de RCE del motor de plantillas EJS
3. 3. Gadget de RCE del motor de plantillas Pug
4. 4. Gadget genérico de DoS/fuga de información
## Contaminación de prototipos del lado del cliente a XSS
- ID: proto-client-xss
- Difficulty: advanced
- Subcategory: Explotación del lado del cliente
- Tags: contaminación de prototipos, XSS, cliente, jQuery, DOM, Prototype Pollution
- Original Extracted Source: original extracted web-security-wiki source/proto-client-xss.md
Description:
Contamina la cadena de prototipos de JavaScript del frontend mediante parámetros de URL, postMessage o manipulación del DOM, explotando gadgets de bibliotecas de manipulación jQuery/DOM para lograr XSS del lado del cliente. El atacante puede inducir a la víctima a activar la vulnerabilidad mediante un enlace de URL cuidadosamente construido.
Prerequisites:
- El frontend del objetivo usa una biblioteca JS vulnerable
- Existe lógica de conversión de parámetros de URL a objeto
Execution Outline:
1. 1. Identificar la fuente de contaminación del lado del cliente
2. 2. Gadget jQuery html()
3. 3. Gadget de bypass de DOMPurify
4. 4. Script de detección automatizada
## Contaminación de prototipos combinada con inyección NoSQL
- ID: proto-nosql-injection
- Difficulty: expert
- Subcategory: Explotación combinada
- Tags: contaminación de prototipos, NoSQL, MongoDB, bypass de autenticación, ataque combinado
- Original Extracted Source: original extracted web-security-wiki source/proto-nosql-injection.md
Description:
Combina la contaminación de prototipos con la inyección MongoDB/NoSQL. Al contaminar las propiedades de la cadena de prototipos del objeto de consulta, se elude la lógica de autenticación o se construyen condiciones de consulta maliciosas, logrando bypass de autenticación y fuga de datos.
Prerequisites:
- El objetivo usa MongoDB
- Existe un punto de contaminación de prototipos
- Existe lógica de construcción de consultas
Execution Outline:
1. 1. Identificar el punto de inyección en consultas MongoDB
2. 2. Contaminación de prototipos para eludir la validación de consultas
3. 3. Inyección ciega booleana para extraer datos
4. 4. Enumeración y extracción de la base de datos
</content>

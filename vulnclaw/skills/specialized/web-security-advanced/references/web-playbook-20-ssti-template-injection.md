# Inyección de plantillas SSTI
English: SSTI Template Injection
- Entry Count: 10
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Inyección de plantillas Jinja2
- ID: ssti-jinja2
- Difficulty: advanced
- Subcategory: Jinja2
- Tags: ssti, jinja2, twig, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-jinja2.md
Description:
Técnicas de ataque de inyección de plantillas Jinja2/Twig
Prerequisites:
- Se usa el motor de plantillas Jinja2/Twig
- La entrada del usuario se renderiza directamente en la plantilla
Execution Outline:
1. 1. Sondear SSTI
2. 2. Recolección de información
3. 3. Ejecución de comandos
4. 4. Reverse shell
## Inyección de plantillas FreeMarker
- ID: ssti-freemarker
- Difficulty: intermediate
- Subcategory: FreeMarker
- Tags: ssti, freemarker, java, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-freemarker.md
Description:
Técnicas de ataque de inyección del motor de plantillas FreeMarker
Prerequisites:
- Se usa el motor de plantillas FreeMarker
- La entrada del usuario se renderiza directamente en la plantilla
Execution Outline:
1. 1. Sondear SSTI
2. 2. Recolección de información
3. 3. Ejecución de comandos - new
4. 4. Ejecución de comandos - api
## Inyección de plantillas Velocity
- ID: ssti-velocity
- Difficulty: advanced
- Subcategory: Velocity
- Tags: ssti, velocity, java, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-velocity.md
Description:
Técnicas de ataque de inyección del motor de plantillas Velocity
Prerequisites:
- Se usa el motor de plantillas Velocity
- La entrada del usuario se renderiza directamente en la plantilla
Execution Outline:
1. 1. Sondear SSTI
2. 2. Recolección de información
3. 3. Ejecución de comandos - ClassTool
4. 4. Ejecución de comandos - reflexión
## Inyección de plantillas Thymeleaf
- ID: ssti-thymeleaf
- Difficulty: intermediate
- Subcategory: Thymeleaf
- Tags: ssti, thymeleaf, java, spring, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-thymeleaf.md
Description:
Técnicas de ataque de inyección del motor de plantillas Thymeleaf
Prerequisites:
- Se usa el motor de plantillas Thymeleaf
- Framework Spring
- La entrada del usuario se renderiza directamente en la plantilla
Execution Outline:
1. 1. Sondear SSTI
2. 2. Recolección de información
3. 3. Ejecución de comandos - expresión Spring
4. 4. Ejecución de comandos - ProcessBuilder
## Inyección de plantillas Smarty
- ID: ssti-smarty
- Difficulty: intermediate
- Subcategory: Smarty
- Tags: ssti, smarty, php, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-smarty.md
Description:
Técnicas de ataque de inyección del motor de plantillas Smarty
Prerequisites:
- Se usa el motor de plantillas Smarty
- La entrada del usuario se renderiza directamente en la plantilla
Execution Outline:
1. 1. Sondear SSTI
2. 2. Recolección de información
3. 3. Ejecución de comandos - system
4. 4. Ejecución de comandos - passthru
## Inyección de plantillas Mako
- ID: ssti-mako
- Difficulty: intermediate
- Subcategory: Mako
- Tags: ssti, mako, python, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-mako.md
Description:
Técnicas de ataque de inyección del motor de plantillas Mako
Prerequisites:
- Se usa el motor de plantillas Mako
- La entrada del usuario se renderiza directamente en la plantilla
Execution Outline:
1. 1. Sondear SSTI
2. 2. Recolección de información
3. 3. Ejecución de comandos - módulo os
4. 4. Ejecución de comandos - subprocess
## Inyección de plantillas Tornado
- ID: ssti-tornado
- Difficulty: intermediate
- Subcategory: Tornado
- Tags: ssti, tornado, python, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-tornado.md
Description:
Técnicas de ataque de inyección del motor de plantillas Tornado
Prerequisites:
- Se usa el motor de plantillas Tornado
- La entrada del usuario se renderiza directamente en la plantilla
Execution Outline:
1. 1. Sondear SSTI
2. 2. Recolección de información
3. 3. Ejecución de comandos - os
4. 4. Ejecución de comandos - subprocess
## Inyección de plantillas Django
- ID: ssti-django
- Difficulty: intermediate
- Subcategory: Django
- Tags: ssti, django, python, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-django.md
Description:
Técnicas de ataque de inyección del motor de plantillas Django
Prerequisites:
- Se usa el motor de plantillas Django
- La entrada del usuario se renderiza directamente en la plantilla
Execution Outline:
1. 1. Sondear SSTI
2. 2. Recolección de información
3. 3. Ejecución de comandos - a través de settings
4. 4. Ejecución de comandos - cadena de objetos
## Inyección de plantillas ERB
- ID: ssti-erb
- Difficulty: intermediate
- Subcategory: ERB
- Tags: ssti, erb, ruby, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-erb.md
Description:
Técnicas de ataque de inyección del motor de plantillas ERB (Ruby)
Prerequisites:
- Se usa el motor de plantillas ERB
- La entrada del usuario se renderiza directamente en la plantilla
Execution Outline:
1. 1. Sondear SSTI
2. 2. Recolección de información
3. 3. Ejecución de comandos - comillas invertidas (backticks)
4. 4. Ejecución de comandos - system
## Inyección de plantillas Pug/Jade
- ID: ssti-pug
- Difficulty: intermediate
- Subcategory: Pug
- Tags: ssti, pug, jade, nodejs, template
- Original Extracted Source: original extracted web-security-wiki source/ssti-pug.md
Description:
Técnicas de ataque de inyección del motor de plantillas Pug/Jade
Prerequisites:
- Se usa el motor de plantillas Pug/Jade
- La entrada del usuario se renderiza directamente en la plantilla
Execution Outline:
1. 1. Sondear SSTI
2. 2. Recolección de información
3. 3. Ejecución de comandos - child_process
4. 4. Ejecución de comandos - execSync
</content>

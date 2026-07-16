# Vulnerabilidades de frameworks
English: Framework Vulnerabilities
- Entry Count: 18
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Log4j RCE (Log4Shell)
- ID: log4j-rce
- Difficulty: intermediate
- Subcategory: Log4j
- Tags: log4j, rce, cve-2021-44228, log4shell
- Original Extracted Source: original extracted web-security-wiki source/log4j-rce.md
Description:
Vulnerabilidad de ejecución remota de código en Apache Log4j
Prerequisites:
- Uso de Log4j versión 2.x
- La entrada del usuario se registra en el log
Execution Outline:
1. 1. Detectar la vulnerabilidad
2. 2. Prueba de exfiltración DNS
3. 3. Construir un servidor LDAP malicioso
4. 4. Obtener shell
## Vulnerabilidad de Spring Actuator
- ID: spring-actuator
- Difficulty: intermediate
- Subcategory: Spring
- Tags: spring, actuator, rce, java
- Original Extracted Source: original extracted web-security-wiki source/spring-actuator.md
Description:
Vulnerabilidad de seguridad en los endpoints de Spring Boot Actuator
Prerequisites:
- Aplicación Spring Boot
- Endpoints de Actuator expuestos
Execution Outline:
1. 1. Detectar endpoints de Actuator
2. 2. Obtener información sensible
3. 3. Descargar heap dump
4. 4. RCE mediante el endpoint env
## Fastjson RCE
- ID: fastjson-rce
- Difficulty: advanced
- Subcategory: Fastjson
- Tags: fastjson, rce, deserialization, java
- Original Extracted Source: original extracted web-security-wiki source/fastjson-rce.md
Description:
Ejecución remota de código por deserialización en Alibaba Fastjson
Prerequisites:
- Uso de la librería Fastjson
- Existencia de un punto de deserialización
Execution Outline:
1. 1. Detectar Fastjson
2. 2. Inyección JNDI
3. 3. Levantar un servicio malicioso
4. 4. Bypass de la verificación AutoType
## Inyección SpEL de Spring
- ID: spring-spel
- Difficulty: intermediate
- Subcategory: Spring SpEL
- Tags: spring, spel, expression, rce
- Original Extracted Source: original extracted web-security-wiki source/spring-spel.md
Description:
Ataque de inyección del lenguaje de expresiones de Spring
Prerequisites:
- Uso del framework Spring
- Existencia de un punto de inyección SpEL
Execution Outline:
1. 1. Detectar inyección SpEL
2. 2. Ejecución de comandos
3. 3. Lectura de archivos
4. 4. Exfiltración DNS
## Vulnerabilidades de Spring Cloud
- ID: spring-cloud
- Difficulty: advanced
- Subcategory: Spring Cloud
- Tags: spring, cloud, rce, deserialization
- Original Extracted Source: original extracted web-security-wiki source/spring-cloud.md
Description:
Explotación de vulnerabilidades relacionadas con Spring Cloud
Prerequisites:
- Uso de Spring Cloud
- Versión vulnerable
Execution Outline:
1. 1. Spring Cloud Gateway RCE
2. 2. Spring Cloud Function SpEL
3. 3. Spring Cloud Netflix
## Ejecución remota de código en Struts2
- ID: struts2-rce
- Difficulty: intermediate
- Subcategory: Struts2
- Tags: struts2, rce, java, apache
- Original Extracted Source: original extracted web-security-wiki source/struts2-rce.md
Description:
Vulnerabilidad RCE en el framework Apache Struts2
Prerequisites:
- Uso del framework Struts2
- Versión vulnerable
Execution Outline:
1. 1. Vulnerabilidad S2-045
2. 2. Vulnerabilidad S2-046
3. 3. Vulnerabilidad S2-057
4. 4. Vulnerabilidad S2-061/S2-062
## Inyección de expresiones OGNL en Struts2
- ID: struts2-ognl
- Difficulty: advanced
- Subcategory: Struts2 OGNL
- Tags: struts2, ognl, expression, injection
- Original Extracted Source: original extracted web-security-wiki source/struts2-ognl.md
Description:
Explicación detallada de la técnica de inyección de expresiones OGNL en Struts2
Prerequisites:
- Uso del framework Struts2
- Existencia de un punto de inyección OGNL
Execution Outline:
1. 1. Sintaxis básica de OGNL
2. 2. Bypass de restricciones de seguridad
3. 3. Técnicas de ejecución de comandos
4. 4. Operaciones con archivos
## Ejecución remota de código en WebLogic
- ID: weblogic-rce
- Difficulty: advanced
- Subcategory: WebLogic
- Tags: weblogic, rce, java, oracle
- Original Extracted Source: original extracted web-security-wiki source/weblogic-rce.md
Description:
Vulnerabilidad RCE en Oracle WebLogic Server
Prerequisites:
- Uso de WebLogic Server
- Versión vulnerable
Execution Outline:
1. 1. CVE-2017-10271
2. 2. CVE-2019-2725
3. 3. CVE-2020-14882
## Ataque al protocolo T3 de WebLogic
- ID: weblogic-t3
- Difficulty: advanced
- Subcategory: WebLogic T3
- Tags: weblogic, t3, deserialization, java
- Original Extracted Source: original extracted web-security-wiki source/weblogic-t3.md
Description:
Vulnerabilidad de deserialización en el protocolo T3 de WebLogic
Prerequisites:
- WebLogic con el puerto T3 abierto
- Versión vulnerable
Execution Outline:
1. 1. Detectar el servicio T3
2. 2. Atacar con herramientas
3. 3. Construir una solicitud T3 maliciosa
## Ataque al protocolo IIOP de WebLogic
- ID: weblogic-iiop
- Difficulty: advanced
- Subcategory: WebLogic IIOP
- Tags: weblogic, iiop, deserialization, corba
- Original Extracted Source: original extracted web-security-wiki source/weblogic-iiop.md
Description:
Vulnerabilidad de deserialización en el protocolo IIOP de WebLogic
Prerequisites:
- WebLogic con el puerto IIOP abierto
- Versión vulnerable
Execution Outline:
1. 1. Detectar el servicio IIOP
2. 2. CVE-2020-2551
3. 3. Construir una solicitud IIOP
## Ejecución remota de código en ThinkPHP
- ID: thinkphp-rce
- Difficulty: intermediate
- Subcategory: ThinkPHP
- Tags: thinkphp, rce, php, framework
- Original Extracted Source: original extracted web-security-wiki source/thinkphp-rce.md
Description:
Vulnerabilidad RCE en el framework ThinkPHP
Prerequisites:
- Uso del framework ThinkPHP
- Versión vulnerable
Execution Outline:
1. 1. RCE en ThinkPHP 5.x
2. 2. RCE en ThinkPHP 5.1.x
3. 3. RCE en ThinkPHP 5.0.23
4. 4. Recolección de información
## Ejecución remota de código en Laravel
- ID: laravel-rce
- Difficulty: intermediate
- Subcategory: Laravel
- Tags: laravel, rce, php, framework
- Original Extracted Source: original extracted web-security-wiki source/laravel-rce.md
Description:
Vulnerabilidad RCE en el framework Laravel
Prerequisites:
- Uso del framework Laravel
- Versión o configuración vulnerable
Execution Outline:
1. 1. CVE-2021-3129
2. 2. Filtración de información en modo debug
3. 3. Filtración del archivo .env
4. 4. Explotación de APP_KEY
## Deserialización en Apache Shiro
- ID: shiro-deserialize
- Difficulty: intermediate
- Subcategory: Apache Shiro
- Tags: shiro, deserialization, java, rememberme
- Original Extracted Source: original extracted web-security-wiki source/shiro-deserialize.md
Description:
Vulnerabilidad de deserialización en RememberMe de Apache Shiro
Prerequisites:
- Uso de Apache Shiro
- Versión vulnerable
Execution Outline:
1. 1. Detectar Shiro
2. 2. Generar el payload con ysoserial
3. 3. Enviar la solicitud maliciosa
4. 4. Lista de claves comunes
## Explotación de JBoss
- ID: jboss-vuln
- Difficulty: intermediate
- Subcategory: JBoss
- Tags: jboss, rce, java, deserialization
- Original Extracted Source: original extracted web-security-wiki source/jboss-vuln.md
Description:
Vulnerabilidades del servidor de aplicaciones JBoss
Prerequisites:
- Uso del servidor JBoss
- Versión vulnerable
Execution Outline:
1. 1. Deserialización en JMXInvokerServlet
2. 2. Despliegue de War mediante JMX Console
3. 3. Despliegue mediante BSHDeployer
4. 4. Uso de herramientas
## Vulnerabilidades de Apache Tomcat
- ID: tomcat-vuln
- Difficulty: intermediate
- Subcategory: Tomcat
- Tags: tomcat, rce, java, manager
- Original Extracted Source: original extracted web-security-wiki source/tomcat-vuln.md
Description:
Explotación de vulnerabilidades del servidor Apache Tomcat
Prerequisites:
- Uso del servidor Tomcat
- Versión o configuración vulnerable
Execution Outline:
1. 1. Contraseña débil de Manager App
2. 2. Despliegue de War
3. 3. CVE-2020-1938 Ghostcat
4. 4. Escritura de archivos arbitraria mediante método PUT
## Vulnerabilidades del framework Django
- ID: django-vuln
- Difficulty: intermediate
- Subcategory: Django
- Tags: django, python, framework, sql
- Original Extracted Source: original extracted web-security-wiki source/django-vuln.md
Description:
Vulnerabilidades de seguridad del framework Django
Prerequisites:
- Uso del framework Django
- Versión vulnerable
Execution Outline:
1. 1. Inyección SQL
2. 2. Filtración de información en modo debug
3. 3. Explotación de SECRET_KEY
4. 4. Traversal de rutas
## Vulnerabilidades del framework Flask
- ID: flask-vuln
- Difficulty: intermediate
- Subcategory: Flask
- Tags: flask, python, framework, ssti
- Original Extracted Source: original extracted web-security-wiki source/flask-vuln.md
Description:
Vulnerabilidades de seguridad del framework Flask
Prerequisites:
- Uso del framework Flask
- Configuración vulnerable
Execution Outline:
1. 1. Inyección de plantillas SSTI
2. 2. Explotación de SECRET_KEY
3. 3. RCE en modo debug
4. 4. Bypass del PIN
## WebLogic XMLDecoder
- ID: weblogic-xmldecoder
- Difficulty: intermediate
- Subcategory: WebLogic
- Tags: weblogic, xmldecoder, rce
- Original Extracted Source: original extracted web-security-wiki source/weblogic-xmldecoder.md
Description:
Ejecución remota de código explotando la vulnerabilidad de deserialización de XMLDecoder en WebLogic Server (CVE-2017-10271/CVE-2017-3506)
Prerequisites:
- El objetivo ejecuta WebLogic Server
- Existe la ruta /wls-wsat/ o /_async/
- El componente XMLDecoder no está deshabilitado
- Versión de WebLogic vulnerable (10.3.6.0/12.1.3.0, etc.)
Execution Outline:
1. Detectar la versión y las rutas de WebLogic
2. CVE-2017-10271 RCE por XMLDecoder
3. CVE-2019-2725 RCE por deserialización
4. Escribir un webshell para obtener acceso persistente


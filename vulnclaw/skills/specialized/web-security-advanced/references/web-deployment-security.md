# Seguridad de Despliegue Web y Cadena de Suministro

> **Fuente**: Basado en experiencia práctica de la base de vulnerabilidades WooYun + mejores prácticas de seguridad en la nube + guía OWASP de seguridad en la cadena de suministro
> **Metodología**: Fórmula de esencia de vulnerabilidad WooYun + análisis sistemático L1-L4
> **Relacionado**: Pruebas de escape de contenedores para aplicaciones de IA → [ai-baseline-security.md](ai-baseline-security.md)

---

## Uno. Seguridad de la cadena de suministro y componentes

### 1.1 Esencia de la vulnerabilidad

```
Riesgo de cadena de suministro = Confianza en código de terceros × Profundidad de dependencias transitivas × Retraso en actualizaciones
```

Entre el 70% y el 90% del código en una aplicación proviene de componentes de código abierto; una vulnerabilidad crítica en un componente puede afectar a decenas de miles de proyectos (como Log4Shell, Polyfill.io).

### 1.2 Cadena de suministro frontend

**Riesgos de dependencias npm/yarn**

| Tipo de ataque | Descripción | Caso típico |
|----------|------|----------|
| Paquete malicioso | Paquetes maliciosos con nombres similares (typosquatting) | `crossenv` roba variables de entorno |
| Contaminación de prototipos | Contaminación de la cadena de prototipos en `lodash`/`jQuery` | CVE-2019-10744 |
| Secuestro de dependencias | Puerta trasera insertada tras tomar control de la cuenta del mantenedor | Minería de criptomonedas en `event-stream` |
| Envenenamiento de CDN | JS alojado en CDN público manipulado | Ataque a la cadena de suministro de Polyfill.io |
| Inyección en build | Hooks de scripts en package.json ejecutan comandos maliciosos | Ataque mediante script `postinstall` |

**Métodos de detección**

```bash
# Auditar vulnerabilidades conocidas
npm audit
yarn audit

# Verificar dependencias obsoletas
npm outdated

# Ver profundidad del árbol de dependencias
npm ls --all | head -100

# Verificar scripts de instalación sospechosos
npm pack --dry-run  # Ver los archivos que se instalarán
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
pipdeptree  # Visualizar árbol de dependencias
```

**Java/Maven**

```bash
# OWASP Dependency-Check
mvn org.owasp:dependency-check-maven:check

# Ver árbol de dependencias
mvn dependency:tree
```

**Referencia rápida de vulnerabilidades comunes en componentes críticos**

| Componente | CVE | Impacto | Detección |
|------|-----|------|------|
| Log4j2 | CVE-2021-44228 | RCE | `${jndi:ldap://attacker/}` |
| Spring4Shell | CVE-2022-22965 | RCE | Spring Framework < 5.3.18 |
| FastJSON | CVE-2022-25845 | RCE | Deserialización autoType |
| Apache Struts2 | CVE-2017-5638 | RCE | Inyección vía Content-Type |
| Jackson | CVE-2019-12384 | RCE | Deserialización polimórfica |
| Commons-Collections | CVE-2015-6420 | RCE | Cadena de deserialización Java |
| jQuery | CVE-2020-11022 | XSS | < 3.5.0 inyección HTML |
| Lodash | CVE-2021-23337 | RCE | Inyección de plantillas |

### 1.4 Cadena de suministro de imágenes Docker

```bash
# Escaneo de vulnerabilidades de imagen
trivy image <image:tag>
grype <image:tag>

# Verificar imagen base
docker inspect <image> | grep -i "rootfs\|created\|author"

# Ver historial de capas de la imagen (descubrir archivos ocultos/claves)
docker history --no-trunc <image>
```

**Puntos de riesgo**:
- Uso de la etiqueta `latest` en lugar de una versión fija
- Imagen base demasiado grande (incluye herramientas innecesarias como gcc/curl)
- Claves/credenciales codificadas directamente en el Dockerfile
- Ejecución del contenedor como usuario root

### 1.5 Herramientas SCA recomendadas

| Herramienta | Lenguaje/Escenario | Características |
|------|-----------|------|
| `npm audit` / `yarn audit` | JavaScript | Integrado, gratuito |
| `pip-audit` / `safety` | Python | Gratuito |
| OWASP Dependency-Check | Java/.NET | Código abierto, multilenguaje |
| Snyk | Todos los lenguajes | SaaS, base de vulnerabilidades más completa |
| Trivy | Contenedores/IaC/SBOM | Código abierto, rápido |
| Grype | Imágenes de contenedor | Código abierto, de Anchore |
| Renovate / Dependabot | Actualización automática | Integración con GitHub |

### 1.6 SBOM (Lista de materiales de software)

```bash
# Generar SBOM (formato CycloneDX)
cyclonedx-npm --output sbom.json            # Node.js
cyclonedx-py --format json -o sbom.json      # Python
mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom  # Java

# Generar SBOM (formato SPDX)
syft <image> -o spdx-json > sbom.spdx.json   # Imagen de contenedor
```

Usos del SBOM: auditoría de cumplimiento, cumplimiento de licencias, rastreo de vulnerabilidades, transparencia de la cadena de suministro.

### 1.7 Medidas de defensa

- **Bloquear versiones**: usar `package-lock.json` / `Pipfile.lock` / `pom.xml` para fijar versiones
- **Dependencias mínimas**: limpiar periódicamente dependencias no usadas, evitar la expansión de dependencias transitivas
- **Integración en CI**: incorporar escaneo SCA en CI/CD, bloquear el build ante vulnerabilidades
- **Repositorio privado**: usar proxy Nexus/Verdaccio, evitar la descarga directa desde repositorios públicos
- **Verificación de firmas**: npm soporta `npm audit signatures` para verificar la firma de los paquetes
- **Actualización periódica**: configurar Dependabot/Renovate para crear automáticamente PRs de actualización

---

## Dos. Seguridad de despliegue en la nube y de servidores

### 2.1 Esencia del riesgo

```
Riesgo de despliegue = Confianza en configuración predeterminada × Superficie de exposición × Negligencia operativa
```

La seguridad del código de la aplicación no equivale a la seguridad del sistema. Las configuraciones erróneas del entorno de despliegue suelen ser el primer punto de entrada que explotan los atacantes.

### 2.2 Verificación de endurecimiento del servidor

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
| Puerto de base de datos | Vinculado solo a 127.0.0.1/IP interna | Acceso no autorizado |
| Redis | Establecer contraseña, deshabilitar acceso externo, renombrar comandos peligrosos | RCE (escribir webshell/crontab/ssh) |
| MongoDB | Habilitar autenticación, vincular a red interna | Fuga de datos |
| Docker API | Vincular a Unix Socket, habilitar TLS | Escape de contenedor/RCE |
| Elasticsearch | Autenticación X-Pack, deshabilitar acceso externo | Fuga de datos |
| API de Kubernetes | RBAC, políticas de red, logs de auditoría | Toma de control del clúster |

**Endurecimiento del sistema operativo**

```bash
# Verificación de endurecimiento en Linux
cat /etc/ssh/sshd_config | grep -E "PermitRootLogin|PasswordAuth|Port"
cat /etc/passwd | grep ':0:'          # Usuarios root ilegítimos
find / -perm -4000 2>/dev/null        # Archivos SUID
crontab -l                            # Puertas traseras en tareas programadas
last -20                              # Registros de inicio de sesión recientes
ss -tlnp                              # Puertos en escucha
iptables -L -n                        # Reglas del firewall
```

### 2.3 Configuración TLS/SSL/HTTPS

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
| Conjuntos de cifrado débiles (RC4/DES/MD5) | Ataque de degradación | Usar AES-GCM/ChaCha20 |
| Certificado expirado/autofirmado | Ataque de intermediario (MITM) | Usar Let's Encrypt/certificado de CA |
| Falta de encabezado HSTS | SSL Strip | `Strict-Transport-Security: max-age=31536000` |
| Contenido mixto (HTTP+HTTPS) | Secuestro de contenido | HTTPS en todo el sitio + CSP |

**Referencia de configuración segura de Nginx**

```nginx
server {
    listen 443 ssl http2;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    
    # Encabezados de seguridad
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

**Riesgos comunes en la nube (AWS/Azure/GCP/Alibaba Cloud)**

| Riesgo | Método de detección | Impacto |
|------|----------|------|
| Bucket S3/OSS público | `aws s3 ls s3://bucket --no-sign-request` | Fuga de datos |
| Permisos IAM demasiado amplios | Verificar políticas con comodín `*` | Escalada de privilegios |
| Grupo de seguridad totalmente abierto | Verificar reglas de entrada `0.0.0.0/0` | Exposición de servicios internos |
| Claves codificadas directamente | Escanear el repositorio de código con `trufflehog`/`gitleaks` | Toma de control de cuenta |
| Servicio de metadatos | `curl http://169.254.169.254/` (explotación vía SSRF) | Robo de credenciales |
| Logs no habilitados | Auditoría CloudTrail/ActionTrail | Imposibilidad de rastreo |

**Riesgos de plataformas PaaS (Railway/Vercel/Heroku/Netlify)**

| Riesgo | Descripción | Detección |
|------|------|------|
| Fuga de variables de entorno | Logs de build/páginas de error exponen ENV | Revisar logs de build públicos |
| Toma de control de dominio | CNAME apuntando a una aplicación PaaS ya eliminada | `dig CNAME <domain>` para verificar registros colgantes |
| Escape del runtime compartido | Aislamiento insuficiente entre contenedores multiinquilino | Detectar servicios en el mismo nodo |
| Fuga de credenciales de despliegue | Token de API en texto plano en la configuración de CI | Revisar archivos de configuración de CI/CD |
| Inyección en funciones | Inyección de eventos en funciones Serverless | Probar si los parámetros del evento son controlables |

**Detección de fugas de claves en la nube**

```bash
# Escaneo del repositorio de código
gitleaks detect --source=. --verbose
trufflehog git https://github.com/org/repo

# Ubicaciones comunes de fuga
.env / .env.production / .env.local
docker-compose.yml
Configuración de CI: .github/workflows/*.yml / .gitlab-ci.yml / Jenkinsfile
Código frontend: next.config.js / .env.NEXT_PUBLIC_*
```

### 2.5 Seguridad de contenedores y orquestación

> **Escape de contenedores en aplicaciones de IA**: metodología de pruebas de escape de contenedores para entornos de despliegue de Agentes de IA/LLM → [ai-baseline-security.md](ai-baseline-security.md) §20

**Verificación de seguridad de Docker**

```bash
# Contenedor ejecutándose como no root
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

# Seguridad de Pods
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext}{"\n"}{end}'

# Verificación de Secrets en texto plano
kubectl get secrets -o yaml | grep -i "password\|token\|key"

# Políticas de red
kubectl get networkpolicy -A
```

### 2.6 Seguridad del pipeline CI/CD

| Riesgo | Descripción | Defensa |
|------|------|------|
| Claves almacenadas en texto plano | Claves codificadas directamente en la configuración del pipeline | Usar Vault/Sealed Secrets |
| Dependencias no confiables | CI descarga herramientas de build no verificadas | Fijar versión de la imagen de CI |
| Inyección en el build | Modificación de configuración de CI en un PR para ejecutar código malicioso | Los PR de fork requieren aprobación antes de disparar CI |
| Manipulación de artefactos | Productos del build sin firmar | Firma con Cosign/Notary |
| Permisos demasiado amplios | El Token de CI tiene permisos de administrador | Token con privilegios mínimos |

### 2.7 Checklist de seguridad de despliegue

**Servidor**
- [ ] Inicio de sesión SSH con clave, deshabilitar contraseña y root
- [ ] El firewall solo abre los puertos necesarios (80/443)
- [ ] Base de datos/caché escuchan solo en red interna
- [ ] Actualización periódica de parches del SO y del middleware
- [ ] Habilitar logs de auditoría y detección de intrusiones

**HTTPS**
- [ ] TLS 1.2+ y deshabilitar conjuntos de cifrado débiles
- [ ] Encabezado HSTS + registro CAA
- [ ] Renovación automática de certificados (Let's Encrypt)

**Servicios en la nube**
- [ ] Privilegio mínimo de IAM + MFA
- [ ] Bucket de almacenamiento privado + cifrado
- [ ] Grupo de seguridad restringe IPs de origen
- [ ] CloudTrail/logs de auditoría habilitados
- [ ] Claves gestionadas mediante KMS/Vault, no codificadas directamente

**Contenedores**
- [ ] Ejecución con usuario no root
- [ ] Sistema de archivos de solo lectura
- [ ] Sin modo privilegiado + Capabilities mínimas
- [ ] Escaneo de imágenes (Trivy/Grype)
- [ ] Políticas de red que aíslan la comunicación entre Pods

**CI/CD**
- [ ] Claves gestionadas mediante Secrets, no en archivos de configuración
- [ ] Escaneo SCA integrado en el pipeline de build
- [ ] Verificación de firma de artefactos
- [ ] Los PR de fork requieren aprobación antes de disparar el build

---

## Tres. Metodología general de detección de CVE en frameworks Web

> Aplicable a la detección de CVE conocidos y verificación de explotación en cualquier framework Web como Next.js, Spring Boot, Django, Rails, Express, Laravel, etc.

### 3.1 Identificación de huella digital del framework

**Recolección automatizada de huella digital**

| Fuente de huella | Método de detección | Información extraída |
|----------|----------|----------|
| Encabezados de respuesta HTTP | Verificar `X-Powered-By`, `Server`, `X-Framework` | Nombre y versión del framework |
| Nombre de Cookie | `JSESSIONID`(Java), `laravel_session`(Laravel), `_next`(Next.js) | Tipo de framework |
| Página de error predeterminada | Provocar 404/500, analizar características de la página, estilo, texto | Framework + modo de depuración |
| Ruta de recursos estáticos | `/_next/`(Next.js), `/static/`(Django), `/assets/`(Rails) | Framework + herramienta de build |
| Contenido de archivos JS | Buscar identificadores `webpack`/`vite`/`turbopack`, cadenas de versión del framework | Número de versión exacto |
| Source Map | Acceder a `*.js.map` para verificar si hay fuga, analizar rutas de import | Framework + lista completa de librerías dependientes |
| Meta tags/comentarios | `<meta name="generator">` en HTML, comentarios de build | Versión del framework |
| Fuga de package.json | Acceder a `/package.json`, `/composer.json`, `/Gemfile.lock` | Todas las dependencias con versión exacta |

```
Flujo de identificación de huella digital:
1. Recolección pasiva → análisis de encabezados de respuesta, Cookie, HTML, JS
2. Sondeo activo → rutas predeterminadas, provocar errores, acceso a archivos de configuración
3. Fijación de versión → precisión hasta versión mayor.menor.parche
4. Coincidencia de CVE → consulta en NVD/Snyk/GitHub Advisory
```

### 3.2 Búsqueda de CVE y verificación de PoC

**Fuentes de datos de CVE**

| Fuente de datos | URL | Características |
|--------|-----|------|
| NVD | nvd.nist.gov | Base de datos oficial de CVE, puntuación CVSS |
| GitHub Advisory | github.com/advisories | Vulnerabilidades de proyectos de código abierto, con enlaces a PoC |
| Snyk | snyk.io/vuln | Coincidencia precisa a nivel de dependencia |
| Exploit-DB | exploit-db.com | PoC y EXP verificados |
| PacketStorm | packetstormsecurity.com | Avisos de seguridad y código de explotación |
| ChangeLog del framework | Notas de versión oficiales del framework | Detalles de correcciones de seguridad |

**Flujo general de verificación de CVE**

```
1. Comparación de versión
   Confirmar número de versión → consultar el rango de versiones afectadas del CVE → confirmar si está dentro del rango afectado

2. Reproducción de PoC
   a. Buscar PoC públicos (GitHub/Exploit-DB/blogs de seguridad)
   b. Comprender el principio de la vulnerabilidad (el diff del parche es el mejor material)
   c. Construir la petición en el entorno de pruebas para verificar
   d. Nota: en entornos de producción solo verificar la condición de disparo, no ejecutar Payloads destructivos

3. Análisis del parche (deducción inversa de defensa L4)
   a. Comparar el diff de código antes y después de la corrección → entender qué se corrigió
   b. Deducir: en la lógica de procesamiento previa a la corrección, dónde existía el defecto
   c. Reflexionar: ¿la corrección es completa? ¿existe posibilidad de eludir la corrección?
```

### 3.3 Clasificación de superficies de ataque comunes en frameworks

| Tipo de superficie de ataque | Método de detección general | Patrón de vulnerabilidad típico |
|-----------|-------------|-------------|
| **Bypass de rutas/middleware** | Pruebas de normalización de rutas: `//path`, `/./path`, `/%2e/path`, variantes de mayúsculas/minúsculas, falsificación de encabezados especiales | Bypass de autenticación, omisión de autorización |
| **Inyección de plantillas/renderizado** | Inyectar sintaxis de plantilla en parámetros: `{{7*7}}`(Jinja2), `${7*7}`(Thymeleaf), `<%= 7*7 %>`(ERB) | SSTI→RCE |
| **Deserialización** | Identificar el formato serializado (`ac ed 00 05`/`O:`/`rO0AB`), enviar datos serializados maliciosos | RCE por deserialización en Java/PHP/Python |
| **Server Actions/RPC** | Interceptar llamadas RPC específicas del framework, analizar identificadores de endpoint, llamar directamente eludiendo la validación del frontend | CSRF, bypass de validación de entrada |
| **Inyección SSR/RSC** | Interceptar y modificar parámetros de renderizado del lado del servidor (como `_rsc`/`__data`/`loader`), construir Payloads anómalos | Ejecución de código en el servidor |
| **Fuga de archivos de configuración** | Recorrer rutas de configuración comunes: `.env`, `web.config`, `application.yml`, `settings.py` | Fuga de claves/credenciales |
| **Endpoints de depuración** | Verificar el modo de depuración del framework: `/debug`, `/_debug`, `/__inspect`, `/graphql`(introspection) | Fuga de información→RCE |
| **Contaminación de prototipos (JS)** | Inyectar en el cuerpo de la petición JSON `{"__proto__":{"isAdmin":true}}` o `{"constructor":{"prototype":{"x":1}}}` | Escalada de privilegios, DoS |
| **Envenenamiento de caché** | Manipular encabezados relacionados con la clave de caché (`X-Forwarded-Host`/`X-Original-URL`), verificar si la respuesta queda cacheada | XSS almacenado, phishing |

### 3.4 Checklist general de seguridad de frameworks

```
[ ] Confirmar la versión exacta del framework y todas sus dependencias
[ ] Consultar los CVE correspondientes en NVD/Snyk/GitHub Advisory
[ ] Verificar que todos los CVE de alto riesgo (CVSS≥7.0) estén corregidos
[ ] Verificar si el Source Map está deshabilitado
[ ] Verificar si el modo de depuración está desactivado
[ ] Verificar si la página de error filtra stack trace/rutas/versión
[ ] Verificar si las rutas de configuración predeterminadas son accesibles
[ ] Verificar si la autenticación de middleware/rutas puede eludirse mediante variantes de ruta
[ ] Verificar si todos los endpoints de API requieren autenticación (probar eliminando Cookie/Token)
[ ] Verificar si los encabezados de seguridad están completos (CSP/HSTS/X-Frame-Options/X-Content-Type-Options)
[ ] Verificar si la protección CSRF cubre todas las operaciones que cambian estado
[ ] Verificar si los endpoints RPC/Action específicos del framework tienen autenticación independiente
```

---

*Basado en la base de vulnerabilidades WooYun (88,636 registros) + mejores prácticas de seguridad en la nube/cadena de suministro | Solo para investigación de seguridad y referencia defensiva*

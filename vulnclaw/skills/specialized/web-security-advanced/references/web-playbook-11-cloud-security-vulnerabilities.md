# Vulnerabilidades de seguridad en la nube
English: Cloud Security Vulnerabilities
- Entry Count: 4
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## SSRF en la nube para robar credenciales de metadatos
- ID: cloud-ssrf-metadata
- Difficulty: intermediate
- Subcategory: Ataques a IMDS
- Tags: seguridad en la nube, SSRF, AWS, GCP, Azure, IMDS, metadatos
- Original Extracted Source: original extracted web-security-wiki source/cloud-ssrf-metadata.md
Description:
Explota una vulnerabilidad SSRF para acceder al servicio de metadatos de instancia (IMDS) de servicios en la nube (AWS/GCP/Azure) y obtener credenciales IAM temporales. El atacante puede usar la Access Key obtenida para tomar control de recursos en la nube, logrando una escalada lateral desde una vulnerabilidad web hasta el entorno en la nube.
Prerequisites:
- El objetivo se ejecuta en un entorno de nube
- Existe una vulnerabilidad SSRF
- La instancia tiene asociado un rol IAM
Execution Outline:
1. 1. Sondeo del servicio de metadatos de AWS
2. 2. Explotación de metadatos de GCP/Azure
3. 3. Movimiento lateral usando las credenciales obtenidas
4. 4. Explotación profunda — fuga de datos S3/escalada de privilegios
## Explotación de configuración incorrecta de buckets S3
- ID: cloud-s3-misconfig
- Difficulty: beginner
- Subcategory: Seguridad de S3
- Tags: seguridad en la nube, S3, AWS, configuración incorrecta, fuga de datos
- Original Extracted Source: original extracted web-security-wiki source/cloud-s3-misconfig.md
Description:
Explota configuraciones incorrectas de control de acceso en buckets S3 de AWS (lectura/escritura/listado público) para obtener datos sensibles o insertar archivos maliciosos. Es común en hospedaje de sitios estáticos, almacenamiento de logs y buckets de respaldo, y puede provocar fuga de datos, manipulación del sitio web o ataques a la cadena de suministro.
Prerequisites:
- Se conoce el nombre del bucket S3 objetivo
- Acceso vía AWS CLI o HTTP
Execution Outline:
1. 1. Enumeración de nombres de buckets S3
2. 2. Enumeración de permisos
3. 3. Búsqueda de datos sensibles
4. 4. Verificación de la explotación (manipulación de sitio estático/XSS)
## Escalada de privilegios de AWS IAM
- ID: cloud-iam-escalation
- Difficulty: advanced
- Subcategory: Escalada de privilegios IAM
- Tags: seguridad en la nube, AWS, IAM, escalada de privilegios, Privilege Escalation
- Original Extracted Source: original extracted web-security-wiki source/cloud-iam-escalation.md
Description:
Tras haber obtenido credenciales de AWS con privilegios bajos, explota permisos excesivos en las políticas IAM (como iam:PassRole, lambda:CreateFunction, etc.) para escalar privilegios hasta administrador. Cubre más de 20 rutas conocidas de escalada de privilegios en AWS IAM.
Prerequisites:
- Se han obtenido credenciales de AWS
- La política IAM tiene permisos excesivos
Execution Outline:
1. 1. Enumerar los permisos actuales
2. 2. Escalada de privilegios mediante iam:PassRole + Lambda
3. 3. Otras rutas de escalada de privilegios
4. 4. Herramientas automatizadas de escalada de privilegios
## Escape de contenedores en Kubernetes
- ID: cloud-k8s-escape
- Difficulty: expert
- Subcategory: Seguridad de contenedores
- Tags: seguridad en la nube, Kubernetes, escape de contenedores, Docker, contenedor privilegiado
- Original Extracted Source: original extracted web-security-wiki source/cloud-k8s-escape.md
Description:
Partiendo de haber obtenido una shell dentro de un Pod de Kubernetes, explota configuraciones incorrectas (contenedor privilegiado, montaje de rutas del host, ServiceAccount con privilegios altos) para lograr el escape del contenedor y, posteriormente, tomar control del host o de todo el clúster de Kubernetes.
Prerequisites:
- Se ha obtenido una shell dentro del Pod
- El Pod tiene configuraciones incorrectas
Execution Outline:
1. 1. Reconocimiento del entorno del contenedor
2. 2. Escape de contenedor privilegiado
3. 3. Toma de control del clúster explotando el ServiceAccount
4. 4. Creación de un Pod privilegiado para obtener una reverse shell
</content>

# Vulnerabilidades de archivos
English: File Vulnerabilities
- Entry Count: 7
- Use this file to shortlist relevant payloads, then open the linked source markdown for the full workflow and commands.
## Bypass de subida de archivos
- ID: file-upload-bypass
- Difficulty: intermediate
- Subcategory: Subida de archivos
- Tags: upload, bypass, webshell
- Original Extracted Source: original extracted web-security-wiki source/file-upload-bypass.md
Description:
Técnicas de bypass de las restricciones de subida de archivos
Prerequisites:
- El objetivo tiene funcionalidad de subida de archivos
- Existen restricciones de subida
Execution Outline:
1. Bypass de extensión
2. Content-Type
3. Webshell disfrazada de imagen
4. Bypass con espacios
## Descarga arbitraria de archivos
- ID: file-download
- Difficulty: beginner
- Subcategory: Descarga
- Tags: file-download, lfi, leak
- Original Extracted Source: original extracted web-security-wiki source/file-download.md
Description:
Explota un defecto de control de ruta en la funcionalidad de descarga de archivos para descargar cualquier archivo sensible del servidor
Prerequisites:
- El objetivo tiene funcionalidad de descarga de archivos
- El parámetro de ruta del archivo es controlable
- El servidor no filtra estrictamente la ruta
Execution Outline:
1. Identificar la interfaz de descarga de archivos
2. Descarga de archivos sensibles mediante recorrido de rutas
3. Descarga del código fuente y configuración de la base de datos
4. Sondeo automatizado masivo de archivos sensibles
## Condición de carrera
- ID: file-competition
- Difficulty: advanced
- Subcategory: Race Condition
- Tags: race-condition, file-upload
- Original Extracted Source: original extracted web-security-wiki source/file-competition.md
Description:
Explota la condición de carrera (Race Condition) en el proceso de subida/procesamiento de archivos, ejecutando operaciones maliciosas dentro de la ventana de tiempo entre la verificación de seguridad y el uso del archivo
Prerequisites:
- El objetivo tiene funcionalidad de subida de archivos
- El servidor primero sube y luego verifica en su flujo de procesamiento
- Es posible acceder al archivo subido con alta concurrencia
- Se conoce la ruta de almacenamiento de archivos temporales
Execution Outline:
1. Identificar la ventana de condición de carrera
2. Explotación de la condición de carrera - subida y acceso concurrentes
3. Script de explotación de condición de carrera concurrente en Python
4. Escritura de .htaccess mediante condición de carrera
## Recorrido de rutas
- ID: file-traversal
- Difficulty: beginner
- Subcategory: Traversal
- Tags: traversal, file
- Original Extracted Source: original extracted web-security-wiki source/file-traversal.md
Description:
Explota secuencias de recorrido de rutas (../) para superar las restricciones de directorio en el acceso a archivos, leyendo o escribiendo archivos arbitrarios fuera de la raíz web
Prerequisites:
- El objetivo tiene funcionalidad de lectura/inclusión de archivos
- El parámetro de ruta del archivo es controlable
- El filtrado de rutas del servidor no es estricto
Execution Outline:
1. Prueba básica de recorrido de rutas
2. Bypass del filtro de rutas mediante codificación
3. Recorrido de rutas específico de Windows
4. Escalada de LFI a RCE
## Zip Slip
- ID: file-zip-slip
- Difficulty: intermediate
- Subcategory: Zip
- Tags: zip-slip, file, rce
- Original Extracted Source: original extracted web-security-wiki source/file-zip-slip.md
Description:
Explota el recorrido de rutas en un archivo comprimido (ZIP/TAR) maliciosamente construido para lograr escritura de archivos arbitraria, sobrescribiendo archivos críticos del servidor o escribiendo una webshell
Prerequisites:
- El objetivo tiene funcionalidad de subida y descompresión automática de archivos ZIP/TAR
- La biblioteca de descompresión no filtra el recorrido de rutas en el nombre de archivo
- Se conoce la ruta de la raíz web u otros directorios críticos
Execution Outline:
1. Sondear la funcionalidad de subida y descompresión de ZIP
2. Construir un archivo comprimido malicioso de Zip Slip
3. Subir y verificar el Zip Slip
4. Variante de Zip Slip con archivos TAR
## Bypass de tipo MIME
- ID: file-mime
- Difficulty: beginner
- Subcategory: MIME
- Tags: mime, bypass
- Original Extracted Source: original extracted web-security-wiki source/file-mime.md
Description:
Falsifica el tipo MIME (Content-Type) para eludir la verificación de tipo de la subida de archivos y subir un archivo ejecutable malicioso
Prerequisites:
- El objetivo tiene funcionalidad de subida de archivos
- El servidor determina el tipo de archivo únicamente por el Content-Type
- Se conocen los tipos MIME permitidos por el objetivo
Execution Outline:
1. Sondear el mecanismo de verificación de tipo de archivo
2. Falsificación del tipo MIME para subir una webshell
3. Falsificación de Magic Bytes
4. Verificar el resultado de la subida
## Truncamiento por byte nulo
- ID: file-null-byte
- Difficulty: intermediate
- Subcategory: Null Byte
- Tags: null-byte, bypass
- Original Extracted Source: original extracted web-security-wiki source/file-null-byte.md
Description:
Explota el byte nulo (%00/\x00) para truncar la validación de la extensión del nombre de archivo, eludiendo las restricciones de lista blanca de subida de archivos
Prerequisites:
- El objetivo usa lista blanca para validar la extensión de archivo
- El lenguaje o biblioteca del backend es susceptible al truncamiento por byte nulo (PHP<5.3.4, versiones antiguas de Java)
- Existe un punto de truncamiento en la concatenación de rutas del servidor
Execution Outline:
1. Principio del truncamiento por byte nulo y detección del entorno
2. Truncamiento por byte nulo en la subida de archivos
3. Truncamiento por byte nulo en la inclusión de archivos
4. Alternativas modernas (PHP>=5.3.4)
</content>

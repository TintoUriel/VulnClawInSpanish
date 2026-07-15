<div align="center">

# VulnClaw 🦞

> *Herramienta CLI de pentesting impulsada por IA — habla en cristiano, rompe vulnerabilidades.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![OpenAI Compatible](https://img.shields.io/badge/API-OpenAI_Compatible-green)](https://platform.openai.com/)
[![MCP](https://img.shields.io/badge/Toolchain-MCP-orange)](https://modelcontextprotocol.io/)
[![PyPI](https://img.shields.io/badge/PyPI-v0.3.3-blueviolet)](https://pypi.org/project/vulnclaw/)
[![Security](https://img.shields.io/badge/Scope-Authorized_Only-red)](#declaración-de-seguridad)
[![AtomGitStars](https://atomgit.com/Unclecheng-li/VulnClaw/star/badge.svg)](https://atomgit.com/Unclecheng-li/VulnClaw)
<br>

🌐 **Versión en inglés**: [`README_EN.md`](README_EN.md)

**Este proyecto es un Agent de pentesting con IA que se ejecuta de forma independiente.**
<br>
Sitio oficial del proyecto: https://unclecheng-li.github.io/vulnclaw.com/
<br>

Basado en un Agent LLM + cadena de herramientas MCP + orquestación de Skills de pentesting,
combinado con modelos compatibles como OpenAI / Anthropic / MiniMax / DeepSeek, etc.,
entrada en lenguaje natural → flujo completo automatizado de «recopilación de información → descubrimiento de vulnerabilidades → explotación → generación de reportes».

[Inicio rápido](#inicio-rápido) · [Diseño de arquitectura](#arquitectura) · [Sistema de Skills](#skills-integradas)

</div>

---

## Qué puede hacer

Introduces lenguaje natural y la IA ejecuta automáticamente todo el flujo de pentesting:

```
Entrada del usuario: ayúdame a hacer un pentest a http://target.example.com

VulnClaw ejecuta automáticamente:
  Ronda 1:  Recopilación de información → fingerprinting, escaneo de puertos, enumeración de directorios
  Ronda 2:  Descubrimiento de vulnerabilidades → detección de puntos de inyección, CVE conocidos, fallos de configuración
  Ronda 3:  Explotación → verificación de PoC, obtención de privilegios
  Ronda 4:  Generación de reportes → reporte estructurado + script PoC en Python
```

<img width="1148" height="642" alt="image" src="https://github.com/user-attachments/assets/576e1cf6-25da-4969-864b-40e77d020dbf" />

<img width="2529" height="1136" alt="image" src="https://github.com/user-attachments/assets/9612c633-31f3-4062-8f56-ea5b4989fd50" />

Adecuado para pentesting autorizado, competencias CTF, enseñanza de seguridad, ejercicios de equipo rojo, entre otros escenarios.

---

## Características

- **Motor de resolución orientado a objetivos (predeterminado)** — abandona el flujo de trabajo de rondas fijas, y converge automáticamente usando como criterio de finalización «objetivo alcanzado / frontera de exploración agotada / presupuesto de seguridad»
- **Búsqueda en espacio de estados con grafo de pizarra (blackboard)** — modela el pentesting como una búsqueda desde el origin hasta el goal: Fact (hechos confirmados) + Intent (direcciones de exploración), estructuralmente evita "dar vueltas en el mismo sitio"
- **Compuerta antialucinación a nivel de evidencia** — las flags/conclusiones declaradas deben aparecer carácter por carácter en la salida real de las herramientas para ser aceptadas, evitando victorias falsas por flags inventadas de la nada
- **Impulsado por lenguaje natural** — describe la intención del pentesting en lenguaje humano, identifica automáticamente la fase y las herramientas
- **13 proveedores de LLM** — OpenAI / Anthropic / MiniMax / DeepSeek / Zhipu / Moonshot / Qwen / SiliconFlow / Doubao / Baichuan / StepFun / SenseTime / 01.AI, cambio con un solo clic
- **Cadena de herramientas MCP** — 4 servicios MCP: `fetch` / `memory` con implementación local lista para usar, `chrome-devtools` / `burp` conectados a servicios MCP externos para automatización de navegador y captura/repetición de tráfico HTTP
- **Almacenamiento nativo de evidencia de tráfico** — almacenamiento propio de VulnClaw para capturas: filtrado por alcance dentro de la ejecución, indexado en JSONL de tipo append + los paquetes originales de cada solicitud se guardan en `evidence/traffic/`. Herramientas integradas `traffic_list` / `traffic_view` / `traffic_repeat` / `traffic_sitemap` leen y escriben directamente sobre este almacenamiento (`traffic_repeat` admite repetición con sobrescritura); los reportes de vulnerabilidades verificadas incluyen directamente en línea la solicitud/respuesta original que las demuestra. El proxy mitmproxy y el backend de captura de navegador Playwright son dependencias opcionales (`pip install vulnclaw[traffic]`) y se activan según disponibilidad detectada; su integración automática en el ciclo de ejecución en sandbox se implementará junto con el PRD de sandbox/directorio de ejecución. Burp/chrome-devtools funcionan como capa interactiva opcional superpuesta, normalizada dentro del mismo almacenamiento
- **Núcleo de Agent de IA** — protocolo compatible con OpenAI + Tool Calling + ciclo de pentesting autónomo
- **Razonamiento estructurado + reflexión adaptativa** — hechos/restricciones/cadenas de ataque conocidos se consolidan de forma estructurada; los fallos se clasifican automáticamente y las estrategias de bypass de payload se escalan progresivamente en niveles L0-L4
- **Sistema de plugins de detección de vulnerabilidades** — runtime de plugins de bajo acoplamiento + plugin Web de solo lectura integrado, los resultados se incorporan automáticamente al reporte (`vulnclaw plugins`)
- **21 Skills de pentesting** — 7 centrales + 14 especializadas (incluye CTF Web/Crypto/Misc, osint-recon, secknowledge-skill), con 180 documentos de referencia
- **Herramientas de codificación/cifrado** — 29 operaciones (Base64/Hex/URL/AES/JWT/Morse, etc.), el LLM puede invocarlas con precisión, sin depender de adivinar
- **Ejecución de código Python** — herramienta integrada `python_execute`, útil para construir payloads y analizar respuestas; actualmente sigue siendo una capacidad experimental de alto riesgo, no debe considerarse un sandbox de aislamiento fuerte
- **Pentesting continuo** — ciclos periódicos (por defecto 100 rondas/ciclo × 10 ciclos = 1000 rondas), genera reportes automáticamente en cada ciclo, hasta que se termine manualmente
- **Control de visualización del proceso de razonamiento** — `think on/off` alterna con un solo comando la visualización/ocultación del proceso de pensamiento del LLM, desactivado por defecto, salida limpia mostrando solo conclusiones
- **Prompt de modo sandbox** — desbloquea capacidades de pruebas de seguridad de IA, exclusivo para escenarios de CTF / pentesting autorizado
- **Reporte automático y PoC** — genera reportes estructurados en Markdown y scripts PoC ejecutables en Python
- **Modo Web UI** — `vulnclaw web` inicia una interfaz Web local, opera todo el flujo de pentesting desde el navegador, por defecto en `127.0.0.1:7788`
- **Base de conocimiento de seguridad** — módulo de base de conocimiento integrado con datos semilla básicos, mantenible desde el CLI; la recuperación aumentada se está integrando gradualmente al flujo principal

---

## Actualización de arquitectura: de «flujo de trabajo de rondas fijas» a «resolución orientada a objetivos»

La versión anterior del pentesting autónomo era un **ciclo de rondas fijas** (se ejecutaba hasta agotar N rondas), lo que en modelos débiles caía fácilmente en bucles infinitos del tipo "solicitar repetidamente la misma página, decir que va a probar inyección pero nunca enviar el paquete". La nueva versión reconstruye el pentesting como una **búsqueda en espacio de estados**, y esto es el núcleo de esta refactorización.

### Ciclo de resolución de grafo de pizarra + OODA (motor predeterminado `solve`)

Se concibe el pentesting como una búsqueda dirigida desde el **origin** (objetivo) hasta el **goal** (obtener la flag / shell / confirmar una vulnerabilidad de alto riesgo), impulsada por dos primitivas:

| Primitiva | Significado |
|------|------|
| **Fact** | Un hecho objetivo confirmado por la salida real de una herramienta (el punto de apoyo de la exploración) |
| **Intent** | Una dirección de exploración declarada (un paso aún no ejecutado), que parte de un Fact y, al concluir, produce un nuevo Fact |

Estructura del ciclo (`vulnclaw/agent/solver.py`):

```
REASON (lee todo el grafo) → ¿objetivo alcanzado? / propone nueva dirección de exploración / no propone nada
        │
EXPLORE (toma un Intent) → lo ejecuta realmente con herramientas → escribe la conclusión confirmada como un nuevo Fact
        │
Finalización: objetivo alcanzado / frontera de exploración agotada (Reason ya no propone direcciones) / se alcanza el presupuesto de seguridad
```

**Por qué estructuralmente se evita dar vueltas en círculos**: una vez que "la página de inicio es un formulario de login" se convierte en un Fact, Reason ya no volverá a proponer "revisar la página de inicio", sino que propondrá "probar inyección SQL"; cada Intent se toma una sola vez y concluye una sola vez, marcándose como `concluded`/`abandoned`, **es imposible repetirlo**. La finalización está orientada por el objetivo, ya no se cuentan rondas fijas.

### Compuerta antialucinación a nivel de evidencia

Los modelos débiles a menudo inventan flags de la nada. El nuevo motor registra en `solve()` **toda la salida real de las herramientas** (cuerpos de respuesta HTTP, salida de `python_execute`) como única evidencia confiable:

- **Compuerta de conclusión**: si la flag declarada en la conclusión de Explore no aparece carácter por carácter en la salida real de la herramienta → se determina como alucinación, se descarta y se marca `[no verificado]`.
- **Compuerta de finalización**: cuando Reason declara "objetivo alcanzado", si el objetivo requiere una flag pero la salida real nunca contuvo ninguna → se rechaza la finalización y se continúa explorando.
- **Convergencia inmediata**: en cuanto se obtiene una flag verificada por evidencia, se finaliza de inmediato, sin rondas de verificación vacías adicionales.

> Este mecanismo es especialmente amigable con modelos débiles: el antiguo ciclo de rondas fijas caía fácilmente en bucles vacíos de solicitudes repetidas, mientras que «orientado a objetivos + antialucinación por evidencia» obliga al Agent a acercarse al objetivo paso a paso usando salida real de herramientas, y rechaza cualquier "finalización" sin respaldo de evidencia.

### Razonamiento estructurado + reflexión adaptativa

- **Capa de estado de razonamiento** (`reasoning_state.py`): hechos conocidos (con nivel de confianza), obstáculos de razonamiento (WAF/filtros, etc.), cadenas de ataque candidatas, consolidados de forma estructurada e inyectados en el prompt.
- **Motor de reflexión** (`reflexion.py`): los fallos se clasifican automáticamente (limitación de entorno/ruta incorrecta/parámetro incorrecto/información insuficiente), y las estrategias de bypass de payload se escalan progresivamente en **niveles L0-L4** (original → codificación URL → comentario de doble escritura → Unicode/hex → ofuscación multicapa/cambio de superficie de ataque), el modo persistent conserva la memoria de fallos entre ciclos.

### Sistema de plugins de detección de vulnerabilidades

Runtime de plugins de bajo acoplamiento (`vulnclaw/plugins/`) + plugin Web de solo lectura integrado (encabezados de seguridad HTTP / JWT / análisis de endpoints JS), los resultados de los plugins pueden deduplicarse y fusionarse en `SessionState.findings` para entrar al flujo de reportes.

> Para volver al antiguo motor de rondas fijas: `vulnclaw config set session.engine rounds`

---

## Inicio rápido

### Instalación

```bash
# Instalar desde PyPI (recomendado)
pip install vulnclaw

# Instalar desde el código fuente
git clone https://github.com/Unclecheng-li/VulnClaw.git
cd VulnClaw
pip install -e .
```

### Ejecución con Docker (opcional)

La imagen ya incluye la Web UI y el runtime necesario para los servicios MCP predeterminados (`npx` / `uvx`); todo el estado (configuración, sesiones, objetivos, reportes) se persiste en el volumen `/data`.

```bash
cp .env.example .env          # completa VULNCLAW_LLM_API_KEY, etc.
docker compose up --build      # construye la imagen e inicia la Web UI
# abre http://127.0.0.1:7788
```

También puedes ejecutar un comando CLI específico con docker puro:

```bash
docker run --rm -it \
  -e VULNCLAW_LLM_API_KEY=sk-your-key-here \
  -v vulnclaw-data:/data \
  vulnclaw:latest scan <target>
```

> ⚠️ El `localhost` dentro del contenedor apunta al propio contenedor. Para escanear servicios del host, usa `host.docker.internal`; para escanear otros contenedores, comparte la red y accede por el nombre del contenedor. Más detalles en [DOCKER.md](DOCKER.md).

### Inicio en cuatro pasos

```bash
# 1. Elige el proveedor (rellena automáticamente Base URL y nombre del modelo)
vulnclaw config provider minimax   (o openai/anthropic/deepseek/zhipu/moonshot/qwen/siliconflow)

# 1.2 (opcional) personaliza Base URL o nombre del modelo
vulnclaw config set llm.base_url https://your-own-api.example.com/v1 
vulnclaw config set llm.model your-model-name

# 2. Configura la API Key
vulnclaw config set llm.api_key sk-your-key-here
#    — o usa el inicio de sesión con suscripción ChatGPT (sin necesidad de API Key):
#      vulnclaw login   (inicio de sesión por navegador; ver docs/keyless-auth.md, presta atención a los riesgos de ToS)

# 3. Predeterminado: abre el CLI / REPL original
vulnclaw

# 4. Opcional: abre el panel de trabajo TUI
vulnclaw tui
```

### Verificación del entorno

```bash
vulnclaw doctor
```

Ejemplo de salida:

```
🦞 Verificación del entorno de VulnClaw

  Python: 3.14.4
  Node.js: v24.14.1
  npx: instalado
  nmap: instalado

Configuración LLM:
  Provider: openai
  Auth Mode: static
  Credentials: configurado
  Base URL: https://api.openai.com/v1
  Model: gpt-4o

Servicios MCP:
  fetch: habilitado [P0]
  memory: habilitado [P0]
  ...

✅ Entorno listo, ejecuta vulnclaw para comenzar
```

---

## Referencia rápida de comandos CLI

`vulnclaw --help` muestra todos los comandos:

```bash
$ vulnclaw --help

🦞 VulnClaw — AI-powered penetration testing CLI

 Usage: vulnclaw [OPTIONS] COMMAND [ARGS]...

 Options:
   --version  Show version and exit.
   --help     Show this message and exit.

 Commands:
   run           🚀 Pentesting de flujo completo con un clic
   persistent    🔄 Pentesting continuo (100 rondas/ciclo)
   recon         🔍 Solo fase de recopilación de información
   scan          🔎 Ejecutar fase de escaneo de vulnerabilidades
   exploit       💥 Ejecutar fase de explotación
   report        📝 Generar reporte a partir del registro de sesión
   repl          💬 Iniciar la interfaz REPL clásica interactiva
   config        ⚙️  Gestionar la configuración (set/get/list/provider)
   init          🔧 Inicializar configuración
   doctor        🏥  Verificar el entorno de ejecución
   tui           🖥️  Abrir el panel de trabajo TUI en terminal
   web           🌐 Iniciar la Web UI local
```

### Detalle de comandos

| Comando | Descripción | Ejemplo |
|------|------|------|
| `vulnclaw` | Abre por defecto la interfaz interactiva CLI / REPL original | `vulnclaw` |
| `vulnclaw tui` | Abre explícitamente el panel de trabajo TUI en terminal | `vulnclaw tui` / `vulnclaw tui --target target.com` |
| `vulnclaw repl` | Inicia la interfaz REPL clásica interactiva | `vulnclaw repl` |
| `vulnclaw solve <target>` | Resolución orientada a objetivos (sin rondas fijas, se detiene al alcanzar el objetivo) | `vulnclaw solve target.com --goal "obtener flag"` |
| `vulnclaw run <target>` | Pentesting de flujo completo con un clic (por defecto usa el motor solve) | `vulnclaw run 192.168.1.1` |
| `vulnclaw persistent <target>` | Pentesting continuo (100 rondas/ciclo) | `vulnclaw persistent 192.168.1.1` |
| `vulnclaw recon <target>` | Solo recopilación de información (sin explotar vulnerabilidades) | `vulnclaw recon target.com` |
| `vulnclaw scan <target>` | Fase de escaneo de vulnerabilidades | `vulnclaw scan target.com --ports 80,443` |
| `vulnclaw exploit <target>` | Fase de explotación | `vulnclaw exploit target.com --cve CVE-2024-1234` |
| `vulnclaw report <session>` | Genera reporte a partir del JSON de sesión | `vulnclaw report session_xxx.json` |
| `vulnclaw config set <key> <value>` | Establece un elemento de configuración | `vulnclaw config set llm.api_key sk-xxx` |
| `vulnclaw config get <key>` | Consulta un elemento de configuración | `vulnclaw config get llm.model` |
| `vulnclaw config list` | Lista toda la configuración | `vulnclaw config list` |
| `vulnclaw config provider <name>` | Cambia el proveedor LLM | `vulnclaw config provider minimax` |
| `vulnclaw init` | Inicializa el archivo de configuración | `vulnclaw init` |
| `vulnclaw doctor` | Verifica el entorno de ejecución | `vulnclaw doctor` |
| `vulnclaw plugins list` | Lista los plugins de detección de vulnerabilidades | `vulnclaw plugins list --stage discovery` |
| `vulnclaw plugins info <id>` | Consulta los metadatos de un plugin | `vulnclaw plugins info builtin.web.headers` |
| `vulnclaw plugins run <id>` | Ejecuta un plugin (solo analiza los datos de entrada) | `vulnclaw plugins run builtin.web.headers --input headers.json --session s.json` |
| `vulnclaw web` | Inicia la Web UI local | `vulnclaw web` / `vulnclaw web --port 8080` |

### Panel de trabajo TUI

`vulnclaw tui` es el punto de entrada opcional al panel de trabajo TUI en terminal. Muestra en la terminal el objetivo autorizado, el modo de verificación, la vista general de ejecución, los límites de seguridad, la vista previa de comandos, el estado histórico, los reportes y los diagnósticos de entorno en línea, permitiendo al usuario confirmar el alcance antes de iniciar la tarea.

```bash
vulnclaw tui
vulnclaw tui --target https://target.example --mode quick --only-port 443
vulnclaw tui --dry-run --target https://target.example --mode deep --only-path /admin
```

Por defecto `vulnclaw` sigue entrando al CLI / REPL original; solo entrando explícitamente `vulnclaw tui` se accede al TUI.
La vista general de ejecución lee las instantáneas históricas, cantidad de riesgos, restricciones persistentes y número de bloqueos por restricción del objetivo seleccionado, ayudando al usuario a confirmar que el contexto no se ha degradado antes de continuar las pruebas.
En "Configurar alcance de pruebas" del TUI se pueden editar directamente las acciones permitidas y prohibidas, por ejemplo permitir solo `recon,scan`, o prohibir `exploit,post_exploitation`.

### Gestión de configuración

```bash
# Ver todos los proveedores y cambiar
vulnclaw config provider --list    # ver todos los proveedores disponibles
vulnclaw config provider minimax   # cambiar a MiniMax

# Configuración manual (modo custom)
vulnclaw config set llm.base_url https://your-api.com/v1
vulnclaw config set llm.model your-model-name
vulnclaw config set llm.api_key sk-your-key
```

---

## Modos de uso

### Modo uno: interacción CLI / REPL original (predeterminado)

```bash
$ vulnclaw
```

Al iniciar sin parámetros se entra a la interfaz interactiva 🦞 original, dialogando en lenguaje natural:

```
🦞 vulnclaw> haz un pentest a 192.168.1.100, este es mi laboratorio autorizado

[*] Entrando al modo de pentesting autónomo, presiona Ctrl+C para interrumpir en cualquier momento
── Ronda 1 ──
  [+] Objetivo: 192.168.1.100
  [+] Puertos abiertos: 22, 80, 443, 8080
```

### Modo dos: panel de trabajo TUI (activación explícita)

```bash
$ vulnclaw tui
```

El TUI primero muestra el objetivo, el modo de verificación, la vista general de ejecución y los límites de seguridad, permitiéndote confirmar el alcance autorizado antes de iniciar la tarea:

```text
Panel de trabajo TUI de VulnClaw

Objetivo autorizado        https://example.com
Modo de verificación        Sondeo rápido / recon
Vista general de ejecución  Instantáneas históricas, cantidad de riesgos, restricciones persistentes, bloqueos por restricción
Límites de seguridad        Solo probar puerto 443, prohibido exploit/persistent/post_exploitation

1 Configurar objetivo autorizado
2 Seleccionar modo de verificación
3 Configurar alcance de pruebas
4 Iniciar verificación de seguridad autorizada
8 Configuración de modelo/API
```

Formas de inicio habituales:

```bash
vulnclaw tui
vulnclaw tui --target https://target.example --mode quick --only-port 443
vulnclaw tui --dry-run --target https://target.example --mode deep --only-path /admin
```

El menú 3 "Configurar alcance de pruebas" permite editar host, puertos, rutas, exclusiones, acciones permitidas y prohibidas; estos límites se incluyen en la confirmación previa al inicio y en el comando de tarea real.
El menú 7 "Entrada de diagnóstico del entorno" muestra dentro del TUI un resumen de Python, Node/npx/uvx/nmap, configuración LLM y servicios/herramientas MCP; para el detalle completo, ejecuta `vulnclaw doctor`.
El menú 8 "Configuración de modelo/API" permite cambiar directamente Provider, Base URL, Model y API Key; tras guardar, el panel de trabajo usa de inmediato la nueva configuración.

### Modo tres: subcomando REPL clásico

```bash
$ vulnclaw repl
```

Entra a la interfaz interactiva 🦞 clásica, dialogando en lenguaje natural:

```
🦞 vulnclaw> haz un pentest a 192.168.1.100, este es mi laboratorio autorizado

[*] Entrando al modo de pentesting autónomo, presiona Ctrl+C para interrumpir en cualquier momento
── Ronda 1 ──
  [+] Objetivo: 192.168.1.100
  [+] Puertos abiertos: 22, 80, 443, 8080
  [+] Fingerprint Web: Apache/2.4.62
── Ronda 2 ──
  [+] Se descubrió /manager/html (Tomcat Manager)
  [+] Coincide con CVE-202X-XXXX: bypass de autenticación de Apache Tomcat
── Ronda 3 ──
  [+] Verificación de vulnerabilidad exitosa

🦞 192.168.1.100 | Reporte> generar reporte de pentesting
[+] Reporte guardado en: ./reports/192.168.1.100_20260418.md
[+] Script PoC guardado en: ./pocs/CVE-202X-XXXX.py
```

#### Comandos integrados del REPL clásico

| Comando                  | Descripción                                       |
| --------------------- | ------------------------------------------ |
| `target <host>`       | Establece el objetivo del pentesting                           |
| `status`              | Consulta el estado actual (objetivo, fase, herramientas, visualización de razonamiento) |
| `tools`               | Lista las herramientas MCP disponibles actualmente                      |
| `think`               | Alterna mostrar/ocultar el proceso de razonamiento      |
| `think on` / `off`    | Controla con precisión la visualización del proceso de razonamiento      |
| `persistent`          | Inicia el pentesting continuo (100 rondas/ciclo, reporte automático) |
| `persistent <host>`   | Inicia el pentesting continuo sobre un objetivo específico                   |
| `clear`               | Limpia la sesión actual                       |
| `help`                | Muestra información de ayuda                       |
| `exit` / `quit` / `q` | Sale de VulnClaw                              |

#### Modo de pentesting autónomo

VulnClaw entra automáticamente en un ciclo de pentesting autónomo de múltiples rondas al detectar las siguientes palabras clave junto con un objetivo:

| Forma de activación | Ejemplo |
| -------- | ---- |
| Instrucción de pentesting | `haz un pentest a http://target.com` |
| CTF / buscar flag | `ayúdame a encontrar la flag en http://ctf.site` |
| Fuerza bruta / bypass | `haz fuerza bruta de contraseñas débiles en http://target.com` |
| **Activación explícita** | `objetivo: http://target.com, entra en modo de pentesting autónomo` |

> 💡 En el REPL, presiona `Ctrl+C` para interrumpir el ciclo autónomo en cualquier momento. Al cambiar de objetivo, el contexto de la sesión se reinicia automáticamente.

### Modo dos: modo de comando único

```bash
# Pentesting de flujo completo con un clic
vulnclaw run 192.168.1.100

# Pentesting continuo (100 rondas por ciclo, hasta 10 ciclos, reporte automático)
vulnclaw persistent 192.168.1.100

# Parámetros de ciclo personalizados
vulnclaw persistent 192.168.1.100 --rounds 200 --cycles 5

# Solo recopilación de información
vulnclaw recon 192.168.1.100

# Escaneo de vulnerabilidades (se puede indicar el puerto)
vulnclaw scan 192.168.1.100 --ports 80,443,8080

# Explotación (se puede indicar el CVE)
vulnclaw exploit 192.168.1.100 --cve CVE-2024-1234 --cmd id

# Generar reporte
vulnclaw report session.json
```

### Modo tres: modo de pentesting continuo

Adecuado para escenarios que requieren pentesting profundo de larga duración. VulnClaw se ejecuta en **ciclos periódicos**:

```
┌──────────────────────────────────────────────┐
│  Ciclo 1 (100 rondas) → reporte automático → continúa │
│  Ciclo 2 (100 rondas) → reporte automático → continúa │
│  Ciclo 3 (100 rondas) → reporte automático → continúa │
│  ...                                         │
│  Hasta Ctrl+C o alcanzar el número máximo de ciclos (10 por defecto) │
└──────────────────────────────────────────────┘
```

**Características**:
- **Mantiene el estado entre ciclos** — cada ciclo conserva todos los hallazgos, vulnerabilidades y registros de pasos anteriores
- **Reporte por ciclo** — al terminar cada ciclo se genera automáticamente un reporte Markdown independiente (con nuevas vulnerabilidades y resumen acumulado)
- **Interrupción flexible** — Ctrl+C interrumpe en cualquier momento, y aun así se genera el reporte del ciclo en curso
- **Descubrimiento incremental** — el reporte distingue entre "nuevo en este ciclo" y "total acumulado", permitiendo un seguimiento claro del progreso
- **Configurable** — el número de rondas por ciclo, el número máximo de ciclos y si se genera reporte automático son configurables

```bash
# Modo CLI
vulnclaw persistent 192.168.1.100              # 100 rondas/ciclo × 10 ciclos por defecto
vulnclaw persistent 192.168.1.100 -r 200 -c 5  # 200 rondas/ciclo × 5 ciclos
vulnclaw persistent 192.168.1.100 --no-report   # no genera reporte automático

# Modo TUI
vulnclaw tui --target 192.168.1.100 --mode continuous

# Modo REPL
🦞 vulnclaw> target 192.168.1.100
🦞 vulnclaw> persistent
# o directamente
🦞 vulnclaw> persistent 192.168.1.100
```

### Modo cuatro: modo Web UI

Opera todo el flujo de pentesting desde el navegador, adecuado para usuarios que prefieren una interfaz gráfica.

```bash
# Instalar las dependencias de Web
pip install 'vulnclaw[web]'

# Iniciar la Web UI (por defecto 127.0.0.1:7788)
vulnclaw web

# Puerto personalizado
vulnclaw web --port 8080

# Solo revisar la información de inicio (sin iniciar realmente el servicio)
vulnclaw web --dry-run
```

Tras iniciar, accede desde el navegador a `http://127.0.0.1:7788`.

> ⚠️ Por defecto solo se vincula a la dirección de loopback local. Para acceso remoto es necesario indicar explícitamente `--host 0.0.0.0 --allow-remote`; asegúrate de que el entorno de red sea seguro.

---

## Configuración de proveedores LLM

VulnClaw soporta APIs con protocolo compatible con OpenAI, con 13 preajustes de proveedores integrados y soporte para endpoints personalizados:

```bash
vulnclaw config provider --list    # ver todos los proveedores
vulnclaw config provider minimax   # cambiar con un clic
```

| Proveedor      | Comando                   | Modelo predeterminado              |
| ----------- | ---------------------- | --------------------- |
| OpenAI      | `provider openai`      | gpt-4o                |
| Anthropic Claude | `provider anthropic` | claude-sonnet-5   |
| MiniMax     | `provider minimax`     | MiniMax-M3            |
| DeepSeek    | `provider deepseek`    | deepseek-v4-pro       |
| Zhipu GLM    | `provider zhipu`       | glm-4.7               |
| Kimi        | `provider moonshot`    | kimi-k2.6             |
| Qwen (Tongyi)    | `provider qwen`        | qwen3-max             |
| SiliconFlow | `provider siliconflow` | DeepSeek-V4-Flash     |
| Doubao        | `provider doubao`      | Doubao-Seed-2.0-Pro   |
| Baichuan        | `provider baichuan`    | Baichuan4-Turbo       |
| StepFun    | `provider stepfun`     | step-3.5-flash        |
| SenseTime        | `provider sensetime`   | SenseNova-6.7-Flash-Lite |
| 01.AI (Yi)    | `provider yi`          | yi-lightning          |
| Personalizado      | `provider custom`      | rellenar manualmente              |

---

## Arquitectura

```
┌─────────────────────────────────────────────┐
│                VulnClaw CLI                  │
│  ┌─────────┐  ┌─────────┐  ┌────────────┐  │
│  │ Lenguaje │  │ Motor de │  │ Reporte y  │  │
│  │ natural  │  │ orquest. │  │   PoC      │  │
│  │  (capa)  │  │ de tareas│  │ (generador)│  │
│  └────┬────┘  └────┬────┘  └─────┬──────┘  │
│       └─────────────┼─────────────┘        │
│               ┌─────▼──────┐                │
│               │ LLM Agent  │                │
│               │(jailbreak+ │               │
│               │  Skill)    │               │
│               └─────┬──────┘                │
│               ┌─────▼──────┐                │
│               │ Capa de    │                │
│               │ orquest.   │                │
│               │ MCP (4 svc)│                │
│               └─────┬──────┘                │
│               ┌─────▼──────┐                │
│               │ Base de    │                │
│               │ conocim.   │                │
│               │ de seguri. │                │
│               └────────────┘                │
└─────────────────────────────────────────────┘
```

### Módulos centrales

| Módulo           | Archivo                                             | Descripción                                          |
| -------------- | ------------------------------------------------ | --------------------------------------------- |
| **Entrada CLI/TUI** | `cli/main.py` + `cli/tui.py`                   | Comandos Typer + CLI/REPL original por defecto + TUI explícito       |
| **Núcleo del Agent** | `agent/core.py`                                  | Punto de coordinación de AgentCore (tras la refactorización central conserva principalmente pocas responsabilidades de coordinación) |
| **Motor de resolución (predeterminado)** | `agent/solver.py` + `agent/blackboard.py`  | Ciclo OODA orientado a objetivos + grafo de pizarra Fact/Intent + compuerta antialucinación a nivel de evidencia |
| **Razonamiento / reflexión**   | `agent/reasoning_state.py` + `reflexion.py`   | Hechos/restricciones/cadenas de ataque estructurados + clasificación de fallos y escalado L0-L4 |
| **Sistema de plugins**   | `plugins/` (registry/runtime/web)                | Runtime de plugins de detección de vulnerabilidades de bajo acoplamiento + plugin Web de solo lectura integrado   |
| **Prompt dinámico** | `agent/prompts.py`                               | Identidad base + contrato central + Skill + lista de herramientas MCP    |
| **Ensamblaje de prompts** | `agent/system_prompt.py` + `prompt_context.py`  | Ensamblaje del system prompt / contexto de ronda / resumen de ataque |
| **Análisis de entrada**   | `agent/input_analysis.py`                        | Identificación de objetivo, fase, extracción de pistas de vulnerabilidad del usuario          |
| **Anti-bucle infinito / CTF** | `agent/anti_loop.py` + `ctf_mode.py`        | Señal de finalización, ruta de ataque, objetivos fallidos, máquina de estados de flag      |
| **Estado de sesión**   | `agent/context.py`                               | Seguimiento de fase + hallazgos de vulnerabilidad + registro de pasos                |
| **Contexto de Skill / KB** | `agent/skill_context.py` + `kb_context.py` | Selección de Skill e inyección de prompt de base de conocimiento |
| **Herencia de estado de objetivo** | `target_state/store.py`                        | Consolidación de resultados del mismo objetivo, recuperación, instantáneas, rollback, reporte de objetivo |
| **Orquestación MCP**   | `mcp/registry.py` + `lifecycle.py` + `router.py` | Registro de servicios + ciclo de vida + enrutamiento de lenguaje natural → herramientas       |
| **Despacho de Skill** | `skills/loader.py` + `dispatcher.py`             | Skill en formato de directorio + despacho dinámico de intenciones CTF/SRC/AI/Web etc. |
| **Herramientas de codificación** | `skills/crypto_tools.py`                         | 29 operaciones de codificación/cifrado, registradas como herramientas integradas del Agent  |
| **Gestión de configuración**   | `config/schema.py` + `settings.py`               | Modelos Pydantic + persistencia YAML + 13 preajustes de Provider |
| **Generación de reportes**   | `report/generator.py` + `poc_builder.py`         | Reporte Markdown + plantilla PoC en Python               |
| **Base de conocimiento de seguridad** | `kb/store.py` + `retriever.py`                   | Almacenamiento JSON + recuperación de CVE/técnicas/herramientas                 |

---

## Cadena de herramientas MCP

| Servicio MCP | N.º de herramientas | Modo | Uso | Estado |
|---|---|---|---|---|
| fetch | 1 | Local (httpx) | Solicitudes HTTP, pruebas de API | Listo para usar |
| memory | 2 | Local (JSON) | Memoria de contexto, persistencia de estado | Listo para usar |
| chrome-devtools | 31+ | stdio MCP | Automatización de navegador, capturas de pantalla, ejecución de JS | Requiere despliegue |
| burp | Varias | stdio MCP | Captura HTTP, repetición, escaneo de vulnerabilidades | Requiere despliegue |

> Además hay 5 herramientas de Agent integradas (`python_execute` + `nmap_scan` + `crypto_decode` + `brute_force_login` + `load_skill_reference`), invocables sin necesidad de MCP.

### Despliegue de Chrome DevTools MCP

[Repositorio: ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) — más de 31 herramientas, cubre clic/formularios/capturas de pantalla/ejecución de JS/monitoreo de red/análisis de rendimiento

**Prerrequisitos**: Node.js LTS (v20+) + navegador Chrome

```bash
# Paso 1: iniciar la depuración remota de Chrome
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\tmp\chrome-debug
# Linux/Mac
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

# Paso 2: habilitar la configuración de VulnClaw (se descarga automáticamente vía npx, sin instalación manual)
vulnclaw config set mcp.servers.chrome-devtools.enabled true
```

La configuración de VulnClaw ya incluye `npx -y chrome-devtools-mcp@latest`; al habilitarse se conecta automáticamente. Si necesitas indicar una dirección de depuración de Chrome específica, edita `~/.vulnclaw/config.yaml`:

```yaml
mcp:
  servers:
    chrome-devtools:
      enabled: true
      transport:
        type: stdio
        command: npx
        args: ["-y", "chrome-devtools-mcp@latest", "--browser-url=http://127.0.0.1:9222"]
```

### Despliegue de Burp Suite MCP

[Repositorio: PortSwigger/mcp-server](https://github.com/PortSwigger/mcp-server) — extensión MCP oficial, soporta protocolos SSE + Stdio

**Prerrequisitos**: Java 11+ + Burp Suite Professional

```bash
# Paso 1: clonar y construir
git clone https://github.com/PortSwigger/mcp-server.git burp-mcp
cd burp-mcp
./gradlew embedProxyJar    # Windows: gradlew.bat embedProxyJar
# Artefacto: build/libs/burp-mcp-all.jar

# Paso 2: cargar en Burp Suite
# Burp → Extensions → Add → Type: Java → selecciona burp-mcp-all.jar

# Paso 3: en la pestaña MCP de Burp marca "Enabled" (escucha por defecto en 127.0.0.1:9876)

# Paso 4: habilitar la configuración de VulnClaw
vulnclaw config set mcp.servers.burp.enabled true
```

Se recomienda copiar el JAR a una ubicación fija y actualizar la configuración:

```yaml
mcp:
  servers:
    burp:
      enabled: true
      transport:
        type: stdio
        command: java
        args: ["-jar", "~/.vulnclaw/tools/burp-mcp-all.jar", "--sse-url", "http://127.0.0.1:9876"]
```

> Ver instrucciones de despliegue detalladas en [docs/mcp-deployment.md](docs/mcp-deployment.md)

---

## Skills integradas

### Skills centrales (7)

| Skill             | Descripción               |
| ----------------- | ------------------ |
| pentest-flow      | Orquestación del flujo completo de pentesting |
| recon             | Flujo de recopilación de información       |
| vuln-discovery    | Flujo de descubrimiento de vulnerabilidades       |
| exploitation      | Flujo de explotación       |
| post-exploitation | Flujo de post-explotación         |
| reporting         | Flujo de generación de reportes         |
| waf-bypass        | Biblioteca de técnicas de bypass de WAF     |

### Skills especializadas (14)

| Skill                     | N.º de documentos de referencia | Descripción                                         |
| ------------------------- | ---------- | -------------------------------------------- |
| web-pentest               | 4          | Pentesting de aplicaciones Web                                 |
| android-pentest           | 9          | Pentesting de aplicaciones Android                                 |
| client-reverse            | 20         | Análisis de ingeniería inversa de cliente                               |
| web-security-advanced     | 34         | Seguridad Web avanzada (inyección, bypass, cadenas de explotación)           |
| ai-mcp-security           | 7          | Pruebas de seguridad de AI/MCP                              |
| intranet-pentest-advanced | 15         | Pentesting avanzado de intranet                                 |
| pentest-tools             | 18         | Referencia rápida de herramientas de pentesting                                 |
| rapid-checklist            | 3          | Lista de verificación rápida                                 |
| crypto-toolkit            | 3          | Codificación/cifrado (29 operaciones, registradas como herramientas integradas)   |
| **ctf-web**               | 9          | Base de conocimiento de ataques Web CTF (bypass PHP/RCE/SSTI/deserialización) |
| **ctf-crypto**            | 6          | Base de conocimiento de ataques de criptografía CTF (RSA/AES/ECC/PRNG/ataques de retículos) |
| **ctf-misc**              | 6          | Base de conocimiento de misceláneos CTF (PyJail/BashJail/cadenas de codificación/ingeniería inversa de VM) |
| **osint-recon**           | 7          | Recopilación de inteligencia de fuentes abiertas OSINT (modelo de cuatro dimensiones: servidor/sitio web/dominio/personal) |
| **secknowledge-skill**    | 39         | Base de conocimiento de pruebas de seguridad Web+AI, orientada a escenarios CTF/SRC/bug bounty masivo (metodologías WooYun/Xianzhi/GAARM/OWASP) |

Las Skills se despachan automáticamente según la entrada del usuario, sin necesidad de selección manual. Las Skills especializadas incluyen documentos detallados de metodología en el directorio `references/`, que el LLM puede cargar bajo demanda con la herramienta `load_skill_reference`.

`secknowledge-skill` se integra desde [`Pa55w0rd/secknowledge-skill`](https://github.com/Pa55w0rd/secknowledge-skill); los 38 documentos de `references/` del upstream han sido incorporados por completo, y se agregó adicionalmente `vulnclaw-ctf-src-routing.md` como guía de navegación de VulnClaw para escenarios CTF/SRC. Se activa con entradas de señal fuerte como `SRC`, `descubrimiento de vulnerabilidades`, `bug bounty masivo`, `GAARM`, `OWASP LLM/ASI/WSTG`, `Web+AI`, y se usa para cargar bajo demanda materiales de SQLi, XSS, RCE, SSRF, AI/MCP, Agent, matrices de riesgo y metodologías de prueba.

### Herramienta integrada de codificación/cifrado (crypto_decode)

`crypto_decode` está registrada como herramienta integrada del Agent, el LLM puede invocarla en cualquier contexto, sin depender de adivinar el resultado de la decodificación:

| Categoría     | Operaciones                                                                                     |
| -------- | ---------------------------------------------------------------------------------------- |
| Codificación   | base64, base32, base58, hex, url, html, unicode, rot13, caesar, morse (cada uno con encode/decode) |
| Hash     | md5, sha1, sha256, sha512                                                                |
| Cifrado/descifrado   | aes_encrypt, aes_decrypt (modo CBC, padding PKCS7)                                          |
| JWT      | jwt_decode, jwt_encode                                                                   |
| Reconocimiento automático | auto_decode — prueba todas las codificaciones comunes, devuelve el resultado coincidente                                              |

---

## Gestión de configuración

### Configuración por línea de comandos

```bash
vulnclaw config list                          # ver toda la configuración
vulnclaw config get llm.model                 # ver un elemento
vulnclaw config set llm.api_key sk-xx         # establecer la API Key
vulnclaw config set session.max_rounds 30     # establecer el número máximo de rondas del pentesting autónomo (15 por defecto)
vulnclaw config set session.stale_rounds_threshold 8  # establecer el umbral de detección de bucle infinito (5 por defecto)
vulnclaw config set session.show_thinking false # ocultar el proceso de razonamiento (también se puede con think off en el REPL)
```

### Elementos configurables

| Elemento de configuración                   | Valor predeterminado | Descripción                                     |
| ------------------------ | ------ | ----------------------------------------- |
| `llm.provider`           | openai | Proveedor LLM (13 integrados + custom)         |
| `llm.api_key`            | vacío     | API Key (auth_mode=static)              |
| `llm.auth_mode`          | static | `static` (api_key) o `oauth` (`vulnclaw login`) |
| `llm.chatgpt_auto_proxy` | false  | Inicia automáticamente el proxy puente de backend ChatGPT integrado         |
| `llm.base_url`           | según provider | URL base de la API, personalizable              |
| `llm.model`              | según provider | Nombre del modelo, personalizable                   |
| `llm.temperature`        | 0.1    | Temperatura de muestreo                                 |
| `llm.max_tokens`         | 4096   | Máximo de tokens de salida por solicitud                       |
| `session.engine`         | solve  | Motor autónomo: `solve` (orientado a objetivos, predeterminado) / `rounds` (antiguo de rondas fijas) |
| `session.solve_max_steps` | 40    | Límite máximo de seguridad de pasos de exploración de solve (respaldo, no una longitud fija de flujo) |
| `session.solve_max_intents` | 3   | Número máximo de nuevas direcciones de exploración que Reason puede proponer por vez        |
| `session.solve_max_tool_rounds` | 6 | Número máximo de rondas de llamadas a herramientas por exploración de cada Intent        |
| `session.max_rounds`     | 15     | Número máximo de rondas del antiguo motor `rounds` (se recomienda 10-50)  |
| `session.output_dir`     | ./vulnclaw-output | Directorio de salida de reportes                    |
| `session.report_format`  | markdown | Formato de reporte (markdown / html)            |
| `session.poc_language`   | python | Lenguaje de generación de PoC (python / bash)            |
| `session.show_thinking`  | false  | Muestra el proceso de razonamiento del LLM (contenido de la etiqueta think, oculto por defecto) |
| `session.persistent_rounds_per_cycle` | 100 | Número de rondas por ciclo en el pentesting continuo |
| `session.persistent_max_cycles` | 10 | Número máximo de ciclos del pentesting continuo (0=ilimitado) |
| `session.persistent_auto_report` | true | Genera reporte automático en cada ciclo del pentesting continuo |
| `session.stale_rounds_threshold` | 5 | Umbral de detección de bucle infinito — al alcanzar este número de rondas consecutivas sin nuevos hallazgos, se activa un cambio forzado de estrategia |

### Variables de entorno

| Variable                          | Descripción                   |
| ----------------------------- | ---------------------- |
| `VULNCLAW_LLM_PROVIDER`       | Nombre del proveedor LLM         |
| `VULNCLAW_LLM_API_KEY`        | API Key                |
| `VULNCLAW_LLM_AUTH_MODE`      | static / oauth         |
| `VULNCLAW_LLM_CHATGPT_AUTO_PROXY` | Proxy ChatGPT integrado  |
| `VULNCLAW_LLM_BASE_URL`       | URL base de la API           |
| `VULNCLAW_LLM_MODEL`          | Nombre del modelo               |
| `VULNCLAW_SESSION_MAX_ROUNDS`| Número máximo de rondas del pentesting autónomo       |
| `VULNCLAW_SESSION_STALE_ROUNDS_THRESHOLD` | Umbral de detección de bucle infinito |
| `VULNCLAW_SESSION_REASONING_STATE_ENABLED` | Interruptor del estado de razonamiento estructurado |
| `VULNCLAW_SESSION_REFLEXION_ENABLED` | Interruptor del motor de reflexión adaptativa |
| `VULNCLAW_SESSION_REFLEXION_MAX_SAME_VULN_FAILS` | Umbral de fallos consecutivos del mismo tipo de vulnerabilidad para activar reflexión |
| `VULNCLAW_SESSION_ESCALATION_MAX_LEVEL` | Límite máximo de escalado de payload (0-4) |
| `VULNCLAW_SESSION_PLUGIN_RUNTIME_ENABLED` | Interruptor del runtime de plugins |
| `VULNCLAW_SESSION_PLUGIN_MAX_REQUESTS_PER_TARGET` | Presupuesto de solicitudes de plugin por objetivo |

Prioridad: **variable de entorno > archivo de configuración > valor predeterminado integrado**

El archivo de configuración se encuentra en `~/.vulnclaw/config.yaml`.

---

## Registro de cambios

### v0.4.1

**Exploración paralela + motor de memoria + cadena de herramientas de recopilación de información + MCP streamable-http**

- **Exploración paralela de múltiples intents** — el motor solve admite explorar varias direcciones a la vez (por defecto max_parallel=3), una excepción en una dirección no afecta a las demás, cada intent tiene su propio buffer de evidencia y registro de llamadas a herramientas.
- **Motor de memoria del agent** — el blackboard agrega un registro de llamadas a herramientas (visible entre intents), la fase reason lista explícitamente las direcciones ya abandonadas y prohíbe volver a proponerlas, el contexto de explore incluye un resumen de "herramientas ya ejecutadas"; el mecanismo de checkpoint omite reason cuando el estado del grafo no cambió, evitando ciclos vacíos; se agregó deduplicación Jaccard como respaldo para direcciones abandonadas.
- **Optimización del criterio de conclude** — se relajó el estándar de "hay progreso" (descubrir una nueva interfaz o confirmar acceso no autorizado ahora cuentan como avance), ya no se descartan fácilmente hallazgos valiosos; se inyecta una instrucción de conclude override en el último paso para evitar ciclos vacíos; se agregó un respaldo de evidencia para evitar que conclude descarte por error exploraciones que sí tuvieron datos de retorno.
- **Compuerta de negación en el criterio de finalización** — cuando el modelo escribe conclusiones negativas como "no se alcanzó el criterio de finalización" en el campo complete, ya no se interpreta erróneamente como completado; se exige explícitamente el valor booleano complete=true + referencia a un evidence fact.
- **Recopilación de información JS (js_recon)** — captura la página y todos los archivos JS, extrae rutas de API / dominios relacionados / claves embebidas; descubre dinámicamente nombres de entidades en PascalCase y los combina con la ruta base y verbos CRUD para inferir interfaces ocultas; las interfaces recopiladas se someten automáticamente a pruebas de acceso no autorizado GET+POST.
- **Prueba de acceso no autorizado (unauth_test)** — solicitudes masivas sin credenciales, evaluación por código de estado/cuerpo de respuesta/tipo de contenido; soporta comparación diferencial con/sin token para confirmar el acceso no autorizado; omite automáticamente interfaces destructivas como delete/save/sms.
- **Enumeración de directorios (dir_enum)** — fuerza bruta concurrente de diccionario, con línea base de 404 e identificación de camuflaje global 200 (si una ruta aleatoria devuelve 200, se detiene automáticamente), filtrado por código de estado y longitud de respuesta.
- **Mapeo del espacio (space_search)** — consulta unificada con seis motores FOFA / Hunter / Quake / Shodan / ZoomEye / 0.zone, con engine=all se consultan en paralelo todos los motores con key configurada.
- **Enumeración de subdominios (subdomain_enum)** — agregación pasiva de mapeo del espacio + fuerza bruta DNS con diccionario integrado, deduplicación automática.
- **Soporte de MCP streamable-http** — soporta servidores MCP de transporte HTTP como Chrome DevTools MCP; conexión perezosa (no ocupa slot de sesión al iniciar); establece conexión y descubre herramientas automáticamente en la primera llamada; ante fallo de conexión, degrada a service_unavailable sin afectar el ciclo solve.
- **Corrección de nombres de herramientas Chrome MCP** — las herramientas placeholder se cambiaron por nombres reales de herramientas Chrome MCP (chrome_navigate / chrome_read_page / chrome_pentest_* etc.).
- Cuando una herramienta devuelve undefined ahora se marca como fallo en lugar de éxito silencioso; fact_seq / intent_seq continúan correctamente tras la recuperación de sesión; se agregó el bloque de configuración ReconConfig y el elemento de configuración solve_max_parallel.

### v0.4.0

**Núcleo: el motor autónomo se refactorizó de «flujo de trabajo de rondas fijas» a «resolución orientada a objetivos»**

- **Nuevo motor de resolución orientado a objetivos (predeterminado)** — ciclo OODA basado en el grafo de pizarra Fact/Intent, con criterio de finalización de «objetivo alcanzado / frontera de exploración agotada / presupuesto de seguridad», estructuralmente evita "dar vueltas en el mismo sitio"; nuevo comando `vulnclaw solve`, el modo autónomo de `run`/REPL ahora usa este motor por defecto (`session.engine=rounds` permite volver a la lógica antigua).
- **Nueva compuerta antialucinación a nivel de evidencia** — registra toda la salida real de herramientas como única evidencia confiable; la flag/finalización declarada debe aparecer carácter por carácter en la salida real para ser aceptada, de lo contrario se determina como alucinación y se continúa explorando; al obtener una flag verificada, se converge de inmediato.
- **Nuevo razonamiento estructurado + reflexión adaptativa** — los hechos conocidos (con nivel de confianza)/restricciones/cadenas de ataque se consolidan de forma estructurada e inyectan en el prompt; los fallos se clasifican automáticamente y las estrategias de bypass de payload se escalan progresivamente en niveles L0-L4, el modo persistent conserva la memoria de fallos entre ciclos.
- **Nuevo sistema de plugins de detección de vulnerabilidades** — runtime de plugins de bajo acoplamiento + plugin Web de solo lectura integrado (encabezados de seguridad HTTP / JWT / endpoints JS), los resultados se pueden deduplicar y fusionar en findings y en el flujo de reportes; nuevos comandos `vulnclaw plugins list/info/run`.
- **Corrección de #45, restricción errónea de herramientas** — las restricciones de acción ya no interpretan erróneamente los métodos HTTP (OPTIONS/POST) o el uso de `requests` como "explotación"; solo los payloads de ataque reales (SQLi/RCE/path traversal, etc.) cuentan como exploit; herramientas puramente locales como `load_skill_reference`/`crypto_decode` quedan exentas de la restricción de alcance.
- Nuevos elementos de configuración `session.engine` / `solve_*` / `reflexion_*` / `plugin_*`, todos con soporte de inyección por variable de entorno.

---

## Declaración de seguridad

**Fase de Alpha pública**: VulnClaw es software de Alpha pública orientado a pruebas de seguridad autorizadas, CTF, entornos experimentales y escenarios de investigación controlada; no debe usarse como medio de control de seguridad o mecanismo de autorización en entornos de producción. Lee [SECURITY.md](SECURITY.md) antes de usarlo.

VulnClaw se destina únicamente a **pruebas de seguridad autorizadas**. Antes de usar esta herramienta, asegúrate de que:

1. Has obtenido **autorización explícita** del sistema objetivo
2. El alcance de las pruebas ha sido **confirmado por escrito** con el propietario del objetivo
3. Cumples con las **leyes y reglamentos** locales

Realizar pentesting a un sistema sin autorización es ilegal. Los autores de esta herramienta no se hacen responsables del uso indebido.

---

## Licencia

[Licencia MIT](LICENSE)

---

## Únete a la comunidad

Intercambia, comparte y crece junto a más entusiastas de la seguridad

| Grupo de comunidad | Grupo de desarrolladores |
|:--:|:--:|
| Únete a la discusión y comparte, entérate de las últimas novedades y consejos de uso | Únete a nosotros para participar en contribuciones de código abierto y debates técnicos en profundidad |
| ![Grupo de comunidad de VulnClaw](assets/comunidad-vulnclaw-qr.jpg) | ![Grupo de desarrolladores de VulnClaw](assets/vulnclaw-desarrolladores-qr.png) |
| **Grupo QQ: 954402631** | **Grupo QQ: 1065858551** |

---

<div align="center">

> 🦞 **VulnClaw** — que cada pentesting tenga un método a seguir.

</div>

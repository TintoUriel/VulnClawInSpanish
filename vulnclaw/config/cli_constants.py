"""CLI shared data constants — extracted from cli/manual.py.

Moved here so that infrastructure-layer modules (e.g. skills/) can consume
CLI metadata without depending on the entry-layer cli/ package.

Modificado por: Nyaecho
Fecha de modificación: 2026-07-08
Motivo de la modificación: Eliminar la violación V5 — skills/flag_skills.py dependía
         inversamente de cli/manual.py; se extrajeron las constantes de datos
         compartidas a la capa de infraestructura config/.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManualTopic:
    """A CLI manual topic or command."""

    name: str
    summary: str
    usage: str
    flags: tuple[tuple[str, str], ...] = ()
    notes: tuple[str, ...] = ()
    examples: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()


ROOT_OPTIONS: tuple[tuple[str, str], ...] = (
    ("--help", "Muestra la ayuda breve de Typer para el comando raíz o el subcomando seleccionado."),
    ("--version", "Imprime la versión instalada de VulnClaw y termina."),
    ("--man, --manual", "Imprime este manual completo de la CLI y termina."),
)

COMMON_TASK_FLAGS: tuple[tuple[str, str], ...] = (
    (
        "--prompt TEXT",
        "Reemplaza por completo el prompt de tarea integrado. Úsalo cuando la intención del comando "
        "por defecto es cercana pero necesitas una redacción exacta, contexto de credenciales, una "
        "nota de laboratorio o un flujo de trabajo personalizado.",
    ),
    (
        "--only-port PORT",
        "Agrega una indicación de alcance estricta: solo este puerto TCP/UDP está en alcance. "
        "Los puertos válidos van de 1 a 65535.",
    ),
    (
        "--only-host HOST",
        "Restringe las pruebas a un solo host, incluso cuando una URL, CIDR, datos de reconocimiento "
        "o el historial de objetivos apunten a hosts relacionados.",
    ),
    (
        "--only-path PATH",
        "Restringe las pruebas web a una sola ruta, como /admin. Disponible en los comandos de tarea "
        "orientados a URL.",
    ),
    (
        "--blocked-host HOST",
        "Marca un host como explícitamente fuera de alcance. Las llamadas a herramientas hacia ese "
        "host se bloquean cuando VulnClaw puede inferir el destino.",
    ),
    (
        "--blocked-path PATH",
        "Marca una ruta como explícitamente fuera de alcance. Disponible en los comandos de tarea "
        "orientados a URL.",
    ),
    (
        "--allow-actions CSV",
        "Lista blanca de acciones separadas por comas. Los valores comunes son recon, scan, exploit, "
        "post_exploitation, report, run y persistent. Si se define, los comandos fuera de la lista "
        "blanca se bloquean antes de iniciar la tarea, y las comprobaciones de herramientas/fase "
        "continúan durante la ejecución.",
    ),
    (
        "--block-actions CSV",
        "Lista negra de acciones separadas por comas, usando los mismos nombres de acción que "
        "--allow-actions.",
    ),
    (
        "--resume / --no-resume",
        "Reanuda el historial de objetivos guardado por defecto. Usa --no-resume para una ejecución "
        "limpia que ignora el estado de objetivo almacenado.",
    ),
    (
        "--snapshot ID",
        "Reanuda desde una instantánea (snapshot) específica del estado de objetivo en lugar de la más reciente.",
    ),
)

ACTION_NAMES = (
    "recon",
    "scan",
    "exploit",
    "post_exploitation",
    "report",
    "run",
    "persistent",
)

TASK_COMMAND_NAMES = {"run", "persistent", "recon", "scan", "network-scan", "exploit"}

COMMANDS: tuple[ManualTopic, ...] = (
    ManualTopic(
        name="run",
        summary="Ejecuta el flujo de trabajo completo de pentest autorizado contra un objetivo.",
        usage="vulnclaw run TARGET [--scope full|web|api|mobile] [--output PATH] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Host, IP, URL u otro identificador de objetivo autorizado. Obligatorio."),
            (
                "--scope TEXT",
                "Enfoque de prueba de alto nivel. La redacción integrada reconoce full, web, api y "
                "mobile, pero el valor se pasa al prompt de la tarea, por lo que también son "
                "posibles etiquetas personalizadas.",
            ),
            (
                "--output PATH",
                "Después de la ejecución, genera un informe en PATH a partir del estado de objetivo "
                "guardado. Un sufijo .html escribe HTML; en caso contrario se usa el formato de "
                "informe configurado.",
            ),
        ),
        notes=(
            "Requiere credenciales de LLM configuradas (llm.api_key o auth_mode) antes de iniciar la tarea.",
            "Por defecto (session.engine=solve) esto ejecuta el bucle solve orientado a objetivos: sin "
            "un número fijo de rondas, acotado por session.solve_max_steps/solve_max_intents/"
            "solve_max_tool_rounds, y se detiene cuando se agota la frontera de exploración; es el "
            "mismo motor subyacente que `vulnclaw solve`. Define session.engine=rounds para usar en "
            "su lugar el bucle heredado auto_pentest de rondas fijas (acotado por session.max_rounds).",
            "Usa --allow-actions recon,scan cuando quieras una cobertura amplia pero sin explotación.",
        ),
        examples=(
            "vulnclaw run https://lab.example --scope web --allow-actions recon,scan",
            "vulnclaw run 10.10.10.5 --output reports/lab.md --no-resume",
        ),
    ),
    ManualTopic(
        name="solve",
        summary="Bucle solve orientado a objetivos, sin un número fijo de rondas.",
        usage=(
            "vulnclaw solve TARGET [--goal TEXT] [--max-steps N] [--max-intents N] "
            "[--max-tool-rounds N] [--resume/--no-resume] [--snapshot ID]"
        ),
        flags=(
            ("TARGET", "Host, IP, URL u otro identificador de objetivo autorizado. Obligatorio."),
            (
                "--goal TEXT",
                "Condición de éxito, por ejemplo 'capturar la flag' o 'obtener una shell'. Por "
                "defecto busca y verifica una flag/shell/vulnerabilidad de alto valor.",
            ),
            ("--prompt TEXT", "Descripción de tarea personalizada que reemplaza la generada automáticamente."),
            (
                "--max-steps N",
                "Límite de seguridad en pasos de exploración (no es una longitud de flujo fija; por defecto 40).",
            ),
            ("--max-intents N", "Número máximo de intents nuevos generados por paso de razonamiento (por defecto 3)."),
            (
                "--max-tool-rounds N",
                "Número máximo de rondas de llamadas a herramientas por exploración de intent (por defecto 4).",
            ),
            ("--resume / --no-resume", "Reanuda el historial de objetivos guardado por defecto."),
            ("--snapshot ID", "Reanuda desde una instantánea específica del estado de objetivo en lugar de la más reciente."),
        ),
        notes=(
            "A diferencia de run/persistent, solve no tiene un número fijo de rondas: busca en un "
            "grafo de Hechos/Intents desde el objetivo hacia la meta y se detiene al tener éxito o "
            "cuando ya no queda ningún camino.",
            "Este es el mismo motor que `run` usa por defecto (session.engine=solve); `solve` expone "
            "sus parámetros de ajuste directamente en la línea de comandos en lugar de mediante la configuración.",
        ),
        examples=(
            "vulnclaw solve https://lab.example --goal 'get a shell'",
            "vulnclaw solve 10.10.10.5 --max-steps 60 --max-intents 4",
        ),
    ),
    ManualTopic(
        name="persistent",
        summary="Ejecuta ciclos de pentest repetidos y, opcionalmente, escribe un informe después de cada ciclo.",
        usage="vulnclaw persistent TARGET [--rounds N] [--cycles N] [--no-report] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Objetivo autorizado. Obligatorio."),
            (
                "--rounds N, -r N",
                "Rondas por ciclo. 0 significa usar session.persistent_rounds_per_cycle de la configuración.",
            ),
            (
                "--cycles N, -c N",
                "Número máximo de ciclos. 0 significa usar session.persistent_max_cycles de la "
                "configuración; si ese valor de configuración también es 0, la ejecución no tiene "
                "límite hasta ser interrumpida.",
            ),
            ("--no-report", "Desactiva la generación normal de informes por ciclo persistente."),
        ),
        notes=(
            "El modo persistente es para ejecuciones de laboratorio o evaluación autorizadas y "
            "prolongadas, donde VulnClaw debe seguir ciclando entre reconocimiento, escaneo, "
            "verificación e informes.",
            "Usa Ctrl+C para interrumpir. El comando de todos modos imprime un resumen final.",
        ),
        examples=(
            "vulnclaw persistent https://lab.example --rounds 25 --cycles 4",
            "vulnclaw persistent 10.0.0.0/24 --allow-actions recon,scan --no-report",
        ),
    ),
    ManualTopic(
        name="recon",
        summary="Ejecuta solo reconocimiento, sin explotación.",
        usage="vulnclaw recon TARGET [COMMON TASK FLAGS]",
        flags=(("TARGET", "Host, IP, URL, CIDR o dominio a investigar. Obligatorio."),),
        notes=(
            "El prompt por defecto solicita reconocimiento autorizado sin explotación.",
            "Buen primer comando cuando solo quieres descubrimiento de activos, fingerprinting y notas.",
        ),
        examples=("vulnclaw recon example.com --only-host example.com",),
    ),
    ManualTopic(
        name="scan",
        summary="Ejecuta descubrimiento de vulnerabilidades sin explotación.",
        usage="vulnclaw scan TARGET [--ports PORTS] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Objetivo autorizado. Obligatorio."),
            (
                "--ports PORTS",
                "Lista o rango de puertos indicativo, como 80,443,8080. Esto es una guía para el "
                "prompt, no un interruptor exclusivo de nmap; usa network-scan para control directo "
                "del perfil de nmap.",
            ),
        ),
        notes=(
            "El prompt por defecto le pide a VulnClaw identificar vulnerabilidades sin explotación.",
            "Usa --block-actions exploit para una lista negra explícita además de la redacción del escaneo.",
        ),
        examples=("vulnclaw scan https://lab.example --ports 80,443 --block-actions exploit",),
    ),
    ManualTopic(
        name="network-scan",
        summary="Ejecuta descubrimiento de red basado en nmap y sondas de seguimiento seguras opcionales.",
        usage=(
            "vulnclaw network-scan [TARGET] [--profile adaptive|fast|thorough|stealth] "
            "[--ports PORTS] [--parallel-agents N]"
        ),
        flags=(
            (
                "TARGET",
                "Host, IP o CIDR opcional. Si se omite, VulnClaw intenta detectar la subred Wi-Fi "
                "conectada y escanear ese CIDR.",
            ),
            (
                "--profile TEXT",
                "Perfil de escaneo de nmap. adaptive usa el historial de objetivos y valores por "
                "defecto; fast favorece la velocidad; thorough amplía la cobertura; stealth reduce "
                "la intensidad del escaneo.",
            ),
            ("--ports PORTS", "Lista o rango de puertos para nmap, por ejemplo 22,80,443 o 1-1000."),
            (
                "--max-rounds N",
                "Rondas de seguimiento del agente después de nmap. 0 significa usar session.max_rounds.",
            ),
            (
                "--parallel-agents N",
                "Número de agentes hijos a desplegar en abanico entre las superficies descubiertas. "
                "1 desactiva el despliegue en abanico.",
            ),
            (
                "--parallel-depth N",
                "Número de oleadas de descubrimiento de agentes hijos cuando --parallel-agents es mayor que 1.",
            ),
            ("--worker-rounds N", "Rondas del agente por cada worker de superficie hijo."),
            (
                "--surface-limit N",
                "Máximo de superficies descubiertas consideradas para el despliegue en abanico de agentes hijos.",
            ),
            (
                "--safe-probes / --no-safe-probes",
                "Con las sondas seguras activadas, VulnClaw usa por defecto --allow-actions "
                "recon,scan y realiza únicamente sondas de verificación no destructivas después de "
                "nmap. Con --no-safe-probes, resume los eslabones débiles sin sondas de seguimiento.",
            ),
            ("--only-port PORT", "Restringe el análisis de seguimiento a un solo puerto."),
            ("--only-host HOST", "Restringe el análisis de seguimiento a un solo host."),
            ("--blocked-host HOST", "Excluye un host del análisis de seguimiento."),
            ("--allow-actions CSV", "Sobrescribe la lista blanca de acciones de sondas seguras."),
            ("--block-actions CSV", "Agrega una lista negra de acciones."),
            ("--resume / --no-resume", "Usa o ignora el historial de objetivos guardado."),
            ("--snapshot ID", "Reanuda desde una instantánea específica del estado de objetivo."),
        ),
        notes=(
            "Este es el comando a usar cuando quieres que nmap participe directamente.",
            "La validación de perfil integrada acepta adaptive, fast, thorough y stealth.",
        ),
        examples=(
            "vulnclaw network-scan --profile fast",
            "vulnclaw network-scan 192.168.56.0/24 --ports 22,80,443 --parallel-agents 3",
        ),
    ),
    ManualTopic(
        name="exploit",
        summary="Ejecuta una tarea autorizada enfocada en explotación.",
        usage="vulnclaw exploit TARGET [--cve CVE-ID] [--cmd CMD] [COMMON TASK FLAGS]",
        flags=(
            ("TARGET", "Objetivo autorizado. Obligatorio."),
            ("--cve CVE-ID", "Indica a VulnClaw que se enfoque en un CVE específico."),
            (
                "--cmd CMD",
                "Comando de verificación para hallazgos de tipo ejecución de comandos. Por defecto, id.",
            ),
        ),
        notes=(
            "Úsalo solo contra sistemas donde la explotación esté explícitamente autorizada.",
            "Los indicadores de alcance igualmente aplican y se verifican antes de iniciar el comando.",
        ),
        examples=(
            "vulnclaw exploit https://lab.example --cve CVE-2024-1234 --only-path /vulnerable",
        ),
    ),
    ManualTopic(
        name="report",
        summary="Genera un informe a partir de un archivo de sesión guardado o del historial de objetivos.",
        usage="vulnclaw report SESSION_JSON [--target] [--pdf] [--pdf-out PATH]",
        flags=(
            (
                "SESSION_JSON",
                "Ruta a un archivo JSON de sesión guardado. Con --target, este argumento se "
                "interpreta en su lugar como un nombre de objetivo.",
            ),
            (
                "--target",
                "Genera a partir del historial de estado de objetivo actual en lugar de un archivo JSON de sesión.",
            ),
            (
                "--pdf",
                "También exporta un PDF. Requiere el extra pdf, por ejemplo pip install 'vulnclaw[pdf]'.",
            ),
            (
                "--pdf-out PATH",
                "Ruta de salida del PDF. Por defecto, la ruta del informe generado con un sufijo .pdf.",
            ),
        ),
        notes=(
            "Los informes incluyen hallazgos verificados, estado de falso positivo/revisión, resumen "
            "de la ruta de ataque y la gobernanza de alcance registrada cuando esté disponible.",
        ),
        examples=(
            "vulnclaw report ~/.vulnclaw/sessions/session_001.json",
            "vulnclaw report https://lab.example --target --pdf",
        ),
    ),
    ManualTopic(
        name="config",
        summary="Administra valores de configuración y presets de proveedor.",
        usage=(
            "vulnclaw config list\n"
            "vulnclaw config get KEY\n"
            "vulnclaw config set KEY VALUE\n"
            "vulnclaw config provider [NAME|--list]"
        ),
        flags=(
            ("set KEY VALUE", "Define una clave de configuración en notación de punto, como llm.model o session.max_rounds."),
            ("get KEY", "Imprime un valor de configuración. Las claves con apariencia de secreto se enmascaran."),
            ("list", "Imprime toda la configuración efectiva en formato YAML."),
            ("provider NAME", "Cambia el preset de proveedor y completa los valores por defecto de base_url/model."),
            ("provider --list, -l", "Lista los presets de proveedor y muestra el proveedor actual."),
        ),
        notes=(
            "Se requiere un subcomando de config; ejecutar vulnclaw config solo imprime el uso y termina.",
            "Claves LLM útiles: llm.provider, llm.api_key, llm.api_keys, llm.auth_mode, "
            "llm.chatgpt_auto_proxy, llm.base_url, llm.model, llm.max_tokens, "
            "llm.max_context_tokens, llm.temperature, llm.reasoning_effort. Usa `vulnclaw login` "
            "en lugar de llm.api_key para autenticación OAuth basada en suscripción de ChatGPT.",
            "Claves de sesión útiles: session.output_dir, session.report_format, session.max_rounds, "
            "session.engine (solve|rounds), session.solve_max_steps, session.solve_max_intents, "
            "session.solve_max_tool_rounds, session.solve_max_parallel, session.show_thinking, "
            "session.persistent_rounds_per_cycle, session.persistent_max_cycles, "
            "session.persistent_auto_report, session.language, session.reasoning_state_enabled, "
            "session.reflexion_enabled, session.plugin_runtime_enabled. Las claves repl_parallel_* "
            "(repl_parallel_enabled/agents/depth/worker_rounds/surface_limit) solo se aplican al "
            "despliegue en abanico --parallel-agents de network-scan del motor heredado 'rounds', "
            "no a 'solve'.",
            "Claves de seguridad útiles: safety.enable_python_execute, safety.python_execute_mode, "
            "safety.python_execute_max_lines, safety.tool_parallel, safety.tool_max_concurrent.",
        ),
        examples=(
            "vulnclaw config provider --list",
            "vulnclaw config provider deepseek",
            "vulnclaw config set llm.api_keys 'key-one,key-two,key-three'",
            "vulnclaw config set session.max_rounds 25",
            "vulnclaw config set session.engine rounds",
        ),
    ),
    ManualTopic(
        name="kb",
        summary="Administra la base de conocimiento de seguridad local.",
        usage="vulnclaw kb update\nvulnclaw kb status",
        flags=(
            ("update", "Siembra o actualiza las entradas incluidas de la base de conocimiento."),
            ("status", "Muestra si la recuperación semántica está activa, si el fallback por palabras clave está activo, o si no hay datos disponibles."),
        ),
        notes=(
            "La recuperación semántica requiere el extra kb. Sin él, VulnClaw recurre a la recuperación por palabras clave cuando existen datos.",
        ),
        examples=("vulnclaw kb update", "vulnclaw kb status"),
    ),
    ManualTopic(
        name="target-state",
        summary="Inspecciona, compara, restaura o limpia el historial de objetivos persistido.",
        usage=(
            "vulnclaw target-state list TARGET\n"
            "vulnclaw target-state preview TARGET [--snapshot ID]\n"
            "vulnclaw target-state diff TARGET FROM_ID [--to TO_ID]\n"
            "vulnclaw target-state rollback TARGET SNAPSHOT_ID\n"
            "vulnclaw target-state clear TARGET"
        ),
        flags=(
            ("list TARGET", "Lista hasta 20 instantáneas recientes de un objetivo."),
            ("preview TARGET", "Muestra fase, estrategia de reanudación, conteo de hallazgos, activos prioritarios y próximas acciones."),
            ("preview --snapshot ID", "Previsualiza una instantánea específica."),
            ("diff TARGET FROM_ID --to TO_ID", "Compara dos instantáneas, o compara FROM_ID con el estado actual cuando se omite --to."),
            ("rollback TARGET SNAPSHOT_ID", "Restaura el historial de objetivo a una instantánea."),
            ("clear TARGET", "Elimina el historial de objetivo persistido de un objetivo."),
        ),
        notes=(
            "Los comandos de tarea usan el estado de objetivo cuando --resume está habilitado, que es el valor por defecto.",
            "Usa --no-resume en run/recon/scan/exploit/persistent/network-scan para ignorar este historial.",
        ),
        examples=(
            "vulnclaw target-state list https://lab.example",
            "vulnclaw target-state preview https://lab.example",
            "vulnclaw target-state diff https://lab.example snap-a --to snap-b",
        ),
        aliases=("target", "state", "history"),
    ),
    ManualTopic(
        name="plugins",
        summary="Inspecciona y ejecuta plugins de detección de vulnerabilidades.",
        usage=(
            "vulnclaw plugins list [--stage STAGE] [--tag TAG]\n"
            "vulnclaw plugins info PLUGIN_ID\n"
            "vulnclaw plugins run PLUGIN_ID --target TARGET [--stage STAGE] [--option KEY=VALUE] "
            "[--input FILE]"
        ),
        flags=(
            ("list --stage STAGE", "Filtra la lista de plugins por etapa, por ejemplo discovery."),
            ("list --tag TAG", "Filtra la lista de plugins por etiqueta."),
            ("info PLUGIN_ID", "Imprime los metadatos JSON completos de un plugin."),
            ("run PLUGIN_ID", "ID de plugin a ejecutar. Obligatorio."),
            ("run --target TARGET", "Host/IP/URL objetivo para la ejecución del plugin."),
            ("run --stage STAGE", "Etapa bajo la cual ejecutar el plugin (por defecto: discovery)."),
            (
                "run --option KEY=VALUE, -o KEY=VALUE",
                "Opción de plugin, repetible. El valor se interpreta como JSON cuando es posible.",
            ),
            ("run --input FILE", "Archivo JSON cuyo contenido se combina con las opciones del plugin."),
        ),
        notes=(
            "Los plugins son las comprobaciones de detección estructuradas y sin LLM (headers, "
            "endpoints JS, JWT, etc.) que respaldan session.plugin_runtime_enabled durante las "
            "ejecuciones autónomas.",
            "session.plugin_default_timeout y session.plugin_max_requests_per_target acotan la "
            "ejecución de plugins durante las ejecuciones autónomas; el comando run de la CLI no "
            "tiene tal límite.",
        ),
        examples=(
            "vulnclaw plugins list",
            "vulnclaw plugins info builtin.web.headers",
            "vulnclaw plugins run builtin.web.headers --target https://lab.example",
        ),
    ),
    ManualTopic(
        name="tui",
        summary="Abre el banco de trabajo de terminal para la configuración guiada de tareas.",
        usage="vulnclaw tui [--target TARGET] [--mode quick|standard|deep|continuous] [SCOPE FLAGS]",
        flags=(
            ("--target TARGET, -t TARGET", "Precarga el objetivo autorizado."),
            (
                "--mode MODE, -m MODE",
                "Precarga el modo del banco de trabajo. quick corresponde a recon, standard a run, "
                "deep a scan, y continuous a persistent.",
            ),
            ("--only-port PORT", "Precarga un único puerto permitido."),
            ("--only-host HOST", "Precarga un único host permitido."),
            ("--only-path PATH", "Precarga una única ruta permitida."),
            ("--blocked-host HOST", "Precarga un host excluido."),
            ("--blocked-path PATH", "Precarga una ruta excluida."),
            ("--allow-actions CSV", "Precarga las acciones permitidas."),
            ("--block-actions CSV", "Precarga las acciones bloqueadas."),
            ("--resume / --no-resume", "Precarga el comportamiento de reanudación del historial de objetivos."),
            ("--dry-run", "Muestra el resumen de lanzamiento y termina sin iniciar una tarea."),
            ("--once", "Muestra el panel una sola vez y termina, útil para pruebas de humo."),
        ),
        notes=(
            "La TUI expone los mismos controles de alcance y acción que los comandos de tarea de la CLI.",
        ),
        examples=(
            "vulnclaw tui",
            "vulnclaw tui --target https://lab.example --mode quick --only-port 443",
            "vulnclaw tui --dry-run --target https://lab.example --mode deep",
        ),
    ),
    ManualTopic(
        name="web",
        summary="Inicia la Web UI local de FastAPI/React.",
        usage="vulnclaw web [--host HOST] [--port PORT] [--dry-run] [--allow-remote]",
        flags=(
            ("--host HOST", "Dirección de enlace. Por defecto 127.0.0.1."),
            ("--port PORT", "Puerto de enlace. Por defecto 7788."),
            ("--dry-run", "Valida las importaciones e imprime información de lanzamiento sin iniciar uvicorn."),
            (
                "--allow-remote",
                "Requerido cuando --host no es 127.0.0.1. Esto evita exponer accidentalmente la Web UI.",
            ),
        ),
        notes=(
            "Instala el extra web si faltan FastAPI/uvicorn: pip install 'vulnclaw[web]'.",
            "Mantén la Web UI en localhost salvo que necesites intencionalmente acceso remoto.",
        ),
        examples=("vulnclaw web", "vulnclaw web --port 8080 --dry-run"),
    ),
    ManualTopic(
        name="repl",
        summary="Inicia el REPL clásico de lenguaje natural.",
        usage="vulnclaw repl\nvulnclaw",
        flags=(
            ("sin argumentos", "Ejecutar vulnclaw sin subcomando abre este REPL por defecto."),
        ),
        notes=(
            "Los comandos del REPL incluyen help, status, target TARGET, tools, report [TARGET], persistent [TARGET], think [on|off], clear y exit.",
            "Las entradas en lenguaje natural que incluyen una palabra clave de modo automático y un objetivo entran en modo de pentest autónomo.",
            "El despliegue en abanico acotado de agentes hijos en paralelo está disponible desde el flag --parallel-agents del comando network-scan, no directamente desde el REPL.",
        ),
        examples=("vulnclaw", "vulnclaw repl"),
    ),
    ManualTopic(
        name="init",
        summary="Crea los directorios de configuración de VulnClaw y el archivo de configuración inicial.",
        usage="vulnclaw init",
        notes=(
            "Crea ~/.vulnclaw por defecto, a menos que VULNCLAW_CONFIG_DIR apunte a otro lugar.",
        ),
        examples=("vulnclaw init",),
    ),
    ManualTopic(
        name="doctor",
        summary="Verifica la preparación del entorno de ejecución y las integraciones configuradas.",
        usage="vulnclaw doctor",
        notes=(
            "Verifica Python, node, npx, uvx, nmap, la configuración del LLM, el registro del servicio MCP y el número de herramientas expuestas.",
            "Úsalo antes de una ejecución real cuando la configuración del proveedor, MCP o las herramientas del frontend no estén claras.",
        ),
        examples=("vulnclaw doctor",),
    ),
    ManualTopic(
        name="login",
        summary="Inicia sesión con una suscripción de ChatGPT (Codex \"Sign in with ChatGPT\").",
        usage="vulnclaw login [--proxy-url URL] [--no-browser] [--set-default/--no-set-default]",
        flags=(
            (
                "--proxy-url URL",
                "Usa un base_url de proxy externo compatible con OpenAI en lugar del puente integrado.",
            ),
            ("--no-browser", "Imprime la URL de inicio de sesión en lugar de abrir un navegador."),
            (
                "--set-default / --no-set-default",
                "Define llm.auth_mode=oauth al tener éxito (por defecto: sí se define).",
            ),
        ),
        notes=(
            "Abre la página de consentimiento de ChatGPT, guarda un token renovable y (con "
            "llm.chatgpt_auto_proxy) inicia un proxy local integrado que conecta chat.completions "
            "con el backend de ChatGPT.",
            "Esto reutiliza el cliente OAuth de Codex de primera parte de OpenAI. Usar una "
            "suscripción de ChatGPT a través de un cliente no oficial puede violar los Términos de "
            "Servicio de OpenAI y puede restringir tu cuenta; procede bajo tu propio riesgo.",
            "Usa `vulnclaw logout` para eliminar los tokens guardados, o `vulnclaw config set "
            "llm.auth_mode static` junto con llm.api_key para volver a una clave de API estática.",
        ),
        examples=("vulnclaw login", "vulnclaw login --no-browser"),
    ),
    ManualTopic(
        name="logout",
        summary="Elimina los tokens OAuth guardados del flujo de inicio de sesión de ChatGPT.",
        usage="vulnclaw logout",
        notes=("No cambia llm.auth_mode; vuelve a static por separado si es necesario.",),
        examples=("vulnclaw logout",),
    ),
    ManualTopic(
        name="manual",
        summary="Imprime este manual completo.",
        usage="vulnclaw manual [TOPIC] [--format text|markdown|man]\nvulnclaw man [TOPIC] [--format text|markdown|man]\nvulnclaw --man",
        flags=(
            ("TOPIC", "Nombre de comando/tema opcional, como scan, network-scan, config o target-state."),
            ("--format text, -f text", "Formato humano de terminal. Es el valor por defecto."),
            ("--format markdown, -f markdown", "Markdown adecuado para documentación o fragmentos de README."),
            ("--format man, -f man", "Formato de página de manual roff, adecuado para guardar como vulnclaw.1."),
        ),
        notes=(
            "El comando manual viene empaquetado con VulnClaw, por lo que funciona tanto desde wheels instaladas como desde checkouts del código fuente.",
        ),
        examples=(
            "vulnclaw manual",
            "vulnclaw manual network-scan",
            "vulnclaw manual --format man",
        ),
        aliases=("man", "help-man"),
    ),
)

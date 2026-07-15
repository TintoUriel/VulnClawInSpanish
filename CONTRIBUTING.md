# Contributing to VulnClaw

Gracias por contribuir a VulnClaw.

El objetivo de este documento no es imponer un proceso engorroso, sino ayudarte a entender rápidamente la estructura actual del código, para que puedas modificarlo en el nivel correcto y así reducir situaciones del tipo "la funcionalidad funciona, pero la arquitectura cada vez es más caótica".

---

## Uno. Estructura del proyecto

```text
VulnClaw/
|-- vulnclaw/
|   |-- __init__.py              # Versión del paquete y metadatos básicos
|   |-- orchestrator.py          # Punto de entrada compartido de orquestación de tareas CLI / Web
|   |-- repl_runner.py           # Auxiliar de ejecución compartido del REPL
|   |-- agent/                   # Lógica central del Agent
|   |   |-- core.py              # Capa envolvente y punto de coordinación de AgentCore
|   |   |-- llm_client.py        # Llamadas al LLM, reintentos, retorno resumido de herramientas
|   |   |-- tool_call_manager.py # Deduplicación, ejecución y empaquetado de resultados de tool-call
|   |   |-- builtin_tools.py     # python_execute / nmap_scan / puente MCP
|   |   |-- context.py           # Estado de sesión, findings, pasos, estado del ciclo de vida
|   |   |-- runtime_state.py     # Estado del ciclo en tiempo de ejecución
|   |   |-- loop_controller.py   # Ciclo principal auto / persistent
|   |   |-- finding_parser.py    # Extracción de findings, niveles de evidencia y clasificación de ciclo de vida
|   |   |-- prompt_context.py    # Contexto de ronda y resumen del ataque
|   |   |-- prompts.py           # Auxiliares de construcción de prompts
|   |   |-- system_prompt.py     # Composición dinámica del system prompt
|   |   |-- input_analysis.py    # Extracción de objetivo, fase y pistas de vulnerabilidad
|   |   |-- anti_loop.py         # Prevención de bucles infinitos, objetivos fallidos, seguimiento de rutas de ataque
|   |   |-- recon_tracker.py     # Seguimiento del grado de completitud de las dimensiones de recon
|   |   |-- ctf_mode.py          # Identificación y verificación de flags CTF
|   |   |-- skill_context.py     # Selección de contexto de Skill
|   |   |-- kb_context.py        # Inyección de contexto de la base de conocimiento
|   |   `-- think_filter.py      # Mostrar/ocultar las etiquetas think
|   |-- cli/
|   |   |-- main.py              # Comandos CLI, doctor, arranque de web, CLI de target-state
|   |   |-- tui.py               # Clases de datos del TUI, renderizado del dashboard, constantes de color
|   |   `-- tui_textual.py       # Panel de trabajo TUI impulsado por Textual
|   |-- config/                  # Esquema de configuración, carga, guardado, sobrescritura por variables de entorno
|   |-- kb/                      # Almacenamiento, recuperación y actualización de la base de conocimiento
|   |-- mcp/
|   |   |-- lifecycle.py         # Comportamiento de attach / probe / call / degrade
|   |   |-- registry.py          # Estado del servicio, salud, estado de attach, registro de herramientas
|   |   `-- router.py            # Sugerencia de herramientas MCP a partir de intención en lenguaje natural
|   |-- report/                  # Generación de reportes, filtrado, generación de PoC
|   |-- skills/                  # Skills markdown integradas, loader, dispatcher
|   |   |-- core/                  # 7 Skills centrales en formato plano (un solo archivo .md)
|   |   |-- specialized/           # Skills especializadas en formato de directorio, cada subdirectorio contiene SKILL.md
|   |   |   |-- <skill-name>/
|   |   |   |   |-- SKILL.md      # frontmatter + condiciones de activación + normas de comportamiento
|   |   |   |   `-- references/  # Material que puede cargarse bajo demanda con load_skill_reference
|   |   |   `-- secknowledge-skill/ # Integración de base de conocimiento de seguridad CTF/SRC/Web+AI
|   |   |-- crypto_tools.py        # Implementación de la herramienta integrada crypto_decode
|   |   |-- dispatcher.py          # Enrutamiento de intención en lenguaje natural hacia Skills
|   |   `-- loader.py             # Carga de Skills en formato plano/directorio y lectura de references
|   |-- target_state/            # Historial de objetivos, preview, diff, rollback, plan de reanudación
|   |-- web/
|   |   |-- app.py               # Rutas FastAPI y servicio de frontend estático
|   |   |-- schemas.py           # Modelos de solicitud/respuesta de la API Web
|   |   |-- task_manager.py      # Estado e historial persistente de tareas Web
|   |   |-- stream.py            # Codificación de eventos SSE
|   |   |-- services/            # Capa de servicios de config / report / target / task / MCP
|   |   `-- static/              # Página estática de respaldo cuando no existe el dist del frontend
|   `-- warstories/              # Contenido markdown de casos integrados
|-- frontend/
|   |-- src/
|   |   |-- pages/               # Páginas Dashboard / Tasks / Target / Snapshots / Reports / Settings
|   |   |-- api/                 # Encapsulado de solicitudes API del frontend
|   |   |-- hooks/               # Hooks de React Query
|   |   `-- types/               # Tipos compartidos del frontend
|   `-- package.json             # Scripts de build y desarrollo del frontend
|-- scripts/                     # Scripts de preflight de release / verificación de dist
|-- tests/                       # Pruebas de backend, CLI, MCP, release, web, report
|-- .github/workflows/           # Workflows de CI / preflight / release
|-- README.md                    # Descripción en español
|-- README_EN.md                 # Descripción en inglés
|-- pyproject.toml               # Metadatos de empaquetado y reglas de build de Hatch
`-- CONTRIBUTING.md              # Este archivo
```

---

## Dos. Navegación del código

Guía rápida de qué módulo revisar según el escenario de modificación.

### 2.1 Modificar el comportamiento del Agent → `vulnclaw/agent/`

Escenarios aplicables:
- Comportamiento del ciclo de pentesting autónomo / continuo
- Orquestación de llamadas a herramientas
- Procesamiento de solicitudes y respuestas del LLM
- Lógica de recon / CTF / anti-loop
- Ciclo de vida de findings, niveles de evidencia, análisis de resultados

`core.py` es la capa envolvente de coordinación. A menos que sea realmente lógica de punto de entrada, prioriza modificar el helper/módulo correspondiente en lugar de acumular lógica de vuelta en `core.py`.

### 2.2 Modificar el flujo de tareas compartido → `vulnclaw/orchestrator.py` / `vulnclaw/repl_runner.py`

Escenarios aplicables:
- Ciclo de vida de tareas compartido entre CLI / Web / REPL
- Flujo restore → run → save → summarize
- Auxiliar de ejecución única del REPL

Cuando el mismo comportamiento aparece tanto en CLI como en Web, debe consolidarse aquí; no escribas una copia en `cli/main.py` y otra en `web/services/task_service.py`.

### 2.3 Modificar la línea de comandos o el REPL → `vulnclaw/cli/main.py`

Escenarios aplicables:
- Comandos Typer
- Experiencia del REPL
- Salida de `doctor`
- Comportamiento del lanzador `web`
- Subcomando `target-state`

Esta capa se encarga del punto de entrada, el enlace de parámetros y la salida al usuario; no es adecuada para contener la lógica central de pentesting.

### 2.4 Modificar el panel de trabajo TUI → `vulnclaw/cli/tui.py` / `vulnclaw/cli/tui_textual.py`

Escenarios aplicables:
- Diseño y renderizado del dashboard TUI
- Sistema de comandos con barra (`/target`, `/mode`, `/start`, etc.)
- Interacción del Command Palette
- Máquina de estados de confirmación/aviso

**Relación arquitectónica:**

| Archivo | Responsabilidad |
|------|------|
| `tui.py` | Clases de datos, renderizado del dashboard con Rich, constantes de color, registro de comandos con barra, punto de entrada `run_tui()` |
| `tui_textual.py` | Implementación de la App Textual: DashboardScreen, CommandPalette, SecondaryPopup, manejadores de comandos con barra, máquina de estados de confirmación, motor de ejecución de subprocesos |

### 2.5 Modificar la configuración → `vulnclaw/config/`

- `schema.py`: definición del modelo de configuración
- `settings.py`: carga, guardado, sobrescritura por variables de entorno, rutas de directorios

No escribas parsing de configuración a mano disperso por toda la lógica de negocio.

### 2.6 Modificar la lógica de reportes → `vulnclaw/report/`

Escenarios aplicables:
- Renderizado de reportes en Markdown / HTML
- Filtrado del contenido del reporte
- Generación de PoC
- Resumen de verificación e información de localización

El punto de entrada principal es `generator.py`, que afecta tanto a los reportes de target-state como a los de persistent-cycle.

### 2.7 Modificar el comportamiento de MCP → `vulnclaw/mcp/`

- `registry.py`: estado del servicio, salud, estado de attach, registro de herramientas
- `lifecycle.py`: lógica de attach / probe / call / degrade
- `router.py`: sugerencia de herramientas MCP a partir de intención en lenguaje natural

Estado actual:
- `fetch` / `memory`: ejecutables localmente
- `chrome-devtools` / `burp`: ya cuentan con attach stdio real, descubrimiento dinámico de herramientas y esqueleto de sesión persistente
- Otros servicios: en su mayoría siguen degradando a placeholders estructurados

Al modificar MCP, considera también la presentación de diagnósticos, la clasificación de error_type y el comportamiento de degradación tras un fallo de attach.

### 2.8 Modificar la continuación de pruebas / herencia de resultados → `vulnclaw/target_state/`

Escenarios aplicables:
- Persistencia de target-state
- Reglas de merge
- preview / diff / rollback
- Estrategia de reanudación y generación de resúmenes

Esto se encarga de "compartir resultados del mismo objetivo entre comandos". No metas esta lógica de vuelta en `core.py`, ni la repitas en la capa de páginas.

### 2.9 Modificar el backend Web → `vulnclaw/web/`

- `app.py`: rutas FastAPI y servicio de recursos estáticos del frontend
- `schemas.py`: modelos de solicitud/respuesta
- `task_manager.py`: estado e historial de tareas Web
- `services/`: capa de servicios de config / report / target / task / MCP

Prioriza colocar la lógica en `web/services/` para evitar que las funciones de rutas se conviertan en un totum revolutum.

### 2.10 Modificar la interfaz Web → `frontend/`

Escenarios aplicables:
- Páginas Dashboard / Task Console / Target State / Snapshots / Reports / Settings
- Hooks de React Query
- Enlaces de API del frontend
- Interacción y optimización de estilos de la consola

El contrato entre frontend y backend debe mantenerse consistente con `vulnclaw/web/schemas.py`.

Actualmente el lado Web incluye principalmente: API del backend, persistencia del estado de tareas, preview/diff del target, diagnósticos MCP y configuración del modo de seguridad en Settings.

Principios:
- La capa Web reutiliza el eje principal existente de agent / target_state / report
- No dupliques en la capa Web un nuevo conjunto de lógica de recuperación
- No dejes que el frontend tenga acceso directo a claves sensibles

### 2.11 Modificar el flujo de empaquetado / publicación → `scripts/`, `.github/workflows/`, `pyproject.toml`

Escenarios aplicables:
- Preflight local
- Verificación de artefactos dist
- Workflow de CI / release
- Include / exclude de build
- Metadatos del paquete

La fuente de verdad de la versión es `pyproject.toml`; `vulnclaw/__init__.py` es el respaldo.

### 2.12 Modificar o agregar Skills → `vulnclaw/skills/`

Escenarios aplicables:
- Agregar documentación de nuevos flujos centrales de pentesting
- Agregar nuevas bases de conocimiento especializadas o documentos de referencia
- Ajustar las reglas de despacho automático de lenguaje natural a Skill
- Actualizar el conjunto de materiales legibles por `load_skill_reference`

Actualmente hay dos formatos de Skill:

| Formato | Ubicación | Uso |
|------|------|------|
| flat-format | `vulnclaw/skills/core/*.md` | Skills de flujo central |
| directory-format | `vulnclaw/skills/specialized/<skill-name>/` | Skills especializadas, deben incluir `SKILL.md`, opcionalmente `references/` |

Convenciones del directory-format:
- `SKILL.md` usa YAML frontmatter, debe incluir al menos `name` y `description`
- En `references/` se colocan archivos `.md`, `.yaml`, `.yml`; el nombre del archivo se expone al Agent
- El contenido de referencia debe dividirse por tema, evita meter toda una base de conocimiento grande en `SKILL.md`
- Cuando se necesite activar esa Skill, agrega palabras clave de señal fuerte en `SKILL_INTENT_MAP` dentro de `dispatcher.py`
- Tras agregar o modificar una Skill, actualiza en conjunto `tests/test_skills.py` y la tabla de Skills del README

`secknowledge-skill` es el ejemplo actual de integración de base de conocimiento externa; al sincronizar Skills externas, conserva la fuente, la licencia y las notas de integración.

### 2.13 Notas

- Modifica el código en el módulo correcto en la medida de lo posible, no vuelvas a amontonar en `core.py` responsabilidades que ya se separaron
- Si estás modificando el flujo de tareas compartido, prioriza `orchestrator.py` / `repl_runner.py`
- Al modificar lógica de comportamiento, procura complementar las pruebas correspondientes
- Al modificar la lógica de empaquetado/publicación, revisa también `pyproject.toml`, `scripts/`, `.github/workflows/`
- Al modificar la documentación, asegúrate de que la descripción de capacidades coincida con la implementación real actual, especialmente en las partes propensas a confusión como MCP, sandbox y límites de seguridad

---

## Tres. Normas de colaboración de ramas

### 3.1 Resumen

#### Propósito de la norma

Para garantizar la estabilidad y publicabilidad de la rama principal main, unificar el flujo de desarrollo colaborativo entre varias personas y reducir el riesgo de conflictos de fusión de código e incidentes en producción, se establece esta norma. Todos los colaboradores que envíen código deben seguir este flujo.

#### Principios centrales

- **Estabilidad del tronco**: la rama main es la rama estable de nivel productivo, puede publicarse y ejecutarse directamente en cualquier momento
- **Verificación por capas**: todas las funcionalidades y correcciones entran primero a la rama de desarrollo dev para pruebas de integración, y solo tras verificarse sin errores se sincronizan a main
- **Admisión por PR**: está prohibido hacer push directo a las ramas de larga duración; todo cambio debe pasar por revisión mediante el flujo de Pull Request
- **Historial claro**: mantener los registros de commits limpios y legibles, siguiendo una convención unificada de nomenclatura y de mensajes de commit

### 3.2 Modelo de ramas

El repositorio adopta un modelo simplificado de Git Flow con "dos ramas de larga duración + múltiples ramas temporales".

#### Ramas de larga duración (protegidas, prohibido el push directo)

| Nombre de rama | Rol | Reglas de permisos | Descripción |
|--------|------|----------|------|
| `main` | Rama principal de producción | Solo los administradores pueden fusionar vía PR; prohibido el push directo, el push forzado y la eliminación | Contiene el código estable de las publicaciones oficiales, cada fusión corresponde a una versión publicable, con su respectiva etiqueta de versión |
| `dev` | Rama de integración de desarrollo | Todos los colaboradores fusionan vía PR; prohibido el push directo, el push forzado y la eliminación | Rama principal del desarrollo diario, todas las funcionalidades nuevas y correcciones de bugs se fusionan primero aquí para pruebas de integración y verificación |

#### Ramas temporales (se eliminan al terminar el desarrollo)

Las ramas temporales se crean a partir de su rama base correspondiente, y se eliminan inmediatamente después de que la funcionalidad se completa y se fusiona.

| Tipo de rama | Formato de nomenclatura | Rama base | Destino de fusión | Escenario de uso |
|----------|----------|----------|----------|----------|
| Rama de funcionalidad | `feature/descripción-de-la-funcionalidad` | dev | dev | Nuevas funcionalidades, características, refactorización, actualizaciones mayores de documentación |
| Rama de corrección | `fix/descripción-del-problema` | dev | dev | Corrección de bugs no urgentes detectados en entornos de desarrollo o pruebas |
| Rama de documentación | `docs/descripción` | dev | dev | Modificaciones puramente de documentación, actualización de descripciones, adición de comentarios |

### 3.3 Flujo de desarrollo estándar (ramas de funcionalidad / corrección)

#### Paso 1: sincronizar la rama base y crear la rama de desarrollo

```bash
# Cambiar a la rama dev y obtener el código remoto más reciente
git checkout dev
git pull origin dev

# Crear una rama de funcionalidad/corrección a partir de dev, siguiendo la convención de nomenclatura
git checkout -b feature/i18n-frontend
```

#### Paso 2: desarrollo y commits locales

Los mensajes de commit siguen el formato "tipo: descripción breve", por ejemplo:

```
feat: agregar soporte de internacionalización i18n en el frontend
fix: corregir excepción en la decodificación base64url
docs: actualizar instrucciones de instalación del README
```

Se recomienda hacer commits pequeños, cada commit correspondiendo a un cambio lógico independiente.

#### Paso 3: sincronizar con upstream y reordenar los commits con rebase

Antes de enviar el PR, sincroniza primero el código más reciente de dev para evitar conflictos de fusión:

```bash
# Obtener el código más reciente de dev
git fetch origin dev

# Hacer rebase sobre el dev más reciente para mantener un historial de commits lineal
git rebase origin/dev
```

Si hay conflictos, resuélvelos localmente y ejecuta `git add . && git rebase --continue`.

Una vez completado el rebase, haz push a tu rama remota:

```bash
git push origin feature/i18n-frontend
```

#### Paso 4: enviar el Pull Request

Inicia el PR en la página del repositorio de GitHub, con tu rama de funcionalidad como origen y `dev` como destino.

El título del PR debe coincidir con el mensaje de commit, y la descripción debe incluir:
- Resumen del contenido del cambio
- Archivos modificados y alcance del impacto
- Estado de la verificación de pruebas
- Issue asociado (obligatorio)

Espera a que las verificaciones automáticas de CI pasen y a la revisión de código.

#### Paso 5: revisión aprobada, fusión de la rama

Una vez aprobada la revisión y superadas todas las verificaciones, el mantenedor realiza la fusión. Al completarse la fusión, se elimina la rama de funcionalidad.

### 3.4 Reglas de revisión y admisión de PR

#### Condiciones de admisión obligatorias

Todo PR debe cumplir simultáneamente antes de fusionarse:

- **Debe estar asociado a un Issue existente**, y en la descripción del PR usar `Fixes #123` o `Closes #123` para vincularlo
- Todas las verificaciones automáticas de CI deben pasar (pruebas, build, validación de estilo de código)
- No debe haber comentarios de revisión de código sin resolver
- No debe haber conflictos de fusión con la rama destino
- El código debe estar rebaseado sobre la versión más reciente de la rama destino

#### Requisitos de revisión

- Fusión a `dev`: al menos 1 mantenedor debe aprobar la revisión
- Fusión a `main`: debe ser aprobada finalmente por el propietario del repositorio o un mantenedor principal

### 3.5 Normas y consideraciones comunes

- **Prohibido el push directo a las ramas de larga duración**: tanto main como dev están protegidas por reglas de protección de ramas, deben pasar por el flujo de PR
- **Prohibido el push forzado a las ramas de larga duración**: está terminantemente prohibido ejecutar `git push --force` en main y dev
- **Limpieza oportuna de ramas**: al completarse la fusión del PR, elimina de inmediato la rama temporal correspondiente
- **Usa rebase para sincronizar con upstream**: al obtener código de upstream, prioriza usar `git rebase` en lugar de `git merge`
- **Comunica con anticipación los cambios grandes**: para cambios grandes que involucren ajustes de arquitectura o refactorización de módulos centrales, se recomienda llegar a un consenso primero mediante un Issue o discusión antes de desarrollar

---

## Cuatro. Normas de envío de PR

### 4.1 Principio de Issue primero (Issue First)

Todos los PR **deben** estar asociados a un issue existente. Si encuentras un bug o quieres proponer una nueva funcionalidad, crea primero un issue.

- En la descripción del PR, usa `Fixes #123` o `Closes #123` para vincular el issue correspondiente
- Los PR sin un issue asociado no serán revisados
- Para correcciones pequeñas (errores tipográficos, cambios de una sola línea) puedes abrir un issue breve con una explicación concisa

### 4.2 Formato del título del PR

El título debe seguir la convención de [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(alcance opcional): <descripción breve>
```

**Tipos:**

| Tipo | Descripción |
|------|------|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Cambio de documentación |
| `style` | Formato de código (sin afectar la lógica) |
| `refactor` | Refactorización (sin cambiar la funcionalidad) |
| `perf` | Optimización de rendimiento |
| `test` | Relacionado con pruebas |
| `chore` | Cambios de build/herramientas/dependencias |

**Ejemplos:**

- `feat: agregar funcionalidad de inicio de sesión de usuario`
- `fix(api): corregir el error no devuelto en caso de timeout`
- `docs: actualizar las instrucciones de instalación`
- `chore: actualizar httpx a 0.28.0`

### 4.3 Requisitos de la descripción del PR

- Debe explicar: qué problema resuelve (issue asociado) y cómo lo corregiste
- Cambios de UI (Web UI o TUI): adjunta capturas de pantalla o GIF comparando el antes y el después
- Cambios de lógica: explica cómo lo verificaste (pasos de prueba manual / cobertura de pruebas unitarias)
- Prohibido: pegar directamente una descripción larga generada por IA. A los mantenedores no les gusta la "literatura de relleno generada por IA", describe con tus propias palabras de forma concisa

### 4.4 Verificación antes de enviar

Antes de enviar el PR, confirma lo siguiente:

**Verificación de backend:**
```bash
# Verificación de estilo de código
ruff check vulnclaw tests

# Ejecutar pruebas
pytest -q
```

**Verificación de frontend:**
```bash
cd frontend
npm ci
npx tsc -b
```

**Preverificación completa (opcional):**
```bash
python scripts/release_preflight.py
python scripts/release_preflight.py --build
```

Como mínimo revisa:
1. Que las pruebas relacionadas pasen
2. Que la documentación coincida con la implementación
3. Que la nueva lógica esté en el módulo correcto, y no vuelva a amontonar responsabilidades en un archivo grande
4. Si afecta la versión, la salida del CLI, el README o el flujo de empaquetado, que los archivos relacionados estén actualizados

---

## Cinco. Guía de estilo de código

Lo siguiente no son reglas obligatorias, pero seguirlas hará que la revisión sea más fluida.

**Backend (Python):**
- Ejecuta `ruff check vulnclaw tests` para verificar el estilo del código (configuración en `pyproject.toml`)
- Límite de longitud de línea: 100 caracteres
- Versión objetivo de Python: 3.10+

**Frontend (TypeScript/React):**
- Ejecuta `npx tsc -b` para asegurar que la verificación de tipos pase
- Sigue el estilo existente de los componentes React del proyecto

**Principios generales:**
- Granularidad de funciones: procura mantener responsabilidad única, evita funciones excesivamente grandes
- Evita el else: prioriza los retornos anticipados (early return)
- Manejo de errores: se recomienda usar try/catch o .catch(), según el caso
- Seguridad de tipos (TypeScript): evita abusar de any, procura definir tipos precisos
- Inmutabilidad de variables: prioriza const sobre let
- Nomenclatura: usa palabras en inglés concisas pero claras en su significado

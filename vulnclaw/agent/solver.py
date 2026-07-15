"""Bucle de resolución OODA orientado a objetivos — reemplaza el flujo de rondas fijas por un grafo de pizarra (blackboard).

Estructura del bucle (sin número fijo de rondas):
  1. Siembra el Fact inicial con origin/goal.
  2. REASON: lee todo el grafo → determina si se alcanzó el objetivo / propone un nuevo Intent de exploración / no propone nada.
  3. EXPLORE: toma un Intent, lo ejecuta realmente con herramientas, y escribe la conclusión confirmada como un nuevo Fact.
  4. Condición de término: objetivo alcanzado / frontera de exploración agotada (sin Intent y Reason ya no propone) / se alcanza el presupuesto de seguridad.

El presupuesto de seguridad (max_steps) es solo un tope de respaldo para evitar
que se descontrole, no un contador de fases del flujo; en condiciones normales
el bucle termina antes por «objetivo alcanzado» o «frontera agotada».
"""

from __future__ import annotations

import asyncio
import contextvars
import json
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from vulnclaw.agent.agent_context import AgentContext


from vulnclaw.agent.blackboard import Blackboard, BoardIntent, IntentStatus
from vulnclaw.agent.llm_client import build_chat_completion_kwargs, call_llm_auto
from vulnclaw.agent.think_filter import strip_think_tags

FRONTIER_RECOVERY_LIMIT = 2

# Señales que indican «avance/conclusión confirmada» en la fase de exploración
# (coincidencia amplia, para no pasar por alto un intent que sí progresó)
_ADVANCE_MARKERS = [
    "confirmado",
    "éxito",
    "se obtuvo",
    "se consiguió",
    "se extrajo",
    "flag{",
    "flag ",
    "bypass exitoso",
    "eco de salida",
    "vulnerabilidad presente",
    "hallazgo",
    "devuelve 200",
    "devolvió 200",
    "status: 200",
    "sin autorización",
    "no requiere autenticación",
    "interfaz accesible",
    "filtración de información",
    "hallazgo clave",
    "hallazgo importante",
    "expuesto",
    "filtración",
    "200 ok",
    "cors",
    "se puede escribir",
    "se puede subir",
    "se puede descargar",
    "contraseña débil",
    "punto de inyección",
    "xss",
    "sql inject",
]
# Señales que indican «esta dirección no lleva a ningún lado» en la fase de exploración
_DEAD_END_MARKERS = [
    "no existe",
    "no se puede",
    "falló",
    "sin salida",
    "sin hallazgos",
    "sin inyección",
    "sin eco",
    "descartado",
]
# Expresiones negativas en el motivo de finalización — cuando el modelo escribe
# «no alcanzado» en el campo de finalización, esto lo detecta y lo rechaza
_NEGATION_MARKERS = [
    "no se alcanzó",
    "no alcanzado",
    "no se registró",
    "no se encontró",
    "no se completó",
    "no se logró",
    "aún no",
    "no hay",
    "no es suficiente",
    "no se puede probar",
    "no se puede confirmar",
    "no puede probar",
    "no cumple",
]


def _has_negation(text: str) -> bool:
    """Indica si el motivo de finalización contiene una expresión negativa (es decir, en realidad no se alcanzó)."""
    return any(m in (text or "") for m in _NEGATION_MARKERS)


_current_worker: contextvars.ContextVar["ExploreWorker | None"] = contextvars.ContextVar(
    "_current_worker", default=None
)


@dataclass
class ExploreWorker:
    intent_id: str
    evidence_buffer: list[str] = field(default_factory=list)
    tc_start: int = 0


class BoardGuard:
    """Serialise mutating Blackboard operations with an asyncio.Lock."""

    def __init__(self, board: Blackboard) -> None:
        self._board = board
        self._lock = asyncio.Lock()

    async def add_fact(self, description: str, source: str = "") -> Any:
        async with self._lock:
            return self._board.add_fact(description, source)

    async def conclude_intent(self, intent_id: str, fact_desc: str, source: str = "") -> Any:
        async with self._lock:
            return self._board.conclude_intent(intent_id, fact_desc, source)

    async def abandon_intent(self, intent_id: str, note: str = "") -> Any:
        async with self._lock:
            return self._board.abandon_intent(intent_id, note)

    async def record_tool_call(self, **kwargs: Any) -> None:
        async with self._lock:
            self._board.record_tool_call(**kwargs)


class IntentStreamSink:
    """Wraps a StreamSink to prefix output with ``[i00x]``."""

    def __init__(self, inner: Any, intent_id: str) -> None:
        self._inner = inner
        self._prefix = f"[{intent_id}] "
        self._first = True

    def on_status(self, message: str) -> None:
        if self._inner:
            self._inner.on_status(f"{self._prefix}{message}")

    def on_thinking_token(self, token: str) -> None:
        if self._inner:
            self._inner.on_thinking_token(token)

    def on_content_token(self, token: str) -> None:
        if self._inner:
            if self._first:
                self._inner.on_content_token(self._prefix)
                self._first = False
            self._inner.on_content_token(token)

    def on_tool_call(self, tool_name: str, args: str) -> None:
        if self._inner:
            self._inner.on_tool_call(f"{self._prefix}{tool_name}", args)

    def on_tool_result(self, result_summary: str) -> None:
        if self._inner:
            self._inner.on_tool_result(result_summary)

    def on_stream_end(self) -> None:
        if self._inner:
            self._inner.on_stream_end()
        self._first = True


@dataclass
class SolveResult:
    completed: bool
    reason: str
    steps: int
    facts: int
    board: Blackboard


# Banderas con forma flag{...} / ctfshow{...} / NSSCTF{...}
_FLAG_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{1,20}\{[^{}\n]{1,200}\}")


def _extract_flags(text: str) -> list[str]:
    """Extrae todos los tokens con forma de flag en el texto (deduplicados, conservando el orden)."""
    return list(dict.fromkeys(_FLAG_RE.findall(text or "")))


def _goal_wants_flag(goal: str) -> bool:
    g = (goal or "").lower()
    return any(k in g for k in ("flag", "captura la bandera", "ctf", "shell", "getshell"))


def _unverified_flags(claim: str, evidence: str) -> list[str]:
    """Devuelve los flags declarados en claim que no aparecen en la evidencia real de las herramientas (posible alucinación)."""
    return [f for f in _extract_flags(claim) if f not in evidence]


def _completion_is_grounded(goal: str, evidence: str) -> tuple[bool, str]:
    """Verificación de evidencia para la finalización: si el objetivo exige un flag, este debe haber aparecido realmente en la salida de las herramientas."""
    if not _goal_wants_flag(goal):
        return True, ""
    if _extract_flags(evidence):
        return True, ""
    return False, "El objetivo requiere un flag, pero no apareció ningún flag en la salida real de ninguna herramienta; se considera no verificado/posible alucinación"


def _extract_json(text: str) -> Optional[dict]:
    """Extrae de forma robusta un objeto JSON de la respuesta del LLM."""
    if not text:
        return None
    cleaned = strip_think_tags(text).strip()
    # Quita el cercado de código ```json ... ```
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    # Intento directo
    try:
        obj = json.loads(cleaned)
        return obj if isinstance(obj, dict) else None
    except (ValueError, TypeError):
        pass
    # Degradación: captura el primer bloque de llaves balanceadas
    start = cleaned.find("{")
    if start < 0:
        return None
    depth = 0
    for idx in range(start, len(cleaned)):
        ch = cleaned[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                with_suppress = cleaned[start : idx + 1]
                try:
                    obj = json.loads(with_suppress)
                    return obj if isinstance(obj, dict) else None
                except (ValueError, TypeError):
                    return None
    return None


async def _structured_call(agent: AgentContext, prompt: str, *, max_tokens: int = 900) -> str:
    """Llamada estructurada al LLM sin herramientas (usada por Reason / Conclude)."""
    client = agent._get_client()
    messages = [{"role": "user", "content": prompt}]
    kwargs = build_chat_completion_kwargs(agent, messages, max_tokens=max_tokens, temperature=0.2)
    response = client.chat.completions.create(**kwargs)
    if response and response.choices:
        return response.choices[0].message.content or ""
    return ""


def _reason_prompt(board: Blackboard, max_intents: int) -> str:
    # Inspirado en Cairn reason.md: lista explícitamente open intents y abandoned intents, evita repeticiones
    open_list = board.open_intents()
    abandoned = [i for i in board.intents if i.status == IntentStatus.ABANDONED]
    concluded = [i for i in board.intents if i.status == IntentStatus.CONCLUDED]

    open_block = ""
    if open_list:
        open_block = "Intents actualmente en estado OPEN (en exploración o pendientes de explorar):\n"
        for i in open_list:
            open_block += f"  - {i.id}: {i.description}\n"
        open_block += "Si los open intents ya cubren todas las direcciones de valor, no propongas nuevos.\n\n"

    abandoned_block = ""
    if abandoned:
        abandoned_block = "Intents abandonados (sin salida o ya verificados):\n"
        for i in abandoned[-10:]:
            note = f" — {i.note[:60]}" if i.note else ""
            abandoned_block += f"  - {i.id}: {i.description}{note}\n"
        abandoned_block += "⚠ **Está terminantemente prohibido volver a proponer direcciones idénticas o muy superpuestas a los abandoned intents anteriores.** Ya se verificó que no llevan a ningún lado.\n\n"

    concluded_block = ""
    if concluded:
        concluded_block = "Intents ya concluidos (con resultado):\n"
        for i in concluded[-5:]:
            concluded_block += f"  - {i.id} → {i.result_fact}: {i.description}\n"
        concluded_block += "\n"

    frontier_block = ""
    if not open_list and not board.completed:
        frontier_block = (
            "Frontier recovery rule: there are currently no OPEN intents and the goal is "
            "not complete. Do not return {\"complete\": false} without new intents in this "
            "state. Propose fresh, non-overlapping directions that pivot to a different "
            "attack surface, parameter shape, HTTP method/header/cookie angle, source leak, "
            "or runtime behavior. Avoid repeating abandoned intents, but do not stop just "
            "because earlier broad directions failed.\n\n"
        )

    return (
        "Eres un experto senior en pentesting en este dominio. A continuación tienes la "
        "instantánea del «grafo de pizarra» de la tarea actual: facts son hechos objetivos "
        "ya confirmados, intents son direcciones de exploración. El grafo parte de facts y, "
        "mediante la exploración de un intent, obtiene un nuevo fact, acercándose "
        "progresivamente al goal.\n\n"
        f"{open_block}{abandoned_block}{concluded_block}{frontier_block}"
        "Determina dos cosas: ① si los facts existentes ya satisfacen el goal; ② si no lo "
        "satisfacen, si se debe proponer una nueva dirección de exploración.\n\n"
        "Devuelve únicamente un objeto JSON, sin ningún otro contenido:\n"
        '- Si el goal ya se alcanzó: {"complete": true, "reason": "explica por qué se alcanzó", "evidence": ["f002"]}'
        " (complete debe ser el booleano true; evidence debe referenciar al menos un fact id real que demuestre el logro)\n"
        '- Si no se alcanzó y se debe proponer una nueva dirección: {"complete": false, "intents": [{"from": ["f001"], "description": "dirección de exploración valiosa e independiente"}]}\n'
        '- Si no se alcanzó pero por ahora no hace falta añadir direcciones: {"complete": false}\n\n'
        "Reglas:\n"
        "- **El campo complete solo puede ser el booleano true o false**.\n"
        "- **La determinación de finalización debe basarse en hechos objetivos ya confirmados en facts**, no en suposiciones o deseos, y evidence debe referenciar fact ids reales.\n"
        "- Si algún fact está marcado como [No verificado]/[Finalización rechazada]/posible alucinación, jamás debe usarse para determinar que se alcanzó el objetivo.\n"
        "- **Está terminantemente prohibido volver a proponer direcciones idénticas o muy superpuestas a los abandoned intents** — ya se exploraron y no llevan a ningún lado.\n"
        "- Si todavía hay algún intent en estado open y los facts actuales no revelan una nueva "
        "dirección más valiosa que los open intents, devuelve {\"complete\": false} (sin proponer "
        "nuevas direcciones), y deja que los open intents sigan avanzando.\n"
        f"- Propón como máximo {max_intents} direcciones de alto valor, sin superposición entre sí, "
        "que puedan avanzar de forma independiente, cada una centrada en una idea central.\n"
        "- description debe ser concisa y enfocada, sin extenderse; cada intent debe cubrir una dimensión distinta.\n\n"
        "## Grafo de pizarra\n```\n" + board.to_prompt_graph() + "\n```\n"
    )


def _conclude_prompt(board: Blackboard, intent: BoardIntent, evidence: str) -> str:
    return (
        "Esta es la «fase de conclusión». Anula cualquier instrucción anterior de seguir "
        "explorando/enviando solicitudes/esperando resultados — detén de inmediato cualquier "
        "acción y limítate a resumir.\n"
        "Solo puedes resumir en base a información **ya confirmada realmente** en la «salida "
        "real de las herramientas»; no debes seguir invocando herramientas ni esperar "
        "resultados incompletos.\n\n"
        "Devuelve únicamente un objeto JSON:\n"
        '{"advanced": true/false, "fact": "el nuevo hecho objetivo confirmado en esta ronda (incremental)"}\n\n'
        "## Criterios para determinar advanced (con sesgo amplio hacia true)\n"
        "Casos en los que advanced=true (basta con **cualquiera** de los siguientes):\n"
        "- Se descubrió una nueva interfaz/endpoint accesible (aunque solo se confirme un 200)\n"
        "- Se confirmó una API accesible sin autorización (devuelve datos sin necesitar token)\n"
        "- Se descubrió información de la pila tecnológica/versión/configuración (cabecera Server, filtración en página de error, etc.)\n"
        "- Se descubrió un problema de configuración de seguridad (comodín en CORS, cabeceras de seguridad ausentes, ruta sensible con 403, etc.)\n"
        "- Se confirmó la existencia de una vulnerabilidad (punto de inyección/XSS/SSRF/lectura de archivos, etc.)\n"
        "- Se obtuvo un flag/shell/credencial real\n\n"
        "advanced=false únicamente cuando **no hubo ningún hallazgo nuevo en absoluto**: todas las "
        "solicitudes fueron 404/timeout/repetición de información ya conocida.\n\n"
        "## Reglas inquebrantables\n"
        "- fact debe ser un hecho objetivo **ya confirmado por la salida real de una herramienta**, no un plan, suposición o inferencia.\n"
        "- **Está terminantemente prohibido inventar flags/shells/contraseñas/datos** — si no apareció en la salida de una herramienta, no se puede afirmar que se obtuvo.\n"
        "- fact debe contener únicamente información incremental, no repitas lo que ya está en el grafo.\n\n"
        f"## Dirección de exploración actual {intent.id}\n{intent.description}\n\n"
        "## Salida real de las herramientas en esta exploración (tu única fuente confiable de hechos)\n```\n" + (evidence.strip() or "(sin salida de herramientas)") + "\n```\n\n"
        "## Grafo de pizarra\n```\n" + board.to_prompt_graph() + "\n```\n"
    )


def _explore_context(board: Blackboard, intent: BoardIntent, step: int, max_rounds: int) -> str:
    from_desc = ""
    if intent.from_facts:
        refs = [board.get_fact(fid) for fid in intent.from_facts]
        from_desc = "\n".join(f"  - {f.id}: {f.description}" for f in refs if f)
        from_desc = f"\nBasado en los hechos conocidos:\n{from_desc}"

    # Resumen de herramientas ya ejecutadas — evita repeticiones entre intents
    tc_summary = board.tool_call_summary(20)
    tc_block = ""
    if tc_summary:
        tc_block = (
            "\n## Herramientas ya ejecutadas (prohibido repetir la misma herramienta+mismos parámetros)\n"
            + tc_summary + "\n"
        )

    # Mejora de Cairn #5: inyecta la instrucción de override de conclusión en el último paso
    conclude_override = ""
    if step == max_rounds:
        conclude_override = (
            "\n## ⚠ Este es el último paso — detén la exploración de inmediato y resume\n"
            "No inicies más llamadas a herramientas ni esperes resultados incompletos.\n"
            "Basándote en la salida de herramientas ya obtenida, resume todos los hechos objetivos descubiertos en esta dirección.\n\n"
        )

    return (
        f"[Dirección de exploración {intent.id} · paso {step}/{max_rounds}]\n"
        f"Objetivo (goal): {board.goal}\n"
        f"Dirección de exploración actual: {intent.description}{from_desc}\n"
        f"{conclude_override}"
        f"{tc_block}\n"
        "## Reglas de ejecución (de cumplimiento obligatorio)\n"
        "1. Ejecuta realmente con herramientas en torno a la dirección actual; cada paso debe incluir una llamada a herramienta + análisis de la respuesta.\n"
        "2. ⚠ Está absolutamente prohibido repetir la misma herramienta+mismos parámetros que ya aparecen en la lista de «herramientas ya ejecutadas» de arriba.\n"
        "3. ⚠ Haz fetch de la misma URL solo una vez — si ya se hizo fetch, analiza directamente con el resultado ya obtenido.\n"
        "4. Si la dirección no lleva a ningún lado, explica claramente el motivo y detente.\n"
        "\n## Cadena de uso de herramientas (según el tipo de objetivo)\n"
        "Cadena estándar de pentest web:\n"
        "  ① js_recon(url=objetivo) — extrae interfaces del JS + sondeo automático sin autorización (**llamar primero**)\n"
        "  ② dir_enum(url=objetivo) — enumeración de directorios\n"
        "  ③ space_search(domain=dominio) — mapeo de superficie\n"
        "  ④ subdomain_enum(domain=dominio) — enumeración de subdominios\n"
        "  ⑤ unauth_test(base_url, endpoints) — verificación de acceso sin autorización sobre las interfaces descubiertas\n"
        "  ⑥ fetch(url, method) — sondeo de una sola solicitud (solo para rutas específicas no cubiertas por js_recon/dir_enum)\n"
        "Cadena Chrome MCP: chrome_navigate → chrome_read_page/chrome_get_web_content → análisis (no hagas navigate repetidamente)\n"
    )


def _is_duplicate_intent(board: Blackboard, new_desc: str) -> bool:
    """Comprueba si la nueva propuesta se superpone en gran medida con un intent ya abandoned (solo compara contra abandoned, no contra concluded).

    Solo bloquea la repetición de direcciones ya fallidas; las direcciones exitosas pueden profundizarse de nuevo sobre nuevos hechos.
    """
    abandoned = [i for i in board.intents if i.status == IntentStatus.ABANDONED]
    if not abandoned:
        return False
    new_lower = new_desc.lower()
    new_words = set(re.findall(r"[a-zA-Záéíóúñü]{2,}", new_lower))
    if len(new_words) < 3:
        return False
    for existing in abandoned:
        old_lower = existing.description.lower()
        old_words = set(re.findall(r"[a-zA-Záéíóúñü]{2,}", old_lower))
        if len(old_words) < 3:
            continue
        overlap = len(new_words & old_words) / max(len(new_words | old_words), 1)
        if overlap > 0.65:
            return True
    return False


def _add_decision_intents(board: Blackboard, decision: dict) -> int:
    added = 0
    for item in decision.get("intents") or []:
        desc = (item or {}).get("description", "").strip() if isinstance(item, dict) else ""
        if not desc:
            continue
        if _is_duplicate_intent(board, desc):
            continue
        board.add_intent(desc, (item or {}).get("from"))
        added += 1
    return added


def _frontier_recovery_prompt(board: Blackboard, max_intents: int, streak: int) -> str:
    return (
        _reason_prompt(board, max_intents)
        + "\n\n## Frontier recovery override\n"
        + f"This is recovery attempt {streak}/{FRONTIER_RECOVERY_LIMIT}. "
        + "The solve graph has no OPEN intents, but the goal is not complete. "
        + "Return JSON with at least one new intent unless the existing facts prove the "
        + "goal is impossible under the authorized scope. The new intents must be concrete "
        + "next actions and must pivot away from abandoned directions.\n"
        + 'Valid recovery response: {"complete": false, "intents": [{"from": ["f001"], '
        + '"description": "try a different concrete path"}]}\n'
    )


def _add_fallback_recovery_intents(board: Blackboard, max_intents: int) -> int:
    if not board.intents:
        return 0

    from_facts = board.fact_ids()[-3:]
    candidates = [
        (
            "Pivot to header/cookie auth bypass: test Authorization, x-auth-token, "
            "Cookies, Aaa, X-Forwarded-* and method override headers against login "
            "and likely protected pages."
        ),
        (
            "Pivot to request-shape login bypass: compare form vs JSON bodies, "
            "duplicate username/password parameters, array parameters, empty values, "
            "and GET/POST/PUT method differences while preserving session cookies."
        ),
        (
            "Pivot to source and backup leakage under catch-all routing: classify "
            "candidate source/backup paths by status, content-type, body length, "
            "hash and headers rather than status code alone."
        ),
    ]

    added = 0
    for desc in candidates:
        if _is_duplicate_intent(board, desc):
            continue
        board.add_intent(desc, from_facts)
        added += 1
        if added >= max(1, min(max_intents, len(candidates))):
            break
    return added


async def reason_step(agent: AgentContext, board: Blackboard, max_intents: int) -> dict:
    raw = await _structured_call(agent, _reason_prompt(board, max_intents), max_tokens=1200)
    parsed = _extract_json(raw)
    return parsed or {}


async def frontier_recovery_step(
    agent: AgentContext,
    board: Blackboard,
    max_intents: int,
    streak: int,
) -> dict:
    raw = await _structured_call(
        agent, _frontier_recovery_prompt(board, max_intents, streak), max_tokens=1200
    )
    parsed = _extract_json(raw)
    return parsed or {}


async def explore_step(
    agent: AgentContext,
    board: Blackboard,
    intent: BoardIntent,
    *,
    max_tool_rounds: int,
    evidence_buffer: list[str],
    stream_sink: Any = None,
    skip_context_write: bool = False,
) -> tuple[bool, str]:
    """Explora realmente en torno a un Intent y devuelve (si avanzó, descripción del hecho concluido).

    La fase de conclusión solo alimenta al modelo con la «salida real de herramientas capturada en esta exploración» como única fuente confiable de hechos, para reducir alucinaciones.
    skip_context_write: en modo paralelo, omite la escritura en agent.context.messages (evita escrituras cruzadas).
    """
    system_prompt = agent._build_system_prompt(
        agent.context.state.target, auto_mode=True, user_input=intent.description
    )
    evidence_start = len(evidence_buffer)
    tc_start = len(board.tool_calls)
    last_text = ""
    prev_tc_count = tc_start
    no_new_tc_streak = 0
    for step in range(1, max_tool_rounds + 1):
        ctx = _explore_context(board, intent, step, max_tool_rounds)
        text = await call_llm_auto(agent, system_prompt, ctx, stream_sink=stream_sink)
        last_text = text or ""
        if not skip_context_write:
            agent.context.add_assistant_message(f"[Exploración {intent.id} paso {step}] {last_text}")
        if hasattr(agent, "_finding_parser"):
            agent._finding_parser.parse(last_text)
        lowered = last_text.lower()
        if any(m.lower() in lowered for m in _ADVANCE_MARKERS):
            break
        if any(m in last_text for m in _DEAD_END_MARKERS) and step >= 2:
            break
        # Inspirado en el checkpoint de Cairn: compara la cantidad de tool_calls antes/después de este paso — si no hay nuevas, el modelo está dando vueltas en vacío
        cur_tc_count = len(board.tool_calls)
        if cur_tc_count == prev_tc_count:
            no_new_tc_streak += 1
            if no_new_tc_streak >= 2:
                last_text += "\n[!] 2 pasos consecutivos sin nuevas llamadas a herramientas (en vacío), se termina esta dirección."
                break
        else:
            # Comprueba si las llamadas nuevas de este paso son todas repetidas (mismo tool+key_args ya visto antes)
            new_tcs = board.tool_calls[prev_tc_count:]
            all_repeated = all(
                any(old.tool == tc.tool and old.key_args == tc.key_args
                    for old in board.tool_calls[:prev_tc_count])
                for tc in new_tcs
            ) if new_tcs else True
            if all_repeated and step >= 2:
                last_text += "\n[!] Todas las llamadas a herramientas de este paso fueron repetidas, se termina esta dirección."
                break
            no_new_tc_streak = 0
        prev_tc_count = cur_tc_count

    # ── Mejora de Cairn #2: fase Conclude (inspirada en explore-conclude.md) ──────
    # Sin importar cómo termine explore (rondas agotadas/advance/dead-end/en vacío), siempre se entra en la fase conclude.
    # conclude resume en base a la salida real de herramientas, con sesgo hacia conservar los hallazgos de valor.
    intent_evidence = "\n".join(evidence_buffer[evidence_start:])[-6000:]
    raw = await _structured_call(
        agent, _conclude_prompt(board, intent, intent_evidence), max_tokens=600
    )
    parsed = _extract_json(raw) or {}
    advanced = bool(parsed.get("advanced"))
    fact = str(parsed.get("fact", "")).strip()
    if not fact:
        fact = strip_think_tags(last_text).strip()[:200]

    # ── Mejora de Cairn #2b: respaldo de evidencia ─────────────────────────────────
    # Si conclude dice advanced=false, pero la salida de herramientas muestra claramente
    # una respuesta 200 o un hallazgo nuevo, se fuerza advanced=true (evita que el
    # conclude de un modelo débil descarte hallazgos de valor).
    if not advanced and intent_evidence:
        evidence_lower = intent_evidence.lower()
        has_data = any(marker in evidence_lower for marker in [
            "status: 200", "200 ok", '"success"', "'success'",
            "sin autorización", "posible falta de autorización", "devuelve datos",
            "interfaz/ruta", "coincidencia",
        ])
        if has_data and fact:
            advanced = True

    return advanced, fact


async def solve(
    agent: AgentContext,
    *,
    origin: str,
    goal: str,
    hints: Optional[list[str]] = None,
    max_steps: int = 40,
    max_intents: int = 3,
    max_tool_rounds: int = 4,
    max_parallel: int = 1,
    stream_sink: Any = None,
    on_event: Optional[Callable[[str, dict], None]] = None,
) -> SolveResult:
    """Ejecuta el bucle de resolución orientado a objetivos hasta que el objetivo se alcance / la frontera se agote / se llegue al presupuesto de seguridad."""
    board = agent.context.state.board
    board.origin = origin or board.origin
    board.goal = goal or board.goal
    guard = BoardGuard(board)

    def emit(kind: str, payload: dict) -> None:
        if on_event is not None:
            on_event(kind, payload)

    # Búfer de evidencia global — única fuente confiable de evidencia para todas las determinaciones de flag/finalización
    evidence_buffer: list[str] = []
    original_execute = agent._execute_mcp_tool

    async def _recording_execute(tool_name: str, tool_args: dict) -> str:
        import json as _json

        key_args = _json.dumps(tool_args, ensure_ascii=False, sort_keys=True)[:200]
        output = await original_execute(tool_name, tool_args)
        out_str = str(output)

        worker = _current_worker.get()
        if worker is not None:
            worker.evidence_buffer.append(out_str)
            if len(worker.evidence_buffer) > 400:
                del worker.evidence_buffer[:200]
            intent_id = worker.intent_id
        else:
            intent_id = ""

        evidence_buffer.append(out_str)
        if len(evidence_buffer) > 400:
            del evidence_buffer[:200]

        status = 0
        if "Status: 200" in out_str:
            status = 200
        elif "Status: 403" in out_str:
            status = 403
        elif "Status: 404" in out_str:
            status = 404
        note = out_str[:100].replace("\n", " ")
        await guard.record_tool_call(
            tool=tool_name, key_args=key_args,
            intent_id=intent_id, status=status, note=note,
        )
        return output

    agent._execute_mcp_tool = _recording_execute  # type: ignore[method-assign]

    try:
        # Siembra el hecho inicial
        if not board.facts:
            seed = f"Objetivo origin={origin}; objetivo goal={goal}"
            if hints:
                seed += "; pistas: " + " | ".join(hints)
            board.add_fact(seed, source="origin")

        empty_reason_streak = 0
        consecutive_errors = 0
        complete_reject_streak = 0
        steps = 0

        last_checkpoint = (-1, -1, -1)

        def _graph_checkpoint() -> tuple[int, int, int]:
            return (
                len(board.facts),
                sum(1 for i in board.intents if i.status == IntentStatus.CONCLUDED),
                sum(1 for i in board.intents if i.status == IntentStatus.ABANDONED),
            )

        async def _try_frontier_recovery() -> bool:
            nonlocal empty_reason_streak, consecutive_errors
            if empty_reason_streak >= FRONTIER_RECOVERY_LIMIT:
                return False

            empty_reason_streak += 1
            emit(
                "frontier_recovery",
                {"streak": empty_reason_streak, "reason": "no_open_intents"},
            )
            try:
                recovery_decision = await frontier_recovery_step(
                    agent, board, max_intents, empty_reason_streak
                )
            except Exception as exc:
                consecutive_errors += 1
                emit("error", {"phase": "frontier_recovery", "error": str(exc)})
                return False

            emit("reason", {"decision": recovery_decision, "step": steps, "recovery": True})
            if _add_decision_intents(board, recovery_decision):
                empty_reason_streak = 0
                return True

            fallback_added = _add_fallback_recovery_intents(board, max_intents)
            if fallback_added:
                emit(
                    "frontier_recovery",
                    {
                        "streak": empty_reason_streak,
                        "reason": "fallback_intents",
                        "added": fallback_added,
                    },
                )
                empty_reason_streak = 0
                return True
            return False

        while steps < max_steps and not board.completed:
            cur_checkpoint = _graph_checkpoint()
            open_intents = board.open_intents()
            skip_reason = (cur_checkpoint == last_checkpoint and open_intents)
            last_checkpoint = cur_checkpoint

            if skip_reason:
                pass
            else:
                try:
                    decision = await reason_step(agent, board, max_intents)
                except Exception as exc:
                    consecutive_errors += 1
                    emit("error", {"phase": "reason", "error": str(exc)})
                    if consecutive_errors >= 3:
                        break
                    continue
                emit("reason", {"decision": decision, "step": steps})

                complete_flag = decision.get("complete")
                if complete_flag is not None and complete_flag is not False:
                    full_evidence = "\n".join(evidence_buffer)
                    reason_text = str(
                        decision.get("reason")
                        or (complete_flag if isinstance(complete_flag, str) else "")
                    ).strip()
                    evidence_ids = [
                        fid for fid in (decision.get("evidence") or []) if board.get_fact(fid)
                    ]
                    grounded, why = _completion_is_grounded(board.goal, full_evidence)
                    fake = _unverified_flags(reason_text, full_evidence)

                    reject_reason: Optional[str] = None
                    if complete_flag is not True:
                        reject_reason = "La determinación de finalización no usó complete=true explícito, se trata como no alcanzado"
                    elif not reason_text:
                        reject_reason = "La declaración de finalización carece de una explicación en reason"
                    elif _has_negation(reason_text):
                        reject_reason = f"El motivo de finalización contiene una expresión negativa, en realidad no se alcanzó: {reason_text[:80]}"
                    elif not evidence_ids:
                        reject_reason = "La declaración de finalización no referencia ningún fact confirmado como evidencia"
                    elif not grounded:
                        reject_reason = why
                    elif fake:
                        reject_reason = f"El flag {fake[0]} referenciado en la declaración de finalización no aparece en la salida real de ninguna herramienta"

                    if reject_reason is None:
                        board.mark_complete(reason_text)
                        emit("completed", {"reason": reason_text})
                        break
                    board.add_fact(f"[Finalización rechazada] {reject_reason}; continúa la exploración y verificación", source="verify")
                    emit("complete_rejected", {"reason": reject_reason})
                    complete_reject_streak += 1
                    if complete_reject_streak >= 3:
                        break
                    continue
                complete_reject_streak = 0

                _add_decision_intents(board, decision)

                open_intents = board.open_intents()
                if not open_intents:
                    await _try_frontier_recovery()
                    open_intents = board.open_intents()
                    if empty_reason_streak >= FRONTIER_RECOVERY_LIMIT and not open_intents:
                        break
                    if not open_intents:
                        continue
                empty_reason_streak = 0

            # ── Selecciona el batch de intents a explorar ──────────────────────────────
            open_intents = board.open_intents()
            if not open_intents:
                await _try_frontier_recovery()
                open_intents = board.open_intents()
                if empty_reason_streak >= FRONTIER_RECOVERY_LIMIT and not open_intents:
                    break
                if not open_intents:
                    continue
            empty_reason_streak = 0

            batch = open_intents[:max_parallel]
            is_parallel = len(batch) > 1 and max_parallel > 1

            for intent in batch:
                board.claim_intent(intent.id)
                emit("explore_start", {"intent_id": intent.id, "description": intent.description})

            if is_parallel:
                results = await _explore_batch(
                    agent, board, batch,
                    max_tool_rounds=max_tool_rounds,
                    evidence_buffer=evidence_buffer,
                    stream_sink=stream_sink,
                )
            else:
                intent = batch[0]
                worker = ExploreWorker(intent_id=intent.id, evidence_buffer=list(evidence_buffer), tc_start=len(board.tool_calls))
                _current_worker.set(worker)
                try:
                    advanced, fact = await explore_step(
                        agent, board, intent,
                        max_tool_rounds=max_tool_rounds,
                        evidence_buffer=worker.evidence_buffer,
                        stream_sink=stream_sink,
                    )
                except Exception as exc:
                    advanced, fact = False, ""
                    results = [(intent, False, f"Excepción durante la exploración: {exc}", True)]
                else:
                    results = [(intent, advanced, fact, False)]
                finally:
                    _current_worker.set(None)
                    evidence_buffer.extend(
                        e for e in worker.evidence_buffer if e not in evidence_buffer
                    )

            any_error = False
            for intent, advanced, fact, is_error in results:
                if is_error:
                    consecutive_errors += 1
                    board.abandon_intent(intent.id, note=fact[:120])
                    emit("error", {"phase": "explore", "intent_id": intent.id, "error": fact})
                    any_error = True
                    continue
                consecutive_errors = 0

                full_evidence = "\n".join(evidence_buffer)
                fake_flags = _unverified_flags(fact, full_evidence)
                if fake_flags:
                    note = f"Se declaró haber obtenido el flag {fake_flags[0]} pero no aparece en la salida de ninguna herramienta real; se considera alucinación y se rechaza"
                    board.abandon_intent(intent.id, note=note)
                    board.add_fact(f"[No verificado] Exploración {intent.id}: {note}", source="verify")
                    emit("hallucination", {"intent_id": intent.id, "flags": fake_flags})
                elif advanced and fact:
                    new_fact = board.conclude_intent(intent.id, fact)
                    emit(
                        "conclude",
                        {"intent_id": intent.id, "fact": new_fact.id if new_fact else "", "desc": fact},
                    )
                    captured = _extract_flags(fact)
                    if captured and _goal_wants_flag(board.goal):
                        board.mark_complete(
                            f"Flag verificado y obtenido desde {new_fact.id if new_fact else 'fact'}: {captured[0]}"
                        )
                        emit("completed", {"reason": board.complete_reason})
                        break
                else:
                    board.abandon_intent(intent.id, note=(fact or "sin avance")[:120])
                    emit("abandon", {"intent_id": intent.id, "note": fact})

            if board.completed:
                break

            if any_error and consecutive_errors >= 3:
                break

            steps += len(batch)
            agent.context.state.save()

            if is_parallel:
                summaries = []
                for intent, advanced, fact, is_error in results:
                    tag = "✓" if advanced else ("✗ ERR" if is_error else "—")
                    summaries.append(f"[{intent.id} {tag}] {fact[:120]}")
                agent.context.add_assistant_message(
                    "[Resumen de exploración paralela]\n" + "\n".join(summaries)
                )
    finally:
        agent._execute_mcp_tool = original_execute  # type: ignore[method-assign]

    reason = (
        board.complete_reason
        if board.completed
        else ("Frontera de exploración agotada" if steps < max_steps else "Se alcanzó el límite del presupuesto de seguridad")
    )
    return SolveResult(
        completed=board.completed,
        reason=reason,
        steps=steps,
        facts=len(board.facts),
        board=board,
    )


async def _explore_batch(
    agent: AgentContext,
    board: Blackboard,
    intents: list[BoardIntent],
    *,
    max_tool_rounds: int,
    evidence_buffer: list[str],
    stream_sink: Any = None,
) -> list[tuple[BoardIntent, bool, str, bool]]:
    """Run multiple intent explorations concurrently via asyncio.gather.

    Returns list of (intent, advanced, fact, is_error) tuples.
    """

    async def _run_one(intent: BoardIntent) -> tuple[BoardIntent, bool, str, bool]:
        worker = ExploreWorker(
            intent_id=intent.id,
            evidence_buffer=list(evidence_buffer),
            tc_start=len(board.tool_calls),
        )
        sink = IntentStreamSink(stream_sink, intent.id) if stream_sink else None
        ctx_token = _current_worker.set(worker)
        try:
            advanced, fact = await explore_step(
                agent, board, intent,
                max_tool_rounds=max_tool_rounds,
                evidence_buffer=worker.evidence_buffer,
                stream_sink=sink,
                skip_context_write=True,
            )
            return (intent, advanced, fact, False)
        except Exception as exc:
            return (intent, False, f"Excepción durante la exploración: {exc}", True)
        finally:
            _current_worker.reset(ctx_token)
            for e in worker.evidence_buffer:
                if e not in evidence_buffer:
                    evidence_buffer.append(e)

    raw = await asyncio.gather(*(_run_one(i) for i in intents), return_exceptions=True)
    results: list[tuple[BoardIntent, bool, str, bool]] = []
    for idx, r in enumerate(raw):
        if isinstance(r, BaseException):
            results.append((intents[idx], False, f"Excepción durante la exploración: {r}", True))
        else:
            results.append(r)
    return results

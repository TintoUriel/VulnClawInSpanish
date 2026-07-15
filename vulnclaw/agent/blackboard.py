"""Modelo de pizarra (blackboard) — búsqueda en espacio de estados impulsada por los primitivos Fact / Intent.

El pentest se modela como una búsqueda dirigida en un espacio de estados desde origin hacia goal:
- Fact:   hecho objetivo ya confirmado (punto de apoyo de la exploración)
- Intent: dirección de exploración declarada (un paso aún no ejecutado); parte de uno o más Fact y, al concluir, produce un nuevo Fact
- La condición de término la determina «meta alcanzada / frontera de exploración agotada / presupuesto de seguridad», no un número fijo de rondas

Este modelo es una estructura de datos pura, se adjunta a SessionState para persistirse, y lo impulsa el bucle OODA de solver.py.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class IntentStatus(str, Enum):
    OPEN = "open"  # declarado, pendiente de exploración
    EXPLORING = "exploring"  # en exploración
    CONCLUDED = "concluded"  # concluido, produjo un Fact
    ABANDONED = "abandoned"  # explorado pero no hizo avanzar la meta, abandonado


class BoardFact(BaseModel):
    id: str
    description: str
    source: str = ""  # origen (bootstrap / explore:i003 / hint ...)


class BoardIntent(BaseModel):
    id: str
    from_facts: list[str] = Field(default_factory=list)  # ids de los Fact de partida
    description: str
    status: IntentStatus = IntentStatus.OPEN
    result_fact: str | None = None  # id del Fact producido al concluir
    note: str = ""  # motivo de abandono / nota


class ToolCallRecord(BaseModel):
    """Registro compacto de una llamada a herramienta ya ejecutada — evita repetir la misma herramienta+parámetros entre intents."""
    tool: str
    key_args: str = ""
    intent_id: str = ""
    status: int = 0
    note: str = ""


class Blackboard(BaseModel):
    """Grafo de Fact/Intent. Crece desde origin hasta goal.

    Inspirado en Cairn: además de Fact/Intent, mantiene un **registro de
    ejecución tool_calls**; cada herramienta invocada durante un explore
    se registra aquí. Los prompts de contexto de Reason y Explore incluyen
    un resumen de este registro, para que el LLM pueda ver "qué ya se hizo"
    y evitar repeticiones.
    """

    origin: str = ""
    goal: str = ""
    facts: list[BoardFact] = Field(default_factory=list)
    intents: list[BoardIntent] = Field(default_factory=list)
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    completed: bool = False
    complete_reason: str = ""
    fact_seq: int = Field(default=0, exclude=True)
    intent_seq: int = Field(default=0, exclude=True)

    def model_post_init(self, __context: Any) -> None:
        if self.facts and self.fact_seq == 0:
            nums = [int(f.id[1:]) for f in self.facts if f.id[1:].isdigit()]
            self.fact_seq = max(nums) if nums else len(self.facts)
        if self.intents and self.intent_seq == 0:
            nums = [int(i.id[1:]) for i in self.intents if i.id[1:].isdigit()]
            self.intent_seq = max(nums) if nums else len(self.intents)

    # ── Fact ────────────────────────────────────────────────────────
    def add_fact(self, description: str, source: str = "") -> BoardFact:
        self.fact_seq += 1
        fact = BoardFact(id=f"f{self.fact_seq:03d}", description=description.strip(), source=source)
        self.facts.append(fact)
        return fact

    def get_fact(self, fact_id: str) -> BoardFact | None:
        return next((f for f in self.facts if f.id == fact_id), None)

    def fact_ids(self) -> list[str]:
        return [f.id for f in self.facts]

    # ── Intent ──────────────────────────────────────────────────────
    def add_intent(self, description: str, from_facts: list[str] | None = None) -> BoardIntent:
        self.intent_seq += 1
        valid_from = [fid for fid in (from_facts or []) if self.get_fact(fid)]
        intent = BoardIntent(
            id=f"i{self.intent_seq:03d}",
            from_facts=valid_from,
            description=description.strip(),
        )
        self.intents.append(intent)
        return intent

    def get_intent(self, intent_id: str) -> BoardIntent | None:
        return next((i for i in self.intents if i.id == intent_id), None)

    def open_intents(self) -> list[BoardIntent]:
        return [i for i in self.intents if i.status == IntentStatus.OPEN]

    def active_intents(self) -> list[BoardIntent]:
        """Intents sin concluir (open + exploring), para determinar si la frontera de exploración se agotó."""
        return [i for i in self.intents if i.status in (IntentStatus.OPEN, IntentStatus.EXPLORING)]

    def claim_intent(self, intent_id: str) -> BoardIntent | None:
        intent = self.get_intent(intent_id)
        if intent and intent.status == IntentStatus.OPEN:
            intent.status = IntentStatus.EXPLORING
        return intent

    def conclude_intent(self, intent_id: str, fact_description: str, source: str = "") -> BoardFact | None:
        """La exploración llegó a una conclusión valiosa → produce un Fact y lo enlaza."""
        intent = self.get_intent(intent_id)
        if intent is None:
            return None
        fact = self.add_fact(fact_description, source=source or f"explore:{intent_id}")
        intent.status = IntentStatus.CONCLUDED
        intent.result_fact = fact.id
        return fact

    def abandon_intent(self, intent_id: str, note: str = "") -> BoardIntent | None:
        intent = self.get_intent(intent_id)
        if intent is not None:
            intent.status = IntentStatus.ABANDONED
            if note:
                intent.note = note
        return intent

    def mark_complete(self, reason: str) -> None:
        self.completed = True
        self.complete_reason = reason.strip()

    # ── Tool call memory ───────────────────────────────────────────
    def record_tool_call(
        self, tool: str, key_args: str, intent_id: str = "",
        status: int = 0, note: str = "",
    ) -> None:
        self.tool_calls.append(ToolCallRecord(
            tool=tool, key_args=key_args[:200], intent_id=intent_id,
            status=status, note=note[:120],
        ))
        if len(self.tool_calls) > 200:
            del self.tool_calls[:100]

    def has_called(self, tool: str, key_args: str) -> bool:
        return any(
            tc.tool == tool and tc.key_args == key_args[:200]
            for tc in self.tool_calls
        )

    def tool_call_summary(self, max_lines: int = 40) -> str:
        if not self.tool_calls:
            return ""
        seen: dict[str, str] = {}
        for tc in self.tool_calls:
            key = f"{tc.tool}({tc.key_args})"
            if key not in seen:
                seen[key] = f"  {tc.intent_id or '-'}: {tc.tool}({tc.key_args})" + (
                    f" → {tc.note}" if tc.note else ""
                )
        lines = list(seen.values())[-max_lines:]
        return "\n".join(lines)

    # ── Renderizado ────────────────────────────────────────────────────────────
    def to_prompt_graph(self, *, include_concluded: bool = True) -> str:
        """Renderiza el grafo como texto compacto (estilo YAML) para que lo lea el LLM."""
        lines: list[str] = [f"goal: {self.goal or '(sin definir)'}", f"origin: {self.origin or '(sin definir)'}"]

        lines.append("facts:")
        if self.facts:
            for fact in self.facts:
                src = f"  ({fact.source})" if fact.source else ""
                lines.append(f"  - {fact.id}: {fact.description}{src}")
        else:
            lines.append("  (ninguno todavía)")

        lines.append("intents:")
        shown = self.intents if include_concluded else self.active_intents()
        if shown:
            for intent in shown:
                frm = f" from={','.join(intent.from_facts)}" if intent.from_facts else ""
                res = f" -> {intent.result_fact}" if intent.result_fact else ""
                note = f"  // {intent.note}" if intent.note else ""
                lines.append(f"  - {intent.id} [{intent.status.value}]{frm}{res}: {intent.description}{note}")
        else:
            lines.append("  (ninguno todavía)")

        tc_summary = self.tool_call_summary(30)
        if tc_summary:
            lines.append("executed_tools (prohibido repetir una herramienta+parámetros ya ejecutada):")
            lines.append(tc_summary)

        return "\n".join(lines)

    def get_summary(self) -> dict[str, object]:
        status_counts: dict[str, int] = {}
        for intent in self.intents:
            status_counts[intent.status.value] = status_counts.get(intent.status.value, 0) + 1
        return {
            "completed": self.completed,
            "facts": len(self.facts),
            "intents": len(self.intents),
            "open_intents": len(self.open_intents()),
            "intent_status_counts": status_counts,
            "complete_reason": self.complete_reason,
        }

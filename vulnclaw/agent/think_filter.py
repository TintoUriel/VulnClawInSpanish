"""VulnClaw Think Tag Filter — strip <think>/<thinking> blocks from LLM output.

Modificado por: Nyaecho
Fecha de modificación: 2026-07-08
Motivo de la modificación: Corrección V2 — Las funciones de utilidad de texto
         puro se movieron a config/text_utils.py; aquí se vuelven a exportar
         para mantener la compatibilidad hacia atrás en la capa agent/.
"""

from __future__ import annotations

from vulnclaw.config.text_utils import format_think_tags, strip_think_tags  # noqa: F401

__all__ = ["strip_think_tags", "format_think_tags"]

"""Context builder — assemble message arrays for the LLM from chat history."""

from __future__ import annotations

from typing import Any

from vulnclaw.i18n import _


class ContextBuilder:
    """Build OpenAI-compatible message arrays from chat history.

    Only user and assistant text messages are included in the
    context — tool results and system messages are excluded to
    keep token usage low.
    """

    def __init__(self, system_prompt: str | None = None) -> None:
        self._system_prompt = system_prompt or _("tui.agent.context.system_prompt")

    def build(
        self,
        history: list[dict[str, str]],
        user_text: str,
    ) -> list[dict[str, Any]]:
        """Build the full messages list for the LLM API call.

        Parameters
        ----------
        history:
            List of ``{"role": "user"|"assistant", "content": str}`` dicts.
        user_text:
            The current user input to append.

        Returns
        -------
        OpenAI-format messages list with system prompt + history + user message.
        """
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt},
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": user_text})
        return messages

    def from_message_data(
        self,
        message_data: list,
        user_text: str,
    ) -> list[dict[str, Any]]:
        """Build context from ChatMessageData objects (services.history)."""
        history: list[dict[str, str]] = []
        for msg in message_data:
            if msg.type in ("user", "assistant"):
                history.append({"role": msg.type, "content": msg.content})
        return self.build(history, user_text)

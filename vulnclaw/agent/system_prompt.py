"""Dynamic system prompt assembly for AgentCore."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from vulnclaw.agent.prompts import AUTO_PENTEST_INSTRUCTION, RECON_INSTRUCTION, build_system_prompt

if TYPE_CHECKING:
    from vulnclaw.agent.context import TaskConstraints


def build_dynamic_system_prompt(
    *,
    target: Optional[str],
    phase: Optional[str],
    skill_context: Optional[str],
    mcp_tools: list[dict],
    enable_personnel_dim: bool,
    auto_mode: bool,
    user_input: Optional[str],
    kb_context: str,
    task_constraints: Optional["TaskConstraints"] = None,
) -> str:
    """Build the dynamic system prompt for one turn."""
    prompt = build_system_prompt(
        target=target,
        phase=phase,
        skill_context=skill_context,
        mcp_tools=mcp_tools,
        enable_personnel_dim=enable_personnel_dim,
    )

    if auto_mode:
        prompt += "\n\n" + AUTO_PENTEST_INSTRUCTION

    if user_input:
        recon_triggers = [
            "recolectar",
            "recopilar",
            "recolección de información",
            "reconocimiento",
            "recon",
            "osint",
            "ingeniería social",
            "social engineering",
            "investigar",
            "autor",
            "personas",
            "inteligencia",
            "analizar objetivo",
            "análisis de objetivo",
            "descubrimiento de activos",
            "subdominio",
        ]
        if any(trigger in user_input.lower() for trigger in recon_triggers):
            if enable_personnel_dim:
                prompt += "\n\n" + RECON_INSTRUCTION
            else:
                recon_no_personnel = RECON_INSTRUCTION.replace(
                    "### Dimensión 4: Información de personal ⚡ Activación condicional",
                    "### Dimensión 4: Información de personal ⚡ Activación condicional"
                    " (no activada en esta ejecución — el usuario no mencionó necesidades de"
                    " ingeniería social/seguimiento de personal)",
                )
                recon_no_personnel = (
                    recon_no_personnel.replace(
                        "- [ ] Nombre y cargo",
                        "- [x] Nombre y cargo (no activado, omitido)",
                    )
                    .replace(
                        "- [ ] Fecha de nacimiento y teléfono de contacto",
                        "- [x] Fecha de nacimiento y teléfono de contacto (no activado, omitido)",
                    )
                    .replace(
                        "- [ ] Dirección de correo electrónico",
                        "- [x] Dirección de correo electrónico (no activado, omitido)",
                    )
                    .replace(
                        "- [ ] Cuentas de redes sociales (Bilibili, Weibo, Zhihu, Twitter, LinkedIn, GitHub)",
                        "- [x] Cuentas de redes sociales (no activado, omitido)",
                    )
                    .replace(
                        "- [ ] Correlación entre plataformas (buscar el nombre de usuario/correo en"
                        " otras plataformas, revisar correos en el historial de commits)",
                        "- [x] Correlación entre plataformas (no activado, omitido)",
                    )
                )
                prompt += "\n\n" + recon_no_personnel

    if kb_context:
        prompt += "\n\n" + kb_context

    if task_constraints is not None:
        constraints_block = task_constraints.to_prompt_block()
        if constraints_block:
            prompt += "\n\n" + constraints_block

    return prompt

"""Prompt/round-context helpers for AgentCore."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vulnclaw.agent.agent_context import AgentContext



def build_round_context(agent: AgentContext, round_num: int, max_rounds: int) -> str:
    """Build context string for the current round in auto loop."""
    state = agent.context.state
    constraints_summary = ""
    constraints_block = (
        state.get_constraints_prompt_block()
        if hasattr(state, "get_constraints_prompt_block")
        else ""
    )
    if constraints_block:
        constraints_summary = f"\n\n{constraints_block}"

    reasoning_summary = ""
    session_config = getattr(agent.config, "session", None)
    reasoning_enabled = getattr(session_config, "reasoning_state_enabled", True)
    if reasoning_enabled:
        reasoning = getattr(state, "reasoning", None)
        reasoning_block = (
            reasoning.to_prompt_block()
            if hasattr(reasoning, "to_prompt_block")
            else ""
        )
        if reasoning_block:
            reasoning_summary = f"\n\n{reasoning_block}"

    reflexion_summary = ""
    reflexion_enabled = getattr(session_config, "reflexion_enabled", True)
    reflexion = getattr(agent.runtime, "reflexion", None)
    if reflexion_enabled and hasattr(reflexion, "to_prompt_block"):
        reflexion_block = reflexion.to_prompt_block()
        if reflexion_block:
            reflexion_summary = f"\n\n{reflexion_block}"
        if hasattr(reflexion, "to_reflection_prompt"):
            reflection_block = reflexion.to_reflection_prompt()
            if reflection_block:
                reflexion_summary += f"\n\n{reflection_block}"

    findings_summary = ""
    if state.findings:
        findings_summary = f"\nVulnerabilidades encontradas: {len(state.findings)}"
        for finding in state.findings[-5:]:
            findings_summary += (
                f"\n  - [{finding.severity}] {finding.title}: {finding.evidence[:100]}"
            )

    user_hint_directive = ""
    if round_num <= agent.runtime.user_vuln_hint_rounds and agent.runtime.user_vuln_hint:
        user_hint_directive = (
            f"\n\n{'=' * 50}\n"
            f"[INDICACIÓN EXPLÍCITA DEL USUARIO — Ronda {round_num}/{agent.runtime.user_vuln_hint_rounds}]\n"
            f"{agent.runtime.user_vuln_hint}\n"
            f"{'=' * 50}\n"
        )
        agent.runtime.user_vuln_hint_rounds -= 1

    steps_summary = ""
    if state.executed_steps:
        recent_steps = state.executed_steps[-8:]
        steps_summary = f"\nPasos ejecutados recientemente: {len(state.executed_steps)} en total"
        for step in recent_steps:
            steps_summary += f"\n  - {step[:150]}"

    failed_summary = ""
    if state.executed_steps:
        failed_attempts = []
        failure_markers = [
            "fallo",
            "no hay",
            "misma respuesta",
            "bloqueado",
            "404",
            "no",
            "sin éxito",
            "inválido",
            "error",
            "failed",
            "still",
            "no se encontró",
            "sin resultado",
            "timeout",
            "prohibido",
            "denied",
            "no existe",
            "no se puede",
            "no puede",
            "incorrecto",
        ]
        for step in state.executed_steps:
            if any(marker in step.lower() for marker in failure_markers):
                failed_attempts.append(step[:150])
        if failed_attempts:
            failed_summary = "\nHistorial de fallos (no repitas estas acciones):"
            for failure in failed_attempts[-10:]:
                failed_summary += f"\n  ❌ {failure}"

    recon_summary = ""
    if state.recon_data:
        recon_summary = f"\nDatos de reconocimiento: {list(state.recon_data.keys())}"

    resume_summary = ""
    if getattr(state, "resume_summary", ""):
        resume_summary = f"\n\n{state.resume_summary}"

    notes_summary = ""
    if state.notes:
        notes_summary = f"\nNotas importantes: {'; '.join(state.notes[-5:])}"

    facts_summary = ""
    if hasattr(state, "confirmed_facts") and state.confirmed_facts:
        facts_summary = "\nHechos confirmados (verificados por herramientas, confiables):"
        for fact in state.confirmed_facts[-8:]:
            facts_summary += f"\n  ✅ {fact[:150]}"

    assumptions_summary = ""
    if hasattr(state, "unverified_assumptions") and state.unverified_assumptions:
        assumptions_summary = "\n⚠️ Hipótesis no verificadas (base del razonamiento pero sin confirmar, podrían ser erróneas):"
        for assumption in state.unverified_assumptions[-5:]:
            assumptions_summary += f"\n  ❓ {assumption[:150]}"
        assumptions_summary += "\n→ ¡Si alguna hipótesis es errónea, todo el razonamiento basado en ella queda invalidado! Prioriza verificar las hipótesis clave."

    path_warning = ""
    same_path_fails = agent.runtime.same_path_fail_count

    if state.executed_steps:
        recent = state.executed_steps[-8:]
        if len(recent) >= 5:
            recent_text = " ".join(recent).lower()
            stuck_indicators = ["get=", "post=", "payload", "parámetro", "intento"]
            stuck_count = sum(
                1 for indicator in stuck_indicators if recent_text.count(indicator) >= 3
            )
            if stuck_count >= 1:
                path_warning = (
                    "\n\n⚠️ Ya llevas varias rondas intentando en la ruta actual sin lograr un avance."
                    "\n¿Existe alguna otra ruta de explotación más simple? Revisa nuevamente el código fuente/la información."
                    "\nEnumera todas las rutas posibles y cambia a la más simple."
                )

    path_switch_warning = ""
    if not reflexion_enabled and same_path_fails >= 3:
        path_switch_warning = (
            f"\n\n🔴 Instrucción obligatoria de cambio de ruta: ¡ya fallaste {same_path_fails} veces en la misma ruta de ataque!"
            f"\nDebes ejecutar de inmediato los siguientes pasos:"
            f"\n1. Detente y enumera al menos 3 rutas de ataque alternativas **completamente distintas**"
            f"\n   (no se trata de cambiar el valor del payload, sino el método de ataque: por ejemplo, pasar de"
            f" 'bypass de regex' a 'lectura de archivo con pseudo-protocolo' o 'bypass por array')"
            f"\n2. Ordena estas rutas alternativas de menor a mayor dificultad"
            f"\n3. Elige la ruta alternativa más simple y comienza a intentarla"
            f"\n4. Antes de probar la nueva ruta, dedica 1 ronda a verificar tu nueva hipótesis"
            f"\n\n⚠️ ¡Prohibido seguir intentando en la misma ruta solo cambiando el valor del payload!"
        )
        agent.runtime.same_path_fail_count = 0
        agent.runtime.path_switch_forced = True

    assumption_reminder = ""
    if round_num > 2 and round_num % 3 == 0:
        assumption_reminder = (
            "\n\n🧠 Punto de control de verificación de hipótesis:"
            "\nAntes de dar el siguiente paso, dedica 10 segundos a preguntarte:"
            "\n1. ¿En qué hipótesis se basa mi razonamiento actual?"
            "\n2. ¿Ya verifiqué estas hipótesis? ¿O solo las estoy dando por sentadas?"
            "\n3. Si alguna hipótesis es errónea, ¿se derrumba toda mi cadena de razonamiento?"
            "\n4. ¿Puedo dedicar 1 ronda a enviar una solicitud para verificar la hipótesis más crítica?"
            "\n\n❌ Hipótesis fatales comunes: preg_replace solo reemplaza la primera coincidencia / la simulación en Python = el comportamiento del servidor / el nombre del parámetro es tal valor"
        )

    python_timeout_warning = ""
    python_timeout_rounds = agent.runtime.python_timeout_rounds
    if python_timeout_rounds >= 1:
        python_timeout_warning = (
            "\n\n⚠️ **Advertencia de ejecución de código**: el script de Python de la ronda anterior superó el tiempo límite."
            "\nProhibido escribir scripts complejos de más de 10 líneas."
            "\nPrioriza el uso de las herramientas existentes (fetch/python_execute) en lugar de escribir tu propio código de scraping/parsing."
            "\nProhibido volver a ejecutar el mismo bloque extenso de script repetidamente."
        )

    dead_loop_warning = ""
    rounds_no_progress = agent.runtime.rounds_without_progress
    stale_threshold = agent.config.session.stale_rounds_threshold

    blocked_targets_warning = ""
    blocked_targets = agent.runtime.blocked_targets
    if blocked_targets:
        blocked_targets_warning = (
            f"\n\n🚨 **Advertencia de objetivo inaccesible**: los siguientes objetivos han fallado varias veces consecutivas, prohibido intentarlo de nuevo:"
            f"\n{chr(10).join(f'  ❌ {target} — confirmado como inalcanzable' for target in blocked_targets)}"
            f"\n\nDebes:"
            f"\n1. Dejar de acceder de inmediato a los objetivos anteriores"
            f"\n2. Enfocarte en otros objetivos activos"
            f"\n3. Si no hay otros objetivos, pasar a la explotación profunda de las vulnerabilidades ya confirmadas"
            f"\n4. No sigas desperdiciando rondas intentando conectarte a objetivos inalcanzables"
        )

    if rounds_no_progress >= stale_threshold:
        dead_loop_warning = (
            f"\n\n🔴 Advertencia grave: ¡llevas {rounds_no_progress} rondas consecutivas sin ningún hallazgo nuevo!"
            f"\nEsto indica que estás en un bucle infinito. Debes tomar de inmediato una de las siguientes medidas:"
            f"\n1. 🔥 Volver a obtener el código fuente completo (con python_execute + strip_tags)"
            f"\n2. 🔥 Probar una ruta de ataque completamente distinta (cambiar el nombre del parámetro, el método, la herramienta)"
            f"\n3. 🔥 Si la información actual es insuficiente, reconócelo e intenta otros métodos de recolección de información"
            f"\n4. 🔥 ¡Deja de repetir la misma operación! Revisa el historial de fallos y elige una nueva dirección"
            f"\n\n⚠️ ¡Repetir la misma operación de nuevo no producirá un resultado distinto!"
        )
    elif rounds_no_progress >= max(stale_threshold // 2, 2):
        dead_loop_warning = (
            f"\n\n⚠️ Advertencia: llevas {rounds_no_progress} rondas consecutivas sin hallazgos nuevos."
            f"\nVerifica: ¿estás repitiendo la misma operación? ¿hay otras rutas sin probar?"
            f"\nSi el método actual no funciona, cambia de inmediato a otro método."
        )

    flag_warning = ""
    claimed_flag = agent.runtime.claimed_flag
    flag_verified = agent.runtime.flag_verified
    if claimed_flag and flag_verified:
        flag_warning = (
            f"\n\n✅ FLAG verificada: {claimed_flag}"
            f"\n¡Tu tarea está completa! Resume brevemente el proceso de resolución y marca [DONE] para finalizar."
            f"\n⚠️ ¡No vuelvas a verificar ni a enviar solicitudes repetidas! Resume y finaliza de inmediato."
        )
    elif claimed_flag and not flag_verified:
        flag_warning = (
            f"\n\n⚠️ Anteriormente afirmaste haber encontrado la flag: {claimed_flag}"
            f"\n¡Pero esta flag no ha sido verificada de forma independiente! Debes:"
            f"\n1. Reenviar el payload con una herramienta para confirmar que el resultado es reproducible"
            f"\n2. O verificarla de forma cruzada con un método distinto (por ejemplo, leer el mismo contenido con otra función/ruta)"
            f"\n3. Si la verificación falla, debes reconocer que la flag anterior era incorrecta y continuar resolviendo"
            f"\nNo marques [DONE] hasta completar la verificación"
        )

    ctf_mode_warning = ""
    is_ctf = agent.runtime.is_ctf_mode
    if is_ctf and not claimed_flag:
        ctf_mode_warning = (
            "\n\n🔴 Modo de resolución CTF — tu tarea es encontrar y verificar la flag."
            "\nActualmente aún no has encontrado ninguna flag, prohibido marcar [DONE]."
            "\nAnaliza la información disponible y elige la ruta de ataque más prometedora para continuar avanzando."
            "\nSi la ruta actual está bloqueada, intenta cambiar a otra."
        )
    elif is_ctf and claimed_flag and not flag_verified:
        ctf_mode_warning = (
            "\n\n🔴 Modo de resolución CTF — afirmaste haber encontrado la flag pero no la has verificado."
            "\nDebes verificar la autenticidad de la flag con una herramienta antes de poder marcar [DONE]."
            "\nSi la verificación falla, debes seguir buscando la flag correcta."
        )

    recon_dim_status = ""
    if agent.runtime.is_recon_phase:
        dim_status_text = state.get_recon_status_text()
        is_complete = state.is_recon_complete()
        rounds_no_progress = agent.runtime.rounds_without_progress

        recon_dim_status = f"\n\n📊 Progreso de las dimensiones de recolección de información:\n{dim_status_text}"
        if not is_complete:
            recon_dim_status += (
                "\n\n🔴 ¡La recolección de información no está completa! Aún quedan dimensiones sin verificar, prohibido marcar [DONE]."
                "\nContinúa verificando las dimensiones pendientes, asegurándote de completar al menos una ronda en cada una."
            )
        elif (is_complete and rounds_no_progress >= 3) or (rounds_no_progress >= 8 + 5):
            output_dir = str(agent.config.session.output_dir.resolve())
            if is_complete:
                trigger_reason = f"todas las dimensiones están completas ✅, {rounds_no_progress} rondas consecutivas sin avance"
            else:
                trigger_reason = f"{rounds_no_progress} rondas consecutivas sin avance (válvula de seguridad 8+5)"
            recon_dim_status += (
                f"\n\n🔴 ★★★ Cambio forzado de fase: reconocimiento → explotación ★★★\n"
                f"{trigger_reason}.\n"
                f"Debes cambiar de inmediato a la 【fase de explotación de vulnerabilidades】, en lugar de seguir recolectando información o guardando informes.\n\n"
                f"★ Ejecuta de inmediato lo siguiente:\n"
                f"1. En tu respuesta, indica «cambiar a descubrimiento de vulnerabilidades» o «fase: vuln_discovery»\n"
                f"2. Basándote en los resultados de reconocimiento ya recolectados (perfil del objetivo/sitios vecinos/fugas de API, etc.),\n"
                f"   realiza una explotación real sobre la superficie de ataque de mayor valor\n"
                f"3. 【Prohibido】seguir guardando informes de reconocimiento o invocar herramientas de recolección de información\n"
                f"4. 【Prohibido】repetir hallazgos ya existentes; debe haber nuevos pasos de verificación reales\n\n"
                f"★ Directorio de salida (el informe de reconocimiento se guarda automáticamente por el framework, no es necesario guardarlo manualmente):\n"
                f"   {output_dir}\n"
                f"⚠️ El objetivo de esta prueba de penetración es 【lograr una explotación real de vulnerabilidades】, ¡no un informe de reconocimiento!"
            )
        if round_num < 8:
            recon_dim_status += (
                f"\n\n🔴 Garantía de rondas mínimas de recolección de información: ronda actual {round_num}, "
                f"se requieren al menos 8 rondas. Aunque parezca suficiente, continúa profundizando."
            )

    return (
        f"\n\n[Ciclo autónomo Round {round_num}/{max_rounds}]"
        f"\nObjetivo actual: {state.target or 'no establecido'}"
        f"\nFase actual: {state.phase.value}"
        f"\nDirectorio de salida: {agent.config.session.output_dir.resolve()}"
        f"{constraints_summary}"
        f"{reasoning_summary}"
        f"{reflexion_summary}"
        f"{user_hint_directive}"
        f"{findings_summary}"
        f"{facts_summary}"
        f"{assumptions_summary}"
        f"{steps_summary}"
        f"{failed_summary}"
        f"{recon_summary}"
        f"{resume_summary}"
        f"{notes_summary}"
        f"{path_warning}"
        f"{path_switch_warning}"
        f"{assumption_reminder}"
        f"{python_timeout_warning}"
        f"{blocked_targets_warning}"
        f"{dead_loop_warning}"
        f"{flag_warning}"
        f"{ctf_mode_warning}"
        f"{recon_dim_status}"
        f"\n\nBasándote en el estado actual y en todos los hallazgos anteriores, decide el siguiente paso y continúa avanzando en la prueba de penetración."
        f"\nNota: no repitas operaciones que ya realizaste antes, enfócate en avanzar al siguiente paso."
        f"\nSi encuentras pistas importantes o completas la prueba, agrega la marca [DONE] al final de tu respuesta."
    )


async def generate_attack_summary(agent: AgentContext) -> str:
    """Generate a detailed attack path summary for the cycle report."""
    state = agent.context.state

    steps = state.executed_steps[-30:] if state.executed_steps else []
    steps_text = (
        "\n".join(f"{i + 1}. {step}" for i, step in enumerate(steps)) if steps else "(sin pasos registrados)"
    )

    notes = state.notes[-20:] if state.notes else []
    notes_text = "\n".join(f"- {note}" for note in notes) if notes else "(sin observaciones registradas)"

    findings = state.findings
    if findings:
        lines = []
        for finding in findings:
            evidence = (finding.evidence or "")[:150].strip()
            lines.append(f"[{finding.severity}] {finding.title} | Evidencia: {evidence or 'ninguna'}")
        findings_text = "\n".join(lines)
    else:
        findings_text = "Ninguna"

    prompt = (
        f"Objetivo: {state.target or '?'}  |  Fase actual: {state.phase.value}\n"
        f"\n=== Pasos ejecutados ===\n{steps_text}\n"
        f"\n=== Observaciones/resultados clave ===\n{notes_text}\n"
        f"\n=== Vulnerabilidades encontradas ===\n{findings_text}\n\n"
        f"Genera un párrafo narrativo detallado en español sobre la ruta de ataque, que incluya los siguientes elementos:\n"
        f"1. Las URLs/rutas concretas probadas (por ejemplo, https://target.com/admin/login)\n"
        f"2. La técnica/herramienta concreta usada en cada paso (por ejemplo, inyección ciega con SQLMap, enumeración de directorios, escaneo de puertos con nmap)\n"
        f"3. Características clave de la respuesta (por ejemplo, diferencia de 155 bytes de longitud, error HTTP 500 reflejado)\n"
        f"4. La relación entre la vulnerabilidad y la superficie de ataque (por ejemplo, se descubrió /manager/html mediante enumeración de directorios, coincidiendo con el CVE-2023-44487)\n"
        f"5. El estado del descubrimiento de subdominios (por ejemplo, se encontraron api.target.com, cms.target.com, etc.)\n"
        f"Requisitos de formato: narrativa en párrafos naturales, sin listas, entre 200 y 400 palabras, en español puro, sin etiquetas <thinking>."
    )

    try:
        client = agent._get_client()
        messages = [{"role": "user", "content": prompt}]
        from vulnclaw.agent.llm_client import build_chat_completion_kwargs

        response = client.chat.completions.create(
            **build_chat_completion_kwargs(
                agent,
                messages,
                max_tokens=800,
                temperature=0.3,
            )
        )
        if response and response.choices:
            raw = response.choices[0].message.content or ""
            from vulnclaw.agent.think_filter import strip_think_tags

            return strip_think_tags(raw).strip()
    except Exception:
        pass
    return ""

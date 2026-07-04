"""Bounded multi-agent coordination for parallel attack-surface work."""

from __future__ import annotations

import asyncio
import copy
import re
from dataclasses import dataclass, field
from typing import Any, Callable

from vulnclaw.agent.context import SessionState, VulnerabilityFinding


@dataclass(frozen=True)
class AttackSurface:
    """A concrete surface a child agent can investigate."""

    target: str
    kind: str = "surface"
    reason: str = ""


@dataclass
class ParallelAgentRunResult:
    """Summary of a parallel multi-agent run."""

    root_results: list[Any] = field(default_factory=list)
    worker_results: list[Any] = field(default_factory=list)
    surfaces: list[AttackSurface] = field(default_factory=list)
    waves_completed: int = 0


AgentFactory = Callable[[], Any]


def extract_attack_surfaces(session: SessionState, *, limit: int = 20) -> list[AttackSurface]:
    """Extract high-value concrete surfaces from the current session state."""
    surfaces: list[AttackSurface] = []

    for service in session.recon_data.get("network_services", []) or []:
        if not isinstance(service, dict):
            continue
        host = str(service.get("host", "") or "").strip()
        port = service.get("port")
        proto = str(service.get("protocol", "tcp") or "tcp").strip()
        service_name = str(service.get("service", "") or "").strip()
        if not host or not port:
            continue
        surfaces.append(
            AttackSurface(
                target=f"{host}:{port}",
                kind="service",
                reason=f"{proto}/{service_name or 'unknown'} discovered during network scan",
            )
        )

    for scan in session.recon_data.get("network_scans", []) or []:
        if not isinstance(scan, dict):
            continue
        for weak_link in scan.get("weak_links", []) or []:
            if not isinstance(weak_link, dict):
                continue
            target = str(weak_link.get("target", "") or "").strip()
            if target:
                surfaces.append(
                    AttackSurface(
                        target=target,
                        kind="weak_link",
                        reason=str(weak_link.get("reason", "") or "weak-link candidate"),
                    )
                )

    for key, kind in (("subdomains", "host"), ("paths", "path")):
        for value in session.recon_data.get(key, []) or []:
            target = str(value).strip()
            if target:
                surfaces.append(AttackSurface(target=target, kind=kind, reason=f"recon {key}"))

    for finding in session.findings:
        location = _extract_location(finding)
        if location:
            surfaces.append(
                AttackSurface(
                    target=location,
                    kind="finding",
                    reason=f"{finding.title} ({finding.verification_status})",
                )
            )

    return _dedupe_surfaces(surfaces)[:limit]


async def run_parallel_pentest(
    root_agent: Any,
    *,
    agent_factory: AgentFactory,
    user_input: str,
    target: str,
    discovery_rounds: int = 1,
    worker_rounds: int = 3,
    max_agents: int = 3,
    max_depth: int = 1,
    surface_limit: int = 20,
    stream_sink: Any = None,
) -> ParallelAgentRunResult:
    """Run a root discovery pass, then fan out bounded child agents by surface."""
    discovery_rounds = max(1, discovery_rounds)
    worker_rounds = max(1, worker_rounds)
    max_agents = max(1, max_agents)
    max_depth = max(1, max_depth)

    summary = ParallelAgentRunResult()
    summary.root_results = await root_agent.auto_pentest(
        user_input,
        target=target,
        max_rounds=discovery_rounds,
        stream_sink=stream_sink,
    )

    seen: set[str] = set()
    for depth in range(1, max_depth + 1):
        surfaces = [
            surface
            for surface in extract_attack_surfaces(root_agent.session_state, limit=surface_limit)
            if surface.target not in seen
        ][:max_agents]
        if not surfaces:
            break

        for surface in surfaces:
            seen.add(surface.target)
        summary.surfaces.extend(surfaces)

        worker_results = await _run_surface_wave(
            root_agent,
            agent_factory=agent_factory,
            surfaces=surfaces,
            worker_rounds=worker_rounds,
        )
        summary.worker_results.extend(worker_results)
        summary.waves_completed = depth

    return summary


async def _run_surface_wave(
    root_agent: Any,
    *,
    agent_factory: AgentFactory,
    surfaces: list[AttackSurface],
    worker_rounds: int,
) -> list[Any]:
    semaphore = asyncio.Semaphore(max(1, len(surfaces)))

    async def _run_one(surface: AttackSurface) -> Any:
        async with semaphore:
            child = agent_factory()
            _seed_child_session(child.session_state, root_agent.session_state, surface)
            prompt = _surface_prompt(surface, root_agent.session_state)
            result = await child.auto_pentest(
                prompt,
                target=root_agent.session_state.target,
                max_rounds=worker_rounds,
            )
            merge_session_state(root_agent.session_state, child.session_state)
            return {"surface": surface, "results": result}

    return await asyncio.gather(*(_run_one(surface) for surface in surfaces))


def merge_session_state(parent: SessionState, child: SessionState) -> None:
    """Merge child findings, recon data, notes, and steps into a parent session."""
    for finding in child.findings:
        parent.add_finding(finding)

    for key, value in child.recon_data.items():
        existing = parent.recon_data.get(key)
        if isinstance(value, list):
            if not isinstance(existing, list):
                parent.recon_data[key] = list(value)
            else:
                parent.recon_data[key] = existing + [item for item in value if item not in existing]
        elif isinstance(value, dict):
            merged = dict(existing) if isinstance(existing, dict) else {}
            merged.update(value)
            parent.recon_data[key] = merged
        elif key not in parent.recon_data or not parent.recon_data[key]:
            parent.recon_data[key] = value

    for note in child.notes:
        if note not in parent.notes:
            parent.notes.append(note)
    for step in child.executed_steps:
        if step not in parent.executed_steps:
            parent.executed_steps.append(step)
    for record in child.step_records:
        if record not in parent.step_records:
            parent.step_records.append(record)


def _seed_child_session(child: SessionState, parent: SessionState, surface: AttackSurface) -> None:
    child.target = parent.target
    child.phase = parent.phase
    child.task_constraints = parent.task_constraints.model_copy(deep=True)
    child.recon_data = copy.deepcopy(parent.recon_data)
    child.resume_summary = (
        f"Parallel worker assigned to {surface.kind} {surface.target}. "
        f"Reason: {surface.reason}. Preserve scope constraints."
    )


def _surface_prompt(surface: AttackSurface, session: SessionState) -> str:
    constraints = session.task_constraints.to_prompt_block()
    constraints_suffix = f"\n\n{constraints}" if constraints else ""
    return (
        f"Parallel worker task for authorized testing of attack surface {surface.target}. "
        f"Surface type: {surface.kind}. Reason: {surface.reason}. "
        "Investigate this surface only. Record concrete evidence, candidate findings, "
        "safe verification results, and new surfaces discovered. "
        "Do not brute force credentials, run destructive payloads, or perform post-exploitation "
        "unless the inherited task constraints explicitly allow exploit actions."
        f"{constraints_suffix}"
    )


def _dedupe_surfaces(surfaces: list[AttackSurface]) -> list[AttackSurface]:
    seen: set[str] = set()
    deduped: list[AttackSurface] = []
    for surface in surfaces:
        key = surface.target.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(surface)
    return deduped


def _extract_location(finding: VulnerabilityFinding) -> str:
    text = f"{finding.evidence or ''}\n{finding.description or ''}"
    url_match = re.search(r"https?://[^\s<>'\")\]]+", text)
    if url_match:
        return url_match.group(0)
    host_port_match = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}\b", text)
    if host_port_match:
        return host_port_match.group(0)
    return ""

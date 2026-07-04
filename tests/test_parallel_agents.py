"""Tests for bounded parallel agent coordination."""

from __future__ import annotations

import pytest

from vulnclaw.agent.context import SessionState, VulnerabilityFinding
from vulnclaw.agent.parallel_agents import extract_attack_surfaces, run_parallel_pentest


class FakeAgent:
    def __init__(self) -> None:
        self.session_state = SessionState(target="192.168.1.0/24")
        self.calls: list[str] = []

    async def auto_pentest(self, prompt, target=None, max_rounds=0, stream_sink=None):
        self.calls.append(prompt)
        if "authorized fast network scan" in prompt:
            self.session_state.recon_data["network_services"] = [
                {
                    "host": "192.168.1.10",
                    "port": 22,
                    "protocol": "tcp",
                    "service": "ssh",
                },
                {
                    "host": "192.168.1.20",
                    "port": 445,
                    "protocol": "tcp",
                    "service": "microsoft-ds",
                },
            ]
            return ["root-discovery"]

        self.session_state.add_finding(
            VulnerabilityFinding(
                title=f"Surface reviewed {len(self.calls)}",
                severity="Info",
                vuln_type="surface-review",
                evidence=prompt,
            )
        )
        self.session_state.notes.append("worker note")
        return ["worker-result"]


def test_extract_attack_surfaces_from_network_state_and_findings():
    state = SessionState(target="192.168.1.0/24")
    state.recon_data["network_services"] = [
        {"host": "192.168.1.10", "port": 22, "protocol": "tcp", "service": "ssh"},
        {"host": "192.168.1.10", "port": 22, "protocol": "tcp", "service": "ssh"},
    ]
    state.recon_data["network_scans"] = [
        {
            "weak_links": [
                {"target": "192.168.1.20:445", "reason": "SMB exposed"},
            ]
        }
    ]
    state.add_finding(
        VulnerabilityFinding(
            title="Web finding",
            vuln_type="web",
            evidence="Observed at http://192.168.1.30/admin",
        )
    )

    surfaces = extract_attack_surfaces(state)

    assert [surface.target for surface in surfaces] == [
        "192.168.1.10:22",
        "192.168.1.20:445",
        "http://192.168.1.30/admin",
    ]


@pytest.mark.asyncio
async def test_run_parallel_pentest_fans_out_and_merges_worker_state():
    root = FakeAgent()
    children: list[FakeAgent] = []

    def factory():
        child = FakeAgent()
        children.append(child)
        return child

    result = await run_parallel_pentest(
        root,
        agent_factory=factory,
        user_input="Perform an authorized fast network scan against 192.168.1.0/24.",
        target="192.168.1.0/24",
        discovery_rounds=1,
        worker_rounds=2,
        max_agents=2,
        max_depth=1,
    )

    assert result.root_results == ["root-discovery"]
    assert result.waves_completed == 1
    assert [surface.target for surface in result.surfaces] == [
        "192.168.1.10:22",
        "192.168.1.20:445",
    ]
    assert len(children) == 2
    assert len(root.session_state.findings) == 2
    assert root.session_state.notes == ["worker note"]
    assert all("Investigate this surface only" in child.calls[0] for child in children)

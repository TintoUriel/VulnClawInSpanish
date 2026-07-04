"""Constraint policy helpers for task, phase, and tool enforcement."""

from __future__ import annotations

from vulnclaw.agent.context import PentestPhase, TaskConstraints

PHASE_TO_ACTION: dict[PentestPhase, str] = {
    PentestPhase.RECON: "recon",
    PentestPhase.VULN_DISCOVERY: "scan",
    PentestPhase.EXPLOITATION: "exploit",
    PentestPhase.POST_EXPLOITATION: "post_exploitation",
    PentestPhase.REPORTING: "report",
}


def normalize_action_name(action: str) -> str:
    """Normalize action aliases into a shared policy namespace."""
    lowered = (action or "").strip().lower()
    aliases = {
        "run": "run",
        "recon": "recon",
        "scan": "scan",
        "exploit": "exploit",
        "post": "post_exploitation",
        "post_exploitation": "post_exploitation",
        "report": "report",
        "reporting": "report",
        "persistent": "persistent",
    }
    return aliases.get(lowered, lowered)


def validate_action_constraints(action: str, constraints: TaskConstraints) -> str | None:
    """Return a constraint violation message when a task action is out of scope."""
    if constraints.is_empty():
        return None

    normalized = normalize_action_name(action)
    allowed = [normalize_action_name(item) for item in constraints.allowed_actions]
    blocked = [normalize_action_name(item) for item in constraints.blocked_actions]

    # Composite commands (run, persistent) include all phases;
    # fine-grained enforcement happens inside the loop via phase/tool checks.
    if normalized in ("run", "persistent"):
        if normalized in blocked:
            return f"constraint_violation: command '{normalized}' is blocked by task constraints"
        return None

    if allowed and normalized not in allowed:
        return f"constraint_violation: command '{normalized}' is outside allowed actions [{', '.join(allowed)}]"

    if normalized in blocked:
        return f"constraint_violation: command '{normalized}' is blocked by task constraints"

    return None


def validate_phase_transition(
    next_phase: PentestPhase,
    constraints: TaskConstraints,
) -> str | None:
    """Return a constraint violation message when a phase transition is out of scope."""
    action = PHASE_TO_ACTION.get(next_phase)
    if action is None:
        return None
    violation = validate_action_constraints(action, constraints)
    if violation is None:
        return None
    return f"{violation} (phase transition to {next_phase.value})"


# 纯本地/知识类工具：不与目标交互，不纳入「动作范围」约束
LOCAL_META_TOOLS = {"load_skill_reference", "crypto_decode"}

# 真正代表「利用」意图的攻击载荷特征——与传输方式（HTTP 方法/网络库）无关
EXPLOIT_PAYLOAD_MARKERS = [
    "union select",
    " or 1=1",
    "'or'",
    "../",
    "..\\",
    "<script",
    "cmd=",
    "php://",
    "data://",
    "extractvalue(",
    "updatexml(",
    "load_file(",
    "into outfile",
    "{{",  # SSTI
    "${",  # SSTI/EL
    "%00",
    "/etc/passwd",
    "/bin/sh",
    "bash -i",
    "nc -e",
    "powershell -e",
]

# python_execute 中代表本地命令执行/反弹 shell 的特征
PYTHON_EXPLOIT_MARKERS = [
    "os.system",
    "subprocess",
    "pty.spawn",
    "/bin/sh",
    "bash -i",
    "nc -e",
    "reverse_shell",
]


def infer_tool_action(tool_name: str, args: dict[str, object]) -> str:
    """Infer the effective action class of a tool invocation.

    关键原则：只有「实际攻击载荷」才推断为 exploit；HTTP 方法、是否用 requests/urllib
    等传输细节不构成利用意图（recon/scan 阶段本就需要发 POST/OPTIONS、用 requests 探测）。
    """
    normalized_tool = (tool_name or "").strip().lower()

    if normalized_tool in LOCAL_META_TOOLS:
        return "recon"  # 仅本地操作，配合 validate_tool_action 豁免

    # Intel tools: read-only lookups (no target egress) and active recon
    # (low-impact target/3rd-party contact) both classify as passive "recon".
    from vulnclaw.intel.tools import READ_ONLY_INTEL_TOOLS, RECON_INTEL_TOOLS

    if normalized_tool in READ_ONLY_INTEL_TOOLS or normalized_tool in RECON_INTEL_TOOLS:
        return "recon"

    if normalized_tool == "nmap_scan":
        return "recon"

    if normalized_tool == "fetch":
        url = str(args.get("url", "") or "").lower()
        method = str(args.get("method", "GET") or "GET").upper()
        body = str(args.get("body", "") or "").lower()
        if any(marker in url or marker in body for marker in EXPLOIT_PAYLOAD_MARKERS):
            return "exploit"
        # 方法本身不代表利用：GET/HEAD/OPTIONS 属侦察，其它（POST 测表单等）属扫描
        if method in ("GET", "HEAD", "OPTIONS"):
            return "recon"
        return "scan"

    if normalized_tool == "python_execute":
        code = str(args.get("code", "") or "").lower()
        if any(marker in code for marker in EXPLOIT_PAYLOAD_MARKERS + PYTHON_EXPLOIT_MARKERS):
            return "exploit"
        # 用 requests/httpx/urllib/socket 做 HTTP 探测属扫描，而非利用
        if any(m in code for m in ("requests.", "httpx.", "urllib", "http.client", "socket")):
            return "scan"
        return "recon"

    if normalized_tool == "brute_force_login":
        return "scan"

    return "scan"


def validate_tool_action(
    tool_name: str, args: dict[str, object], constraints: TaskConstraints
) -> str | None:
    """Return a constraint violation when a tool invocation implies a blocked action."""
    # 纯本地/知识类工具不受动作范围约束（加载文档、编解码不触碰目标）
    if (tool_name or "").strip().lower() in LOCAL_META_TOOLS:
        return None
    inferred = infer_tool_action(tool_name, args)
    violation = validate_action_constraints(inferred, constraints)
    if violation is None:
        return None
    return f"{violation} (tool '{tool_name}' inferred action '{inferred}')"

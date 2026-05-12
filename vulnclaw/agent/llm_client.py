"""LLM client helpers for AgentCore."""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from vulnclaw.agent.tool_call_manager import (
    handle_tool_calls,
    handle_tool_calls_with_results,
)


def extract_response(message: Any) -> str:
    """Extract the actual response text from an LLM message.

    Handles:
    1. Normal content (no thinking)
    2. Content with inline <thinking> tags (open/closed)
    3. Separate reasoning_content field (DeepSeek R1, etc.)
    """
    content = message.content or ""
    reasoning = getattr(message, "reasoning_content", None) or ""
    if reasoning and not content:
        content = f"<thinking>\n{reasoning}\n</thinking>\n"
    elif reasoning and content:
        content = f"<thinking>\n{reasoning}\n</thinking>\n{content}"
    return content


def _is_non_retriable_llm_error(error_text: str) -> bool:
    """Return True for configuration/auth errors that should fail fast."""
    hard_fail_markers = [
        "bad_request_error",
        "incorrect api key",
        "invalid api key",
        "invalid chat setting",
        "invalid function arguments json string",
        "tool_call_id",
        "authentication",
        "unauthorized",
        "permission denied",
        "model not found",
        "no such model",
        "invalid_request_error",
        "unsupported parameter",
    ]
    return any(marker in error_text for marker in hard_fail_markers)


async def _call_with_persistent_retries(agent: Any, request_fn, stage_label: str) -> tuple[Any, int]:
    """Keep retrying retriable LLM calls until success or manual interruption.

    Returns:
        (response, retry_attempts)
    """
    loop = asyncio.get_event_loop()
    retry_attempts = 0

    while True:
        try:
            response = await loop.run_in_executor(None, request_fn)
            if response is not None and getattr(response, "choices", None):
                return response, retry_attempts

            retry_attempts += 1
            print(
                f"[!] {stage_label} LLM API 异常响应，第 {retry_attempts} 次重连尝试中... (5s 后重试)",
                file=sys.stdout,
                flush=True,
            )
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            error_text = str(exc).lower()
            if _is_non_retriable_llm_error(error_text):
                raise

            retry_attempts += 1
            print(
                f"[!] {stage_label} LLM 连接异常，第 {retry_attempts} 次重连尝试中... ({exc})",
                file=sys.stdout,
                flush=True,
            )
            await asyncio.sleep(5)


def _prepend_retry_notice(text: str, retry_attempts: int) -> str:
    """Annotate a successful response if retries happened within the same round."""
    if retry_attempts <= 0:
        return text
    return f"[LLM恢复] 本轮在第 {retry_attempts} 次重连后恢复。\n{text}"


def _format_tool_results_fallback(tool_results: list[dict[str, Any]], skipped_info: list[str]) -> str:
    """Build a plain-text fallback summary when provider tool-summary format is incompatible."""
    parts = ["[tool results processed] 当前提供商不兼容标准工具总结回传，已降级为纯文本结果摘要："]
    for item in tool_results:
        content = item.get("content", "") if isinstance(item, dict) else str(item)
        if len(content) > 800:
            content = content[:400] + "\n...[中间省略]...\n" + content[-400:]
        parts.append(content)
    if skipped_info:
        parts.append("⚠️ 本轮跳过: " + "; ".join(skipped_info))
    return "\n".join(parts)


async def call_llm(agent: Any, system_prompt: str) -> str:
    """Call the LLM with the current context and system prompt (single turn)."""
    client = agent._get_client()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(agent.context.get_messages())
    tools = agent._build_openai_tools()

    kwargs = {
        "model": agent.config.llm.model,
        "messages": messages,
        "max_tokens": agent.config.llm.max_tokens,
        "temperature": agent.config.llm.temperature,
    }
    if tools:
        kwargs["tools"] = tools

    provider = agent.config.llm.provider.lower()
    if provider == "openai" and "o1" in agent.config.llm.model.lower():
        kwargs["reasoning_effort"] = agent.config.llm.reasoning_effort
        kwargs.pop("temperature", None)

    response, retry_attempts = await _call_with_persistent_retries(
        agent,
        lambda: client.chat.completions.create(**kwargs),
        "单轮",
    )

    choice = response.choices[0]
    if choice.message.tool_calls:
        return _prepend_retry_notice(await handle_tool_calls(agent, choice.message), retry_attempts)
    return _prepend_retry_notice(extract_response(choice.message), retry_attempts)


async def call_llm_auto(agent: Any, system_prompt: str, round_context: str) -> str:
    """Call the LLM in auto-pentest mode with round context appended."""
    client = agent._get_client()

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(agent.context.get_messages())
    messages.append({"role": "user", "content": round_context})
    tools = agent._build_openai_tools()

    kwargs = {
        "model": agent.config.llm.model,
        "messages": messages,
        "max_tokens": agent.config.llm.max_tokens,
        "temperature": agent.config.llm.temperature,
    }
    if tools:
        kwargs["tools"] = tools

    provider = agent.config.llm.provider.lower()
    if provider == "openai" and "o1" in agent.config.llm.model.lower():
        kwargs["reasoning_effort"] = agent.config.llm.reasoning_effort
        kwargs.pop("temperature", None)

    response, retry_attempts = await _call_with_persistent_retries(
        agent,
        lambda: client.chat.completions.create(**kwargs),
        "自主循环",
    )

    choice = response.choices[0]
    if choice.message.tool_calls:
        tool_results, skipped_info = await handle_tool_calls_with_results(agent, choice.message)

        executed_tcs = []
        for tc in tool_results:
            if not isinstance(tc, dict) or "tool_call" not in tc:
                import sys
                print(f"[!] 跳过异常工具结果: {type(tc).__name__} {str(tc)[:100]}", file=sys.stderr)
                continue
            executed_tcs.append(tc["tool_call"])

        assistant_msg = {
            "role": "assistant",
            "content": choice.message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in executed_tcs
            ],
        }
        messages.append(assistant_msg)

        for tool_result in tool_results:
            if isinstance(tool_result, dict) and "tool_call_id" in tool_result:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_result["tool_call_id"],
                    "content": tool_result.get("content", ""),
                })

        tool_summary_parts = []
        for tc in executed_tcs:
            try:
                args_str = str(tc.function.arguments)[:200]
            except Exception:
                args_str = "<无法读取>"
            tool_summary_parts.append(f"调用工具: {tc.function.name}({args_str})")
        for tr in tool_results:
            content = tr.get("content", "") if isinstance(tr, dict) else str(tr)
            if len(content) > 1000:
                content = content[:500] + "\n...[中间省略]...\n" + content[-500:]
            tool_summary_parts.append(f"工具结果: {content}")
            if isinstance(tr, dict) and isinstance(tr.get("structured_content"), dict) and tr["structured_content"]:
                structured = json.dumps(tr["structured_content"], ensure_ascii=False)
                if len(structured) > 1000:
                    structured = structured[:500] + "\n...[中间省略]...\n" + structured[-500:]
                tool_summary_parts.append(f"结构化结果: {structured}")
        if skipped_info:
            tool_summary_parts.append(f"⚠️ 本轮跳过: {'; '.join(skipped_info)}")

        try:
            kwargs["messages"] = messages
            response2, second_retry_attempts = await _call_with_persistent_retries(
                agent,
                lambda: client.chat.completions.create(**kwargs),
                "工具总结",
            )
            final_text = extract_response(response2.choices[0].message)
            agent.context.add_assistant_message(final_text)
            return _prepend_retry_notice(final_text, retry_attempts + second_retry_attempts)
        except Exception as e2:
            error_text = str(e2).lower()
            if _is_non_retriable_llm_error(error_text):
                fallback = _format_tool_results_fallback(tool_results, skipped_info)
                agent.context.add_assistant_message(fallback)
                return fallback
            return f"[tool results processed] 继续分析错误: {e2}"

    return _prepend_retry_notice(extract_response(choice.message), retry_attempts)

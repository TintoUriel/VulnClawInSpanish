# VulnClaw 流式输出功能 - 实施任务计划

## 架构决策摘要
- **方案**: 最小侵入式（方案 A）
- **核心模式**: "输出 sink（Output Sink）" 抽象——LLM 调用层接受可选的输出回调对象，由调用方（CLI vs Web）明确决定输出去向
- **防止重复输出的关键**: 默认为 "不输出"，sink 由调用方显式注入；流式输出完成后设置 `result.output_already_streamed = True` 标志，CLI 的 `_print_agent_output()` 据此跳过重复打印

## 贡献要求合规性
本计划严格遵循 [CONTRIBUTING.md](file:///workspace/CONTRIBUTING.md) 的核心原则：

| 原则 | 本计划对应 | 状态 |
|------|-----------|------|
| "在正确模块里改代码" | `StreamSink`/`call_llm_stream()` 放在 `llm_client.py`（LLM 调用层）；`TerminalStreamSink` 放在 `cli/main.py`（CLI 输出层） | ✅ |
| "不要把职责堆回 core.py" | 核心逻辑在 `llm_client.py`（helper 模块），`core.py` 仅透传 sink 参数 | ✅ |
| "改行为逻辑时同步补测试" | Task 11 覆盖所有核心功能测试 | ✅ |
| "不引入不必要的新模块" | 不拆分独立模块，`StreamSink` 定义直接放在 `llm_client.py` | ✅ |

### 模块放置规则（严格遵循 CONTRIBUTING.md）
```
vulnclaw/agent/llm_client.py     # LLM 调用层 → StreamSink, call_llm_stream(), call_llm_auto_stream()
vulnclaw/cli/main.py             # CLI 渲染层 → TerminalStreamSink, sink 注入调用点
vulnclaw/agent/core.py           # Agent 协调层 → stream_sink 参数透传（仅加参数，不加业务逻辑）
tests/test_llm_client_streaming.py  # 测试文件（遵循 tests/ 结构）
```

## 设计要点（关键变更点）

### 调用链改造（Before → After）
```
BEFORE:                                         AFTER:

CLI main.py → AgentCore.chat()  ...             CLI main.py:
  → call_llm(agent, prompt)                     stream_sink = TerminalStreamSink(console, config)
    → client.chat.completions.create()          result = await agent.chat(user_input, stream_sink=stream_sink)
    → returns full str                           _print_agent_output(result)  ← 检查标志跳过
  → result.output = str                         
  → _print_agent_output(result) ← 整串打印      

WebTaskManager → run_agent_task() ...           WebTaskManager → run_agent_task() ...
  → AgentCore.chat()                              → AgentCore.chat()  (无 stream_sink)
    → call_llm(agent, prompt)                      → call_llm(agent, prompt, stream_sink=None)
      → returns full str                             → 非流式，返回 str，无终端输出
    → result.output = str                           → result.output = str  
    → publish SSE event                             → publish SSE event
```

### Sink 接口设计
```python
# vulnclaw/agent/llm_client.py — StreamSink Protocol 定义
from typing import Protocol, Optional

class StreamSink(Protocol):
    """输出流接收器抽象。子类实现各阶段回调。

    放在 llm_client.py 中符合 CONTRIBUTING.md 的模块放置原则。
    """
    def on_status(self, message: str) -> None:        # "Thinking..." 等状态提示
        ...
    def on_thinking_token(self, token: str) -> None:  # 思考过程的 token (可选隐藏)
        ...
    def on_content_token(self, token: str) -> None:   # 正文 token
        ...
    def on_tool_call(self, tool_name: str, args: str) -> None:  # 工具调用提示
        ...
    def on_tool_result(self, result_summary: str) -> None:  # 工具结果摘要
        ...
    def on_stream_end(self) -> None:                  # 流式结束（换行/清理）
        ...

# _NullSink（默认，什么都不做）用于非 CLI 路径（内部使用，不导出）
class _NullSink:
    """空实现，确保无 sink 时不产生任何输出。"""
    def on_status(self, message: str) -> None: ...
    def on_thinking_token(self, token: str) -> None: ...
    def on_content_token(self, token: str) -> None: ...
    def on_tool_call(self, tool_name: str, args: str) -> None: ...
    def on_tool_result(self, result_summary: str) -> None: ...
    def on_stream_end(self) -> None: ...
```

---

## [ ] Task 1: 定义 StreamSink 抽象和默认实现
- **Priority**: P0
- **Depends On**: None
- **Location**: `vulnclaw/agent/llm_client.py`（严格遵循"LLM 调用在 agent/llm_client.py"原则，不拆分独立模块）
- **Description**:
  - 在 `vulnclaw/agent/llm_client.py` 末尾（在现有函数之后）定义 `StreamSink` Protocol/基类
  - 定义 `_NullSink`（默认值，空实现，确保无 sink 时不产生任何输出）
  - 定义 sink 回调方法签名（如设计要点中所示）
  - 添加类型注解 `Optional[StreamSink]`
- **Acceptance Criteria Addressed**: FR-3, FR-4, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: `_NullSink` 的所有方法调用均无副作用（不写 stdout、不抛异常）
  - `programmatic` TR-1.2: `StreamSink` 可被自定义子类覆盖并正确接收回调
- **Notes**: 保持轻量，不引入任何 IO。核心是 "接口定义"。放在 `llm_client.py` 中符合 CONTRIBUTING.md 的"在正确模块里改代码"原则。

## [ ] Task 2: 实现 call_llm_stream() 流式调用函数
- **Priority**: P0
- **Depends On**: Task 1
- **Description**:
  - 在 `llm_client.py` 中新增 `call_llm_stream(agent, system_prompt, stream_sink=None) -> str`
  - 内部逻辑：
    1. `client.chat.completions.create(..., stream=True)`
    2. 发送前调用 `stream_sink.on_status("Thinking...")`
    3. 迭代 `response`：对每个 chunk 提取 `delta.content` 和 `delta.reasoning_content`
    4. 对于 reasoning 流：调用 `on_thinking_token()`（在 sink 内部决定是否渲染）
    5. 对于 content 流：调用 `on_content_token()`
    6. 累积完整文本到 `full_text`
    7. 循环结束调用 `on_stream_end()`
    8. 返回 `full_text`（保留与 `call_llm()` 完全相同的返回格式——包括 `<thinking>` 标签包裹）
  - **错误/降级处理**：
    - 如果 `stream=True` 调用抛出明确的不支持异常，或响应没有 delta 结构，则调用 `_call_llm_non_stream()`（将现有 `call_llm()` 逻辑提取为私有函数）并将完整文本逐段喂给 sink（模拟流式：将完整文本按句子或字符分段触发 `on_content_token`），最后返回完整文本
- **Acceptance Criteria Addressed**: FR-1, FR-5, AC-1, AC-4, AC-5, AC-8, AC-9, AC-11
- **Test Requirements**:
  - `programmatic` TR-2.1: 使用 mock `openai` client 返回流式 delta 序列 → 验证 `on_content_token` 按顺序被调用，且返回值 == 完整文本
  - `programmatic` TR-2.2: mock client 在 `stream=True` 时抛出 `NotImplementedError` → 验证函数自动降级并仍然返回完整文本
  - `programmatic` TR-2.3: 响应含 reasoning_content → 验证 `on_thinking_token` 被调用
  - `programmatic` TR-2.4: 模拟 `asyncio.CancelledError` → 验证函数优雅处理，返回已累积文本
- **Notes**: 这是本功能的核心实现，逻辑最集中，需仔细测试。

## [ ] Task 3: 在 call_llm() 中接入 sink，保持签名兼容
- **Priority**: P0
- **Depends On**: Task 2
- **Description**:
  - 为 `call_llm(agent, system_prompt, *, stream_sink: Optional[StreamSink] = None) -> str` 添加可选 `stream_sink` 参数
  - 当 `stream_sink is None` 或 `isinstance(stream_sink, NullSink)` → 使用现有的非流式路径（`_call_llm_non_stream()`）
  - 当 `stream_sink is not None` → 调用 `call_llm_stream()` 替代
  - 保持返回值类型 `str` 不变，保持调用方代码零改动即可工作（但调用方需显式传 sink 才能启用流式）
  - 同步更新 `_call_with_persistent_retries` 中的重试逻辑——确保重试时 sink 仍收到 `on_status` 重置提示
- **Acceptance Criteria Addressed**: FR-1, NFR-3, AC-12
- **Test Requirements**:
  - `programmatic` TR-3.1: 不传 sink 调用 → 返回 str，且无输出到终端（行为与旧版一致）
  - `programmatic` TR-3.2: 传 sink 调用 → sink 的方法被按序调用，且返回 str 与不传 sink 时等效
  - `programmatic` TR-3.3: 模拟多次重试 → 每次重试前 sink 收到 `on_status("Reconnecting...")` 或类似消息
- **Notes**: 这一步是"切换开关"——从此调用方可以通过传 sink 选择流式，不传则行为不变。

## [ ] Task 4: 实现 call_llm_auto_stream() 支持工具调用场景
- **Priority**: P0
- **Depends On**: Task 2
- **Description**:
  - 在 `llm_client.py` 中新增 `call_llm_auto_stream(agent, system_prompt, round_context, stream_sink=None) -> str`
  - 逻辑与 `call_llm_auto()` 对应，但流式处理：
    1. 流式获取 LLM 响应，直到遇到完整的 tool_calls（`delta.tool_calls` 逐段累积）
    2. 当检测到 tool_calls 时：调用 `stream_sink.on_tool_call(tool_name, args_str)` 显示工具调用摘要，**暂停流式输出**，同步执行工具
    3. 工具执行完成后：调用 `stream_sink.on_tool_result(result_summary)` 显示工具结果摘要
    4. 如需第二次 LLM 调用（工具总结阶段），同样以流式方式调用 `client.chat.completions.create(stream=True)` 并输出总结文本
    5. 最终返回与非流式 `call_llm_auto()` 等价的完整文本
  - 降级逻辑同 Task 2
- **Acceptance Criteria Addressed**: FR-2, AC-2, AC-9
- **Test Requirements**:
  - `programmatic` TR-4.1: mock 一个带 tool_calls 的流式响应 → 验证 `on_tool_call` 被调用且工具被执行
  - `programmatic` TR-4.2: 纯文本响应（无工具）→ 验证走纯流式路径，`on_content_token` 被正确调用
  - `programmatic` TR-4.3: 工具调用+二次总结流程 → 验证完整返回文本与非流式版本等效
- **Notes**: tool_calls 的流式累积比纯文本复杂——`openai` SDK 会分 chunk 送达 tool_calls 数组元素，需要正确累积 id/name/arguments 再解析。

## [ ] Task 5: 在 call_llm_auto() 中接入 sink（同 Task 3 模式）
- **Priority**: P0
- **Depends On**: Task 4
- **Description**:
  - `call_llm_auto(agent, system_prompt, round_context, *, stream_sink: Optional[StreamSink] = None) -> str`
  - sink 非空 → 走 `call_llm_auto_stream()`；sink 为空 → 走原有非流式逻辑
  - 保持调用链（尤其 `loop_controller.auto_pentest` 中）的兼容性
- **Acceptance Criteria Addressed**: FR-2, NFR-3
- **Test Requirements**:
  - `programmatic` TR-5.1: 不传 sink → 行为与旧版一致
  - `programmatic` TR-5.2: 传 sink → 返回值与不传 sink 时等效，且 sink 收到流式事件
- **Notes**: Task 3 的镜像任务，但针对 auto_pentest 路径。

## [ ] Task 6: 实现 CLI 终端流式渲染器（TerminalStreamSink）
- **Priority**: P0
- **Depends On**: Task 1
- **Location**: `vulnclaw/cli/main.py`（遵循 CONTRIBUTING.md "CLI 渲染在 cli/main.py"）
- **Description**:
  - 在 `vulnclaw/cli/main.py` 末尾或文件顶部区域实现 `TerminalStreamSink` 类
  - 行为：
    - `on_status(msg)`: 打印如 `[dim]Thinking...[/dim]`（单行，不带换行）
    - `on_thinking_token(token)`: 如果 `config.session.show_thinking == True`，则以 `[dim italic]` Rich 样式打印 token；否则丢弃
    - `on_content_token(token)`: 直接打印 token（不包装 Rich markup，避免 token 内部字符被当作 markup）
    - `on_tool_call(name, args)`: 换行打印 `[bold cyan]→ 调用工具: {name}[/]` + args 摘要
    - `on_tool_result(summary)`: 换行打印 `[dim]→ 工具结果: {summary[:200]}...[/]`（截断防止过长）
    - `on_stream_end()`: 打印换行
  - 使用 `console.print(..., end="", soft_wrap=True)` 或类似方式实现增量输出
  - **去重保护**: 实例维护一个内部标志 `_status_shown`，首个 content token 到达时清除 status 行（或在 status 后换行）
- **Acceptance Criteria Addressed**: FR-3, AC-1, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: `show_thinking=False` → on_thinking_token 调用不会产生输出；on_content_token 调用产生正确输出
  - `programmatic` TR-6.2: `show_thinking=True` → thinking 内容以 dim 样式输出
  - `human-judgment` TR-6.3: 实际运行体验中文字平滑追加，无多余换行或错位
- **Notes**: Rich 的 markup 解析可能导致 token 中 `[` `]` 等字符被误解释——必须转义或用 `Text` 对象直接写入。放在 `cli/main.py` 中符合 CONTRIBUTING.md 的模块放置原则。

## [ ] Task 7: 在 AgentCore 中传递 sink 参数
- **Priority**: P0
- **Depends On**: Task 3, Task 5
- **Description**:
  - `AgentCore.chat(user_input, target=None, *, stream_sink: Optional[StreamSink] = None)` → 在内部 `call_llm(self, system_prompt, stream_sink=stream_sink)` 处透传
  - `AgentCore.auto_pentest(user_input, target=None, max_rounds=15, on_step=None, *, stream_sink: Optional[StreamSink] = None)` → 透传到 `call_llm_auto`
  - `AgentCore.persistent_pentest(..., *, stream_sink: Optional[StreamSink] = None)` → 透传到 `auto_pentest` 以及 `_generate_attack_summary` 内部的 LLM 调用
  - **重要**: 在返回值 `AgentResult` 上添加一个**临时标志** `_streamed: bool = True` 或在返回前由 sink 驱动的外层设置 `result._output_already_printed = True`。CLI 层的 `_print_agent_output()` 检查此标志并跳过重复打印。
  - 不影响 `loop_controller.py` 的纯逻辑循环（它只调用 `call_llm_auto`，签名扩展保持兼容）。
- **Acceptance Criteria Addressed**: FR-4, AC-1, AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-7.1: 带 sink 调用 `chat()` → 返回的 `AgentResult` 含流式标志
  - `programmatic` TR-7.2: 不带 sink 调用 → 标志为 False，兼容原有路径
- **Notes**: 使用 keyword-only 参数 (`*`) 避免破坏现有位置参数调用。

## [ ] Task 8: 改造 CLI REPL 调用路径以注入 sink
- **Priority**: P0
- **Depends On**: Task 6, Task 7
- **Description**:
  - 在 `_run_repl()` 的 chat 分支中：
    ```python
    # 修改前
    async def call():
        return await agent.chat(user_input, target=current_target)
    
    # 修改后
    sink = TerminalStreamSink(console, config.session.show_thinking)
    async def call():
        return await agent.chat(user_input, target=current_target, stream_sink=sink)
    ```
  - 在 auto_pentest 分支同理：
    ```python
    sink = TerminalStreamSink(console, config.session.show_thinking)
    return await agent.auto_pentest(
        user_input, target=current_target,
        max_rounds=config.session.max_rounds,
        on_step=on_step, stream_sink=sink,
    )
    ```
  - 在 persistent_pentest 分支同理
  - **修改 `_print_agent_output()`**:
    ```python
    def _print_agent_output(output: str, config) -> None:
        # 新增：如果 output 是一个已流式标记的对象，跳过
        if getattr(output, "_streamed", False):
            return
        # 或者：如果 output 是 str 但长度为 0 且上游已流式则跳过
        # 更稳妥的方式：在调用处根据标志决定是否调用此函数
        ...
    ```
    实际上更清晰的是：**不修改 `_print_agent_output` 的签名**，而是在调用处（`after_result`）根据 `result._streamed` 标志决定是否调用它。
  - 对于**子命令** (`vulnclaw run`, `vulnclaw recon`, `vulnclaw scan`, `vulnclaw exploit`, `vulnclaw persistent`)：
    - 在 `runner(agent, config)` 中注入 sink
    - 关键函数: `_run_cli_orchestrated_task()` 中的 `runner` 参数是一个闭包——在该闭包中创建 sink 并传给 agent 方法
- **Acceptance Criteria Addressed**: FR-6, AC-1, AC-2, AC-3
- **Test Requirements**:
  - `human-judgment` TR-8.1: 实际运行 `vulnclaw` REPL → 输入一条查询，看到 "Thinking..." → 逐字输出 → 结束
  - `programmatic` TR-8.2: 断言 `_print_agent_output()` 在流式路径中**不被调用**（通过 mock 验证）
  - `programmatic` TR-8.3: 子命令 `run`/`recon` 等在传入 sink 时正确流式
- **Notes**: 这是用户直接感知到的最终效果，也是最容易出 UX 问题的地方。需在实际终端中测试多种场景。

## [ ] Task 9: 确保 Web 路径不产生终端输出
- **Priority**: P0
- **Depends On**: Task 7
- **Description**:
  - 检查 `vulnclaw/web/services/task_service.py` 中 `start_task()` 的实现
  - 检查它如何调用 agent：它创建 agent 实例后调用 agent 的 `auto_pentest` / `chat` 等方法
  - **明确不传 `stream_sink`**（默认 `None`）——这是默认行为，不需额外改动
  - 但要确保：当 `stream_sink is None` 时，`call_llm()` 走非流式路径，**不会**在服务端进程的 stdout 上产生任何输出
  - 在 Web 路径中，输出仍然通过 `WebTaskManager.publish(task_id, "task_output", {...})` → SSE 事件 → 前端渲染
  - 添加一个保护：在 `WebTaskManager` 调用 agent 之前，将 `agent._web_mode = True`（或类似标志）作为防御性编程——但主要还是靠不传递 sink 这个隐式约定
- **Acceptance Criteria Addressed**: FR-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: mock WebTaskManager 调用链 → 捕获 stdout → 断言无流式输出
  - `programmatic` TR-9.2: 对比 sink 存在/缺失两种模式的 stdout 差异
- **Notes**: 这是用户特别关心的一点——**不能让 Web 端看到"两边相同输出"**。需要明确的测试和代码审查验证。

## [ ] Task 10: 支持 thinking 标签显示/隐藏配置
- **Priority**: P1
- **Depends On**: Task 6
- **Description**:
  - `TerminalStreamSink.__init__(self, console, show_thinking: bool)` 接收 `show_thinking` 参数
  - `on_thinking_token(token)` 实现中：如果 `show_thinking is False`，不打印；如果 True，用 dim 样式打印
  - 不改变 `extract_response()` 中对 `<thinking>` 标签的处理——agent 上下文仍然保存完整文本（含 thinking），仅**渲染层**决定是否显示
  - 如果 LLM 返回内联 `<thinking>` 标签而不是独立的 `reasoning_content` 字段，需要在流式 token 中识别标签切换：
    - 累积 token 时检测是否遇到 `<thinking>` / `</thinking>` 文本
    - 遇到打开标签：切换到 thinking 模式（受 `show_thinking` 控制）
    - 遇到关闭标签：切回正文模式
- **Acceptance Criteria Addressed**: FR-3, AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-10.1: `show_thinking=False` → thinking token 不产生 stdout 输出
  - `programmatic` TR-10.2: `show_thinking=True` → thinking token 以 dim 样式输出
  - `programmatic` TR-10.3: 内联 `<thinking>...</thinking>` 格式 → thinking 部分被正确识别和控制

## [ ] Task 11: 编写单元测试
- **Priority**: P0
- **Depends On**: Task 1-10 (与各任务并行编写，随各任务完成)
- **Description**:
  - 在 `tests/test_llm_client_streaming.py`（或集成到现有 `tests/test_agent.py`）中添加测试：
    - 测试 `call_llm_stream` 对 mock 流式响应的 token 顺序和完整文本
    - 测试 `call_llm_auto_stream` 的工具调用流
    - 测试自动降级（stream 不支持 → 非流式回退）
    - 测试 `NullSink` 零副作用
    - 测试 `TerminalStreamSink` 正确响应 show_thinking
  - 复用 `tests/` 中已有的 mock 模式和夹具（如 `monkeypatch` 替换 `openai` client）
  - 不执行真实网络调用
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-8, AC-9, AC-11
- **Test Requirements**:
  - `programmatic` TR-11.1: 所有新增测试通过
  - `programmatic` TR-11.2: 现有测试（`pytest tests/ -x`）**全部**通过，无回归

## [ ] Task 12: 现有测试套件回归验证
- **Priority**: P0
- **Depends On**: Task 11
- **Description**:
  - 运行完整测试套件：`cd /workspace && python -m pytest tests/ -v`
  - 修复任何因签名更改导致的失败（理论上不应该有，因为新增参数都是 keyword-only 且带默认值 None）
- **Acceptance Criteria Addressed**: NFR-3
- **Test Requirements**:
  - `programmatic` TR-12.1: `pytest` 全绿
  - `programmatic` TR-12.2: 检查 `tests/test_cli.py` 中对 `_print_agent_output` 的 mock——如果测试中直接 mock 了 `_print_agent_output`，需确保新的 "跳过流式" 逻辑不影响测试预期

## [ ] Task 13: 安装依赖并手动冒烟测试
- **Priority**: P1
- **Depends On**: Task 12
- **Description**:
  - 确保依赖安装（`pip install -e .` 或等价命令）
  - 手动在本地终端中启动 REPL：
    1. 输入 "hello"（单轮 chat）→ 观察流式输出
    2. 输入 "对 testphp.vulnweb.com 进行侦察"（触发 auto_pentest）→ 观察逐轮流式输出
    3. 切换 `think` 开关 → 观察 thinking 显示/隐藏
    4. Ctrl+C 中断 → 观察优雅中断行为
  - 启动 Web UI (`vulnclaw web`) → 在浏览器中创建任务 → 观察服务端终端**不**输出流式文本，前端正常显示事件
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-6, AC-7
- **Test Requirements**:
  - `human-judgment` TR-13.1: CLI REPL 流式输出体验流畅
  - `human-judgment` TR-13.2: Web UI 无重复输出，功能正常
- **Notes**: 这是最终用户体验验证，自动化测试无法完全替代。

## [ ] Task 14: 无新依赖验证
- **Priority**: P2
- **Depends On**: Task 12
- **Description**:
  - 对比 `requirements.txt` / `pyproject.toml` / `setup.cfg` 的改动 diff
  - 确认未引入新包
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-14.1: `git diff HEAD -- requirements*.txt pyproject.toml setup.cfg setup.py` 输出为空（或仅注释/版本变更，无新包）

---

## 任务依赖图
```
Task 1 (Sink 定义 @ llm_client.py)
  ├─→ Task 2 (call_llm_stream) ─→ Task 3 (call_llm 接入) ─→ Task 7 (AgentCore 透传) ─→ Task 8 (CLI 注入)
  │                                                                                            ├─→ Task 9 (Web 路径验证)
  │                                                                                            └─→ Task 13 (手动冒烟)
  ├─→ Task 4 (call_llm_auto_stream) ─→ Task 5 (call_llm_auto 接入) ─→ Task 7
  ├─→ Task 6 (TerminalStreamSink @ cli/main.py) ─→ Task 8
  └─→ Task 10 (thinking 配置) ─→ Task 6

Task 11 (测试) → 与 Task 2-10 并行，各任务完成后即补对应测试
Task 12 (回归) → 依赖 Task 11 完成
Task 14 (依赖检查) → 最后独立验证

关键路径: Task 1 → Task 2 → Task 3 → Task 7 → Task 8 → Task 9/13
```

## 模块放置检查清单（实现时必须遵守）
- [ ] `StreamSink` Protocol 定义在 `vulnclaw/agent/llm_client.py`
- [ ] `call_llm_stream()` / `call_llm_auto_stream()` 实现放在 `vulnclaw/agent/llm_client.py`
- [ ] `TerminalStreamSink` 实现放在 `vulnclaw/cli/main.py`
- [ ] 不新建 `vulnclaw/agent/stream_output.py` 或其他独立模块
- [ ] `AgentCore` 的 `core.py` 只透传参数，不加业务逻辑
- [ ] 测试文件放在 `tests/test_llm_client_streaming.py`

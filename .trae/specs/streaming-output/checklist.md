# VulnClaw 流式输出功能 - 验证清单

## 验收标准检查点

### AC-1: Chat 模式流式输出
- [ ] **CP-AC1.1**: 用户在 CLI REPL 输入单轮查询后，终端立即显示 "Thinking..." 提示
- [ ] **CP-AC1.2**: LLM 生成的文本逐字/逐块追加到终端，无黑屏等待
- [ ] **CP-AC1.3**: 响应完成后光标位置正确（末尾有换行）
- [ ] **CP-AC1.4**: `agent.context.messages` 中正确存储了完整响应文本（含 thinking 标签）

### AC-2: Auto Pentest 模式流式输出
- [ ] **CP-AC2.1**: 每一轮（Round）的 LLM 生成阶段均为流式输出
- [ ] **CP-AC2.2**: LLM 发起工具调用时，显示 `[工具调用: xxx]` 提示
- [ ] **CP-AC2.3**: 工具执行后的 LLM 总结/分析阶段恢复流式输出
- [ ] **CP-AC2.4**: 各轮之间显示清晰分隔符（如 `-- Round N --`）

### AC-3: Persistent Pentest 模式流式输出
- [ ] **CP-AC3.1**: 每个周期的每一轮中 LLM 输出均为流式
- [ ] **CP-AC3.2**: 周期结束时的 `_generate_attack_summary()` 也使用流式输出
- [ ] **CP-AC3.3**: 周期之间显示周期分隔符和汇总信息

### AC-4: thinking 标签显示控制（关闭）
- [ ] **CP-AC4.1**: `config.session.show_thinking = False` 时，thinking 内容不在终端显示
- [ ] **CP-AC4.2**: agent 上下文中的完整文本仍包含 `<thinking>` 标签（供后续使用）
- [ ] **CP-AC4.3**: 响应文本仅显示最终正文内容

### AC-5: thinking 标签显示控制（开启）
- [ ] **CP-AC5.1**: `config.session.show_thinking = True` 时，thinking 内容以区分样式（dim/italic）流式显示
- [ ] **CP-AC5.2**: 正文内容以普通样式在 thinking 内容之后流式显示
- [ ] **CP-AC5.3**: 内联 `<thinking>...</thinking>` 格式的标签被正确识别和渲染

### AC-6: Web UI 路径不产生终端输出
- [ ] **CP-AC6.1**: 通过 Web UI 发起任务时，服务端进程 stdout 无流式文本输出
- [ ] **CP-AC6.2**: Web 端输出仍通过 `WebTaskManager.publish()` → SSE 事件传递
- [ ] **CP-AC6.3**: 前端正常接收并显示事件，无重复输出

### AC-7: CLI 路径正常输出
- [ ] **CP-AC7.1**: 通过 CLI/REPL 调用时，流式文本实时输出到终端
- [ ] **CP-AC7.2**: 输出不污染服务器日志或其他进程的 stdout

### AC-8: 自动降级到非流式
- [ ] **CP-AC8.1**: LLM Provider 不支持 `stream=True` 时，函数自动切换到非流式调用
- [ ] **CP-AC8.2**: 用户看到完整文本一次性输出（与当前行为一致），无错误提示
- [ ] **CP-AC8.3**: 返回值与流式路径相同（完整字符串）

### AC-9: 返回值完整性
- [ ] **CP-AC9.1**: `call_llm_stream()`/`call_llm_auto_stream()` 返回完整响应字符串
- [ ] **CP-AC9.2**: 返回值包含 thinking 标签（如有）
- [ ] **CP-AC9.3**: 流式返回的字符串与非流式返回的字符串内容一致

### AC-10: 不引入新依赖
- [ ] **CP-AC10.1**: `requirements.txt` / `pyproject.toml` 中未添加新依赖
- [ ] **CP-AC10.2**: 仅使用现有 `openai`、`rich`、`typer` 等库

### AC-11: Ctrl+C 中断行为
- [ ] **CP-AC11.1**: 用户在流式生成过程中按下 Ctrl+C，函数优雅终止
- [ ] **CP-AC11.2**: 已收集的部分文本作为返回值（不丢失）
- [ ] **CP-AC11.3**: 无未刷新的终端缓冲区残留

### AC-12: 错误重试兼容性
- [ ] **CP-AC12.1**: 重试逻辑与流式兼容
- [ ] **CP-AC12.2**: 重试时重新显示 "Thinking..." 或重连提示
- [ ] **CP-AC12.3**: 重试成功后正常流式输出

---

## 代码质量检查点

### 架构检查
- [ ] **CP-ARCH.1**: `StreamSink` Protocol/基类正确定义，所有 sink 方法签名清晰
- [ ] **CP-ARCH.2**: `_NullSink` 正确实现为空操作（无副作用）
- [ ] **CP-ARCH.3**: `call_llm_stream()` 和 `call_llm_auto_stream()` 正确处理流式和非流式降级
- [ ] **CP-ARCH.4**: `TerminalStreamSink` 正确实现 Rich 样式渲染

### 模块放置检查（严格遵循 CONTRIBUTING.md）
- [ ] **CP-MODULE.1**: `StreamSink` 定义在 `vulnclaw/agent/llm_client.py`（非独立模块）
- [ ] **CP-MODULE.2**: `call_llm_stream()` / `call_llm_auto_stream()` 在 `llm_client.py`
- [ ] **CP-MODULE.3**: `TerminalStreamSink` 在 `vulnclaw/cli/main.py`
- [ ] **CP-MODULE.4**: 未创建 `stream_output.py` 或其他独立模块文件
- [ ] **CP-MODULE.5**: `core.py` 只透传 `stream_sink` 参数，无新增业务逻辑

### 向后兼容性检查
- [ ] **CP-BC.1**: `call_llm()` 和 `call_llm_auto()` 的参数签名向后兼容（新增参数有默认值）
- [ ] **CP-BC.2**: 不传 sink 参数时，行为与修改前完全一致
- [ ] **CP-BC.3**: 所有现有调用点（`loop_controller.py`、`core.py`、`orchestrator.py`）无需修改即可工作

### 输出隔离检查
- [ ] **CP-ISO.1**: Web 路径中 agent 调用不传递 `stream_sink`（默认 `None`）
- [ ] **CP-ISO.2**: CLI 路径中正确注入 `TerminalStreamSink`
- [ ] **CP-ISO.3**: `_print_agent_output()` 在流式路径中被正确跳过（或由标志控制）
- [ ] **CP-ISO.4**: WebTaskManager 路径不产生任何 stdout 输出

### 测试覆盖检查
- [ ] **CP-TEST.1**: 新增 `tests/test_llm_client_streaming.py` 存在
- [ ] **CP-TEST.2**: `call_llm_stream` 的 token 顺序和完整文本测试通过
- [ ] **CP-TEST.3**: `call_llm_auto_stream` 的工具调用流测试通过
- [ ] **CP-TEST.4**: 自动降级场景测试通过
- [ ] **CP-TEST.5**: `TerminalStreamSink` 对 show_thinking 配置的正确响应测试通过
- [ ] **CP-TEST.6**: 现有测试套件（`pytest tests/`）全部通过，无回归

### 手动验证检查
- [ ] **CP-MANUAL.1**: 在真实终端中运行 `vulnclaw` REPL → 单轮 chat → 观察到流式输出
- [ ] **CP-MANUAL.2**: 在真实终端中运行带目标的自动渗透 → 观察到每轮流式输出
- [ ] **CP-MANUAL.3**: 切换 `think` 开关 → 观察到 thinking 显示/隐藏
- [ ] **CP-MANUAL.4**: Ctrl+C 中断 → 观察到优雅中断行为
- [ ] **CP-MANUAL.5**: 启动 `vulnclaw web` → Web UI 创建任务 → 确认服务端终端无流式输出

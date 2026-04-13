# nanobot vs agno vs OpenManus：从 Agent 项目的角度做系统性对比

> 对比目标：从 Agent 工程视角（Agent 类/运行链路、上下文工程、工具调用与管理、长短记忆、MCP、Skill 等）分析两个项目的设计取舍与可扩展点，并给出“模板（prompt-as-code/skill 目录结构/工作区 bootstrap）”层面的详细差异。

## 快速对比表（TL;DR）

| 维度 | nanobot | agno | OpenManus |
|---|---|---|---|
| Agent 主体 | 以 `AgentLoop` 为核心引擎，显式管理会话、上下文、工具循环 | 以 `Agent` 为核心配置对象，`run()` 委托到 `_run`，把上下文/工具/存储模块化 | 以 `BaseAgent` 为抽象骨架（step-loop），`ToolCallAgent` 提供工具调用循环，`Manus/...` 作为具体 Agent 组装工具 |
| 上下文工程（System Prompt） | 以工作区文件为中心：`AGENTS.md/SOUL.md/USER.md/TOOLS.md + MEMORY.md + Skills` 拼装 | 以结构化拼装为中心：description/role/instructions/skills/memories/knowledge/summary 等按开关注入，并支持 `{var}` 从 `run_context` 解析 | 以 prompt 常量为中心（`app/prompt/*.py`），system/next-step 两段提示组合，少量 runtime 格式化注入 |
| Tool 管理模型 | `ToolRegistry` 注册 `Tool`，`AgentLoop` 自己执行工具并回填 tool message | `Function/Toolkit` 统一建模；模型层可以“解析并执行 tool calls”，带事件流、hook、HITL（确认/外部执行/用户输入） | `BaseTool` + `ToolCollection`；`ToolCallAgent` 按 tool_call 顺序执行并写入 tool message |
| Tool-call 循环 | 显式 while-loop：LLM -> tool_calls -> execute -> 回填 -> 再问 LLM | 在 `Model` 层实现“拿到 tool_calls -> 生成 FunctionCall -> 执行 -> 回填”并产出事件 | 显式 step-loop：`think()` 调 `llm.ask_tool()` 得到 tool_calls -> `act()` 执行工具 -> 写回 memory |
| 记忆（短/长） | 文件化双层：`HISTORY.md`（可 grep）+ `MEMORY.md`（长期事实），并有 consolidation（LLM 调 tool 保存） | DB/策略化：`MemoryManager` 管理 `UserMemory`，可开启“agentic memory”（提供 `update_user_memory` 工具），并可注入 session summary / learnings / culture | 仅会话内 `Memory.messages`（带 max_messages 截断），无内置长期记忆/总结/检索模块 |
| MCP | 把 MCP server tools 包装成 nanobot `Tool` 注册进 `ToolRegistry` | MCP 作为 `Toolkit`（`MCPTools`）参与 tool 解析/执行；支持 stdio/sse/streamable-http、动态 header、run 级 session 管理、可选 refresh/build | `MCPClients` 连接 SSE/stdio，拉取 tools 后生成 `MCPClientTool`，以 `mcp_{server_id}_{tool}` 命名并加入 `ToolCollection` |
| Skill 形态与调用 | Skill=目录+`SKILL.md`；system prompt 里给 summary + 路径，按需让模型用 `read_file` 读取全文；支持 `always` 注入 | Skill=目录+`SKILL.md`+可选 `scripts/` `references/`；system prompt 给“技能系统说明+技能列表”；通过工具 `get_skill_instructions/reference/script` 访问（可执行脚本，带路径安全校验） | 无独立 skills 子系统（更多依赖：不同 Agent 子类 + prompt + tool 集合来固化能力模板） |
| “模板”落地方式 | 强工作区模板：首次/缺失时把内置模板同步到 workspace（bootstrap + memory 文件骨架） | 更偏“运行期拼装模板”：system message 结构标签化；skills 有独立 spec/验证；不以 workspace 文件作为必选中心 | 更偏“代码内模板”：prompt 常量 + agent 子类默认工具集合；不做 workspace 文件同步 |
| 适用场景倾向 | 追求“可读可改的 prompt-as-files + 轻量工具循环 + 文件式记忆” | 追求“可组合组件化 Agent 框架 + 多能力模块（memory/knowledge/culture）+ 强 tool/HITL/事件体系” | 追求“开箱即用的 ReAct+Tool 应用工程”，偏应用层组装（Browser/Sandbox/MCP 等工具包） |

---

## 1) Agent 类/运行链路：谁是“核心骨架”

### nanobot：`AgentLoop` 是“总控引擎”

- 入口对象是 `AgentLoop`，负责：会话、上下文、工具注册与执行、MCP 连接、迭代收敛等。
- 工具循环是显式 while-loop：每轮调用 provider，检测 `tool_calls`，逐个执行后用 tool message 回填，再继续下一轮。

关键代码（d:\编程学习记录\nanobot\nanobot\agent\loop.py，截取 tool-call 循环主干）：

```python
while iteration < self.max_iterations:
    iteration += 1

    response = await self.provider.chat(
        messages=messages,
        tools=self.tools.get_definitions(),
        model=self.model,
        temperature=self.temperature,
        max_tokens=self.max_tokens,
        reasoning_effort=self.reasoning_effort,
    )

    if response.has_tool_calls:
        tool_call_dicts = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.name, "arguments": json.dumps(tc.arguments, ensure_ascii=False)},
            }
            for tc in response.tool_calls
        ]
        messages = self.context.add_assistant_message(messages, response.content, tool_call_dicts)

        for tool_call in response.tool_calls:
            result = await self.tools.execute(tool_call.name, tool_call.arguments)
            messages = self.context.add_tool_result(messages, tool_call.id, tool_call.name, result)
    else:
        messages = self.context.add_assistant_message(messages, clean)
        final_content = clean
        break
```

### agno：`Agent` 是“配置中枢”，运行由 `_run` 组织

- `Agent.run()` 只是一个薄委托，把输入、`user_id/session_id` 等交给 `_run.run_dispatch`。
- 运行期会统一解析依赖、拼装 `RunMessages`、启动后台任务（memory/learning/culture）、调用 `agent.model.response()`（包含工具调用执行），最终落库与收尾。

关键代码（d:\编程学习记录\agno\libs\agno\agno\agent\agent.py，`run()` 委托到 `_run.run_dispatch`）：

```python
def run(...)-> Union[RunOutput, Iterator[Union[RunOutputEvent, RunOutput]]]:
    return _run.run_dispatch(
        self,
        input=input,
        stream=stream,
        stream_events=stream_events,
        user_id=user_id,
        session_id=session_id,
        session_state=session_state,
        run_context=run_context,
        run_id=run_id,
        ...
    )
```

### OpenManus：`BaseAgent` step-loop + `ToolCallAgent` 工具循环

- `BaseAgent.run()` 做 step-based 循环，并在每步后检查“是否卡住”（重复输出阈值）。
- `ToolCallAgent` 把 tool calling 定型为：`think()` 调 `llm.ask_tool()`，`act()` 执行工具并写回 memory。
- `Manus` 通过默认 `available_tools: ToolCollection` 组装工具，并在启动/运行时接入 MCP tools。

关键代码（d:\编程学习记录\OpenManus\app\agent\base.py，`run()` step-loop）：

```python
async def run(self, request: Optional[str] = None) -> str:
    if self.state != AgentState.IDLE:
        raise RuntimeError(f"Cannot run agent from state: {self.state}")
    if request:
        self.update_memory("user", request)

    results: List[str] = []
    async with self.state_context(AgentState.RUNNING):
        while self.current_step < self.max_steps and self.state != AgentState.FINISHED:
            self.current_step += 1
            step_result = await self.step()
            if self.is_stuck():
                self.handle_stuck_state()
            results.append(f"Step {self.current_step}: {step_result}")

        if self.current_step >= self.max_steps:
            self.current_step = 0
            self.state = AgentState.IDLE
            results.append(f"Terminated: Reached max steps ({self.max_steps})")
    await SANDBOX_CLIENT.cleanup()
    return "\n".join(results) if results else "No steps executed"
```

---

## 2) 上下文工程（Context Engineering）：System Prompt 如何被“工程化”

### nanobot：以 workspace 的“bootstrap 模板文件”作为上下文主干

`ContextBuilder.build_system_prompt()` 的拼装顺序非常明确：

1. identity/runtime/workspace 说明（含 memory/skills 路径约定）
2. `AGENTS.md/SOUL.md/USER.md/TOOLS.md`（存在就读入）
3. `MEMORY.md`（长期记忆）
4. always skills 全文注入（可选）
5. skills summary（progressive loading：只给摘要和 SKILL.md 路径）

关键代码（d:\编程学习记录\nanobot\nanobot\agent\context.py，system prompt 拼装）：

```python
def build_system_prompt(self, skill_names: list[str] | None = None) -> str:
    parts = [self._get_identity()]

    bootstrap = self._load_bootstrap_files()
    if bootstrap:
        parts.append(bootstrap)

    memory = self.memory.get_memory_context()
    if memory:
        parts.append(f"# Memory\n\n{memory}")

    always_skills = self.skills.get_always_skills()
    if always_skills:
        always_content = self.skills.load_skills_for_context(always_skills)
        if always_content:
            parts.append(f"# Active Skills\n\n{always_content}")

    skills_summary = self.skills.build_skills_summary()
    if skills_summary:
        parts.append(f"""# Skills
The following skills extend your capabilities. To use a skill, read its SKILL.md file using the read_file tool.
{skills_summary}""")

    return "\n\n---\n\n".join(parts)
```

同时它把“运行时元数据块”拼到 user message 前（并标注为 metadata-only），避免被当作指令（d:\编程学习记录\nanobot\nanobot\agent\context.py，截取合并逻辑）：

```python
runtime_ctx = self._build_runtime_context(channel, chat_id)
user_content = self._build_user_content(current_message, media)

if isinstance(user_content, str):
    merged = f"{runtime_ctx}\n\n{user_content}"
else:
    merged = [{"type": "text", "text": runtime_ctx}] + user_content
```

### agno：以“结构化标签 + 开关注入 + run_context 变量解析”作为上下文主干

`get_system_message()` 的策略是：

- 如果用户直接提供了 `agent.system_message`（str/Message/callable），优先用它；否则按 `build_context` 开关构建默认 system message。
- 默认 system message 由多段“结构化拼装”组成：description、`<your_role>`、`<instructions>`、`<additional_information>`、tool instructions、expected_output、additional_context、skills snippet、memories/culture/summary/learnings/knowledge instructions、模型侧 system message、输出格式约束（JSON prompt / response model prompt）、可选 `<session_state>` 等。
- 支持 `resolve_in_context`：把 system message 里的 `{var}` 用 `run_context` 的 `session_state/dependencies/metadata/user_id` 做安全替换（通过 `Template.safe_substitute`）。

关键代码（d:\编程学习记录\agno\libs\agno\agno\agent\_messages.py，变量替换）：

```python
format_variables = ChainMap(
    session_state if session_state is not None else {},
    dependencies or {},
    metadata or {},
    {"user_id": user_id} if user_id is not None else {},
)
template = string.Template(converted_msg)
return template.safe_substitute(format_variables)
```

关键代码（d:\编程学习记录\agno\libs\agno\agno\agent\_messages.py，skills/memories 注入片段）：

```python
if agent.skills is not None:
    skills_snippet = agent.skills.get_system_prompt_snippet()
    if skills_snippet:
        system_message_content += f"\n{skills_snippet}\n"

if agent.add_memories_to_context:
    if not user_id:
        user_id = "default"
    if agent.memory_manager is None:
        set_memory_manager(agent)
    user_memories = agent.memory_manager.get_user_memories(user_id=user_id)
    if user_memories and len(user_memories) > 0:
        system_message_content += "<memories_from_previous_interactions>"
        for _memory in user_memories:
            system_message_content += f"\n- {_memory.memory}"
        system_message_content += "\n</memories_from_previous_interactions>\n\n"
```

### OpenManus：prompt 常量 + next-step 引导（更偏应用层）

OpenManus 的“上下文工程”主要集中在 `app/prompt/*.py`，通过 system prompt + next step prompt 的组合来驱动工具选择。

关键代码（d:\编程学习记录\OpenManus\app\prompt\manus.py，节选）：

```python
SYSTEM_PROMPT = (
    "You are OpenManus, an all-capable AI assistant, aimed at solving any task presented by the user. "
    "The initial directory is: {directory}"
)

NEXT_STEP_PROMPT = """
Based on user needs, proactively select the most appropriate tool or combination of tools.
...
If you want to stop the interaction at any point, use the `terminate` tool/function call.
"""
```

对比总结：

- nanobot 更像“固定骨架 + 文件内容注入”，上下文工程的主要扩展点在 workspace 文件/skills 文档。
- agno 更像“可配置流水线”，上下文工程的主要扩展点在 `Agent` 字段、`run_context`、以及 memory/knowledge/culture/summary 等可插拔模块。

---

## 3) 工具调用与管理：Tool 是怎么被建模、选择、执行、回填的

### nanobot：`ToolRegistry` + `Tool` 抽象 + AgentLoop 自己执行

- 工具通过 `ToolRegistry.register()` 注册，LLM 调用时给 provider 的是 `tools.get_definitions()`（tool schema）。
- 运行时对每个 `tool_call`：`registry.execute(name, arguments)` 得到字符串结果，再由 `ContextBuilder.add_tool_result()` 以 `role=tool` 回填到 messages。

关键代码（d:\编程学习记录\nanobot\nanobot\agent\loop.py，执行工具 + 回填 tool message）：

```python
for tool_call in response.tool_calls:
    result = await self.tools.execute(tool_call.name, tool_call.arguments)
    messages = self.context.add_tool_result(messages, tool_call.id, tool_call.name, result)
```

关键代码（d:\编程学习记录\nanobot\nanobot\agent\context.py，回填 tool result）：

```python
def add_tool_result(self, messages, tool_call_id: str, name: str, result: str):
    messages.append(
        {"role": "tool", "tool_call_id": tool_call_id, "name": name, "content": result}
    )
    return messages
```

关键特征：

- 工具执行“在 AgentLoop 内显式发生”，可读性强、路径短、调试直观。
- 没有把“人类确认/外部执行/用户输入”等 HITL 作为工具模型的一等字段（更偏轻量）。

### agno：`Function/Toolkit` 统一建模，工具执行链路在 Model 层更“框架化”

在 agno 里，工具相关分层更细：

1. Agent 侧解析“有哪些工具可用”：`get_tools/aget_tools` 会把用户提供的 tools、默认 memory/knowledge/skills 访问工具等统一合并，还会负责 MCP 工具连接与健康检查。
2. Tool schema 生成：`parse_tools()` 把 `Toolkit/Function/callable/dict` 统一转换成可给模型使用的函数 schema，并把 instructions 片段收集到 `agent._tool_instructions` 里（供 system message 注入）。
3. Tool 执行：`Model.get_function_calls_to_run()` 解析 tool calls，`Model.run_function_call()` 顺序执行并产出事件（started/completed/paused 等），同时构建 tool message 回填。

关键代码（d:\编程学习记录\agno\libs\agno\agno\agent\_tools.py，`parse_tools()` 统一工具建模并收集 tool instructions）：

```python
def parse_tools(agent: Agent, tools: List[Union[Toolkit, Callable, Function, Dict]], model: Model, ...):
    _function_names: List[str] = []
    _functions: List[Union[Function, dict]] = []
    agent._tool_instructions = []

    for tool in tools:
        if isinstance(tool, Dict):
            _functions.append(tool)
        elif isinstance(tool, Toolkit):
            toolkit_functions = tool.get_async_functions() if async_mode else tool.get_functions()
            for name, _func in toolkit_functions.items():
                if name in _function_names:
                    continue
                _function_names.append(name)
                _func = _func.model_copy(deep=True)
                _func._agent = agent
                _func.process_entrypoint(strict=effective_strict)
                _functions.append(_func)
            if tool.add_instructions and tool.instructions is not None:
                agent._tool_instructions.append(tool.instructions)
        ...
    return _functions
```

关键代码（d:\编程学习记录\agno\libs\agno\agno\models\base.py，执行 FunctionCall 并产出 tool_call_started 事件）：

```python
yield ModelResponse(
    content=function_call.get_call_str(),
    tool_executions=[ToolExecution(tool_call_id=function_call.call_id, tool_name=function_call.function.name, tool_args=function_call.arguments)],
    event=ModelResponseEvent.tool_call_started.value,
)

try:
    function_execution_result = function_call.execute()
except AgentRunException as a_exc:
    ...
```

### OpenManus：ToolCollection 执行 + ToolCallAgent 回填

关键代码（d:\编程学习记录\OpenManus\app\agent\toolcall.py，think -> act -> execute_tool，节选）：

```python
response = await self.llm.ask_tool(
    messages=self.messages,
    system_msgs=[Message.system_message(self.system_prompt)] if self.system_prompt else None,
    tools=self.available_tools.to_params(),
    tool_choice=self.tool_choices,
)

self.tool_calls = tool_calls = response.tool_calls if response and response.tool_calls else []

assistant_msg = (
    Message.from_tool_calls(content=content, tool_calls=self.tool_calls)
    if self.tool_calls
    else Message.assistant_message(content)
)
self.memory.add_message(assistant_msg)

for command in self.tool_calls:
    result = await self.execute_tool(command)
    tool_msg = Message.tool_message(
        content=result,
        tool_call_id=command.id,
        name=command.function.name,
        base64_image=self._current_base64_image,
    )
    self.memory.add_message(tool_msg)
```

关键特征：

- `Function` 是一等数据模型，内建 tool hooks、缓存、`requires_confirmation`、`requires_user_input`、`external_execution`、`approval_type` 等（支持 HITL/审计）。
- tool-call 的执行与事件产出更“框架化”，适合构建复杂交互、暂停恢复、审计追踪等能力。

---

## 4) 长短记忆模块：持久化形态与“自动更新”的方式

### nanobot：文件化双层记忆 + consolidation（LLM 调工具保存）

- 长期记忆：`memory/MEMORY.md`
- 历史日志：`memory/HISTORY.md`（鼓励可 grep 的时间前缀）
- consolidation：把旧对话整理成一段 history_entry + 全量 memory_update，并通过 `save_memory` tool call 写回文件，再更新 session 的 `last_consolidated`。

关键代码（d:\编程学习记录\nanobot\nanobot\agent\memory.py，双层存储 + consolidation 的 save_memory tool schema）：

```python
class MemoryStore:
    def __init__(self, workspace: Path):
        self.memory_dir = ensure_dir(workspace / "memory")
        self.memory_file = self.memory_dir / "MEMORY.md"
        self.history_file = self.memory_dir / "HISTORY.md"

_SAVE_MEMORY_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "parameters": {
                "type": "object",
                "properties": {"history_entry": {"type": "string"}, "memory_update": {"type": "string"}},
                "required": ["history_entry", "memory_update"],
            },
        },
    }
]
```

工程取舍：

- 优点：存储透明、可手工编辑、可用传统工具检索；适合“个人工作区 + prompt-as-files”风格。
- 局限：更复杂的检索/权限/多用户隔离/策略优化需要另起模块（目前靠文件 + LLM consolidation）。

### agno：`MemoryManager` + DB 存储 + 可选 agentic memory（工具化更新）

- `MemoryManager` 面向 `UserMemory`（DB schema），对外提供 CRUD/查询/优化策略等能力（具体 DB 可插拔）。
- 在 system message 里可以把“历史用户偏好/信息”注入 `<memories_from_previous_interactions>`。
- 当开启 `enable_agentic_memory` 时，会在上下文里告诉模型可以用 `update_user_memory` 工具来新增/更新/删除/清空记忆（让“记忆更新”成为 agent 行为的一部分）。

关键代码（d:\编程学习记录\agno\libs\agno\agno\memory\manager.py，MemoryManager 以 db 为后端）：

```python
@dataclass
class MemoryManager:
    model: Optional[Model] = None
    db: Optional[Union[BaseDb, AsyncBaseDb]] = None
    delete_memories: bool = True
    update_memories: bool = True
    add_memories: bool = True

    def read_from_db(self, user_id: Optional[str] = None):
        if self.db:
            if user_id is None:
                all_memories: List[UserMemory] = self.db.get_user_memories()
            else:
                all_memories = self.db.get_user_memories(user_id=user_id)
            ...
```

### OpenManus：仅会话内 memory（无长期记忆模块）

关键代码（d:\编程学习记录\OpenManus\app\schema.py，`Memory` 结构）：

```python
class Memory(BaseModel):
    messages: List[Message] = Field(default_factory=list)
    max_messages: int = Field(default=100)

    def add_message(self, message: Message) -> None:
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]
```

工程取舍：

- 优点：天然支持多用户隔离、可扩展存储后端、可叠加策略（summarize/optimize）；更适合产品化/服务化。
- 局限：对“直接读写一份本地 Markdown 作为真相源”的需求不如 nanobot 直观。

---

## 5) MCP（Model Context Protocol）集成方式：当 MCP tools 进入 Agent 体系

### nanobot：把 MCP tools 包装成 nanobot Tool，纳入同一注册表

- 连接 MCP server 后，将 server tool 包装成 `MCPToolWrapper`，命名为 `mcp_{server}_{tool}`，并注册到 `ToolRegistry`。
- 整体上 MCP tool 对 AgentLoop 来说就是“普通工具”，沿用同一套 tool-call 循环。

关键代码（d:\编程学习记录\nanobot\nanobot\agent\tools\mcp.py，包装 MCP tool 为 nanobot Tool）：

```python
class MCPToolWrapper(Tool):
    def __init__(self, session, server_name: str, tool_def, tool_timeout: int = 30):
        self._session = session
        self._original_name = tool_def.name
        self._name = f"mcp_{server_name}_{tool_def.name}"
        self._parameters = tool_def.inputSchema or {"type": "object", "properties": {}}

    async def execute(self, **kwargs: Any) -> str:
        result = await asyncio.wait_for(
            self._session.call_tool(self._original_name, arguments=kwargs),
            timeout=self._tool_timeout,
        )
        ...
```

### agno：把 MCP 当作 `Toolkit`（`MCPTools`），并做 run 级连接管理

`MCPTools` 作为 `Toolkit` 接入 tools 系统，特征包括：

- 支持多 transport（stdio/sse/streamable-http）
- 支持动态 header（`header_provider`），并引入 run_id 维度的 session 生命周期管理（TTL/锁）
- 支持 `refresh_connection`、`include_tools/exclude_tools`、tool 前缀等更丰富的配置

关键代码（d:\编程学习记录\agno\libs\agno\agno\tools\mcp\mcp.py，run 级 session 管理 + 动态 header）：

```python
class MCPTools(Toolkit):
    def __init__(..., transport: Optional[Literal["stdio", "sse", "streamable-http"]] = None, header_provider: Optional[Callable[..., dict[str, Any]]] = None, ...):
        super().__init__(name="MCPTools", **kwargs)
        ...
        if header_provider is not None:
            if self.transport not in ["sse", "streamable-http"]:
                raise ValueError(...)
            self.header_provider = header_provider

        self._run_sessions: dict[str, Tuple[ClientSession, float]] = {}
        self._run_session_contexts: dict[str, Any] = {}
        self._session_ttl_seconds: float = 300.0
        self._session_lock: Optional[asyncio.Lock] = None
```

### OpenManus：MCPClients 拉取 tools -> 生成 MCPClientTool -> 加入 ToolCollection

关键代码（d:\编程学习记录\OpenManus\app\tool\mcp.py，连接并把 server tools 注册为本地可调用 tools）：

```python
async def _initialize_and_list_tools(self, server_id: str) -> None:
    await session.initialize()
    response = await session.list_tools()

    for tool in response.tools:
        original_name = tool.name
        tool_name = f"mcp_{server_id}_{original_name}"
        tool_name = self._sanitize_tool_name(tool_name)

        server_tool = MCPClientTool(
            name=tool_name,
            description=tool.description,
            parameters=tool.inputSchema,
            session=session,
            server_id=server_id,
            original_name=original_name,
        )
        self.tool_map[tool_name] = server_tool

    self.tools = tuple(self.tool_map.values())
```

对比总结：

- nanobot 的 MCP 接入更“薄封装”：一旦注册进 `ToolRegistry`，就与内置工具同权同路。
- agno 的 MCP 接入更“框架化”：把 MCP 视作 `Toolkit`，并在 async tools 解析阶段处理连接/重连/构建。

---

## 6) Skill 系统：Skill 到底是什么？怎么被发现、怎么被调用、如何控制上下文成本

### nanobot：Skill = `skills/<name>/SKILL.md`（workspace 优先）+ progressive loading + always skill

- 扫描路径：workspace skills 优先，其次 builtin skills（同名不重复）。
- 通过 `build_skills_summary()` 把“技能清单（含 path/可用性/缺失依赖）”塞进 system prompt；模型需要时再用 `read_file` 读取 SKILL.md 全文。
- 支持 `always`：满足条件的技能会被全文注入 system prompt（更强约束，但也更占上下文）。

关键代码（d:\编程学习记录\nanobot\nanobot\agent\skills.py，skills summary + always skills，节选）：

```python
def build_skills_summary(self) -> str:
    all_skills = self.list_skills(filter_unavailable=False)
    if not all_skills:
        return ""
    lines = ["<skills>"]
    for s in all_skills:
        skill_meta = self._get_skill_meta(s["name"])
        available = self._check_requirements(skill_meta)
        lines.append(f"  <skill available=\"{str(available).lower()}\">")
        lines.append(f"    <name>{name}</name>")
        lines.append(f"    <location>{path}</location>")
        ...
    lines.append("</skills>")
    return "\n".join(lines)

def get_always_skills(self) -> list[str]:
    result = []
    for s in self.list_skills(filter_unavailable=True):
        skill_meta = self._parse_nanobot_metadata(meta.get("metadata", ""))
        if skill_meta.get("always") or meta.get("always"):
            result.append(s["name"])
    return result
```

### agno：Skill = 结构化 spec（可验证）+ 技能访问工具（instructions/reference/script）

agno 的 Skill 系统更“像一个子产品”：

- `LocalSkills` loader 可以加载单个 skill 目录或多 skill 目录，并可按 spec 验证（失败会抛 `SkillValidationError`）。
- system prompt 注入的是 “skills_system snippet”，强调：Skill 名不是可调用函数，必须通过工具访问，并指导 progressive discovery workflow。
- 提供三类工具：`get_skill_instructions` / `get_skill_reference` / `get_skill_script`（可选 execute=True 运行脚本），并做了路径安全校验，避免路径穿越。

关键代码（d:\编程学习记录\agno\libs\agno\agno\skills\agent_skills.py，system snippet + skill access tools，节选）：

```python
def get_system_prompt_snippet(self) -> str:
    if not self._skills:
        return ""
    lines = [
        "<skills_system>",
        "## IMPORTANT: How to Use Skills",
        "**Skill names are NOT callable functions.**",
        "1. `get_skill_instructions(skill_name)` ...",
        "2. `get_skill_reference(skill_name, reference_path)` ...",
        "3. `get_skill_script(skill_name, script_path, execute=False)` ...",
        "## Available Skills",
    ]
    for skill in self._skills.values():
        lines.append("<skill>")
        lines.append(f"  <name>{skill.name}</name>")
        lines.append(f"  <description>{skill.description}</description>")
        ...
    lines.append("</skills_system>")
    return "\n".join(lines)

def get_tools(self) -> List[Function]:
    tools: List[Function] = []
    tools.append(Function(name="get_skill_instructions", entrypoint=self._get_skill_instructions, ...))
    tools.append(Function(name="get_skill_reference", entrypoint=self._get_skill_reference, ...))
    tools.append(Function(name="get_skill_script", entrypoint=self._get_skill_script, ...))
    return tools
```

### OpenManus：无独立 skills 子系统

- 更倾向用“不同 Agent 子类 + 默认 tool 集合 + prompt”来固化能力模板，而不是提供一个可加载/可发现/可按需注入的 skills 目录机制。

对比总结：

- nanobot：把 “skill 使用说明”更多交给 SKILL.md 内容本身，并依赖通用文件工具 `read_file`。
- agno：把 “skill 使用流程”固化到系统提示与专用工具中，Skill 访问更可控，且支持脚本执行与 references 的强区分。

---

## 7) “模板”层面的详细对比：prompt-as-code / workspace bootstrap / skill 目录结构

这里的“模板”不是指某个单一文件，而是指：项目把 Agent 的“行为规范/上下文骨架/可扩展能力”如何固化为可复用的结构。

### 7.1 nanobot 的模板体系：workspace bootstrap 文件是第一公民

nanobot 会把内置模板同步到 workspace（只补缺失文件），形成一个“可编辑的 prompt-as-files 工作区”：

- 根目录 bootstrap：`AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`
- 记忆文件：`memory/MEMORY.md`, `memory/HISTORY.md`
- 技能目录：`skills/`

关键代码（d:\编程学习记录\nanobot\nanobot\utils\helpers.py，只创建缺失模板文件）：

```python
def sync_workspace_templates(workspace: Path, silent: bool = False) -> list[str]:
    """Sync bundled templates to workspace. Only creates missing files."""
    added: list[str] = []

    def _write(src, dest: Path):
        if dest.exists():
            return
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(src.read_text(encoding="utf-8") if src else "", encoding="utf-8")
        added.append(str(dest.relative_to(workspace)))

    for item in tpl.iterdir():
        if item.name.endswith(".md"):
            _write(item, workspace / item.name)
    _write(tpl / "memory" / "MEMORY.md", workspace / "memory" / "MEMORY.md")
    _write(None, workspace / "memory" / "HISTORY.md")
    (workspace / "skills").mkdir(exist_ok=True)
    return added
```

模板的意义：

- bootstrap 文件本质是“可版本化的系统提示片段”，用户可以像改配置一样改提示。
- MEMORY/HISTORY 是“可落地的长期状态”，并且完全可人工审阅。

### 7.2 agno 的模板体系：运行期 system message 结构化拼装 + skill spec 模板

agno 不强制一个 workspace 文件体系作为上下文主轴，它更偏向：

- 用 `get_system_message()` 生成一个带结构标签的 system message（可按开关组合）
- 用 skill 目录 spec（`SKILL.md + scripts/ + references/`）作为“技能模板”，并可验证目录结构与内容
- 用 tools/memory/knowledge 等模块作为“能力模板”，按需注入到 system message 或工具列表中

关键代码（d:\编程学习记录\agno\libs\agno\agno\agent\_messages.py，system message 生成入口）：

```python
def get_system_message(
    agent: Agent,
    session: AgentSession,
    run_context: Optional[RunContext] = None,
    tools: Optional[List[Union[Function, dict]]] = None,
    add_session_state_to_context: Optional[bool] = None,
) -> Optional[Message]:
    ...
```

关键代码（d:\编程学习记录\agno\libs\agno\agno\skills\skill.py，Skill 数据模型）：

```python
@dataclass
class Skill:
    name: str
    description: str
    instructions: str
    source_path: str
    scripts: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    license: Optional[str] = None
    compatibility: Optional[str] = None
    allowed_tools: Optional[List[str]] = None
```

关键代码（d:\编程学习记录\agno\libs\agno\agno\skills\loaders\local.py，LocalSkills loader 识别“单 skill / 多 skill”目录）：

```python
skill_md_path = self.path / "SKILL.md"
if skill_md_path.exists():
    skill = self._load_skill_from_folder(self.path)
    if skill:
        skills.append(skill)
else:
    for item in self.path.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                skill = self._load_skill_from_folder(item)
                if skill:
                    skills.append(skill)
```

### 7.3 OpenManus 的模板体系：prompt 模块 + agent 子类默认组装

- prompt 模板：集中在 `OpenManus\app\prompt\`（例如 `manus.py`），属于典型的 prompt-as-code（常量/字符串模板）。
- agent 能力模板：集中在 `OpenManus\app\agent\`，通过不同 Agent 子类的默认 `available_tools: ToolCollection` 固化能力组合。

关键代码（d:\编程学习记录\OpenManus\app\agent\manus.py，模板如何落到 Agent 默认值）：

```python
class Manus(ToolCallAgent):
    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(),
            BrowserUseTool(),
            StrReplaceEditor(),
            AskHuman(),
            StringReverseTool(),
            Terminate(),
        )
    )
```

模板的意义：

- system prompt 的结构是“代码生成的模板”，而不是“文件拼装的模板”。
- skill 的访问是“工具化模板”，而不是依赖通用文件工具的自由读取。

---

## 8) 选型建议（按工程偏好）

- 你想把 Agent 的“人格/规则/上下文骨架”像配置文件一样放在 workspace，随时可手改、可 diff、可 grep：更偏 nanobot。
- 你想要一个可组合的 Agent 框架，天然有 memory/knowledge/culture/session summary、HITL、工具事件流、可插拔后端：更偏 agno。
- 你更关心“可运行的应用工程骨架”，希望用多个具体 Agent（Browser/Sandbox/MCP/DataAnalysis）快速拼装可用能力：更偏 OpenManus。


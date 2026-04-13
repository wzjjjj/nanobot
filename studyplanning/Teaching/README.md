# nanobot 源码学习：教学索引

这套教学材料面向“读源码学架构”，采用从大到小、逐层递进的方式：先建立系统全局模型，再逐条主链路深挖到可改代码的程度。

- 课程大纲（总览）：[Course_Syllabus.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Course_Syllabus.md)
- 架构原始材料：[ARCHITECTURE.md](file:///d:/编程学习记录/nanobot/studyplanning/ARCHITECTURE.md) · [LEARNING_ROADMAP.md](file:///d:/编程学习记录/nanobot/studyplanning/LEARNING_ROADMAP.md)

## 学习建议（强烈推荐）

- 每节课先回答“关键问题”，再看代码；不要从第 1 行读到最后 1 行。
- 走读时只做三件事：找入口、跟数据、画边界。
- 每节课至少做 1 个小实验（可以是“破坏性实验”）：改一行，看系统如何崩/如何跑。

## 专题导读：从源码学 Agent 工程（上下文 / 工具 / 轨迹 / 状态 / 成本）

这确实是一个典型的 **Agent 项目**：它把“LLM 调用 + 工具执行 + 多轮循环 + 状态持久化 + 渠道收发”做成了一个可运行的工程化系统。核心引擎在 [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L35-L509)，你可以用下面 5 个专题把这类项目的关键设计一次性打穿。

### 1) 上下文工程（Context Engineering）

- **system prompt 组装：身份 + bootstrap + memory + skills**
  - 入口：ContextBuilder 的 [build_system_prompt](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L27-L55)
  - 关键点：把长期记忆（MEMORY.md）直接注入 system，而把技能做成“摘要常驻、正文按需加载”的 progressive loading
    - skills 摘要：[build_skills_summary](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L101-L141)
    - always skills：[get_always_skills](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L193-L202)
- **runtime context 注入：把“元数据”与 user 合并，且声明不可信**
  - 构造与合并：[_build_runtime_context](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L99-L108) + [build_messages](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L121-L145)
  - 设计理由：避免某些 provider 拒绝“连续同角色消息”（同样是 user 的两条）
- **写入 session 时“去污染”：runtime context 不落盘**
  - 写入点：[_save_turn](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L455-L489)
  - 设计理由：runtime context 是每次请求的动态噪声，落盘会挤占上下文窗口并污染后续检索

动手练习（推荐做一个就够）：把 [build_system_prompt](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L27-L55) 的产物打印出来（CLI 模式），然后删掉 workspace 下某个 bootstrap 文件，观察模型行为变化。

### 2) 工具调用（Tool Calling）与“可用能力面”

- **工具能力面由 ToolRegistry 决定**
  - schema 导出：[ToolRegistry.get_definitions](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py#L34-L37) → [Tool.to_schema](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L172-L182)
  - 默认注册：[AgentLoop._register_default_tools](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L115-L132)
- **参数可靠性：cast + validate，失败时给模型“换路”的提示**
  - 参数校验与错误提示：[ToolRegistry.execute](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py#L38-L60)
  - schema 驱动的类型转换：[Tool.cast_params](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L55-L122)
- **tool_call ↔ tool_result 的绑定：tool_call_id 必须一致**
  - 写回点：[add_tool_result](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L169-L175)
  - Provider 兼容性：LiteLLM 会把 id 归一化并保持两侧同步，避免严格 provider 报错
    - [LiteLLMProvider._sanitize_messages](file:///d:/编程学习记录/nanobot/nanobot/providers/litellm_provider.py#L180-L207)

动手练习：把某个 tool 的 parameters 故意改成更严格（比如整数范围），观察模型如何在 [ToolRegistry.execute](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py#L38-L60) 的错误提示引导下自我修正。

### 3) 任务轨迹（Task Trace / Progress）设计

- **进度流的抽象：on_progress 回调 + bus/outbound 的 metadata 标记**
  - 发送进度：[_bus_progress](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L427-L434)（`_progress` / `_tool_hint`）
  - 渠道侧过滤：ChannelManager 会按配置决定是否把进度/工具提示推到用户侧
    - [ChannelManager._dispatch_outbound](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L208-L236)
    - 配置开关：[ChannelsConfig](file:///d:/编程学习记录/nanobot/nanobot/config/schema.py#L204-L218)
- **“可读的轨迹”：把 tool_calls 格式化成一句话提示**
  - 格式化：[_tool_hint](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L169-L178)
  - 剥离模型的 `<think>` 噪声：[_strip_think](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L162-L168)

动手练习：打开 send_tool_hints，让你在真实聊天里看到 tool hint；然后比较关闭时的用户体验差异（信息密度 vs 干扰）。

### 4) 状态管理（Session / Memory / Cancellation）

- **会话状态：JSONL 持久化 + 只追加（append-only）**
  - Session 设计说明：见 [Session](file:///d:/编程学习记录/nanobot/nanobot/session/manager.py#L16-L34)
  - 历史裁剪（对齐到 user turn，避免孤儿 tool_result）：[get_history](file:///d:/编程学习记录/nanobot/nanobot/session/manager.py#L46-L65)
- **记忆：长记忆（MEMORY.md）常驻 + 历史（HISTORY.md）可检索**
  - consolidation 的核心策略：保留最近半窗，把更老的对话交给 LLM 提炼后写文件
    - [MemoryStore.consolidate](file:///d:/编程学习记录/nanobot/nanobot/agent/memory.py#L65-L157)
  - 触发点：session 超过 memory_window 后后台 consolidate
    - [AgentLoop._process_message](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L396-L413)
- **取消与并发：/stop 取消当前 session 的所有任务 + 子 agent**
  - [AgentLoop._handle_stop](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L278-L293)

动手练习：在一次较长任务中发送 /stop，观察主任务与子任务的取消是否都生效，以及渠道侧是否还会继续刷进度消息。

### 5) 成本与延迟控制（Cost / Latency Controls）

- **控制上下文尺寸（最直接的成本手柄）**
  - memory_window（输入历史窗口）：[AgentLoop.__init__](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L49-L80) + [AgentDefaults.memory_window](file:///d:/编程学习记录/nanobot/nanobot/config/schema.py#L221-L234)
  - tool result 截断（避免一次工具返回把上下文打爆）：[_save_turn](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L455-L465)
  - exec 输出截断与超时：[ExecTool.execute](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/shell.py#L66-L124)
- **控制 provider “400/循环污染”风险（把失败隔离在本轮）**
  - provider error 不写入 session：[_run_agent_loop](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L235-L247)
  - 请求前清洗空 content（大量 400 的根源）：[LLMProvider._sanitize_empty_content](file:///d:/编程学习记录/nanobot/nanobot/providers/base.py#L44-L88)
- **利用“提示词缓存”能力（若 provider 支持）**
  - LiteLLM：给 system 与 tools 注入 cache_control（ephemeral），让支持缓存的网关/模型复用提示词
    - [LiteLLMProvider._apply_cache_control](file:///d:/编程学习记录/nanobot/nanobot/providers/litellm_provider.py#L126-L150)
  - OpenAI Codex Responses：显式发送 prompt_cache_key
    - [OpenAICodexProvider.chat](file:///d:/编程学习记录/nanobot/nanobot/providers/openai_codex_provider.py#L27-L80)
- **把“不可控慢点”超时掉（工具侧）**
  - MCP tool 超时：[MCPToolWrapper.execute](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/mcp.py#L37-L71)

动手练习：把 memory_window 调小（比如 20），再做一个需要长历史的任务，对比“成本下降”与“能力退化”的平衡点；然后通过 MEMORY.md 的抽象化写法把能力拉回来。

## Module 01：全局视野

- Lesson 01：项目目标与核心架构（你要先能画出架构草图）
  - [Module_01_Lesson_01_architecture_overview.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_01_Lesson_01_architecture_overview.md)
- Lesson 02：目录结构与关键模块（你要先知道每个目录“管什么”）
  - [Module_01_Lesson_02_project_structure.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_01_Lesson_02_project_structure.md)
- Lesson 03：启动流程与配置加载（你要能从 CLI 一步步走到 AgentLoop）
  - [Module_01_Lesson_03_bootstrap_and_config.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_01_Lesson_03_bootstrap_and_config.md)

## Module 02：核心链路（从消息到回复）

- Lesson 01：消息生命周期（Channel → Bus → Agent → Outbound）
  - [Module_02_Lesson_01_message_lifecycle.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_02_Lesson_01_message_lifecycle.md)
- Lesson 02：AgentLoop 迭代（LLM ↔ Tools 的多轮循环）
  - [Module_02_Lesson_02_agent_loop.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_02_Lesson_02_agent_loop.md)
- Lesson 03：ContextBuilder（Prompt 如何拼出来、如何演进）
  - [Module_02_Lesson_03_context_building.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_02_Lesson_03_context_building.md)

## Module 03：关键子系统（工具 / 记忆 / 技能）

- Lesson 01：工具系统与注册表（Tool → ToolRegistry → Function Calling）
  - [Module_03_Lesson_01_tools_and_registry.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_03_Lesson_01_tools_and_registry.md)
- Lesson 02：双层记忆系统（Session JSONL + MEMORY/HISTORY）
  - [Module_03_Lesson_02_memory_system.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_03_Lesson_02_memory_system.md)
- Lesson 03：技能系统（Markdown Skill + progressive loading）
  - [Module_03_Lesson_03_skill_system.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_03_Lesson_03_skill_system.md)

## Module 04：基础设施与扩展（并发 / 渠道 / Provider）

- Lesson 01：异步总线与并发模型（asyncio.Queue + dispatcher）
  - [Module_04_Lesson_01_bus_and_async.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_04_Lesson_01_bus_and_async.md)
- Lesson 02：渠道层设计（BaseChannel + ChannelManager）
  - [Module_04_Lesson_02_channels_design.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_04_Lesson_02_channels_design.md)
- Lesson 03：Provider 抽象层（统一 chat() + LiteLLM 适配）
  - [Module_04_Lesson_03_provider_layer.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_04_Lesson_03_provider_layer.md)

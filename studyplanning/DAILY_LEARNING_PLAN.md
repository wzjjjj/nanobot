# nanobot 每日学习计划 (7天速成)

这份计划结合了 [nanobot 源码解析文章](https://mp.weixin.qq.com/s/k_cpKKIzjFDzjqKO29-5ow) 与项目实际结构，旨在帮助你从零开始深入理解 nanobot 的设计与实现。

## 学习目标
1.  **掌握架构**：理解 Agent Loop、Bus、Context 等核心组件的交互。
2.  **理解流程**：通过代码追踪消息从输入到输出的全过程。
3.  **动手实践**：能够修改代码、增加工具或 Skill。

---

## Day 1: 环境搭建与初体验 (Phase 0)

### 目标
- 跑通项目，确保环境正常。
- 体验 CLI 交互，观察日志。
- 建立对项目目录结构的整体认知。

### 核心阅读
- [README.md](../README.md) (项目主文档)
- [studyplanning/PHASE_0_SETUP.md](PHASE_0_SETUP.md) (环境搭建指南)
- [nanobot/cli/commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py) (CLI 入口)

### 任务
1.  **环境准备**：配置 Python 环境，安装依赖。
2.  **运行 Hello World**：使用 `nanobot agent -m "Hello"` 运行一次简单的对话。
3.  **开启日志**：使用 `--logs` 参数运行，观察控制台输出的日志流。
4.  **目录浏览**：对照文章提到的“分层架构”，浏览 `nanobot/` 下的子目录（agent, bus, channels, tools 等）。

### 检验
- [ ] 能成功运行 `nanobot agent -m "你好"` 并收到回复。
- [ ] 能在日志中看到 "Agent loop started" 和 "Processing message" 等关键信息。
- [ ] 能说出 `nanobot/agent` 和 `nanobot/channels` 分别是做什么的。

---

## Day 2: 核心架构与消息流转 (Phase 1 - Part 1)

### 目标
- 理解文章中提到的 **"外部处理流程"**。
- 掌握消息如何从 CLI/Channel 进入系统，经过 Session 处理，最终到达 Agent Loop。

### 核心阅读
- [nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py) (核心：`_process_message`, `get_or_create`)
- [nanobot/session/manager.py](file:///d:/编程学习记录/nanobot/nanobot/session/manager.py) (会话管理)
- [nanobot/agent/context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py) (上下文构建)

### 任务
1.  **追踪 Session**：在 `loop.py` 中找到 `session = self.sessions.get_or_create(msg.session_key)`，理解 Session 是如何被检索或创建的。
2.  **追踪 History**：看 `session.get_history()` 如何获取历史消息。
3.  **追踪 Context**：看 `self.context.build_messages(...)` 如何将 System Prompt、History 和当前消息组装成 LLM 的输入。

### 检验
- [ ] 能画出一条消息从 `_process_message` 开始，经过 Session 获取、Context 构建，最后进入 `_run_agent_loop` 的流程图。
- [ ] 能解释为什么 Session 需要 `get_or_create`。
- [ ] 能找到 System Prompt 是在哪里定义的（提示：`ContextBuilder`）。

---

## Day 3: 大脑 - Agent Loop 与 ReAct (Phase 1 - Part 2)

### 目标
- 理解文章中提到的 **"内部 Agent 循环 ReAct 的过程"**。
- 掌握 LLM 如何决定调用工具，以及工具结果如何回填。

### 核心阅读
- [nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py) (核心：`_run_agent_loop`)
- [nanobot/providers/base.py](file:///d:/编程学习记录/nanobot/nanobot/providers/base.py) (LLM 接口)

### 任务
1.  **循环逻辑**：阅读 `_run_agent_loop` 方法，重点看 `while iteration < self.max_iterations:` 循环体。
2.  **工具调用**：找到 `response.has_tool_calls` 的判断逻辑，看代码如何处理工具调用（Tool Execution）和结果回填（Tool Result）。
3.  **Prompt 演化**：思考在多轮工具调用中，`messages` 列表是如何变化的（User -> Assistant(Tool Call) -> Tool(Result) -> Assistant(Final)）。

### 检验
- [ ] 能解释 `max_iterations` 的作用。
- [ ] 能描述当 LLM 决定调用工具时，`_run_agent_loop` 发生了什么（Message 列表增加了什么）。
- [ ] 能找到工具执行结果是如何被添加回 `messages` 列表的。

---

## Day 4: 记忆系统 (Memory System)

### 目标
- 理解文章提到的 **"Memory 持久化记忆"**。
- 掌握 nanobot 的双层记忆机制：`MEMORY.md` (长期事实) vs `HISTORY.md` (完整日志)。

### 核心阅读
- [nanobot/agent/memory.py](file:///d:/编程学习记录/nanobot/nanobot/agent/memory.py) (MemoryStore)
- [nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py) (核心：`_consolidate_memory`)
- [nanobot/skills/memory/SKILL.md](file:///d:/编程学习记录/nanobot/nanobot/skills/memory/SKILL.md) (记忆 Skill 定义)

### 任务
1.  **文件结构**：查看 `workspace/memory/` 目录，了解 `MEMORY.md` 和 `HISTORY.md` 的内容。
2.  **Consolidation**：阅读 `_consolidate_memory` 方法，理解系统何时触发记忆整理，以及如何使用 LLM 将对话压缩成 Summary 和 Facts。
3.  **检索机制**：看 `ContextBuilder` 如何将 `MEMORY.md` 的内容注入到 System Prompt 中。

### 检验
- [ ] 能解释 `MEMORY.md` 和 `HISTORY.md` 的区别。
- [ ] 能触发一次 Consolidation（可以通过修改 `memory_window` 参数或发送大量消息）。
- [ ] 能说出 Agent 是如何“想起”之前发生的事情的（grep vs context）。

---

## Day 5: 工具与技能 (Tools & Skills)

### 目标
- 理解文章提到的 **"Tools 工具执行系统"**。
- 学习如何扩展 Agent 的能力。

### 核心阅读
- [nanobot/agent/tools/registry.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py) (工具注册)
- [nanobot/agent/tools/base.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py) (工具基类)
- [nanobot/agent/skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py) (Skill 加载)
- [nanobot/skills/](file:///d:/编程学习记录/nanobot/nanobot/skills/) (查看现有的 Skill)

### 任务
1.  **工具注册**：看 `ToolRegistry` 如何自动发现和注册工具。
2.  **Skill 结构**：打开一个 Skill（如 `weather` 或 `github`），看 `SKILL.md` 是如何定义的。
3.  **Context 注入**：看 `ContextBuilder` 如何根据 Skill 的定义将其 prompt 注入到上下文中。

### 检验
- [ ] 能解释 Tool 和 Skill 的区别（Tool 是代码函数，Skill 是 Prompt/文档/资源集合）。
- [ ] 尝试创建一个简单的 Skill（参考 `skill-creator`）。
- [ ] 尝试修改一个现有的 Tool 或添加一个新的 Tool。

---

## Day 6: 工程细节 - Bus 与 Channels (Bus & Channels)

### 目标
- 理解文章提到的 **"Bus 消息路由与队列"** 和 **"Channels 聊天平台适配层"**。
- 理解异步消息架构如何解耦 Agent 和外部平台。

### 核心阅读
- [nanobot/bus/queue.py](file:///d:/编程学习记录/nanobot/nanobot/bus/queue.py) (MessageBus)
- [nanobot/bus/events.py](file:///d:/编程学习记录/nanobot/nanobot/bus/events.py) (消息定义)
- [nanobot/channels/base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py) (Channel 基类)
- [nanobot/channels/manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py) (Channel 管理)

### 任务
1.  **消息总线**：看 `MessageBus` 如何使用 `asyncio.Queue` 实现 `consume_inbound` 和 `publish_outbound`。
2.  **Channel 适配**：选择一个 Channel（如 `cli` 或 `telegram`），看它如何将接收到的外部事件转换为 `InboundMessage` 并推送到 Bus。
3.  **Outbound 流程**：看 Agent 产生的 `OutboundMessage` 如何通过 Bus 分发回对应的 Channel。

### 检验
- [ ] 能解释为什么需要 MessageBus 而不是 Agent 直接调用 Channel API。
- [ ] 能画出 Channel -> Bus -> Agent -> Bus -> Channel 的数据流向图。
- [ ] 能说出 `InboundMessage` 中包含了哪些关键字段（session_key, content, etc.）。

---

## Day 7: 进阶与总结 (Advanced & Synthesis)

### 目标
- 融会贯通，尝试进行一些高级配置或修改。
- 总结学习成果。

### 核心阅读
- [nanobot/config/schema.py](file:///d:/编程学习记录/nanobot/nanobot/config/schema.py) (配置定义)
- [nanobot/agent/subagent.py](file:///d:/编程学习记录/nanobot/nanobot/agent/subagent.py) (Subagent 机制)

### 任务
1.  **配置修改**：尝试修改 `config.yaml`（如果存在）或相关配置代码，调整 Agent 的行为（如模型参数、工具开关）。
2.  **Subagent**：阅读 `spawn` 工具和 `SubagentManager`，理解 Agent 如何派生子 Agent 处理后台任务。
3.  **回顾**：重新阅读一遍源码解析文章，看现在是否能完全看懂其中的每一句话和代码片段。

### 检验
- [ ] 能自信地回答文章中提出的问题。
- [ ] 能够向别人解释 nanobot 的架构。
- [ ] 完成一个小的功能开发（如添加一个新的 Slash Command 或一个新的 Tool）。

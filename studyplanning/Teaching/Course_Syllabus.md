# nanobot 源码学习课程大纲

本课程以“从大到小、逐层递进”为原则：先建立全局架构模型，再沿着关键链路把代码读到能改、能扩展的程度。

入口索引：[README.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/README.md)

## Module 01：全局视野

- Lesson 01：项目目标与核心架构
  - 目标：能说清 nanobot 的两种运行形态（CLI 直连 / Gateway），并画出模块边界图。
  - 正文：[Module_01_Lesson_01_architecture_overview.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_01_Lesson_01_architecture_overview.md)
- Lesson 02：目录结构与关键模块
  - 目标：能把 `nanobot/` 顶级目录映射到“职责分层”。
  - 正文：[Module_01_Lesson_02_project_structure.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_01_Lesson_02_project_structure.md)
- Lesson 03：启动流程与配置加载
  - 目标：能从 CLI 入口一路追到 AgentLoop 的创建，并知道配置从哪里来。
  - 正文：[Module_01_Lesson_03_bootstrap_and_config.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_01_Lesson_03_bootstrap_and_config.md)

## Module 02：核心链路（从消息到回复）

- Lesson 01：消息生命周期
  - 目标：能追踪消息从 Channel 到 Agent，再到 Outbound 的完整路径。
  - 正文：[Module_02_Lesson_01_message_lifecycle.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_02_Lesson_01_message_lifecycle.md)
- Lesson 02：AgentLoop 迭代（LLM ↔ Tools）
  - 目标：能解释为什么要多轮迭代、迭代何时停止、tool_call 如何回填。
  - 正文：[Module_02_Lesson_02_agent_loop.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_02_Lesson_02_agent_loop.md)
- Lesson 03：ContextBuilder（Prompt 拼装）
  - 目标：能说清 system prompt 的组成、skills 的 progressive loading，以及 runtime context 合并策略。
  - 正文：[Module_02_Lesson_03_context_building.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_02_Lesson_03_context_building.md)

## Module 03：关键子系统（工具 / 记忆 / 技能）

- Lesson 01：工具系统与注册表
  - 目标：能读懂 Tool 的 schema/validate/execute，并能新增一个工具的最小实现。
  - 正文：[Module_03_Lesson_01_tools_and_registry.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_03_Lesson_01_tools_and_registry.md)
- Lesson 02：双层记忆系统
  - 目标：能说清 Session 与 Memory 的分工，以及 consolidation 何时触发、写到哪里。
  - 正文：[Module_03_Lesson_02_memory_system.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_03_Lesson_02_memory_system.md)
- Lesson 03：技能系统
  - 目标：能解释 Skill 的加载优先级（workspace > builtin）和 always skill 机制。
  - 正文：[Module_03_Lesson_03_skill_system.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_03_Lesson_03_skill_system.md)

## Module 04：基础设施与扩展（并发 / 渠道 / Provider）

- Lesson 01：异步总线与并发模型
  - 目标：理解 `asyncio.Queue` 的解耦价值，理解 outbound dispatcher 的职责。
  - 正文：[Module_04_Lesson_01_bus_and_async.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_04_Lesson_01_bus_and_async.md)
- Lesson 02：渠道层设计
  - 目标：能按 BaseChannel 的接口写一个新渠道的骨架，并知道路由点在哪里。
  - 正文：[Module_04_Lesson_02_channels_design.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_04_Lesson_02_channels_design.md)
- Lesson 03：Provider 抽象层
  - 目标：能解释 ProviderRegistry 的“单一真相”，以及 LiteLLMProvider 如何规整请求/响应。
  - 正文：[Module_04_Lesson_03_provider_layer.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_04_Lesson_03_provider_layer.md)


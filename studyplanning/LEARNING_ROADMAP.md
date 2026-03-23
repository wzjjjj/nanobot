# nanobot 源码学习路线 (Total-Split-Total 架构)

为了更深入、系统地学习 nanobot 项目，本计划采用 **“总（Total）- 分（Split）- 总（Total）”** 的结构进行编排。

这份路线图将不仅仅是“读代码”，而是通过 **“提出问题 -> 追踪实现 -> 动手验证”** 的循环来构建你的认知体系。

## 第一部分：总 (Total) - 全局视野与核心概念

在深入细节之前，我们需要先建立对 nanobot 的宏观认知。这部分不仅仅是看文档，而是要通过观察和简单的交互来理解系统的边界和核心组件。

**目标**：理解 nanobot 的设计哲学、核心组件及其职责边界。
**产出**：能手绘出系统的架构草图。

- [**Day 01: 全局概览与环境搭建**](days/Day_01_Overview_and_Setup.md)
  - 核心任务：跑通环境，通过日志观察一次完整的交互流程，识别核心模块（Agent, Bus, Channels, Tools）。

---

## 第二部分：分 (Split) - 模块深度拆解

这是学习的核心阶段。我们将系统拆解为独立的模块，逐个击破。每个模块的学习都遵循“从外到内”的顺序。

**目标**：能够向他人详细解释每个模块的工作原理，并能进行代码级的修改。

### 阶段一：消息流与大脑 (Message Flow & Brain)
- [**Day 02: 消息流转机制 (Message Lifecycle)**](days/Day_02_Message_Lifecycle.md)
  - 深度追踪：`Channel` -> `Bus` -> `Session` -> `Agent` 的全链路。
  - 关键问题：消息是如何被标准化（InboundMessage）的？Session 是如何维持对话状态的？

- [**Day 03: Agent 核心循环 (The Loop & ReAct)**](days/Day_03_Agent_Loop.md)
  - 深度追踪：`_run_agent_loop` 的内部逻辑。
  - 关键问题：LLM 是如何决定调用工具的？工具的执行结果是如何回填到 Prompt 中的？Prompt 是如何演进的？

### 阶段二：记忆与扩展 (Memory & Extensions)
- [**Day 04: 双层记忆系统 (Memory System)**](days/Day_04_Memory_System.md)
  - 深度追踪：`MEMORY.md` (事实) 与 `HISTORY.md` (日志) 的读写机制。
  - 关键问题：Agent 何时决定“记住”一件事？记忆是如何被检索并注入到 Context 中的？

- [**Day 05: 工具与技能体系 (Tools & Skills)**](days/Day_05_Tools_and_Skills.md)
  - **更新**：新增 **MCP (Model Context Protocol)** 和 **Skill System** 学习内容。
  - 深度追踪：`ToolRegistry`、`MCPToolWrapper` 与 `SkillsLoader`。
  - 关键问题：如何集成 MCP 工具？Skill 是如何通过 Markdown 定义并增强 Agent 能力的？

### 阶段三：基础设施 (Infrastructure)
- [**Day 06: 异步总线与多渠道 (Bus & Channels)**](days/Day_06_Bus_and_Channels.md)
  - **更新**：新增 **Matrix** 等新 Channel 的适配学习。
  - 深度追踪：`asyncio.Queue` 在 `MessageBus` 中的应用。
  - 关键问题：系统如何处理高并发消息？如何实现跨平台的统一接口？

---

## 第三部分：总 (Total) - 融会贯通与实战

最后，我们将所有模块重新组合，通过一个综合性的实战任务来检验学习成果。

**目标**：具备独立开发 Agent 功能的能力，能对架构进行改进。

- [**Day 07: 架构复盘与实战演练**](days/Day_07_Synthesis_and_Action.md)
  - 核心任务：实现一个跨模块的新功能（例如：添加一个新的 Slash Command，或者集成一个新的 Channel）。
  - 深度思考：nanobot 的架构有哪些优缺点？如果让你重构，你会怎么做？

---

## 学习方法建议

1.  **带着问题读代码**：不要从第一行读到最后一行。先问自己“这个功能是怎么实现的？”，然后去代码里找答案。
2.  **利用 IDE 功能**：多用“跳转到定义”（Go to Definition）和“查找引用”（Find Usages）。
3.  **动手改代码**：最好的验证方法是修改代码，看它是否按预期崩掉或工作。在 `days/` 目录下的每个文档中，都设有【破坏性实验】环节。
4.  **记录笔记**：将你的理解画成图，或者写在代码注释里。

开始你的旅程吧！ -> [**Day 01: 全局概览与环境搭建**](days/Day_01_Overview_and_Setup.md)

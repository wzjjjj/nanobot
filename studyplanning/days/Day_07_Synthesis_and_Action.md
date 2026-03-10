# Day 07: 架构复盘与实战演练 (Synthesis & Action)

本阶段聚焦于 **“融会贯通”**，通过综合性的实战来检验对 nanobot 的掌握。

## 学习目标

1.  **架构复盘**：回顾全链路，能够从顶层到底层完整描述 nanobot 的工作原理。
2.  **实战开发**：实现一个包含新指令、新 Skill 或新 Tool 的完整功能。
3.  **设计思考**：能够评价 nanobot 的架构优缺点，并提出改进建议。

## 任务清单

### 1. 架构图重绘 (Redraw Architecture)

*   **动作**：
    *   在纸上或绘图工具中，凭记忆画出 nanobot 的架构图。
    *   包含：CLI/Gateway -> Bus -> Session -> Context -> Agent -> LLM -> Tools -> Memory。
    *   标注出关键的数据流（Inbound, Outbound, ToolCall, MemoryUpdate）。
*   **对比**：
    *   与 Day 01 画的草图对比，有什么变化？
    *   现在的图是否包含了更多细节（例如 Consolidation 触发点、Skill 注入点）？

### 2. 实战任务：天气预报机器人 (Weather Bot)

*   **目标**：创建一个能够查询天气的 Skill/Tool，并能通过 CLI 交互。
*   **步骤**：
    1.  **Tool**：创建一个简单的 Python Tool，调用公开的天气 API（或者 mock 数据）。
    2.  **Skill**：创建一个 `weather` Skill，包含 `SKILL.md`，告诉 Agent 何时使用这个 Tool，以及如何回答用户关于天气的问题。
    3.  **配置**：确保新 Tool 和 Skill 被加载。
    4.  **测试**：运行 `nanobot agent -m "北京今天天气怎么样？"`。
*   **挑战**：
    *   让 Agent 根据天气给出穿衣建议（这是 Skill 的 Prompt 逻辑）。
    *   让 Agent 记住用户的默认城市（这是 Memory 的逻辑）。

### 3. 深度思考：如果让你重构 (Refactor Thoughts)

*   **问题**：
    *   当前的 Bus 是基于内存的（`asyncio.Queue`），如果要支持分布式部署，你会怎么改？（提示：Redis, RabbitMQ）
    *   当前的 Memory 是基于文件的（`MEMORY.md`），如果用户量很大，会有什么问题？你会怎么优化？（提示：Vector DB, SQL）
    *   当前的 Agent 是单线程处理消息的吗？如何提高并发能力？

## 核心回顾

*   [LEARNING_ROADMAP.md](../LEARNING_ROADMAP.md): 总路线图。
*   [nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py): 核心。
*   [nanobot/bus/queue.py](file:///d:/编程学习记录/nanobot/nanobot/bus/queue.py): 通信。

## 验收标准

- [ ] 能够自信地向他人讲解 nanobot 的架构。
- [ ] 完成了天气预报机器人的实战任务。
- [ ] 能够针对架构提出至少 2 个合理的改进点。

---
[上一天：Day 06 异步总线与多渠道](Day_06_Bus_and_Channels.md) | [返回路线图](../LEARNING_ROADMAP.md)

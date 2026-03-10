# Day 04: 双层记忆系统 (Memory System)

本阶段聚焦于 **“Agent 如何记事”**，理解 nanobot 的长期记忆机制。

## 学习目标

1.  **记忆结构**：理解 `MEMORY.md` (长期事实) 与 `HISTORY.md` (完整日志) 的分工。
2.  **Consolidation 机制**：掌握系统如何自动压缩对话历史并提炼事实。
3.  **记忆注入**：理解 `ContextBuilder` 如何将记忆注入到 System Prompt 中。

## 任务清单

### 1. 记忆文件概览 (Memory Files)

*   **位置**：[workspace/memory/](../workspace/memory/)
*   **动作**：
    *   查看 `MEMORY.md`。它包含了哪些内容？（User Info, Preferences, Project Context）
    *   查看 `HISTORY.md`。它包含了哪些内容？（Timestamps, Roles, Content）
*   **思考**：
    *   这两个文件的区别是什么？
    *   为什么需要分两个文件？（提示：Token Limit vs Retrieval）

### 2. 记忆整理触发 (Trigger Consolidation)

*   **文件**：[nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py)
*   **动作**：
    *   找到 `_consolidate_memory` 方法。
    *   观察触发条件：`len(session.messages) > self.memory_window`。
    *   观察 `messages_to_process` 的计算。
*   **思考**：
    *   整理过程是否会阻塞主线程？（提示：`asyncio.create_task`）
    *   整理后的消息去哪了？（提示：`session.messages` 被截断，旧消息进文件）

### 3. LLM 整理逻辑 (LLM Consolidation)

*   **文件**：[nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py)
*   **动作**：
    *   找到 Prompt 定义：`You are a memory consolidation agent...`。
    *   观察 LLM 的输出格式（JSON: `history_entry`, `memory_update`）。
    *   观察 `memory.append_history` 和 `memory.write_long_term` 的调用。
*   **思考**：
    *   LLM 是如何区分“流水账”和“重要事实”的？
    *   如果 `memory_update` 为空，会发生什么？

### 4. 动手实验：触发整理 (Trigger Consolidation)

*   **动作**：
    1.  修改 `config.yaml`（或代码默认值），将 `memory_window` 设置为很小的值（例如 4）。
    2.  运行 `nanobot agent` 并连续对话 5 次。
    3.  观察日志中的 `Memory consolidation started`。
    4.  检查 `HISTORY.md` 和 `MEMORY.md` 是否有更新。
*   **观察**：
    *   `HISTORY.md` 中是否增加了刚才的对话摘要？
    *   `MEMORY.md` 中是否提取到了关键信息（例如如果你告诉它你的名字）？

## 核心代码索引

*   [nanobot/agent/memory.py](file:///d:/编程学习记录/nanobot/nanobot/agent/memory.py): MemoryStore 类。
*   [nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py): 记忆整理逻辑 `_consolidate_memory`。
*   [nanobot/skills/memory/SKILL.md](file:///d:/编程学习记录/nanobot/nanobot/skills/memory/SKILL.md): 记忆 Skill 定义。

## 验收标准

- [ ] 能解释双层记忆系统的设计意图。
- [ ] 能手动触发一次记忆整理。
- [ ] 能在 `MEMORY.md` 中看到提取出的事实。
- [ ] 能解释 ContextBuilder 是如何使用 `MEMORY.md` 的。

---
[上一天：Day 03 Agent 核心循环](Day_03_Agent_Loop.md) | [下一天：Day 05 工具与技能体系](Day_05_Tools_and_Skills.md)

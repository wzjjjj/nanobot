# Day 02: 消息流转机制 (Message Lifecycle)

本阶段聚焦于 **“消息是如何在系统内流动的”**。

## 学习目标

1.  **消息生命周期**：理解 `InboundMessage` -> `Session` -> `Context` -> `Agent` 的转换过程。
2.  **Session 管理**：掌握 `Session` 的创建、获取和持久化机制。
3.  **Context 构建**：理解 `ContextBuilder` 如何组装 System Prompt、History 和当前消息。

## 任务清单

### 1. 追踪消息入口 (Trace Inbound Message)

*   **文件**：[nanobot/cli/commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py)
*   **动作**：
    *   找到 `agent` 命令函数。
    *   区分两种路径：
        *   单条消息模式：运行 `nanobot agent -m "hi"`，代码会调用 `agent_loop.process_direct(message, session_id, ...)`；`InboundMessage(...)` 是在 `nanobot/agent/loop.py` 的 `process_direct` 里创建的。
        *   交互模式：运行 `nanobot agent`（不带 `-m`），代码会在 CLI 中直接 `bus.publish_inbound(InboundMessage(...))`，然后由 `AgentLoop.run()` 消费。
    *   在 `nanobot/agent/loop.py` 里找到 `process_direct`，确认 `msg = InboundMessage(...)` 的真实位置。
*   **思考**：如果是从 Telegram 进来的消息，会怎么处理？（提示：`nanobot/channels/telegram.py` -> `_on_message` -> `BaseChannel._handle_message` -> `bus.publish_inbound`）

### 2. 深入 Session 内部 (Dive into Session)

*   **文件**：[nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py)
*   **动作**：
    *   找到 `_process_message` 方法。
    *   找到 `key = session_key or msg.session_key`，以及紧随其后的 `session = self.sessions.get_or_create(key)`。
    *   跳转到 [nanobot/session/manager.py](file:///d:/编程学习记录/nanobot/nanobot/session/manager.py)。
    *   观察 `Session` 类的 `messages` 属性是如何存储历史消息的（JSONL 格式）。
*   **思考**：
    *   `session_key` 是什么格式？（提示：默认 `channel:chat_id`，也可能被 `session_key_override` 覆盖）
    *   为什么需要 `get_or_create`？
    *   历史消息是如何从文件加载到内存的？（提示：`_load` 方法）

### 3. 构建上下文 (Build Context)

*   **文件**：[nanobot/agent/context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py)
*   **动作**：
    *   找到 `ContextBuilder.build_messages` 方法。
    *   观察 System Prompt 是如何生成的（包含 workspace 信息、Memory、Skills）。
    *   观察 `history` 是如何被拼接进去的。
    *   观察 `current_message` 是如何与运行时信息合并后，作为单条 User 消息添加的（避免连续同 role 消息）。
*   **思考**：
    *   System Prompt 的内容是固定的吗？还是动态生成的？
    *   如果历史消息太长，会被截断吗？（提示：`session.get_history(max_messages=...)`）

### 4. 观察 Prompt 全貌 (Observe Full Prompt)

*   **破坏性实验**：在 `nanobot/agent/loop.py` 的 `_run_agent_loop` 方法开头，打印 `initial_messages`：
    ```python
    import json
    print(">>> PROMPT DUMP START <<<")
    print(json.dumps(initial_messages, indent=2, ensure_ascii=False))
    print(">>> PROMPT DUMP END <<<")
    ```
*   **动作**：运行 `nanobot agent -m "hi"`。
*   **观察**：控制台输出了什么？
    *   System Prompt 包含了哪些信息？
    *   History 包含了哪些消息？
    *   User 消息在哪里？

## 核心代码索引

*   [nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py): 核心消息处理逻辑 `_process_message`。
*   [nanobot/session/manager.py](file:///d:/编程学习记录/nanobot/nanobot/session/manager.py): Session 持久化管理。
*   [nanobot/agent/context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py): 上下文构建器。

## 验收标准

- [ ] 能画出从 CLI 输入到 Prompt 生成的时序图。
- [ ] 能解释 SessionKey 的作用。
- [ ] 能说出 System Prompt 中包含的关键信息（Memory, Skills, etc.）。
- [ ] 能看到完整的 Prompt 结构。

---
[上一天：Day 01 全局概览](Day_01_Overview_and_Setup.md) | [下一天：Day 03 Agent 核心循环](Day_03_Agent_Loop.md)

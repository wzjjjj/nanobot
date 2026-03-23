# Day 06: 异步总线与多渠道 (Bus & Channels)

本阶段聚焦于 **“消息高速公路”**，理解 nanobot 如何处理并发与跨平台，以及如何扩展新的通信渠道。

## 学习目标

1.  **MessageBus**：理解 `asyncio.Queue` 实现的生产者-消费者模型。
2.  **Channels**：掌握如何适配不同的聊天平台（如 Telegram, Discord, **Matrix [New!]**）。
3.  **异步编程**：理解 Python `asyncio` 在项目中的应用。

## 任务清单

### 1. 消息总线核心 (Message Bus Core)

*   **文件**：[nanobot/bus/queue.py](file:///d:/编程学习记录/nanobot/nanobot/bus/queue.py)
*   **动作**：
    *   查看 `MessageBus` 类。
    *   观察 `consume_inbound` 和 `publish_outbound` 方法。
    *   观察 `asyncio.Queue` 的使用（`get`, `put`）。
*   **思考**：
    *   为什么需要队列？为什么不能直接调用函数？（提示：解耦，缓冲，异步）
    *   如果 Agent 处理很慢，队列会积压吗？

### 2. Channel 适配层 (Channel Adapter)

*   **文件**：
    *   [nanobot/channels/base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py) (Base Class)
    *   [nanobot/channels/matrix.py](file:///d:/编程学习记录/nanobot/nanobot/channels/matrix.py) (**New!**)
*   **动作**：
    *   查看 `BaseChannel` 类，理解 `_on_message` (Inbound) 和 `send_message` (Outbound) 的契约。
    *   **对比阅读**：打开 `nanobot/channels/matrix.py`（或 `whatsapp.py`, `mochat.py`），看看它们是如何实现 `BaseChannel` 的。
    *   注意它们是如何处理特定平台的认证、连接和消息格式转换的。
*   **思考**：
    *   不同平台的 API 差异巨大，`BaseChannel` 如何抹平差异？
    *   新增一个 Channel 需要实现哪些最少的方法？

### 3. Channel 管理器 (Channel Manager)

*   **文件**：[nanobot/channels/manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py)
*   **动作**：
    *   查看 `ChannelManager` 类。
    *   观察如何加载配置并初始化各个 Channel。
    *   观察如何订阅 Bus 的 Outbound 消息并分发给对应的 Channel。
*   **思考**：
    *   如果配置了多个 Channel，它们是并行工作的吗？
    *   Agent 回复消息时，怎么知道发给哪个 Channel？（提示：`OutboundMessage.channel`）

### 4. 动手实验：模拟并发 (Simulate Concurrency)

*   **破坏性实验**：在 `nanobot/agent/loop.py` 的处理逻辑中增加 `await asyncio.sleep(5)`，模拟耗时操作。
*   **动作**：
    1.  启动 Gateway 模式（`nanobot gateway`，如果配置允许）。
    2.  快速发送 3 条消息。
    3.  观察日志：消息是顺序处理的还是并发处理的？
    4.  观察 Bus 的队列长度（如果在代码里加日志的话）。

## 核心代码索引

*   [nanobot/bus/queue.py](file:///d:/编程学习记录/nanobot/nanobot/bus/queue.py): 消息总线实现。
*   [nanobot/channels/base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py): Channel 基类。
*   [nanobot/channels/matrix.py](file:///d:/编程学习记录/nanobot/nanobot/channels/matrix.py): Matrix 协议实现示例。
*   [nanobot/channels/manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py): Channel 管理。

## 验收标准

- [ ] 能解释 MessageBus 的作用。
- [ ] 能画出 Channel -> Bus -> Agent -> Bus -> Channel 的数据流。
- [ ] 能解释 `InboundMessage` 和 `OutboundMessage` 的转换过程。
- [ ] 知道如何查阅新 Channel (如 Matrix) 的实现代码。

---
[上一天：Day 05 工具与技能体系](Day_05_Tools_and_Skills.md) | [下一天：Day 07 架构复盘与实战](Day_07_Synthesis_and_Action.md)

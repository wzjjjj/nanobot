# Module 04 · Lesson 01：异步总线与并发模型（Bus & Async）

## 学习目标

- 能解释 MessageBus 为什么用 `asyncio.Queue`，它解耦了哪些关系。
- 能理解 AgentLoop 的并发策略：主循环消费 inbound，但处理消息用 task 分发。
- 能理解 outbound dispatcher 的职责与退出条件（cancel）。

## 先修知识

- `asyncio.Queue`：`put` / `await get`。
- 事件循环中“一个常驻 while True 协程”的基本形态。

## 本节要回答的关键问题

- 为什么 inbound/outbound 要分两个队列？
- AgentLoop 为什么要 `asyncio.create_task(self._dispatch(msg))`，而不是直接 await？
- `/stop` 是如何及时生效的？它与并发模型有什么关系？
- ChannelManager 的 dispatcher 为什么用 `asyncio.wait_for(..., timeout=1.0)`？

## 核心概念

### 1) Producer-Consumer + 解耦边界

- Channels 是 inbound producer
- AgentLoop 是 inbound consumer + outbound producer
- ChannelManager 是 outbound consumer

MessageBus 把它们拆开，避免出现“平台代码依赖模型代码”的反向耦合。

## 代码走读路线

1. MessageBus：两个队列与四个方法
   - [queue.py](file:///d:/编程学习记录/nanobot/nanobot/bus/queue.py#L8-L35)
2. AgentLoop.run：消费 inbound 并分发 task
   - [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L259-L315)
3. /stop：取消 active tasks 与 subagents
   - [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L271-L315)
4. ChannelManager dispatcher：消费 outbound 并路由
   - [manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L208-L238)

## 关键代码讲解

### 1) MessageBus 的“最小实现”

MessageBus 没有引入复杂中间件，只有两个 `asyncio.Queue`：
- [queue.py](file:///d:/编程学习记录/nanobot/nanobot/bus/queue.py#L8-L19)

它的价值不是功能复杂，而是“边界清晰”：模块之间只通过消息交互。

### 2) AgentLoop 的“响应性”设计：task 分发

AgentLoop.run 的注释明确写了：为了保持对 `/stop` 的响应，需要把消息处理分发成 task：
- [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L259-L277)

效果是：

- 主循环能继续消费 inbound（尤其是 `/stop`）
- 重任务在后台执行，完成后通过 outbound 回传

### 3) dispatcher 的 timeout：避免永久阻塞

`asyncio.wait_for(..., timeout=1.0)` 常见于“可取消的常驻循环”：

- 超时就 continue，让协程能检查取消信号或其他状态
- 不会卡死在 `await queue.get()` 上

对应实现：
- AgentLoop inbound 消费：[loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L265-L270)
- ChannelManager outbound 消费：[manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L212-L236)

## 动手练习

### 练习 1：画出并发拓扑

请画出 3 个常驻协程/任务的关系：

- Channel.start()（每个平台至少一个）
- AgentLoop.run()
- ChannelManager._dispatch_outbound()

并标注它们各自 await 的队列方法。

### 练习 2：解释“为什么不用直接 await _dispatch(msg)”

请用一句话回答（重点提 `/stop` 的即时性）。

提示：对照 [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L271-L277) 的注释与实现。

## 验收清单

- [ ] 我能说清 inbound/outbound 两个队列的分工。
- [ ] 我能解释 AgentLoop 为什么要 task 分发，以及它如何提升响应性。
- [ ] 我能解释 dispatcher timeout 的意义。

## 下一课预告

下一课讲渠道层：BaseChannel 的抽象接口、allowFrom 门禁、以及 ChannelManager 如何启用/派发：
- [Module_04_Lesson_02_channels_design.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_04_Lesson_02_channels_design.md)


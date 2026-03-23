# Module 02 · Lesson 01：消息生命周期（Message Lifecycle）

## 学习目标

- 能从代码层面追踪一条消息的路径：Channel → Bus → AgentLoop → Bus → Channel。
- 能解释 `InboundMessage` / `OutboundMessage` 的字段与用途。
- 能指出“权限校验”发生在哪里、“解耦”发生在哪里、“派发”发生在哪里。

## 先修知识

- `asyncio.Queue` 的基本理解（put/await get）。
- “适配器模式”的直觉：把平台消息统一成内部格式。

## 本节要回答的关键问题

- 每个平台进来的消息，怎么被统一成同一种结构？
- 为什么要引入 MessageBus，而不是 Channel 直接调用 Agent？
- AgentLoop 消费 inbound 的并发模型是什么？为什么要 task 化？
- Outbound 是如何回到正确的平台/会话的？

## 核心概念

### 1) 统一消息模型（Inbound / Outbound）

通过统一的数据结构，channels 不需要知道 agent 细节，agent 也不需要知道平台差异。

- [events.py](file:///d:/编程学习记录/nanobot/nanobot/bus/events.py#L8-L37)

### 2) 消息总线（Bus）是“解耦点”

Bus 只做两件事：

- inbound 队列：channels → agent
- outbound 队列：agent → channels

- [queue.py](file:///d:/编程学习记录/nanobot/nanobot/bus/queue.py#L8-L35)

## 代码走读路线（按这条走，不迷路）

1. 先看统一消息结构
   - [events.py](file:///d:/编程学习记录/nanobot/nanobot/bus/events.py#L8-L37)
2. 再看 Channel 如何产生 `InboundMessage`
   - [base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py#L61-L112)
3. 再看 AgentLoop 如何消费 inbound 并发布 outbound
   - [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L259-L315)
4. 最后看 ChannelManager 如何派发 outbound 到具体平台
   - [manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L208-L238)

## 关键代码讲解

### 1) InboundMessage / session_key：会话隔离的核心

`InboundMessage.session_key` 默认等于 `"{channel}:{chat_id}"`，意味着不同平台、不同 chat 会自然隔离成不同 session。
- [events.py](file:///d:/编程学习记录/nanobot/nanobot/bus/events.py#L8-L25)

这就是为什么你经常会看到 session key 长得像 `telegram:123456`。

### 2) BaseChannel._handle_message：标准化与权限校验

Channel 的职责边界非常清晰：把平台消息转成内部 InboundMessage，并做 allowFrom 校验：
- 权限校验：[base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py#L61-L70)
- 标准化 + publish_inbound：[base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py#L71-L112)

你可以把它理解为“平台适配器 + 入站门禁”。

### 3) AgentLoop.run：消费 inbound 的主循环

AgentLoop 是常驻引擎，持续消费 inbound。它的设计点是：每条消息被包装成 task，从而保持对 `/stop` 的响应能力。
- [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L259-L315)

### 4) ChannelManager._dispatch_outbound：出站路由与过滤

出站派发点会做两类过滤：

- “进度消息 / tool hint”是否允许发送（由 config 控制）
- channel 是否存在

- [manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L208-L238)

## 动手练习

### 练习 1：把消息生命周期写成 8 行伪代码

请写出类似下面的伪代码（只写关键动作）：

1) Channel 收到平台消息  
2) allowFrom 校验  
3) 组装 InboundMessage  
4) bus.publish_inbound  
5) AgentLoop.consume_inbound  
6) 处理消息生成 OutboundMessage  
7) bus.publish_outbound  
8) ChannelManager.consume_outbound → channel.send  

### 练习 2：回答“门禁在哪里”

如果你要实现“只允许某个用户列表能对 bot 说话”，你应该改哪一层？

提示：从 [base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py#L61-L70) 开始找。

## 验收清单

- [ ] 我能指出 inbound/outbound 的数据结构定义文件。
- [ ] 我能指出 allowFrom 校验发生在哪里。
- [ ] 我能指出 outbound 派发发生在哪里。
- [ ] 我能用自己的话讲清“为什么 Bus 必须存在”。

## 下一课预告

下一课进入 AgentLoop 的“思考引擎”：LLM 是如何多轮调用工具并收敛到最终回复的：
- [Module_02_Lesson_02_agent_loop.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_02_Lesson_02_agent_loop.md)


# Module 04 · Lesson 02：渠道层设计（Channels）

## 学习目标

- 能解释 BaseChannel 抽象接口的三件事：start/stop/send。
- 能指出 allowFrom 门禁的默认策略，以及它为什么要“空列表拒绝所有”。
- 能解释 ChannelManager 的职责：按配置初始化渠道 + outbound 派发。

## 先修知识

- 抽象类与接口的直觉。
- 对“平台适配”有基本理解（Telegram/Discord/Email 各不相同）。

## 本节要回答的关键问题

- Channel 的职责边界在哪里结束？为什么不让 Channel 直接调用 Provider？
- allowFrom 的安全默认值是什么？在哪里强制检查？
- ChannelManager 如何决定启用哪些渠道？缺依赖时如何处理？
- OutboundMessage 如何回到正确的渠道实现？

## 核心概念

### 1) Channel 是“适配器”，不是“业务引擎”

Channel 只做平台相关的 IO：收消息、转成统一 InboundMessage、发送 OutboundMessage。核心逻辑留在 AgentLoop。

### 2) 安全默认：deny-by-default

allowFrom 空列表意味着“拒绝所有”，避免用户忘记配置导致机器人暴露在公网。

## 代码走读路线

1. BaseChannel 接口与入站处理
   - [base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py#L12-L112)
2. ChannelManager 初始化与 allowFrom 校验
   - [manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L16-L162)
3. Outbound 派发到具体 channel.send()
   - [manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L208-L238)

## 关键代码讲解

### 1) BaseChannel：统一接口

BaseChannel 规定了每个渠道必须实现：

- start：连接平台并持续监听
- stop：清理资源
- send：发送 OutboundMessage

对应抽象方法：
- [base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py#L34-L59)

### 2) allowFrom：门禁策略（两处）

第一处：BaseChannel.is_allowed（运行时校验）：
- [base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py#L61-L70)

第二处：ChannelManager._validate_allow_from（启动时强制）：
- [manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L155-L162)

这两处配合，使得“没配置 allowFrom 就启动”会直接退出，避免误配置带来的安全风险。

### 3) 入站标准化：`_handle_message(...)`

所有渠道最终都应该把平台消息转成 InboundMessage，并 publish 到 bus：
- [base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py#L71-L112)

### 4) 渠道初始化：按配置启用 + 依赖缺失容错

ChannelManager 按配置启用渠道，并用 try/except ImportError 处理“可选依赖缺失”的情况：
- [manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L34-L152)

这使得 nanobot 可以“按需安装 channel 依赖”，而不是强制装全家桶。

### 5) outbound 派发：路由到 channel.send

dispatcher 从 bus.consume_outbound 拿到 OutboundMessage，再根据 msg.channel 找到 channel 实例并调用 send：
- [manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L225-L233)

## 动手练习

### 练习 1：写一个新 Channel 的骨架（只写结构）

请你写出一个 `FooChannel(BaseChannel)` 的骨架（不需要可运行），包含：

- name = "foo"
- async def start/stop/send
- 在接收到平台消息时调用 `_handle_message(...)`

然后回答：你需要在哪个地方把它接入系统？

提示：看 [ChannelManager._init_channels](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L34-L152) 的模式。

### 练习 2：解释“为什么 allowFrom 空列表要拒绝所有”

用一句话回答（站在安全默认策略角度）。

## 验收清单

- [ ] 我能说清 BaseChannel 三个抽象方法的职责。
- [ ] 我能指出 allowFrom 门禁的两处实现点。
- [ ] 我能说清 outbound 派发如何路由到具体 channel.send。

## 下一课预告

下一课讲 Provider 抽象层：为什么要统一 chat() 接口、ProviderRegistry 的“单一真相”，以及 LiteLLMProvider 如何规整请求/响应：
- [Module_04_Lesson_03_provider_layer.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_04_Lesson_03_provider_layer.md)


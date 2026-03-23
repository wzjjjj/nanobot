# Module 01 · Lesson 01：项目目标与核心架构

## 学习目标

- 能用一句话解释 nanobot 的定位（多渠道接入 + 工具调用 + 可持久化记忆）。
- 能区分两种运行形态：CLI 直连 vs Gateway 常驻服务。
- 能画出 5 个核心模块及消息方向：Channels / Bus / AgentLoop / Tools / Session&Memory。

## 先修知识

- Python async/await 的基本概念（只需要理解“事件循环 + await”）。
- 读懂 dataclass/typing 的基本写法。

## 本节要回答的关键问题

- nanobot 要解决的核心问题是什么？“99% fewer lines” 的意义是什么？
- CLI 直连链路和 Gateway 链路分别长什么样？差别在哪里？
- MessageBus 在架构里承担了什么解耦作用？
- AgentLoop 的职责边界是什么？它为什么是“主干”？

## 核心概念

### 1) 两种运行形态

- CLI 直连：一次输入 → 一次 agent turn → 输出到终端。
- Gateway：多个渠道不断把消息推入系统，AgentLoop 持续消费并回发。

这不是“两个项目”，而是同一个核心引擎在两种接入方式下的不同运行容器。

### 2) 从外到内的分层

nanobot 的层次可以用一句话记住：**接入（Channels）→ 解耦（Bus）→ 智能（AgentLoop）→ 能力（Tools）→ 记忆（Session/Memory）**。

## 代码走读路线

1. 先读架构说明，建立“脑内地图”
   - [ARCHITECTURE.md](file:///d:/编程学习记录/nanobot/studyplanning/ARCHITECTURE.md#L1-L182)
2. 再看 README 的产品定位与 Quick Start，理解运行形态
   - [README.md](file:///d:/编程学习记录/nanobot/README.md#L15-L195)
3. 把架构落到“入口”：CLI 从哪里进？
   - [__main__.py](file:///d:/编程学习记录/nanobot/nanobot/__main__.py#L1-L8)
   - [commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py#L155-L560)

## 关键代码讲解

### 1) 入口：`python -m nanobot` 的最短路径

- `nanobot/__main__.py` 只有两件事：导入 CLI app 并执行。
  - [__main__.py](file:///d:/编程学习记录/nanobot/nanobot/__main__.py#L1-L8)

你可以把它理解成“总入口转发器”：真正的启动逻辑都在 CLI 命令里。

### 2) CLI / Gateway 与核心引擎的关系

在 CLI 命令里，`agent()` 和 `gateway()` 都会创建 `AgentLoop`，只是消息从哪里来、往哪里去不同：

- Gateway：创建 `MessageBus` + `ChannelManager`，并发运行 `agent.run()` 与 `channels.start_all()`。
  - [commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py#L291-L468)
- CLI：创建 `AgentLoop` 后，要么直接 `process_direct()`（单次消息），要么把交互输入转成 `InboundMessage` 丢进 bus。
  - [commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py#L478-L658)

关键结论：**AgentLoop 是核心引擎；CLI/Gateway 是不同的“接入容器”。**

## 动手练习

### 练习 1：画出你的架构草图（强制）

请你在纸上或白板画出下面这个层次（不要求画得漂亮，但要求方向正确）：

1) Channels（Telegram/Discord/...）  
2) MessageBus（inbound/outbound）  
3) AgentLoop（消费 inbound，发布 outbound）  
4) Tools（filesystem/web/shell/...）  
5) Session/Memory（会话 JSONL + MEMORY/HISTORY 文件）  

### 练习 2：定位“CLI 直连链路”的实际入口

打开并快速浏览：
- [commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py#L478-L560)

回答：`nanobot agent -m "hi"` 最终会调用哪个方法来处理消息？

提示：你会看到 `agent_loop.process_direct(...)`。

## 验收清单

- [ ] 我能复述 nanobot 的两种运行形态和差异。
- [ ] 我能画出 5 个核心模块及消息方向。
- [ ] 我能指出 CLI 的主要入口文件与命令函数位置。

## 下一课预告

下一课把“目录结构”映射成“职责分层”，并建立你读源码的导航习惯：
- [Module_01_Lesson_02_project_structure.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_01_Lesson_02_project_structure.md)


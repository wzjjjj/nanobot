# Module 01 · Lesson 02：目录结构与关键模块

## 学习目标

- 能把 `nanobot/` 顶级目录映射到架构分层（入口 / 通信 / 接入 / 智能 / 上下文 / 工具 / Provider / 记忆）。
- 能说清每个目录里“你应该先读哪个文件”，避免迷路式阅读。
- 能用 3–5 条“导航原则”在 IDE 里高效跳转。

## 先修知识

- 会用 IDE 的“跳转到定义 / 查找引用 / 全局搜索”。
- 知道 Python 包结构（`__init__.py`、模块导入）。

## 本节要回答的关键问题

- 为什么目录结构本身就是一种架构声明？
- `agent/` 与 `channels/` 的边界是什么？谁负责“业务流程”，谁负责“适配平台”？
- `bus/` 为什么单独成目录？它解决了什么耦合问题？
- `templates/` 与 `workspace` 有什么关系？

## 核心概念

### 1) “从外到内”比“从上到下”更重要

读框架类项目，如果从某个核心文件第一行读起，很容易陷入细节。更好的方式是：

1) 先建立模块边界（目录级）  
2) 再找关键链路（文件级）  
3) 最后才是实现细节（函数级）  

### 2) 一个可用的目录职责映射（建议背下来）

你可以用 `ARCHITECTURE.md` 的分层作为标准答案：
- [ARCHITECTURE.md](file:///d:/编程学习记录/nanobot/studyplanning/ARCHITECTURE.md#L10-L182)

## 代码走读路线

1. 把 README 的“Project Structure”当作目录总览
   - [README.md](file:///d:/编程学习记录/nanobot/README.md#L1169-L1188)
2. 对照 `ARCHITECTURE.md` 的“模块分层”，把目录和职责一一对齐
   - [ARCHITECTURE.md](file:///d:/编程学习记录/nanobot/studyplanning/ARCHITECTURE.md#L10-L153)
3. 在每个目录里只挑“最短路径文件”先读（下面给出清单）

## 关键模块速览（读源码最短路径）

### 入口层（CLI）

- [commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py)：你从这里进入系统

### 智能层（AgentLoop）

- [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py)：一条消息如何变成一次回复（LLM ↔ Tools 多轮）
- [context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py)：system prompt + history + memory + skills 如何拼装

### 通信层（Bus）

- [events.py](file:///d:/编程学习记录/nanobot/nanobot/bus/events.py)：统一的 Inbound/Outbound 数据结构
- [queue.py](file:///d:/编程学习记录/nanobot/nanobot/bus/queue.py)：解耦用的 asyncio.Queue

### 接入层（Channels）

- [base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py)：所有平台的统一接口
- [manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py)：按配置启用渠道 + outbound 派发

### 记忆与会话

- [manager.py](file:///d:/编程学习记录/nanobot/nanobot/session/manager.py)：会话 JSONL 存储与 get_history 对齐策略
- [memory.py](file:///d:/编程学习记录/nanobot/nanobot/agent/memory.py)：MEMORY.md/HISTORY.md 的读写与 consolidation

### 工具系统

- [base.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py)：Tool 抽象与参数校验
- [registry.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py)：注册与执行

### Provider 层

- [base.py](file:///d:/编程学习记录/nanobot/nanobot/providers/base.py)：统一 provider.chat() 接口
- [litellm_provider.py](file:///d:/编程学习记录/nanobot/nanobot/providers/litellm_provider.py)：LiteLLM 适配与响应解析
- [registry.py](file:///d:/编程学习记录/nanobot/nanobot/providers/registry.py)：ProviderSpec 注册表（单一真相）

## 动手练习

### 练习 1：给目录做“职责标签”

在你的笔记里写出下面映射（不用完全一致，但要有边界意识）：

- `cli/`：入口与运行容器
- `channels/`：平台适配（把平台消息转成统一 InboundMessage）
- `bus/`：解耦队列（inbound/outbound）
- `agent/`：主引擎（构建上下文、LLM 调用、工具循环、写会话）
- `providers/`：模型调用统一接口
- `session/`：会话历史存储与回放
- `config/`：配置加载与路径派生
- `templates/`：workspace 初始化模板（AGENTS/SOUL/TOOLS/USER 等）

### 练习 2：用“最短路径”回答两个问题

1) “消息是在哪一层被统一成 InboundMessage 的？”  
2) “回复是在哪一层被派发回具体平台的？”  

提示：前者看 [base.py](file:///d:/编程学习记录/nanobot/nanobot/channels/base.py#L71-L112)，后者看 [manager.py](file:///d:/编程学习记录/nanobot/nanobot/channels/manager.py#L208-L238)。

## 验收清单

- [ ] 我能用目录结构复述 nanobot 的分层架构。
- [ ] 我知道每层先读哪个文件（最短路径清单）。
- [ ] 我能回答“标准化在哪里发生”“派发在哪里发生”。

## 下一课预告

下一课从 CLI 入手走一遍“启动与配置加载”，你会第一次看到 AgentLoop 的构造参数来自哪里：
- [Module_01_Lesson_03_bootstrap_and_config.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_01_Lesson_03_bootstrap_and_config.md)


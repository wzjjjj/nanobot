# Module 03 · Lesson 02：双层记忆系统（Session + Memory）

## 学习目标

- 能区分 Session（JSONL 对话记录）与 Memory（MEMORY/HISTORY 文件）的职责。
- 能解释 consolidation（归并）发生的条件、输入、输出与副作用。
- 能说明为什么 Session 采用 append-only，以及 get_history 为什么要“对齐到 user turn”。

## 先修知识

- 基本文件读写（read_text / write_text / append）。
- 了解“上下文窗口有限”，需要压缩历史。

## 本节要回答的关键问题

- 为什么要同时存在 Session 和 Memory 两套存储？
- consolidation 的“输入”是什么？它怎么把对话变成 MEMORY/HISTORY？
- consolidation 成功后，Session 的哪些字段会变化？
- 为什么 get_history 要丢掉开头的非 user 消息？

## 核心概念

### 1) 两套存储解决两类问题

- Session：可追溯的完整对话历史（短期上下文的来源），按会话隔离保存。
- Memory：长期事实与可 grep 事件日志（进入 system prompt 的只有 MEMORY.md）。

### 2) consolidation = 把“旧对话”变成“可复用知识”

它不是删除历史，而是：

- 把旧消息摘要成一段 history_entry 写进 HISTORY.md（可检索）
- 把可持久化的事实合并进 MEMORY.md（会进入 system prompt）

## 代码走读路线

1. Session 数据结构与 get_history 策略
   - [session/manager.py](file:///d:/编程学习记录/nanobot/nanobot/session/manager.py#L16-L71)
2. MemoryStore：MEMORY/HISTORY 文件读写与 consolidate()
   - [agent/memory.py](file:///d:/编程学习记录/nanobot/nanobot/agent/memory.py#L45-L157)
3. AgentLoop 的触发点（/new 与窗口触发）
   - [agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L362-L409)

## 关键代码讲解

### 1) Session 是 append-only（重要但容易忽略）

Session 文档里写得很明确：消息 append-only 有利于 LLM cache 与可追溯性；consolidation 不会修改 messages 或 get_history 的输出，只会改变 last_consolidated 截断点。
- [Session](file:///d:/编程学习记录/nanobot/nanobot/session/manager.py#L16-L26)

### 2) get_history 为什么要“对齐到 user turn”

工具调用会形成一组结构：assistant(tool_calls) → tool(result) → assistant(...)。如果历史切片从中间开始（比如从 tool_result 开始），很多 provider 会拒绝或语义会断裂。nanobot 通过“丢掉开头的非 user 消息”避免这类上下文破碎：
- [get_history](file:///d:/编程学习记录/nanobot/nanobot/session/manager.py#L46-L64)

### 3) MemoryStore 的文件分工

MemoryStore 在 workspace/memory 下维护两个文件：

- MEMORY.md：长期事实（会进入 system prompt）
- HISTORY.md：事件日志（不进 prompt，但适合 grep）

- [MemoryStore.__init__](file:///d:/编程学习记录/nanobot/nanobot/agent/memory.py#L45-L52)

system prompt 注入的只有 long-term memory：
- [get_memory_context](file:///d:/编程学习记录/nanobot/nanobot/agent/memory.py#L65-L68)

### 4) consolidation 的实现方式：让模型调用 save_memory 工具

MemoryStore.consolidate 不是自己写摘要，而是构造一个 prompt，让 provider 必须调用一个虚拟工具 `save_memory`，把结果以结构化 arguments 交回来：
- tool schema：[agent/memory.py](file:///d:/编程学习记录/nanobot/nanobot/agent/memory.py#L18-L42)
- consolidate 主体：[agent/memory.py](file:///d:/编程学习记录/nanobot/nanobot/agent/memory.py#L69-L155)

### 5) /new 触发“归档并清空会话”

`/new` 的语义是：先 archive_all 归档当前 session，再清空 session 开启新会话：
- [agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L362-L392)

## 动手练习

### 练习 1：回答“长期事实”和“事件日志”分别存哪

写出两个文件名并解释它们的差异：

- MEMORY.md：进 system prompt
- HISTORY.md：不进 prompt，但可检索

提示：从 [MemoryStore](file:///d:/编程学习记录/nanobot/nanobot/agent/memory.py#L45-L68) 找证据。

### 练习 2：解释为什么 get_history 要从 user 开始

用一句话解释，并指出对应代码：
- [get_history](file:///d:/编程学习记录/nanobot/nanobot/session/manager.py#L46-L56)

## 验收清单

- [ ] 我能说清 Session 与 Memory 的分工。
- [ ] 我能解释 consolidation 的输入/输出与文件落点。
- [ ] 我能解释 get_history 的“对齐到 user turn”策略。

## 下一课预告

下一课讲 Skill 系统：workspace skills 如何覆盖 builtin skills、skills summary 如何生成、always skill 如何注入：
- [Module_03_Lesson_03_skill_system.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_03_Lesson_03_skill_system.md)


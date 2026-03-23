# Module 02 · Lesson 03：ContextBuilder（Prompt 拼装）

## 学习目标

- 能解释 system prompt 的组成：identity + bootstrap files + memory + active skills + skills summary。
- 能说明为什么要把 runtime context 和 user message 合并成同一个 user role（避免 provider 拒绝）。
- 能定位 skills 的 progressive loading 机制：summary 进 prompt，正文按需 read。

## 先修知识

- 了解 “system / user / assistant / tool” 这四类 role。
- 知道 prompt 上下文是有限的，需要控制“什么该进 system prompt”。

## 本节要回答的关键问题

- nanobot 的 system prompt 到底长什么样？从哪里拼出来？
- workspace 里的 `AGENTS.md / SOUL.md / USER.md / TOOLS.md` 为什么存在？
- Memory 为什么要分成 `MEMORY.md` 和 `HISTORY.md`？
- Skill 为什么不把所有 SKILL.md 全部塞进 system prompt？

## 核心概念

### 1) ContextBuilder = “输入管道”

AgentLoop 干的是“迭代与执行”，ContextBuilder 干的是“把可用信息变成模型输入”。

### 2) Progressive Loading（渐进加载）

Skill 的全文可能很长，全部塞进 system prompt 会挤占上下文。所以 nanobot 的策略是：

- system prompt 里只放 skills summary（名字、描述、路径、available）
- 需要用时，再按路径读取完整 SKILL.md（由 agent 触发）

## 代码走读路线

1. ContextBuilder：system prompt 拼装与 messages 构建
   - [context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L16-L146)
2. SkillsLoader：skills summary 生成与加载优先级
   - [skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L13-L141)
3. MemoryStore：memory context 注入方式
   - [memory.py](file:///d:/编程学习记录/nanobot/nanobot/agent/memory.py#L45-L68)

## 关键代码讲解

### 1) system prompt 的拼装顺序

`build_system_prompt()` 按顺序 append：

1) identity（运行环境、workspace 路径、平台策略）  
2) bootstrap 文件（AGENTS/SOUL/USER/TOOLS）  
3) long-term memory（MEMORY.md）  
4) always skills（always=true 的技能全文会被注入）  
5) skills summary（用于 progressive loading）  

对应源码：
- [context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L27-L54)

### 2) runtime context 的合并策略（非常关键）

某些 provider 会拒绝“连续两个 user role”的消息，所以 nanobot 把 runtime metadata 和用户输入合并到同一条 user message：
- [context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L121-L145)

这段设计背后的原则是：

- runtime metadata 是“非指令”信息（标注为 untrusted tag）
- 但它必须紧邻用户输入，方便模型使用（例如当前时间、channel/chat_id）

### 3) bootstrap 文件的意义：workspace 可塑性

bootstrap 文件来自 workspace（不是代码仓库的固定文件），这意味着：

- 你可以通过修改 workspace 文档改变 nanobot 的“人格/规则/工具说明”
- 这比改源码更轻量，更适合日常个性化

对应默认文件名：
- [context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L19-L20)

### 4) skills summary 的生成：让模型知道“有哪些技能可用”

SkillsLoader 会把 skills 列表生成一个 XML 风格 summary，包含 name/description/location/availability：
- [skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L101-L141)

注意优先级：workspace skills 会覆盖 builtin skills：
- [skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L38-L57)

## 学习笔记（结合本次问答）

### 1) skills summary 到底有什么用？

`skills_summary` 是一个“技能目录字符串”，会被拼进 system prompt，目的不是直接执行，而是让模型在不加载所有 SKILL.md 正文的情况下先“知道有哪些技能、在哪里、是否可用”，从而实现渐进加载：
- 注入位置： [context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L45-L53)
- 内容形态：XML 风格，包含 `<name>/<description>/<location>` 以及 `available="true/false"`：[skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L101-L141)
- 触发机制：模型读到 summary 后，会基于当前任务语义匹配 `<description>`，当判断某个 skill 有帮助时，再按 `<location>` 调用 `read_file` 读取 SKILL.md 全文（不是代码里硬编码 if/else 自动触发）。

### 2) skill 的 available 是如何判定的？

`available` 不是“模型觉得可用”，而是 nanobot 在生成 summary 时按技能元信息检查依赖：
- 判定函数：[_check_requirements](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L177-L187)
- 当前仅检查两类依赖：
  - `requires.bins`：用 `shutil.which` 判断某个 CLI 是否存在
  - `requires.env`：判断某个环境变量是否存在
- 如果不可用，会把缺失项写进 `<requires>`（例如缺 CLI、缺 ENV）：[_get_missing_requirements](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L142-L153)

### 3) runtime context 合并是什么意思？什么时候生成？

合并指的是：把“运行时元数据块”和“用户真实输入”合成一条 user 消息，避免部分 provider 拒绝连续两个 user role：
- 生成与合并位置：[build_messages](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L121-L145)
- runtime metadata 的内容：当前时间/时区 +（可选）channel/chat_id：[_build_runtime_context](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L99-L107)
- 生成时机：每次收到一条入站消息、准备调用 LLM 之前都会生成（由 AgentLoop 调用 `build_messages`）：[loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L419-L425)
- 历史不污染：保存 session 历史时会剥掉 runtime ctx 前缀，只保留用户文本；多模态也会过滤掉那段 text：[_save_turn](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L455-L485)

### 4) ContextBuilder 在 AgentLoop 里怎么用（一次请求的完整链路）

把一轮请求拆开看，ContextBuilder 主要承担“构建首包 + 迭代追加”两类职责：
- 初始化：`AgentLoop.__init__` 里创建 `self.context = ContextBuilder(workspace)`：[loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L49-L88)
- 首包构建：`build_messages` 生成 `[system] + history + [user]`：[loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L419-L425)
- 工具循环追加：
  - LLM 有 tool calls：`add_assistant_message` 追加 assistant（含 tool_calls），随后 `add_tool_result` 追加 tool 结果：[loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L203-L234)
  - LLM 无 tool calls：追加最终 assistant 文本并结束：[loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L235-L248)
- 工具 schema 的来源：每轮调用 LLM 时传入 `tools=self.tools.get_definitions()`，把当前注册的工具以 function-calling schema 暴露给模型：[loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L194-L201)

## 动手练习

### 练习 1：写出 system prompt 的组成清单

不看代码，写出 5 个组成部分，然后对照 [build_system_prompt](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L27-L54) 自查。

### 练习 2：回答“为什么要合并 runtime context 与 user message”

用一句话回答，并指出对应的代码位置：
- [build_messages](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L121-L145)

## 验收清单

- [ ] 我能说清 system prompt 的组成与顺序。
- [ ] 我能解释 runtime context 合并的兼容性原因。
- [ ] 我能解释 skills progressive loading 的动机与实现点。

## 下一课预告

下一模块进入“工具系统”：工具 schema、参数校验、执行与错误提示是如何设计的：
- [Module_03_Lesson_01_tools_and_registry.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_03_Lesson_01_tools_and_registry.md)

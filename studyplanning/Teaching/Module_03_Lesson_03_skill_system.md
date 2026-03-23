# Module 03 · Lesson 03：技能系统（Skill System）

## 学习目标

- 能解释 Skill 的“定义形态”（目录 + SKILL.md）与加载优先级（workspace > builtin）。
- 能说清 skills summary（progressive loading）的生成逻辑与字段。
- 能理解 always skill：为什么有些技能要强制注入到 system prompt。

## 先修知识

- Markdown + YAML frontmatter 的基本概念。
- 理解“把说明写成文档”也是一种工程手段（prompt-as-code）。

## 本节要回答的关键问题

- Skill 是怎么被发现的？在哪里扫描？
- workspace skills 为什么优先？它如何覆盖 builtin？
- “available=false” 是怎么判断的？缺依赖时发生什么？
- always skill 的用处是什么？为什么不能所有技能都 always？

## 核心概念

### 1) Skill = 给 Agent 的“操作手册”

nanobot 把很多能力提升的策略写成 SKILL.md，而不是硬编码进 Python。好处是：

- 易迭代：改文档即改策略
- 可组合：按需注入，避免污染 system prompt

### 2) Progressive Loading（summary 进 prompt，正文按需读）

skills summary 让模型知道“有哪些技能可用以及路径在哪里”，但不占用太多上下文。

## 代码走读路线

1. SkillsLoader（核心）
   - [skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L13-L227)
2. ContextBuilder 如何把 skills summary 注入 system prompt
   - [context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L39-L53)

## 关键代码讲解

### 1) 技能扫描与优先级：workspace 覆盖 builtin

SkillsLoader.list_skills 会先扫描 workspace 的 `workspace/skills/*/SKILL.md`，再扫描内置 skills（`nanobot/skills/*/SKILL.md`），并且避免同名重复：
- [list_skills](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L26-L57)

这就是“你可以在 workspace 里自定义/覆盖技能”的工程基础。

### 2) 技能摘要（skills summary）

build_skills_summary 会生成一个 XML 风格的 summary：

- name
- description（来自 frontmatter）
- location（SKILL.md 路径）
- available（requirements 是否满足）

- [build_skills_summary](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L101-L141)

ContextBuilder 会把 summary 放到 system prompt，并告诉模型“需要用技能就 read 这个文件”：
- [context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L45-L53)

### 3) 技能可用性判断（requirements）

SkillsLoader 会读取 skill 的 metadata（frontmatter 里的 metadata 字段），解析其中的 requires（bins/env），用于判断 available：
- metadata 读取：[skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L203-L227)
- requirements 检查：[skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L177-L187)

这使得“技能需要某个 CLI 工具/环境变量”这种约束可以写在文档里，而不是写死在代码里。

### 4) always skill：强制注入的技能

`get_always_skills()` 会选出 always=true 的技能，并将其全文注入 system prompt：
- [get_always_skills](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L193-L201)
- 注入点：[context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L39-L44)

实践建议：always 只放“全局原则/安全边界/通用工作流”，不要放大篇幅教程。

## 动手练习

### 练习 1：解释“为什么 workspace skill 优先”

用一句话回答，并指出对应代码位置：
- [list_skills](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L38-L53)

### 练习 2：找出 summary 里包含哪些字段

打开并浏览：
- [build_skills_summary](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py#L101-L141)

写下 summary 对每个 skill 输出了哪些标签。

## 验收清单

- [ ] 我能说清 skill 的目录结构与加载优先级。
- [ ] 我能解释 skills summary 的目的与内容。
- [ ] 我能解释 always skill 的用途与取舍标准。

## 下一课预告

下一模块进入基础设施：先看 MessageBus 的并发模型与 dispatcher，再看如何写一个新 Channel：
- [Module_04_Lesson_01_bus_and_async.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_04_Lesson_01_bus_and_async.md)


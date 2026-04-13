# Module 03 · Lesson 01：工具系统与注册表（Tools & Registry）

## 学习目标

- 能读懂 Tool 抽象的 3 个要素：name/description/parameters + execute。
- 能解释参数“cast → validate → execute”的流水线。
- 能定位工具调用失败时的返回策略（错误文本 + 引导提示）。

## 先修知识

- JSON Schema 的直觉：type/properties/required。
- Python 抽象类（ABC）与方法覆盖。

## 本节要回答的关键问题

- LLM 为什么能“知道”工具参数长什么样？schema 从哪来？
- 为什么要做 cast_params？它解决了什么调用兼容问题？
- 工具执行失败为什么不抛异常，而是返回字符串错误？
- ToolRegistry 的职责边界是什么？它负责“注册/执行/导出定义”，但不负责“工具逻辑”。

## 核心概念

### 1) Tool = “可声明的能力”

Tool 不只是一个函数，它还必须能自描述：

- 工具叫什么（name）
- 工具做什么（description）
- 参数是什么（parameters → JSON Schema）

对应接口：
- [tools/base.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L7-L53)

### 2) ToolRegistry = “工具运行时”

ToolRegistry 负责把一堆 Tool 管理起来，并提供两个关键能力：

- 导出工具定义列表（给 LLM）
- 按名字执行工具（给 AgentLoop）

- [tools/registry.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py#L8-L65)

## 代码走读路线

1. 先读 Tool 抽象与 schema 导出
   - [tools/base.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L7-L181)
2. 再读参数 cast / validate 的实现（理解“为什么兼容”）
   - [tools/base.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L55-L171)
3. 最后读 ToolRegistry.execute：流水线与错误返回风格
   - [tools/registry.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py#L38-L60)

## 关键代码讲解

### 1) schema 导出：`Tool.to_schema()`

`to_schema()` 把 Tool 变成 OpenAI function schema 形态，这就是 LLM 看到的工具定义：
- [to_schema](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L172-L181)

### 2) 参数 cast：降低“参数类型不一致”导致的失败

LLM 给的参数可能是字符串 `"1"`，但 schema 需要整数 `1`。Tool 先尝试按 schema 做安全 cast：
- [cast_params](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L55-L122)

### 3) 参数 validate：把“错误”变成可读提示

validate 不抛异常，而是返回 error list：
- [validate_params](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L124-L171)

### 4) 执行策略：失败返回字符串，而不是炸掉主循环

ToolRegistry.execute 的策略是：

- 工具不存在：返回错误文本（包含可用工具名）
- 参数不合法：返回错误文本 + 引导模型“换个思路”
- 工具执行异常：捕获异常并返回错误文本 + 引导提示

对应源码：
- [execute](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py#L38-L60)

这让 AgentLoop 可以“把错误当作上下文”喂回模型，从而触发自我纠错，而不是直接崩溃。

## 动手练习

### 练习 1：写一个最小 Tool（只写草图）

请你写出一个“echo”工具的骨架（不需要真的跑，只要你能写出 4 个部分）：

- name
- description
- parameters（包含一个 string 参数）
- execute（返回该 string）

然后对照 Tool 抽象接口检查你是否覆盖完整：
- [tools/base.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L7-L53)

### 练习 2：解释 cast 与 validate 的区别

用两句话回答：

- cast 做什么？
- validate 做什么？

提示：分别从 [cast_params](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L55-L62) 与 [validate_params](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L124-L132) 入手。

## 验收清单

- [ ] 我能说清 Tool 的 3 个自描述要素与 execute。
- [ ] 我能说清 cast 与 validate 的动机。
- [ ] 我能指出 ToolRegistry.execute 的错误返回策略。

## 学习疑问复盘（对话汇总）

下面是本节学习过程中出现过的高频疑问点，便于你复习时按问题回溯到代码定位与设计动机。

### 1) Tool 抽象与 schema

- Tool 为什么要用 `@property` 暴露 `name/description/parameters`，而不是 `@staticmethod` / `@classmethod`？
  - 目标是把 Tool 当作“可实例化能力对象”，由注册表持有实例并导出 schema，而不是仅仅一组函数集合。
  - 相关代码：Tool 抽象接口 [tools/base.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L7-L53)，schema 导出 [to_schema](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L172-L181)。
- LLM 为什么能“知道”工具参数长什么样？
  - 因为 AgentLoop 每轮调用模型时都会把 `tools=[tool.to_schema() ...]` 作为工具定义传给 provider，模型看到的是 JSON Schema。
  - 相关代码：导出定义 [ToolRegistry.get_definitions](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py#L34-L36)，传给模型 [AgentLoop._run_agent_loop](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L194-L206)。

### 2) 参数 cast/validate 的动机

- `cast_params` 是做什么的？为什么不直接 validate？
  - 解决“模型参数类型漂移”的兼容问题：例如 schema 要 `integer/number/boolean`，但模型可能给出字符串 `"1"` / `"true"`；先按 schema 做安全转换，再做严格校验。
  - 相关代码：cast 逻辑 [cast_params](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L55-L122)。
- validate 为什么返回 error list 而不是抛异常？
  - 让错误变成可读的上下文，喂回模型触发自我纠错；并且避免因为一次工具失败导致主循环崩溃。
  - 相关代码：validate 逻辑 [validate_params](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/base.py#L124-L171)，执行流水线 [ToolRegistry.execute](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py#L38-L59)。

### 3) 工具执行失败的返回策略

- 工具失败为什么经常返回字符串 `"Error: ..."`，甚至还会附带提示语？
  - ToolRegistry 会把错误统一包装成字符串返回，并加上引导模型“换个思路”的提示，降低同一错误反复重试造成的死循环概率。
  - 相关代码：[ToolRegistry.execute](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py#L38-L59)。

### 4) “模型是什么”与 tool_calls 的形态

- “模型”在这套系统里扮演什么角色？
  - 模型负责根据 messages + tools(schema) 决定输出文本还是输出 `tool_calls`；nanobot 负责执行工具并把结果回写到 messages。
  - 相关代码：模型调用入口 [AgentLoop._run_agent_loop](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L194-L206)。
- 大模型返回的 `tool_calls` 在 nanobot 内部是什么结构？
  - 各 provider 的原始返回格式不同，nanobot 会在 provider 层把它们统一成 `ToolCallRequest(id, name, arguments)`，供 AgentLoop 统一处理。
  - 相关代码：统一抽象 [ToolCallRequest](file:///d:/编程学习记录/nanobot/nanobot/providers/base.py#L8-L22)，执行与回写 [AgentLoop._run_agent_loop](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L207-L239)。

### 5) 工具如何被 Agent 调用（链路定位）

- 从“注册 → 选择 → 执行 → 回写”的关键链路在哪里？
  - 注册：`_register_default_tools()` 在构造 `AgentLoop` 时执行。
  - 选择：每轮 `provider.chat(..., tools=self.tools.get_definitions(), ...)` 把 schema 发给模型，由模型决定是否返回 `tool_calls`。
  - 执行：`result = await self.tools.execute(tool_call.name, tool_call.arguments)`。
  - 回写：`messages.append({"role": "tool", "tool_call_id": ..., "name": ..., "content": ...})`。
  - 相关代码：注册 [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L115-L132)，chat 与执行回写 [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L194-L239)，回写实现 [add_tool_result](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L169-L175)。

### 6) 工具循环（反复调用停不下来）如何止损

- nanobot 当前有哪些“停止/止损”机制？
  - iteration 上限：达到 `max_iterations` 会退出并返回固定提示。
  - 错误分支：当 `finish_reason == "error"` 会中断，避免错误内容污染历史导致永久 400 循环。
  - 相关代码：停止条件 [AgentLoop._run_agent_loop](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L240-L260)。
- 如果模型仍然反复发起相同工具调用，可以怎么改？
  - 在 agent loop 层做“重复调用检测”（例如窗口内同名同参重复超过阈值则提前 break，并把原因写回对话），属于工程侧兜底策略。

### 7) 实战坑：工具名/参数导致 provider 报错

- 为什么工具 `name` 用中文可能会触发 “invalid params” 之类的错误？
  - 一些 provider 对 function/tool name 的字符集与格式更严格（常见要求是 ASCII/字母数字/下划线等）。这类问题通常在“模型侧发起 tool call”阶段暴露为 API 参数校验失败。

## 下一课预告

下一课讲“记忆系统”：Session JSONL 与 MEMORY/HISTORY 文件如何配合，以及 consolidation 如何触发：
- [Module_03_Lesson_02_memory_system.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_03_Lesson_02_memory_system.md)

# Module 02 · Lesson 02：AgentLoop 迭代（LLM ↔ Tools）

## 学习目标

- 能解释 `_run_agent_loop()` 的循环逻辑：什么时候调用 LLM、什么时候执行工具、什么时候停止。
- 能说清 tool call 是如何被“追加到 messages”并回填 tool result 的。
- 能定位 3 个关键“收敛点”：finish_reason=stop/error、无 tool_calls、max_iterations。

## 先修知识

- 了解“ReAct”直觉：模型先想 → 需要外部信息就调用工具 → 把结果喂回模型 → 收敛到最终回答。
- 知道 `messages` 是一个“不断增长”的对话列表。

## 本节要回答的关键问题

- LLM 是如何“看到工具”的？工具 schema 从哪里来？
- tool_call 和 tool_result 的关联是如何保持一致的？
- 为什么要做 `_strip_think()`？它解决了什么兼容性问题？
- 为什么要限制 `max_iterations`？

## 核心概念

### 1) messages 是“状态机的状态”

AgentLoop 的迭代不是靠一堆全局变量，而是靠不断把新信息 append 到 `messages`：assistant 消息、tool result、再下一轮 LLM。

### 2) 工具调用协议（Function Calling）

模型返回 tool_calls → 系统把这些 tool_calls 作为 assistant 消息的一部分写入 messages → 执行工具 → 把 tool result 以 role=tool 写回 → 再调用 LLM。

## 代码走读路线

1. 读 `_run_agent_loop()` 的主循环（这是本节主角）
   - [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L180-L257)
2. 读 ContextBuilder 的“追加消息”方法（它决定 messages 怎么长大）
   - [context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L121-L193)
3. 读 ToolRegistry：工具 schema 如何导出，工具如何执行
   - [registry.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py#L8-L65)

## 关键代码讲解

### 1) 主循环：`_run_agent_loop()`

`_run_agent_loop()` 的核心结构可以总结为：

1) `provider.chat(messages, tools=tool_schemas, ...)`  
2) 如果 `response.has_tool_calls`：  
   - 把 tool_calls 写入 assistant 消息（append 到 messages）  
   - 逐个执行工具（`tools.execute(...)`）  
   - 把 tool result 写入 role=tool（append 到 messages）  
   - 回到 1) 继续  
3) 否则（没有 tool_calls）：把 assistant content 作为最终回答，break  

对应源码：
- [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L180-L257)

### 2) 工具 schema 从哪里来

每次调用模型时，都会把“当前注册的工具定义”传进去：

- `tools=self.tools.get_definitions()`
  - [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L194-L201)
- `get_definitions()` 来自 ToolRegistry，把每个 Tool 的 `to_schema()` 拼成 OpenAI function schema 列表
  - [registry.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py#L34-L37)

结论：**LLM 能调用哪些工具，取决于 ToolRegistry 当前注册了什么。**

### 3) tool_call 与 tool_result 的“绑定”

关键在于 tool_call_id：

- assistant 消息里会带 tool_calls（含 id）
- tool result 消息里会带 tool_call_id（必须匹配）

ContextBuilder 负责把 tool result 以标准格式 append：
- [add_tool_result](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L169-L175)

LiteLLMProvider 还专门做了“tool_call_id 归一化映射”，避免某些 provider 因为 id 太长或不一致而拒绝请求：
- [litellm_provider.py](file:///d:/编程学习记录/nanobot/nanobot/providers/litellm_provider.py#L180-L207)

### 4) “思考内容”清洗：`_strip_think()`

某些模型会在 content 里嵌入 `<think>...</think>`，但这些内容通常不希望出现在最终回复里，且可能污染后续上下文。nanobot 在关键路径做了剥离：
- [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L162-L168)

### 5) 收敛策略：finish_reason=error 与 max_iterations

当 provider 返回 error 时，nanobot 会避免把错误响应写入 session（防止“400 循环污染”）：
- [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L236-L247)

当工具循环超过 `max_iterations`，返回一个明确的“需要拆任务”的提示：
- [loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py#L250-L256)

## 本课总结（结合问答）

- AgentLoop 是一个“messages 驱动的状态机”：每轮把 assistant/tool 的新信息 append 到 messages，让下一次 LLM 调用看见最新状态。
- 主循环的 3 个状态：CALL_LLM（chat）→ EXECUTE_TOOLS（写入 tool_calls、执行工具、写回 tool 结果）→ FINAL_ANSWER（无 tool_calls 时产出最终回答并 break）。
- LLM 能“看到工具”不是魔法：每次 chat 都显式传 `tools=self.tools.get_definitions()`，而 `get_definitions()` 通过 `tool.to_schema()` 输出 OpenAI function schema（name/description/parameters）。
- 工具结果写回模型的写回点：`ContextBuilder.add_tool_result()` 把结果以 `role=tool` 追加到 messages，并带 `tool_call_id` 与 `assistant.tool_calls[].id` 对齐。
- `tool_call_id` 的作用：一次 assistant 回复可能包含多个 tool_calls；id 用于把每条 tool 结果精确绑定到对应的调用；provider 侧还会做 id 归一化但保持两端一致。
- L208 的 `on_progress(..., tool_hint=True)` 是“进度提示”：把将要调用的工具格式化成简短字符串输出，便于在 CLI/频道里观察执行过程，不影响核心逻辑。
- 为什么重开终端仍然有“之前的 messages”：交互模式默认 session key 常为 `cli:direct`，session 会落盘到 `workspace/sessions/*.jsonl`，启动后会被加载；用 `/new` 才会 clear 并开始新会话。
- 收敛策略的 3 个退出边：无 tool_calls（正常结束）、finish_reason=error（直接返回错误提示且不写入 session）、iteration 达到 max_iterations（提示拆任务）。

## 动手练习

### 练习 1：把 `_run_agent_loop()` 画成状态机

至少包含 3 个状态：

- CALL_LLM
- EXECUTE_TOOLS
- FINAL_ANSWER

并标出 3 条退出边：

- 无 tool_calls → FINAL_ANSWER
- finish_reason=error → FINAL_ANSWER（错误提示）
- iteration >= max_iterations → FINAL_ANSWER（需要拆分）

### 练习 2：回答“工具结果是怎么回到模型里的”

请你用一句话指出“写回点”在哪个函数：

提示：看 [add_tool_result](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py#L169-L175)。

## 验收清单

- [ ] 我能复述 `_run_agent_loop()` 的循环结构与停止条件。
- [ ] 我能说清 tool_calls 与 tool_result 如何绑定。
- [ ] 我能指出工具 schema 从 ToolRegistry 导出的位置。

## 下一课预告

下一课讲 ContextBuilder：system prompt 由哪些部分拼成、skills 为什么要 progressive loading、runtime context 为什么要和 user 合并：
- [Module_02_Lesson_03_context_building.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_02_Lesson_03_context_building.md)

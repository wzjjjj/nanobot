# Day 03: Agent 核心循环 (The Loop & ReAct)

本阶段聚焦于 **“大脑是如何运转的”**，理解 Agent 的决策循环（ReAct）。

## 学习目标

1.  **ReAct 模式**：理解 `Thought` -> `Action` -> `Observation` 的循环。
2.  **Tool Call 机制**：掌握 LLM 是如何决定调用工具的，以及工具结果是如何回填的。
3.  **Prompt 演化**：观察在多轮工具调用中，`messages` 列表的变化。

## 任务清单

### 1. 核心循环结构 (The While Loop)

*   **文件**：[nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py)
*   **动作**：
    *   找到 `_run_agent_loop` 方法。
    *   找到 `while iteration < self.max_iterations:` 循环。
    *   观察 `response = await self.provider.chat(...)` 的调用。
*   **思考**：
    *   `iteration` 是什么？为什么需要限制最大迭代次数？
    *   如果 `iteration` 超过限制，会发生什么？
    *   `messages` 列表在循环中是如何累积的？

### 2. 工具调用分支 (Tool Call Branch)

*   **文件**：[nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py)
*   **动作**：
    *   找到 `if response.has_tool_calls:` 分支。
    *   观察 `tool_calls` 是如何被提取的（`response.tool_calls`）。
    *   观察 Assistant 消息是如何被追加的（包含 `tool_calls`）。
    *   观察工具执行循环（`for tc in response.tool_calls:`）。
*   **思考**：
    *   工具参数是哪里来的？（提示：LLM 生成的 JSON）
    *   工具是如何被调用的？（提示：`self.tools.execute(tc.name, args)`）
    *   工具执行结果是如何回填的？（提示：`messages.append({"role": "tool", ...})`）

### 3. 工具执行与结果回填 (Execution & Result)

*   **文件**：[nanobot/agent/tools/registry.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py)
*   **动作**：
    *   找到 `ToolRegistry.execute` 方法。
    *   观察参数校验和执行逻辑。
    *   观察执行结果是如何被格式化为字符串的。
*   **思考**：
    *   如果工具执行报错，会发生什么？
    *   Agent 怎么知道工具执行失败了？（提示：结果字符串包含 Error）

### 4. 动手实验：追踪 Tool Call (Trace Tool Call)

*   **动作**：运行一个一定会触发工具的命令。
    ```bash
    nanobot agent -m "列出当前目录下的文件"
    ```
*   **观察**：
    *   观察日志中的 `Tool Call: list_dir`。
    *   观察日志中的 `Tool Result: ...`。
    *   观察最终回复。
*   **破坏性实验**：在 `nanobot/agent/loop.py` 的工具执行循环中，强行修改某个工具的返回结果：
    ```python
    result = "HACKED: Nothing here!"  # 覆盖真实结果
    ```
    再次运行命令，看看 Agent 会怎么回复。它应该会被你骗到，以为目录是空的。

## 核心代码索引

*   [nanobot/agent/loop.py](file:///d:/编程学习记录/nanobot/nanobot/agent/loop.py): 核心循环 `_run_agent_loop`。
*   [nanobot/agent/tools/registry.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py): 工具注册与执行。
*   [nanobot/providers/base.py](file:///d:/编程学习记录/nanobot/nanobot/providers/base.py): LLM 接口定义。

## 验收标准

- [ ] 能画出 ReAct 循环的流程图（Thought -> Action -> Observation）。
- [ ] 能解释为什么 LLM 需要看到工具的执行结果。
- [ ] 能解释 `tool_role` 消息的作用。
- [ ] 能成功欺骗 Agent（通过修改工具返回结果）。

---
[上一天：Day 02 消息流转机制](Day_02_Message_Lifecycle.md) | [下一天：Day 04 双层记忆系统](Day_04_Memory_System.md)

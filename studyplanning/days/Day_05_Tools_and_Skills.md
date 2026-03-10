# Day 05: 工具与技能体系 (Tools & Skills)

本阶段聚焦于 **“Agent 的手和脚”**，理解 nanobot 如何通过 Tool 和 Skill 扩展能力。

## 学习目标

1.  **ToolRegistry**：理解工具的发现、注册和元数据提取。
2.  **Skill System**：理解 Skill 的概念（Prompt + Docs + Files），以及如何动态加载 Skill。
3.  **Context Injection**：掌握 Skill 内容是如何注入到 System Prompt 中的。

## 任务清单

### 1. Tool 注册机制 (Tool Registry)

*   **文件**：[nanobot/agent/tools/registry.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py)
*   **动作**：
    *   观察 `register_tool` 装饰器。
    *   观察 `get_definitions` 方法（生成 OpenAI Tool Schema）。
    *   查看 `nanobot/agent/tools/` 下的具体工具实现（例如 `filesystem.py`, `web.py`）。
*   **思考**：
    *   工具的参数类型是如何被提取的？（提示：Type Hints）
    *   如果工具需要异步执行，怎么处理？

### 2. Skill 系统 (Skill System)

*   **文件**：[nanobot/agent/skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py)
*   **动作**：
    *   查看 `load_skills` 方法。
    *   观察 Skill 的目录结构（`SKILL.md` + 资源文件）。
    *   查看现有的 Skill（例如 `nanobot/skills/github/SKILL.md`）。
*   **思考**：
    *   Skill 与 Tool 的区别是什么？（提示：Skill 是知识/流程，Tool 是动作）
    *   Agent 如何知道有哪些 Skill 可用？

### 3. Skill 加载与 Context (Load Skill)

*   **文件**：[nanobot/agent/context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py)
*   **动作**：
    *   观察 `ContextBuilder` 如何读取 `skills/` 目录。
    *   观察 `SKILL.md` 的内容是如何被拼接到 System Prompt 中的。
*   **思考**：
    *   如果有太多 Skill，Context Window 会不会爆？
    *   是否有按需加载 Skill 的机制？（提示：目前可能是全量加载，或者基于关键词）

### 4. 动手实验：创建自定义 Skill (Create Custom Skill)

*   **动作**：
    1.  在 `workspace/skills/` 下创建一个新目录 `hello-skill`。
    2.  创建 `SKILL.md`，写入一些特定的指令（例如：“当你被问到‘你好’时，必须回答‘World’。”）。
    3.  重启 Agent（如果需要），运行 `nanobot agent -m "你好"`。
*   **观察**：
    *   Agent 是否遵循了新 Skill 的指令？
    *   在日志中能否看到 Skill 内容被注入到 Prompt 中？

## 核心代码索引

*   [nanobot/agent/tools/registry.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py): 工具注册中心。
*   [nanobot/agent/skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py): Skill 加载逻辑。
*   [nanobot/agent/context.py](file:///d:/编程学习记录/nanobot/nanobot/agent/context.py): 上下文注入。

## 验收标准

- [ ] 能解释 Tool 和 Skill 的本质区别。
- [ ] 能手动创建一个简单的 Skill 并使其生效。
- [ ] 能通过日志确认 Skill 内容被注入到了 Prompt 中。
- [ ] 能解释 Tool Schema 是如何生成的。

---
[上一天：Day 04 双层记忆系统](Day_04_Memory_System.md) | [下一天：Day 06 异步总线与多渠道](Day_06_Bus_and_Channels.md)

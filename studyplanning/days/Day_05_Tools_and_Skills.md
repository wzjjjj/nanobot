# Day 05: 工具与技能体系 (Tools & Skills)

本阶段聚焦于 **“Agent 的手和脚”**，理解 nanobot 如何通过 Tool、Skill 以及最新的 **MCP (Model Context Protocol)** 扩展能力。

## 学习目标

1.  **ToolRegistry**：理解原生 Python 工具的发现、注册和元数据提取。
2.  **MCP Integration**：**[New!]** 理解如何通过 MCP 协议集成外部工具，打破语言和进程边界。
3.  **Skill System**：**[New!]** 理解基于 Markdown 的 Skill 系统（Prompt + Docs），以及如何动态加载 Skill。
4.  **Context Injection**：掌握 Skill 内容是如何注入到 System Prompt 中的。

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

### 2. MCP 工具集成 (MCP Integration) [New!]

*   **文件**：[nanobot/agent/tools/mcp.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/mcp.py)
*   **概念**：MCP (Model Context Protocol) 是一个开放标准，允许 AI 模型安全地连接到本地或远程的数据和工具。
*   **动作**：
    *   阅读 `MCPToolWrapper` 类，理解它是如何将 MCP 工具包装成 nanobot 原生 Tool 的。
    *   阅读 `connect_mcp_servers` 函数，理解如何配置和连接 MCP 服务器（stdio 或 http/sse）。
    *   检查配置文件（如果有 `mcp_servers` 配置项），看看是如何定义的。
*   **思考**：
    *   MCP 工具与原生 Python 工具相比，有什么优势？（提示：跨语言、隔离性、标准化）
    *   `MCPToolWrapper` 是如何处理超时和错误的？

### 3. Skill 系统 (Skill System) [New!]

*   **文件**：
    *   [nanobot/agent/skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py) (Loader)
    *   [nanobot/skills/README.md](file:///d:/编程学习记录/nanobot/nanobot/skills/README.md) (Docs)
*   **动作**：
    *   查看 `SkillsLoader` 类，特别是 `list_skills` 和 `load_skill` 方法。
    *   观察 `nanobot/skills/` 目录下的结构。
    *   阅读一个具体的 Skill（例如 `nanobot/skills/github/SKILL.md`），注意它的 YAML frontmatter 和 Markdown 内容。
*   **思考**：
    *   Skill 与 Tool 的区别是什么？（提示：Skill 侧重于**“教”** Agent 怎么做，通常包含 Prompt 和流程；Tool 侧重于**“做”**，是具体的函数执行）
    *   `SKILL.md` 中的内容最终去了哪里？（提示：System Prompt）

### 4. 动手实验：创建自定义 Skill (Create Custom Skill)

*   **动作**：
    1.  在 `workspace/skills/` 下创建一个新目录 `hello-skill`。
    2.  创建 `SKILL.md`，必须包含 YAML 头信息：
        ```markdown
        ---
        name: hello-skill
        description: A simple greeting skill
        ---
        # Hello Skill
        当你被问到“你好”时，你必须热情地回答“Hello World from Skill System!”。
        ```
    3.  重启 Agent（如果需要加载新 Skill），运行 `nanobot agent -m "你好"`。
*   **观察**：
    *   Agent 是否遵循了新 Skill 的指令？
    *   在日志中能否看到 Skill 内容被注入到 Prompt 中？

## 核心代码索引

*   [nanobot/agent/tools/registry.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/registry.py): 工具注册中心。
*   [nanobot/agent/tools/mcp.py](file:///d:/编程学习记录/nanobot/nanobot/agent/tools/mcp.py): MCP 协议集成。
*   [nanobot/agent/skills.py](file:///d:/编程学习记录/nanobot/nanobot/agent/skills.py): Skill 加载逻辑。
*   [nanobot/skills/](file:///d:/编程学习记录/nanobot/nanobot/skills/): 内置 Skill 目录。

## 验收标准

- [ ] 能解释 Tool 和 Skill 的本质区别。
- [ ] 理解 MCP 是什么，以及 nanobot 如何通过 `MCPToolWrapper` 支持它。
- [ ] 能手动创建一个包含 YAML frontmatter 的 Skill 并使其生效。
- [ ] 能解释 Tool Schema 是如何生成的。

---
[上一天：Day 04 双层记忆系统](Day_04_Memory_System.md) | [下一天：Day 06 异步总线与多渠道](Day_06_Bus_and_Channels.md)

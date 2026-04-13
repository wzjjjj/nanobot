# Day 01: 全局概览与环境搭建

本阶段通过 **“环境搭建 -> CLI 初体验 -> 架构地图”** 的步骤，建立对项目的宏观认知。

## 学习目标

1.  **跑通环境**：能够成功运行 `nanobot` 并进行简单对话。
2.  **核心组件识别**：能够通过目录结构和日志，识别出项目的关键模块（Agent, Bus, Channels, Tools）。
3.  **消息流感性认知**：通过日志观察一次完整的交互流程，理解消息从输入到输出的大致路径。

## 任务清单

### 1. 环境准备 (Environment Setup)

*   **参考文档**：[studyplanning/PHASE_0_SETUP.md](../PHASE_0_SETUP.md)
*   **动作**：
    1.  安装 Python 依赖（推荐使用 `poetry` 或 `pip`）。
    2.  配置环境变量（如有需要）。
    3.  确认 `nanobot` 命令可用。

### 2. Hello World (CLI Interaction)

*   **动作**：运行以下命令，并观察输出。    
    ```bash
    nanobot agent -m "你好，介绍一下你自己"
    ```
*   **思考**：
    *   这个命令是从哪个文件入口进来的？（提示：`nanobot/cli/commands.py`）
    *   它是如何加载配置的？

### 3. 开启透视眼 (Enable Logs)

*   **动作**：使用 `--logs` 参数运行，观察控制台输出的详细日志。
    ```bash
    nanobot agent -m "今天天气怎么样" --logs
    ```
*   **观察点**：

    *   寻找 `Agent loop started`。
    *   寻找 `Processing message from cli:direct`。
    *   寻找 `Response to cli:direct`。
    *   注意日志中出现的模块名称（例如 `nanobot.agent.loop`, `nanobot.providers.base`）。

### 4. 绘制架构草图 (Draw Architecture Sketch)

*   **动作**：根据 `nanobot/` 目录下的子目录结构，尝试画出模块关系图。
    *   `agent/`: 核心大脑
    *   `bus/`: 消息高速公路
    *   `channels/`: 对外接口
    *   `tools/`: 手脚
    *   `memory/`: 记忆
    *   `templates/`: 初始化模板 (New!)
*   **验证**：对比文章中的架构描述，看你的理解是否一致。

## 破坏性实验 (Destructive Experiment)

*   **任务**：修改 `nanobot/cli/commands.py` 中的 `agent` 函数，在函数入口处添加一行打印：
    ```python
    print(">>> HACK: I am here inside the CLI command! <<<")
    ```
*   **预期**：再次运行命令，确认看到了这行输出。这证明你找到了正确的入口。

## 核心代码索引

*   [nanobot/cli/commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py): CLI 命令入口。
*   [nanobot/config/loader.py](file:///d:/编程学习记录/nanobot/nanobot/config/loader.py): 配置加载逻辑。
*   [nanobot/config/paths.py](file:///d:/编程学习记录/nanobot/nanobot/config/paths.py): 路径管理 (New!)。

## 验收标准

- [ ] 环境配置无误，命令可执行。
- [ ] 能在日志中定位到“请求开始”和“请求结束”的标志。
- [ ] 能说出至少 3 个核心模块的名称及其职责。

---
[返回路线图](../LEARNING_ROADMAP.md) | [下一天：Day 02 消息流转机制](Day_02_Message_Lifecycle.md)

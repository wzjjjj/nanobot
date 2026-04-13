# Module 01 · Lesson 03：启动流程与配置加载

## 学习目标

- 能从 `nanobot` 命令入口追到 `AgentLoop(...)` 被实例化的位置。
- 能说清配置文件路径如何确定（默认路径 vs `--config` 覆盖）。
- 能解释“多实例”为什么要把 runtime data dir 绑到 config 路径上。

## 先修知识

- 了解 CLI 参数解析的基本概念（这里用 Typer）。
- 知道 Path/文件路径的基本操作。

## 本节要回答的关键问题

- `nanobot agent` 与 `nanobot gateway` 启动流程分别是什么？
- `Config` 是怎么从 `config.json` 里加载出来的？默认在哪里？
- `--config` 发生了什么？它除了加载配置，还影响了哪些路径？
- Provider 是怎么选出来的？为什么有“direct provider”与 LiteLLM 两类？

## 核心概念

### 1) 入口不等于核心

CLI 入口是“运行容器”，核心引擎在 `AgentLoop`。读源码时先把“容器职责”和“引擎职责”拆开，避免把 CLI 代码误当核心。

### 2) 多实例 = “用 config 路径派生数据目录”

多实例支持的关键点：runtime data（cron/media/logs 等）不应该写到同一个全局目录，否则不同实例互相污染。nanobot 的实现策略是：**以 config 文件所在目录作为实例级 data dir**。

## 代码走读路线

1. 从模块入口看起：`python -m nanobot` → CLI app
   - [__main__.py](file:///d:/编程学习记录/nanobot/nanobot/__main__.py#L1-L8)
2. 追踪 CLI 命令：`gateway()` / `agent()`
   - [commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py#L291-L560)
3. 追踪配置加载与路径派生
   - [loader.py](file:///d:/编程学习记录/nanobot/nanobot/config/loader.py#L9-L48)
   - [paths.py](file:///d:/编程学习记录/nanobot/nanobot/config/paths.py#L11-L55)

## 关键代码讲解

### 1) CLI 总入口：Typer app

`commands.py` 通过 `typer.Typer(...)` 定义命令集合，`@app.command()` 标记子命令。
- [commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py#L36-L41)
- `gateway()`：[commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py#L291-L468)
- `agent()`：[commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py#L478-L658)

### 2) 配置加载：默认路径与覆盖

配置加载的入口是 `_load_runtime_config(...)`：
- [commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py#L267-L284)

它内部调用 `load_config(...)`，并在传入 `--config` 时调用 `set_config_path(...)`：
- [loader.py](file:///d:/编程学习记录/nanobot/nanobot/config/loader.py#L13-L48)

默认配置路径（未指定 `--config`）：
- [loader.py](file:///d:/编程学习记录/nanobot/nanobot/config/loader.py#L19-L24)

### 3) “多实例路径派生”的实现点

`get_data_dir()` 通过 `get_config_path().parent` 派生实例级目录：
- [paths.py](file:///d:/编程学习记录/nanobot/nanobot/config/paths.py#L11-L19)

它影响的内容包括但不限于：
- cron 存储目录：[paths.py](file:///d:/编程学习记录/nanobot/nanobot/config/paths.py#L27-L30)
- media 目录：[paths.py](file:///d:/编程学习记录/nanobot/nanobot/config/paths.py#L21-L25)

理解这点后，你会更容易读懂 README 里“Multiple Instances”的说明：不同实例只要 config 放不同目录，就天然隔离 runtime data。

### 4) Provider 的选择：direct vs LiteLLM

`_make_provider(config)` 决定具体 Provider 类型：
- [commands.py](file:///d:/编程学习记录/nanobot/nanobot/cli/commands.py#L214-L265)

你可以先记住三个分支：

- `custom`：OpenAI-compatible endpoint，直接调用（绕过 LiteLLM）
- `azure_openai` / `openai_codex`：也是 direct/OAuth 路径
- 其他：走 `LiteLLMProvider`（统一接入多家模型）

## 动手练习

### 练习 1：画出启动链路（CLI 与 Gateway 各 1 条）

请用箭头写出两条链路（只到“AgentLoop 创建”为止）：

- CLI：`__main__` → `commands.agent()` → `_load_runtime_config()` → `_make_provider()` → `AgentLoop(...)`
- Gateway：`__main__` → `commands.gateway()` → `_load_runtime_config()` → `_make_provider()` → `AgentLoop(...)` → `ChannelManager(...)`

### 练习 2：定位 “workspace 是哪来的”

在 `gateway()` 和 `agent()` 里都能看到：

- `config = _load_runtime_config(config, workspace)`
- `sync_workspace_templates(config.workspace_path)`

请你追一下 `workspace_path` 是哪里来的、什么时候确保目录存在。

提示：先从 [paths.py](file:///d:/编程学习记录/nanobot/nanobot/config/paths.py#L37-L41) 看 `get_workspace_path()`，再回到 Config 的字段含义。

## 验收清单

- [ ] 我能从 CLI 命令定位到 AgentLoop 的创建代码位置。
- [ ] 我能解释默认 config 路径、`--config` 覆盖与多实例 data dir 之间的关系。
- [ ] 我能说清 provider 选择为什么有 direct 与 LiteLLM 两条路。

## 下一课预告

下一模块将进入“核心链路”：从 Channel 收到消息，到 AgentLoop 输出回复：
- [Module_02_Lesson_01_message_lifecycle.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/Module_02_Lesson_01_message_lifecycle.md)


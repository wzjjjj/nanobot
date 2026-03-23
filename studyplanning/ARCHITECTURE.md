# nanobot 总体架构描述

## 1. 系统目标与运行形态

nanobot 是一个“多渠道接入 + 工具调用 + 可持久化记忆”的轻量 AI 助手框架，核心运行形态只有两类：

- 直连模式（CLI）：用户输入直接进入 AgentLoop，输出打印到终端
- 网关模式（Gateway）：常驻服务，多个 Channel 将消息汇入，再由 AgentLoop 统一处理并回发

## 2. 模块分层（从外到内）
·
### 2.1 入口层（CLI）

- 负责解析命令、加载配置、实例化核心组件并启动
- 主要入口：
  - `nanobot agent`：单次或交互式对话
  - `nanobot gateway`：启动 Channel + AgentLoop + 定时/心跳服务

代码位置：
- `nanobot/cli/commands.py`
- `nanobot/__main__.py`
- `pyproject.toml`（console_scripts）

### 2.2 通信层（MessageBus）

MessageBus 是“接入层（channels）”与“智能层（agent）”之间的解耦点。

- inbound queue：channels → agent
- outbound queue：agent → channels

收益：
- agent 不关心 telegram/slack 等平台差异
- channels 不关心 LLM、工具调用、上下文拼装

代码位置：
- `nanobot/bus/events.py`
- `nanobot/bus/queue.py`

### 2.3 接入层（Channels + ChannelManager）

- 每个 Channel 负责把平台消息转成统一的 `InboundMessage`，再推入 `MessageBus.inbound`
- `ChannelManager` 负责：
  - 根据配置启用/初始化哪些 channel
  - 监听 `MessageBus.outbound` 并把消息路由到对应 channel 的 `send()`

代码位置：
- `nanobot/channels/base.py`
- `nanobot/channels/manager.py`
- `nanobot/channels/*.py`

### 2.4 智能层（AgentLoop：核心引擎）

AgentLoop 是项目的“主干”，其职责是把一次输入完整变成一次输出：

1. 读取/创建 session，决定是否触发记忆归并
2. 构建上下文（system prompt + history + memory + skills + media）
3. 调用 LLM Provider 得到回复或工具调用
4. 执行工具调用，将工具结果喂回 LLM（多轮迭代）
5. 把最终回复写回 session 并发布 outbound（网关模式）

代码位置：
- `nanobot/agent/loop.py`

### 2.5 上下文层（ContextBuilder：Prompt 拼装）

ContextBuilder 负责把“工作区 bootstrap 文件 + memory + skills + 近期对话历史”拼成 system prompt，并把当前用户输入（可含图片）包装成 LLM 消息。

关键点：
- bootstrap 文件来自 workspace（默认 `~/.nanobot/workspace`）
- long-term memory 会进入 system prompt（`MEMORY.md`）
- skills 采用 progressive loading：system prompt 里只提供摘要与路径，需要时再读完整 SKILL.md

代码位置：
- `nanobot/agent/context.py`
- `nanobot/agent/skills.py`
- `nanobot/agent/memory.py`

### 2.6 工具层（Tools：函数调用能力）

工具系统由三部分构成：

- `Tool` 抽象：定义 name/description/parameters/execute，并提供轻量参数校验
- `ToolRegistry`：注册、导出 tool schemas、执行工具
- 具体工具实现：filesystem、shell、web、message、spawn、cron 等

AgentLoop 会在启动时注册默认工具集合，并把 tool schemas 传入 LLM，使其可以发起 tool calls。

代码位置：
- `nanobot/agent/tools/base.py`
- `nanobot/agent/tools/registry.py`
- `nanobot/agent/tools/*.py`

### 2.7 Provider 层（LLMProvider：统一模型调用）

Provider 的目标是屏蔽不同模型/网关的差异，让 AgentLoop 始终以统一接口 `provider.chat()` 使用模型。

项目当前主实现是 `LiteLLMProvider`：
- 负责组装 LiteLLM 参数（model、tools、temperature 等）
- 解析 tool_calls 与 reasoning_content
- 根据 registry 做 model 前缀、gateway 检测与参数 override

代码位置：
- `nanobot/providers/litellm_provider.py`
- `nanobot/providers/registry.py`

### 2.8 会话与记忆（Session + Memory）

两套存储解决两类需求：

- Session（JSONL）：保存完整对话历史，用于短期上下文与可追溯性（默认在 `~/.nanobot/sessions`）
- Memory（workspace 文件）：
  - `memory/MEMORY.md`：长期事实，会进入 system prompt
  - `memory/HISTORY.md`：事件日志，不进入 prompt，依赖 grep 检索

当 session 过长时，AgentLoop 会触发“记忆归并”：
- 把旧消息压缩成一段 history_entry（写入 HISTORY.md）
- 把可持久化事实合并到 MEMORY.md

代码位置：
- `nanobot/session/manager.py`
- `nanobot/agent/memory.py`
- `nanobot/agent/loop.py`（`_consolidate_memory`）

### 2.9 任务调度与守护（Cron + Heartbeat）

- Cron：管理 jobs，按 `at/every/cron` 触发回调，回调通常是“把任务作为一次 agent turn 执行”
- Heartbeat：周期性唤醒 agent，读取 workspace 的 `HEARTBEAT.md` 并执行其中指令（或返回无事可做的 token）

代码位置：
- `nanobot/cron/service.py`
- `nanobot/heartbeat/service.py`

### 2.10 子代理（Subagent：后台任务）

SubagentManager 用于把“较长任务”拆出去后台跑：
- 子代理拥有独立上下文与工具集合（没有 message、spawn 等能力）
- 结果通过 bus 以 system message 形式回注到主循环，由主循环再向用户输出

代码位置：
- `nanobot/agent/subagent.py`

### 2.11 WhatsApp Bridge（Node 子系统）

WhatsApp 由于生态限制需要通过 Node bridge 接入：
- Node 端跑 WhatsApp Web 客户端
- Python 端通过 WebSocket 与 bridge 通信
- bridge 默认只绑定 localhost，可选 token 鉴权

代码位置：
- `bridge/src/index.ts`
- `bridge/src/server.ts`
- `bridge/src/whatsapp.ts`

## 3. 两条关键执行链路（建议背下来）

### 3.1 CLI 直连链路

`nanobot agent` → 构造 AgentLoop → `process_direct()` → `_process_message()` →
`ContextBuilder.build_messages()` → `_run_agent_loop()`（LLM↔Tools 迭代）→
写 session → 输出到终端

### 3.2 Gateway 多渠道链路

Channel 收消息 → `bus.publish_inbound()` →
`AgentLoop.run()` 消费 inbound → 处理得到 `OutboundMessage` →
`bus.publish_outbound()` → `ChannelManager._dispatch_outbound()` → channel.send 回平台

## 4. 扩展点（做二次开发最常碰到的地方）

- 新增工具：实现 `Tool` 并在 AgentLoop 注册
- 新增渠道：实现 `BaseChannel`，在 `ChannelManager` 按配置启用
- 新增 Provider：在 provider registry 增加 spec，并在 config schema 添加字段
- 新增 Skill：新增 `skills/<name>/SKILL.md`（内置或 workspace skills）

## 5. 你应该从哪些文件开始读（最短路径）

- 入口与启动：`nanobot/cli/commands.py`
- 核心引擎：`nanobot/agent/loop.py`
- Prompt 拼装：`nanobot/agent/context.py`
- 工具系统：`nanobot/agent/tools/*`
- Provider：`nanobot/providers/litellm_provider.py`、`nanobot/providers/registry.py`
- 会话与记忆：`nanobot/session/manager.py`、`nanobot/agent/memory.py`


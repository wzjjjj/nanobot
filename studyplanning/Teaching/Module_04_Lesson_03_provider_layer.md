# Module 04 · Lesson 03：Provider 抽象层（LLM Providers）

## 学习目标

- 能解释为什么需要 LLMProvider 抽象：让 AgentLoop 面向统一接口编程。
- 能理解 ProviderRegistry 的设计意图：provider 元数据的“单一真相”。
- 能读懂 LiteLLMProvider.chat 的关键步骤：sanitize → kwargs → acompletion → parse_response。

## 先修知识

- 理解“适配层”的价值：把不同厂商的差异屏蔽掉。
- 对 OpenAI-style chat completion 的 messages/tools 概念有直觉。

## 本节要回答的关键问题

- AgentLoop 调用模型的统一入口是什么？参数有哪些？
- ProviderRegistry 如何根据 model/provider/api_base/api_key 决定“走哪家”？
- LiteLLMProvider 为什么要做 messages 清洗？它解决了哪些 400 错误？
- tool_call_id 为什么要归一化？

## 核心概念

### 1) 统一接口：`provider.chat(...)`

AgentLoop 只关心：

- messages
- tools（可选）
- model/temperature/max_tokens

不关心“具体是哪家模型后端”。

对应接口定义：
- [providers/base.py](file:///d:/编程学习记录/nanobot/nanobot/providers/base.py#L32-L127)

### 2) 注册表驱动（Registry-Driven）

ProviderRegistry 把“如何识别 provider、如何前缀模型名、需要哪些 env”等规则集中管理，避免 scattered if/else。

- [providers/registry.py](file:///d:/编程学习记录/nanobot/nanobot/providers/registry.py#L1-L115)

## 代码走读路线

1. LLMProvider 抽象与 LLMResponse 结构
   - [providers/base.py](file:///d:/编程学习记录/nanobot/nanobot/providers/base.py#L8-L127)
2. ProviderRegistry：ProviderSpec 的字段含义与顺序优先级
   - [providers/registry.py](file:///d:/编程学习记录/nanobot/nanobot/providers/registry.py#L19-L115)
3. LiteLLMProvider.chat：请求规整与响应解析
   - [litellm_provider.py](file:///d:/编程学习记录/nanobot/nanobot/providers/litellm_provider.py#L209-L337)

## 关键代码讲解

### 1) 统一返回结构：LLMResponse

LLMResponse 把不同 provider 的返回规整成：

- content（文本）
- tool_calls（函数调用请求列表）
- finish_reason
- usage / reasoning_content / thinking_blocks（可选）

- [providers/base.py](file:///d:/编程学习记录/nanobot/nanobot/providers/base.py#L16-L30)

这就是为什么 AgentLoop 可以用同一套逻辑处理“普通回答”和“工具调用”。

### 2) ProviderRegistry：为什么“顺序很重要”

registry 注释明确写了：order matters，gateway 要优先，因为它们能路由任意模型（fallback 更合理）。
- [providers/registry.py](file:///d:/编程学习记录/nanobot/nanobot/providers/registry.py#L1-L11)

并且 ProviderSpec 字段里区分了：

- is_gateway / is_local / is_oauth / is_direct
- detect_by_key_prefix / detect_by_base_keyword（用于根据 key/base 推断）
- litellm_prefix / skip_prefixes（用于模型名前缀规整）

你读懂这些字段后，“为什么 model 会被自动变成 openrouter/xxx”就不神秘了。

### 3) LiteLLMProvider.chat 的关键步骤

LiteLLMProvider.chat 的结构很稳定：

1) resolve model（可能加前缀）  
2) sanitize messages（去掉非标准字段、处理空 content）  
3) 组装 kwargs（model/messages/max_tokens/temperature/tools/...）  
4) 调用 `acompletion(**kwargs)`  
5) parse_response（把 LiteLLM response 转成 LLMResponse）  

对应代码：
- [litellm_provider.py](file:///d:/编程学习记录/nanobot/nanobot/providers/litellm_provider.py#L209-L337)

### 4) 为什么要 sanitize empty content

provider 经常会拒绝：

- 空字符串 content
- list content 中空的 text block

nanobot 在 base provider 层提供了通用清洗：
- [providers/base.py](file:///d:/编程学习记录/nanobot/nanobot/providers/base.py#L45-L89)

这属于“可靠性工程”：把不稳定输入规范化，减少 400 回路。

### 5) tool_call_id 归一化：解决严格 provider 的链路一致性

一些 provider 对 tool_call_id 的长度/格式/一致性很敏感。LiteLLMProvider 会映射/缩短 id，并保证 assistant.tool_calls[].id 与 tool.tool_call_id 对得上：
- [litellm_provider.py](file:///d:/编程学习记录/nanobot/nanobot/providers/litellm_provider.py#L180-L207)

## 动手练习

### 练习 1：用 6 行话总结 LiteLLMProvider.chat

要求包含：resolve model、sanitize、kwargs、tools、acompletion、parse。

### 练习 2：回答“我新增一个 Provider 要改哪里”

请写出两步（只写文件名与动作）：

提示：看 [providers/registry.py](file:///d:/编程学习记录/nanobot/nanobot/providers/registry.py#L1-L7) 顶部注释。

## 验收清单

- [ ] 我能说清 LLMProvider 抽象的价值与 chat() 的角色。
- [ ] 我能解释 ProviderRegistry 的单一真相与顺序优先级。
- [ ] 我能指出 LiteLLMProvider.chat 的 5 个关键步骤。

## 课程复盘入口

回到教学索引，选择下一条你想深挖的链路（比如 Cron、Heartbeat、Subagent）：
- [README.md](file:///d:/编程学习记录/nanobot/studyplanning/Teaching/README.md)


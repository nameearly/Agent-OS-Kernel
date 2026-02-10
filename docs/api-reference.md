# API Reference

## Core Classes

### AgentOSKernel

主内核类，管理所有 Agent 生命周期。

```python
from agent_os_kernel import AgentOSKernel

kernel = AgentOSKernel(config=None)
```

#### Methods

| Method | Description |
|--------|-------------|
| `spawn_agent(name, task, priority)` | 创建 Agent |
| `run(max_iterations)` | 运行内核 |
| `stop()` | 停止内核 |
| `get_agent(pid)` | 获取 Agent |
| `list_agents()` | 列出所有 Agent |
| `print_status()` | 打印状态 |

---

### ContextManager

虚拟内存式上下文管理。

```python
from agent_os_kernel import ContextManager

cm = ContextManager(max_context_tokens=128000)
```

#### Methods

| Method | Description |
|--------|-------------|
| `allocate_page(agent_pid, content, importance)` | 分配页面 |
| `access_page(page_id)` | 访问页面 |
| `get_agent_context(agent_pid)` | 获取上下文 |
| `swap_out(agent_pid)` | 换出 |
| `swap_in(agent_pid)` | 换入 |

---

### StorageManager

PostgreSQL 五重角色存储。

```python
from agent_os_kernel import StorageManager

storage = StorageManager.from_postgresql(url)
```

#### Methods

| Method | Description |
|--------|-------------|
| `save_conversation(agent_pid, messages)` | 保存对话 |
| `create_checkpoint(agent_pid)` | 创建检查点 |
| `semantic_search(query, limit)` | 向量搜索 |
| `acquire_lock(name)` | 获取锁 |
| `log_action(...)` | 记录操作 |

---

### AgentScheduler

进程调度器。

```python
from agent_os_kernel import AgentScheduler

scheduler = AgentScheduler()
```

#### Methods

| Method | Description |
|--------|-------------|
| `add_process(agent)` | 添加进程 |
| `remove_process(pid)` | 移除进程 |
| `schedule()` | 调度 |
| `get_stats()` | 获取统计 |

---

## LLM Module

### LLMProviderFactory

LLM Provider 工厂。

```python
from agent_os_kernel.llm import LLMProviderFactory, LLMConfig

factory = LLMProviderFactory()
provider = factory.create(LLMConfig(
    provider="deepseek",
    model="deepseek-chat"
))
```

### Supported Providers

| Provider | Models |
|----------|--------|
| `openai` | gpt-4o, gpt-4-turbo |
| `deepseek` | deepseek-chat, deepseek-reasoner |
| `kimi` | moonshot-v1-8k, moonshot-v1-32k |
| `qwen` | qwen-turbo, qwen-plus, qwen-max |
| `anthropic` | claude-3-opus, claude-3-sonnet |

---

## Communication Module

### AgentMessenger

Agent 消息系统。

```python
from agent_os_kernel.agents.communication import (
    AgentMessenger, Message, MessageType
)

messenger = AgentMessenger()
await messenger.register_agent("agent-1", "Alice")
```

### KnowledgeSharing

知识共享系统。

```python
from agent_os_kernel.agents.communication import KnowledgeSharing

knowledge = KnowledgeSharing()
```

### GroupChatManager

群聊管理。

```python
from agent_os_kernel.agents.communication import GroupChatManager

chat = GroupChatManager()
chat_id = chat.create_chat("讨论主题")
```

---

## Exceptions

| Exception | Description |
|-----------|-------------|
| `AgentError` | Agent 基础异常 |
| `ContextError` | 上下文异常 |
| `StorageError` | 存储异常 |
| `SecurityError` | 安全异常 |
| `SchedulerError` | 调度异常 |

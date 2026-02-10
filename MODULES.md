# Agent OS Kernel Modules

## Core Modules

| Module | File | Description |
|--------|------|-------------|
| **kernel.py** | `agent_os_kernel/kernel.py` | 主内核 |
| **context_manager.py** | `agent_os_kernel/core/context_manager.py` | 虚拟内存式上下文 |
| **scheduler.py** | `agent_os_kernel/core/scheduler.py` | 进程调度 |
| **storage.py** | `agent_os_kernel/core/storage.py` | 持久化存储 |
| **security.py** | `agent_os_kernel/core/security.py` | 安全子系统 |
| **metrics.py** | `agent_os_kernel/core/metrics.py` | 性能指标 |
| **events.py** | `agent_os_kernel/core/events.py` | 事件系统 |
| **state.py** | `agent_os_kernel/core/state.py` | 状态管理 |
| **exceptions.py** | `agent_os_kernel/core/exceptions.py` | 异常定义 |

## LLM Modules

| Module | File | Description |
|--------|------|-------------|
| **provider.py** | `agent_os_kernel/llm/provider.py` | Provider 抽象 |
| **factory.py** | `agent_os_kernel/llm/factory.py` | 工厂模式 |
| **openai.py** | `agent_os_kernel/llm/openai.py` | OpenAI |
| **anthropic.py** | `agent_os_kernel/llm/anthropic.py` | Anthropic |
| **deepseek.py** | `agent_os_kernel/llm/deepseek.py` | DeepSeek |
| **kimi.py** | `agent_os_kernel/llm/kimi.py` | Kimi |
| **minimax.py** | `agent_os_kernel/llm/minimax.py` | MiniMax |
| **qwen.py** | `agent_os_kernel/llm/qwen.py` | Qwen |
| **ollama.py** | `agent_os_kernel/llm/ollama.py` | Ollama |
| **vllm.py** | `agent_os_kernel/llm/vllm.py` | vLLM |

## Tool Modules

| Module | File | Description |
|--------|------|-------------|
| **registry.py** | `agent_os_kernel/tools/registry.py` | 工具注册表 |
| **base.py** | `agent_os_kernel/tools/base.py` | 工具基类 |
| **mcp/client.py** | `agent_os_kernel/tools/mcp/client.py` | MCP 客户端 |
| **mcp/registry.py** | `agent_os_kernel/tools/mcp/registry.py` | MCP 注册表 |

## Communication Modules

| Module | File | Description |
|--------|------|-------------|
| **messenger.py** | `agent_os_kernel/agents/communication/messenger.py` | 消息传递 |
| **knowledge_share.py** | `agent_os_kernel/agents/communication/knowledge_share.py` | 知识共享 |
| **group_chat.py** | `agent_os_kernel/agents/communication/group_chat.py` | 群聊 |
| **collaboration.py** | `agent_os_kernel/agents/communication/collaboration.py` | 协作 |

## Statistics

| Category | Count |
|----------|-------|
| Core Modules | 9 |
| LLM Modules | 10 |
| Tool Modules | 4 |
| Communication Modules | 4 |
| **Total** | **27** |

## Dependencies

```yaml
# Core
psutil>=5.9.0      # 系统监控
pyyaml>=6.0        # 配置
requests>=2.31.0   # HTTP

# Optional
openai>=1.0.0      # OpenAI Provider
anthropic>=0.3.0   # Anthropic Provider
redis>=4.5.0       # 缓存
redis>=4.5.0       # Redis
postgresql         # PostgreSQL
```

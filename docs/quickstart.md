# 快速开始指南

## 安装

```bash
# 基本安装
pip install agent-os-kernel

# 安装依赖
pip install -e ".[dev]"
```

## 快速示例

### 1. 最简单的 Agent

```python
from agent_os_kernel import AgentOSKernel

# 创建内核
kernel = AgentOSKernel()

# 创建 Agent
agent_pid = kernel.spawn_agent(
    name="Assistant",
    task="帮助用户解决问题",
    priority=50
)

# 运行
kernel.run(max_iterations=10)
```

### 2. 使用 Mock Provider (无需 API Key)

```python
from agent_os_kernel.llm import LLMProviderFactory

factory = LLMProviderFactory()

# 使用 Mock Provider 进行测试
provider = factory.create_mock()

# 测试聊天
result = provider.chat([
    {"role": "user", "content": "Hello!"}
])
print(result["content"])
```

### 3. 使用 OpenAI Provider

```python
from agent_os_kernel.llm import LLMProviderFactory, LLMConfig

factory = LLMProviderFactory()

# 创建 OpenAI Provider
provider = factory.create(LLMConfig(
    provider="openai",
    model="gpt-4o",
    api_key="your-api-key"
))

# 发送消息
result = provider.chat([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the weather?"}
])

print(result["content"])
```

### 4. 使用上下文管理

```python
from agent_os_kernel import ContextManager

# 创建上下文管理器
cm = ContextManager(max_context_tokens=128000)

# 分配页面
page_id = cm.allocate_page(
    agent_pid="agent-1",
    content="大量上下文内容...",
    importance=0.8
)

# 获取优化后的上下文
context = cm.get_agent_context(agent_pid="agent-1")
```

### 5. 使用存储

```python
from agent_os_kernel import StorageManager

# 创建存储
storage = StorageManager.from_postgresql(
    "postgresql://user:pass@localhost/agent_os",
    enable_vector=True
)

# 保存对话
storage.save_conversation(agent_id, messages)

# 语义搜索
results = storage.semantic_search(
    query="用户之前提到的需求",
    limit=5
)
```

### 6. 使用事件系统

```python
from agent_os_kernel import EventBus, EventType

# 创建事件总线
event_bus = EventBus()

# 订阅事件
event_bus.subscribe(
    handler_id="logger",
    callback=lambda e: print(e),
    event_types=[EventType.AGENT_CREATED]
)
```

## 运行示例

```bash
# 运行基本示例
python -m agent_os_kernel --demo basic

# 运行通信示例
python -m agent_os_kernel --demo messaging

# 运行工作流示例
python -m agent_os_kernel --demo workflow
```

## API 服务器

```bash
# 启动 API 服务器
uvicorn agent_os_kernel.api.server:AgentOSKernelAPI --host 0.0.0.0 --port 8000
```

### API 端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | /health | 健康检查 |
| POST | /api/v1/agents | 创建 Agent |
| GET | /api/v1/agents | 列出 Agent |
| GET | /api/v1/agents/{id} | 获取 Agent |
| DELETE | /api/v1/agents/{id} | 删除 Agent |
| GET | /api/v1/metrics | 获取指标 |
| GET | /api/v1/metrics/prometheus | Prometheus 格式 |

## Docker 部署

```bash
# 构建镜像
docker build -t agent-os-kernel .

# 运行
docker run -p 8000:8000 agent-os-kernel
```

## 下一步

- [架构设计](architecture.md)
- [API 参考](api-reference.md)
- [最佳实践](best-practices.md)
- [示例代码](../examples/)

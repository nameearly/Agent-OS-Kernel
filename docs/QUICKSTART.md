# Agent-OS-Kernel 快速入门指南

## 安装

```bash
# 克隆项目
git clone https://github.com/bit-cook/Agent-OS-Kernel.git
cd Agent-OS-Kernel

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 1. 初始化内核

```python
from agent_os_kernel import AgentOSKernel

kernel = AgentOSKernel()
print(f"Kernel version: {kernel.version}")
```

### 2. 配置

```yaml
# config.yaml
app:
  name: Agent-OS-Kernel
  debug: true

llm:
  default_provider: openai
  providers:
    openai:
      model: gpt-4
      api_key: ${OPENAI_API_KEY}
```

```python
from agent_os_kernel.core.config_manager import ConfigManager

config = ConfigManager("config.yaml")
```

### 3. 使用Agent

```python
from agent_os_kernel import AgentOSKernel

kernel = AgentOSKernel()

# 创建Agent
agent = await kernel.create_agent(
    name="Assistant",
    system_prompt="You are a helpful assistant."
)

# 运行对话
response = await agent.run("Hello!")
print(response)
```

### 4. 使用Agent池

```python
from agent_os_kernel.core.agent_pool import AgentPool

pool = AgentPool(max_size=10)

# 获取Agent
agent = await pool.get_agent("worker-1")
```

### 5. 事件系统

```python
from agent_os_kernel.core.event_bus import EventBus

bus = EventBus()

# 订阅事件
@bus.on("agent.created")
async def on_agent_created(event):
    print(f"Agent created: {event.data['agent_id']}")

# 发布事件
await bus.publish("test.event", {"key": "value"})
```

### 6. 熔断器

```python
from agent_os_kernel.core.circuit_breaker import CircuitBreaker

cb = CircuitBreaker(
    failure_threshold=5,
    timeout_seconds=30
)

result = await cb.call(risky_function)
```

### 7. 上下文管理

```python
from agent_os_kernel.core.context_manager import ContextManager

ctx = ContextManager(max_tokens=128000)

# 管理对话上下文
await ctx.add_message("user", "Hello!")
```

## 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_agent_pool.py -v

# 生成覆盖率报告
pytest --cov=agent_os_kernel tests/
```

## 运行示例

```bash
# 基本示例
python examples/basic/comprehensive_demo.py

# Agent示例
python examples/basic/agent_pool_demo.py
```

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| app.debug | 调试模式 | false |
| llm.default_provider | 默认LLM提供商 | openai |
| agents.pool_size | Agent池大小 | 10 |
| database.url | 数据库连接串 | - |

## 常见问题

### Q: 如何添加新的LLM提供商?

```python
from agent_os_kernel.llm.base_provider import BaseLLMProvider

class MyProvider(BaseLLMProvider):
    async def complete(self, prompt: str) -> str:
        # 实现逻辑
        return "response"
```

### Q: 如何扩展事件系统?

```python
# 自定义事件类型
from agent_os_kernel.core.events import Event, EventType

class CustomEvent(Event):
    type = EventType.CUSTOM
```

## 下一步

- [API文档](API.md)
- [部署指南](DEPLOYMENT.md)
- [性能基准](PERFORMANCE.md)

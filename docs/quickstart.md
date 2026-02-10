# 快速入门指南

## 安装

### 基础安装

```bash
pip install agent-os-kernel
```

### 完整安装

```bash
pip install agent-os-kernel[all]
```

### 从源码安装

```bash
git clone https://github.com/bit-cook/Agent-OS-Kernel.git
cd Agent-OS-Kernel
pip install -e .
```

---

## 快速开始

### 1. 基础使用

```python
from agent_os_kernel import AgentOSKernel

# 创建内核
kernel = AgentOSKernel()

# 创建 Agent
agent_pid = kernel.spawn_agent(
    name="MyAgent",
    task="帮我完成一个任务",
    priority=50
)

# 运行
kernel.run(max_iterations=10)

# 查看状态
kernel.print_status()
```

### 2. 使用中国模型

```python
from agent_os_kernel.llm import LLMProviderFactory, LLMConfig

# 创建 DeepSeek Provider
factory = LLMProviderFactory()
provider = factory.create(LLMConfig(
    provider="deepseek",
    model="deepseek-chat",
    api_key="your-api-key"
))
```

### 3. 上下文压缩

```python
from agent_os_kernel.core.optimization import ContextCompressor, CompressionStrategy

compressor = ContextCompressor()

# 压缩消息
compressed = compressor.compress_messages(
    messages,
    strategy=CompressionStrategy.HYBRID
)
```

---

## 配置

### 配置文件

```yaml
# config.yaml
api_keys:
  deepseek: "${DEEPSEEK_API_KEY}"
  kimi: "${KIMI_API_KEY}"

llms:
  models:
    - name: "deepseek-chat"
      provider: "deepseek"
    - name: "moonshot-v1-32k"
      provider: "kimi"

default_model: "deepseek-chat"
```

### 环境变量

```bash
export DEEPSEEK_API_KEY="your-key"
export KIMI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

---

## 核心概念

### Agent

Agent 是任务执行的基本单元：

```python
# 创建 Agent
agent_pid = kernel.spawn_agent(
    name="Assistant",
    task="任务描述",
    priority=50,  # 优先级 (1-100)
    timeout=300   # 超时时间 (秒)
)

# 终止 Agent
kernel.terminate(agent_pid)
```

### 调度器

调度器管理 Agent 的执行：

```python
from agent_os_kernel import AgentScheduler

scheduler = AgentScheduler()

# 添加任务
scheduler.add_task(agent_pid, priority=50)

# 获取状态
status = scheduler.get_status()
```

### 工具

工具扩展 Agent 的能力：

```python
from agent_os_kernel.tools import ToolRegistry

registry = ToolRegistry()

# 注册工具
registry.register(MyTool())

# 列出工具
tools = registry.list_tools()
```

---

## 高级功能

### 多 Agent 协调

```python
from agent_os_kernel.agents import WorkflowAgent

# 创建工作流
workflow = WorkflowAgent(
    name="DataPipeline",
    steps=[
        {"name": "数据收集", "task": "从 API 收集数据"},
        {"name": "数据清洗", "task": "清洗数据"},
        {"name": "数据分析", "task": "分析结果"}
    ]
)

# 执行
result = await workflow.run()
```

### 分布式部署

```python
from agent_os_kernel.distributed import DistributedScheduler

scheduler = DistributedScheduler(
    node_id="scheduler-1",
    host="localhost",
    port=8001
)

# 注册节点
await scheduler.register_node(
    node_id="worker-1",
    hostname="gpu-server",
    port=8002
)

# 提交任务
await scheduler.submit_task(
    task_id="task-1",
    agent_config={"name": "DistributedAgent"}
)
```

### 监控

```python
from agent_os_kernel.resources import SystemMonitor

monitor = SystemMonitor()

# 采集指标
metrics = await monitor.collect_metrics()

# 获取告警
alerts = monitor.get_alerts(unresolved=True)

# 导出数据
export = monitor.export_metrics(3600)
```

---

## 示例

### 基本示例

```bash
python examples/basic_usage.py
```

### Agent 示例

```bash
python examples/agent_spawning.py
```

### 优化示例

```bash
python examples/optimization_demo.py
```

### 分布式示例

```bash
python examples/distributed_demo.py
```

---

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_kernel.py -v

# 运行类型检查
mypy agent_os_kernel/
```

---

## Docker 部署

```bash
# 构建镜像
docker build -t agent-os-kernel .

# 运行容器
docker run -p 8000:8000 agent-os-kernel

# 使用 docker-compose
docker-compose up -d
```

---

## 故障排除

### 问题：API Key 未设置

```bash
# 检查环境变量
echo $DEEPSEEK_API_KEY

# 设置环境变量
export DEEPSEEK_API_KEY="your-key"
```

### 问题：内存不足

```python
# 使用上下文压缩
from agent_os_kernel.core.optimization import compress_context

compressed = compress_context(messages, max_tokens=4000)
```

### 问题：Agent 无响应

```python
# 设置超时
kernel.spawn_agent(
    name="Agent",
    task="Task",
    timeout=60  # 60秒超时
)
```

---

## 进一步阅读

- [架构设计](architecture.md)
- [API 参考](api-reference.md)
- [最佳实践](best-practices.md)
- [分布式部署](distributed-deployment.md)

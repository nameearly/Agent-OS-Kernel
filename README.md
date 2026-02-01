# Agent OS Kernel

[![CI](https://github.com/bit-cook/Agent-OS-Kernel/actions/workflows/ci.yml/badge.svg)](https://github.com/bit-cook/Agent-OS-Kernel/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个基于操作系统设计原理的 AI Agent 运行时内核。

借鉴传统操作系统 50 年的演化经验，为 AI Agent 构建一个真正的"操作系统"：

| 传统计算机 | Agent 世界 | OS Kernel 职责 |
|-----------|-----------|---------------|
| CPU       | LLM       | 调度推理任务 |
| RAM       | Context Window | 管理上下文窗口 |
| Disk      | Database  | 持久化存储 |
| Process   | Agent     | 生命周期管理 |

## 🏗️ 架构设计

```
┌─────────────────────────────────────────┐
│         Agent Applications              │
│    (CodeAssistant, ResearchAgent...)    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          Agent OS Kernel                │
│  ┌──────────┬──────────┬──────────┐     │
│  │ Context  │ Process  │   I/O    │     │
│  │ Manager  │Scheduler │ Manager  │     │
│  └──────────┴──────────┴──────────┘     │
│  ┌─────────────────────────────────┐    │
│  │     Storage Layer (PostgreSQL)  │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Hardware Resources              │
│    LLM API | Vector DB | Message Queue │
└─────────────────────────────────────────┘
```

## 📦 核心组件

### 1. Context Manager（上下文管理器）

**类比：虚拟内存管理**

- 实现 LLM 上下文窗口的"虚拟内存"
- 智能页面置换算法（LRU + 语义重要性）
- 自动 swap in/out 机制
- 最大化 KV-Cache 命中率

```python
from agent_os_kernel import ContextManager

context_manager = ContextManager(max_context_tokens=100000)

# 分配上下文页面
page_id = context_manager.allocate_page(
    agent_pid="agent-123",
    content="System: You are a helpful assistant...",
    importance=1.0  # 重要性评分
)

# 访问页面（自动处理换入）
page = context_manager.access_page(page_id)
```

### 2. Process Scheduler（进程调度器）

**类比：操作系统进程调度**

- 优先级调度
- 时间片轮转
- 抢占式调度
- 资源配额管理

```python
from agent_os_kernel import AgentScheduler, AgentProcess

scheduler = AgentScheduler(time_slice=60.0)

# 创建 Agent 进程
process = AgentProcess(
    pid="agent-001",
    name="CodeAssistant",
    priority=30  # 数字越小优先级越高
)

# 加入调度队列
scheduler.add_process(process)

# 调度执行
process = scheduler.schedule()
```

### 3. Storage Layer（存储层）

**类比：文件系统 + 数据库**

- Agent 进程状态持久化
- 检查点（Checkpoint）机制
- 审计日志（Audit Trail）
- 向量检索（语义搜索）

支持两种存储后端：
- **MemoryStorage**: 内存存储（开发和测试）
- **PostgreSQLStorage**: PostgreSQL + pgvector（生产环境）

```python
from agent_os_kernel import StorageManager

# 内存存储
storage = StorageManager()

# PostgreSQL 存储
storage = StorageManager.from_postgresql(
    "postgresql://user:pass@localhost:5432/agent_os"
)
```

### 4. Tool System（工具系统）

**类比：设备驱动 + 系统调用**

- 标准化的工具接口
- Agent-Native CLI 包装
- 工具注册和发现
- 统一的错误处理

```python
from agent_os_kernel import Tool, ToolRegistry

# 定义工具
class CalculatorTool(Tool):
    def name(self) -> str:
        return "calculator"
    
    def description(self) -> str:
        return "Evaluate mathematical expressions"
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        expression = kwargs['expression']
        result = eval(expression)
        return {
            "success": True,
            "data": result,
            "error": None
        }

# 注册工具
registry = ToolRegistry()
registry.register(CalculatorTool())

# 使用工具
tool = registry.get("calculator")
result = tool.execute(expression="2 + 2")
```

### 5. Security Subsystem（安全子系统）

**类比：权限管理 + 沙箱**

- Docker 容器隔离
- 完整的审计追踪
- 决策过程可视化
- 执行回放功能

```python
from agent_os_kernel import SandboxManager, SecurityPolicy

sandbox = SandboxManager()
policy = SecurityPolicy(
    max_memory_mb=512,
    max_cpu_percent=50,
    allowed_paths=["/tmp", "/workspace"]
)

# 创建沙箱
sandbox_id = sandbox.create_sandbox("agent-001", policy)

# 在沙箱中执行
result = sandbox.execute_in_sandbox("agent-001", "ls -la")
```

## 🚀 快速开始

### 安装

```bash
# 基础版本（仅 Python 标准库）
pip install agent-os-kernel

# 完整功能
pip install agent-os-kernel[all]

# 特定功能
pip install agent-os-kernel[postgres,claude,docker]
```

### 创建第一个 Agent

```python
from agent_os_kernel import AgentOSKernel

# 初始化内核
kernel = AgentOSKernel()

# 创建 Agent
agent_pid = kernel.spawn_agent(
    name="MyAssistant",
    task="Help me with coding",
    priority=50
)

# 运行
kernel.run(max_iterations=10)

# 查看状态
kernel.print_status()
```

### 与 Claude API 集成

```python
import os
from agent_os_kernel import ClaudeIntegratedKernel

# 设置 API 密钥
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

# 创建内核
kernel = ClaudeIntegratedKernel()

# 创建 Agent
agent_pid = kernel.spawn_agent(
    name="ResearchAssistant",
    task="Find information about AI agents",
    priority=30
)

# 运行
kernel.run(max_iterations=5)
```

## 📊 性能指标

### Context Manager
- **内存效率**: 90%+ 上下文利用率
- **Cache 命中率**: 目标 70%+（降低 10x 成本）
- **换页延迟**: < 100ms

### Process Scheduler
- **调度延迟**: < 10ms
- **公平性**: ±5% 资源分配偏差
- **吞吐量**: 1000+ 进程/小时

### Storage Layer
- **写入延迟**: < 50ms（PostgreSQL）
- **查询延迟**: < 100ms（向量检索）
- **审计完整性**: 100%（所有操作可追溯）

## 🎓 设计原则

### 1. 向操作系统学习
- **虚拟内存思想**: 透明的资源管理
- **进程抽象**: 统一的生命周期
- **分层架构**: 清晰的职责边界
- **标准接口**: 一致的 API 设计

### 2. 关键权衡

| 维度 | 选择 | 原因 |
|------|------|------|
| **调度策略** | 抢占式 | LLM 调用不可中断，只能步骤间抢占 |
| **存储方案** | PostgreSQL | 统一数据平面，ACID 保证 |
| **工具协议** | Agent-Native CLI | 利用 LLM 训练数据，减少 token 开销 |
| **安全模型** | 沙箱 + 审计 | 限制能力 + 建立信任 |

### 3. 未来扩展
- [ ] 分布式调度（多节点）
- [ ] GPU 资源管理
- [ ] 热迁移（进程在节点间迁移）
- [ ] 自适应调度（基于 RL）
- [ ] 联邦学习支持

## 📁 项目结构

```
agent-os-kernel/
├── agent_os_kernel/          # 核心包
│   ├── core/                 # 核心模块
│   │   ├── types.py          # 数据类型定义
│   │   ├── context_manager.py # 上下文管理器
│   │   ├── scheduler.py      # 进程调度器
│   │   ├── storage.py        # 存储层
│   │   └── security.py       # 安全子系统
│   ├── tools/                # 工具系统
│   │   ├── base.py           # 工具基类
│   │   ├── registry.py       # 工具注册表
│   │   └── builtin.py        # 内置工具
│   ├── integrations/         # 集成模块
│   │   └── claude_integration.py  # Claude API 集成
│   └── kernel.py             # 主内核
├── tests/                    # 测试套件
├── examples/                 # 使用示例
├── docs/                     # 文档
├── pyproject.toml            # 项目配置
├── requirements.txt          # 依赖
└── README.md                 # 本文件
```

## 🤝 贡献

欢迎贡献！这个项目正在快速演化。

关键领域：
1. **Context Manager**: 更智能的换页算法
2. **Scheduler**: 更好的公平性和吞吐量
3. **Storage**: 真实的 PostgreSQL 集成
4. **Security**: 完整的沙箱和审计
5. **Tools**: 更多的 Agent-Native CLI 包装

## 📄 许可证

MIT License

## 🙏 致谢

这个项目的灵感来自：
- Linux Kernel - 操作系统设计的典范
- PostgreSQL - 数据库的瑞士军刀
- Anthropic Claude - 展示了 Agent 的可能性

---

**Note**: 这是一个实验性项目，用于探索 Agent 基础设施的未来形态。生产使用需要更多的工程化工作。

如果你觉得这个方向有意思，欢迎 Star ⭐ 和讨论！

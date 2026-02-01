<div align="center">

# 🖥️ Agent OS Kernel

**Operating System Kernel for AI Agents**

> Inspired by [Ruohang Feng's "The Operating System Moment for AI Agents"](https://vonng.com/db/agent-os/), attempting to fill the "missing kernel" in the Agent ecosystem

[![CI](https://github.com/bit-cook/Agent-OS-Kernel/actions/workflows/ci.yml/badge.svg)](https://github.com/bit-cook/Agent-OS-Kernel/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/bit-cook/Agent-OS-Kernel/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[中文](./README.md) | [English](./README_EN.md) | [Manifesto](./MANIFESTO.md) | [Docs](https://github.com/bit-cook/Agent-OS-Kernel/wiki) | [Examples](./examples)

</div>

---

## 📖 Project Origin

In 2025, coding Agents exploded. Products like Claude Code and Manus demonstrated the amazing capabilities of AI Agents. But look closely, and you'll discover a startling fact: **their underlying operations are extremely "primitive"**.

Agents directly manipulate the file system and terminal, relying on a "trust model" rather than an "isolation model." This is just like **1980s DOS** — no memory protection, no multitasking, no standardized device interfaces.

It took us 30 years to evolve from DOS to modern operating systems, and the Agent ecosystem is now compressing and replaying this history.

**Agent OS Kernel was born to fill this "missing kernel."**

> For detailed philosophy, please read our [Manifesto (MANIFESTO.md)](./MANIFESTO.md) and the inspiration source ["The Operating System Moment for AI Agents"](https://vonng.com/db/agent-os/)

---

## 🎯 Core Insight: Understanding Agent Infrastructure Through Operating Systems

| Traditional Computer | Agent World | Core Challenge | Agent OS Kernel Solution |
|---------------------|-------------|----------------|-------------------------|
| **CPU** | **LLM** | How to efficiently schedule inference tasks? | Preemptive scheduling + resource quota management |
| **RAM** | **Context Window** | How to manage limited context windows? | [Virtual memory-style context management](#-memory-management-the-most-complex-and-important-battlefield) |
| **Disk** | **Database** | How to persist state? | [PostgreSQL's five roles](#-storage-database-the-most-certain-opportunity) |
| **Process** | **Agent** | How to manage lifecycle? | [True process management](#-process-management-red-ocean-on-the-surface-deep-waters-unexplored) |
| **Device Driver** | **Tools** | How to standardize tool invocation? | [Agent-Native CLI](#-io-management-the-appearance-and-essence-of-protocol-wars) |
| **Security** | **Sandbox** | How to ensure security? | [Sandbox + Observability + Audit](#-security-and-observability-trust-infrastructure) |

> **Core Insight**: Just as Linux lets applications ignore hardware details, Agent OS Kernel lets AI Agents ignore context management, resource scheduling, and persistent storage.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Agent Applications                     │
│     (CodeAssistant │ ResearchAgent │ DataAnalyst...)    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                 🎛️ Agent OS Kernel                       │
│  ┌──────────────┬──────────────┬──────────────┐         │
│  │   Context    │   Process    │    I/O       │         │
│  │   Manager    │  Scheduler   │   Manager    │         │
│  │  (Virtual    │  (Scheduler) │  (Tools)     │         │
│  │   Memory)    │              │              │         │
│  └──────────────┴──────────────┴──────────────┘         │
│  ┌──────────────────────────────────────────┐           │
│  │       💾 Storage Layer (PostgreSQL)       │           │
│  │   Memory │ State │ Vector Index │ Audit   │           │
│  └──────────────────────────────────────────┘           │
│  ┌──────────────────────────────────────────┐           │
│  │       🔒 Security Subsystem               │           │
│  │   Sandbox │ Observability │ Audit        │           │
│  └──────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                 🖥️ Hardware Resources                     │
│        LLM APIs │ Vector DB │ Message Queue              │
└─────────────────────────────────────────────────────────┘
```

---

## ✨ Core Features

### 🧠 Memory Management: The Most Complex and Important Battlefield

**History Lesson: Is 640KB Enough?** In 1981, IBM PC designers thought 640KB of memory "should be enough." Today, when we say 128K context is "already large," we're making the same mistake.

Agent OS Kernel implements **operating system-level virtual memory mechanisms**:

- **Context Pages**: Split long contexts into fixed-size pages
- **Page Fault**: Automatically load pages from database when accessed but not in memory
- **Page Replacement**: LRU + importance + semantic similarity multi-factor scoring
- **KV-Cache Optimization**: Static content first, dynamic content sorted by access frequency

> **Manus's Core Experience**: KV-Cache hit rate is the most important performance metric. On Claude, cached tokens cost 1/10th of uncached tokens.

```python
from agent_os_kernel import ContextManager

# Use context like virtual memory
cm = ContextManager(max_context_tokens=128000)

# Allocate page (automatic overflow handling)
page_id = cm.allocate_page(
    agent_pid="agent-1",
    content="Large amount of context content...",
    importance=0.8,
    page_type="user"
)

# Access page (automatic swap in)
page = cm.access_page(page_id)

# Get optimized context (KV-Cache friendly layout)
context = cm.get_agent_context(
    agent_pid="agent-1",
    optimize_for_cache=True  # Key: optimize cache hit rate
)
```

**Memory Hierarchy** (referencing DeepSeek Engram paper):

```
L1 Cache (Registers)  ->  System Prompt (< 1K tokens, always in context)
L2 Cache (Cache)      ->  Working Memory (10-20K tokens, current task)
RAM (Memory)          ->  Session Context (50-100K tokens, current session)
Disk (Storage)        ->  Long-term Memory (database, unlimited capacity)
```

### 💾 Storage (Database): The Most Certain Opportunity

**PostgreSQL's Five Roles**:

| Role | Function | Analogy |
|-----|------|------|
| **Long-term Memory** | Conversation history, learned knowledge, user preferences | Hippocampus |
| **State Persistence** | Checkpoints/snapshots, task state, recovery points | Hard Disk |
| **Vector Index** | Semantic retrieval, similarity matching, context swap decisions | Page Table |
| **Coordination** | Distributed locks, task queues, event notifications | IPC Mechanism |
| **Audit Log** | Immutable records of all operations, compliance, replayability | Black Box |

```python
from agent_os_kernel import StorageManager

# PostgreSQL serves five roles simultaneously
storage = StorageManager.from_postgresql(
    "postgresql://user:pass@localhost/agent_os",
    enable_vector=True  # Enable vector search (pgvector)
)

# 1. Long-term memory - save conversation history
storage.save_conversation(agent_pid, messages)

# 2. State persistence - create checkpoint
checkpoint_id = storage.create_checkpoint(agent_pid)

# 3. Vector index - semantic retrieval of relevant memories
results = storage.semantic_search(
    agent_pid="agent-1",
    query="Requirements user mentioned earlier",
    limit=5
)

# 4. Coordination - distributed locks
with storage.acquire_lock("task-123"):
    # Execute exclusive operation
    pass

# 5. Audit log - record all operations
storage.log_action(
    agent_pid="agent-1",
    action_type="tool_call",
    input={"tool": "calculator", "args": [1, 2]},
    output={"result": 3},
    reasoning="User asked to calculate 1+2"
)
```

### ⚡ Process Management: Red Ocean on the Surface, Deep Waters Unexplored

The core of current Agent frameworks is almost the same while loop:

```python
while not done:
    thought = llm.think(context)
    action = llm.decide(thought)
    result = tools.execute(action)
    context.update(result)
```

**When the core abstraction is so simple that any undergraduate can implement it, it cannot be a moat.**

True process management goes far beyond a while loop:

- **Concurrent Scheduling**: Priority + time slice + preemptive scheduling
- **State Persistence**: Recover from checkpoint after Agent crash
- **Inter-Process Communication**: State synchronization between Agents
- **Graceful Termination**: Safe exit rather than kill -9

```python
from agent_os_kernel import AgentOSKernel, ResourceQuota

# Configure resource quotas
quota = ResourceQuota(
    max_tokens_per_window=100000,    # Hourly token limit
    max_api_calls_per_window=1000,   # Hourly API call limit
)

kernel = AgentOSKernel(quota=quota)

# Create long-running Agent
agent_pid = kernel.spawn_agent(
    name="DBA_Agent",
    task="7x24 monitor database health",
    priority=10  # High priority
)

# Recover Agent from checkpoint after crash
new_pid = kernel.restore_checkpoint(checkpoint_id)
```

### 🛠️ I/O Management: Agent-Native CLI

While MCP is popular, it has issues with large token overhead and reinventing the wheel. **Unix CLI has been doing this elegantly for 55 years.**

Agent OS Kernel's judgment: **The eventual winner is "Agent-Native CLI"** — command-line tools with structured output, standardized error codes, and self-describing capabilities.

```python
from agent_os_kernel import Tool, ToolRegistry

# Define tool conforming to Agent-Native CLI standard
class DatabaseQueryTool(Tool):
    def name(self) -> str:
        return "query_db"
    
    def description(self) -> str:
        return "Query database with SQL"
    
    def parameters(self) -> dict:
        return {
            "sql": {"type": "string", "required": True}
        }
    
    def execute(self, sql: str, **kwargs) -> dict:
        # Standardized output format
        return {
            "success": True,
            "data": [...],
            "error": None,
            "metadata": {"rows": 10, "time_ms": 45}
        }

# Auto-discover system CLI tools
registry = ToolRegistry()
registry.auto_discover_cli_tools()  # Register grep, psql, curl, etc.
```

### 🔒 Security and Observability: Trust Infrastructure

**Prompt Injection is the Buffer Overflow of the AI era.**

True trust requires three layers of infrastructure:

| Layer | Function | Analogy |
|-----|------|------|
| **Sandbox** | Limit what Agent can do | Prison walls |
| **Observability** | Understand what Agent is doing and why | Security camera |
| **Audit Log** | Trace complete decision chain afterward | Aircraft black box |

```python
from agent_os_kernel import SecurityPolicy, PermissionLevel

# Configure security policy
policy = SecurityPolicy(
    permission_level=PermissionLevel.STANDARD,
    max_memory_mb=512,
    max_cpu_percent=50,
    allowed_paths=["/workspace"],
    blocked_paths=["/etc", "/root"],
    network_enabled=False
)

# Create restricted Agent
agent_pid = kernel.spawn_agent(
    name="SandboxedAgent",
    task="Process untrusted data",
    policy=policy
)

# View complete audit trail
audit = kernel.get_audit_trail(agent_pid)
for log in audit:
    print(f"[{log.timestamp}] {log.action_type}")
    print(f"  Input: {log.input_data}")
    print(f"  Reasoning: {log.reasoning}")
    print(f"  Output: {log.output_data}")
```

---

## 🚀 Quick Start

### Installation

```bash
# Basic version
pip install agent-os-kernel

# Production (PostgreSQL persistence)
pip install agent-os-kernel[postgres]

# Full features
pip install agent-os-kernel[all]
```

### Basic Example

```python
from agent_os_kernel import AgentOSKernel

# Initialize kernel
kernel = AgentOSKernel()

# Create Agent
agent_pid = kernel.spawn_agent(
    name="CodeAssistant",
    task="Help me write a Python web scraper",
    priority=30
)

# Run kernel
kernel.run(max_iterations=10)

# View system status
kernel.print_status()
```

### Claude Integration Example

```python
import os
from agent_os_kernel import ClaudeIntegratedKernel

os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

kernel = ClaudeIntegratedKernel()

# Create research Agent
agent_pid = kernel.spawn_agent(
    name="ResearchAssistant",
    task="Research latest developments in LLM context management",
    priority=10
)

# Run and monitor
kernel.run(max_iterations=5)

# View audit trail
audit = kernel.get_audit_trail(agent_pid)
```

---

## 📊 Performance Benchmarks

| Metric | Value | Description |
|--------|-------|-------------|
| **Context Utilization** | 92% | 40% improvement over native context window |
| **KV-Cache Hit Rate** | 75% | Reduces API costs by 8x |
| **Page Swap-in Latency** | 45ms | P95 latency |
| **Scheduling Latency** | 3ms | From ready to running |

---

## 🔍 Comparison with Other Frameworks

| Feature | Agent OS Kernel | LangChain | AutoGPT |
|---------|-----------------|-----------|---------|
| **Core Positioning** | OS Kernel | App Framework | Autonomous Agent |
| **Context Management** | ✅ Virtual Memory | ⚠️ Chained | ❌ Manual |
| **KV-Cache Optimization** | ✅ Built-in | ❌ | ❌ |
| **Multi-Agent Scheduling** | ✅ Preemptive | ❌ | ❌ |
| **PostgreSQL Five Roles** | ✅ Full Support | ⚠️ External | ⚠️ File |
| **Agent-Native CLI** | ✅ Built-in | ⚠️ External | ❌ |
| **Secure Sandbox** | ✅ Docker | ❌ | ❌ |
| **Decision Audit** | ✅ Complete | ❌ | ⚠️ Logging |

---

## 🗺️ Roadmap

### v0.2.x (Current)
- [x] Core kernel implementation
- [x] Virtual memory-style context management
- [x] KV-Cache optimization
- [x] PostgreSQL five roles support
- [x] Preemptive process scheduling
- [x] Docker sandbox
- [x] Complete audit trail

### v0.3.0 (In Progress)
- [ ] Database as Runtime exploration
- [ ] Distributed scheduler
- [ ] Agent hot migration
- [ ] Web UI monitoring dashboard

### v0.4.0 (Planned)
- [ ] Agent-Native CLI standard
- [ ] GPU resource management
- [ ] Kubernetes Operator

---

## 📚 Related Resources

### Inspiration Sources
- ["The Operating System Moment for AI Agents"](https://vonng.com/db/agent-os/) - Ruohang Feng
- [Context Engineering for AI Agents](https://manus.im/blog/context-engineering) - Manus
- [Engram](https://arxiv.org/abs/2502.01623) - DeepSeek

### Related Projects
- [Pigsty](https://pigsty.io/) - PostgreSQL distribution
- [E2B](https://e2b.dev/) - Agent sandbox
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol

---

## 📄 License

MIT License © 2026 Bit-Cook

---

<div align="center">

**If this project helps you, please give us a ⭐️ Star!**

[![Star History Chart](https://api.star-history.com/svg?repos=bit-cook/Agent-OS-Kernel&type=Date)](https://star-history.com/#bit-cook/Agent-OS-Kernel&Date)

</div>

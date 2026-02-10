# 🖥️ Agent OS Kernel

**AI Agent 的操作系统内核**

> 受到[《AI Agent 的操作系统时刻》](https://vonng.com/db/agent-os/) 启发，尝试填补 Agent 生态中"缺失的内核"

**支持本地模型**: Ollama | vLLM | Kimi | LocalAI  
**支持中国模型**: DeepSeek | Qwen | Kimi | MiniMax

[![CI](https://github.com/bit-cook/Agent-OS-Kernel/actions/workflows/ci.yml/badge.svg)](https://github.com/bit-cook/Agent-OS-Kernel/actions)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://github.com/bit-cook/Agent-OS-Kernel/releases)
[![License](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

[English](./README_EN.md) | [文档](docs/) | [示例](examples/)

---

## 快速开始

```bash
pip install agent-os-kernel
```

```python
from agent_os_kernel import AgentOSKernel

kernel = AgentOSKernel()
agent = kernel.spawn_agent(name="Assistant", role="general", goal="帮助用户")
kernel.run()
```

## 核心特性

| 特性 | 说明 |
|------|------|
| 虚拟内存式上下文 | LRU + 语义相似度的页面置换 |
| PostgreSQL 五重角色 | 记忆/状态/向量/协调/审计 |
| 抢占式调度 | 优先级 + 时间片 + 资源配额 |
| 多 Provider | OpenAI/DeepSeek/Kimi/Qwen 等 |
| MCP 工具 | 400+ 服务器支持 |
| 可观测性 | 指标/事件/追踪/成本追踪 |

## 项目结构

```
Agent-OS-Kernel/
├── agent_os_kernel/    # 核心代码 (40+ 模块)
├── examples/          # 示例代码 (27)
├── tests/            # 测试 (20+)
├── docs/             # 文档 (20+)
├── research/         # 研究 (15)
├── config/           # 配置
├── scripts/          # 脚本
└── development-docs/ # 开发文档
```

详见 [PROJECT_STRUCTURE.md](./docs/PROJECT_STRUCTURE.md)

## 统计

| 指标 | 数值 |
|------|------|
| Python 文件 | 140+ |
| 核心模块 | 40+ |
| LLM Providers | 11 |
| 测试 | 20+ |
| 文档 | 20+ |
| 研究 | 15 |

## 许可证

MIT License © 2026

---

⭐ Star 支持我们！

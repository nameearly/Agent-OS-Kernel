# -*- coding: utf-8 -*-
"""
Agent OS Kernel - 基于操作系统设计原理的 AI Agent 运行时内核

核心理念：
- 将 LLM 视为 CPU，调度推理任务
- 将 Context Window 视为 RAM，管理上下文窗口
- 将 Database 视为 Disk，持久化存储
- 将 Agent 视为 Process，生命周期管理

主要组件：
- ContextManager: 上下文管理器（虚拟内存）
- AgentScheduler: 进程调度器
- ToolRegistry: 工具注册表（I/O 管理）
- StorageManager: 存储管理器
- SecuritySubsystem: 安全子系统

使用示例：
    >>> from agent_os_kernel import AgentOSKernel
    >>> kernel = AgentOSKernel()
    >>> agent_pid = kernel.spawn_agent("Assistant", "Help me with coding")
    >>> kernel.run(max_iterations=10)
"""

__version__ = "0.2.0"
__author__ = "Bit-Cook"
__license__ = "MIT"

# 核心数据结构和枚举
from .core.types import (
    AgentState,
    AgentProcess,
    ContextPage,
    Checkpoint,
    AuditLog,
    ResourceQuota,
)

# 核心管理器
from .core.context_manager import ContextManager
from .core.scheduler import AgentScheduler
from .core.storage import StorageManager, PostgreSQLStorage
from .core.security import SandboxManager, SecurityPolicy

# 工具系统
from .tools.base import Tool, SimpleTool
from .tools.registry import ToolRegistry

# 主内核
from .kernel import AgentOSKernel

# 集成
from .integrations.claude_integration import ClaudeIntegratedKernel

__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__license__",
    
    # 核心类型
    "AgentState",
    "AgentProcess",
    "ContextPage",
    "Checkpoint",
    "AuditLog",
    "ResourceQuota",
    
    # 核心管理器
    "ContextManager",
    "AgentScheduler",
    "StorageManager",
    "PostgreSQLStorage",
    "SandboxManager",
    "SecurityPolicy",
    
    # 工具系统
    "Tool",
    "SimpleTool",
    "ToolRegistry",
    
    # 主内核和集成
    "AgentOSKernel",
    "ClaudeIntegratedKernel",
]

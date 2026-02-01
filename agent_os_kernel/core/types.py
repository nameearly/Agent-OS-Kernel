# -*- coding: utf-8 -*-
"""
Agent OS Kernel - 核心数据类型定义
"""

import uuid
import time
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime


class AgentState(Enum):
    """Agent 进程状态"""
    READY = "ready"           # 就绪，等待执行
    RUNNING = "running"       # 正在执行
    WAITING = "waiting"       # 等待资源（如 API 限流）
    SUSPENDED = "suspended"   # 被挂起（主动暂停）
    TERMINATED = "terminated" # 已终止
    ERROR = "error"           # 出错状态


class PageStatus(Enum):
    """上下文页面状态"""
    IN_MEMORY = "in_memory"   # 在内存中
    SWAPPED = "swapped"       # 已换出到磁盘
    LOADING = "loading"       # 正在加载
    DIRTY = "dirty"           # 已修改，需要写回


@dataclass
class AgentProcess:
    """
    Agent 进程控制块 (PCB - Process Control Block)
    
    类比操作系统 PCB，存储进程的所有状态信息
    """
    pid: str
    name: str
    state: AgentState = AgentState.READY
    priority: int = 50  # 0-100, 数字越小优先级越高
    
    # 资源使用统计
    token_usage: int = 0
    api_calls: int = 0
    execution_time: float = 0.0
    cpu_time: float = 0.0  # 实际推理时间
    
    # 上下文和状态
    context: Dict[str, Any] = field(default_factory=dict)
    checkpoint_id: Optional[str] = None
    parent_pid: Optional[str] = None  # 父进程 PID（支持进程层次结构）
    
    # 时间戳
    created_at: float = field(default_factory=time.time)
    last_run: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    terminated_at: Optional[float] = None
    
    # 调度相关
    time_slice: float = 60.0  # 时间片（秒）
    waiting_since: Optional[float] = None
    
    # 错误处理
    error_count: int = 0
    last_error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        data = asdict(self)
        data['state'] = self.state.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentProcess':
        """从字典恢复对象"""
        # 处理枚举
        if 'state' in data and isinstance(data['state'], str):
            data['state'] = AgentState(data['state'])
        
        # 过滤掉多余的字段
        valid_fields = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def is_active(self) -> bool:
        """检查进程是否处于活动状态"""
        return self.state in (AgentState.READY, AgentState.RUNNING, AgentState.WAITING)
    
    def get_runtime(self) -> float:
        """获取进程运行时间（秒）"""
        if self.terminated_at:
            return self.terminated_at - (self.started_at or self.created_at)
        return time.time() - (self.started_at or self.created_at)


@dataclass
class ContextPage:
    """
    上下文页面（内存页）
    
    类比操作系统的内存页，是上下文管理的最小单位
    """
    page_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_pid: str = ""
    content: str = ""
    tokens: int = 0
    
    # 页面属性
    importance_score: float = 0.5  # 0-1，重要性评分
    semantic_embedding: Optional[List[float]] = None  # 语义向量
    
    # 访问统计
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    created_at: float = field(default_factory=time.time)
    
    # 页面状态
    status: PageStatus = PageStatus.IN_MEMORY
    dirty: bool = False  # 是否已修改
    
    # 页面类型
    page_type: str = "general"  # system, task, history, tool_result 等
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    def touch(self):
        """更新访问时间（被访问时调用）"""
        self.access_count += 1
        self.last_accessed = time.time()
    
    def get_lru_score(self, current_time: Optional[float] = None) -> float:
        """
        计算 LRU 分数（越小越应该被换出）
        
        综合考虑：
        - 最后访问时间
        - 访问频率
        - 重要性
        """
        if current_time is None:
            current_time = time.time()
        
        time_factor = (current_time - self.last_accessed) / 3600  # 归一化到小时
        freq_factor = 1.0 / (self.access_count + 1)
        importance_factor = 1.0 - self.importance_score
        
        # 加权组合
        return time_factor * 0.4 + freq_factor * 0.3 + importance_factor * 0.3


@dataclass
class Checkpoint:
    """
    检查点（用于进程恢复）
    
    类比操作系统的进程快照，用于容错和迁移
    """
    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_pid: str = ""
    
    # 进程状态
    process_state: Dict[str, Any] = field(default_factory=dict)
    context_pages: List[Dict[str, Any]] = field(default_factory=list)
    
    # 元数据
    timestamp: float = field(default_factory=time.time)
    description: str = ""  # 检查点描述
    tags: List[str] = field(default_factory=list)
    
    # 版本控制
    parent_checkpoint: Optional[str] = None  # 父检查点（增量存储）
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class AuditLog:
    """
    审计日志条目
    
    记录 Agent 的每个重要操作，用于调试、审计和回放
    """
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_pid: str = ""
    action_type: str = ""  # llm_call, tool_call, state_change, error 等
    
    # 操作详情
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""  # Agent 的推理过程
    
    # 元数据
    timestamp: float = field(default_factory=time.time)
    duration_ms: Optional[float] = None  # 操作耗时
    
    # 资源使用
    tokens_used: int = 0
    api_calls: int = 0
    
    # 上下文信息
    session_id: Optional[str] = None
    trace_id: Optional[str] = None  # 分布式追踪 ID
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_readable_string(self) -> str:
        """转换为可读的字符串格式"""
        time_str = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return (
            f"[{time_str}] {self.action_type}\n"
            f"  Agent: {self.agent_pid[:8]}...\n"
            f"  Reasoning: {self.reasoning[:200]}...\n"
            f"  Tokens: {self.tokens_used}"
        )


@dataclass
class ResourceQuota:
    """
    资源配额定义
    
    用于限制 Agent 的资源使用
    """
    # 时间窗口（秒）
    window_seconds: int = 3600
    
    # Token 限制
    max_tokens_per_window: int = 100000
    max_tokens_per_request: int = 10000
    
    # API 调用限制
    max_api_calls_per_window: int = 1000
    max_api_calls_per_minute: int = 60
    
    # 计算资源限制
    max_execution_time: float = 300.0  # 最大执行时间（秒）
    max_memory_mb: int = 512  # 最大内存使用
    
    # 并发限制
    max_concurrent_tools: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class ToolCall:
    """工具调用记录"""
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    @property
    def duration_ms(self) -> Optional[float]:
        """获取执行耗时（毫秒）"""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None


@dataclass
class LLMResponse:
    """LLM 响应封装"""
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def prompt_tokens(self) -> int:
        return self.usage.get('prompt_tokens', 0)
    
    @property
    def completion_tokens(self) -> int:
        return self.usage.get('completion_tokens', 0)
    
    @property
    def total_tokens(self) -> int:
        return self.usage.get('total_tokens', 0)


# 类型别名
ProcessTable = Dict[str, AgentProcess]
PageTable = Dict[str, ContextPage]

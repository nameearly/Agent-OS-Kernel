# -*- coding: utf-8 -*-
"""
Agent OS Kernel - 主内核

整合所有子系统，提供统一的 Agent 运行时环境
"""

import uuid
import time
import logging
from typing import Optional, Dict, Any, List, Callable

from .core.types import AgentProcess, AgentState, ResourceQuota, AuditLog
from .core.context_manager import ContextManager
from .core.scheduler import AgentScheduler
from .core.storage import StorageManager, StorageBackend
from .core.security import SandboxManager, SecurityPolicy, PermissionManager
from .tools.registry import ToolRegistry
from .tools.builtin import (
    CalculatorTool,
    SearchTool,
    FileReadTool,
    FileWriteTool,
    PythonExecuteTool,
)


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class AgentOSKernel:
    """
    Agent OS Kernel - 主内核
    
    整合所有子系统：
    - ContextManager: 上下文管理
    - AgentScheduler: 进程调度
    - ToolRegistry: 工具注册
    - StorageManager: 存储管理
    - SandboxManager: 安全沙箱
    
    Attributes:
        version: 内核版本
        context_manager: 上下文管理器
        scheduler: 进程调度器
        tool_registry: 工具注册表
        storage: 存储管理器
        sandbox: 沙箱管理器
    """
    
    VERSION = "0.2.0"
    
    def __init__(self, 
                 max_context_tokens: int = 100000,
                 time_slice: float = 60.0,
                 storage_backend: Optional[StorageBackend] = None,
                 enable_sandbox: bool = True):
        """
        初始化 Agent OS Kernel
        
        Args:
            max_context_tokens: 最大上下文 token 数
            time_slice: 调度时间片（秒）
            storage_backend: 存储后端，默认使用内存存储
            enable_sandbox: 是否启用沙箱
        """
        logger.info("=" * 60)
        logger.info(f"Agent OS Kernel v{self.VERSION}")
        logger.info("=" * 60)
        
        # 初始化子系统
        self.context_manager = ContextManager(max_context_tokens=max_context_tokens)
        self.scheduler = AgentScheduler(
            time_slice=time_slice,
            quota=ResourceQuota()
        )
        self.tool_registry = ToolRegistry()
        self.storage = StorageManager(storage_backend)
        self.sandbox = SandboxManager() if enable_sandbox else None
        self.permission_manager = PermissionManager()
        
        # 注册内置工具
        self._register_builtin_tools()
        
        # 钩子函数
        self.pre_step_hooks: List[Callable] = []
        self.post_step_hooks: List[Callable] = []
        
        logger.info("[Kernel] Initialized successfully")
        logger.info("")
    
    def _register_builtin_tools(self):
        """注册内置工具"""
        tools = [
            CalculatorTool(),
            SearchTool(),
            FileReadTool(),
            FileWriteTool(),
            PythonExecuteTool(),
        ]
        
        for tool in tools:
            self.tool_registry.register(tool, category="builtin")
        
        logger.info(f"[Kernel] Registered {len(tools)} built-in tools")
    
    def spawn_agent(self, name: str, task: str, 
                   priority: int = 50,
                   policy: Optional[SecurityPolicy] = None) -> str:
        """
        创建并启动一个新 Agent
        
        Args:
            name: Agent 名称
            task: 任务描述
            priority: 优先级（0-100，越小越优先）
            policy: 安全策略
        
        Returns:
            Agent PID
        """
        # 1. 创建进程
        process = AgentProcess(
            pid=str(uuid.uuid4()),
            name=name,
            priority=priority
        )
        
        # 2. 初始化上下文
        system_prompt = f"You are {name}. Your task: {task}"
        page_id = self.context_manager.allocate_page(
            agent_pid=process.pid,
            content=system_prompt,
            importance=1.0,
            page_type="system"
        )
        
        task_page_id = self.context_manager.allocate_page(
            agent_pid=process.pid,
            content=f"Current task: {task}",
            importance=0.9,
            page_type="task"
        )
        
        process.context['system_page'] = page_id
        process.context['task_page'] = task_page_id
        process.context['task'] = task
        
        # 3. 设置安全策略
        if policy:
            self.permission_manager.set_policy(process.pid, policy)
        
        # 4. 创建沙箱
        if self.sandbox:
            self.sandbox.create_sandbox(process.pid, policy)
        
        # 5. 保存到存储
        self.storage.save_process(process)
        
        # 6. 加入调度队列
        self.scheduler.add_process(process)
        
        logger.info(f"✓ Spawned agent: {name} (PID: {process.pid[:8]}...)")
        logger.info(f"  Task: {task}")
        logger.info(f"  Priority: {priority}")
        logger.info("")
        
        return process.pid
    
    def execute_agent_step(self, process: AgentProcess) -> Dict[str, Any]:
        """
        执行 Agent 的一步推理
        
        子类应该重写这个方法来实现具体的 LLM 调用
        
        Args:
            process: Agent 进程
        
        Returns:
            执行结果
        """
        # 1. 执行前置钩子
        for hook in self.pre_step_hooks:
            hook(process)
        
        # 2. 获取上下文
        context = self.context_manager.get_agent_context(process.pid)
        
        # 3. 模拟 LLM 推理
        # 注意：实际实现应该调用 LLM API
        logger.info(f"[Agent {process.name}] Thinking...")
        time.sleep(0.5)  # 模拟推理延迟
        
        # 4. 模拟决策
        reasoning = f"I need to work on: {process.context.get('task', 'unknown task')}"
        action = {
            "tool": "calculator",
            "parameters": {"expression": "2 + 2"}
        }
        
        # 5. 请求资源配额
        tokens_needed = 1000
        if not self.scheduler.request_resources(process.pid, tokens_needed):
            logger.warning(f"[Agent {process.name}] Quota exceeded, waiting...")
            return {"done": False, "waiting": True}
        
        # 6. 执行工具调用
        tool = self.tool_registry.get(action['tool'])
        if tool:
            # 检查权限
            if not self.permission_manager.can_use_tool(process.pid, action['tool']):
                result = {
                    "success": False,
                    "error": f"Tool '{action['tool']}' is not allowed for this agent"
                }
            else:
                result = tool.execute(**action['parameters'])
        else:
            result = {"success": False, "error": "Tool not found"}
        
        # 7. 记录审计日志
        self.storage.log_action(
            agent_pid=process.pid,
            action_type="tool_call",
            input_data={"context": context[:500], "action": action},
            output_data=result,
            reasoning=reasoning
        )
        
        # 8. 更新上下文
        if result.get('success'):
            result_text = f"Tool: {action['tool']}\nResult: {result['data']}"
            self.context_manager.allocate_page(
                agent_pid=process.pid,
                content=result_text,
                importance=0.7,
                page_type="tool_result"
            )
        
        # 9. 执行后置钩子
        for hook in self.post_step_hooks:
            hook(process, result)
        
        logger.info(f"[Agent {process.name}] Executed: {action['tool']}")
        logger.info(f"  Reasoning: {reasoning[:200]}...")
        logger.info(f"  Result: {result}")
        logger.info("")
        
        return {
            "done": True,  # 模拟：一步就完成
            "reasoning": reasoning,
            "action": action,
            "result": result
        }
    
    def run(self, max_iterations: int = 10, single_agent: Optional[str] = None):
        """
        主事件循环
        
        Args:
            max_iterations: 最大迭代次数
            single_agent: 如果只运行特定 Agent，指定其 PID
        """
        logger.info("=" * 60)
        logger.info("Starting Agent OS Kernel main loop...")
        logger.info("=" * 60)
        logger.info("")
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"--- Iteration {iteration}/{max_iterations} ---")
            
            # 调度下一个 Agent
            if single_agent:
                process = self.scheduler.processes.get(single_agent)
                if not process or not process.is_active():
                    logger.info(f"Agent {single_agent[:8]}... is not active")
                    break
            else:
                process = self.scheduler.schedule()
            
            if not process:
                logger.info("No processes to schedule")
                time.sleep(1)
                continue
            
            # 执行一步
            try:
                result = self.execute_agent_step(process)
                
                # 检查是否完成
                if result.get('done'):
                    self.scheduler.terminate_process(process.pid)
                    logger.info(f"✓ Agent {process.name} completed")
                
                # 检查是否需要等待
                if result.get('waiting'):
                    self.scheduler.wait_process(process.pid, "resource_quota")
                
            except Exception as e:
                logger.exception(f"✗ Error in agent {process.name}")
                process.error_count += 1
                process.last_error = str(e)
                
                if process.error_count >= 3:
                    logger.error(f"Agent {process.name} exceeded error limit, terminating")
                    self.scheduler.terminate_process(process.pid, reason="error")
                else:
                    # 重试
                    self.scheduler.wait_process(process.pid, "error_recovery")
            
            logger.info("")
            time.sleep(0.5)
        
        logger.info("=" * 60)
        logger.info("Agent OS Kernel shutdown")
        logger.info("=" * 60)
    
    def create_checkpoint(self, agent_pid: str, 
                         description: str = "") -> Optional[str]:
        """
        为 Agent 创建检查点
        
        Args:
            agent_pid: Agent PID
            description: 检查点描述
        
        Returns:
            检查点 ID
        """
        process = self.scheduler.processes.get(agent_pid)
        if not process:
            logger.error(f"Agent {agent_pid[:8]}... not found")
            return None
        
        checkpoint_id = self.storage.save_checkpoint(process, description)
        process.checkpoint_id = checkpoint_id
        
        logger.info(f"Created checkpoint {checkpoint_id[:8]}... for agent {process.name}")
        return checkpoint_id
    
    def restore_checkpoint(self, checkpoint_id: str) -> Optional[str]:
        """
        从检查点恢复 Agent
        
        Args:
            checkpoint_id: 检查点 ID
        
        Returns:
            新 Agent PID
        """
        checkpoint = self.storage.load_checkpoint(checkpoint_id)
        if not checkpoint:
            logger.error(f"Checkpoint {checkpoint_id[:8]}... not found")
            return None
        
        # 恢复进程状态
        process_data = checkpoint.process_state
        new_process = AgentProcess.from_dict(process_data)
        new_process.pid = str(uuid.uuid4())  # 分配新 PID
        new_process.state = AgentState.READY
        new_process.created_at = time.time()
        
        # 重新加入调度
        self.scheduler.add_process(new_process)
        self.storage.save_process(new_process)
        
        logger.info(f"Restored agent {new_process.name} from checkpoint "
                   f"{checkpoint_id[:8]}... (new PID: {new_process.pid[:8]}...)")
        
        return new_process.pid
    
    def terminate_agent(self, agent_pid: str, reason: str = "user_request"):
        """
        终止 Agent
        
        Args:
            agent_pid: Agent PID
            reason: 终止原因
        """
        process = self.scheduler.processes.get(agent_pid)
        if not process:
            return
        
        # 清理资源
        self.context_manager.release_agent_pages(agent_pid)
        
        if self.sandbox:
            self.sandbox.destroy_sandbox(agent_pid)
        
        self.scheduler.terminate_process(agent_pid, reason)
        
        logger.info(f"Terminated agent {process.name} (reason: {reason})")
    
    def get_agent_status(self, agent_pid: str) -> Optional[Dict[str, Any]]:
        """获取 Agent 状态"""
        process = self.scheduler.processes.get(agent_pid)
        if not process:
            return None
        
        return {
            "pid": process.pid,
            "name": process.name,
            "state": process.state.value,
            "priority": process.priority,
            "token_usage": process.token_usage,
            "api_calls": process.api_calls,
            "execution_time": process.get_runtime(),
            "error_count": process.error_count,
        }
    
    def print_status(self):
        """打印系统状态"""
        print("\n" + "=" * 60)
        print("System Status")
        print("=" * 60)
        
        # Context Manager
        ctx_stats = self.context_manager.get_stats()
        print(f"\n[Context Manager]")
        print(f"  Memory: {ctx_stats['current_usage']:,} / {ctx_stats['max_tokens']:,} tokens "
              f"({ctx_stats['usage_percent']:.1f}%)")
        print(f"  Pages in memory: {ctx_stats['pages_in_memory']}")
        print(f"  Pages swapped: {ctx_stats['pages_swapped']}")
        print(f"  Page faults: {ctx_stats['page_faults']}")
        
        # Scheduler
        sched_stats = self.scheduler.get_process_stats()
        print(f"\n[Scheduler]")
        print(f"  Total processes: {sched_stats['total_processes']}")
        print(f"  Active: {sched_stats['active_processes']}")
        print(f"  Running: {sched_stats['running'] or 'None'}")
        print(f"  Ready queue: {sched_stats['ready_queue_size']}")
        print(f"  Waiting queue: {sched_stats['waiting_queue_size']}")
        
        quota_stats = sched_stats['quota_usage']
        print(f"  Token quota: {quota_stats['global_usage']['tokens']:,} / "
              f"{quota_stats['global_limits']['tokens']:,} "
              f"({quota_stats['usage_percent']['tokens']:.1f}%)")
        
        # Storage
        storage_stats = self.storage.get_stats()
        print(f"\n[Storage]")
        print(f"  Processes: {storage_stats['processes']}")
        print(f"  Checkpoints: {storage_stats['checkpoints']}")
        print(f"  Audit logs: {storage_stats['audit_logs']}")
        
        # Tools
        tool_stats = self.tool_registry.get_stats()
        print(f"\n[Tools]")
        print(f"  Registered: {tool_stats['total_tools']}")
        print(f"  Categories: {', '.join(tool_stats['categories'].keys())}")
        
        print("=" * 60 + "\n")
    
    def add_pre_step_hook(self, hook: Callable):
        """添加前置钩子"""
        self.pre_step_hooks.append(hook)
    
    def add_post_step_hook(self, hook: Callable):
        """添加后置钩子"""
        self.post_step_hooks.append(hook)
    
    def get_audit_trail(self, agent_pid: str, limit: int = 100) -> List[AuditLog]:
        """获取审计追踪"""
        return self.storage.get_audit_trail(agent_pid, limit)
    
    def shutdown(self):
        """关闭内核"""
        logger.info("Shutting down Agent OS Kernel...")
        
        # 终止所有活动进程
        for process in list(self.scheduler.processes.values()):
            if process.is_active():
                self.terminate_agent(process.pid, reason="shutdown")
        
        # 关闭存储
        self.storage.close()
        
        logger.info("Agent OS Kernel shutdown complete")

# -*- coding: utf-8 -*-
"""
Agent Scheduler - 进程调度器

类比操作系统进程调度：
- 优先级调度
- 时间片轮转
- 抢占式调度
- 资源配额管理
"""

import time
import logging
from typing import Optional, Dict, Any, List
from queue import PriorityQueue, Empty
from collections import defaultdict
from dataclasses import dataclass, field

from .types import AgentProcess, AgentState, ResourceQuota


logger = logging.getLogger(__name__)


@dataclass(order=True)
class SchedulableProcess:
    """可调度进程包装器（用于优先级队列）"""
    priority: int
    timestamp: float = field(compare=True)
    process: AgentProcess = field(compare=False)


class ResourceQuotaManager:
    """
    资源配额管理器
    
    管理 API 调用、Token 使用等资源配额
    """
    
    def __init__(self, quota: ResourceQuota):
        self.quota = quota
        self.current_usage = {
            'tokens': 0,
            'api_calls': 0,
        }
        self.per_agent_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            'tokens': 0,
            'api_calls': 0,
        })
        self.window_start = time.time()
    
    def reset_if_needed(self):
        """检查并重置配额窗口"""
        current_time = time.time()
        if current_time - self.window_start >= self.quota.window_seconds:
            logger.info(f"Resetting quota window (was active for {current_time - self.window_start:.0f}s)")
            self.current_usage = {'tokens': 0, 'api_calls': 0}
            self.per_agent_usage.clear()
            self.window_start = current_time
    
    def request_quota(self, agent_pid: str, tokens: int, 
                     api_calls: int = 1) -> Tuple[bool, str]:
        """
        请求资源配额
        
        Returns:
            (是否批准, 原因)
        """
        self.reset_if_needed()
        
        # 检查全局配额
        if self.current_usage['tokens'] + tokens > self.quota.max_tokens_per_window:
            return False, "Global token quota exceeded"
        
        if self.current_usage['api_calls'] + api_calls > self.quota.max_api_calls_per_window:
            return False, "Global API call quota exceeded"
        
        # 检查单个请求限制
        if tokens > self.quota.max_tokens_per_request:
            return False, f"Request exceeds max tokens per request ({self.quota.max_tokens_per_request})"
        
        # 检查单个 Agent 配额
        agent_usage = self.per_agent_usage[agent_pid]
        max_per_agent_tokens = self.quota.max_tokens_per_window * 0.3
        max_per_agent_calls = self.quota.max_api_calls_per_window * 0.3
        
        if agent_usage['tokens'] + tokens > max_per_agent_tokens:
            return False, "Agent token quota exceeded (30% of global)"
        
        if agent_usage['api_calls'] + api_calls > max_per_agent_calls:
            return False, "Agent API call quota exceeded (30% of global)"
        
        # 批准并记录
        self.current_usage['tokens'] += tokens
        self.current_usage['api_calls'] += api_calls
        agent_usage['tokens'] += tokens
        agent_usage['api_calls'] += api_calls
        
        return True, "Approved"
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """获取使用统计"""
        return {
            'window_start': self.window_start,
            'window_elapsed': time.time() - self.window_start,
            'global_usage': self.current_usage.copy(),
            'global_limits': {
                'tokens': self.quota.max_tokens_per_window,
                'api_calls': self.quota.max_api_calls_per_window,
            },
            'usage_percent': {
                'tokens': (self.current_usage['tokens'] / self.quota.max_tokens_per_window) * 100,
                'api_calls': (self.current_usage['api_calls'] / self.quota.max_api_calls_per_window) * 100,
            },
            'per_agent_count': len(self.per_agent_usage),
        }


class AgentScheduler:
    """
    Agent 调度器
    
    实现功能：
    1. 优先级调度（数字越小优先级越高）
    2. 时间片轮转
    3. 抢占式调度
    4. 资源配额管理
    5. 等待队列管理
    
    Attributes:
        time_slice: 默认时间片（秒）
        ready_queue: 就绪队列
        waiting_queue: 等待队列
        processes: 所有进程表
        running: 当前运行的进程
    """
    
    def __init__(self, time_slice: float = 60.0, 
                 quota: Optional[ResourceQuota] = None):
        """
        初始化调度器
        
        Args:
            time_slice: 默认时间片（秒）
            quota: 资源配额配置
        """
        self.time_slice = time_slice
        
        # 就绪队列（优先级队列）
        self.ready_queue: PriorityQueue[SchedulableProcess] = PriorityQueue()
        
        # 等待队列（不按优先级，按等待原因）
        self.waiting_queue: Dict[str, AgentProcess] = {}
        
        # 所有进程
        self.processes: Dict[str, AgentProcess] = {}
        
        # 当前运行的进程
        self.running: Optional[AgentProcess] = None
        
        # 资源配额
        self.quota_manager = ResourceQuotaManager(quota or ResourceQuota())
        
        # 统计
        self.stats = {
            'total_scheduled': 0,
            'total_preempted': 0,
            'total_completed': 0,
            'total_errors': 0,
        }
        
        logger.info(f"AgentScheduler initialized with {time_slice}s time slice")
    
    def add_process(self, process: AgentProcess):
        """
        添加新进程到调度队列
        
        Args:
            process: Agent 进程
        """
        self.processes[process.pid] = process
        self._enqueue(process)
        logger.info(f"Added process {process.name} (PID: {process.pid[:8]}...)")
    
    def _enqueue(self, process: AgentProcess):
        """将进程加入就绪队列"""
        process.state = AgentState.READY
        schedulable = SchedulableProcess(
            priority=process.priority,
            timestamp=time.time(),
            process=process
        )
        self.ready_queue.put(schedulable)
    
    def schedule(self) -> Optional[AgentProcess]:
        """
        调度下一个要执行的进程
        
        Returns:
            被调度的进程，如果没有则返回 None
        """
        # 检查并重置配额
        self.quota_manager.reset_if_needed()
        
        # 检查当前进程是否需要抢占
        if self.running:
            if self._should_preempt(self.running):
                logger.debug(f"Preempting {self.running.name}")
                self._enqueue(self.running)
                self.running = None
                self.stats['total_preempted'] += 1
        
        # 检查等待队列中是否有进程可以唤醒
        self._check_waiting_queue()
        
        # 如果没有运行中的进程，从队列取一个
        if not self.running:
            try:
                schedulable = self.ready_queue.get(block=False)
                process = schedulable.process
                
                # 检查进程是否仍然有效
                if process.state == AgentState.TERMINATED:
                    return self.schedule()  # 递归获取下一个
                
                process.state = AgentState.RUNNING
                process.last_run = time.time()
                if process.started_at is None:
                    process.started_at = time.time()
                
                self.running = process
                self.stats['total_scheduled'] += 1
                
                logger.debug(f"Scheduled {process.name} (priority={process.priority})")
                
            except Empty:
                pass
        
        return self.running
    
    def _should_preempt(self, process: AgentProcess) -> bool:
        """
        判断是否应该抢占当前进程
        
        抢占条件：
        1. 时间片用完
        2. 有更高优先级的进程在等待
        3. 资源使用过多
        4. 进程执行时间过长
        """
        # 1. 时间片用完
        if time.time() - process.last_run > self.time_slice:
            logger.debug(f"Time slice expired for {process.name}")
            return True
        
        # 2. 有更高优先级的进程在等待
        if not self.ready_queue.empty():
            # 查看队列中的最高优先级
            next_schedulable = self.ready_queue.queue[0]
            if next_schedulable.priority < process.priority - 10:  # 优先级差距超过 10
                logger.debug(f"Higher priority process waiting (prio {next_schedulable.priority} < {process.priority})")
                return True
        
        # 3. 资源使用过多（单个进程占用超过 30% 配额）
        quota_stats = self.quota_manager.get_usage_stats()
        agent_usage = self.quota_manager.per_agent_usage.get(process.pid, {})
        if agent_usage.get('tokens', 0) > quota_stats['global_limits']['tokens'] * 0.3:
            logger.debug(f"Resource usage exceeded for {process.name}")
            return True
        
        # 4. 执行时间过长
        if time.time() - process.started_at > process.time_slice * 5:  # 超过5个时间片
            logger.debug(f"Execution time limit exceeded for {process.name}")
            return True
        
        return False
    
    def _check_waiting_queue(self):
        """检查等待队列，尝试唤醒进程"""
        to_wakeup = []
        
        for pid, process in self.waiting_queue.items():
            # 这里可以实现各种唤醒条件
            # 例如：资源可用、超时、外部事件等
            if process.waiting_since and time.time() - process.waiting_since > 30:
                # 等待超过30秒的进程尝试唤醒
                to_wakeup.append(pid)
        
        for pid in to_wakeup:
            self.wakeup_process(pid)
    
    def wait_process(self, pid: str, reason: str = "waiting"):
        """
        将进程置为等待状态
        
        Args:
            pid: 进程 ID
            reason: 等待原因
        """
        process = self.processes.get(pid)
        if not process:
            return
        
        if self.running and self.running.pid == pid:
            self.running = None
        
        process.state = AgentState.WAITING
        process.waiting_since = time.time()
        self.waiting_queue[pid] = process
        
        logger.debug(f"Process {process.name} is now waiting ({reason})")
    
    def wakeup_process(self, pid: str):
        """
        唤醒等待中的进程
        
        Args:
            pid: 进程 ID
        """
        if pid in self.waiting_queue:
            process = self.waiting_queue.pop(pid)
            process.waiting_since = None
            self._enqueue(process)
            logger.debug(f"Woke up process {process.name}")
    
    def terminate_process(self, pid: str, reason: str = "completed"):
        """
        终止进程
        
        Args:
            pid: 进程 ID
            reason: 终止原因
        """
        process = self.processes.get(pid)
        if not process:
            return
        
        process.state = AgentState.TERMINATED
        process.terminated_at = time.time()
        
        if self.running and self.running.pid == pid:
            self.running = None
        
        if pid in self.waiting_queue:
            del self.waiting_queue[pid]
        
        if reason == "error":
            self.stats['total_errors'] += 1
        else:
            self.stats['total_completed'] += 1
        
        logger.info(f"Terminated {process.name} (reason: {reason})")
    
    def suspend_process(self, pid: str) -> Optional[str]:
        """
        挂起进程（保存检查点）
        
        Args:
            pid: 进程 ID
        
        Returns:
            检查点 ID（如果支持）
        """
        process = self.processes.get(pid)
        if not process:
            return None
        
        if self.running and self.running.pid == pid:
            self.running = None
        
        process.state = AgentState.SUSPENDED
        # 这里应该创建检查点，返回 checkpoint_id
        # 简化实现，返回 None
        return None
    
    def resume_process(self, pid: str):
        """
        恢复挂起的进程
        
        Args:
            pid: 进程 ID
        """
        process = self.processes.get(pid)
        if not process or process.state != AgentState.SUSPENDED:
            return
        
        self._enqueue(process)
        logger.info(f"Resumed process {process.name}")
    
    def request_resources(self, agent_pid: str, tokens: int, 
                         api_calls: int = 1) -> bool:
        """
        请求资源配额
        
        Args:
            agent_pid: Agent PID
            tokens: 需要的 token 数
            api_calls: 需要的 API 调用次数
        
        Returns:
            是否批准
        """
        approved, reason = self.quota_manager.request_quota(agent_pid, tokens, api_calls)
        
        if not approved:
            logger.warning(f"Resource request denied for {agent_pid[:8]}: {reason}")
            # 将进程置为等待状态
            self.wait_process(agent_pid, reason)
        else:
            # 更新进程统计
            process = self.processes.get(agent_pid)
            if process:
                process.token_usage += tokens
                process.api_calls += api_calls
        
        return approved
    
    def get_active_processes(self) -> List[AgentProcess]:
        """获取所有活动进程"""
        return [p for p in self.processes.values() if p.is_active()]
    
    def get_process_stats(self) -> Dict[str, Any]:
        """获取进程统计"""
        states = defaultdict(int)
        for p in self.processes.values():
            states[p.state.value] += 1
        
        return {
            **self.stats,
            'total_processes': len(self.processes),
            'active_processes': len(self.get_active_processes()),
            'running': self.running.name if self.running else None,
            'ready_queue_size': self.ready_queue.qsize(),
            'waiting_queue_size': len(self.waiting_queue),
            'state_distribution': dict(states),
            'quota_usage': self.quota_manager.get_usage_stats(),
        }

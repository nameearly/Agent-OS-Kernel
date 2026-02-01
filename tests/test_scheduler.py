"""测试调度器"""

import time
import pytest
from agent_os_kernel.core.scheduler import (
    AgentScheduler,
    ResourceQuotaManager,
)
from agent_os_kernel.core.types import (
    AgentProcess,
    AgentState,
    ResourceQuota,
)


class TestResourceQuotaManager:
    def test_request_quota_approved(self):
        quota = ResourceQuota(
            max_tokens_per_window=1000,
            max_api_calls_per_window=100
        )
        manager = ResourceQuotaManager(quota)
        
        approved, reason = manager.request_quota("agent-1", 100, 1)
        
        assert approved is True
        assert manager.current_usage['tokens'] == 100
    
    def test_request_quota_denied_global(self):
        quota = ResourceQuota(max_tokens_per_window=100)
        manager = ResourceQuotaManager(quota)
        
        approved, reason = manager.request_quota("agent-1", 200, 1)
        
        assert approved is False
        assert "Global token quota" in reason
    
    def test_request_quota_denied_per_agent(self):
        quota = ResourceQuota(max_tokens_per_window=1000)
        manager = ResourceQuotaManager(quota)
        
        # 第一个请求应该成功
        manager.request_quota("agent-1", 400, 1)
        # 第二个请求应该失败（超过 30% 限制）
        approved, reason = manager.request_quota("agent-1", 100, 1)
        
        # 400 + 100 = 500, 超过 1000 * 0.3 = 300
        assert approved is False
        assert "Agent token quota" in reason


class TestAgentScheduler:
    def test_add_process(self):
        scheduler = AgentScheduler()
        process = AgentProcess(pid="test-1", name="Test")
        
        scheduler.add_process(process)
        
        assert process.pid in scheduler.processes
        assert scheduler.ready_queue.qsize() == 1
    
    def test_schedule_returns_process(self):
        scheduler = AgentScheduler()
        process = AgentProcess(pid="test-1", name="Test", priority=10)
        
        scheduler.add_process(process)
        scheduled = scheduler.schedule()
        
        assert scheduled is not None
        assert scheduled.pid == "test-1"
        assert scheduled.state == AgentState.RUNNING
    
    def test_schedule_empty_queue(self):
        scheduler = AgentScheduler()
        
        scheduled = scheduler.schedule()
        
        assert scheduled is None
    
    def test_priority_ordering(self):
        scheduler = AgentScheduler()
        
        # 低优先级先加入
        low_priority = AgentProcess(pid="low", name="Low", priority=50)
        high_priority = AgentProcess(pid="high", name="High", priority=10)
        
        scheduler.add_process(low_priority)
        scheduler.add_process(high_priority)
        
        # 应该先调度高优先级
        scheduled = scheduler.schedule()
        assert scheduled.pid == "high"
    
    def test_terminate_process(self):
        scheduler = AgentScheduler()
        process = AgentProcess(pid="test-1", name="Test")
        
        scheduler.add_process(process)
        scheduler.terminate_process("test-1")
        
        assert process.state == AgentState.TERMINATED
        assert process.pid not in scheduler.waiting_queue
    
    def test_wait_and_wakeup(self):
        scheduler = AgentScheduler()
        process = AgentProcess(pid="test-1", name="Test")
        
        scheduler.add_process(process)
        scheduler.schedule()  # 设置为 running
        
        scheduler.wait_process("test-1", "test_reason")
        
        assert process.state == AgentState.WAITING
        assert "test-1" in scheduler.waiting_queue
        
        scheduler.wakeup_process("test-1")
        
        assert process.state == AgentState.READY
        assert "test-1" not in scheduler.waiting_queue
    
    def test_get_process_stats(self):
        scheduler = AgentScheduler()
        process = AgentProcess(pid="test-1", name="Test")
        
        scheduler.add_process(process)
        stats = scheduler.get_process_stats()
        
        assert stats['total_processes'] == 1
        assert stats['active_processes'] == 1

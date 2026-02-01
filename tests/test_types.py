"""测试核心类型"""

import pytest
from agent_os_kernel.core.types import (
    AgentState,
    AgentProcess,
    ContextPage,
    PageStatus,
)


class TestAgentState:
    def test_enum_values(self):
        assert AgentState.READY.value == "ready"
        assert AgentState.RUNNING.value == "running"
        assert AgentState.WAITING.value == "waiting"
        assert AgentState.SUSPENDED.value == "suspended"
        assert AgentState.TERMINATED.value == "terminated"
        assert AgentState.ERROR.value == "error"


class TestAgentProcess:
    def test_default_creation(self):
        process = AgentProcess(pid="test-123", name="TestAgent")
        
        assert process.pid == "test-123"
        assert process.name == "TestAgent"
        assert process.state == AgentState.READY
        assert process.priority == 50
        assert process.token_usage == 0
        assert process.api_calls == 0
    
    def test_to_dict(self):
        process = AgentProcess(pid="test-123", name="TestAgent")
        data = process.to_dict()
        
        assert data['pid'] == "test-123"
        assert data['name'] == "TestAgent"
        assert data['state'] == "ready"
    
    def test_from_dict(self):
        data = {
            'pid': 'test-123',
            'name': 'TestAgent',
            'state': 'running',
            'priority': 30,
        }
        process = AgentProcess.from_dict(data)
        
        assert process.pid == 'test-123'
        assert process.state == AgentState.RUNNING
        assert process.priority == 30
    
    def test_is_active(self):
        ready = AgentProcess(pid="1", name="Ready", state=AgentState.READY)
        running = AgentProcess(pid="2", name="Running", state=AgentState.RUNNING)
        waiting = AgentProcess(pid="3", name="Waiting", state=AgentState.WAITING)
        terminated = AgentProcess(pid="4", name="Terminated", state=AgentState.TERMINATED)
        
        assert ready.is_active() is True
        assert running.is_active() is True
        assert waiting.is_active() is True
        assert terminated.is_active() is False


class TestContextPage:
    def test_default_creation(self):
        page = ContextPage(agent_pid="agent-1", content="Test content")
        
        assert page.agent_pid == "agent-1"
        assert page.content == "Test content"
        assert page.importance_score == 0.5
        assert page.status == PageStatus.IN_MEMORY
    
    def test_touch_updates_access(self):
        page = ContextPage(agent_pid="agent-1", content="Test")
        initial_count = page.access_count
        
        page.touch()
        
        assert page.access_count == initial_count + 1
        assert page.last_accessed > 0
    
    def test_get_lru_score(self):
        import time
        page = ContextPage(
            agent_pid="agent-1",
            content="Test",
            importance_score=1.0,
            access_count=10
        )
        
        score = page.get_lru_score()
        
        # 高重要性、高访问次数的页面应该有较低的换出分数
        assert score >= 0
        assert score <= 1  # 由于归一化

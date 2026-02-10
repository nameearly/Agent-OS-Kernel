"""测试类型定义"""

import pytest
from enum import Enum
from typing import Dict, List, Any

from agent_os_kernel.core.types import (
    AgentState,
    ResourceQuota,
    PermissionLevel,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
    MessageType,
    AgentType,
)


class TestAgentState:
    """测试 AgentState 枚举"""
    
    def test_state_values(self):
        """测试状态值"""
        assert AgentState.CREATED.value == "created"
        assert AgentState.IDLE.value == "idle"
        assert AgentState.RUNNING.value == "running"
        assert AgentState.WAITING.value == "waiting"
        assert AgentState.COMPLETED.value == "completed"
        assert AgentState.FAILED.value == "failed"
        assert AgentState.STOPPED.value == "stopped"
    
    def test_state_count(self):
        """测试状态数量"""
        states = list(AgentState)
        assert len(states) == 8


class TestResourceQuota:
    """测试 ResourceQuota"""
    
    def test_default_values(self):
        """测试默认值"""
        quota = ResourceQuota()
        
        assert quota.max_tokens == 128000
        assert quota.max_memory_mb == 1024
        assert quota.max_cpu_percent == 100
        assert quota.max_disk_gb == 10
    
    def test_custom_values(self):
        """测试自定义值"""
        quota = ResourceQuota(
            max_tokens=64000,
            max_memory_mb=512,
            max_cpu_percent=50
        )
        
        assert quota.max_tokens == 64000
        assert quota.max_memory_mb == 512
        assert quota.max_cpu_percent == 50


class TestPermissionLevel:
    """测试 PermissionLevel"""
    
    def test_permission_values(self):
        """测试权限值"""
        assert PermissionLevel.RESTRICTED.value == "restricted"
        assert PermissionLevel.STANDARD.value == "standard"
        assert PermissionLevel.ADVANCED.value == "advanced"
        assert PermissionLevel.FULL.value == "full"


class TestToolCategory:
    """测试 ToolCategory"""
    
    def test_category_values(self):
        """测试类别值"""
        assert ToolCategory.CALCULATOR.value == "calculator"
        assert ToolCategory.FILE.value == "file"
        assert ToolCategory.NETWORK.value == "network"
        assert ToolCategory.DATABASE.value == "database"


class TestToolDefinition:
    """测试 ToolDefinition"""
    
    def test_create_definition(self):
        """测试创建工具定义"""
        tool = ToolDefinition(
            name="calculator",
            description="Perform math calculations",
            category=ToolCategory.CALCULATOR,
            version="1.0.0",
            author="Agent-OS-Kernel"
        )
        
        assert tool.name == "calculator"
        assert tool.category == ToolCategory.CALCULATOR
        assert tool.version == "1.0.0"
    
    def test_to_dict(self):
        """测试转换为字典"""
        tool = ToolDefinition(
            name="test_tool",
            description="Test tool"
        )
        
        result = tool.to_dict()
        
        assert result["name"] == "test_tool"
        assert result["description"] == "Test tool"
        assert result["category"] == "general"
        assert result["version"] == "1.0.0"
    
    def test_with_parameters(self):
        """测试带参数的工具"""
        param = ToolParameter(
            name="num1",
            param_type="number",
            required=True,
            description="First number"
        )
        
        tool = ToolDefinition(
            name="add",
            description="Add two numbers",
            parameters=[param]
        )
        
        assert len(tool.parameters) == 1
        assert tool.parameters[0].name == "num1"


class TestMessageType:
    """测试 MessageType"""
    
    def test_message_types(self):
        """测试消息类型"""
        assert MessageType.CHAT.value == "chat"
        assert MessageType.TASK.value == "task"
        assert MessageType.SYSTEM.value == "system"
        assert MessageType.ERROR.value == "error"


class TestAgentType:
    """测试 AgentType"""
    
    def test_agent_types(self):
        """测试 Agent 类型"""
        assert AgentType.GENERAL.value == "general"
        assert AgentType.CODER.value == "coder"
        assert AgentType.RESEARCHER.value == "researcher"
        assert AgentType.WRITER.value == "writer"

"""测试Agent定义"""

import pytest


class TestAgentDefinition:
    """测试Agent定义"""
    
    def test_agent_definition_exists(self):
        """测试Agent定义存在"""
        from agent_os_kernel.core.agent_definition import AgentDefinition
        assert AgentDefinition is not None
    
    def test_task_definition_exists(self):
        """测试Task定义存在"""
        from agent_os_kernel.core.agent_definition import TaskDefinition
        assert TaskDefinition is not None
    
    def test_crew_definition_exists(self):
        """测试Crew定义存在"""
        from agent_os_kernel.core.agent_definition import CrewDefinition
        assert CrewDefinition is not None

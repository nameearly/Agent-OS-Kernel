"""测试工作流引擎"""

import pytest
import asyncio


class TestWorkflowEngine:
    """测试工作流引擎"""
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """测试初始化"""
        from agent_os_kernel.core.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        assert engine is not None
    
    @pytest.mark.asyncio
    async def test_create_workflow(self):
        """测试创建工作流"""
        from agent_os_kernel.core.workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        workflow = await engine.create_workflow("test-workflow")
        assert workflow is not None
        assert workflow.workflow_id is not None


class TestWorkflowNode:
    """测试工作流节点"""
    
    def test_node_exists(self):
        """测试节点存在"""
        from agent_os_kernel.core.workflow_engine import WorkflowNode
        assert WorkflowNode is not None
    
    def test_node_init(self):
        """测试节点初始化"""
        from agent_os_kernel.core.workflow_engine import WorkflowNode
        node = WorkflowNode(node_id="test", name="Test Node", task=lambda: None)
        assert node.node_id == "test"

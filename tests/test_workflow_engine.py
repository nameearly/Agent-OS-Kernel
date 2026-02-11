"""测试工作流引擎"""

import pytest


class TestWorkflowEngineExists:
    """测试工作流引擎存在"""
    
    def test_import(self):
        from agent_os_kernel.core.workflow_engine import WorkflowEngine
        assert WorkflowEngine is not None
    
    def test_node_import(self):
        from agent_os_kernel.core.workflow_engine import WorkflowNode
        assert WorkflowNode is not None

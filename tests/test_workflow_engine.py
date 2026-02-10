# -*- coding: utf-8 -*-
"""测试工作流引擎"""

import pytest
import asyncio
from agent_os_kernel.core.workflow_engine import (
    WorkflowEngine, Workflow, WorkflowNode, 
    WorkflowStatus, NodeStatus
)


class TestWorkflowEngine:
    """WorkflowEngine 测试类"""
    
    @pytest.fixture
    def engine(self):
        """创建测试引擎"""
        return WorkflowEngine(max_concurrent=5)
    
    @pytest.fixture
    async def workflow(self, engine):
        """创建测试工作流"""
        wf = await engine.create_workflow(
            name="Test Workflow",
            description="测试工作流"
        )
        yield wf
        # cleanup
    
    async def test_create_workflow(self, engine):
        """测试创建工作流"""
        wf = await engine.create_workflow(
            name="My Workflow",
            description="测试"
        )
        
        assert wf.workflow_id is not None
        assert wf.name == "My Workflow"
        assert wf.status == WorkflowStatus.CREATED
        assert len(wf.nodes) == 0
        
        await engine.shutdown()
    
    async def test_add_task(self, workflow):
        """测试添加任务"""
        async def sample_task(inputs, context):
            return {"result": "done"}
        
        await workflow.add_node(WorkflowNode(
            node_id="task1",
            name="Task 1",
            task=sample_task,
            dependencies=[]
        ))
        
        assert "task1" in workflow.nodes
        assert len(workflow.nodes) == 1
    
    async def test_workflow_execution(self, engine, workflow):
        """测试工作流执行"""
        results = []
        
        async def task_a(inputs, context):
            results.append("a")
            return {"value": 1}
        
        async def task_b(inputs, context):
            results.append("b")
            return {"value": 2}
        
        # A -> B
        await workflow.add_node(WorkflowNode(
            node_id="a",
            name="Task A",
            task=task_a,
            dependencies=[]
        ))
        
        await workflow.add_node(WorkflowNode(
            node_id="b",
            name="Task B",
            task=task_b,
            dependencies=["a"]
        ))
        
        result = await engine.execute(workflow)
        
        assert result["status"] == WorkflowStatus.COMPLETED
        assert len(result["completed"]) == 2
        assert len(result["failed"]) == 0
        assert "a" in result["completed"]
        assert "b" in result["completed"]
    
    async def test_parallel_execution(self, engine, workflow):
        """测试并行执行"""
        order = []
        
        async def task_x(inputs, context):
            order.append("x")
            return {"x": "done"}
        
        async def task_y(inputs, context):
            order.append("y")
            return {"y": "done"}
        
        async def task_z(inputs, context):
            order.append("z")
            return {"z": "done"}
        
        # X 和 Y 可以并行，然后 Z
        await workflow.add_node(WorkflowNode(
            node_id="x",
            name="Task X",
            task=task_x,
            dependencies=[]
        ))
        
        await workflow.add_node(WorkflowNode(
            node_id="y",
            name="Task Y",
            task=task_y,
            dependencies=[]
        ))
        
        await workflow.add_node(WorkflowNode(
            node_id="z",
            name="Task Z",
            task=task_z,
            dependencies=["x", "y"]
        ))
        
        result = await engine.execute(workflow)
        
        assert result["status"] == WorkflowStatus.COMPLETED
        assert order.index("z") > order.index("x")
        assert order.index("z") > order.index("y")


class TestWorkflowNode:
    """WorkflowNode 测试类"""
    
    def test_can_execute_no_dependencies(self):
        """测试无依赖节点"""
        node = WorkflowNode(
            node_id="test",
            name="Test",
            task=lambda x, y: x
        )
        
        assert node.can_execute(set())
    
    def test_can_execute_with_dependencies(self):
        """测试有依赖节点"""
        node = WorkflowNode(
            node_id="test",
            name="Test",
            task=lambda x, y: x,
            dependencies=["dep1", "dep2"]
        )
        
        assert not node.can_execute(set())
        assert not node.can_execute({"dep1"})
        assert node.can_execute({"dep1", "dep2"})
        assert node.can_execute({"dep1", "dep2", "extra"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

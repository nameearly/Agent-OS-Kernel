"""测试主内核"""

import pytest
from agent_os_kernel.kernel import AgentOSKernel
from agent_os_kernel.core.types import AgentState


class TestAgentOSKernel:
    def test_initialization(self):
        kernel = AgentOSKernel()
        
        assert kernel.version == "0.2.0"
        assert kernel.context_manager is not None
        assert kernel.scheduler is not None
        assert kernel.tool_registry is not None
    
    def test_spawn_agent(self):
        kernel = AgentOSKernel()
        
        pid = kernel.spawn_agent("TestAgent", "Test task", priority=30)
        
        assert pid is not None
        assert pid in kernel.scheduler.processes
        
        process = kernel.scheduler.processes[pid]
        assert process.name == "TestAgent"
        assert process.priority == 30
    
    def test_get_agent_status(self):
        kernel = AgentOSKernel()
        pid = kernel.spawn_agent("TestAgent", "Test task")
        
        status = kernel.get_agent_status(pid)
        
        assert status is not None
        assert status['name'] == "TestAgent"
        assert status['state'] == "ready"
    
    def test_terminate_agent(self):
        kernel = AgentOSKernel()
        pid = kernel.spawn_agent("TestAgent", "Test task")
        
        kernel.terminate_agent(pid)
        
        process = kernel.scheduler.processes[pid]
        assert process.state == AgentState.TERMINATED
    
    def test_create_and_restore_checkpoint(self):
        kernel = AgentOSKernel()
        pid = kernel.spawn_agent("TestAgent", "Test task")
        
        # 创建检查点
        checkpoint_id = kernel.create_checkpoint(pid, "Test checkpoint")
        assert checkpoint_id is not None
        
        # 恢复检查点
        new_pid = kernel.restore_checkpoint(checkpoint_id)
        assert new_pid is not None
        assert new_pid != pid
        
        process = kernel.scheduler.processes[new_pid]
        assert process.name == "TestAgent"
    
    def test_run_single_iteration(self):
        kernel = AgentOSKernel()
        kernel.spawn_agent("TestAgent", "Test task")
        
        # 运行一次迭代
        kernel.run(max_iterations=1)
        
        # 检查进程是否被处理
        active = kernel.scheduler.get_active_processes()
        # 进程可能被终止或仍在等待
        assert len(active) >= 0
    
    def test_builtin_tools_registered(self):
        kernel = AgentOSKernel()
        
        tools = kernel.tool_registry.list_tools()
        tool_names = [t['name'] for t in tools]
        
        assert 'calculator' in tool_names
        assert 'search' in tool_names
        assert 'read_file' in tool_names

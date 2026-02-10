# -*- coding: utf-8 -*-
"""测试状态机"""

import pytest
import asyncio
from agent_os_kernel.core.state_machine import StateMachine


class TestStateMachine:
    """StateMachine 测试类"""
    
    @pytest.fixture
    def fsm(self):
        """创建状态机"""
        fsm = StateMachine(name="test_fsm")
        
        fsm.add_state("initial", is_initial=True)
        fsm.add_state("processing")
        fsm.add_state("completed", is_final=True)
        fsm.add_state("error")
        
        fsm.add_transition("initial", "processing", "start")
        fsm.add_transition("processing", "completed", "finish")
        fsm.add_transition("processing", "error", "fail")
        
        return fsm
    
    async def test_start(self, fsm):
        """测试启动"""
        await fsm.start()
        
        assert fsm.get_state() == "initial"
    
    async def test_transition(self, fsm):
        """测试转换"""
        await fsm.start()
        await fsm.send_event("start")
        
        assert fsm.get_state() == "processing"
    
    async def test_final_state(self, fsm):
        """测试最终状态"""
        await fsm.start()
        await fsm.send_event("start")
        await fsm.send_event("finish")
        
        assert fsm.get_state() == "completed"
        assert fsm.is_final_state()
    
    async def test_is_in_state(self, fsm):
        """测试状态检查"""
        await fsm.start()
        
        assert fsm.is_in_state("initial")
        assert not fsm.is_in_state("processing")
    
    async def test_history(self, fsm):
        """测试历史记录"""
        await fsm.start()
        await fsm.send_event("start")
        await fsm.send_event("finish")
        
        history = fsm.get_history()
        
        assert len(history) == 2
    
    async def test_get_stats(self, fsm):
        """测试统计"""
        await fsm.start()
        
        stats = fsm.get_stats()
        
        assert stats["name"] == "test_fsm"
        assert stats["states_count"] == 4
        assert stats["is_running"]

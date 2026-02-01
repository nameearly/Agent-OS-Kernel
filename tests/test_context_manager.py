"""测试上下文管理器"""

import pytest
from agent_os_kernel.core.context_manager import (
    ContextManager,
    KVCacheOptimizer,
    SemanticImportanceCalculator,
)
from agent_os_kernel.core.types import ContextPage, PageStatus


class TestContextManager:
    def test_initialization(self):
        cm = ContextManager(max_context_tokens=1000)
        
        assert cm.max_context_tokens == 1000
        assert cm.current_usage == 0
        assert len(cm.pages_in_memory) == 0
    
    def test_allocate_page(self):
        cm = ContextManager(max_context_tokens=1000)
        
        page_id = cm.allocate_page("agent-1", "Hello world", importance=0.8)
        
        assert page_id is not None
        assert len(cm.pages_in_memory) == 1
        assert cm.current_usage > 0
    
    def test_access_page_in_memory(self):
        cm = ContextManager(max_context_tokens=1000)
        page_id = cm.allocate_page("agent-1", "Test content")
        
        page = cm.access_page(page_id)
        
        assert page is not None
        assert page.content == "Test content"
        assert page.access_count == 1
    
    def test_access_page_triggers_swap(self):
        # 创建一个小容量的上下文管理器
        cm = ContextManager(max_context_tokens=100)
        
        # 分配一些页面填满内存
        page_ids = []
        for i in range(5):
            pid = cm.allocate_page("agent-1", f"Content {i}" * 10, importance=0.1)
            page_ids.append(pid)
        
        # 现在应该有一些页面被换出
        assert len(cm.swapped_pages) > 0
        
        # 访问被换出的页面应该触发换入
        swapped_page_id = list(cm.swapped_pages.keys())[0]
        page = cm.access_page(swapped_page_id)
        
        assert page is not None
        assert page.status == PageStatus.IN_MEMORY
    
    def test_get_agent_context(self):
        cm = ContextManager(max_context_tokens=1000)
        
        cm.allocate_page("agent-1", "System prompt", importance=1.0, page_type="system")
        cm.allocate_page("agent-1", "Task description", importance=0.9, page_type="task")
        
        context = cm.get_agent_context("agent-1")
        
        assert "System prompt" in context
        assert "Task description" in context
    
    def test_release_agent_pages(self):
        cm = ContextManager(max_context_tokens=1000)
        
        for i in range(3):
            cm.allocate_page("agent-1", f"Content {i}")
        
        released = cm.release_agent_pages("agent-1")
        
        assert released == 3
        assert len(cm.pages_in_memory) == 0
        assert cm.current_usage == 0
    
    def test_get_stats(self):
        cm = ContextManager(max_context_tokens=1000)
        cm.allocate_page("agent-1", "Test")
        
        stats = cm.get_stats()
        
        assert 'current_usage' in stats
        assert 'max_tokens' in stats
        assert 'usage_percent' in stats


class TestKVCacheOptimizer:
    def test_optimize_layout(self):
        optimizer = KVCacheOptimizer()
        
        pages = [
            ContextPage(agent_pid="1", content="History", page_type="history"),
            ContextPage(agent_pid="1", content="System", page_type="system"),
            ContextPage(agent_pid="1", content="Task", page_type="task"),
        ]
        
        # 设置访问次数
        pages[0].access_count = 5
        pages[1].access_count = 1
        pages[2].access_count = 3
        
        optimized = optimizer.optimize_layout(pages)
        
        # 系统提示应该在前面
        assert optimized[0].page_type == "system"
        # 任务描述次之
        assert optimized[1].page_type == "task"


class TestSemanticImportanceCalculator:
    def test_heuristic_importance(self):
        calc = SemanticImportanceCalculator()
        
        system_page = ContextPage(agent_pid="1", content="System", page_type="system")
        task_page = ContextPage(agent_pid="1", content="Task", page_type="task")
        general_page = ContextPage(agent_pid="1", content="General", page_type="general")
        
        assert calc.calculate_importance(system_page, []) == 1.0
        assert calc.calculate_importance(task_page, []) == 0.9
        assert calc.calculate_importance(general_page, []) == 0.5

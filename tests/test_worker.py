"""测试Worker"""

import pytest


class TestWorkerPool:
    """测试Worker池"""
    
    def test_initialization(self):
        """测试初始化"""
        from agent_os_kernel.core.worker import WorkerPool
        pool = WorkerPool(max_workers=4)
        assert pool.max_workers == 4
    
    def test_get_stats(self):
        """测试获取统计"""
        from agent_os_kernel.core.worker import WorkerPool
        pool = WorkerPool()
        stats = pool.get_stats()
        assert stats is not None


class TestWorkerStatus:
    """测试Worker状态"""
    
    def test_exists(self):
        """测试状态存在"""
        from agent_os_kernel.core.worker import WorkerStatus
        assert WorkerStatus is not None

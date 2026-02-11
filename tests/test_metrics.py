"""测试指标收集器"""

import pytest


class TestMetricsCollector:
    """测试指标收集器"""
    
    def test_initialization(self):
        """测试初始化"""
        from agent_os_kernel.core.metrics import MetricsCollector
        collector = MetricsCollector()
        assert collector is not None
    
    def test_get_stats(self):
        """测试获取统计"""
        from agent_os_kernel.core.metrics import MetricsCollector
        collector = MetricsCollector()
        stats = collector.get_stats()
        assert stats is not None


class TestMetricType:
    """测试指标类型"""
    
    def test_exists(self):
        """测试存在"""
        from agent_os_kernel.core.metrics import MetricType
        assert MetricType is not None

"""测试指标收集器"""

import pytest
import time
from agent_os_kernel.core.metrics_collector import MetricsCollector, MetricType


class TestMetricsCollector:
    def test_counter(self):
        collector = MetricsCollector()
        collector.counter("requests", 1)
        collector.counter("requests", 2)
        assert collector.get_counter("requests") == 3
    
    def test_gauge(self):
        collector = MetricsCollector()
        collector.gauge("memory", 100)
        collector.gauge("memory", 200)
        assert collector.get_gauge("memory") == 200
    
    def test_histogram(self):
        collector = MetricsCollector()
        collector.histogram("latency", 10)
        collector.histogram("latency", 20)
        collector.histogram("latency", 30)
        p50 = collector.get_histogram_percentile("latency", 50)
        assert p50 is not None
    
    def test_get_all(self):
        collector = MetricsCollector()
        collector.counter("test", 1)
        collector.gauge("value", 100)
        metrics = collector.get_all()
        assert "counters" in metrics
        assert "gauges" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

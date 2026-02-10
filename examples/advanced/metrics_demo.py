# -*- coding: utf-8 -*-
"""指标收集器演示"""

import asyncio
from agent_os_kernel.core.metrics_collector import MetricsCollector, get_metrics_collector


async def main():
    print("="*60)
    print("Metrics Collector Demo")
    print("="*60)
    
    # 创建收集器
    collector = MetricsCollector(flush_interval=10, enable_console=True)
    collector.start()
    
    # 记录指标
    print("\n📊 记录指标...")
    collector.counter("http_requests_total", 1, {"method": "GET"})
    collector.counter("http_requests_total", 1, {"method": "POST"})
    collector.counter("http_requests_total", 2, {"method": "PUT"})
    
    collector.gauge("active_connections", 150)
    collector.gauge("memory_usage_mb", 512)
    
    # 模拟延迟
    import time
    start = time.time()
    # 模拟工作
    time.sleep(0.1)
    collector.timer("request_latency", time.time() - start, {"endpoint": "/api/users"})
    
    print("\n✅ 指标已记录")
    
    # 获取所有指标
    metrics = collector.get_all()
    print(f"\n📈 计数器: {metrics['counters']}")
    print(f"📈 仪表: {metrics['gauges']}")
    
    # 导出 Prometheus 格式
    prometheus_output = collector.export_prometheus()
    print(f"\n📊 Prometheus 格式输出:")
    print(prometheus_output[:500])
    
    collector.stop()
    print("\n✅ 演示完成")


if __name__ == "__main__":
    asyncio.run(main())

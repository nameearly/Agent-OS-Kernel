# -*- coding: utf-8 -*-
"""批处理演示"""

import asyncio
from agent_os_kernel.core.batch_processor import BatchProcessor, AggregationType


async def main():
    print("="*60)
    print("Batch Processing Demo")
    print("="*60)
    
    # 创建批处理器
    processor = BatchProcessor(
        batch_size=10,
        timeout_ms=500,
        max_concurrent=3,
        aggregation={
            "value": AggregationType.SUM,
            "count": AggregationType.COUNT,
            "score": AggregationType.AVG
        }
    )
    await processor.start()
    
    print("\n📦 添加数据...")
    
    # 添加数据
    for i in range(25):
        await processor.add(
            {"value": i * 10, "score": 100 - i},
            batch_key="metrics"
        )
        await asyncio.sleep(0.05)
    
    await asyncio.sleep(1)
    
    # 统计
    stats = processor.get_stats()
    print(f"\n📊 批处理统计: {stats}")
    
    await processor.stop()
    print("\n✅ 演示完成")


if __name__ == "__main__":
    asyncio.run(main())

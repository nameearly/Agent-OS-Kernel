# -*- coding: utf-8 -*-
"""管道处理演示"""

import asyncio
from agent_os_kernel.core.pipeline import Pipeline


async def main():
    print("="*60)
    print("Pipeline Demo")
    print("="*60)
    
    # 创建管道
    pipeline = Pipeline(
        name="data_processing",
        max_concurrent=5
    )
    
    # 添加处理阶段
    @pipeline.stage("extract")
    def extract(data, results):
        print(f"📤 Extract: {data}")
        return {"raw": data}
    
    @pipeline.stage("transform")
    def transform(data, results):
        print(f"🔄 Transform: {data}")
        return {"processed": data.get("raw", "").upper()}
    
    @pipeline.stage("validate")
    def validate(data, results):
        print(f"✅ Validate: {data}")
        return {"valid": True}
    
    @pipeline.stage("load")
    def load(data, results):
        print(f"💾 Load: {data}")
        return {"loaded": True}
    
    # 注册回调
    pipeline.on_complete(lambda item: print(f"✅ Completed: {item.item_id}"))
    
    print("\n📦 处理数据...")
    
    # 处理单个数据
    result = await pipeline.process("hello world")
    print(f"\n📋 结果:")
    print(f"  阶段结果: {result.results}")
    print(f"  完成时间: {result.completed_at}")
    
    # 批量处理
    print("\n📦 批量处理...")
    batch_results = await pipeline.process_batch([
        "item1", "item2", "item3"
    ])
    
    print(f"\n📊 管道统计:")
    stats = pipeline.get_stats()
    print(f"  总项目: {stats['total_items']}")
    print(f"  完成: {stats['completed']}")
    print(f"  阶段数: {stats['stages']}")
    
    print("\n✅ 演示完成")


if __name__ == "__main__":
    asyncio.run(main())

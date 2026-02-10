# -*- coding: utf-8 -*-
"""优化调度器演示 - MemScheduler 理念"""

import asyncio
from agent_os_kernel.core.optimized_scheduler import (
    OptimizedScheduler, Priority, TaskStatus
)


async def main():
    print("="*60)
    print("Optimized Scheduler Demo (MemScheduler)")
    print("="*60)
    
    # 创建调度器
    scheduler = OptimizedScheduler(
        max_concurrent=3,
        default_timeout=30.0,
        quota_managed=True
    )
    
    results = []
    
    async def process_task(task_id: int):
        """处理任务"""
        await asyncio.sleep(0.1)
        return f"Task-{task_id} completed"
    
    print("\n📦 提交任务...")
    
    # 提交不同优先级的任务
    priorities = [
        (Priority.CRITICAL, "Critical-1"),
        (Priority.CRITICAL, "Critical-2"),
        (Priority.HIGH, "High-1"),
        (Priority.NORMAL, "Normal-1"),
        (Priority.NORMAL, "Normal-2"),
        (Priority.LOW, "Low-1"),
        (Priority.BACKGROUND, "Background-1"),
    ]
    
    task_ids = []
    for i, (priority, name) in enumerate(priorities):
        task_id = await scheduler.schedule(
            name=name,
            func=process_task,
            task_id=i,
            priority=priority
        )
        task_ids.append(task_id)
        print(f"  📤 {name} (Priority: {priority.name})")
    
    print("\n⏳ 等待任务完成...")
    await asyncio.sleep(1)
    
    print(f"\n📊 调度器统计:")
    stats = scheduler.get_stats()
    for k, v in stats.items():
        if k != "quotas":
            print(f"  {k}: {v}")
    
    print("\n📋 配额状态:")
    for quota_name, quota in stats.get("quotas", {}).items():
        print(f"  {quota_name}: {quota.get('current_tasks')}/{quota.get('max_tasks')}")
    
    # 获取结果
    print(f"\n✅ 任务结果:")
    for task_id in task_ids[:5]:
        result = await scheduler.get_result(task_id)
        print(f"  {task_id[:8]}: {result}")
    
    print("\n" + "="*60)
    print("✅ 演示完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

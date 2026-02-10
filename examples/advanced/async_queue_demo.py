# -*- coding: utf-8 -*-
"""异步队列演示"""

import asyncio
from agent_os_kernel.core.async_queue import AsyncQueue, QueueType


async def handler(message):
    """消息处理器"""
    print(f"📨 收到消息: {message.topic} -> {message.payload}")


async def main():
    print("="*60)
    print("Async Queue Demo")
    print("="*60)
    
    # 创建异步队列
    queue = AsyncQueue(
        name="events",
        queue_type=QueueType.PRIORITY,
        max_size=1000
    )
    await queue.start()
    
    print("\n📤 发布消息...")
    
    # 发布消息
    for i in range(5):
        await queue.publish(
            topic="user.events",
            payload={"event_id": i, "data": f"event_{i}"},
            priority=i % 3 + 1
        )
    
    # 订阅
    await queue.subscribe("user.events", handler)
    
    await asyncio.sleep(0.5)
    
    # 统计
    stats = queue.get_stats()
    print(f"\n📊 队列统计: {stats}")
    
    print(f"\n📋 主题列表: {queue.list_topics()}")
    
    await queue.stop()
    print("\n✅ 演示完成")


if __name__ == "__main__":
    asyncio.run(main())

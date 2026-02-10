# -*- coding: utf-8 -*-
"""事件总线演示

演示发布/订阅模式的事件驱动架构。
"""

import asyncio
from agent_os_kernel.core.event_bus import EventBus, Event, EventPriority


async def handle_agent_start(event: Event):
    """处理 Agent 启动事件"""
    print(f"🤖 Agent 启动: {event.payload.get('agent_id')}")


async def handle_agent_message(event: Event):
    """处理消息事件"""
    print(f"💬 消息: {event.payload.get('content', '')[:50]}...")


async def handle_error(event: Event):
    """处理错误事件"""
    print(f"❌ 错误: {event.payload.get('error')}")


async def main():
    """主函数"""
    print("="*60)
    print("Event Bus Demo")
    print("="*60)
    
    # 创建事件总线
    bus = EventBus(max_queue_size=100)
    await bus.initialize()
    
    # 订阅事件
    bus.subscribe("agent.started", handle_agent_start)
    bus.subscribe("agent.message.*", handle_agent_message)
    bus.subscribe("agent.error", handle_error, priority=EventPriority.HIGH)
    
    print("\n📬 订阅者已注册")
    
    # 发布事件
    print("\n📨 发布事件...")
    
    # Agent 启动
    await bus.publish(
        event_type="agent.started",
        payload={"agent_id": "agent-001", "name": "Assistant"},
        source="kernel"
    )
    
    # 多条消息
    for i in range(3):
        await bus.publish(
            event_type=f"agent.message.{i % 2 + 1}",
            payload={"content": f"这是第{i+1}条消息", "from": "user"},
            source="agent-001"
        )
    
    # 错误事件
    await bus.publish(
        event_type="agent.error",
        payload={"error": "连接超时", "agent_id": "agent-001"},
        priority=EventPriority.CRITICAL
    )
    
    # 等待处理
    await asyncio.sleep(0.5)
    
    # 获取统计
    stats = bus.get_stats()
    print(f"\n📊 事件统计:")
    print(f"   发布: {stats['published']}")
    print(f"   投递: {stats['delivered']}")
    print(f"   失败: {stats['failed']}")
    print(f"   订阅者: {stats['subscribers']}")
    
    # 关闭
    await bus.shutdown()
    print("\n✅ 演示完成")


if __name__ == "__main__":
    asyncio.run(main())

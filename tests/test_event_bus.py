# -*- coding: utf-8 -*-
"""测试事件总线"""

import pytest
import asyncio
from agent_os_kernel.core.event_bus import (
    EventBus, Event, EventPriority, Subscription
)


class TestEventBus:
    """EventBus 测试类"""
    
    @pytest.fixture
    def bus(self):
        """创建测试事件总线"""
        bus = EventBus(max_queue_size=100)
        return bus
    
    @pytest.fixture
    async def initialized_bus(self, bus):
        """创建并初始化事件总线"""
        await bus.initialize()
        yield bus
        await bus.shutdown()
    
    def test_create_bus(self, bus):
        """测试创建事件总线"""
        assert bus._running is False
        assert bus._event_queue.qsize() == 0
    
    @pytest.mark.asyncio
    async def test_publish_event(self, initialized_bus):
        """测试发布事件"""
        event_id = await initialized_bus.publish(
            event_type="test.event",
            payload={"key": "value"}
        )
        
        assert event_id is not None
        assert len(event_id) > 0
    
    @pytest.mark.asyncio
    async def test_subscribe_handler(self, initialized_bus):
        """测试订阅处理器"""
        received = []
        
        async def handler(event):
            received.append(event)
        
        sub_id = initialized_bus.subscribe("test.message", handler)
        
        assert sub_id is not None
        
        await initialized_bus.publish("test.message", {"text": "hello"})
        await asyncio.sleep(0.1)
        
        assert len(received) == 1
        assert received[0].payload["text"] == "hello"
    
    @pytest.mark.asyncio
    async def test_wildcard_subscription(self, initialized_bus):
        """测试通配符订阅"""
        received = []
        
        async def handler(event):
            received.append(event)
        
        # 订阅所有 agent 事件
        initialized_bus.subscribe("agent.*", handler)
        
        await initialized_bus.publish("agent.start", {"id": 1})
        await initialized_bus.publish("agent.stop", {"id": 2})
        await asyncio.sleep(0.1)
        
        assert len(received) == 2
    
    @pytest.mark.asyncio
    async def test_priority_order(self, initialized_bus):
        """测试优先级顺序"""
        order = []
        
        async def low_priority(event):
            order.append("low")
        
        async def high_priority(event):
            order.append("high")
        
        initialized_bus.subscribe("prio.test", low_priority, priority=EventPriority.LOW)
        initialized_bus.subscribe("prio.test", high_priority, priority=EventPriority.HIGH)
        
        await initialized_bus.publish("prio.test", {})
        await asyncio.sleep(0.1)
        
        assert order == ["high", "low"]
    
    @pytest.mark.asyncio
    async def test_unsubscribe(self, initialized_bus):
        """测试取消订阅"""
        received = []
        
        async def handler(event):
            received.append(event)
        
        sub_id = initialized_bus.subscribe("unsub.test", handler)
        initialized_bus.unsubscribe(sub_id)
        
        await initialized_bus.publish("unsub.test", {})
        await asyncio.sleep(0.1)
        
        assert len(received) == 0
    
    @pytest.mark.asyncio
    async def test_stats(self, initialized_bus):
        """测试统计"""
        for i in range(3):
            await initialized_bus.publish("stats.test", {"i": i})
        
        stats = initialized_bus.get_stats()
        
        assert stats["published"] == 3
        assert stats["subscribers"] == 0  # 还没有订阅者


class TestEvent:
    """Event 测试类"""
    
    def test_create_event(self):
        """测试创建事件"""
        event = Event(
            event_id="test-001",
            event_type="test.type",
            payload={"key": "value"}
        )
        
        assert event.event_id == "test-001"
        assert event.event_type == "test.type"
        assert event.payload["key"] == "value"
        assert event.priority == EventPriority.NORMAL
    
    def test_event_to_dict(self):
        """测试事件序列化"""
        event = Event(
            event_id="test-001",
            event_type="test.type",
            payload={"key": "value"},
            source="test"
        )
        
        data = event.to_dict()
        
        assert data["event_id"] == "test-001"
        assert data["event_type"] == "test.type"
        assert data["source"] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

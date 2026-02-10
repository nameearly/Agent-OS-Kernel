# -*- coding: utf-8 -*-
"""测试异步队列"""

import pytest
import asyncio
from agent_os_kernel.core.async_queue import AsyncQueue, QueueType


class TestAsyncQueue:
    """AsyncQueue 测试类"""
    
    @pytest.fixture
    def queue(self):
        """创建异步队列"""
        return AsyncQueue(name="test", queue_type=QueueType.FIFO)
    
    async def test_publish_message(self, queue):
        """测试发布消息"""
        await queue.start()
        
        msg_id = await queue.publish(
            topic="test.topic",
            payload={"key": "value"},
            priority=5
        )
        
        assert msg_id is not None
        assert len(msg_id) > 0
        
        stats = queue.get_stats()
        assert stats["published"] == 1
        
        await queue.stop()
    
    async def test_subscribe(self, queue):
        """测试订阅"""
        await queue.start()
        
        results = []
        
        async def handler(msg):
            results.append(msg)
        
        await queue.subscribe("test.topic", handler)
        await queue.publish("test.topic", {"data": "test"})
        
        await asyncio.sleep(0.2)
        
        assert len(results) == 1
        
        await queue.stop()
    
    async def test_get_message(self, queue):
        """测试获取消息"""
        await queue.start()
        
        await queue.publish("test.topic", {"key": "value"})
        msg = await queue.get("test.topic", timeout=1.0)
        
        assert msg is not None
        assert msg.topic == "test.topic"
        
        await queue.stop()
    
    async def test_list_topics(self, queue):
        """测试列出主题"""
        await queue.start()
        
        await queue.publish("topic1", {"data": "test1"})
        await queue.publish("topic2", {"data": "test2"})
        
        topics = queue.list_topics()
        
        assert "topic1" in topics
        assert "topic2" in topics
        
        await queue.stop()

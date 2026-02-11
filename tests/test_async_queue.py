"""测试异步队列"""

import pytest


class TestAsyncQueue:
    """测试异步队列"""
    
    def test_queue_exists(self):
        """测试队列存在"""
        from agent_os_kernel.core.async_queue import AsyncQueue
        assert AsyncQueue is not None
    
    def test_message_exists(self):
        """测试消息存在"""
        from agent_os_kernel.core.async_queue import Message
        assert Message is not None
    
    def test_status_exists(self):
        """测试状态存在"""
        from agent_os_kernel.core.async_queue import MessageStatus
        assert MessageStatus is not None


class TestQueueType:
    """测试队列类型"""
    
    def test_queue_type_exists(self):
        """测试队列类型存在"""
        from agent_os_kernel.core.async_queue import QueueType
        assert QueueType is not None

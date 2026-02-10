# -*- coding: utf-8 -*-
"""Event Bus - 事件总线

基于发布/订阅模式的事件驱动架构组件。
"""

import asyncio
import logging
from typing import Dict, List, Callable, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """事件优先级"""
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 100


@dataclass
class Event:
    """事件"""
    event_id: str
    event_type: str
    payload: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata
        }


@dataclass
class Subscription:
    """订阅"""
    subscription_id: str
    event_type: str
    handler: Callable
    priority: EventPriority = EventPriority.NORMAL
    filter: Optional[Callable[[Event], bool]] = None
    max_events: Optional[int] = None
    received_count: int = 0
    active: bool = True


class EventBus:
    """事件总线"""
    
    def __init__(
        self,
        max_queue_size: int = 10000,
        enable_audit: bool = True
    ):
        """
        初始化事件总线
        
        Args:
            max_queue_size: 最大队列大小
            enable_audit: 是否启用审计
        """
        self.max_queue_size = max_queue_size
        self.enable_audit = enable_audit
        
        self._subscriptions: Dict[str, List[Subscription]] = defaultdict(list)
        self._wildcards: List[Subscription] = []
        self._event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        
        self._handlers: Dict[str, Set[Callable]] = defaultdict(set)
        
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        
        self._stats = {
            "events_published": 0,
            "events_delivered": 0,
            "events_failed": 0,
            "subscribers": 0
        }
        
        logger.info(f"EventBus initialized: max_queue={max_queue_size}")
    
    async def initialize(self):
        """初始化事件总线"""
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._process_events())
            logger.info("EventBus started")
    
    async def shutdown(self):
        """关闭事件总线"""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("EventBus shutdown")
    
    def subscribe(
        self,
        event_type: str,
        handler: Callable,
        priority: EventPriority = EventPriority.NORMAL,
        filter: Optional[Callable[[Event], bool]] = None
    ) -> str:
        """
        订阅事件
        
        Args:
            event_type: 事件类型 (支持通配符如 "agent.*")
            handler: 处理函数
            priority: 优先级
            filter: 过滤函数
            
        Returns:
            订阅 ID
        """
        if "*" in event_type or "?" in event_type:
            subscription = Subscription(
                subscription_id=str(uuid.uuid4()),
                event_type=event_type,
                handler=handler,
                priority=priority,
                filter=filter
            )
            self._wildcards.append(subscription)
        else:
            subscription = Subscription(
                subscription_id=str(uuid.uuid4()),
                event_type=event_type,
                handler=handler,
                priority=priority,
                filter=filter
            )
            self._subscriptions[event_type].append(subscription)
        
        self._stats["subscribers"] += 1
        
        logger.debug(f"Subscribed to {event_type}: {subscription.subscription_id}")
        return subscription.subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅"""
        # 检查精确匹配
        for event_type, subs in self._subscriptions.items():
            for sub in subs:
                if sub.subscription_id == subscription_id:
                    subs.remove(sub)
                    self._stats["subscribers"] -= 1
                    return True
        
        # 检查通配符
        for sub in self._wildcards:
            if sub.subscription_id == subscription_id:
                self._wildcards.remove(sub)
                self._stats["subscribers"] -= 1
                return True
        
        return False
    
    async def publish(
        self,
        event_type: str,
        payload: Dict = None,
        priority: EventPriority = EventPriority.NORMAL,
        source: Optional[str] = None,
        correlation_id: Optional[str] = None,
        blocking: bool = False
    ) -> str:
        """
        发布事件
        
        Args:
            event_type: 事件类型
            payload: 事件数据
            priority: 优先级
            source: 来源
            correlation_id: 关联 ID
            blocking: 是否阻塞
            
        Returns:
            事件 ID
        """
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            payload=payload or {},
            priority=priority,
            source=source,
            correlation_id=correlation_id
        )
        
        self._stats["events_published"] += 1
        
        if blocking:
            await self._dispatch_event(event)
        else:
            try:
                self._event_queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning(f"Event queue full, dropping event: {event.event_id}")
                self._stats["events_failed"] += 1
        
        return event.event_id
    
    async def _process_events(self):
        """处理事件队列"""
        while self._running:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )
                await self._dispatch_event(event)
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processing error: {e}")
                self._stats["events_failed"] += 1
    
    async def _dispatch_event(self, event: Event):
        """分发事件"""
        # 获取精确匹配的订阅者
        subscribers = self._subscriptions.get(event.event_type, [])
        
        # 获取通配符匹配的订阅者
        for sub in self._wildcards:
            if self._match_wildcard(sub.event_type, event.event_type):
                subscribers.append(sub)
        
        # 按优先级排序
        subscribers.sort(key=lambda x: x.priority.value, reverse=True)
        
        # 并发处理
        tasks = []
        for sub in subscribers:
            if sub.active and (not sub.filter or sub.filter(event)):
                tasks.append(self._handle_subscription(event, sub))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self._stats["events_delivered"] += len(tasks)
    
    async def _handle_subscription(self, event: Event, sub: Subscription):
        """处理单个订阅"""
        try:
            if asyncio.iscoroutinefunction(sub.handler):
                await sub.handler(event)
            else:
                sub.handler(event)
            
            sub.received_count += 1
            
        except Exception as e:
            logger.error(f"Handler error for {sub.subscription_id}: {e}")
            self._stats["events_failed"] += 1
    
    def _match_wildcard(self, pattern: str, event_type: str) -> bool:
        """通配符匹配"""
        import fnmatch
        return fnmatch.fnmatch(event_type, pattern)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "published": self._stats["events_published"],
            "delivered": self._stats["events_delivered"],
            "failed": self._stats["events_failed"],
            "subscribers": self._stats["subscribers"],
            "queue_size": self._event_queue.qsize()
        }


# 便捷函数
def create_event_bus(**kwargs) -> EventBus:
    """创建事件总线"""
    return EventBus(**kwargs)

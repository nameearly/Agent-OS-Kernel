# -*- coding: utf-8 -*-
"""Batch Processor - 批处理器

支持批量处理、窗口操作、聚合计算。
"""

import asyncio
import logging
from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque
import time

logger = logging.getLogger(__name__)


class AggregationType(Enum):
    """聚合类型"""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    LAST = "last"
    FIRST = "first"


@dataclass
class Batch:
    """批次"""
    batch_id: str
    items: List[Any]
    created_at: datetime
    processed_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)


class BatchProcessor:
    """批处理器"""
    
    def __init__(
        self,
        batch_size: int = 100,
        timeout_ms: int = 1000,
        max_concurrent: int = 5,
        aggregation: Optional[Dict[str, AggregationType]] = None
    ):
        """
        初始化批处理器
        
        Args:
            batch_size: 批次大小
            timeout_ms: 超时时间（毫秒）
            max_concurrent: 最大并发数
            aggregation: 聚合配置
        """
        self.batch_size = batch_size
        self.timeout_ms = timeout_ms
        self.max_concurrent = max_concurrent
        self.aggregation = aggregation or {}
        
        self._queue: deque = deque()
        self._batches: Dict[str, Batch] = {}
        self._results: Dict[str, Any] = {}
        self._processing = 0
        self._lock = asyncio.Lock()
        self._callbacks: List[Callable] = []
        
        self._processor_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info(f"BatchProcessor initialized: size={batch_size}, timeout={timeout_ms}ms")
    
    async def start(self):
        """启动批处理器"""
        self._running = True
        self._processor_task = asyncio.create_task(self._process_loop())
        logger.info("BatchProcessor started")
    
    async def stop(self):
        """停止批处理器"""
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
        logger.info("BatchProcessor stopped")
    
    async def add(self, item: Any, batch_key: str = "default") -> str:
        """
        添加项目到批次
        
        Args:
            item: 项目
            batch_key: 批次键
            
        Returns:
            批次 ID
        """
        batch_id = f"{batch_key}_{int(time.time() * 1000)}"
        
        async with self._lock:
            if batch_key not in self._batches:
                self._batches[batch_key] = Batch(
                    batch_id=batch_id,
                    items=[],
                    created_at=datetime.utcnow()
                )
            
            batch = self._batches[batch_key]
            batch.items.append(item)
            
            if len(batch.items) >= self.batch_size:
                await self._process_batch(batch_key)
        
        return batch_id
    
    async def add_batch(self, items: List[Any], batch_key: str = "default") -> str:
        """批量添加"""
        batch_id = f"{batch_key}_batch_{int(time.time() * 1000)}"
        
        batch = Batch(
            batch_id=batch_id,
            items=items,
            created_at=datetime.utcnow()
        )
        
        async with self._lock:
            self._batches[batch_key] = batch
        
        await self._process_batch(batch_key)
        
        return batch_id
    
    async def _process_loop(self):
        """处理循环"""
        while self._running:
            try:
                await asyncio.sleep(self.timeout_ms / 1000.0)
                
                async with self._lock:
                    now = datetime.utcnow()
                    expired_keys = []
                    
                    for key, batch in self._batches.items():
                        if (now - batch.created_at).total_seconds() * 1000 >= self.timeout_ms:
                            await self._process_batch(key)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Process loop error: {e}")
    
    async def _process_batch(self, batch_key: str):
        """处理批次"""
        async with self._lock:
            if batch_key not in self._batches:
                return
            
            batch = self._batches[batch_key]
            
            if not batch.items:
                del self._batches[batch_key]
                return
            
            if self._processing >= self.max_concurrent:
                return
            
            self._processing += 1
        
        try:
            # 执行聚合
            result = await self._aggregate(batch.items)
            
            # 回调
            for callback in self._callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(batch_key, batch.items, result)
                    else:
                        callback(batch_key, batch.items, result)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
            
            self._results[batch.batch_id] = result
            batch.processed_at = datetime.utcnow()
            
            logger.debug(f"Processed batch: {batch_key}, size={len(batch.items)}")
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
        finally:
            async with self._lock:
                self._processing -= 1
                self._batches.pop(batch_key, None)
    
    async def _aggregate(self, items: List[Any]) -> Any:
        """聚合数据"""
        if not self.aggregation:
            return items
        
        result = {}
        
        for field_name, agg_type in self.aggregation.items():
            values = [item.get(field_name) for item in items if isinstance(item, dict) and field_name in item]
            
            if not values:
                continue
            
            if agg_type == AggregationType.SUM:
                result[field_name] = sum(values)
            elif agg_type == AggregationType.AVG:
                result[field_name] = sum(values) / len(values)
            elif agg_type == AggregationType.MIN:
                result[field_name] = min(values)
            elif agg_type == AggregationType.MAX:
                result[field_name] = max(values)
            elif agg_type == AggregationType.COUNT:
                result[field_name] = len(values)
            elif agg_type == AggregationType.LAST:
                result[field_name] = values[-1]
            elif agg_type == AggregationType.FIRST:
                result[field_name] = values[0]
        
        result["_items"] = items
        return result
    
    def on_processed(self, callback: Callable):
        """注册处理完成回调"""
        self._callbacks.append(callback)
    
    async def get_result(self, batch_id: str) -> Optional[Any]:
        """获取处理结果"""
        return self._results.get(batch_id)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "pending_batches": len(self._batches),
            "processing": self._processing,
            "completed_batches": len(self._results),
            "queue_size": len(self._queue)
        }


# 滑动窗口处理器
class SlidingWindowProcessor:
    """滑动窗口处理器"""
    
    def __init__(self, window_size: int = 100, slide_size: int = 10):
        """
        初始化滑动窗口
        
        Args:
            window_size: 窗口大小
            slide_size: 滑动大小
        """
        self.window_size = window_size
        self.slide_size = slide_size
        self._window: deque = deque(maxlen=window_size)
        self._results: deque = deque(maxlen=1000)
    
    async def add(self, item: Any):
        """添加数据点"""
        self._window.append(item)
        
        if len(self._window) >= self.window_size:
            await self._compute()
    
    async def _compute(self):
        """计算窗口统计"""
        items = list(self._window)
        
        result = {
            "count": len(items),
            "sum": sum(items) if all(isinstance(x, (int, float)) for x in items) else None,
            "avg": sum(items) / len(items) if all(isinstance(x, (int, float)) for x in items) else None,
            "min": min(items) if all(isinstance(x, (int, float)) for x in items) else None,
            "max": max(items) if all(isinstance(x, (int, float)) for x in items) else None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self._results.append(result)
    
    def get_latest(self) -> Optional[Dict]:
        """获取最新统计"""
        return self._results[-1] if self._results else None
    
    def get_history(self) -> List[Dict]:
        """获取历史统计"""
        return list(self._results)

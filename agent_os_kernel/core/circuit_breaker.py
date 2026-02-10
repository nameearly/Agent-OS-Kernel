# -*- coding: utf-8 -*-
"""Circuit Breaker - 熔断器

保护系统免受级联故障的影响。
"""

import asyncio
import logging
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """熔断状态"""
    CLOSED = "closed"      # 正常
    OPEN = "open"          # 断开
    HALF_OPEN = "half_open"  # 半开


@dataclass
class CircuitConfig:
    """熔断配置"""
    failure_threshold: int = 5       # 失败次数阈值
    success_threshold: int = 3       # 成功次数阈值 (半开状态)
    timeout_seconds: float = 30.0    # 超时时间
    expected_exception: type = Exception  # 预期的异常类型
    volume_threshold: int = 10       # 最小请求量
    window_seconds: float = 60.0     # 时间窗口


class CircuitBreaker:
    """熔断器"""
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitConfig] = None
    ):
        """
        初始化熔断器
        
        Args:
            name: 熔断器名称
            config: 配置
        """
        self.name = name
        self.config = config or CircuitConfig()
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._total_count = 0
        self._failure_window: Dict[datetime, int] = {}
        
        self._last_failure: Optional[datetime] = None
        self._opened_at: Optional[datetime] = None
        
        self._lock = asyncio.Lock()
        
        logger.info(f"CircuitBreaker '{name}' initialized")
    
    @property
    def state(self) -> CircuitState:
        """获取状态"""
        if self._state == CircuitState.OPEN:
            if self._should_attempt_reset():
                return CircuitState.HALF_OPEN
        return self._state
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该重试"""
        if self._opened_at is None:
            return False
        elapsed = (datetime.utcnow() - self._opened_at).total_seconds()
        return elapsed >= self.config.timeout_seconds
    
    async def call(
        self,
        func: Callable,
        *args,
        fallback: Optional[Callable] = None,
        **kwargs
    ):
        """
        调用受保护的函数
        
        Args:
            func: 要保护的函数
            *args: 位置参数
            fallback: 降级函数
            **kwargs: 关键字参数
            
        Returns:
            函数返回值
        """
        async with self._lock:
            current_state = self.state
            
            if current_state == CircuitState.OPEN:
                if fallback:
                    return await fallback()
                raise CircuitOpenError(f"Circuit '{self.name}' is open")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await self._on_success()
            return result
            
        except self.config.expected_exception as e:
            await self._on_failure()
            if fallback:
                return await fallback()
            raise
    
    async def _on_success(self):
        """成功处理"""
        async with self._lock:
            self._total_count += 1
            
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    logger.info(f"Circuit '{self.name}' closed")
            
            self._last_failure = None
    
    async def _on_failure(self):
        """失败处理"""
        async with self._lock:
            self._total_count += 1
            self._failure_count += 1
            self._last_failure = datetime.utcnow()
            
            now = datetime.utcnow()
            self._failure_window[now] = self._failure_window.get(now, 0) + 1
            
            # 清理旧窗口
            cutoff = now - timedelta(seconds=self.config.window_seconds)
            self._failure_window = {
                k: v for k, v in self._failure_window.items() if k > cutoff
            }
            
            # 计算窗口内的失败率
            window_failures = sum(self._failure_window.values())
            window_total = min(self._total_count, self.config.volume_threshold)
            
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._opened_at = datetime.utcnow()
                logger.warning(f"Circuit '{self.name}' opened after failure in half-open")
            
            elif self._failure_count >= self.config.failure_threshold:
                self._state = CircuitState.OPEN
                self._opened_at = datetime.utcnow()
                logger.warning(f"Circuit '{self.name}' opened: {self._failure_count} failures")
    
    def get_stats(self) -> dict:
        """获取统计"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "total_count": self._total_count,
            "failure_rate": self._failure_count / max(1, self._total_count),
            "last_failure": self._last_failure.isoformat() if self._last_failure else None,
            "opened_at": self._opened_at.isoformat() if self._opened_at else None
        }
    
    def reset(self):
        """重置熔断器"""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._total_count = 0
        self._failure_window.clear()
        self._last_failure = None
        self._opened_at = None
        logger.info(f"Circuit '{self.name}' reset")


class CircuitOpenError(Exception):
    """熔断器打开异常"""
    pass


# 熔断器管理器
class CircuitBreakerManager:
    """熔断器管理器"""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    def get_or_create(
        self,
        name: str,
        config: Optional[CircuitConfig] = None
    ) -> CircuitBreaker:
        """获取或创建熔断器"""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name, config)
        return self._breakers[name]
    
    def get(self, name: str) -> Optional[CircuitBreaker]:
        """获取熔断器"""
        return self._breakers.get(name)
    
    def list_all(self) -> list:
        """列出所有熔断器"""
        return [
            {
                "name": name,
                **breaker.get_stats()
            }
            for name, breaker in self._breakers.items()
        ]
    
    def reset_all(self):
        """重置所有"""
        for breaker in self._breakers.values():
            breaker.reset()
    
    def remove(self, name: str) -> bool:
        """移除熔断器"""
        if name in self._breakers:
            del self._breakers[name]
            return True
        return False


# 全局管理器
_manager: Optional[CircuitBreakerManager] = None


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """获取全局熔断器管理器"""
    global _manager
    if _manager is None:
        _manager = CircuitBreakerManager()
    return _manager

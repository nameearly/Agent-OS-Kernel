# -*- coding: utf-8 -*-
"""
Exceptions - 异常定义

标准化的异常层次结构，便于错误处理和调试
"""


class AgentOSKernelError(Exception):
    """基础异常"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def __str__(self):
        return self.message


class AgentError(AgentOSKernelError):
    """Agent 相关异常"""
    pass


class AgentNotFoundError(AgentError):
    """Agent 未找到"""
    pass


class AgentCreationError(AgentError):
    """Agent 创建失败"""
    pass


class AgentExecutionError(AgentError):
    """Agent 执行失败"""
    pass


class AgentTimeoutError(AgentError):
    """Agent 超时"""
    pass


class ContextError(AgentOSKernelError):
    """上下文相关异常"""
    pass


class ContextOverflowError(ContextError):
    """上下文溢出"""
    pass


class ContextNotFoundError(ContextError):
    """上下文未找到"""
    pass


class PageFaultError(ContextError):
    """缺页异常"""
    pass


class StorageError(AgentOSKernelError):
    """存储相关异常"""
    pass


class StorageConnectionError(StorageError):
    """存储连接失败"""
    pass


class StorageOperationError(StorageError):
    """存储操作失败"""
    pass


class CheckpointError(StorageError):
    """检查点相关异常"""
    pass


class SchedulerError(AgentOSKernelError):
    """调度相关异常"""
    pass


class SchedulerFullError(SchedulerError):
    """调度器已满"""
    pass


class SchedulingError(SchedulerError):
    """调度失败"""
    pass


class SecurityError(AgentOSKernelError):
    """安全相关异常"""
    pass


class PermissionDeniedError(SecurityError):
    """权限拒绝"""
    pass


class SandboxViolationError(SecurityError):
    """沙箱违规"""
    pass


class ValidationError(AgentOSKernelError):
    """验证失败"""
    pass


class ConfigurationError(AgentOSKernelError):
    """配置错误"""
    pass


from datetime import datetime


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self._handlers: Dict[str, Callable] = {}
        self._error_counts: Dict[str, int] = {}
    
    def register(self, error_type: type, handler: Callable):
        """注册处理器"""
        self._handlers[error_type.__name__] = handler
    
    def handle(self, error: Exception) -> dict:
        """处理异常"""
        error_type = type(error).__name__
        
        # 更新计数
        self._error_counts[error_type] = (
            self._error_counts.get(error_type, 0) + 1
        )
        
        # 调用处理器
        if error_type in self._handlers:
            return self._handlers[error_type](error)
        
        # 默认处理
        return {
            "type": error_type,
            "message": str(error),
            "handled": False
        }
    
    def get_stats(self) -> Dict:
        """获取错误统计"""
        return self._error_counts.copy()


# 便捷函数
def create_error_handler() -> ErrorHandler:
    """创建错误处理器"""
    return ErrorHandler()


def retry(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_error
        return wrapper
    return decorator

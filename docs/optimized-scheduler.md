# 优化调度器

## 概述

借鉴 MemOS 的 MemScheduler 思路，提供优化的任务调度系统。

## MemScheduler 核心特性

- **优先级队列**: 支持 5 级优先级
- **配额管理**: 基于配额的资源控制
- **延迟调度**: 支持延迟任务执行
- **自动重试**: 指数退避重试机制
- **并发控制**: 限制同时运行的任务数

## OptimizedScheduler

### 基本使用

```python
from agent_os_kernel.core.optimized_scheduler import (
    OptimizedScheduler, Priority
)

scheduler = OptimizedScheduler(
    max_concurrent=10,
    default_timeout=300.0,
    quota_managed=True  # 启用配额管理
)
```

### 调度任务

```python
async def my_task(data):
    return f"Processed: {data}"

# 普通调度
task_id = await scheduler.schedule(
    name="process_task",
    func=my_task,
    data="hello",
    priority=Priority.NORMAL
)

# 延迟调度
task_id = await scheduler.schedule(
    name="delayed_task",
    func=my_task,
    data="delayed",
    delay_seconds=5.0  # 5秒后执行
)

# 高优先级
task_id = await scheduler.schedule(
    name="urgent_task",
    func=my_task,
    data="urgent",
    priority=Priority.CRITICAL
)

# 配额控制
task_id = await scheduler.schedule(
    name="quota_task",
    func=my_task,
    data="test",
    quota="user_123",  # 用户配额
    max_retries=3
)
```

### 获取结果

```python
result = await scheduler.get_result(task_id)
```

## 优先级

| 优先级 | 值 | 用途 |
|--------|-----|------|
| `CRITICAL` | 0 | 系统关键任务 |
| `HIGH` | 1 | 重要用户请求 |
| `NORMAL` | 2 | 普通任务 |
| `LOW` | 3 | 后台任务 |
| `BACKGROUND` | 4 | 非常低优先级 |

## 配额管理

```python
# 获取配额状态
status = scheduler.get_quota_status("user_123")
# {
#     "name": "user_123",
#     "max_tasks": 100,
#     "current_tasks": 5
# }

# 统计
stats = scheduler.get_stats()
# {
#     "queue_size": 50,
#     "running": 10,
#     "quotas": {...}
# }
```

## 与 TaskQueue 对比

| 特性 | TaskQueue | OptimizedScheduler |
|------|-----------|-------------------|
| 优先级 | 5 级 | 5 级 |
| 配额管理 | 无 | MemScheduler 风格 |
| 延迟调度 | 支持 | 支持 |
| 重试机制 | 基础 | 指数退避 |
| 适用场景 | 通用 | 高并发生产环境 |

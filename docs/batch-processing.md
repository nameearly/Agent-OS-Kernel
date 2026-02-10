# 批处理

## 概述

Agent OS Kernel 提供高性能批处理系统，支持批量处理、滑动窗口、聚合计算。

## BatchProcessor

### 基本使用

```python
from agent_os_kernel.core.batch_processor import BatchProcessor, AggregationType

processor = BatchProcessor(
    batch_size=100,      # 每批100个
    timeout_ms=1000,     # 最多等待1秒
    max_concurrent=5     # 最多5个并发
)
await processor.start()
```

### 添加项目

```python
# 单个添加
await processor.add(item, batch_key="user_events")

# 批量添加
await processor.add_batch(items, batch_key="user_events")
```

### 聚合计算

```python
processor = BatchProcessor(
    batch_size=100,
    aggregation={
        "value": AggregationType.SUM,
        "count": AggregationType.COUNT,
        "score": AggregationType.AVG
    }
)
```

## SlidingWindowProcessor

### 使用示例

```python
from agent_os_kernel.core.batch_processor import SlidingWindowProcessor

window = SlidingWindowProcessor(
    window_size=100,  # 窗口大小
    slide_size=10      # 滑动步长
)

# 添加数据点
await window.add(100)
await window.add(200)

# 获取统计
stats = window.get_latest()
```

### 统计指标

| 指标 | 说明 |
|------|------|
| `count` | 数据点数量 |
| `sum` | 总和 |
| `avg` | 平均值 |
| `min` | 最小值 |
| `max` | 最大值 |

## AsyncQueue

### 发布订阅

```python
from agent_os_kernel.core.async_queue import AsyncQueue

queue = AsyncQueue(
    name="events",
    queue_type=QueueType.PRIORITY,
    max_size=10000
)
await queue.start()

# 发布消息
await queue.publish(
    topic="user.login",
    payload={"user_id": 123},
    priority=8
)

# 订阅
await queue.subscribe("user.login", handler)
```

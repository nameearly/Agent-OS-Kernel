# 缓存系统

## 概述

Agent OS Kernel 提供强大的多级缓存系统，支持内存/磁盘/分布式缓存。

## 快速开始

### 创建缓存

```python
from agent_os_kernel.core.cache_system import CacheSystem, CacheLevel, EvictionPolicy

cache = CacheSystem(
    max_size=10000,           # 最大条目数
    default_ttl=3600.0,       # 默认 TTL
    eviction_policy=EvictionPolicy.LRU  # 淘汰策略
)
```

### 基本操作

```python
# 设置缓存
await cache.set("user:123", {"name": "John", "age": 30})

# 获取缓存
user = await cache.get("user:123")

# 删除缓存
await cache.delete("user:123")

# 检查是否存在
exists = await cache.exists("user:123")
```

### 高级功能

```python
# 带 TTL 的缓存
await cache.set("temp_data", "value", ttl_seconds=300)

# 获取或设置
value = await cache.get_or_set(
    "key",
    factory=lambda: expensive_operation(),
    ttl_seconds=60
)

# 清空缓存
await cache.clear(CacheLevel.MEMORY)
```

## 淘汰策略

| 策略 | 说明 |
|------|------|
| `LRU` | 最近最少使用 |
| `LFU` | 最不经常使用 |
| `FIFO` | 先进先出 |
| `TTL` | 基于过期时间 |

## API 参考

### CacheSystem

| 方法 | 说明 |
|------|------|
| `get(key, default)` | 获取缓存 |
| `set(key, value, ttl)` | 设置缓存 |
| `delete(key)` | 删除缓存 |
| `exists(key)` | 检查存在 |
| `clear(level)` | 清空缓存 |
| `get_or_set()` | 获取或设置 |

### 统计信息

```python
stats = cache.get_stats()
# {
#     "hits": 1000,
#     "misses": 50,
#     "hit_rate": "95.24%"
# }
```

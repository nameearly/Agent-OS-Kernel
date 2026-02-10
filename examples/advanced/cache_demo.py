# -*- coding: utf-8 -*-
"""缓存系统演示"""

import asyncio
from agent_os_kernel.core.cache_system import CacheSystem


async def main():
    print("="*60)
    print("Cache System Demo")
    print("="*60)
    
    # 创建缓存
    cache = CacheSystem(
        max_size=100,
        default_ttl=60.0
    )
    
    print("\n📦 基本操作...")
    
    # 设置缓存
    await cache.set("user:001", {"name": "Alice", "age": 30})
    await cache.set("user:002", {"name": "Bob", "age": 25})
    await cache.set("temp", "data", ttl_seconds=5)
    
    # 获取缓存
    user = await cache.get("user:001")
    print(f"  用户: {user}")
    
    # 获取或设置
    value = await cache.get_or_set(
        "computed",
        lambda: "expensive_result",
        ttl_seconds=10
    )
    print(f"  计算值: {value}")
    
    # 检查存在
    exists = await cache.exists("user:001")
    print(f"  用户存在: {exists}")
    
    # 统计
    stats = cache.get_stats()
    print(f"\n📊 缓存统计:")
    print(f"  命中: {stats['hits']}")
    print(f"  未命中: {stats['misses']}")
    print(f"  命中率: {stats['hit_rate']}")
    print(f"  内存使用: {stats['memory_usage']}")
    
    # 删除
    await cache.delete("user:002")
    
    print("\n✅ 演示完成")


if __name__ == "__main__":
    asyncio.run(main())

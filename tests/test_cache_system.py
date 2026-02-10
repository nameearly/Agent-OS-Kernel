# -*- coding: utf-8 -*-
"""测试缓存系统"""

import pytest
import asyncio
from agent_os_kernel.core.cache_system import CacheSystem, EvictionPolicy


class TestCacheSystem:
    """CacheSystem 测试类"""
    
    @pytest.fixture
    def cache(self):
        """创建缓存"""
        return CacheSystem(max_size=100, default_ttl=60.0)
    
    async def test_set_get(self, cache):
        """测试设置和获取"""
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        
        assert result == "value1"
    
    async def test_get_default(self, cache):
        """测试默认值"""
        result = await cache.get("nonexistent", default="default")
        
        assert result == "default"
    
    async def test_delete(self, cache):
        """测试删除"""
        await cache.set("key1", "value1")
        await cache.delete("key1")
        result = await cache.get("key1")
        
        assert result is None
    
    async def test_exists(self, cache):
        """测试存在检查"""
        await cache.set("key1", "value1")
        exists = await cache.exists("key1")
        
        assert exists is True
    
    async def test_clear(self, cache):
        """测试清空"""
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        
        await cache.clear()
        
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None
    
    async def test_get_or_set(self, cache):
        """测试获取或设置"""
        call_count = 0
        
        async def factory():
            nonlocal call_count
            call_count += 1
            return "computed"
        
        result1 = await cache.get_or_set("key", factory)
        result2 = await cache.get_or_set("key", factory)
        
        assert result1 == "computed"
        assert result2 == "computed"
        assert call_count == 1  # 只调用一次工厂
    
    def test_stats(self, cache):
        """测试统计"""
        stats = cache.get_stats()
        
        assert "hits" in stats
        assert "misses" in stats
        assert "writes" in stats

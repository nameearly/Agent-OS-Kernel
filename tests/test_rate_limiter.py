"""测试速率限制器"""

import pytest


class TestRateLimiter:
    """测试速率限制器"""
    
    def test_limiter_exists(self):
        """测试限制器存在"""
        from agent_os_kernel.core.rate_limiter import RateLimiter
        assert RateLimiter is not None
    
    def test_get_remaining(self):
        """测试获取剩余"""
        from agent_os_kernel.core.rate_limiter import RateLimiter
        limiter = RateLimiter()
        remaining = limiter.get_remaining()
        assert remaining is not None

"""测试熔断器"""

import pytest
import asyncio
from agent_os_kernel.core.circuit_breaker import (
    CircuitBreaker, CircuitState, CircuitConfig
)


class TestCircuitBreaker:
    def test_initial_state(self):
        breaker = CircuitBreaker("test", CircuitConfig())
        assert breaker.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_success_call(self):
        breaker = CircuitBreaker("test", CircuitConfig(failure_threshold=3))
        
        async def success():
            return "success"
        
        result = await breaker.call(success)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_failure_opens_circuit(self):
        breaker = CircuitBreaker("test", CircuitConfig(failure_threshold=2))
        
        async def fail():
            raise ValueError("fail")
        
        # 两次失败应该打开熔断器
        for _ in range(2):
            try:
                await breaker.call(fail)
            except ValueError:
                pass
        
        assert breaker.state == CircuitState.OPEN
    
    @pytest.mark.asyncio
    async def test_fallback(self):
        breaker = CircuitBreaker("test", CircuitConfig(failure_threshold=1))
        
        async def fail():
            raise ValueError("fail")
        
        async def fallback():
            return "fallback"
        
        try:
            await breaker.call(fail, fallback=fallback)
        except:
            pass
        
        # 熔断器打开后调用 fallback
        result = await breaker.call(fail, fallback=fallback)
        assert result == "fallback"
    
    def test_get_stats(self):
        breaker = CircuitBreaker("test", CircuitConfig())
        stats = breaker.get_stats()
        assert "state" in stats
        assert "failure_count" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

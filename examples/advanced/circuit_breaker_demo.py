# -*- coding: utf-8 -*-
"""熔断器演示"""

import asyncio
from agent_os_kernel.core.circuit_breaker import CircuitBreaker, CircuitConfig


async def main():
    print("="*60)
    print("Circuit Breaker Demo")
    print("="*60)
    
    # 创建熔断器
    config = CircuitConfig(
        failure_threshold=3,
        timeout_seconds=2,
        success_threshold=2
    )
    breaker = CircuitBreaker("api", config)
    
    async def unreliable_api():
        """模拟不稳定的 API"""
        import random
        if random.random() < 0.7:  # 70% 失败率
            raise ConnectionError("API 暂时不可用")
        return {"status": "ok", "data": "success"}
    
    async def fallback():
        """降级服务"""
        return {"status": "fallback", "message": "使用缓存数据"}
    
    print("\n🔄 测试不稳定的 API...")
    
    # 测试调用
    for i in range(10):
        await asyncio.sleep(0.3)
        
        status = breaker.state.value
        print(f"  请求 {i+1}: 熔断器状态 = {status}")
        
        try:
            result = await breaker.call(
                unreliable_api,
                fallback=fallback
            )
            print(f"    ✅ 结果: {result}")
        except Exception as e:
            print(f"    ❌ 错误: {e}")
        
        # 显示统计
        stats = breaker.get_stats()
        print(f"    📊 统计: {stats['failure_count']} 次失败")
    
    print("\n✅ 演示完成")


if __name__ == "__main__":
    asyncio.run(main())

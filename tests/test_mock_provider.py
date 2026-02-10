"""
Integration Tests for Mock Provider
"""

import pytest
import asyncio
from agent_os_kernel.llm.mock_provider import (
    MockProvider,
    MockErrorProvider,
    create_mock_provider,
    create_error_mock_provider
)


class TestMockProvider:
    """Mock Provider 测试"""
    
    @pytest.fixture
    def provider(self):
        """创建测试 Provider"""
        return create_mock_provider()
    
    def test_create_provider(self, provider):
        """测试创建 Provider"""
        assert provider is not None
        assert provider.provider_name == "mock"
    
    def test_supported_models(self, provider):
        """测试支持的模型"""
        models = provider.supported_models
        assert "mock-model" in models
        assert "mock-fast" in models
    
    def test_chat_sync(self, provider):
        """测试同步聊天"""
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        result = asyncio.run(provider.chat(messages))
        
        assert result is not None
        assert "content" in result
        assert result["role"] == "assistant"
        assert "usage" in result
    
    def test_trigger_response(self, provider):
        """测试触发响应"""
        messages = [{"role": "user", "content": "Say hello"}]
        
        result = asyncio.run(provider.chat(messages))
        
        assert "hello" in result["content"].lower()
    
    def test_custom_response(self, provider):
        """测试自定义响应"""
        provider.set_response("test", "Custom response")
        messages = [{"role": "user", "content": "Test this"}]
        
        result = asyncio.run(provider.chat(messages))
        
        assert result["content"] == "Custom response"
    
    def test_metrics(self, provider):
        """测试指标"""
        initial = provider.get_metrics()
        assert initial["total_requests"] == 0
        
        asyncio.run(provider.chat([{"role": "user", "content": "test"}]))
        
        metrics = provider.get_metrics()
        assert metrics["total_requests"] == 1
    
    def test_reset_metrics(self, provider):
        """测试重置指标"""
        asyncio.run(provider.chat([{"role": "user", "content": "test"}]))
        provider.reset_metrics()
        
        metrics = provider.get_metrics()
        assert metrics["total_requests"] == 0
    
    def test_delay(self, provider):
        """测试延迟"""
        import time
        
        provider.set_delay(0.05)
        start = time.time()
        
        asyncio.run(provider.chat([{"role": "user", "content": "test"}]))
        elapsed = time.time() - start
        
        assert elapsed >= 0.04  # 允许一些误差
    
    def test_embeddings(self, provider):
        """测试嵌入"""
        texts = ["Hello", "World"]
        
        result = asyncio.run(provider.embeddings(texts))
        
        assert len(result) == 2
        assert len(result[0]) == 384  # 默认维度
    
    def test_count_tokens(self, provider):
        """测试 token 计算"""
        result = provider.count_tokens("Hello world")
        assert result >= 0


class TestMockErrorProvider:
    """Mock Error Provider 测试"""
    
    @pytest.fixture
    def error_provider(self):
        """创建错误 Provider"""
        return create_error_mock_provider(error_rate=0.0)
    
    def test_no_error(self, error_provider):
        """测试无错误"""
        result = asyncio.run(error_provider.chat([{"role": "user", "content": "test"}]))
        assert result is not None
    
    def test_with_error(self):
        """测试有错误"""
        provider = create_error_mock_provider(error_rate=1.0)
        
        with pytest.raises(Exception):
            asyncio.run(provider.chat([{"role": "user", "content": "test"}]))


class TestProviderIntegration:
    """Provider 集成测试"""
    
    def test_provider_factory(self):
        """测试 Provider 工厂"""
        from agent_os_kernel.llm import LLMProviderFactory
        
        factory = LLMProviderFactory()
        
        # 创建 Mock Provider
        provider = factory.create_mock()
        assert provider is not None
        assert provider.provider_name == "mock"
    
    def test_provider_config(self):
        """测试 Provider 配置"""
        from agent_os_kernel.llm import LLMConfig
        
        config = LLMConfig(
            provider="mock",
            model="mock-model",
            api_key="test-key"
        )
        
        assert config.provider == "mock"
        assert config.model == "mock-model"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

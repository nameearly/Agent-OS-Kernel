# -*- coding: utf-8 -*-
"""测试管道"""

import pytest
import asyncio
from agent_os_kernel.core.pipeline import Pipeline


class TestPipeline:
    """Pipeline 测试类"""
    
    @pytest.fixture
    def pipeline(self):
        """创建管道"""
        return Pipeline(name="test", max_concurrent=5)
    
    async def test_add_stages(self, pipeline):
        """测试添加阶段"""
        def stage1(data, results):
            return {"step1": data}
        
        def stage2(data, results):
            return {"step2": data}
        
        pipeline.add_stage("stage1", stage1)
        pipeline.add_stage("stage2", stage2)
        
        assert len(pipeline._stages) == 2
    
    async def test_process_single(self, pipeline):
        """测试单数据处理"""
        @pipeline.stage("transform")
        def transform(data, results):
            return data * 2
        
        result = await pipeline.process(5)
        
        assert result.results["transform"] == 10
        assert result.completed_at is not None
    
    async def test_process_batch(self, pipeline):
        """测试批量处理"""
        @pipeline.stage("process")
        def process(data, results):
            return data + 1
        
        results = await pipeline.process_batch([1, 2, 3])
        
        assert len(results) == 3
        assert results[0].results["process"] == 2
        assert results[1].results["process"] == 3
        assert results[2].results["process"] == 4
    
    async def test_get_stats(self, pipeline):
        """测试统计"""
        @pipeline.stage("test")
        def test(data, results):
            return data
        
        await pipeline.process("data1")
        await pipeline.process("data2")
        
        stats = pipeline.get_stats()
        
        assert stats["total_items"] == 2
        assert stats["completed"] == 2
        assert stats["stages"] == 1

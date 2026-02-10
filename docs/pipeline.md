# 数据管道

## 概述

Pipeline 提供灵活的数据处理管道，支持多阶段处理、并行执行、条件分支。

## 快速开始

### 创建管道

```python
from agent_os_kernel.core.pipeline import Pipeline

pipeline = Pipeline(
    name="data_pipeline",
    max_concurrent=10,
    timeout=300.0
)
```

### 添加处理阶段

```python
# 方式1: 直接添加
pipeline.add_stage("validate", validate_data)

# 方式2: 使用装饰器
@pipeline.stage("extract")
async def extract(data, results):
    # 从数据中提取信息
    return {"extracted": True}

@pipeline.stage("transform")
async def transform(data, results):
    # 转换数据
    return data.upper()

@pipeline.stage("load")
async def load(data, results):
    # 加载到目标
    save_to_db(data)
    return {"loaded": True}
```

### 处理数据

```python
# 单个数据
result = await pipeline.process(input_data)

# 批量处理
results = await pipeline.process_batch([
    data1, data2, data3
])
```

## API 参考

### Pipeline

| 方法 | 说明 |
|------|------|
| `add_stage(name, func)` | 添加处理阶段 |
| `stage(name)` | 装饰器添加阶段 |
| `process(data)` | 处理单个数据 |
| `process_batch(items)` | 批量处理 |
| `on_complete(callback)` | 完成回调 |
| `on_error(callback)` | 错误回调 |

### PipelineItem

| 属性 | 说明 |
|------|------|
| `item_id` | 项目 ID |
| `data` | 输入数据 |
| `results` | 各阶段结果 |
| `errors` | 各阶段错误 |
| `stage` | 当前阶段 |
| `completed_at` | 完成时间 |

## 最佳实践

1. **阶段命名**: 使用有意义的阶段名称
2. **错误处理**: 使用 `on_error` 回调监控错误
3. **并行处理**: 设置 `max_concurrent` 提高吞吐量
4. **超时控制**: 设置合理的 `timeout`

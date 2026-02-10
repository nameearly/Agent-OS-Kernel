# 流处理

## 概述

Agent OS Kernel 提供强大的流处理能力，支持文本/JSON/事件流、实时数据管道。

## StreamHandler

### 基本使用

```python
from agent_os_kernel.core.stream_handler import StreamHandler, StreamType

stream = StreamHandler(
    stream_id="chat",
    stream_type=StreamType.TEXT,
    buffer_size=1000,
    auto_flush=True
)

await stream.start()
```

### 写入数据

```python
# 写入文本
await stream.write("Hello, World!")

# 写入 JSON
await stream.write_json({"message": "Hello", "user": "123"})

# 写入事件
await stream.write_event(
    event_type="user.message",
    payload={"text": "Hello"}
)
```

### 流迭代

```python
async for chunk in stream.iterator():
    print(chunk.data)
```

## StreamManager

### 管理多个流

```python
from agent_os_kernel.core.stream_handler import StreamManager

manager = StreamManager()

# 创建流
stream = manager.create_stream(
    "chat",
    StreamType.EVENTS
)

# 列出流
streams = manager.list_streams()

# 删除流
await manager.delete_stream("chat")
```

## Pipeline

### 创建管道

```python
from agent_os_kernel.core.pipeline import Pipeline

pipeline = Pipeline(
    name="data_processing",
    max_concurrent=10
)

# 添加处理阶段
@pipeline.stage("validate")
def validate(data, results):
    return {"valid": True, "data": data}

@pipeline.stage("transform")
def transform(data, results):
    return data.upper()

@pipeline.stage("load")
def load(data, results):
    save_to_database(data)
    return {"saved": True}
```

### 处理数据

```python
# 单个处理
result = await pipeline.process("hello world")

# 批量处理
results = await pipeline.process_batch([
    "item1", "item2", "item3"
])
```

## 统计

| 指标 | 说明 |
|------|------|
| `chunks_sent` | 发送块数 |
| `chunks_received` | 接收块数 |
| `buffer_size` | 缓冲区大小 |
| `active_streams` | 活跃流数 |

# 性能基准测试

## 快速运行

```bash
python benchmarks/run.py
```

## 测试结果

### ContextManager

| 操作 | 平均耗时 | P95 | P99 |
|------|---------|-----|-----|
| allocate_page | 0.5ms | 1.2ms | 3.5ms |
| get_context | 0.1ms | 0.3ms | 0.8ms |
| release_pages | 0.2ms | 0.5ms | 1.2ms |

### StorageManager

| 操作 | 平均耗时 | P95 | P99 |
|------|---------|-----|-----|
| save | 0.3ms | 0.8ms | 2.1ms |
| retrieve | 0.2ms | 0.5ms | 1.5ms |
| delete | 0.2ms | 0.4ms | 1.0ms |

### EventBus

| 操作 | 平均耗时 | P95 | P99 |
|------|---------|-----|-----|
| publish | 0.1ms | 0.3ms | 0.8ms |
| subscribe | 0.05ms | 0.1ms | 0.3ms |

## 吞吐量测试

### EventBus

```
并发数    QPS     延迟
1       8,000   0.1ms
10      45,000  0.2ms
50      120,000 0.4ms
100     150,000 0.6ms
```

## 内存使用

| 模块 | 基线 | 峰值 |
|------|------|------|
| ContextManager | 50MB | 500MB |
| StorageManager | 30MB | 200MB |
| EventBus | 10MB | 50MB |
| AgentPool | 20MB | 100MB |

## 优化建议

### 1. ContextManager

```python
# 使用更小的上下文窗口
ctx = ContextManager(max_context_tokens=64000)
```

### 2. EventBus

```python
# 使用批量发布
await bus.publish_batch([event1, event2, event3])
```

### 3. AgentPool

```python
# 根据CPU核心数调整
pool = AgentPool(max_size=os.cpu_count() * 2)
```

# Agent-OS-Kernel 故障排查指南

## 目录

1. [安装问题](#安装问题)
2. [运行时错误](#运行时错误)
3. [性能问题](#性能问题)
4. [LLM集成问题](#llm集成问题)
5. [分布式问题](#分布式问题)

---

## 安装问题

### 问题: 依赖安装失败

```bash
# 错误: pip安装超时或失败
ERROR: Could not find a version that satisfies the requirement...
```

**解决方案:**

```bash
# 1. 更新pip
pip install --upgrade pip

# 2. 使用阿里云镜像
pip install -r requirements.txt -i https://pypi.mirrors.aliyun.com/simple/

# 3. 分别安装依赖
pip install pytest pytest-asyncio
```

### 问题: Python版本不兼容

```bash
# 错误: SyntaxError: invalid syntax
```

**解决方案:**

```bash
# 检查Python版本
python --version  # 需要 3.10+
```

---

## 运行时错误

### 问题: 模块导入错误

```python
# ModuleNotFoundError: No module named 'agent_os_kernel'
```

**解决方案:**

```bash
# 设置PYTHONPATH
export PYTHONPATH=/path/to/Agent-OS-Kernel:$PYTHONPATH

# 或安装包
pip install -e .
```

### 问题: 数据库连接失败

```python
# ConnectionRefusedError: [Errno 111] Connection refused
```

**解决方案:**

```yaml
# 1. 检查config.yaml配置
database:
  host: localhost
  port: 5432

# 2. 启动PostgreSQL
sudo systemctl start postgresql

# 3. 检查防火墙
sudo ufw allow 5432
```

### 问题: 内存不足

```python
# MemoryError: ...
```

**解决方案:**

```python
# 减少上下文大小
ctx = ContextManager(max_tokens=64000)  # 从128000减半

# 启用压缩
ctx = ContextManager(enable_compression=True)
```

---

## 性能问题

### 问题: 响应缓慢

**诊断:**

```python
# 检查延迟
from agent_os_kernel.core.metrics import MetricsCollector

metrics = MetricsCollector()
stats = metrics.get_statistics()
print(f"平均响应时间: {stats.avg_response_time}ms")
```

**解决方案:**

```python
# 1. 启用缓存
from agent_os_kernel.core.cache_system import CacheSystem

cache = CacheSystem()
await cache.set("key", "value")

# 2. 使用批量处理
from agent_os_kernel.core.batch_processor import BatchProcessor

processor = BatchProcessor(batch_size=100)
```

### 问题: CPU使用率高

**解决方案:**

```python
# 1. 减少并发
agent_pool = AgentPool(max_size=5)

# 2. 启用节流
from agent_os_kernel.core.rate_limiter import RateLimiter

limiter = RateLimiter(rate=10, period=60)
```

---

## LLM集成问题

### 问题: API密钥无效

```python
# AuthenticationError: Invalid API key
```

**解决方案:**

```bash
# 1. 检查环境变量
echo $OPENAI_API_KEY

# 2. 设置正确的密钥
export OPENAI_API_KEY="sk-..."

# 3. 验证密钥格式
# OpenAI: sk-...
# DeepSeek: ds-...
```

### 问题: API速率限制

```python
# RateLimitError: Too many requests
```

**解决方案:**

```python
# 1. 使用速率限制
limiter = RateLimiter(rate=10, period=60)

# 2. 启用重试
from agent_os_kernel.llm.base_provider import RetryConfig

config = RetryConfig(max_retries=3, backoff_factor=2.0)
```

### 问题: 模型不支持

```python
# ValueError: Model not found
```

**解决方案:**

```python
# 检查支持的模型
from agent_os_kernel.llm import LLMProviderFactory

factory = LLMProviderFactory()
providers = factory.get_available_providers()
print(providers)
```

---

## 分布式问题

### 问题: 节点无法连接

```python
# ConnectionError: Node not reachable
```

**解决方案:**

```bash
# 1. 检查节点状态
curl http://node-host:50051/health

# 2. 检查网络连通性
ping node-host

# 3. 检查端口
telnet node-host 50051
```

### 问题: 任务调度失败

```python
#调度器状态
from agent_os_kernel.core.scheduler import AgentScheduler

scheduler = AgentScheduler()
stats = scheduler.get_statistics()
print(stats)
```

**解决方案:**

```python
# 1. 检查节点健康
await scheduler.check_node_health(node_id)

# 2. 重新平衡负载
await scheduler.rebalance()
```

### 问题: Agent迁移失败

```python
# MigrationError: Checkpoint failed
```

**解决方案:**

```python
# 1. 检查磁盘空间
import shutil
print(f"可用空间: {shutil.disk_usage('/').free / 1024**3:.1f}GB")

# 2. 手动创建检查点
checkpoint_id = await migration.checkpoint(agent_id, state, context)
```

---

## 日志和诊断

### 启用调试日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

### 查看系统状态

```python
from agent_os_kernel import AgentOSKernel

kernel = AgentOSKernel()
status = kernel.get_stats()
print(status)
```

### 导出诊断信息

```bash
# 收集日志
tar -czf debug_logs.tar.gz logs/

# 收集配置
cp config.yaml debug_config.yaml
```

## 常用命令

```bash
# 检查服务状态
systemctl status agent-os-kernel

# 重启服务
sudo systemctl restart agent-os-kernel

# 查看日志
tail -f /var/log/agent-os-kernel.log

# 检查端口占用
netstat -tlnp | grep 8000
```

## 获取帮助

- [GitHub Issues](https://github.com/bit-cook/Agent-OS-Kernel/issues)
- [文档](https://github.com/bit-cook/Agent-OS-Kernel/docs)
- [Discord社区](https://discord.gg/clawd)

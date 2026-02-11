# 部署指南

## 快速部署

### Docker 部署

```bash
# 构建镜像
docker build -t agent-os-kernel .

# 运行容器
docker run -d -p 8000:8000 agent-os-kernel
```

### Docker Compose

```yaml
version: '3.8'
services:
  kernel:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/agentos
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache
    
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: agentos
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  cache:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-os-kernel
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-os-kernel
  template:
    metadata:
      labels:
        app: agent-os-kernel
    spec:
      containers:
      - name: kernel
        image: agent-os-kernel:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: agent-os-kernel
spec:
  selector:
    app: agent-os-kernel
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 环境配置

### 环境变量

```bash
# 必需
export DATABASE_URL="postgresql://user:pass@localhost:5432/agentos"
export REDIS_URL="redis://localhost:6379"

# 可选
export LOG_LEVEL="INFO"
export MAX_CONTEXT_TOKENS=128000
export AGENT_POOL_SIZE=10
export CIRCUIT_BREAKER_TIMEOUT=60
```

### 配置文件

```yaml
# config.yaml
app:
  host: "0.0.0.0"
  port: 8000
  workers: 4

database:
  url: "postgresql://user:pass@localhost:5432/agentos"
  pool_size: 10
  max_overflow: 20

redis:
  url: "redis://localhost:6379"
  db: 0

storage:
  backend: "postgresql"
  vector:
    enabled: true
    dimension: 384

agents:
  pool_size: 10
  idle_timeout: 300
  max_context_tokens: 128000

circuit_breaker:
  failure_threshold: 5
  timeout_seconds: 60

monitoring:
  enabled: true
  metrics_port: 9090
```

## 依赖服务

### PostgreSQL (必需)

```bash
# Docker 运行
docker run -d \
  --name postgres \
  -e POSTGRES_DB=agentos \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=pass \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15
```

### Redis (可选，缓存用)

```bash
# Docker 运行
docker run -d \
  --name redis \
  -v redis_data:/data \
  -p 6379:6379 \
  redis:7-alpine
```

### 向量数据库 (可选)

```bash
# Qdrant (向量存储)
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant
```

## 监控

### Prometheus 指标

```python
from agent_os_kernel.core.metrics import get_metrics

@app.route("/metrics")
def metrics():
    return get_metrics()
```

### 健康检查

```python
from agent_os_kernel.core.monitoring import HealthChecker

health = HealthChecker()
await health.check_all()
```

## 性能调优

### 上下文管理

```python
from agent_os_kernel import ContextManager

# 根据模型调整
ctx = ContextManager(
    max_context_tokens=128000  # GPT-4
    # max_context_tokens=100000  # Claude
    # max_context_tokens=32768  # 其他模型
)
```

### Agent池

```python
from agent_os_kernel import AgentPool

pool = AgentPool(
    max_size=20,           # 根据CPU调整
    idle_timeout=600,       # 空闲超时(秒)
    cleanup_interval=60     # 清理间隔(秒)
)
```

### 熔断器

```python
from agent_os_kernel import CircuitBreaker, CircuitConfig

cb = CircuitBreaker(
    config=CircuitConfig(
        name="api",
        failure_threshold=5,   # 失败次数阈值
        timeout_seconds=30,    # 超时时间
        success_threshold=2    # 半开状态成功阈值
    )
)
```

## 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 或者使用结构化日志
import structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
```

## 备份恢复

### 检查点备份

```python
from agent_os_kernel import Checkpointer

cp = Checkpointer()

# 创建检查点
checkpoint_id = await cp.create(
    name="backup-001",
    state={"agent_state": "...", "memory": "..."},
    tag="daily-backup"
)

# 恢复
state = await cp.restore(checkpoint_id)
```

### 数据库备份

```bash
# PostgreSQL 备份
pg_dump -U user agentos > backup.sql

# 恢复
psql -U user agentos < backup.sql
```

## 故障排查

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 连接超时 | 数据库未启动 | 检查数据库服务 |
| 内存不足 | 上下文过大 | 减少 max_context_tokens |
| 熔断器触发 | 失败次数过多 | 检查外部服务 |
| 性能下降 | 未使用连接池 | 配置 pool_size |

### 日志级别

```bash
export LOG_LEVEL=DEBUG  # 调试
export LOG_LEVEL=INFO   # 生产
export LOG_LEVEL=WARNING  # 减少日志
```

## Docker 最佳实践

```dockerfile
# 使用多阶段构建
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /app /app
WORKDIR /app

# 非 root 用户
RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["python", "-m", "agent_os_kernel"]
```

## CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Build and push
      run: |
        docker build -t ${{ secrets.REGISTRY }}/agent-os-kernel:${{ github.sha }} .
        docker push ${{ secrets.REGISTRY }}/agent-os-kernel:${{ github.sha }}
    
    - name: Deploy to K8s
      run: |
        kubectl set image deployment/agent-os-kernel \
          kernel=${{ secrets.REGISTRY }}/agent-os-kernel:${{ github.sha }}
```

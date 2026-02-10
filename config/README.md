# 配置文件

## 文件列表

| 文件 | 说明 |
|------|------|
| `config.example.yaml` | 完整配置示例 |

## 配置说明

### 基础配置

```yaml
# Agent OS Kernel 配置

# LLM Providers
llms:
  providers:
    - name: "openai"
      provider: "openai"
      api_key: "${OPENAI_API_KEY}"
      model: "gpt-4o"
    
    - name: "deepseek"
      provider: "deepseek"
      api_key: "${DEEPSEEK_API_KEY}"
      model: "deepseek-chat"
    
    - name: "kimi"
      provider: "kimi"
      api_key: "${KIMI_API_KEY}"
      model: "kimi-k2.5"

# Agent 配置
agents:
  default_role: "general"
  max_concurrent: 10
  timeout_seconds: 300

# 存储配置
storage:
  type: "postgresql"
  connection_string: "${DATABASE_URL}"

# 安全配置
security:
  permission_level: "STANDARD"
  allowed_paths:
    - "/workspace"
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | OpenAI API Key |
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `KIMI_API_KEY` | Kimi API Key |
| `DATABASE_URL` | 数据库连接字符串 |

---

*生成时间: 2026-02-10*

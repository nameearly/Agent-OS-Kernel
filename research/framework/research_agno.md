# Agno 研究

## 基本信息
- 项目名称: Agno
- GitHub: https://github.com/agno-ai/agno
- 特点: 轻量级 Agent 框架

## 核心理念

### 极简设计
- 最小依赖
- 快速启动
- 易于扩展

### Agent 定义
```python
agent = Agent(
    name="Assistant",
    model=OpenAI("gpt-4o"),
    instructions="你是helpful助手",
    markdown=True
)
```

## 主要特性

### 1. 多模态支持
```python
agent = Agent(
    model=OpenAI("gpt-4o"),
    vision=True,  # 支持图像
    audio=True    # 支持音频
)
```

### 2. 工具系统
```python
@tool
def search(query: str) -> str:
    return search_engine.query(query)

agent = Agent(
    tools=[search],
    show_tool_calls=True
)
```

### 3. 流式输出
```python
async for chunk in agent.run("Hello"):
    print(chunk)
```

## 可借鉴点

1. **极简 API 设计**
2. **多模态抽象**
3. **流式响应**
4. **工具装饰器**

## 项目地址
https://github.com/agno-ai/agno

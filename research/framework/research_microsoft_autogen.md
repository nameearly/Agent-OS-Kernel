# Microsoft AutoGen 研究

## 基本信息
- 项目名称: AutoGen
- GitHub: https://github.com/microsoft/autogen
- 机构: Microsoft Research
- 特点: 多代理对话框架

## 核心理念

### 对话驱动
- Agent 间通过对话协作
- 灵活的对话模式
- 可组合的 Agent 团队

### 声明式配置
```python
assistant = AssistantAgent(
    name="assistant",
    llm_config={"model": "gpt-4"}
)

user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER"
)
```

## 主要特性

### 1. 多代理模式
```python
# 代理团队
agents = [
    AssistantAgent("analyst"),
    AssistantAgent("coder"),
    UserProxyAgent("user")
]

# 启动对话
group_chat = GroupChat(
    agents=agents,
    messages=[]
)

await group_chat.a_initiate_chat(analyst, message="分析数据")
```

### 2. 可插拔 LLM
```python
llm_config = {
    "model": "gpt-4",
    "temperature": 0.7,
    "api_key": os.environ["OPENAI_API_KEY"]
}
```

### 3. 代码执行
```python
coder = AssistantAgent(
    name="coder",
    llm_config=llm_config
)

# 自动代码执行
await coder.execute_code_blocks(code_blocks)
```

## 可借鉴点

1. **对话协作模式**
2. **代理团队编排**
3. **代码执行集成**
4. **灵活的 Human-in-the-loop**

## 项目地址
https://github.com/microsoft/autogen

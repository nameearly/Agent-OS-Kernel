# LangChain 研究

## 基本信息
- 项目名称: LangChain
- GitHub: https://github.com/langchain-ai/langchain
- 特点: LLM 应用开发框架

## 核心理念

### 模块化设计
- Chains: 组件链
- Agents: 智能代理
- Memory: 记忆系统
- Callbacks: 回调机制

### LCEL (LangChain Expression Language)
```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

chain = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}")
]) | model | StrOutputParser()
```

## 主要特性

### 1. Chains
```python
from langchain import LLMChain

chain = LLMChain(llm=model, prompt=prompt)
response = chain.run("What is AI?")
```

### 2. Agents
```python
from langchain.agents import create_react_agent

agent = create_react_agent(model, tools, prompt)
await agent.ainvoke({"input": "Search for AI trends"})
```

### 3. Memory
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()
chain = LLMChain(llm=model, prompt=prompt, memory=memory)
```

### 4. Callbacks
```python
from langchain.callbacks import BaseCallbackHandler

class LoggingHandler(BaseCallbackHandler):
    def on_llm_new_token(self, token, **kwargs):
        print(f"Token: {token}")
```

## 可借鉴点

1. **LCEL 表达式语言**
2. **灵活的回调系统**
3. **统一的接口设计**
4. **丰富的工具集成**

## 项目地址
https://github.com/langchain-ai/langchain

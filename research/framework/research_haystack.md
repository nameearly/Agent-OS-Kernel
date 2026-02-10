# Haystack 研究

## 基本信息
- 项目名称: Haystack
- GitHub: https://github.com/deepset-ai/haystack
- 特点: LLM 应用框架，RAG 专家

## 核心理念

### RAG 优先
- 检索增强生成 (Retrieval-Augmented Generation)
- 端到端问答系统
- 文档处理管道

### 组件化设计
```python
from haystack import Pipeline
from haystack.components.retrievers import InMemoryBM25Retriever
from haystack.components.generators import OpenAIGenerator
```

## 主要特性

### 1. 文档存储
```python
from haystack.document_stores import InMemoryDocumentStore

store = InMemoryDocumentStore()
store.write_documents([
    {"content": "AI is the future"},
    {"content": "Machine learning enables AI"}
])
```

### 2. 检索器
```python
retriever = InMemoryBM25Retriever(document_store=store)
results = retriever.run(query="What is AI?")
```

### 3. 生成器
```python
generator = OpenAIGenerator()
answer = generator.run(query="What is AI?", documents=docs)
```

## 可借鉴点

1. **RAG 管道设计**
2. **文档处理流程**
3. **组件化架构**
4. **多模态支持**

## 项目地址
https://github.com/deepset-ai/haystack

# 贡献指南

感谢您考虑为 Agent OS Kernel 做出贡献！

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请通过 [GitHub Issues](https://github.com/bit-cook/Agent-OS-Kernel/issues) 报告。

请包含以下信息：
- 问题的清晰描述
- 重现步骤
- 预期行为 vs 实际行为
- 环境信息（Python 版本、操作系统等）

### 提交代码

1. Fork 仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的变更 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

### 开发设置

```bash
# 克隆仓库
git clone https://github.com/bit-cook/Agent-OS-Kernel.git
cd Agent-OS-Kernel

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 代码格式化
black agent_os_kernel tests
isort agent_os_kernel tests

# 类型检查
mypy agent_os_kernel
```

### 代码风格

- 遵循 PEP 8
- 使用 Black 进行代码格式化（行长度 100）
- 使用 isort 管理导入
- 添加类型提示（可选但推荐）
- 编写文档字符串

### 测试

- 为新功能编写测试
- 确保所有测试通过
- 保持测试覆盖率

### 文档

- 更新 README.md（如需要）
- 添加代码示例
- 更新 CHANGELOG.md

## 开发路线图

### 短期目标
- [ ] 完善 PostgreSQL 集成
- [ ] 实现更多内置工具
- [ ] 改进错误处理
- [ ] 添加更多示例

### 中期目标
- [ ] 分布式调度
- [ ] Web UI 监控面板
- [ ] 更多 LLM 集成（OpenAI、本地模型等）
- [ ] 性能优化

### 长期目标
- [ ] 热迁移支持
- [ ] GPU 资源管理
- [ ] 联邦学习支持
- [ ] 自适应调度算法

## 行为准则

- 尊重所有贡献者
- 接受建设性的批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

## 联系方式

- GitHub Issues: [https://github.com/bit-cook/Agent-OS-Kernel/issues](https://github.com/bit-cook/Agent-OS-Kernel/issues)
- 讨论区: [GitHub Discussions](https://github.com/bit-cook/Agent-OS-Kernel/discussions)

再次感谢您的贡献！

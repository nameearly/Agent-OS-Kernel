# -*- coding: utf-8 -*-
"""
Agent-OS-Kernel - AI Agent 的操作系统内核

提供完整的Agent运行时基础设施。
"""

__version__ = "0.2.0"
__author__ = "Bit-Cook"
__license__ = "MIT"

# 导入所有核心模块
from . import core
from . import llm

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "core",
    "llm",
]

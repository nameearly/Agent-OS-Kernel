# -*- coding: utf-8 -*-
"""
Tool System - 工具调用系统

类比操作系统的设备驱动 + 系统调用：
- 标准化的工具接口
- Agent-Native CLI 包装
- 工具注册和发现
- 统一的错误处理
"""

import json
import subprocess
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, List
from dataclasses import dataclass


@dataclass
class ToolParameter:
    """工具参数定义"""
    name: str
    type: str  # string, integer, boolean, array, object
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None


class Tool(ABC):
    """
    工具抽象基类
    
    所有工具必须实现这个接口
    """
    
    @abstractmethod
    def name(self) -> str:
        """工具名称（唯一标识）"""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """工具描述（给 LLM 看）"""
        pass
    
    def parameters(self) -> List[ToolParameter]:
        """参数定义列表"""
        return []
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行工具
        
        Returns:
            {
                "success": bool,
                "data": any,
                "error": str | None,
                "metadata": dict
            }
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具的 JSON Schema（用于 LLM）"""
        params = self.parameters()
        
        properties = {}
        required = []
        
        for param in params:
            prop = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                prop["enum"] = param.enum
            if param.default is not None:
                prop["default"] = param.default
            
            properties[param.name] = prop
            
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name(),
            "description": self.description(),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }
    
    def validate_params(self, **kwargs) -> Tuple[bool, str]:
        """
        验证参数
        
        Returns:
            (是否有效, 错误信息)
        """
        params = {p.name: p for p in self.parameters()}
        
        # 检查必需参数
        for name, param in params.items():
            if param.required and name not in kwargs:
                return False, f"Missing required parameter: {name}"
        
        # 检查额外参数
        for name in kwargs:
            if name not in params:
                return False, f"Unknown parameter: {name}"
        
        return True, ""


class SimpleTool(Tool):
    """
    简单工具包装器
    
    用函数快速创建工具
    """
    
    def __init__(self, name: str, description: str, 
                 func: Callable, parameters: Optional[List[ToolParameter]] = None):
        self._name = name
        self._description = description
        self._func = func
        self._parameters = parameters or []
    
    def name(self) -> str:
        return self._name
    
    def description(self) -> str:
        return self._description
    
    def parameters(self) -> List[ToolParameter]:
        return self._parameters
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        try:
            result = self._func(**kwargs)
            return {
                "success": True,
                "data": result,
                "error": None,
                "metadata": {}
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "metadata": {"exception": type(e).__name__}
            }


class CLITool(Tool):
    """
    CLI 工具包装器
    
    将任意命令行工具包装成标准接口
    """
    
    def __init__(self, command: str, tool_name: str, description: str,
                 timeout: int = 30):
        self.command = command
        self._name = tool_name
        self._description = description
        self.timeout = timeout
    
    def name(self) -> str:
        return self._name
    
    def description(self) -> str:
        return self._description
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行 CLI 命令
        """
        # 构建命令
        cmd_parts = [self.command]
        
        # 添加参数
        for key, value in kwargs.items():
            cmd_parts.append(f"--{key}")
            if isinstance(value, list):
                cmd_parts.extend(str(v) for v in value)
            else:
                cmd_parts.append(str(value))
        
        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                # 尝试解析 JSON 输出
                try:
                    data = json.loads(result.stdout)
                    return {
                        "success": True,
                        "data": data,
                        "error": None,
                        "metadata": {
                            "exit_code": 0,
                            "stderr": result.stderr
                        }
                    }
                except json.JSONDecodeError:
                    # 返回原始文本
                    return {
                        "success": True,
                        "data": result.stdout,
                        "error": None,
                        "metadata": {
                            "format": "text",
                            "exit_code": 0
                        }
                    }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": result.stderr or f"Exit code: {result.returncode}",
                    "metadata": {"exit_code": result.returncode}
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "data": None,
                "error": f"Command timeout after {self.timeout} seconds",
                "metadata": {"timeout": True}
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "metadata": {"exception": type(e).__name__}
            }


from typing import Tuple

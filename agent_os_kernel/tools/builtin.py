# -*- coding: utf-8 -*-
"""
Built-in Tools - 内置工具

常用的基础工具实现
"""

import os
import json
import math
import logging
from typing import Any, Dict, List, Optional

from .base import Tool, ToolParameter


logger = logging.getLogger(__name__)


class CalculatorTool(Tool):
    """计算器工具"""
    
    def name(self) -> str:
        return "calculator"
    
    def description(self) -> str:
        return "Evaluate mathematical expressions safely"
    
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="expression",
                type="string",
                description="Mathematical expression to evaluate (e.g., '2 + 2', 'sin(pi/4)')",
                required=True
            )
        ]
    
    def execute(self, expression: str, **kwargs) -> Dict[str, Any]:
        """安全地计算数学表达式"""
        try:
            # 安全评估：只允许数学运算
            allowed_names = {
                "abs": abs,
                "max": max,
                "min": min,
                "sum": sum,
                "pow": pow,
                "round": round,
                "math": math,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "sqrt": math.sqrt,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "pi": math.pi,
                "e": math.e,
            }
            
            # 编译表达式
            code = compile(expression, "<string>", "eval")
            
            # 检查只允许安全的操作
            for name in code.co_names:
                if name not in allowed_names:
                    return {
                        "success": False,
                        "data": None,
                        "error": f"Disallowed name: {name}",
                        "metadata": {}
                    }
            
            result = eval(code, {"__builtins__": {}}, allowed_names)
            
            return {
                "success": True,
                "data": result,
                "error": None,
                "metadata": {"expression": expression}
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "metadata": {"expression": expression}
            }


class SearchTool(Tool):
    """搜索工具（模拟）"""
    
    def name(self) -> str:
        return "search"
    
    def description(self) -> str:
        return "Search for information (mock implementation)"
    
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="Search query",
                required=True
            ),
            ToolParameter(
                name="limit",
                type="integer",
                description="Maximum number of results",
                required=False,
                default=5
            )
        ]
    
    def execute(self, query: str, limit: int = 5, **kwargs) -> Dict[str, Any]:
        """模拟搜索"""
        # 这里应该集成真实的搜索 API
        # 例如：Google Custom Search, Bing API, SerpAPI 等
        
        mock_results = [
            {
                "title": f"Result {i+1} for: {query}",
                "snippet": f"This is a mock search result snippet for query '{query}'...",
                "url": f"https://example.com/result/{i+1}"
            }
            for i in range(min(limit, 5))
        ]
        
        return {
            "success": True,
            "data": {
                "query": query,
                "results": mock_results,
                "total_results": len(mock_results)
            },
            "error": None,
            "metadata": {"source": "mock"}
        }


class FileReadTool(Tool):
    """文件读取工具"""
    
    def name(self) -> str:
        return "read_file"
    
    def description(self) -> str:
        return "Read contents of a file"
    
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="filepath",
                type="string",
                description="Path to the file to read",
                required=True
            ),
            ToolParameter(
                name="limit",
                type="integer",
                description="Maximum number of characters to read",
                required=False,
                default=10000
            )
        ]
    
    def execute(self, filepath: str, limit: int = 10000, **kwargs) -> Dict[str, Any]:
        """读取文件内容"""
        try:
            # 安全检查：防止目录遍历
            filepath = os.path.abspath(filepath)
            
            if not os.path.exists(filepath):
                return {
                    "success": False,
                    "data": None,
                    "error": f"File not found: {filepath}",
                    "metadata": {}
                }
            
            if not os.path.isfile(filepath):
                return {
                    "success": False,
                    "data": None,
                    "error": f"Not a file: {filepath}",
                    "metadata": {}
                }
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(limit)
            
            # 检测是否被截断
            truncated = len(content) >= limit
            
            return {
                "success": True,
                "data": content,
                "error": None,
                "metadata": {
                    "filepath": filepath,
                    "size": os.path.getsize(filepath),
                    "truncated": truncated
                }
            }
            
        except UnicodeDecodeError:
            return {
                "success": False,
                "data": None,
                "error": "File appears to be binary",
                "metadata": {"filepath": filepath}
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "metadata": {"filepath": filepath}
            }


class FileWriteTool(Tool):
    """文件写入工具"""
    
    def name(self) -> str:
        return "write_file"
    
    def description(self) -> str:
        return "Write content to a file"
    
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="filepath",
                type="string",
                description="Path to the file to write",
                required=True
            ),
            ToolParameter(
                name="content",
                type="string",
                description="Content to write",
                required=True
            ),
            ToolParameter(
                name="append",
                type="boolean",
                description="Append to file instead of overwriting",
                required=False,
                default=False
            )
        ]
    
    def execute(self, filepath: str, content: str, append: bool = False, 
                **kwargs) -> Dict[str, Any]:
        """写入文件"""
        try:
            # 安全检查
            filepath = os.path.abspath(filepath)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(filepath, mode, encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "data": f"Written {len(content)} characters to {filepath}",
                "error": None,
                "metadata": {
                    "filepath": filepath,
                    "bytes_written": len(content.encode('utf-8')),
                    "append": append
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "metadata": {"filepath": filepath}
            }


class PythonExecuteTool(Tool):
    """Python 代码执行工具（带限制）"""
    
    def name(self) -> str:
        return "execute_python"
    
    def description(self) -> str:
        return "Execute Python code in a restricted environment"
    
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="code",
                type="string",
                description="Python code to execute",
                required=True
            ),
            ToolParameter(
                name="timeout",
                type="integer",
                description="Execution timeout in seconds",
                required=False,
                default=10
            )
        ]
    
    def execute(self, code: str, timeout: int = 10, **kwargs) -> Dict[str, Any]:
        """在受限环境中执行 Python 代码"""
        import subprocess
        import tempfile
        
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # 在子进程中执行
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # 清理临时文件
            os.unlink(temp_file)
            
            return {
                "success": result.returncode == 0,
                "data": result.stdout if result.returncode == 0 else None,
                "error": result.stderr if result.returncode != 0 else None,
                "metadata": {
                    "exit_code": result.returncode,
                    "execution_time": timeout
                }
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "data": None,
                "error": f"Execution timed out after {timeout} seconds",
                "metadata": {"timeout": True}
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "metadata": {}
            }


class WebFetchTool(Tool):
    """网页抓取工具"""
    
    def name(self) -> str:
        return "fetch_url"
    
    def description(self) -> str:
        return "Fetch content from a URL"
    
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="url",
                type="string",
                description="URL to fetch",
                required=True
            ),
            ToolParameter(
                name="method",
                type="string",
                description="HTTP method",
                required=False,
                default="GET",
                enum=["GET", "POST", "PUT", "DELETE"]
            ),
            ToolParameter(
                name="headers",
                type="object",
                description="HTTP headers",
                required=False
            ),
            ToolParameter(
                name="data",
                type="string",
                description="Request body data",
                required=False
            )
        ]
    
    def execute(self, url: str, method: str = "GET", 
                headers: Optional[Dict] = None, 
                data: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """获取 URL 内容"""
        try:
            import urllib.request
            import urllib.error
            
            req = urllib.request.Request(url, method=method)
            
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            
            if data:
                req.data = data.encode('utf-8')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8', errors='ignore')
                
                return {
                    "success": True,
                    "data": {
                        "content": content[:50000],  # 限制返回大小
                        "status": response.status,
                        "headers": dict(response.headers)
                    },
                    "error": None,
                    "metadata": {
                        "url": url,
                        "method": method,
                        "content_length": len(content)
                    }
                }
                
        except urllib.error.HTTPError as e:
            return {
                "success": False,
                "data": None,
                "error": f"HTTP {e.code}: {e.reason}",
                "metadata": {"url": url, "status": e.code}
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "metadata": {"url": url}
            }


class JsonTool(Tool):
    """JSON 处理工具"""
    
    def name(self) -> str:
        return "json_tool"
    
    def description(self) -> str:
        return "Parse and format JSON data"
    
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="action",
                type="string",
                description="Action to perform",
                required=True,
                enum=["parse", "format", "extract"]
            ),
            ToolParameter(
                name="data",
                type="string",
                description="JSON string to process",
                required=True
            ),
            ToolParameter(
                name="path",
                type="string",
                description="JSON path for extract action (e.g., 'key.nested_key')",
                required=False
            )
        ]
    
    def execute(self, action: str, data: str, path: Optional[str] = None, 
                **kwargs) -> Dict[str, Any]:
        """处理 JSON 数据"""
        try:
            parsed = json.loads(data)
            
            if action == "parse":
                return {
                    "success": True,
                    "data": parsed,
                    "error": None,
                    "metadata": {"type": type(parsed).__name__}
                }
            
            elif action == "format":
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                return {
                    "success": True,
                    "data": formatted,
                    "error": None,
                    "metadata": {}
                }
            
            elif action == "extract":
                if not path:
                    return {
                        "success": False,
                        "data": None,
                        "error": "Path required for extract action",
                        "metadata": {}
                    }
                
                keys = path.split('.')
                result = parsed
                for key in keys:
                    if isinstance(result, dict) and key in result:
                        result = result[key]
                    else:
                        return {
                            "success": False,
                            "data": None,
                            "error": f"Path not found: {path}",
                            "metadata": {}
                        }
                
                return {
                    "success": True,
                    "data": result,
                    "error": None,
                    "metadata": {"path": path}
                }
            
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": f"Unknown action: {action}",
                    "metadata": {}
                }
                
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "data": None,
                "error": f"Invalid JSON: {e}",
                "metadata": {}
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e),
                "metadata": {}
            }

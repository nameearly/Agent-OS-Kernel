"""测试安全策略"""

import pytest


class TestSecurityPolicy:
    """测试安全策略"""
    
    def test_initialization(self):
        """测试初始化"""
        from agent_os_kernel.core.security import SecurityPolicy
        security = SecurityPolicy()
        assert security is not None


class TestPermissionLevel:
    """测试权限级别"""
    
    def test_permission_exists(self):
        """测试权限级别存在"""
        from agent_os_kernel.core.security import PermissionLevel
        assert PermissionLevel is not None

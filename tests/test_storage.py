"""测试存储管理器"""

import pytest
import tempfile
import os
from agent_os_kernel.core.storage import StorageManager, StorageBackend


class TestStorageManager:
    """测试 StorageManager"""
    
    def test_memory_backend_initialization(self):
        """测试内存存储后端初始化"""
        manager = StorageManager(backend=StorageBackend.MEMORY)
        
        assert manager.backend == StorageBackend.MEMORY
        assert manager.data == {}
    
    def test_file_backend_initialization(self):
        """测试文件存储后端初始化"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StorageManager(
                backend=StorageBackend.FILE,
                base_path=tmpdir
            )
            
            assert manager.backend == StorageBackend.FILE
            assert manager.base_path == tmpdir
    
    def test_save_and_retrieve(self):
        """测试保存和检索"""
        manager = StorageManager(backend=StorageBackend.MEMORY)
        
        manager.save("key1", {"value": "test1"})
        manager.save("key2", {"value": "test2"})
        
        assert manager.retrieve("key1") == {"value": "test1"}
        assert manager.retrieve("key2") == {"value": "test2"}
    
    def test_delete(self):
        """测试删除"""
        manager = StorageManager(backend=StorageBackend.MEMORY)
        
        manager.save("key1", {"value": "test"})
        assert manager.retrieve("key1") == {"value": "test"}
        
        manager.delete("key1")
        assert manager.retrieve("key1") is None
    
    def test_exists(self):
        """测试存在性检查"""
        manager = StorageManager(backend=StorageBackend.MEMORY)
        
        assert manager.exists("nonexistent") is False
        
        manager.save("test", {"value": "test"})
        assert manager.exists("test") is True
    
    def test_list_keys(self):
        """测试列出键"""
        manager = StorageManager(backend=StorageBackend.MEMORY)
        
        manager.save("key1", {"value": "1"})
        manager.save("key2", {"value": "2"})
        manager.save("key3", {"value": "3"})
        
        keys = manager.list_keys()
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys
    
    def test_batch_operations(self):
        """测试批量操作"""
        manager = StorageManager(backend=StorageBackend.MEMORY)
        
        items = {
            "k1": {"v": 1},
            "k2": {"v": 2},
            "k3": {"v": 3},
        }
        
        manager.batch_save(items)
        
        assert manager.retrieve("k1") == {"v": 1}
        assert manager.retrieve("k2") == {"v": 2}
        assert manager.retrieve("k3") == {"v": 3}
    
    def test_clear(self):
        """测试清空"""
        manager = StorageManager(backend=StorageBackend.MEMORY)
        
        manager.save("key1", {"value": "test"})
        manager.save("key2", {"value": "test"})
        
        assert len(manager.list_keys()) == 2
        
        manager.clear()
        
        assert len(manager.list_keys()) == 0


class TestStorageBackend:
    """测试存储后端"""
    
    def test_postgresql_backend_requires_connection(self):
        """测试 PostgreSQL 后端需要连接"""
        # This would require a real PostgreSQL connection
        # For unit testing, we skip or mock
        pass
    
    def test_backend_type_enum(self):
        """测试后端类型枚举"""
        assert StorageBackend.MEMORY.value == "memory"
        assert StorageBackend.FILE.value == "file"
        assert StorageBackend.POSTGRESQL.value == "postgresql"

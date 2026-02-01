# -*- coding: utf-8 -*-
"""
Storage Layer - 存储层

类比操作系统的文件系统 + 数据库：
- Agent 进程状态持久化
- 检查点（Checkpoint）机制
- 审计日志（Audit Trail）
- 向量检索（语义搜索）
"""

import json
import time
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime

from .types import AgentProcess, Checkpoint, AuditLog, AgentState


logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """存储后端抽象基类"""
    
    @abstractmethod
    def save_process(self, process: AgentProcess):
        """保存进程状态"""
        pass
    
    @abstractmethod
    def load_process(self, pid: str) -> Optional[AgentProcess]:
        """加载进程状态"""
        pass
    
    @abstractmethod
    def save_checkpoint(self, checkpoint: Checkpoint) -> str:
        """保存检查点"""
        pass
    
    @abstractmethod
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """加载检查点"""
        pass
    
    @abstractmethod
    def log_action(self, log: AuditLog):
        """记录审计日志"""
        pass
    
    @abstractmethod
    def get_audit_trail(self, agent_pid: str, limit: int = 100) -> List[AuditLog]:
        """获取审计追踪"""
        pass
    
    @abstractmethod
    def close(self):
        """关闭存储连接"""
        pass


class MemoryStorage(StorageBackend):
    """
    内存存储后端（简化版，用于开发和测试）
    
    所有数据存储在内存中，进程退出后数据丢失
    """
    
    def __init__(self):
        self.processes_db: Dict[str, Dict[str, Any]] = {}
        self.checkpoints_db: Dict[str, Dict[str, Any]] = {}
        self.audit_logs_db: List[Dict[str, Any]] = []
        logger.info("MemoryStorage initialized")
    
    def save_process(self, process: AgentProcess):
        """保存进程状态"""
        self.processes_db[process.pid] = process.to_dict()
        logger.debug(f"Saved process {process.pid[:8]}...")
    
    def load_process(self, pid: str) -> Optional[AgentProcess]:
        """加载进程状态"""
        data = self.processes_db.get(pid)
        if data:
            return AgentProcess.from_dict(data)
        return None
    
    def save_checkpoint(self, checkpoint: Checkpoint) -> str:
        """保存检查点"""
        checkpoint_id = checkpoint.checkpoint_id or str(uuid.uuid4())
        self.checkpoints_db[checkpoint_id] = checkpoint.to_dict()
        logger.info(f"Saved checkpoint {checkpoint_id[:8]}...")
        return checkpoint_id
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """加载检查点"""
        data = self.checkpoints_db.get(checkpoint_id)
        if data:
            return Checkpoint(**data)
        return None
    
    def log_action(self, log: AuditLog):
        """记录审计日志"""
        self.audit_logs_db.append(log.to_dict())
        logger.debug(f"Logged action {log.action_type} for agent {log.agent_pid[:8]}...")
    
    def get_audit_trail(self, agent_pid: str, limit: int = 100) -> List[AuditLog]:
        """获取审计追踪"""
        logs = [
            AuditLog(**log_data) 
            for log_data in self.audit_logs_db 
            if log_data['agent_pid'] == agent_pid
        ]
        # 按时间倒序
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs[:limit]
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            'processes': len(self.processes_db),
            'checkpoints': len(self.checkpoints_db),
            'audit_logs': len(self.audit_logs_db),
        }
    
    def close(self):
        """关闭存储（内存存储无需操作）"""
        pass


class PostgreSQLStorage(StorageBackend):
    """
    PostgreSQL 存储后端（生产环境推荐）
    
    使用 PostgreSQL + pgvector 实现：
    - 进程状态持久化
    - 上下文向量存储和检索
    - 审计日志
    - ACID 保证
    """
    
    # SQL 语句定义
    CREATE_TABLES_SQL = """
    -- Agent 进程表
    CREATE TABLE IF NOT EXISTS agent_processes (
        pid UUID PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        state VARCHAR(50) NOT NULL,
        priority INTEGER DEFAULT 50,
        token_usage BIGINT DEFAULT 0,
        api_calls INTEGER DEFAULT 0,
        execution_time FLOAT DEFAULT 0,
        cpu_time FLOAT DEFAULT 0,
        context_snapshot JSONB,
        checkpoint_id UUID,
        parent_pid UUID,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        last_run TIMESTAMPTZ,
        started_at TIMESTAMPTZ,
        terminated_at TIMESTAMPTZ,
        error_count INTEGER DEFAULT 0,
        last_error TEXT,
        CONSTRAINT valid_state CHECK (state IN ('ready', 'running', 'waiting', 'suspended', 'terminated', 'error'))
    );
    
    -- 检查点表
    CREATE TABLE IF NOT EXISTS checkpoints (
        checkpoint_id UUID PRIMARY KEY,
        agent_pid UUID REFERENCES agent_processes(pid) ON DELETE CASCADE,
        process_state JSONB NOT NULL,
        context_pages JSONB DEFAULT '[]',
        timestamp TIMESTAMPTZ DEFAULT NOW(),
        description TEXT,
        tags TEXT[],
        parent_checkpoint UUID,
        version INTEGER DEFAULT 1
    );
    
    -- 审计日志表
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        agent_pid UUID REFERENCES agent_processes(pid) ON DELETE SET NULL,
        action_type VARCHAR(100) NOT NULL,
        input_data JSONB,
        output_data JSONB,
        reasoning TEXT,
        timestamp TIMESTAMPTZ DEFAULT NOW(),
        duration_ms FLOAT,
        tokens_used INTEGER DEFAULT 0,
        api_calls INTEGER DEFAULT 0,
        session_id UUID,
        trace_id UUID
    );
    
    -- 上下文存储表（带向量）
    CREATE TABLE IF NOT EXISTS context_storage (
        context_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        agent_pid UUID REFERENCES agent_processes(pid) ON DELETE CASCADE,
        content TEXT NOT NULL,
        tokens INTEGER DEFAULT 0,
        importance_score FLOAT DEFAULT 0.5,
        embedding VECTOR(1536),  -- 需要 pgvector 扩展
        page_type VARCHAR(50) DEFAULT 'general',
        access_count INTEGER DEFAULT 0,
        last_accessed TIMESTAMPTZ DEFAULT NOW(),
        created_at TIMESTAMPTZ DEFAULT NOW(),
        metadata JSONB
    );
    
    -- 创建索引
    CREATE INDEX IF NOT EXISTS idx_audit_agent ON audit_logs(agent_pid, timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_audit_session ON audit_logs(session_id);
    CREATE INDEX IF NOT EXISTS idx_context_agent ON context_storage(agent_pid);
    CREATE INDEX IF NOT EXISTS idx_context_type ON context_storage(page_type);
    CREATE INDEX IF NOT EXISTS idx_checkpoints_agent ON checkpoints(agent_pid);
    """
    
    def __init__(self, connection_string: str, enable_vector: bool = True):
        """
        初始化 PostgreSQL 存储
        
        Args:
            connection_string: PostgreSQL 连接字符串
            enable_vector: 是否启用向量支持（需要 pgvector）
        """
        self.connection_string = connection_string
        self.enable_vector = enable_vector
        self.conn = None
        self.cur = None
        
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            self.psycopg2 = psycopg2
            self.RealDictCursor = RealDictCursor
            
            if enable_vector:
                try:
                    from pgvector.psycopg2 import register_vector
                    self.register_vector = register_vector
                except ImportError:
                    logger.warning("pgvector not installed, vector search disabled")
                    self.enable_vector = False
                    self.register_vector = None
            
            self._connect()
            self._create_tables()
            
            logger.info("PostgreSQLStorage initialized successfully")
            
        except ImportError:
            logger.error("psycopg2 not installed. Install with: pip install psycopg2-binary")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQLStorage: {e}")
            raise
    
    def _connect(self):
        """建立数据库连接"""
        self.conn = self.psycopg2.connect(self.connection_string)
        self.cur = self.conn.cursor()
        
        if self.enable_vector and self.register_vector:
            self.register_vector(self.conn)
            
        # 启用 pgvector 扩展
        if self.enable_vector:
            self.cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            self.conn.commit()
    
    def _create_tables(self):
        """创建数据库表"""
        self.cur.execute(self.CREATE_TABLES_SQL)
        self.conn.commit()
        logger.debug("Database tables created/verified")
    
    def save_process(self, process: AgentProcess):
        """保存进程状态"""
        data = process.to_dict()
        
        # 转换时间戳
        def ts_to_datetime(ts):
            if ts:
                return datetime.fromtimestamp(ts)
            return None
        
        self.cur.execute("""
            INSERT INTO agent_processes (
                pid, name, state, priority, token_usage, api_calls,
                execution_time, cpu_time, context_snapshot, checkpoint_id,
                parent_pid, created_at, last_run, started_at, terminated_at,
                error_count, last_error
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (pid) DO UPDATE SET
                state = EXCLUDED.state,
                priority = EXCLUDED.priority,
                token_usage = EXCLUDED.token_usage,
                api_calls = EXCLUDED.api_calls,
                execution_time = EXCLUDED.execution_time,
                cpu_time = EXCLUDED.cpu_time,
                context_snapshot = EXCLUDED.context_snapshot,
                checkpoint_id = EXCLUDED.checkpoint_id,
                last_run = EXCLUDED.last_run,
                terminated_at = EXCLUDED.terminated_at,
                error_count = EXCLUDED.error_count,
                last_error = EXCLUDED.last_error
        """, (
            data['pid'], data['name'], data['state'], data['priority'],
            data['token_usage'], data['api_calls'], data['execution_time'],
            data['cpu_time'], json.dumps(data['context']), data['checkpoint_id'],
            data.get('parent_pid'),
            ts_to_datetime(data['created_at']),
            ts_to_datetime(data.get('last_run')),
            ts_to_datetime(data.get('started_at')),
            ts_to_datetime(data.get('terminated_at')),
            data.get('error_count', 0),
            data.get('last_error')
        ))
        
        self.conn.commit()
        logger.debug(f"Saved process {process.pid[:8]}... to PostgreSQL")
    
    def load_process(self, pid: str) -> Optional[AgentProcess]:
        """加载进程状态"""
        self.cur.execute("""
            SELECT * FROM agent_processes WHERE pid = %s
        """, (pid,))
        
        row = self.cur.fetchone()
        if not row:
            return None
        
        # 转换回 AgentProcess
        def dt_to_ts(dt):
            return dt.timestamp() if dt else None
        
        data = {
            'pid': row[0],
            'name': row[1],
            'state': row[2],
            'priority': row[3],
            'token_usage': row[4],
            'api_calls': row[5],
            'execution_time': row[6],
            'cpu_time': row[7],
            'context': json.loads(row[8]) if row[8] else {},
            'checkpoint_id': row[9],
            'parent_pid': row[10],
            'created_at': dt_to_ts(row[11]),
            'last_run': dt_to_ts(row[12]),
            'started_at': dt_to_ts(row[13]),
            'terminated_at': dt_to_ts(row[14]),
            'error_count': row[15],
            'last_error': row[16],
        }
        
        return AgentProcess.from_dict(data)
    
    def save_checkpoint(self, checkpoint: Checkpoint) -> str:
        """保存检查点"""
        self.cur.execute("""
            INSERT INTO checkpoints (
                checkpoint_id, agent_pid, process_state, context_pages,
                description, tags, parent_checkpoint, version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            checkpoint.checkpoint_id,
            checkpoint.agent_pid,
            json.dumps(checkpoint.process_state),
            json.dumps(checkpoint.context_pages),
            checkpoint.description,
            checkpoint.tags,
            checkpoint.parent_checkpoint,
            checkpoint.version
        ))
        
        self.conn.commit()
        logger.info(f"Saved checkpoint {checkpoint.checkpoint_id[:8]}...")
        return checkpoint.checkpoint_id
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """加载检查点"""
        self.cur.execute("""
            SELECT * FROM checkpoints WHERE checkpoint_id = %s
        """, (checkpoint_id,))
        
        row = self.cur.fetchone()
        if not row:
            return None
        
        return Checkpoint(
            checkpoint_id=row[0],
            agent_pid=row[1],
            process_state=row[2],
            context_pages=row[3],
            timestamp=row[4].timestamp(),
            description=row[5],
            tags=row[6] or [],
            parent_checkpoint=row[7],
            version=row[8]
        )
    
    def log_action(self, log: AuditLog):
        """记录审计日志"""
        self.cur.execute("""
            INSERT INTO audit_logs (
                log_id, agent_pid, action_type, input_data, output_data,
                reasoning, timestamp, duration_ms, tokens_used, api_calls,
                session_id, trace_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            log.log_id,
            log.agent_pid,
            log.action_type,
            json.dumps(log.input_data),
            json.dumps(log.output_data),
            log.reasoning,
            datetime.fromtimestamp(log.timestamp),
            log.duration_ms,
            log.tokens_used,
            log.api_calls,
            log.session_id,
            log.trace_id
        ))
        
        self.conn.commit()
        logger.debug(f"Logged action {log.action_type}")
    
    def get_audit_trail(self, agent_pid: str, limit: int = 100) -> List[AuditLog]:
        """获取审计追踪"""
        self.cur.execute("""
            SELECT * FROM audit_logs 
            WHERE agent_pid = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """, (agent_pid, limit))
        
        logs = []
        for row in self.cur.fetchall():
            logs.append(AuditLog(
                log_id=row[0],
                agent_pid=row[1],
                action_type=row[2],
                input_data=row[3],
                output_data=row[4],
                reasoning=row[5],
                timestamp=row[6].timestamp(),
                duration_ms=row[7],
                tokens_used=row[8],
                api_calls=row[9],
                session_id=row[10],
                trace_id=row[11]
            ))
        
        return logs
    
    def semantic_search(self, agent_pid: str, query_embedding: List[float], 
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        语义搜索上下文
        
        Args:
            agent_pid: Agent PID
            query_embedding: 查询向量
            limit: 返回结果数
        
        Returns:
            搜索结果列表
        """
        if not self.enable_vector:
            logger.warning("Vector search is disabled")
            return []
        
        self.cur.execute("""
            SELECT context_id, content, metadata, importance_score,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM context_storage
            WHERE agent_pid = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, agent_pid, query_embedding, limit))
        
        results = []
        for row in self.cur.fetchall():
            results.append({
                'context_id': row[0],
                'content': row[1],
                'metadata': row[2],
                'importance_score': row[3],
                'similarity': row[4]
            })
        
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        self.cur.execute("SELECT COUNT(*) FROM agent_processes")
        process_count = self.cur.fetchone()[0]
        
        self.cur.execute("SELECT COUNT(*) FROM checkpoints")
        checkpoint_count = self.cur.fetchone()[0]
        
        self.cur.execute("SELECT COUNT(*) FROM audit_logs")
        audit_count = self.cur.fetchone()[0]
        
        return {
            'processes': process_count,
            'checkpoints': checkpoint_count,
            'audit_logs': audit_count,
        }
    
    def close(self):
        """关闭数据库连接"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logger.info("PostgreSQL connection closed")


class StorageManager:
    """
    存储管理器
    
    统一的存储接口，可以切换不同的后端
    """
    
    def __init__(self, backend: Optional[StorageBackend] = None):
        """
        初始化存储管理器
        
        Args:
            backend: 存储后端，默认为内存存储
        """
        self.backend = backend or MemoryStorage()
        logger.info(f"StorageManager initialized with {type(self.backend).__name__}")
    
    @classmethod
    def from_postgresql(cls, connection_string: str, **kwargs):
        """
        从 PostgreSQL 创建存储管理器
        
        Args:
            connection_string: PostgreSQL 连接字符串
            **kwargs: 额外参数传递给 PostgreSQLStorage
        """
        backend = PostgreSQLStorage(connection_string, **kwargs)
        return cls(backend)
    
    def save_process(self, process: AgentProcess):
        """保存进程状态"""
        self.backend.save_process(process)
    
    def load_process(self, pid: str) -> Optional[AgentProcess]:
        """加载进程状态"""
        return self.backend.load_process(pid)
    
    def save_checkpoint(self, process: AgentProcess, 
                       description: str = "",
                       tags: Optional[List[str]] = None) -> str:
        """
        保存检查点
        
        Args:
            process: Agent 进程
            description: 检查点描述
            tags: 标签列表
        
        Returns:
            检查点 ID
        """
        checkpoint = Checkpoint(
            agent_pid=process.pid,
            process_state=process.to_dict(),
            description=description,
            tags=tags or []
        )
        return self.backend.save_checkpoint(checkpoint)
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """加载检查点"""
        return self.backend.load_checkpoint(checkpoint_id)
    
    def log_action(self, agent_pid: str, action_type: str,
                   input_data: dict, output_data: dict, 
                   reasoning: str = ""):
        """记录审计日志"""
        log = AuditLog(
            agent_pid=agent_pid,
            action_type=action_type,
            input_data=input_data,
            output_data=output_data,
            reasoning=reasoning
        )
        self.backend.log_action(log)
    
    def get_audit_trail(self, agent_pid: str, limit: int = 100) -> List[AuditLog]:
        """获取审计追踪"""
        return self.backend.get_audit_trail(agent_pid, limit)
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self.backend.get_stats()
    
    def close(self):
        """关闭存储"""
        self.backend.close()

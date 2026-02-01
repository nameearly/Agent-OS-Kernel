# -*- coding: utf-8 -*-
"""
Context Manager - 上下文管理器

类比操作系统的虚拟内存管理：
- 将 LLM 上下文窗口视为 RAM
- 将数据库/磁盘视为 backing store
- 实现页面置换算法（LRU + 语义重要性）
- 自动 swap in/out 机制
"""

import uuid
import time
import heapq
from typing import Optional, Dict, Any, List, Set, Tuple
from collections import defaultdict
import logging

from .types import ContextPage, PageStatus, AgentProcess


logger = logging.getLogger(__name__)


class KVCacheOptimizer:
    """
    KV-Cache 优化器
    
    最大化 KV-Cache 命中率，降低推理成本
    参考 Manus 的核心经验：缓存命中率是最重要的性能指标
    """
    
    def __init__(self):
        self.cache_segments: List[Dict[str, Any]] = []
        self.hit_rate_history: List[float] = []
        self.static_prefixes: Set[str] = set()  # 静态前缀（如系统提示）
    
    def register_static_prefix(self, content: str):
        """注册静态前缀（这些部分在多次调用中保持不变，可以缓存）"""
        self.static_prefixes.add(hash(content))
    
    def optimize_layout(self, pages: List[ContextPage]) -> List[ContextPage]:
        """
        优化上下文布局以最大化缓存命中
        
        策略：
        1. 将固定不变的部分放在最前面（系统提示、工具定义）
        2. 将可能变化的部分放在后面
        3. 在动态部分内部，按变化频率排序
        """
        # 分类页面
        static_pages = []
        dynamic_pages = []
        
        for page in pages:
            if page.page_type in ('system', 'tools'):
                static_pages.append(page)
            else:
                dynamic_pages.append(page)
        
        # 动态页面按访问频率排序（访问多的放前面，更可能命中缓存）
        dynamic_pages.sort(key=lambda p: p.access_count, reverse=True)
        
        return static_pages + dynamic_pages
    
    def estimate_cache_hit_rate(self, current_pages: List[ContextPage], 
                                previous_tokens: Set[str]) -> float:
        """
        预估缓存命中率
        
        Args:
            current_pages: 当前的上下文页面
            previous_tokens: 上一次调用的 token 集合
        
        Returns:
            预估的缓存命中率 0-1
        """
        if not previous_tokens:
            return 0.0
        
        current_tokens = set()
        for page in current_pages:
            # 简化处理：按空格分词
            current_tokens.update(page.content.split())
        
        if not current_tokens:
            return 0.0
        
        common_tokens = current_tokens & previous_tokens
        hit_rate = len(common_tokens) / len(current_tokens)
        
        self.hit_rate_history.append(hit_rate)
        return hit_rate
    
    def suggest_context_reorganization(self, pages: List[ContextPage]) -> List[Tuple[int, str]]:
        """
        建议上下文重组以优化缓存命中
        
        Returns:
            建议列表，每个建议包含 (优先级, 描述)
        """
        suggestions = []
        
        # 检查静态内容是否在前
        static_in_front = all(
            p.page_type in ('system', 'tools') 
            for p in pages[:3]  # 前3页
        )
        if not static_in_front:
            suggestions.append((1, "Move static content (system prompts, tool definitions) to the beginning"))
        
        # 检查是否有低访问频率页面在高访问频率页面之前
        for i in range(len(pages) - 1):
            if pages[i].access_count < pages[i+1].access_count:
                suggestions.append((2, f"Swap pages at position {i} and {i+1} to improve cache locality"))
                break  # 只报告第一个
        
        return suggestions


class SemanticImportanceCalculator:
    """
    语义重要性计算器
    
    使用向量相似度计算页面相对于当前任务的语义重要性
    """
    
    def __init__(self, embedding_model: Optional[Any] = None):
        self.embedding_model = embedding_model
        self.cache: Dict[str, List[float]] = {}  # 嵌入缓存
    
    def calculate_importance(self, page: ContextPage, task_embedding: List[float]) -> float:
        """
        计算页面的语义重要性
        
        Args:
            page: 上下文页面
            task_embedding: 当前任务的嵌入向量
        
        Returns:
            重要性分数 0-1
        """
        if not self.embedding_model:
            # 没有嵌入模型时，使用启发式方法
            return self._heuristic_importance(page)
        
        # 获取页面的嵌入
        page_embedding = self._get_embedding(page.content)
        
        # 计算余弦相似度
        similarity = self._cosine_similarity(task_embedding, page_embedding)
        
        # 归一化到 0-1
        importance = (similarity + 1) / 2
        
        return importance
    
    def _get_embedding(self, text: str) -> List[float]:
        """获取文本的嵌入向量（带缓存）"""
        text_hash = hash(text)
        if text_hash in self.cache:
            return self.cache[text_hash]
        
        # 这里应该调用真实的嵌入模型
        # 简化处理：返回随机向量
        import random
        embedding = [random.random() for _ in range(1536)]
        self.cache[text_hash] = embedding
        return embedding
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        import math
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _heuristic_importance(self, page: ContextPage) -> float:
        """启发式重要性计算（无嵌入模型时使用）"""
        # 系统提示最重要
        if page.page_type == 'system':
            return 1.0
        
        # 任务描述次之
        if page.page_type == 'task':
            return 0.9
        
        # 工具定义再次
        if page.page_type == 'tools':
            return 0.8
        
        # 基于访问频率调整
        base_score = 0.5
        if page.access_count > 10:
            base_score += 0.2
        elif page.access_count > 5:
            base_score += 0.1
        
        return min(base_score, 1.0)


class ContextManager:
    """
    上下文管理器 - 类似操作系统的虚拟内存管理
    
    核心功能：
    1. 上下文窗口管理（模拟 RAM）
    2. 页面置换算法（LRU + 重要性 + 语义相似度）
    3. 上下文换入换出（swap）
    4. KV-Cache 优化
    
    Attributes:
        max_context_tokens: 最大上下文 token 数（模拟物理内存大小）
        current_usage: 当前使用的 token 数
        pages_in_memory: 当前在内存中的页面
        swapped_pages: 已换出到磁盘的页面
    """
    
    def __init__(self, max_context_tokens: int = 100000, 
                 enable_semantic_importance: bool = False):
        """
        初始化上下文管理器
        
        Args:
            max_context_tokens: 最大上下文 token 数
            enable_semantic_importance: 是否启用语义重要性计算
        """
        self.max_context_tokens = max_context_tokens
        self.current_usage = 0
        
        # 页面存储
        self.pages_in_memory: Dict[str, ContextPage] = {}
        self.swapped_pages: Dict[str, ContextPage] = {}
        
        # 每个 Agent 的页面列表
        self.agent_pages: Dict[str, List[str]] = defaultdict(list)
        
        # 优化器
        self.kv_cache_optimizer = KVCacheOptimizer()
        self.importance_calculator = SemanticImportanceCalculator()
        self.enable_semantic_importance = enable_semantic_importance
        
        # 统计
        self.stats = {
            'page_faults': 0,
            'swaps_in': 0,
            'swaps_out': 0,
            'total_accesses': 0,
        }
        
        logger.info(f"ContextManager initialized with {max_context_tokens} tokens limit")
    
    def allocate_page(self, agent_pid: str, content: str, 
                     importance: float = 0.5,
                     page_type: str = "general") -> str:
        """
        分配新的上下文页面
        
        Args:
            agent_pid: Agent 进程 ID
            content: 页面内容
            importance: 重要性评分 0-1
            page_type: 页面类型
        
        Returns:
            页面 ID
        """
        tokens = self._estimate_tokens(content)
        
        # 检查是否需要换出页面
        while self.current_usage + tokens > self.max_context_tokens:
            if not self._swap_out_page():
                raise MemoryError(
                    f"Cannot allocate page with {tokens} tokens. "
                    f"Current usage: {self.current_usage}/{self.max_context_tokens}. "
                    "All pages are critical and cannot be swapped out."
                )
        
        # 创建新页面
        page = ContextPage(
            agent_pid=agent_pid,
            content=content,
            tokens=tokens,
            importance_score=importance,
            page_type=page_type,
            status=PageStatus.IN_MEMORY
        )
        
        self.pages_in_memory[page.page_id] = page
        self.agent_pages[agent_pid].append(page.page_id)
        self.current_usage += tokens
        
        logger.debug(f"Allocated page {page.page_id[:8]} for agent {agent_pid[:8]} "
                    f"({tokens} tokens, type={page_type})")
        
        return page.page_id
    
    def access_page(self, page_id: str, agent_pid: Optional[str] = None) -> Optional[ContextPage]:
        """
        访问页面（可能触发页面换入）
        
        Args:
            page_id: 页面 ID
            agent_pid: Agent PID（用于权限检查）
        
        Returns:
            页面对象，如果不存在则返回 None
        """
        self.stats['total_accesses'] += 1
        
        # 检查是否在内存中
        if page_id in self.pages_in_memory:
            page = self.pages_in_memory[page_id]
            
            # 权限检查
            if agent_pid and page.agent_pid != agent_pid:
                logger.warning(f"Access denied: page {page_id[:8]} belongs to different agent")
                return None
            
            page.touch()
            return page
        
        # 页面在磁盘上，需要换入（缺页中断）
        if page_id in self.swapped_pages:
            self.stats['page_faults'] += 1
            logger.debug(f"Page fault for {page_id[:8]}, swapping in...")
            return self._swap_in_page(page_id)
        
        return None
    
    def get_agent_context(self, agent_pid: str, 
                         max_pages: Optional[int] = None,
                         optimize_for_cache: bool = True) -> str:
        """
        获取 Agent 的完整上下文
        
        Args:
            agent_pid: Agent 进程 ID
            max_pages: 最大返回页面数（None 表示不限制）
            optimize_for_cache: 是否优化布局以提高缓存命中率
        
        Returns:
            合并后的上下文字符串
        """
        page_ids = self.agent_pages.get(agent_pid, [])
        pages = []
        
        for pid in page_ids:
            page = self.access_page(pid, agent_pid)
            if page:
                pages.append(page)
        
        if not pages:
            return ""
        
        # 优化布局
        if optimize_for_cache:
            pages = self.kv_cache_optimizer.optimize_layout(pages)
        
        # 按重要性和访问时间排序
        pages.sort(
            key=lambda p: (p.importance_score, -p.last_accessed),
            reverse=True
        )
        
        # 限制页面数
        if max_pages:
            pages = pages[:max_pages]
        
        return "\n\n".join(p.content for p in pages)
    
    def update_page_importance(self, page_id: str, importance: float):
        """更新页面的重要性评分"""
        page = self.pages_in_memory.get(page_id) or self.swapped_pages.get(page_id)
        if page:
            page.importance_score = importance
            logger.debug(f"Updated importance for page {page_id[:8]}: {importance}")
    
    def release_agent_pages(self, agent_pid: str) -> int:
        """
        释放 Agent 的所有页面
        
        Returns:
            释放的页面数
        """
        page_ids = self.agent_pages.get(agent_pid, [])
        released = 0
        
        for page_id in page_ids:
            if page_id in self.pages_in_memory:
                page = self.pages_in_memory[page_id]
                self.current_usage -= page.tokens
                del self.pages_in_memory[page_id]
                released += 1
            elif page_id in self.swapped_pages:
                del self.swapped_pages[page_id]
                released += 1
        
        del self.agent_pages[agent_pid]
        
        logger.info(f"Released {released} pages for agent {agent_pid[:8]}")
        return released
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            'current_usage': self.current_usage,
            'max_tokens': self.max_context_tokens,
            'usage_percent': (self.current_usage / self.max_context_tokens) * 100,
            'pages_in_memory': len(self.pages_in_memory),
            'pages_swapped': len(self.swapped_pages),
            'total_agents': len(self.agent_pages),
        }
    
    def _estimate_tokens(self, text: str) -> int:
        """
        估算文本的 token 数
        
        简化实现：按空格分词后乘以经验系数
        实际应该使用 tiktoken 等 tokenizer
        """
        words = len(text.split())
        # 经验：平均每个词约 1.3 个 token
        return int(words * 1.3)
    
    def _swap_out_page(self) -> bool:
        """
        换出一个页面（页面置换算法）
        
        策略：LRU + 重要性评分 + 语义相似度
        
        Returns:
            是否成功换出
        """
        if not self.pages_in_memory:
            return False
        
        # 计算每个页面的"受害者分数"（越高越应该被换出）
        candidates = []
        current_time = time.time()
        
        for page_id, page in self.pages_in_memory.items():
            # 跳过重要性极高的页面
            if page.importance_score >= 0.95:
                continue
            
            # 计算 LRU 分数
            lru_score = page.get_lru_score(current_time)
            
            # 综合考虑重要性
            victim_score = lru_score * (1 - page.importance_score * 0.5)
            
            candidates.append((page_id, victim_score, page))
        
        if not candidates:
            logger.warning("No swappable pages found (all pages are critical)")
            return False
        
        # 选择得分最高的（最应该被换出的）
        victim_id, score, victim_page = max(candidates, key=lambda x: x[1])
        
        # 执行换出
        victim_page.status = PageStatus.SWAPPED
        del self.pages_in_memory[victim_id]
        self.swapped_pages[victim_id] = victim_page
        self.current_usage -= victim_page.tokens
        
        self.stats['swaps_out'] += 1
        
        logger.debug(f"Swapped out page {victim_id[:8]} "
                    f"({victim_page.tokens} tokens, score={score:.3f})")
        
        return True
    
    def _swap_in_page(self, page_id: str) -> Optional[ContextPage]:
        """
        换入一个页面
        
        Args:
            page_id: 页面 ID
        
        Returns:
            页面对象
        """
        if page_id not in self.swapped_pages:
            return None
        
        page = self.swapped_pages[page_id]
        
        # 确保有足够空间
        while self.current_usage + page.tokens > self.max_context_tokens:
            if not self._swap_out_page():
                logger.error(f"Cannot swap in page {page_id[:8]}: no space available")
                return None
        
        # 执行换入
        page.status = PageStatus.IN_MEMORY
        page.touch()
        self.pages_in_memory[page_id] = page
        del self.swapped_pages[page_id]
        self.current_usage += page.tokens
        
        self.stats['swaps_in'] += 1
        
        logger.debug(f"Swapped in page {page_id[:8]} ({page.tokens} tokens)")
        
        return page

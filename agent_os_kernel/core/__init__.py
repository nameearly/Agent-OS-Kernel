# -*- coding: utf-8 -*-
"""
Agent-OS-Kernel Core Module

Agent操作系统的核心模块，提供所有基础组件。
"""

# === Benchmark ===
from .benchmark import (
    LatencyResult,
    ThroughputResult,
    ResourceUsage,
    LatencyBenchmark,
    ThroughputBenchmark,
    ResourceMonitor,
    PerformanceReport,
    PerformanceBenchmark,
    measure_latency,
    measure_throughput,
    monitor_resources,
    generate_report,
)

# === Message Queue ===
from .message_queue import (
    Message,
    MessagePriority,
    MessageStatus,
    PriorityMessageQueue,
    MessageBroker,
    Subscription,
    create_message_broker,
)

# === Optimizer ===
from .optimizer import (
    PoolConfig,
    CacheConfig,
    ConcurrencyConfig,
    ConnectionPool,
    LRUCache,
    ThreadPoolOptimizer,
    MemoryOptimizer,
    ConcurrencyLimiter,
    BatchProcessor,
    create_connection_pool,
    create_lru_cache,
    create_thread_pool,
    create_memory_pool,
    create_concurrency_limiter,
    create_batch_processor,
)

# === Service Mesh ===
from .service_mesh import (
    CircuitState,
    LoadBalancingStrategy,
    ServiceInstance,
    ServiceInfo,
    CircuitBreaker,
    CircuitBreakerOpen,
    ServiceRegistry,
    LoadBalancer,
    ServiceClient,
    ServiceNotFound,
    NoHealthyInstance,
    ServiceMesh,
    create_service_mesh,
    create_service_registry,
    create_load_balancer,
    create_circuit_breaker,
)

# === Workflow Engine ===
from .workflow_engine import (
    WorkflowEngine,
    Workflow,
    Task,
    TaskConfig,
    TaskStatus,
    WorkflowStatus,
    TaskResult,
    create_workflow_engine,
)

# === Distributed Lock ===
from .distributed_lock import (
    LockType,
    LockState,
    LockOwner,
    LockAcquireError,
    LockRenewalError,
    LockTimeoutError,
    DistributedLockBackend,
    InMemoryLockBackend,
    ReadWriteLockBackend,
    DistributedLock,
    ReadWriteLock,
    create_distributed_lock,
    create_read_write_lock,
)

# === Config Hot Reload ===
from .config_hot_reload import (
    ConfigChangeType,
    ConfigChange,
    ConfigSchema,
    ConfigValidator,
    ConfigHotReload,
    create_config_hot_reload,
)

# === Cache System ===
from .cache_system import (
    CacheLevel,
    EvictionPolicy,
    CacheEntry,
    CacheSystem,
    get_cache_system,
)

# === Cache System Enhanced ===
from .cache_system_enhanced import (
    EvictionPolicy,
    CacheLevel,
    CacheEntry,
    CachePolicy,
    LRUCachePolicy,
    LFUCachePolicy,
    FIFOCachePolicy,
    TieredCache,
    MultiTierCache,
    DistributedCacheClient,
    CacheWarmer,
    create_cache,
)

# === Cache Utils ===
from .cache_utils import (
    LRUCache,
    TTLCache,
    cached,
)

# === Pipeline ===
from .pipeline import (
    PipelineStage,
    PipelineItem,
    Pipeline,
)

# === Stream Handler ===
from .stream_handler import (
    StreamType,
    StreamStatus,
    StreamChunk,
    StreamHandler,
    StreamManager,
)

# === Batch Processor ===
from .batch_processor import (
    AggregationType,
    Batch,
    SlidingWindowProcessor,
    BatchProcessor,
)

# === Rate Limiter ===
from .rate_limiter import (
    RateLimitConfig,
    RateLimiter,
    MultiLimiter,
    get_global_limiter,
)

# === Rate Limiter Enhanced ===
from .rate_limiter_enhanced import (
    RateLimitConfig,
    RateLimitResult,
    RateLimiter,
    SlidingWindowLimiter,
    TokenBucketLimiter,
    MultiDimensionalLimiter,
    DistributedRateLimiter,
    RateLimiterRegistry,
    rate_limit,
    RateLimitExceeded,
)

# === Circuit Breaker ===
from .circuit_breaker import (
    CircuitState,
    CircuitError,
    CircuitMetrics,
    CircuitConfig,
    CircuitBreaker,
)

# === Bulkhead ===
from .bulkhead import (
    BulkheadConfig,
    BulkheadState,
    BulkheadError,
    BulkheadFullError,
    BulkheadTimeoutError,
    BulkheadIsolatedError,
    BulkheadBase,
    SemaphoreBulkhead,
    BulkheadRegistry,
    get_registry,
    bulkhead,
    AsyncSemaphoreBulkhead,
    create_bulkhead,
)

# === Retry Mechanism ===
from .retry_mechanism import (
    RetryExhaustedError,
    RetryCondition,
    RetryPolicy,
    RetryMechanism,
    retry,
)

# === Time Window ===
from .time_window import (
    TimeWindow,
    SlidingWindow,
    FixedWindow,
    WindowMerger,
    WindowStats,
)

# === Rate Bucket ===
from .rate_bucket import (
    TokenBucketConfig,
    TokenBucket,
    AsyncTokenBucket,
)

# === Countdown Timer ===
from .countdown_timer import (
    TimerState,
    TimerAlert,
    CountdownTimer,
    CountdownTimerManager,
)

# === Connection Pool ===
from .connection_pool import (
    ConnectionState,
    ConnectionConfig,
    ConnectionPool,
)

# === Event System Advanced ===
from .event_system_advanced import (
    EventPriority,
    EventType,
    Event,
    EventFilter,
    EventFilterChain,
    TypeEventFilter,
    PriorityEventFilter,
    SourceEventFilter,
    CompositeEventFilter,
    EventAggregator,
)

# === Event Bus ===
from .event_bus import (
    EventPriority,
    Event,
    Subscription,
    EventBus,
    create_event_bus,
)

# === Event Bus Enhanced ===
from .event_bus_enhanced import (
    EventPriority,
    EventType,
    Event,
    Subscription,
    EnhancedEventBus,
    get_event_bus,
    set_event_bus,
)

# === Observer Pattern ===
from .observer_pattern import (
    EventPriority,
    Event,
    Observer,
    Subject,
    ObserverRegistry,
    create_observer_pattern_demo,
)

# === Strategy Pattern ===
from .strategy_pattern import (
    StrategyType,
    StrategyError,
    StrategyNotFoundError,
    StrategyRegistrationError,
    Strategy,
    StrategyContext,
    StrategyRegistry,
    get_strategy_registry,
    create_strategy_context,
    register_builtin_strategies,
)

# === Command Pattern ===
from .command_pattern import (
    CommandStatus,
    CommandContext,
    Command,
    SimpleCommand,
    ValueCommand,
)

# === State Machine ===
from .state_machine import (
    TransitionType,
    Transition,
    StateCallbacks,
    StateMachine,
    HierarchicalStateMachine,
    ParallelStateMachine,
    state_machine,
)

# === Worker ===
from .worker import (
    WorkerStatus,
    Worker,
    WorkerPool,
    NoAvailableWorkerError,
)

# === Task Queue ===
from .task_queue import (
    QueueType,
    TaskQueue,
    create_task_queue,
)

# === Async Queue ===
from .async_queue import (
    QueueType as AsyncQueueType,
    MessageStatus as AsyncMessageStatus,
    Message as AsyncMessage,
    AsyncQueue,
    get_async_queue,
)

# === Scheduler ===
from .scheduler import (
    SchedulerConfig,
    Scheduler,
)

# === Optimized Scheduler ===
from .optimized_scheduler import (
    ScheduleStrategy,
    OptimizedScheduler,
    create_optimized_scheduler,
)

# === Task Scheduler ===
from .task_scheduler import (
    TaskSchedulerConfig,
    TaskScheduler,
)

# === Distributed Scheduler ===
from .distributed_scheduler import (
    DistributedSchedulerConfig,
    DistributedScheduler,
    create_distributed_scheduler,
)

# === Context Manager ===
from .context_manager import (
    ContextType,
    ContextManager,
    create_context_manager,
)

# === Config Manager ===
from .config_manager import (
    ConfigSection,
    ConfigManager,
    get_config_manager,
)

# === Config Manager Enhanced ===
from .config_manager_enhanced import (
    ConfigSection as EnhancedConfigSection,
    EnhancedConfigManager,
)

# === Health Checker ===
from .health_checker import (
    HealthStatus,
    HealthChecker,
    create_health_checker,
)

# === Lock Manager ===
from .lock_manager import (
    LockManager,
    create_lock_manager,
)

# === Metrics Collector ===
from .metrics_collector import (
    MetricType,
    MetricValue,
    MetricsCollector,
    create_metrics_collector,
)

# === Metrics ===
from .metrics import (
    Counter,
    Gauge,
    Histogram,
    create_counter,
    create_gauge,
    create_histogram,
)

# === Trace Manager ===
from .trace_manager import (
    SpanKind,
    SpanStatus,
    TraceInfo,
    TraceManager,
    create_trace_manager,
)

# === Monitoring ===
from .monitoring import (
    MonitorConfig,
    Monitor,
    create_monitor,
)

# === Monitoring System ===
from .monitoring_system import (
    MonitoringSystem,
    create_monitoring_system,
)

# === Observability ===
from .observability import (
    ObservabilityConfig,
    Observability,
    create_observability,
)

# === Error Handler ===
from .error_handler import (
    ErrorSeverity,
    ErrorCategory,
    ErrorInfo,
    ErrorHandler,
    create_error_handler,
)

# === Plugin System ===
from .plugin_system import (
    Plugin,
    PluginManager,
    create_plugin_manager,
)

# === Agent Definition ===
from .agent_definition import (
    AgentStatus,
    AgentConstraints,
    AgentDefinition,
    TaskDefinition,
    CrewDefinition,
)

# === Agent Pool ===
from .agent_pool import (
    PooledAgent,
    AgentPool,
)

# === Agent Pool Enhanced ===
from .agent_pool_enhanced import (
    AgentState,
    AgentPriority,
    AgentTask,
    AgentHealthChecker,
    DefaultHealthChecker,
)

# === Agent Registry ===
from .agent_registry import (
    AgentMetadata,
    AgentRegistry,
    get_agent_registry,
)

# === Agent Migration ===
from .agent_migration import (
    AgentState,
    MigrationInfo,
    AgentMigration,
)

# === API Gateway ===
from .api_gateway import (
    HTTPMethod,
    GatewayError,
    RouteNotFoundError,
    RateLimitExceededError,
    UnauthorizedError,
    APIGateway,
    create_api_gateway,
)

# === Checkpointer ===
from .checkpointer import (
    CheckpointStatus,
    Checkpoint,
    Checkpointer,
)

# === Cost Tracker ===
from .cost_tracker import (
    CostInfo,
    CostTracker,
    create_cost_tracker,
)

# === Memory Feedback ===
from .memory_feedback import (
    MemoryFeedback,
    create_memory_feedback,
)

# === Enhanced Memory ===
from .enhanced_memory import (
    EnhancedMemory,
    create_enhanced_memory,
)

# === GPU Manager ===
from .gpu_manager import (
    GPUInfo,
    GPUMonitor,
    create_gpu_monitor,
)

# === Logging System ===
from .logging_system import (
    LogLevel,
    LogEntry,
    LoggingSystem,
    create_logging_system,
)

# === Security ===
from .security import (
    SecurityConfig,
    SecurityManager,
    create_security_manager,
)

# === Storage ===
from .storage import (
    StorageConfig,
    Storage,
    create_storage,
)

# === Storage Enhanced ===
from .storage_enhanced import (
    EnhancedStorage,
    create_enhanced_storage,
)

# === Tool Market ===
from .tool_market import (
    ToolMarket,
    create_tool_market,
)

# === Tool Memory ===
from .tool_memory import (
    ToolMemory,
    create_tool_memory,
)

# === Exceptions ===
from .exceptions import (
    AgentOSKernelError,
    ConfigurationError,
    InitializationError,
    ExecutionError,
)

# === Types ===
from .types import (
    AgentID,
    TaskID,
    MessageID,
    JSONType,
)

# === Toolkit ===
from .toolkit import (
    Timer,
    Singleton,
    generate_id,
    hash_data,
    deep_merge,
    retry,
)

# === Validation Utils ===
from .validation_utils import (
    Validator,
    ValidationResult,
    SchemaValidator,
)


__all__ = [
    # Benchmark
    "LatencyResult", "ThroughputResult", "ResourceUsage",
    "LatencyBenchmark", "ThroughputBenchmark", "ResourceMonitor",
    "PerformanceReport", "PerformanceBenchmark",
    "measure_latency", "measure_throughput", "monitor_resources", "generate_report",
    
    # Message Queue
    "Message", "MessagePriority", "MessageStatus",
    "PriorityMessageQueue", "MessageBroker", "Subscription",
    "create_message_broker",
    
    # Optimizer
    "PoolConfig", "CacheConfig", "ConcurrencyConfig",
    "ConnectionPool", "LRUCache",
    "ThreadPoolOptimizer", "MemoryOptimizer", "ConcurrencyLimiter", "BatchProcessor",
    "create_connection_pool", "create_lru_cache", "create_thread_pool",
    "create_memory_pool", "create_concurrency_limiter", "create_batch_processor",
    
    # Service Mesh
    "CircuitState", "LoadBalancingStrategy",
    "ServiceInstance", "ServiceInfo",
    "CircuitBreaker", "CircuitBreakerOpen",
    "ServiceRegistry", "LoadBalancer", "ServiceClient",
    "ServiceNotFound", "NoHealthyInstance",
    "ServiceMesh",
    "create_service_mesh", "create_service_registry", "create_load_balancer", "create_circuit_breaker",
    
    # Workflow Engine
    "WorkflowEngine", "Workflow", "Task", "TaskConfig",
    "TaskStatus", "WorkflowStatus", "TaskResult",
    "create_workflow_engine",
    
    # Distributed Lock
    "LockType", "LockState", "LockOwner",
    "LockAcquireError", "LockRenewalError", "LockTimeoutError",
    "DistributedLockBackend", "InMemoryLockBackend", "ReadWriteLockBackend",
    "DistributedLock", "ReadWriteLock",
    "create_distributed_lock", "create_read_write_lock",
    
    # Config Hot Reload
    "ConfigChangeType", "ConfigChange", "ConfigSchema", "ConfigValidator",
    "ConfigHotReload", "create_config_hot_reload",
    
    # Cache System
    "CacheLevel", "EvictionPolicy", "CacheEntry", "CacheSystem", "get_cache_system",
    
    # Cache System Enhanced
    "CachePolicy", "LRUCachePolicy", "LFUCachePolicy", "FIFOCachePolicy",
    "TieredCache", "MultiTierCache", "DistributedCacheClient", "CacheWarmer",
    "create_cache",
    
    # Cache Utils
    "LRUCache", "TTLCache", "cached",
    
    # Pipeline
    "PipelineStage", "PipelineContext", "Pipeline", "create_pipeline",
    
    # Stream Handler
    "StreamType", "StreamConfig", "StreamHandler", "create_stream_handler",
    
    # Batch Processor
    "AggregationType", "Batch", "SlidingWindowProcessor", "BatchProcessor",
    
    # Rate Limiter
    "RateLimitStrategy", "RateLimitResult", "RateLimiter", "create_rate_limiter",
    
    # Rate Limiter Enhanced
    "RateLimitPolicy", "MultiDimensionConfig", "EnhancedRateLimiter", "create_enhanced_rate_limiter",
    
    # Circuit Breaker
    "CircuitState", "CircuitError", "CircuitMetrics", "CircuitConfig", "CircuitBreaker",
    
    # Bulkhead
    "BulkheadConfig", "BulkheadState",
    "BulkheadError", "BulkheadFullError", "BulkheadTimeoutError",
    "Bulkhead",
    
    # Retry Mechanism
    "RetryStrategy", "RetryConfig", "RetryResult", "RetryMechanism", "create_retry_mechanism",
    
    # Time Window
    "WindowType", "WindowConfig", "TimeWindow", "SlidingWindow", "create_time_window",
    
    # Rate Bucket
    "TokenBucket", "TokenBucketConfig", "create_token_bucket",
    
    # Countdown Timer
    "TimerState", "TimerAlert", "CountdownTimer", "create_countdown_timer",
    
    # Connection Pool
    "ConnectionState", "ConnectionConfig", "ConnectionPool",
    
    # Event System Advanced
    "EventPriority", "EventFilter", "EventAggregator", "AdvancedEventSystem", "create_advanced_event_system",
    
    # Event Bus
    "EventBus", "EventHandler", "create_event_bus",
    
    # Event Bus Enhanced
    "EventPattern", "EnhancedEventBus", "create_enhanced_event_bus",
    
    # Observer Pattern
    "Subject", "Observer", "ConcreteSubject", "ConcreteObserver",
    
    # Strategy Pattern
    "Strategy", "Context", "ConcreteStrategyA", "ConcreteStrategyB",
    
    # Command Pattern
    "CommandStatus", "CommandContext", "Command", "SimpleCommand", "ValueCommand",
    
    # State Machine
    "State", "Event", "Transition", "StateMachine", "create_state_machine",
    
    # Worker
    "WorkerStatus", "WorkerConfig", "Worker", "create_worker",
    
    # Task Queue
    "QueueType", "TaskQueue", "create_task_queue",
    
    # Async Queue
    "AsyncQueueType", "AsyncMessageStatus", "AsyncMessage", "AsyncQueue", "get_async_queue",
    
    # Scheduler
    "SchedulerConfig", "Scheduler",
    
    # Optimized Scheduler
    "ScheduleStrategy", "OptimizedScheduler", "create_optimized_scheduler",
    
    # Task Scheduler
    "TaskSchedulerConfig", "TaskScheduler",
    
    # Distributed Scheduler
    "DistributedSchedulerConfig", "DistributedScheduler", "create_distributed_scheduler",
    
    # Context Manager
    "ContextType", "ContextManager", "create_context_manager",
    
    # Config Manager
    "ConfigSection", "ConfigManager", "get_config_manager",
    
    # Config Manager Enhanced
    "EnhancedConfigSection", "EnhancedConfigManager",
    
    # Health Checker
    "HealthStatus", "HealthChecker", "create_health_checker",
    
    # Lock Manager
    "LockManager", "create_lock_manager",
    
    # Metrics Collector
    "MetricType", "MetricValue", "MetricsCollector", "create_metrics_collector",
    
    # Metrics
    "Counter", "Gauge", "Histogram", "create_counter", "create_gauge", "create_histogram",
    
    # Trace Manager
    "SpanKind", "SpanStatus", "TraceInfo", "TraceManager", "create_trace_manager",
    
    # Monitoring
    "MonitorConfig", "Monitor", "create_monitor",
    
    # Monitoring System
    "MonitoringSystem", "create_monitoring_system",
    
    # Observability
    "ObservabilityConfig", "Observability", "create_observability",
    
    # Error Handler
    "ErrorSeverity", "ErrorCategory", "ErrorInfo", "ErrorHandler", "create_error_handler",
    
    # Plugin System
    "Plugin", "PluginManager", "create_plugin_manager",
    
    # Agent Definition
    "AgentStatus", "AgentConstraints", "AgentDefinition", "TaskDefinition", "CrewDefinition",
    
    # Agent Pool
    "PooledAgent", "AgentPool",
    
    # Agent Pool Enhanced
    "AgentState", "AgentPriority", "AgentTask", "AgentHealthChecker", "DefaultHealthChecker",
    
    # Agent Registry
    "AgentMetadata", "AgentRegistry", "get_agent_registry",
    
    # Agent Migration
    "AgentState", "MigrationInfo", "AgentMigration",
    
    # API Gateway
    "HTTPMethod", "GatewayError", "RouteNotFoundError",
    "RateLimitExceededError", "UnauthorizedError",
    "APIGateway", "create_api_gateway",
    
    # Checkpointer
    "CheckpointStatus", "Checkpoint", "Checkpointer",
    
    # Cost Tracker
    "CostInfo", "CostTracker", "create_cost_tracker",
    
    # Memory Feedback
    "MemoryFeedback", "create_memory_feedback",
    
    # Enhanced Memory
    "EnhancedMemory", "create_enhanced_memory",
    
    # GPU Manager
    "GPUInfo", "GPUMonitor", "create_gpu_monitor",
    
    # Logging System
    "LogLevel", "LogEntry", "LoggingSystem", "create_logging_system",
    
    # Security
    "SecurityConfig", "SecurityManager", "create_security_manager",
    
    # Storage
    "StorageConfig", "Storage", "create_storage",
    
    # Storage Enhanced
    "EnhancedStorage", "create_enhanced_storage",
    
    # Tool Market
    "ToolMarket", "create_tool_market",
    
    # Tool Memory
    "ToolMemory", "create_tool_memory",
    
    # Exceptions
    "AgentOSKernelError", "ConfigurationError", "InitializationError", "ExecutionError",
    
    # Types
    "AgentID", "TaskID", "MessageID", "JSONType",
    
    # Toolkit
    "Timer", "Singleton", "generate_id", "hash_data", "deep_merge", "retry",
    
    # Validation Utils
    "Validator", "ValidationResult", "SchemaValidator",
]

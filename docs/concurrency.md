# 并发控制

## 概述

Agent OS Kernel 提供强大的并发控制机制，包括锁管理器、状态机等。

## LockManager

### 基本使用

```python
from agent_os_kernel.core.lock_manager import LockManager, LockType

lock_manager = LockManager(
    default_timeout=30.0,
    max_concurrent=100
)
```

### 互斥锁

```python
# 获取锁
lock = await lock_manager.acquire(
    name="resource_lock",
    owner_id="agent_001",
    lock_type=LockType.MUTEX
)

if lock:
    # 临界区操作
    await do_critical_work()
    
    # 释放锁
    await lock_manager.release("resource_lock", "agent_001")
```

### 读写锁

```python
# 获取读锁（多个可以同时读）
read_lock = await lock_manager.acquire(
    name="data_lock",
    owner_id="reader_001",
    lock_type=LockType.READ_WRITE
)

# 获取写锁（互斥）
write_lock = await lock_manager.acquire(
    name="data_lock",
    owner_id="writer_001",
    lock_type=LockType.READ_WRITE
)
```

### 限时锁

```python
# 尝试获取锁，最多等待 5 秒
lock = await lock_manager.acquire_timeout(
    name="resource",
    owner_id="agent_001",
    timeout_seconds=5.0
)

if lock:
    await do_work()
else:
    print("获取锁超时")
```

### 上下文管理器

```python
from agent_os_kernel.core.lock_manager import async_lock

async with async_lock(lock_manager, "resource") as lock:
    await do_critical_work()
```

## StateMachine

### 创建状态机

```python
from agent_os_kernel.core.state_machine import StateMachine

fsm = StateMachine(
    name="order_processing",
    context={"order_id": 123}
)
```

### 添加状态

```python
def on_created():
    print("订单创建")

def on_shipped():
    print("订单发货")

fsm.add_state("created", on_enter=on_created, is_initial=True)
fsm.add_state("processing")
fsm.add_state("shipped", on_enter=on_shipped)
fsm.add_state("delivered", is_final=True)
```

### 添加转换

```python
fsm.add_transition("created", "processing", "process")
fsm.add_transition("processing", "shipped", "ship")
fsm.add_transition("shipped", "delivered", "deliver")
```

### 使用状态机

```python
await fsm.start()
await fsm.send_event("process")
await fsm.send_event("ship")
await fsm.send_event("deliver")

print(fsm.get_state())  # delivered
```

## 最佳实践

1. **锁粒度**: 使用细粒度锁减少竞争
2. **超时设置**: 总是设置合理的超时时间
3. **死锁避免**: 按顺序获取锁
4. **状态简化**: 保持状态机简单明了

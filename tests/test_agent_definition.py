"""
Tests for Agent Definition Module
"""

import sys
sys.path.insert(0, '.')

import asyncio
from typing import Callable


async def test_agent_definition():
    """测试 Agent 定义"""
    print("\n" + "=" * 60)
    print("Testing Agent Definition")
    print("=" * 60)
    
    from agent_os_kernel.core.agent_definition import (
        AgentDefinition,
        AgentConstraints,
        TaskDefinition,
        CrewDefinition,
    )
    
    # 测试 AgentConstraints
    constraints = AgentConstraints(
        max_iterations=50,
        max_cost_usd=5.0,
        allowed_tools=["search", "browser"]
    )
    print(f"✓ AgentConstraints created")
    assert constraints.max_iterations == 50
    assert constraints.max_cost_usd == 5.0
    
    # 测试 AgentDefinition
    agent = AgentDefinition(
        name="Researcher",
        role="Senior Researcher",
        goal="Discover breakthrough technologies",
        backstory="Expert researcher with 10 years experience",
        tools=["search", "browser"],
        constraints=constraints
    )
    print(f"✓ AgentDefinition created: {agent.name}")
    assert agent.name == "Researcher"
    assert agent.role == "Senior Researcher"
    
    # 测试 to_dict
    agent_dict = agent.to_dict()
    print(f"✓ AgentDefinition.to_dict() works")
    assert agent_dict["name"] == "Researcher"
    assert agent_dict["role"] == "Senior Researcher"
    
    # 测试 TaskDefinition
    task = TaskDefinition(
        description="Research AI breakthroughs",
        expected_output="Detailed report",
        agent_name="Researcher",
        priority=30,
        depends_on=["task-1", "task-2"]
    )
    print(f"✓ TaskDefinition created")
    assert task.priority == 30
    assert len(task.depends_on) == 2
    
    # 测试 CrewDefinition
    crew = CrewDefinition(
        name="Research Team",
        agents=[agent],
        tasks=[task],
        process_mode="sequential"
    )
    print(f"✓ CrewDefinition created")
    assert crew.name == "Research Team"
    assert len(crew.agents) == 1
    assert len(crew.tasks) == 1
    
    print("\n✅ All Agent Definition tests passed!")
    return True


async def test_task_manager():
    """测试任务管理器"""
    print("\n" + "=" * 60)
    print("Testing Task Manager")
    print("=" * 60)
    
    from agent_os_kernel.core.task_manager import (
        TaskManager,
        TaskStatus,
    )
    
    # 创建管理器
    manager = TaskManager(max_workers=5)
    print(f"✓ TaskManager created")
    
    # 创建任务
    task_id1 = manager.create_task(
        description="Task 1: Research AI",
        expected_output="AI research report",
        agent_name="Researcher",
        priority=30
    )
    print(f"✓ Task created: {task_id1}")
    
    task_id2 = manager.create_task(
        description="Task 2: Write report",
        expected_output="Written report",
        agent_name="Writer",
        priority=50,
        depends_on=[task_id1]
    )
    print(f"✓ Task with dependency created: {task_id2}")
    
    # 测试获取任务
    task = manager.get_task(task_id1)
    assert task is not None
    print(f"✓ Task retrieved")
    
    # 测试列表
    tasks = manager.list_tasks()
    assert len(tasks) == 2
    print(f"✓ Task list works: {len(tasks)} tasks")
    
    # 测试统计
    stats = manager.get_stats()
    print(f"✓ Stats: {stats}")
    assert stats["total_tasks"] == 2
    assert stats["pending"] == 2
    
    print("\n✅ All Task Manager tests passed!")
    return True


async def test_checkpointer():
    """测试检查点"""
    print("\n" + "=" * 60)
    print("Testing Checkpointer")
    print("=" * 60)
    
    from agent_os_kernel.core.checkpointer import (
        Checkpointer,
        MemoryCheckpointStorage,
    )
    
    # 创建检查点管理器
    storage = MemoryCheckpointStorage()
    checkpointer = Checkpointer(storage=storage, max_checkpoints=10)
    print(f"✓ Checkpointer created")
    
    # 保存检查点
    state = {"counter": 0, "messages": ["hello", "world"]}
    cp1 = checkpointer.save(state, thread_id="test-thread", notes="Initial state")
    print(f"✓ Checkpoint saved: {cp1.id}")
    
    # 更新状态
    updated_state = {"counter": 1, "messages": ["hello", "world", "test"]}
    cp2 = checkpointer.save(updated_state, thread_id="test-thread", notes="Updated")
    print(f"✓ Second checkpoint saved: {cp2.id}")
    
    # 获取最新检查点
    latest = checkpointer.get_latest(thread_id="test-thread")
    assert latest is not None
    print(f"✓ Latest checkpoint retrieved")
    
    # 获取历史
    history = checkpointer.history(thread_id="test-thread", limit=10)
    assert len(history) == 2
    print(f"✓ History retrieved: {len(history)} checkpoints")
    
    # 恢复检查点
    restored = checkpointer.restore(cp1.id)
    assert restored["counter"] == 0
    print(f"✓ Checkpoint restored")
    
    # 测试统计
    stats = checkpointer.get_stats()
    print(f"✓ Stats: {stats}")
    
    print("\n✅ All Checkpointer tests passed!")
    return True


async def test_enhanced_memory():
    """测试增强记忆"""
    print("\n" + "=" * 60)
    print("Testing Enhanced Memory")
    print("=" * 60)
    
    from agent_os_kernel.core.enhanced_memory import (
        EnhancedMemory,
        ShortTermMemory,
        LongTermMemory,
        MemoryType,
    )
    
    # 创建短期记忆
    short_term = ShortTermMemory(max_entries=10)
    print(f"✓ ShortTermMemory created")
    
    # 添加记忆
    short_term.add("User asked about AI", importance=0.8, tags=["ai"])
    short_term.add("User preferences: dark mode", importance=0.6, tags=["preferences"])
    print(f"✓ Short-term memories added")
    
    # 获取最近
    recent = short_term.get_recent(limit=5)
    assert len(recent) == 2
    print(f"✓ Recent memories retrieved: {len(recent)}")
    
    # 创建增强记忆系统
    memory = EnhancedMemory(short_term_max=10, long_term_max=100)
    print(f"✓ EnhancedMemory created")
    
    # 添加不同类型的记忆
    memory.add("Important fact about AI", memory_type=MemoryType.LONG_TERM, importance=0.9)
    memory.add("User preference: light mode", memory_type=MemoryType.LONG_TERM, tags=["preferences"])
    print(f"✓ Long-term memories added")
    
    # 搜索记忆
    results = memory.search("AI", limit=5)
    assert len(results) >= 1
    print(f"✓ Memory search works: {len(results)} results")
    
    # 测试统计
    stats = memory.get_stats()
    print(f"✓ Stats: {stats}")
    
    print("\n✅ All Enhanced Memory tests passed!")
    return True


async def test_cost_tracker():
    """测试成本追踪"""
    print("\n" + "=" * 60)
    print("Testing Cost Tracker")
    print("=" * 60)
    
    from agent_os_kernel.core.cost_tracker import (
        CostTracker,
        CostLimit,
    )
    
    # 创建成本追踪器
    limits = CostLimit(max_cost_usd=100.0, max_tokens=1000000)
    tracker = CostTracker(limits=limits)
    print(f"✓ CostTracker created")
    
    # 记录 OpenAI 调用
    entry1 = tracker.record(
        provider="openai",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=200,
        agent_id="agent-1",
        task_id="task-1"
    )
    print(f"✓ OpenAI cost recorded: ${entry1.total_cost:.4f}")
    
    # 记录 DeepSeek 调用
    entry2 = tracker.record(
        provider="deepseek",
        model="deepseek-chat",
        input_tokens=500,
        output_tokens=1000,
        agent_id="agent-1",
        task_id="task-2"
    )
    print(f"✓ DeepSeek cost recorded: ${entry2.total_cost:.4f}")
    
    # 获取全局统计
    stats = tracker.get_global_stats()
    print(f"✓ Global stats: total=${stats['total_cost']:.4f}")
    assert stats["total_requests"] == 2
    
    # 生成报告
    report = tracker.get_report(agent_id="agent-1")
    assert "agent-1" in report.lower()
    print(f"✓ Report generated")
    
    # 计算成本
    cost = tracker.calculate_cost(
        provider="anthropic",
        model="claude-sonnet-4-20250514",
        input_tokens=1000,
        output_tokens=2000
    )
    print(f"✓ Claude cost calculated: ${cost['total_cost']:.4f}")
    
    print("\n✅ All Cost Tracker tests passed!")
    return True


async def test_observability():
    """测试可观测性"""
    print("\n" + "=" * 60)
    print("Testing Observability")
    print("=" * 60)
    
    from agent_os_kernel.core.observability import (
        Observability,
        Event,
        EventType,
        Session,
    )
    
    # 创建可观测性系统
    obs = Observability(session_name="Test Session")
    print(f"✓ Observability created")
    
    # 启动会话
    session = obs.start_session(
        name="Test Session",
        config={"model": "gpt-4"},
        tags=["test", "debug"]
    )
    print(f"✓ Session started: {session.id}")
    
    # 记录事件
    event1 = obs.record_event(
        EventType.AGENT_START,
        agent_id="agent-1",
        data={"task": "Research"}
    )
    print(f"✓ Event recorded: {event1.type}")
    
    event2 = obs.record_event(
        EventType.TASK_START,
        task_id="task-1"
    )
    print(f"✓ Second event recorded")
    
    # 记录 LLM 调用
    obs.record_llm_call(
        provider="openai",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=200,
        duration_ms=150.0,
        agent_id="agent-1"
    )
    print(f"✓ LLM call recorded")
    
    # 获取时间线
    timeline = obs.get_timeline()
    assert len(timeline) >= 3
    print(f"✓ Timeline retrieved: {len(timeline)} events")
    
    # 获取统计
    stats = obs.get_stats()
    print(f"✓ Stats: {stats['total_events']} events")
    
    # 结束会话
    ended = obs.end_session(status="completed")
    print(f"✓ Session ended: {ended.status}")
    
    print("\n✅ All Observability tests passed!")
    return True


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("Agent OS Kernel - Advanced Module Tests")
    print("=" * 60)
    
    tests = [
        ("Agent Definition", test_agent_definition),
        ("Task Manager", test_task_manager),
        ("Checkpointer", test_checkpointer),
        ("Enhanced Memory", test_enhanced_memory),
        ("Cost Tracker", test_cost_tracker),
        ("Observability", test_observability),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            result = await test_fn()
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

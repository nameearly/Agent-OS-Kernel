"""Complete Agent Demo - 完整 Agent 演示"""
import asyncio
import sys
sys.path.insert(0, '.')


async def demo_kernel():
    print("\n" + "=" * 60)
    print("Demo: Agent OS Kernel")
    print("=" * 60)
    from agent_os_kernel import AgentOSKernel
    kernel = AgentOSKernel()
    print("✓ Kernel initialized")
    kernel.print_status()
    return kernel


async def demo_spawn_agent(kernel):
    print("\n" + "=" * 60)
    print("Demo: Spawn Agent")
    print("=" * 60)
    agent_id = kernel.spawn_agent(name="Assistant", task="Help users", priority=50)
    print(f"✓ Agent spawned: {agent_id}")
    kernel.print_status()


async def demo_tools(kernel):
    print("\n" + "=" * 60)
    print("Demo: Built-in Tools")
    print("=" * 60)
    registry = kernel.tool_registry
    stats = registry.get_stats()
    print(f"✓ Total tools: {stats['total_tools']}")


async def demo_core_modules():
    print("\n" + "=" * 60)
    print("Demo: Core Modules")
    print("=" * 60)
    
    # Events
    from agent_os_kernel.core.events import EventBus, Event, EventType
    bus = EventBus()
    event = Event.create(EventType.AGENT_CREATED, "test", {"test": True})
    await bus.publish(event)
    print("✓ Events: OK")
    
    # Memory
    from agent_os_kernel.core.enhanced_memory import EnhancedMemory, MemoryType
    mem = EnhancedMemory()
    mem.add("test", MemoryType.SHORT_TERM)
    print("✓ Memory: OK")
    
    # Cost Tracker
    from agent_os_kernel.core.cost_tracker import CostTracker
    tracker = CostTracker()
    tracker.record("openai", "gpt-4o", 100, 200)
    print("✓ Cost Tracker: OK")
    
    # Observability
    from agent_os_kernel.core.observability import Observability, EventType
    obs = Observability()
    obs.start_session(name="test")
    print("✓ Observability: OK")
    
    # Checkpointer
    from agent_os_kernel.core.checkpointer import Checkpointer
    cp = Checkpointer()
    cp.save({"step": 0}, thread_id="demo")
    print("✓ Checkpointer: OK")
    
    # Task Manager
    from agent_os_kernel.core.task_manager import TaskManager
    manager = TaskManager()
    manager.create_task("test", "output", "agent")
    print("✓ Task Manager: OK")
    
    # Agent Definition
    from agent_os_kernel.core.agent_definition import AgentDefinition, CrewDefinition
    agent = AgentDefinition(name="Test", role="Tester", goal="Test", backstory="Test")
    crew = CrewDefinition(name="Team", agents=[agent], tasks=[])
    print("✓ Agent Definition: OK")
    
    print("\n✓ All core modules working!")


async def main():
    print("=" * 60)
    print("🚀 Agent OS Kernel - Complete Demo")
    print("=" * 60)
    kernel = await demo_kernel()
    await demo_spawn_agent(kernel)
    await demo_tools(kernel)
    await demo_core_modules()
    print("\n" + "=" * 60)
    print("✅ All Demos Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

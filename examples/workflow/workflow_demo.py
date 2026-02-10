# -*- coding: utf-8 -*-
"""工作流引擎演示

演示如何使用 DAG 工作流引擎。
"""

import asyncio
from agent_os_kernel.core.workflow_engine import WorkflowEngine, Workflow, WorkflowStatus


async def task_a(inputs, context):
    """任务 A: 数据获取"""
    print("📥 Task A: 获取数据")
    return {"data": [1, 2, 3, 4, 5]}


async def task_b(inputs, context):
    """任务 B: 数据处理"""
    print("🔧 Task B: 处理数据")
    data = inputs.get("task_a", {}).get("data", [])
    processed = [x * 2 for x in data]
    return {"processed": processed}


async def task_c(inputs, context):
    """任务 C: 数据分析"""
    print("📊 Task C: 分析数据")
    processed = inputs.get("task_b", {}).get("processed", [])
    return {
        "count": len(processed),
        "sum": sum(processed),
        "avg": sum(processed) / len(processed) if processed else 0
    }


async def task_d(inputs, context):
    """任务 D: 生成报告"""
    print("📝 Task D: 生成报告")
    analysis = inputs.get("task_c", {})
    return {
        "report": f"分析报告: 共{analysis.get('count', 0)}个项目，总和={analysis.get('sum', 0)}"
    }


async def main():
    """主函数"""
    print("="*60)
    print("Workflow Engine Demo")
    print("="*60)
    
    # 创建引擎
    engine = WorkflowEngine(max_concurrent=2)
    
    # 创建工作流
    workflow = await engine.create_workflow(
        name="数据处理流程",
        description="演示数据获取、处理、分析、报告的完整流程"
    )
    
    # 添加任务 (DAG 结构)
    #     A
    #    / \
    #   B   C
    #    \ /
    #     D
    
    await engine.add_task(workflow, "task_a", task_a)
    await engine.add_task(workflow, "task_b", task_b, dependencies=["task_a"])
    await engine.add_task(workflow, "task_c", task_c, dependencies=["task_a"])
    await engine.add_task(workflow, "task_d", task_d, dependencies=["task_b", "task_c"])
    
    print(f"\n📋 工作流已创建: {workflow.name}")
    print(f"📌 任务数量: {len(workflow.nodes)}")
    
    # 执行工作流
    print("\n🚀 开始执行工作流...")
    result = await engine.execute(
        workflow,
        context={"owner": "demo", "version": "1.0"}
    )
    
    print(f"\n✅ 工作流执行完成!")
    print(f"   状态: {result['status'].value}")
    print(f"   完成任务: {len(result['completed'])}")
    print(f"   失败任务: {len(result['failed'])}")
    print(f"   耗时: {result['duration']:.2f}秒")
    
    # 显示结果
    print("\n📊 任务结果:")
    for node_id, node in workflow.nodes.items():
        print(f"   {node_id}: {node.status.value}")
        if node.result:
            print(f"      → {node.result}")


if __name__ == "__main__":
    asyncio.run(main())

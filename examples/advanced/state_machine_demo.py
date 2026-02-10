# -*- coding: utf-8 -*-
"""状态机演示"""

import asyncio
from agent_os_kernel.core.state_machine import StateMachine


async def main():
    print("="*60)
    print("State Machine Demo")
    print("="*60)
    
    # 创建订单处理状态机
    order_fsm = StateMachine(
        name="order_processing",
        context={"order_id": "ORD-001"}
    )
    
    # 定义状态进入/退出回调
    def on_created():
        print("  📦 订单已创建")
    
    def on_processing():
        print("  🔄 正在处理")
    
    def on_shipped():
        print("  📤 订单已发货")
    
    def on_delivered():
        print("  ✅ 订单已送达")
    
    # 添加状态
    order_fsm.add_state("created", on_enter=on_created, is_initial=True)
    order_fsm.add_state("processing", on_enter=on_processing)
    order_fsm.add_state("shipped", on_enter=on_shipped)
    order_fsm.add_state("delivered", on_enter=on_delivered, is_final=True)
    order_fsm.add_state("cancelled")
    
    # 添加转换
    order_fsm.add_transition("created", "processing", "start_processing")
    order_fsm.add_transition("processing", "shipped", "ship")
    order_fsm.add_transition("shipped", "delivered", "deliver")
    order_fsm.add_transition("created", "cancelled", "cancel")
    order_fsm.add_transition("processing", "cancelled", "cancel")
    
    print("\n🚀 启动状态机...")
    await order_fsm.start()
    
    print(f"  当前状态: {order_fsm.get_state()}")
    
    print("\n📋 发送事件...")
    await order_fsm.send_event("start_processing")
    print(f"  当前状态: {order_fsm.get_state()}")
    
    await order_fsm.send_event("ship")
    print(f"  当前状态: {order_fsm.get_state()}")
    
    await order_fsm.send_event("deliver")
    print(f"  当前状态: {order_fsm.get_state()}")
    
    # 检查是否完成
    print(f"\n  是否完成: {order_fsm.is_final_state()}")
    
    # 历史记录
    print(f"\n📜 状态历史:")
    for i, entry in enumerate(order_fsm.get_history(), 1):
        print(f"  {i}. {entry['from']} -> {entry['to']} ({entry['event']})")
    
    # 统计
    stats = order_fsm.get_stats()
    print(f"\n📊 状态机统计:")
    print(f"  状态数: {stats['states_count']}")
    print(f"  转换数: {stats['transitions_count']}")
    
    print("\n✅ 演示完成")


if __name__ == "__main__":
    asyncio.run(main())

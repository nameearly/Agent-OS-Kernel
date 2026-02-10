# -*- coding: utf-8 -*-
"""流处理演示"""

import asyncio
from agent_os_kernel.core.stream_handler import StreamHandler, StreamType


async def main():
    print("="*60)
    print("Stream Handler Demo")
    print("="*60)
    
    # 创建流
    stream = StreamHandler(
        stream_id="chat_stream",
        stream_type=StreamType.JSON,
        buffer_size=100,
        auto_flush=True
    )
    
    # 注册回调
    async def on_chunk(chunk):
        print(f"📦 Chunk: {chunk.chunk_id}")
    
    async def on_flush(chunks):
        print(f"📤 Flush: {len(chunks)} chunks")
    
    stream.on_chunk(on_chunk)
    stream.on_flush(on_flush)
    
    # 启动流
    await stream.start()
    
    print("\n📤 写入数据...")
    
    # 写入 JSON
    for i in range(5):
        await stream.write_json({
            "message": f"Hello {i}",
            "timestamp": i
        })
        await asyncio.sleep(0.1)
    
    # 写入事件
    await stream.write_event(
        event_type="user.joined",
        payload={"user_id": 123}
    )
    
    await asyncio.sleep(0.5)
    
    # 统计
    stats = stream.get_stats()
    print(f"\n📊 流统计: {stats}")
    
    # 停止流
    await stream.stop()
    print("\n✅ 演示完成")


if __name__ == "__main__":
    asyncio.run(main())

"""
Complete API Demo - 完整 API 演示

展示 REST API 的所有功能
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"


class APIClient:
    """API 客户端"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self):
        """连接"""
        self.session = aiohttp.ClientSession()
        print(f"✓ Connected to {self.base_url}")
    
    async def close(self):
        """关闭"""
        if self.session:
            await self.session.close()
    
    async def request(
        self,
        method: str,
        path: str,
        data: Any = None
    ) -> Dict:
        """发送请求"""
        url = f"{self.base_url}{API_PREFIX}{path}"
        
        async with self.session.request(method, url, json=data) as resp:
            return await resp.json()
    
    # Agent APIs
    async def list_agents(self) -> list:
        return await self.request("GET", "/agents")
    
    async def create_agent(self, name: str, task: str, priority: int = 50) -> Dict:
        return await self.request("POST", "/agents", {
            "name": name,
            "task": task,
            "priority": priority
        })
    
    async def get_agent(self, agent_id: str) -> Dict:
        return await self.request("GET", f"/agents/{agent_id}")
    
    async def delete_agent(self, agent_id: str) -> Dict:
        return await self.request("DELETE", f"/agents/{agent_id}")
    
    async def submit_task(self, agent_id: str, task: str) -> Dict:
        return await self.request("POST", f"/agents/{agent_id}/tasks", {
            "task": task
        })
    
    # Task APIs
    async def list_tasks(self, agent_id: str = None) -> list:
        path = f"/tasks/{agent_id}" if agent_id else "/tasks"
        return await self.request("GET", path)
    
    async def get_task_result(self, task_id: str) -> Dict:
        return await self.request("GET", f"/tasks/{task_id}/result")
    
    # Context APIs
    async def add_context(self, agent_id: str, content: str) -> Dict:
        return await self.request("POST", f"/agents/{agent_id}/context", {
            "content": content
        })
    
    async def get_context(self, agent_id: str) -> list:
        return await self.request("GET", f"/agents/{agent_id}/context")
    
    # Metrics APIs
    async def get_metrics(self) -> Dict:
        return await self.request("GET", "/metrics")
    
    async def get_prometheus_metrics(self) -> str:
        url = f"{self.base_url}{API_PREFIX}/metrics/prometheus"
        async with self.session.get(url) as resp:
            return await resp.text()
    
    async def get_health(self) -> Dict:
        return await self.request("GET", "/health")
    
    async def get_ready(self) -> Dict:
        return await self.request("GET", "/ready")


async def demo_health_check(client: APIClient):
    """健康检查演示"""
    print("\n" + "=" * 60)
    print("Demo: Health Check")
    print("=" * 60)
    
    health = await client.get_health()
    print(f"✓ Health: {health['status']}")
    
    ready = await client.get_ready()
    print(f"✓ Ready: {ready['status']}")
    
    metrics = await client.get_metrics()
    print(f"✓ Metrics: {metrics['status']}")


async def demo_agent_crud(client: APIClient):
    """Agent CRUD 演示"""
    print("\n" + "=" * 60)
    print("Demo: Agent CRUD")
    print("=" * 60)
    
    # Create
    agent1 = await client.create_agent("Researcher", "Research AI trends", priority=30)
    print(f"✓ Created agent: {agent1['agent_id']}")
    
    agent2 = await client.create_agent("Writer", "Write technical docs", priority=50)
    print(f"✓ Created agent: {agent2['agent_id']}")
    
    # List
    agents = await client.list_agents()
    print(f"✓ Total agents: {len(agents)}")
    
    # Get
    agent = await client.get_agent(agent1['agent_id'])
    print(f"✓ Get agent: {agent['name']}")
    
    return [agent1['agent_id'], agent2['agent_id']]


async def demo_tasks(client: APIClient, agent_ids: list):
    """Task 演示"""
    print("\n" + "=" * 60)
    print("Demo: Task Submission")
    print("=" * 60)
    
    for agent_id in agent_ids:
        task = await client.submit_task(agent_id, "Introduce yourself")
        print(f"✓ Task submitted: {task['task_id']}")
        
        result = await client.get_task_result(task['task_id'])
        print(f"  Result: {result.get('result', 'pending')[:50]}...")


async def demo_context(client: APIClient, agent_id: str):
    """Context 演示"""
    print("\n" + "=" * 60)
    print("Demo: Context Management")
    print("=" * 60)
    
    # Add context
    await client.add_context(agent_id, "User prefers Python")
    print(f"✓ Context added")
    
    await client.add_context(agent_id, "User is working on AI agents")
    print(f"✓ Another context added")
    
    # Get context
    context = await client.get_context(agent_id)
    print(f"✓ Total contexts: {len(context)}")


async def demo_metrics(client: APIClient):
    """Metrics 演示"""
    print("\n" + "=" * 60)
    print("Demo: Metrics")
    print("=" * 60)
    
    metrics = await client.get_metrics()
    print(f"✓ Status: {metrics.get('status')}")
    print(f"✓ Active Agents: {metrics.get('active_agents', 'N/A')}")
    
    # Prometheus format
    prom = await client.get_prometheus_metrics()
    lines = prom.strip().split('\n')[:5]
    print(f"✓ Prometheus metrics (first 5):")
    for line in lines:
        if not line.startswith('#'):
            print(f"  {line[:60]}...")


async def demo_cleanup(client: APIClient, agent_ids: list):
    """清理演示"""
    print("\n" + "=" * 60)
    print("Demo: Cleanup")
    print("=" * 60)
    
    for agent_id in agent_ids:
        result = await client.delete_agent(agent_id)
        print(f"✓ Deleted: {agent_id}")


async def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Agent OS Kernel - Complete API Demo")
    print("=" * 60)
    
    client = APIClient()
    
    try:
        await client.connect()
        
        # Demos
        await demo_health_check(client)
        
        agent_ids = await demo_agent_crud(client)
        
        await demo_tasks(client, agent_ids)
        
        if agent_ids:
            await demo_context(client, agent_ids[0])
        
        await demo_metrics(client)
        
        await demo_cleanup(client, agent_ids)
        
        print("\n" + "=" * 60)
        print("✅ API Demo Complete!")
        print("=" * 60)
        
    except aiohttp.ClientError as e:
        print(f"\n⚠️  API server not running at {BASE_URL}")
        print("   Please start the server first:")
        print("   python -m agent_os_kernel serve --port 8000")
        print(f"\n   Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())

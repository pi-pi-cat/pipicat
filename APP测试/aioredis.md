from fastapi import FastAPI, Depends
from aioredis import Redis, from_url
from contextlib import asynccontextmanager

class RedisManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.redis = None
        return cls._instance

    async def connect(self):
        if self.redis is None:
            self.redis = await from_url(
                "redis://localhost",
                encoding="utf-8",
                decode_responses=True,
                max_connections=10
            )

    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def get_redis(self) -> Redis:
        if self.redis is None:
            await self.connect()
        return self.redis

# 全局 RedisManager 实例
redis_manager = RedisManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    yield
    await redis_manager.disconnect()

app = FastAPI(lifespan=lifespan)

async def get_redis() -> Redis:
    return await redis_manager.get_redis()

@app.get("/example")
async def example_route(redis: Redis = Depends(get_redis)):
    await redis.set("key", "value")
    value = await redis.get("key")
    return {"value": value}

# 在其他地方使用 RedisManager
@app.get("/another-example")
async def another_example():
    redis = await RedisManager().get_redis()
    # 使用 redis ...
    return {"message": "Using Redis in another route"}



### REDIS


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aioredis
import json
from typing import Dict, Any

app = FastAPI()

# 创建 Redis 连接
redis = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)

class TaskResult(BaseModel):
    status: str
    detail: Dict[str, int]
    case_result: Dict[str, Dict[str, Any]]

@app.post("/task/{task_id}/complete")
async def complete_task(task_id: str, result: TaskResult):
    # 将整个任务结果序列化为 JSON
    result_json = result.json()
    
    # 在 Redis 中保存结果，使用 task_id 作为键
    await redis.set(f"task:{task_id}", result_json)
    
    # 可以设置一个过期时间，例如 24 小时
    await redis.expire(f"task:{task_id}", 60 * 60 * 24)
    
    return {"message": "Task result saved successfully"}

@app.get("/task/{task_id}")
async def get_task_result(task_id: str):
    # 从 Redis 中获取结果
    result_json = await redis.get(f"task:{task_id}")
    
    if result_json is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # 将 JSON 字符串解析回 Python 对象
    result = json.loads(result_json)
    
    return result

# 添加一个删除任务结果的端点
@app.delete("/task/{task_id}")
async def delete_task_result(task_id: str):
    # 从 Redis 中删除结果
    deleted = await redis.delete(f"task:{task_id}")
    
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task result deleted successfully"}




# 上下文环境使用教程
from contextlib import contextmanager, asynccontextmanager
import asyncio

# 同步上下文管理器示例
@contextmanager
def file_manager(filename):
    print(f"Opening file: {filename}")
    file = open(filename, 'w')
    try:
        yield file
    finally:
        print(f"Closing file: {filename}")
        file.close()

# 使用同步上下文管理器
def use_sync_context():
    with file_manager("test.txt") as f:
        f.write("Hello, World!")
    print("File operation completed.")

# 异步上下文管理器示例
@asynccontextmanager
async def async_resource_manager():
    print("Acquiring resource...")
    await asyncio.sleep(1)  # 模拟异步操作
    resource = "Async Resource"
    try:
        yield resource
    finally:
        print("Releasing resource...")
        await asyncio.sleep(1)  # 模拟异步清理操作

# 使用异步上下文管理器
async def use_async_context():
    async with async_resource_manager() as resource:
        print(f"Using {resource}")
        await asyncio.sleep(1)  # 模拟异步操作
    print("Async operation completed.")

# 运行示例
if __name__ == "__main__":
    print("Synchronous context manager example:")
    use_sync_context()

    print("\nAsynchronous context manager example:")
    asyncio.run(use_async_context())
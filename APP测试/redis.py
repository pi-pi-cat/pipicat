import asyncio
import aioredis

async def increment_and_timed_decrement(redis, key, operation_time):
    # Lua脚本: 原子操作获取值并+1
    lua_script = """
    local current = redis.call('GET', KEYS[1])
    if current == false then
        redis.call('SET', KEYS[1], '1')
        return 1
    else
        local new = tonumber(current) + 1
        redis.call('SET', KEYS[1], tostring(new))
        return new
    end
    """
    
    # 执行Lua脚本
    result = await redis.eval(lua_script, keys=[key])
    print(f"Value after increment: {result}")
    
    # 创建一个任务来处理10秒后的减值
    decrement_task = asyncio.create_task(delayed_decrement(redis, key, 10))
    
    # 模拟实际操作时间
    await asyncio.sleep(operation_time)
    
    print(f"Operation completed after {operation_time} seconds")
    
    # 等待减值任务完成
    await decrement_task

async def delayed_decrement(redis, key, delay):
    await asyncio.sleep(delay)
    await redis.decr(key)
    new_value = await redis.get(key)
    print(f"Value decremented after {delay} seconds: {new_value}")

async def main():
    redis = await aioredis.create_redis_pool('redis://localhost')
    
    try:
        tasks = []
        for i in range(5):  # 创建5个并发任务，模拟不同的操作时间
            operation_time = 5 + i * 3  # 5, 8, 11, 14, 17 秒
            tasks.append(asyncio.create_task(increment_and_timed_decrement(redis, 'my_key', operation_time)))
        
        await asyncio.gather(*tasks)
    
    finally:
        redis.close()
        await redis.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())

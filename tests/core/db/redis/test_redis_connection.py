from redis.asyncio import Redis


async def test_redis_connection(redis: Redis):
    assert await redis.ping() is True


async def test_redis_set_and_get(redis: Redis):
    await redis.set("test:key", "test-value")

    value = await redis.get("test:key")

    assert value == "test-value"
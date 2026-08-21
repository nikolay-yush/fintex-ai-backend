from collections.abc import AsyncGenerator

import pytest_asyncio
from redis.asyncio import Redis

from app.core.settings import settings


@pytest_asyncio.fixture
async def redis() -> AsyncGenerator[Redis, None]:
    client = Redis.from_url(
        settings.redis.URL,
        decode_responses=True,
    )

    try:
        await client.ping()
        yield client
    finally:
        await client.flushdb()
        await client.aclose()
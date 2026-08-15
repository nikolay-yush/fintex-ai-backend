from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.core.security.brute_force import (
    BruteForceProtection,
)
from app.core.db.redis.client import get_redis


async def get_brute_force_protection(
    redis: Annotated[
        Redis,
        Depends(get_redis),
    ],
) -> BruteForceProtection:
    return BruteForceProtection(redis)
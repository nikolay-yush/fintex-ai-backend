from redis.asyncio import Redis


class BruteForceProtection:
    def __init__(
        self,
        redis: Redis,
        base_delay: int = 1,
        max_delay: int = 30,
        window_seconds: int = 300,
    ) -> None:
        self.redis = redis
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.window_seconds = window_seconds

    @staticmethod
    def _get_key(
        identifier: str,
        client_ip: str,
    ) -> str:
        return (
            f"auth:login:failures:"
            f"{identifier}:{client_ip}"
        )

    async def get_failure_count(
        self,
        identifier: str,
        client_ip: str,
    ) -> int:
        key = self._get_key(
            identifier,
            client_ip,
        )

        value = await self.redis.get(key)

        if value is None:
            return 0

        return int(value)

    async def record_failed_attempt(
        self,
        identifier: str,
        client_ip: str,
    ) -> int:
        key = self._get_key(
            identifier,
            client_ip,
        )

        attempts = await self.redis.incr(key)

        if attempts == 1:
            await self.redis.expire(
                key,
                self.window_seconds,
            )

        return attempts

    async def get_delay(
        self,
        identifier: str,
        client_ip: str,
    ) -> int:
        attempts = await self.get_failure_count(
            identifier,
            client_ip,
        )

        if attempts < 4:
            return 0

        delay = self.base_delay * (
            2 ** (attempts - 4)
        )

        return min(
            delay,
            self.max_delay,
        )

    async def reset_attempts(
        self,
        identifier: str,
        client_ip: str,
    ) -> None:
        key = self._get_key(
            identifier,
            client_ip,
        )

        await self.redis.delete(key)
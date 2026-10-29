from functools import wraps
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar

from fastapi import HTTPException, Request, status
from redis.exceptions import RedisError

from app.core.db.redis.client import redis_client


P = ParamSpec("P")
R = TypeVar("R")

RATE_LIMIT_SCRIPT = """
local current = redis.call("INCR", KEYS[1])

if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end

return current
"""


def rate_limit(
    max_requests: int,
    window_seconds: int,
    key_prefix: str,
) -> Callable[
    [Callable[P, Awaitable[R]]],
    Callable[P, Awaitable[R]],
]:
    if max_requests < 1:
        raise ValueError("max_requests must be >= 1")

    if window_seconds < 1:
        raise ValueError("window_seconds must be >= 1")

    if not key_prefix:
        raise ValueError("key_prefix must not be empty")

    def decorator(
        endpoint: Callable[P, Awaitable[R]],
    ) -> Callable[P, Awaitable[R]]:

        @wraps(endpoint)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            request = kwargs.get("request")

            if not isinstance(request, Request):
                request = next(
                    (arg for arg in args if isinstance(arg, Request)),
                    None,
                )

            if request is None:
                raise RuntimeError(
                    f"Rate limiter on '{endpoint.__name__}' requires "
                    "'request: Request' parameter."
                )

            if request.client is None:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Unable to determine client address.",
                )

            # Uses the direct connection IP.
            # Forwarded headers must be configured and trusted separately.
            client_ip = request.client.host
            key = f"rate_limit:{key_prefix}:{client_ip}"

            try:
                current_count = await redis_client.eval(
                    RATE_LIMIT_SCRIPT,
                    1,
                    key,
                    window_seconds,
                )
            except RedisError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Rate limiting service unavailable.",
                ) from exc

            if current_count > max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Try again later.",
                    headers={"Retry-After": str(window_seconds)},
                )

            return await endpoint(*args, **kwargs)

        return wrapper

    return decorator

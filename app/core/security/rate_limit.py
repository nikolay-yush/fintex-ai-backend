from functools import wraps
from typing import Any, Awaitable, Callable

from fastapi import HTTPException, Request, status

from app.core.db.redis.client import redis_client


def rate_limit(
    max_requests: int,
    window_seconds: int,
    key_prefix: str,
) -> Callable:
    def decorator(
        endpoint: Callable[..., Awaitable[Any]],
    ) -> Callable[..., Awaitable[Any]]:

        @wraps(endpoint)
        async def wrapper(
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            request: Request | None = kwargs.get("request")

            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request is None:
                raise RuntimeError(
                    f"Rate limiter on '{endpoint.__name__}' requires 'request: Request' "
                    "parameter in the endpoint signature."
                )

            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                client_ip = forwarded.split(",")[0].strip()
            elif request.client:
                client_ip = request.client.host
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to determine client address.",
                )

            key = f"rate_limit:{key_prefix}:{client_ip}"

            current_count = await redis_client.incr(key)

            if current_count == 1:
                await redis_client.expire(
                    key,
                    window_seconds,
                )

            if current_count > max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Try again later.",
                )

            return await endpoint(*args, **kwargs)

        return wrapper

    return decorator
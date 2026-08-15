import secrets
from typing import Annotated
from urllib.parse import urlparse

from fastapi import (
    Cookie,
    Header,
    HTTPException,
    Request,
    status,
)

from app.core.settings import settings


MUTATING_METHODS = {
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
}


async def require_csrf(
    csrf_cookie: Annotated[
        str | None,
        Cookie(
            alias="csrf_token",
        ),
    ] = None,
    csrf_header: Annotated[
        str | None,
        Header(
            alias="X-CSRF-Token",
        ),
    ] = None,
) -> None:

    if csrf_cookie is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        )

    if csrf_header is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        )

    if not secrets.compare_digest(
        csrf_cookie,
        csrf_header,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed",
        )


async def require_origin(
    request: Request,
) -> None:

    if request.method not in MUTATING_METHODS:
        return

    origin = request.headers.get("origin")

    # Prefer Origin when the browser provides it.
    if origin is not None:

        if origin not in settings.app.ALLOWED_ORIGINS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid origin",
            )

        return

    # Origin is absent → fallback to Referer.
    referer = request.headers.get("referer")

    if referer is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Origin or Referer header required",
        )

    parsed_referer = urlparse(
        referer,
    )

    referer_origin = (
        f"{parsed_referer.scheme}://"
        f"{parsed_referer.netloc}"
    )

    if referer_origin not in settings.app.ALLOWED_ORIGINS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid referer",
        )
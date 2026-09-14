import pytest
from fastapi import HTTPException, Request

from app.core.security.csrf import (
    create_csrf_token,
    require_csrf,
)


class TestCSRF:
    """Tests for CSRF protection."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method",
        ["POST", "PUT", "PATCH", "DELETE"],
    )
    async def test_mutating_methods_require_csrf(
        self,
        http_request,
        method: str,
    ):
        http_request.scope["method"] = method

        with pytest.raises(HTTPException) as exc_info:
            await require_csrf(
                request=http_request,
                csrf_cookie=None,
                csrf_header=None,
            )

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "CSRF validation failed"

    @pytest.mark.asyncio
    async def test_valid_csrf_token(self, http_request: Request):
        token = create_csrf_token()

        await require_csrf(
            request=http_request,
            csrf_cookie=token,
            csrf_header=token,
        )

    @pytest.mark.asyncio
    async def test_missing_cookie_token(self, http_request: Request):
        token = create_csrf_token()

        with pytest.raises(HTTPException) as exc_info:
            await require_csrf(
                request=http_request,
                csrf_cookie=None,
                csrf_header=token,
            )

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "CSRF validation failed"

    @pytest.mark.asyncio
    async def test_missing_header_token(self, http_request: Request):
        token = create_csrf_token()

        with pytest.raises(HTTPException) as exc_info:
            await require_csrf(
                request=http_request,
                csrf_cookie=token,
                csrf_header=None,
            )

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "CSRF validation failed"

    @pytest.mark.asyncio
    async def test_different_csrf_tokens(self, http_request: Request):
        cookie_token = create_csrf_token()
        header_token = create_csrf_token()

        with pytest.raises(HTTPException) as exc_info:
            await require_csrf(
                request=http_request,
                csrf_cookie=cookie_token,
                csrf_header=header_token,
            )

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "CSRF validation failed"

    @pytest.mark.asyncio
    async def test_empty_cookie_token(self, http_request: Request):
        token = create_csrf_token()

        with pytest.raises(HTTPException) as exc_info:
            await require_csrf(
                request=http_request,
                csrf_cookie="",
                csrf_header=token,
            )

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_empty_header_token(self, http_request: Request):
        token = create_csrf_token()

        with pytest.raises(HTTPException) as exc_info:
            await require_csrf(
                request=http_request,
                csrf_cookie=token,
                csrf_header="",
            )

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_does_not_require_csrf(
        self,
        http_request: Request,
    ):
        http_request.scope["method"] = "GET"

        await require_csrf(
            request=http_request,
            csrf_cookie=None,
            csrf_header=None,
        )
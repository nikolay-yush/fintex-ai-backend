import pytest

from fastapi import HTTPException, Request

from app.core.security.csrf import require_origin


class TestOrigin:
    @pytest.fixture
    def request(self):
        return Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/",
                "headers": [],
            }
        )

    async def test_allowed_origin(self, request, monkeypatch):
        request.scope["headers"] = [
            (b"origin", b"http://localhost:3000"),
        ]

        monkeypatch.setattr(
            "app.core.security.csrf.settings.app.ALLOWED_ORIGINS",
            {"http://localhost:3000"},
        )

        assert await require_origin(request) is None

    async def test_forbidden_origin(self, request, monkeypatch):
        request.scope["headers"] = [
            (b"origin", b"https://evil.example.com"),
        ]

        monkeypatch.setattr(
            "app.core.security.csrf.settings.app.ALLOWED_ORIGINS",
            {"http://localhost:3000"},
        )

        with pytest.raises(HTTPException) as exc:
            await require_origin(request)

        assert exc.value.status_code == 403
        assert exc.value.detail == "Invalid origin"

    async def test_missing_origin_allowed_referer(self, request, monkeypatch):
        request.scope["headers"] = [
            (
                b"referer",
                b"http://localhost:3000/login",
            ),
        ]

        monkeypatch.setattr(
            "app.core.security.csrf.settings.app.ALLOWED_ORIGINS",
            {"http://localhost:3000"},
        )

        assert await require_origin(request) is None

    async def test_missing_origin_and_referer(self, request):
        with pytest.raises(HTTPException) as exc:
            await require_origin(request)

        assert exc.value.status_code == 403
        assert exc.value.detail == "Origin or Referer header required"

    async def test_forbidden_referer(self, request, monkeypatch):
        request.scope["headers"] = [
            (
                b"referer",
                b"https://evil.example.com/login",
            ),
        ]

        monkeypatch.setattr(
            "app.core.security.csrf.settings.app.ALLOWED_ORIGINS",
            {"http://localhost:3000"},
        )

        with pytest.raises(HTTPException) as exc:
            await require_origin(request)

        assert exc.value.status_code == 403
        assert exc.value.detail == "Invalid referer"

    async def test_origin_has_priority_over_referer(
        self,
        request,
        monkeypatch,
    ):
        request.scope["headers"] = [
            (b"origin", b"https://evil.example.com"),
            (
                b"referer",
                b"http://localhost:3000/login",
            ),
        ]

        monkeypatch.setattr(
            "app.core.security.csrf.settings.app.ALLOWED_ORIGINS",
            {"http://localhost:3000"},
        )

        with pytest.raises(HTTPException) as exc:
            await require_origin(request)

        assert exc.value.status_code == 403
        assert exc.value.detail == "Invalid origin"

    async def test_safe_method_skips_origin_check(
        self,
        monkeypatch,
    ):
        request = Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/",
                "headers": [],
            }
        )

        monkeypatch.setattr(
            "app.core.security.csrf.settings.app.ALLOWED_ORIGINS",
            {"http://localhost:3000"},
        )

        assert await require_origin(request) is None
from fastapi import Request, Response

from app.core.settings import settings


def add_csp_report_only(response: Response) -> None:
    csp_directives = {
        "default-src": "'self'",
        "script-src": "'self' https://cdn.jsdelivr.net 'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY='",
        "style-src": "'self' https://cdn.jsdelivr.net 'unsafe-inline'",
        "img-src": "'self' data: https://fastapi.tiangolo.com",
        "font-src": "'self' data:",
        "connect-src": "'self'",
        "object-src": "'none'",
        "base-uri": "'self'",
        "frame-ancestors": "'none'",
    }
    
    response.headers["Content-Security-Policy"] = "; ".join(
        f"{directive} {sources}" for directive, sources in csp_directives.items()
    )


def add_security_headers(response: Response) -> None:
    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["X-Frame-Options"] = "DENY"

    response.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )

    response.headers["Permissions-Policy"] = (
        "camera=(), "
        "microphone=(), "
        "geolocation=()"
    )

    if settings.app.HOST_PROTOCOL == "https":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    add_csp_report_only(response)


async def security_headers_middleware(
    request: Request,
    call_next,
) -> Response:
    response = await call_next(request)

    add_security_headers(response)

    return response
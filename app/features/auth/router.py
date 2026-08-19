from typing import Annotated

from fastapi import APIRouter, Depends, Query, Cookie, Request, status, Response

from app.core.settings import settings
from app.core.security.csrf import require_csrf, require_origin
from app.core.security.rate_limit import rate_limit
from app.features.auth.dependencies import get_current_user
from app.features.auth.exceptions.refresh_token import InvalidRefreshTokenException, RefreshTokenNotFoundException
from app.features.auth.schemas.access_token import AccessTokenResponse
from app.features.auth.schemas.authentication import (
    TokenResponse,
    UserLogin,
)    
from app.features.auth.schemas.email_verification import ResendVerificationRequest
from app.features.auth.schemas.logout import LogoutAllRequest, LogoutRequest, LogoutSessionRequest
from app.features.auth.schemas.refresh_token import RefreshTokenRequest
from app.features.auth.schemas.registration import UserRegister     
from app.features.auth.schemas.password_reset import (
    ForgotPasswordRequest,
    PasswordResetConfirm,
)

from app.features.auth.security import create_csrf_token
from app.features.auth.services.dependencies import (
    get_email_verification_service,
    get_login_service,
    get_logout_service,
    get_password_reset_service,
    get_refresh_token_service,
    get_registration_service,
)
from app.features.auth.services.email_verification import (
    EmailVerificationService,
)
from app.features.auth.services.login import LoginService
from app.features.auth.services.logout import LogoutService
from app.features.auth.services.password_reset import (
    PasswordResetService,
)
from app.features.auth.services.refresh_token import (
    RefreshTokenService,
)
from app.features.auth.services.registration import (
    RegistrationService,
)
from app.features.users.models import User
from app.features.users.schemas import UserResponse


auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


# ============================================================================
# Authentication
# ============================================================================

@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserRegister,
    service: Annotated[
        RegistrationService,
        Depends(get_registration_service),
    ],
):
    return await service.register(data)


@auth_router.post(
    "/login",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_origin),
    ],
)
@rate_limit(max_requests=5, window_seconds=60, key_prefix="login")
async def login(
    request: Request,
    data: UserLogin,
    response: Response,
    service: Annotated[
        LoginService,
        Depends(get_login_service),
    ],
) -> AccessTokenResponse:
    client_ip = (
        request.client.host
        if request.client is not None
        else "unknown"
    )   
    tokens = await service.login(
        data,
        client_ip,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=settings.app.COOKIE_SECURE,
        samesite="lax",
        path="/api/v1/auth",
        max_age=settings.jwt.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    csrf_token = create_csrf_token()

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=settings.app.COOKIE_SECURE,
        samesite="lax",
        path="/api/v1/auth",
        max_age=settings.jwt.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return AccessTokenResponse(
        access_token=tokens.access_token,
    )

@auth_router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_csrf),
        Depends(require_origin)
    ],
)
async def refresh_token(
    response: Response,
    service: Annotated[
        RefreshTokenService,
        Depends(get_refresh_token_service),
    ],
    refresh_token: Annotated[
        str | None,
        Cookie(description="Refresh token from cookie"),
    ] = None,
) -> AccessTokenResponse:
    if not refresh_token:
        raise InvalidRefreshTokenException("Refresh token is missing")

    tokens = await service.refresh_access_token(
        refresh_token=refresh_token,
    )

    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=settings.app.COOKIE_SECURE,
        samesite="lax",
        path="/api/v1/auth",
        max_age=settings.jwt.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return AccessTokenResponse(
        access_token=tokens.access_token,
    )

@auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=dict,
    dependencies=[
        Depends(require_csrf),
        Depends(require_origin),
    ],
)
async def logout(
    response: Response,
    logout_service: Annotated[
        LogoutService,
        Depends(get_logout_service),
    ],
    refresh_token: Annotated[
        str | None,
        Cookie(
            description="Refresh token from cookie",
        ),
    ] = None,
) -> dict[str, str]:

    if not refresh_token:
        raise RefreshTokenNotFoundException()

    await logout_service.logout(
        refresh_token=refresh_token,
    )

    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
    )

    response.delete_cookie(
        key="csrf_token",
        path="/",
    )

    return {
        "message": "Logged out successfully",
    }


@auth_router.post(
    "/logout-session",
    status_code=status.HTTP_200_OK,
    response_model=dict,
    dependencies=[
        Depends(require_csrf),
        Depends(require_origin),
    ],
)
async def logout_session(
    data: LogoutSessionRequest,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    logout_service: Annotated[
        LogoutService,
        Depends(get_logout_service),
    ],
) -> dict[str, str]:

    await logout_service.logout_session(
        token_family=data.token_family,
        user_id=current_user.id,
    )

    return {
        "message": "Session logged out successfully",
    }


@auth_router.post(
    "/logout-all",
    status_code=status.HTTP_200_OK,
    response_model=dict,
    dependencies=[
        Depends(require_csrf),
        Depends(require_origin),
    ],
)
async def logout_all(
    response: Response,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    logout_service: Annotated[
        LogoutService,
        Depends(get_logout_service),
    ],
) -> dict[str, str]:

    await logout_service.logout_all_user_sessions(
        user_id=current_user.id,
    )

    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
    )

    response.delete_cookie(
        key="csrf_token",
        path="/",
    )

    return {
        "message": "All sessions logged out successfully",
    }
# ============================================================================
# Email verification
# ============================================================================

@auth_router.get(
    "/verify-email",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
@rate_limit(
    max_requests=3,
    window_seconds=3600,
    key_prefix="verification_email",
)
async def verify_email(
    token: Annotated[
        str,
        Query(description="Email verification token"),
    ],
    service: Annotated[
        EmailVerificationService,
        Depends(get_email_verification_service),
    ],
):
    await service.verify_email(
        token=token,
    )

    return {
        "message": "Email successfully verified",
    }


@auth_router.post(
    "/resend-verification",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
@rate_limit(
    max_requests=3,
    window_seconds=3600,
    key_prefix="resend-verification",
)
async def resend_verification_email(
    data: ResendVerificationRequest,
    service: Annotated[
        EmailVerificationService,
        Depends(get_email_verification_service),
    ],
):
    await service.resend_verification_email(
        email=data.email,
    )

    return {
        "message": "Verification email sent",
    }


# ============================================================================
# Password recovery
# ============================================================================

@auth_router.post(
    "/forgot-password",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
@rate_limit(
    max_requests=5,
    window_seconds=900,
    key_prefix="forgot_password",
)
async def forgot_password(
    data: ForgotPasswordRequest,
    service: Annotated[
        PasswordResetService,
        Depends(get_password_reset_service),
    ],
) -> dict[str, str]:

    await service.request_password_reset(
        email=data.email,
    )

    return {
        "message": (
            "If an account with this email exists, "
            "a password reset email has been sent."
        ),
    }


@auth_router.post(
    "/reset-password",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
@rate_limit(
    max_requests=10,
    window_seconds=900,
    key_prefix="reset_password",
)
async def reset_password(
    data: PasswordResetConfirm,
    service: Annotated[
        PasswordResetService,
        Depends(get_password_reset_service),
    ],
) -> dict[str, str]:

    await service.reset_password(
        data=data,
    )

    return {
        "message": "Password successfully changed.",
    }
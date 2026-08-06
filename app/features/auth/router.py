from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.features.auth.schemas.authentication import (
    TokenResponse,
    UserLogin,
)    
from app.features.auth.schemas.email_verification import ResendVerificationRequest
from app.features.auth.schemas.refresh_token import RefreshTokenRequest
from app.features.auth.schemas.registration import UserRegister     
from app.features.auth.schemas.password_reset import (
    ForgotPasswordRequest,
    PasswordResetConfirm,
)

from app.features.auth.services.dependencies import (
    get_email_verification_service,
    get_login_service,
    get_password_reset_service,
    get_refresh_token_service,
    get_registration_service,
)
from app.features.auth.services.email_verification import (
    EmailVerificationService,
)
from app.features.auth.services.login import LoginService
from app.features.auth.services.password_reset import (
    PasswordResetService,
)
from app.features.auth.services.refresh_token import (
    RefreshTokenService,
)
from app.features.auth.services.registration import (
    RegistrationService,
)
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
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    data: UserLogin,
    service: Annotated[
        LoginService,
        Depends(get_login_service),
    ],
):
    return await service.login(data)


@auth_router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    data: RefreshTokenRequest,
    service: Annotated[
        RefreshTokenService,
        Depends(get_refresh_token_service),
    ],
):
    return await service.refresh_access_token(
        refresh_token=data.refresh_token,
    )


# ============================================================================
# Email verification
# ============================================================================

@auth_router.get(
    "/verify-email",
    response_model=dict,
    status_code=status.HTTP_200_OK,
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
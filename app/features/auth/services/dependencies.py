from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.postgres.session import get_async_session
from app.core.email.dependencies import get_email_service
from app.core.email.service import EmailService

from app.core.security.brute_force import BruteForceProtection
from app.core.security.dependencies import get_brute_force_protection
from app.features.auth.services.logout import LogoutService
from app.features.users.dependencies import get_user_repo
from app.features.users.repository import UserRepository

from app.features.auth.repositories.dependencies import (
    get_email_verification_token_repo,
    get_password_reset_token_repo,
    get_refresh_token_repo,
)
from app.features.auth.repositories.email_verification_token import (
    EmailVerificationTokenRepository,
)
from app.features.auth.repositories.password_reset_token import (
    PasswordResetTokenRepository,
)
from app.features.auth.repositories.refresh_token import (
    RefreshTokenRepository,
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


def get_registration_service(
    db_async_session: AsyncSession = Depends(get_async_session),
    user_repo: UserRepository = Depends(get_user_repo),
    verification_token_repo: EmailVerificationTokenRepository = Depends(
        get_email_verification_token_repo,
    ),
    email_service: EmailService = Depends(get_email_service),
) -> RegistrationService:
    return RegistrationService(
        db_async_session=db_async_session,
        user_repo=user_repo,
        verification_token_repo=verification_token_repo,
        email_service=email_service,
    )


def get_login_service(
    db_async_session: AsyncSession = Depends(get_async_session),
    user_repo: UserRepository = Depends(get_user_repo),
    refresh_token_repo: RefreshTokenRepository = Depends(
        get_refresh_token_repo,
    ),
    brute_force_protection: BruteForceProtection = Depends(
        get_brute_force_protection,
    ),
) -> LoginService:
    return LoginService(
        db_async_session=db_async_session,
        user_repo=user_repo,
        refresh_token_repo=refresh_token_repo,
        brute_force_protection=brute_force_protection,
    )

def get_logout_service(
    db_async_session: AsyncSession = Depends(get_async_session),
    refresh_token_repo: RefreshTokenRepository = Depends(
        get_refresh_token_repo,
    ),
) -> LogoutService:
    return LogoutService(
        db_async_session=db_async_session,
        refresh_token_repo=refresh_token_repo,
    )


def get_email_verification_service(
    db_async_session: AsyncSession = Depends(get_async_session),
    user_repo: UserRepository = Depends(get_user_repo),
    verification_token_repo: EmailVerificationTokenRepository = Depends(
        get_email_verification_token_repo,
    ),
    email_service: EmailService = Depends(get_email_service),
) -> EmailVerificationService:
    return EmailVerificationService(
        db_async_session=db_async_session,
        user_repo=user_repo,
        verification_token_repo=verification_token_repo,
        email_service=email_service,
    )


def get_password_reset_service(
    db_async_session: AsyncSession = Depends(get_async_session),
    user_repo: UserRepository = Depends(get_user_repo),
    password_reset_token_repo: PasswordResetTokenRepository = Depends(
        get_password_reset_token_repo,
    ),
    email_service: EmailService = Depends(get_email_service),
) -> PasswordResetService:
    return PasswordResetService(
        db_async_session=db_async_session,
        user_repo=user_repo,
        password_reset_token_repo=password_reset_token_repo,
        email_service=email_service,
    )


def get_refresh_token_service(
    db_async_session: AsyncSession = Depends(get_async_session),
    user_repo: UserRepository = Depends(get_user_repo),
    refresh_token_repo: RefreshTokenRepository = Depends(
        get_refresh_token_repo,
    ),
) -> RefreshTokenService:
    return RefreshTokenService(
        db_async_session=db_async_session,
        user_repo=user_repo,
        refresh_token_repo=refresh_token_repo,
    )
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.postgres.session import get_async_session

from .email_verification_token import (
    EmailVerificationTokenRepository,
)
from .password_reset_token import (
    PasswordResetTokenRepository,
)
from .refresh_token import (
    RefreshTokenRepository,
)


def get_refresh_token_repo(
    db_async_session: AsyncSession = Depends(get_async_session),
) -> RefreshTokenRepository:
    return RefreshTokenRepository(
        db_async_session=db_async_session,
    )


def get_email_verification_token_repo(
    db_async_session: AsyncSession = Depends(get_async_session),
) -> EmailVerificationTokenRepository:
    return EmailVerificationTokenRepository(
        db_async_session=db_async_session,
    )


def get_password_reset_token_repo(
    db_async_session: AsyncSession = Depends(get_async_session),
) -> PasswordResetTokenRepository:
    return PasswordResetTokenRepository(
        db_async_session=db_async_session,
    )
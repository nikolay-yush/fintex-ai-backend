from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.email.service import EmailService
from app.features.auth.exceptions import (
    EmailAlreadyVerifiedException,
    EmailVerificationTokenExpiredException,
    EmailVerificationTokenNotFoundException,
    FailedToCreateVerificationTokenException,
)
from app.features.auth.repositories.email_verification_token import (
    EmailVerificationTokenRepository,
)
from app.features.auth.security import (
    create_email_verification_token,
)
from app.features.users.exceptions import UserNotFoundException
from app.features.users.repository import UserRepository


class EmailVerificationService:
    def __init__(
        self,
        db_async_session: AsyncSession,
        user_repo: UserRepository,
        verification_token_repo: EmailVerificationTokenRepository,
        email_service: EmailService,
    ) -> None:
        self.db_async_session = db_async_session
        self.user_repo = user_repo
        self.verification_token_repo = verification_token_repo
        self.email_service = email_service

    async def verify_email(
        self,
        token: str,
    ) -> None:
        # Find verification token
        verification_token = (
            await self.verification_token_repo.get_verification_token(
                token,
            )
        )

        if verification_token is None:
            raise EmailVerificationTokenNotFoundException()

        # Check expiration
        now = datetime.now(timezone.utc)

        if verification_token.expires_at < now:
            raise EmailVerificationTokenExpiredException()

        # Find user
        user = await self.user_repo.get_one_by_id(
            verification_token.user_id,
        )

        if user is None:
            raise UserNotFoundException()

        # Verify email
        user.email_verified = True

        # Delete token
        await self.verification_token_repo.delete_verification_token_by_id(
            verification_token.id,
        )

        # Commit transaction
        await self.db_async_session.commit()

    async def resend_verification_email(
        self,
        email: str,
    ) -> None:
        # Find user
        user = await self.user_repo.get_user_by_email(
            email,
        )

        if user is None:
            raise UserNotFoundException()

        # Check if already verified
        if user.email_verified:
            raise EmailAlreadyVerifiedException()

        # Delete old token
        old_token = (
            await self.verification_token_repo.get_verification_token_by_user_id(
                user.id,
            )
        )

        if old_token is not None:
            await self.verification_token_repo.delete_verification_token_by_id(
                old_token.id,
            )

        # Generate verification token
        verification_token = create_email_verification_token()

        if verification_token is None:
            raise FailedToCreateVerificationTokenException()

        # Save verification token
        await self.verification_token_repo.create_verification_token(
            {
                "token": verification_token,
                "user_id": user.id,
                "expires_at": (
                    datetime.now(timezone.utc)
                    + timedelta(hours=24)
                ),
            },
        )

        # Commit transaction
        await self.db_async_session.commit()

        # Send verification email
        await self.email_service.send_verification_email(
            recipient=user.email,
            token=verification_token,
        )
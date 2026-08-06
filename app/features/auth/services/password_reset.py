from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.email.service import EmailService
from app.features.auth.exceptions import (
    PasswordResetTokenExpiredException,
    PasswordResetTokenNotFoundException,
)
from app.features.auth.repositories.password_reset_token import (
    PasswordResetTokenRepository,
)
from app.features.auth.schemas import PasswordResetConfirm
from app.features.auth.security import (
    create_email_verification_token,
    hash_password,
)
from app.features.users.exceptions import UserNotFoundException
from app.features.users.repository import UserRepository


class PasswordResetService:
    def __init__(
        self,
        db_async_session: AsyncSession,
        user_repo: UserRepository,
        password_reset_token_repo: PasswordResetTokenRepository,
        email_service: EmailService,
    ) -> None:
        self.db_async_session = db_async_session
        self.user_repo = user_repo
        self.password_reset_token_repo = (
            password_reset_token_repo
        )
        self.email_service = email_service

    async def request_password_reset(
        self,
        email: str,
    ) -> None:
        # Find user
        user = await self.user_repo.get_user_by_email(
            email,
        )

        if user is None:
            raise UserNotFoundException()

        # Delete old token
        old_token = (
            await self.password_reset_token_repo.get_reset_token_by_user_id(
                user.id,
            )
        )

        if old_token is not None:
            await self.password_reset_token_repo.delete_reset_token_by_id(
                old_token.id,
            )

        # Generate reset token
        reset_token = create_email_verification_token()

        # Save reset token
        await self.password_reset_token_repo.create_reset_token(
            {
                "token": reset_token,
                "user_id": user.id,
                "expires_at": (
                    datetime.now(timezone.utc)
                    + timedelta(hours=1)
                ),
                "created_at": datetime.now(
                    timezone.utc,
                ),
            },
        )

        # Commit transaction
        await self.db_async_session.commit()

        # Send email
        await self.email_service.send_reset_password_email(
            recipient=user.email,
            token=reset_token,
        )

    async def reset_password(
        self,
        data: PasswordResetConfirm,
    ) -> None:
        # Find reset token
        reset_token = (
            await self.password_reset_token_repo.get_reset_token(
                data.token,
            )
        )

        if reset_token is None:
            raise PasswordResetTokenNotFoundException()

        # Check expiration
        now = datetime.now(timezone.utc)

        if reset_token.expires_at < now:
            raise PasswordResetTokenExpiredException()

        # Find user
        user = await self.user_repo.get_one_by_id(
            reset_token.user_id,
        )

        if user is None:
            raise UserNotFoundException()

        # Update password
        user.hashed_password = hash_password(
            data.password,
        )

        # Delete token
        await self.password_reset_token_repo.delete_reset_token_by_id(
            reset_token.id,
        )

        # Commit transaction
        await self.db_async_session.commit()
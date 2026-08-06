from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.email.service import EmailService
from app.features.auth.exceptions import (
    FailedToCreateUserException,
    FailedToCreateVerificationTokenException,
    UserAlreadyExistsException,
)
from app.features.auth.repositories.email_verification_token import (
    EmailVerificationTokenRepository,
)
from app.features.auth.schemas import UserRegister
from app.features.auth.security import (
    create_email_verification_token,
    hash_password,
)
from app.features.users.repository import UserRepository


class RegistrationService:
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

    async def register(
        self,
        data: UserRegister,
    ):
        # Check if user already exists
        existing_user = await self.user_repo.get_user_by_email(
            data.email,
        )

        if existing_user is not None:
            raise UserAlreadyExistsException()

        # Prepare user data
        values = data.model_dump()

        # Hash password
        values["hashed_password"] = hash_password(
            values.pop("password"),
        )

        # Create user
        user = await self.user_repo.create_one(
            values,
        )

        if user is None:
            raise FailedToCreateUserException()

        # Generate verification token
        verification_token = create_email_verification_token()

        if verification_token is None:
            raise FailedToCreateVerificationTokenException()

        # Save verification token
        await self.verification_token_repo.create_one(
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

        return user
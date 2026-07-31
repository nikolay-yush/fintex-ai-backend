from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.email.service import EmailService
from app.features.auth.exceptions import (
    EmailAlreadyVerifiedException,
    EmailVerificationTokenExpiredException,
    EmailVerificationTokenNotFoundException,
    FailedToCreateUserException,
    InvalidCredentialsException,
    UserAlreadyExistsException,
)
from app.features.auth.repo import AuthRepository
from app.features.auth.schemas import (
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.features.auth.security import (
    create_access_token,
    create_email_verification_token,
    hash_password,
    verify_password,
)
from app.features.users.exceptions import UserNotFoundException
from app.features.users.repo import UserRepository


class AuthService:
    def __init__(
        self,
        db_async_session: AsyncSession,
        auth_repo: AuthRepository,
        user_repo: UserRepository,
        email_service: EmailService,
    ) -> None:
        self.db_async_session = db_async_session
        self.auth_repo = auth_repo
        self.user_repo = user_repo
        self.email_service = email_service

    #  **** REGISTER OPERATIONS ****
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

        # Prepare data
        values = data.model_dump()

        # Hash password
        values["hashed_password"] = hash_password(
            values.pop("password"),
        )

        # Create user
        user = await self.user_repo.create_one(values)

        if user is None:
            raise FailedToCreateUserException()

        # Create email verification token
        verification_token = create_email_verification_token()

        await self.auth_repo.create_one(
            {
                "token": verification_token,
                "user_id": user.id,
                "expires_at": (
                    datetime.now(timezone.utc)
                    + timedelta(hours=24)
                ),
            }
        )

        # Commit transaction
        await self.db_async_session.commit()

        await self.email_service.send_verification_email(
            recipient=user.email,
            token=verification_token,
        )

        return user

    #  **** LOGIN OPERATIONS ****
    async def login(
        self,
        data: UserLogin,
    ) -> TokenResponse:
        user = await self.user_repo.get_user_by_email(
            data.email,
        )

        if user is None:
            raise InvalidCredentialsException()

        if not verify_password(
            data.password,
            user.hashed_password,
        ):
            raise InvalidCredentialsException()

        # Create access token
        access_token = create_access_token(
            user.id,
        )

        return TokenResponse(
            access_token=access_token,
        )

    #  **** EMAIL VERIFICATION OPERATIONS ****
    async def verify_email(
        self,
        token: str,
    ) -> None:
        verification_token = (
            await self.auth_repo.get_verification_token(
                token,
            )
        )

        if verification_token is None:
            raise EmailVerificationTokenNotFoundException()

        now = datetime.now(timezone.utc)

        if verification_token.expires_at < now:
            raise EmailVerificationTokenExpiredException()

        user = await self.user_repo.get_one_by_id(
            model_id=verification_token.user_id,
        )

        if user is None:
            raise EmailVerificationTokenNotFoundException()

        # Verify user email
        user.email_verified = True

        # Delete verification token
        await self.auth_repo.delete_one(
            verification_token.id,
        )

        # Commit transaction
        await self.db_async_session.commit()


    #  **** EMAIL VERIFICATION OPERATIONS ****

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

        # Check email verification
        if user.email_verified:
            raise EmailAlreadyVerifiedException()

        # Delete old verification token
        old_token = (
            await self.auth_repo.get_verification_token_by_user_id(
                user.id,
            )
        )

        if old_token is not None:
            await self.auth_repo.delete_one(
                old_token.id,
            )

        # Create new verification token
        await self.auth_repo.create_one(
            {
                "token": create_email_verification_token(),
                "user_id": user.id,
                "expires_at": (
                    datetime.now(timezone.utc)
                    + timedelta(hours=24)
                ),
            },
        )

        # Commit transaction
        await self.db_async_session.commit()

    
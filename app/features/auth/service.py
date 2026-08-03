from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.core.email.service import EmailService
from app.features.auth.exceptions import (
    EmailAlreadyVerifiedException,
    EmailVerificationTokenExpiredException,
    EmailVerificationTokenNotFoundException,
    FailedToCreateUserException,
    FailedToCreateVerificationTokenException,
    InvalidCredentialsException,
    InvalidRefreshTokenException,
    PasswordResetTokenExpiredException,
    PasswordResetTokenNotFoundException,
    RefreshTokenExpiredException,
    UserAlreadyExistsException,
    UserBannedException,
    UserInactiveException,
)
from app.features.auth.repo import AuthRepository
from app.features.auth.schemas import (
    PasswordResetConfirm,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.features.auth.security import (
    create_access_token,
    create_email_verification_token,
    create_refresh_token,
    decode_refresh_token,
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

        if verification_token is None:
            raise FailedToCreateVerificationTokenException()

        # Create verification token
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

        # Send verification email
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

        # Find user
        user = await self.user_repo.get_user_by_email(
            data.email,
        )

        if user is None:
            raise InvalidCredentialsException()

        # Verify password
        if not verify_password(
            data.password,
            user.hashed_password,
        ):
            raise InvalidCredentialsException()

        # Delete old refresh token
        old_refresh_token = (
            await self.auth_repo.get_refresh_token_by_user_id(
                user.id,
            )
        )

        if old_refresh_token is not None:
            await self.auth_repo.delete_one(
                old_refresh_token.id,
            )

        # Create refresh token
        refresh_token = create_refresh_token(
            user.id,
        )

        # Save refresh token
        await self.auth_repo.create_one(
            {
                "token": refresh_token,
                "user_id": user.id,
                "expires_at": (
                    datetime.now(timezone.utc)
                    + timedelta(
                        days=settings.jwt.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
                    )
                ),
                "created_at": datetime.now(
                    timezone.utc,
                ),
            },
        )

        # Create access token
        access_token = create_access_token(
            user.id,
        )

        # Commit transaction
        await self.db_async_session.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
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
        verification_token = create_email_verification_token()

        if verification_token is None:
            raise FailedToCreateVerificationTokenException()

        # Create new verification token
        await self.auth_repo.create_one(
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


    #  **** PASSWORD RESET OPERATIONS ****
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

        # Delete old reset token
        old_token = (
            await self.auth_repo.get_reset_token_by_user_id(
                user.id,
            )
        )

        if old_token is not None:
            await self.auth_repo.delete_one(
                old_token.id,
            )

        # Create new reset token
        reset_token = create_email_verification_token()

        await self.auth_repo.create_one(
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

        # Send reset password email
        await self.email_service.send_reset_password_email(
            recipient=user.email,
            token=reset_token,
        )

     #  **** PASSWORD RESET OPERATIONS ****
    async def reset_password(
        self,
        data: PasswordResetConfirm,
    ) -> None:

        # Find reset token
        reset_token = (
            await self.auth_repo.get_reset_token(
                data.token,
            )
        )

        if reset_token is None:
            raise PasswordResetTokenNotFoundException()

        now = datetime.now(timezone.utc)

        # Check token expiration
        if reset_token.expires_at < now:
            raise PasswordResetTokenExpiredException()

        # Find user
        user = await self.user_repo.get_one_by_id(
            model_id=reset_token.user_id,
        )

        if user is None:
            raise UserNotFoundException()

        # Update password
        user.hashed_password = hash_password(
            data.password,
        )

        # Delete reset token
        await self.auth_repo.delete_one(
            reset_token.id,
        )

        # Commit transaction
        await self.db_async_session.commit() 


    #  **** REFRESH TOKEN OPERATIONS ****
    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> TokenResponse:

        # Validate refresh token
        user_id = decode_refresh_token(
            refresh_token,
        )

        if user_id is None:
            raise InvalidRefreshTokenException()

        # Find refresh token
        db_refresh_token = (
            await self.auth_repo.get_refresh_token(
                refresh_token,
            )
        )

        if db_refresh_token is None:
            raise InvalidRefreshTokenException()

        # Check refresh token expiration
        now = datetime.now(
            timezone.utc,
        )

        if db_refresh_token.expires_at < now:
            raise RefreshTokenExpiredException()

        # Find user
        user = await self.user_repo.get_one_by_id(
            model_id=user_id,
        )

        if user is None:
            raise UserNotFoundException()

        # Check user status
        if not user.is_active:
            raise UserInactiveException()

        if user.is_banned:
            raise UserBannedException()

        # Create new access token
        access_token = create_access_token(
            user.id,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )  
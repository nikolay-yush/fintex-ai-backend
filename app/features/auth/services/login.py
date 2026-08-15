import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.core.security.brute_force import BruteForceProtection

from app.features.auth.exceptions.authentication import (
    InvalidCredentialsException,
)
from app.features.auth.repositories.refresh_token import (
    RefreshTokenRepository,
)
from app.features.auth.schemas.authentication import (
    TokenResponse,
    UserLogin,
)
from app.features.auth.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.features.users.repository import UserRepository


class LoginService:
    def __init__(
        self,
        db_async_session: AsyncSession,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
        brute_force_protection: BruteForceProtection,
    ) -> None:
        self.db_async_session = db_async_session
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.brute_force_protection = brute_force_protection

    async def login(
        self,
        data: UserLogin,
        client_ip: str,
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
            await self.brute_force_protection.record_failed_attempt(
                data.email,
                client_ip,
            )

            delay = await self.brute_force_protection.get_delay(
                data.email,
                client_ip,
            )

            if delay > 0:
                await asyncio.sleep(delay)

            raise InvalidCredentialsException()

        # Reset brute-force attempts
        await self.brute_force_protection.reset_attempts(
            data.email,
            client_ip,
        )

        # Create refresh token family
        token_family = str(uuid4())

        # Generate refresh token
        refresh_token = create_refresh_token(
            user.id,
        )

        # Save refresh token
        await self.refresh_token_repo.create_refresh_token(
            {
                "token": refresh_token,
                "token_family": token_family,
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
                "revoked_at": None,
            },
        )

        # Generate access token
        access_token = create_access_token(
            user.id,
        )

        # Commit transaction
        await self.db_async_session.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
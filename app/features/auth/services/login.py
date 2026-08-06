from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings

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
    ) -> None:
        self.db_async_session = db_async_session
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo

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
            await self.refresh_token_repo.get_refresh_token_by_user_id(
                user.id,
            )
        )

        if old_refresh_token is not None:
            await self.refresh_token_repo.delete_refresh_token_by_id(
                old_refresh_token.id,
            )

        # Generate new refresh token
        refresh_token = create_refresh_token(
            user.id,
        )

        # Save refresh token
        await self.refresh_token_repo.create_refresh_token(
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
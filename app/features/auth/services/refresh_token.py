from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.features.auth.exceptions import (
    InvalidRefreshTokenException,
    RefreshTokenExpiredException,
    UserBannedException,
    UserInactiveException,
)
from app.features.auth.repositories.refresh_token import (
    RefreshTokenRepository,
)
from app.features.auth.schemas import TokenResponse
from app.features.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.features.users.exceptions import UserNotFoundException
from app.features.users.repository import UserRepository


class RefreshTokenService:
    def __init__(
        self,
        db_async_session: AsyncSession,
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository,
    ) -> None:
        self.db_async_session = db_async_session
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> TokenResponse:

        # Decode refresh token
        user_id = decode_refresh_token(
            refresh_token,
        )

        if user_id is None:
            raise InvalidRefreshTokenException()

        # Find refresh token
        db_refresh_token = (
            await self.refresh_token_repo.get_refresh_token(
                refresh_token,
            )
        )

        if db_refresh_token is None:
            raise InvalidRefreshTokenException()

        # Check expiration
        now = datetime.now(
            timezone.utc,
        )

        if db_refresh_token.expires_at < now:
            raise RefreshTokenExpiredException()

        # Find user
        user = await self.user_repo.get_one_by_id(
            user_id,
        )

        if user is None:
            raise UserNotFoundException()

        # Check user status
        if not user.is_active:
            raise UserInactiveException()

        if user.is_banned:
            raise UserBannedException()

        # Delete old refresh token
        await self.refresh_token_repo.delete_refresh_token_by_id(
            db_refresh_token.id,
        )

        # Generate new refresh token
        new_refresh_token = create_refresh_token(
            user.id,
        )

        # Save refresh token
        await self.refresh_token_repo.create_refresh_token(
            {
                "token": new_refresh_token,
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
            refresh_token=new_refresh_token,
        )
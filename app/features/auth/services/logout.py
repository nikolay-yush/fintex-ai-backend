from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.exceptions.refresh_token import (
    RefreshTokenNotFoundException,
)
from app.features.auth.repositories.refresh_token import (
    RefreshTokenRepository,
)


class LogoutService:
    def __init__(
        self,
        db_async_session: AsyncSession,
        refresh_token_repo: RefreshTokenRepository,
    ) -> None:
        self.db_async_session = db_async_session
        self.refresh_token_repo = refresh_token_repo

    async def logout(
        self,
        refresh_token: str,
    ) -> None:

        db_refresh_token = (
            await self.refresh_token_repo.get_refresh_token(
                refresh_token,
            )
        )

        if db_refresh_token is None:
            raise RefreshTokenNotFoundException()

        revoked = (
            await self.refresh_token_repo.revoke_refresh_token(
                db_refresh_token.id,
            )
        )

        if not revoked:
            raise RefreshTokenNotFoundException()

        await self.db_async_session.commit()

    async def logout_all_user_sessions(
        self,
        user_id: int,
    ) -> None:
        await self.refresh_token_repo.revoke_all_user_tokens(
                user_id,
            )
        await self.db_async_session.commit()

    async def logout_session(
        self,
        token_family: str,
        user_id: int,
    ) -> None:

        session_family = (
            await self.refresh_token_repo.get_token_family_for_user(
                token_family=token_family,
                user_id=user_id,
            )
        )

        if session_family is None:
            raise RefreshTokenNotFoundException()

        revoked = await self.refresh_token_repo.revoke_token_family(
            session_family,
        )

        if revoked == 0:
            raise RefreshTokenNotFoundException()

        await self.db_async_session.commit()
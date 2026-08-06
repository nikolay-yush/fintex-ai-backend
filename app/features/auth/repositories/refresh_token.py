from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.models.refresh_token import RefreshToken
from app.shared.base_crud import BaseCRUD


class RefreshTokenRepository(BaseCRUD[RefreshToken]):
    def __init__(self, db_async_session: AsyncSession) -> None:
        super().__init__(
            db_async_session=db_async_session,
            model=RefreshToken,
        )

    async def get_refresh_token(
        self,
        token: str,
    ) -> RefreshToken | None:

        query = select(
            RefreshToken,
        ).where(
            RefreshToken.token == token,
        )

        result = await self._db_async_session.execute(
            query,
        )

        return result.scalar_one_or_none()


    async def get_refresh_token_by_user_id(
        self,
        user_id: int,
    ) -> RefreshToken | None:

        query = select(
            RefreshToken,
        ).where(
            RefreshToken.user_id == user_id,
        )

        result = await self._db_async_session.execute(
            query,
        )

        return result.scalar_one_or_none()

    async def create_refresh_token(
        self,
        data: dict[str, Any],
    ) -> RefreshToken | None:
        return await self.create_one(data)

    async def delete_refresh_token_by_id(
        self,
        token_id: int,
    ) -> RefreshToken | None:
        return await self.delete_one(token_id)
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.auth.models.password_reset_token import PasswordResetToken
from app.shared.base_crud import BaseCRUD


class PasswordResetTokenRepository(BaseCRUD[PasswordResetToken]):
    def __init__(self, db_async_session: AsyncSession) -> None:
        super().__init__(
            db_async_session=db_async_session,
            model=PasswordResetToken,
        )
    async def get_reset_token(
        self,
        token: str,
    ) -> PasswordResetToken | None:

        query = select(
            PasswordResetToken,
        ).where(
            PasswordResetToken.token == token,
        )

        result = await self._db_async_session.execute(
            query,
        )

        return result.scalar_one_or_none()

    async def get_reset_token_by_user_id(
        self,
        user_id: int,
    ) -> PasswordResetToken | None:

        query = select(
            PasswordResetToken,
        ).where(
            PasswordResetToken.user_id == user_id,
        )

        result = await self._db_async_session.execute(
            query,
        )

        return result.scalar_one_or_none()

    async def create_reset_token(
        self,
        data: dict[str, Any],
    ) -> PasswordResetToken | None:
        return await self.create_one(data)

    async def delete_reset_token_by_id(
        self,
        id: int,
    ) -> PasswordResetToken | None:
        return await self.delete_one(id)
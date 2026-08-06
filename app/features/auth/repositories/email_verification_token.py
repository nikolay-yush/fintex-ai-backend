from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.auth.models.email_verification_token import EmailVerificationToken
from app.shared.base_crud import BaseCRUD


class EmailVerificationTokenRepository(BaseCRUD[EmailVerificationToken]):
    def __init__(self, db_async_session: AsyncSession) -> None:
        super().__init__(
            db_async_session=db_async_session,
            model=EmailVerificationToken,
        )

    async def create_verification_token(
        self,
        data: dict[str, Any]
    ) -> EmailVerificationToken | None:
        return await self.create_one(data)

    async def get_verification_token(
        self,
        token: str,
    ) -> EmailVerificationToken | None:
        query = select(
            EmailVerificationToken
        ).where(
            EmailVerificationToken.token == token,
        )

        result = await self._db_async_session.execute(query)

        return result.scalar_one_or_none()

    async def get_verification_token_by_user_id(
        self,
        user_id: int,
    ) -> EmailVerificationToken | None:
        query = select(
            EmailVerificationToken,
        ).where(
            EmailVerificationToken.user_id == user_id,
        )

        result = await self._db_async_session.execute(
            query,
        )

        return result.scalar_one_or_none()

    async def delete_verification_token_by_id(
        self,
        id: int,
    ) -> EmailVerificationToken | None:
        return await self.delete_one(id)

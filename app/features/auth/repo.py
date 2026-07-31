from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.auth.models import EmailVerificationToken
from app.shared.base_crud import BaseCRUD


class AuthRepository(BaseCRUD[EmailVerificationToken]):
    def __init__(self, db_async_session: AsyncSession) -> None:
        super().__init__(
            db_async_session=db_async_session,
            model=EmailVerificationToken,
        )

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
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, select, update
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

        
    async def delete_refresh_token(
        self,
        token: str,
    ) -> bool:

        query = (
            delete(RefreshToken)
            .where(RefreshToken.token == token)
            .returning(RefreshToken.id)
        )

        result = await self._db_async_session.execute(query)

        deleted_id = result.scalar_one_or_none()

        return deleted_id is not None

    async def delete_all_refresh_tokens(
        self,
        user_id: int,
    ) -> int:

        query = (
            delete(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
            )
            .returning(
                RefreshToken.id,
            )
        )

        result = await self._db_async_session.execute(
            query,
        )

        deleted_ids = result.scalars().all()

        return len(deleted_ids)

    async def revoke_refresh_token(
        self,
        token_id: int,
    ) -> bool:
        query = (
            update(RefreshToken)
            .where(
                RefreshToken.id == token_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(
                revoked_at=datetime.now(timezone.utc),
            )
            .returning(
                RefreshToken.id,
            )
        )

        revoked_id = await self._db_async_session.scalar(query)

        return revoked_id is not None

    async def revoke_token_family(
        self,
        token_family: str,
    ) -> int:
        query = (
            update(RefreshToken)
            .where(
                RefreshToken.token_family == token_family,
                RefreshToken.revoked_at.is_(None),
            )
            .values(
                revoked_at=datetime.now(timezone.utc),
            )
            .returning(RefreshToken.id)
        )

        revoked_ids = await self._db_async_session.scalars(
            query,
        )

        return len(revoked_ids.all())

    async def revoke_all_user_tokens(
        self,
        user_id: int,
    ) -> int:

        query = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(
                revoked_at=datetime.now(timezone.utc),
            )
            .returning(RefreshToken.id)
        )

        result = await self._db_async_session.execute(query)

        revoked_ids = result.scalars().all()

        return len(revoked_ids)

    async def get_token_family_for_user(
        self,
        token_family: str,
        user_id: int,
    ) -> str | None:

        query = (
            select(RefreshToken.token_family)
            .where(
                RefreshToken.token_family == token_family,
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .limit(1)
        )

        result = await self._db_async_session.execute(query)

        return result.scalar_one_or_none()
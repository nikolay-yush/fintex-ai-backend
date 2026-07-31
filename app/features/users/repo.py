from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.users.models import User
from app.features.users.schemas import UserFilters
from app.shared.base_crud import BaseCRUD


class UserRepository(BaseCRUD[User]):

    def __init__(self, db_async_session: AsyncSession) -> None:
        super().__init__(
            db_async_session=db_async_session,
            model=User,
        )
    async def get_user_by_email(self, email: str) -> User | None:
        query = select(self._model).where(self._model.email == email)
        result = await self._db_async_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_users_by_filters(
        self,
        filters: UserFilters,
    ) -> list[User]:
        query = select(User)

        if filters.email is not None:
            query = query.where(User.email == filters.email)

        if filters.full_name is not None:
            query = query.where(
                User.full_name.ilike(f"%{filters.full_name}%")
            )

        if filters.role is not None:
            query = query.where(User.role == filters.role)

        if filters.is_active is not None:
            query = query.where(
                User.is_active == filters.is_active
            )

        if filters.is_banned is not None:
            query = query.where(
                User.is_banned == filters.is_banned
            )

        if filters.last_seen_from is not None:
            query = query.where(
                User.last_seen_at >= filters.last_seen_from
            )

        if filters.last_seen_to is not None:
            query = query.where(
                User.last_seen_at <= filters.last_seen_to
            )

        if filters.last_login_from is not None:
            query = query.where(
                User.last_login_at >= filters.last_login_from
            )

        if filters.last_login_to is not None:
            query = query.where(
                User.last_login_at <= filters.last_login_to
            )

        if filters.created_from is not None:
            query = query.where(
                User.created_at >= filters.created_from
            )

        if filters.created_to is not None:
            query = query.where(
                User.created_at <= filters.created_to
            )

        if filters.updated_from is not None:
            query = query.where(
                User.updated_at >= filters.updated_from
            )

        if filters.updated_to is not None:
            query = query.where(
                User.updated_at <= filters.updated_to
            )

        query = query.order_by(User.id.desc())

        query = query.offset(filters.skip)
        query = query.limit(filters.limit)

        result = await self._db_async_session.execute(query)

        return list(result.scalars().all())

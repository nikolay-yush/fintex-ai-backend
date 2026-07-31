from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.postgres.session import get_async_session

from app.features.users.repo import UserRepository
from app.features.users.service import UserService


def get_user_repo(
    db_async_session: AsyncSession = Depends(get_async_session),
) -> UserRepository:
    return UserRepository(db_async_session=db_async_session)

def get_user_service(
    db_async_session: AsyncSession = Depends(get_async_session),
) -> UserService:
    user_repo = UserRepository(db_async_session=db_async_session)

    return UserService(
        db_async_session=db_async_session,
        user_repo=user_repo,
    )
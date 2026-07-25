from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.postgres.session import get_async_session

from app.features.users.repo import UserRepository
from app.features.users.service import UserService


def get_user_repo(
    db: AsyncSession = Depends(get_async_session),
) -> UserRepository:
    return UserRepository(db=db)

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
) -> UserService:
    return UserService(user_repo=user_repo)
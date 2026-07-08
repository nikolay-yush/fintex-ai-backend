from app.features.users.models import User
from app.features.users.repo import UserRepository
from app.features.users.schemas import (
    UserCreate,
    UserFilters,
    UserUpdateProfile,
)


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
    ) -> None:
        self.user_repo= user_repo

    #  **** READ OPERATIONS ****

    async def get_user_profile(
        self,
        current_user: User,
    ) -> User:
        return current_user
    
    async def get_user_by_id(
        self,
        user_id: int,
    ) -> User | None:
        return await self.user_repo.get_one_by_id(model_id=user_id)

    async def get_user_by_email(
        self,
        email: str,
    ) -> User | None:
        return await self.user_repo.get_user_by_email(email) 

    async def get_users_by_filters(
        self,
        filters: UserFilters,
    ) -> list[User]:
        return await self.user_repo.get_users_by_filters(filters)
    
    #  **** CREATE OPERATIONS ****
    async def create_user(
        self,
        data: UserCreate,
    ) -> User | None:
        values = data.model_dump()
        return await self.user_repo.create_one(values)
    
    #  *** UPDATE OPERATIONS ****
    async def update_user_profile(
        self,
        current_user: User,
        data: UserUpdateProfile,
    ) -> User | None:
        values = data.model_dump()
        return await self.user_repo.update_one(current_user.id, values)

    #  **** DELETE OPERATIONS ****
    async def delete_user(
        self,
        current_user: User,
    ) -> User | None:
        return await self.user_repo.delete_one(current_user.id)
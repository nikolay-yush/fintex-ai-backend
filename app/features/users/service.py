from app.features.users.models import User
from app.features.users.repo import UserRepository
from app.features.users.schemas import (
    UserCreate,
    UserFilters,
    UserUpdateProfile,
)
from app.features.users.exceptions import UserNotFoundException


class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
    ) -> None:
        self.user_repo= user_repo

    #  **** READ OPERATIONS ****
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
        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            return current_user 

        return await self.user_repo.update_one(
            current_user.id, 
            update_data
        )

    #  **** DELETE OPERATIONS ****
    async def delete_user_by_id(
        self,
        user_id: int,
    ) -> None:
        user = await self.user_repo.get_one_by_id(
            model_id=user_id,
        )

        if user is None:
            raise UserNotFoundException()

        await self.user_repo.delete_one(user_id)
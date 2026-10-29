from sqlalchemy.ext.asyncio import AsyncSession
from app.features.users.exceptions import UserAlreadyExistsException
from app.features.users.models import User
from app.features.users.repository import UsersRepository
from app.features.users.schemas import (
    UserCreate,
    UsersFilters,
    UserUpdateProfile,
)
from app.features.users.exceptions import UserNotFoundException
from app.features.users.schemas import UserResponse, UsersListResponse


class UsersService:
    def __init__(
        self,
        db_async_session: AsyncSession,
        user_repo: UsersRepository,
    ) -> None:
        self.db_async_session = db_async_session
        self.user_repo = user_repo

    #  **** READ OPERATIONS ****
    async def get_user_by_id(
        self,
        user_id: int,
    ) -> UserResponse | None:
        user = await self.user_repo.get_one_by_id(model_id=user_id)
        return UserResponse.model_validate(user) if user else None

    async def get_user_by_email(
        self,
        email: str,
    ) -> UserResponse | None:
        user = await self.user_repo.get_user_by_email(email)
        return UserResponse.model_validate(user) if user else None

    async def get_users_by_filters(
        self,
        filters: UsersFilters,
    ) -> tuple[list[UserResponse], int]:
        db_users, total = await self.user_repo.get_users_by_filters(filters)
        response_users = [UserResponse.model_validate(user) for user in db_users]
        return response_users, total

    #  **** CREATE OPERATIONS ****
    async def create_user(
        self,
        data: UserCreate,
    ) -> UserResponse | None:
        
        values = data.model_dump()
        user = await self.user_repo.create_one(values)

        if user is None:
            raise UserAlreadyExistsException()

        await self.db_async_session.commit()
        return UserResponse.model_validate(user)
        
    #  *** UPDATE OPERATIONS ****
    async def update_user_profile(
        self,
        current_user: User,
        data: UserUpdateProfile,
    ) -> UserResponse | None:
        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            return UserResponse.model_validate(current_user)

        user = await self.user_repo.update_one(
            current_user.id, 
            update_data
        )

        if user is None:
            raise UserNotFoundException()
        
        await self.db_async_session.commit()
        return UserResponse.model_validate(user)

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

        await self.db_async_session.commit()
        

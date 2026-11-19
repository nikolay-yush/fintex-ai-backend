from sqlalchemy.ext.asyncio import AsyncSession
from app.features.users.exceptions import UserAlreadyExistsException
from app.features.users.models import User
from app.features.users.repository import UsersRepository
from app.features.users.schemas import (
    UserCreate,
    UsersFilters,
    UserUpdateProfile,
)
from app.features.users.exceptions import UserNotFoundException, UserValidationException
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
    ) -> UserResponse:
        user = await self.user_repo.get_user_by_id(user_id)
        response_user = UserResponse.model_validate(user)
        
        if not response_user:
            raise UserNotFoundException()
        
        return response_user

    async def get_user_by_email(
        self,
        user_email: str,
    ) -> UserResponse:
        user = await self.user_repo.get_user_by_email(user_email)
        response_user = UserResponse.model_validate(user)
        
        if not response_user:
            raise UserNotFoundException() 
               
        return response_user

    async def get_users_by_filters(
        self,
        filters: UsersFilters,
    ) -> tuple[list[UserResponse], int]:
        db_users, total = await self.user_repo.get_users_by_filters(filters)
        response_users = [UserResponse.model_validate(user) for user in db_users]

        if not response_users:
            raise UserNotFoundException()
        
        return response_users, total

    #  **** CREATE OPERATIONS ****
    async def create_user(
        self,
        data: UserCreate,
    ) -> UserResponse:
        
        created_data = data.model_dump()
        
        if not created_data:
            raise UserValidationException()
        
        user = await self.user_repo.create_user(created_data)

        if user is None:
            raise UserAlreadyExistsException()

        await self.db_async_session.commit()
        return UserResponse.model_validate(user)
    

    #  *** UPDATE OPERATIONS ****
    async def update_user_profile(
        self,
        current_user: User,
        data: UserUpdateProfile,
    ) -> UserResponse:
        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            raise UserValidationException()

        user = await self.user_repo.update_user(
            user_id=current_user.id,
            data=update_data
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
        user = await self.user_repo.get_user_by_id(user_id)

        if user is None:
            raise UserNotFoundException()

        await self.user_repo.delete_user(user_id)

        await self.db_async_session.commit()
        

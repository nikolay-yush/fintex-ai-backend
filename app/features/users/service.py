from sqlalchemy.ext.asyncio import AsyncSession
from app.features.auth.exceptions import UserAlreadyExistsException
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
        db_async_session: AsyncSession,
        user_repo: UserRepository,
    ) -> None:
        self.db_async_session = db_async_session
        self.user_repo = user_repo

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
        user = await self.user_repo.create_one(values)

        if user is None:
            raise UserAlreadyExistsException()

        await self.db_async_session.commit()
        
        return user
    
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

        user = await self.user_repo.update_one(
            current_user.id, 
            update_data
        )

        if user is None:
            raise UserNotFoundException()
        
        await self.db_async_session.commit()
        return user

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
        

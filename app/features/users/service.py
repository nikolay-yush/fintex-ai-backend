from datetime import datetime, timezone

from app.features.users.repo import UserRepository
from app.features.users.models import User


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address."""
        return await self.user_repo.get_user_by_email(email)

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by their unique ID."""
        return await self.user_repo.get_one_by_id(user_id)
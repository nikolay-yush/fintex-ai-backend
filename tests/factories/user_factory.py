from datetime import datetime, timezone
from uuid import uuid4

from app.features.users.enums import UserRole
from app.features.users.models import User


class UserFactory:

    @staticmethod
    def build_dict(**kwargs) -> dict:
        """Build user data for tests."""

        now = datetime.now(timezone.utc)

        data = {
            "email": f"{uuid4().hex}@example.com",
            "hashed_password": "hashed_password",
            "full_name": "Test User",
            "email_verified": False,
            "role": UserRole.USER,
            "is_active": True,
            "is_banned": False,
            "last_seen_at": now,
            "created_at": now,
            "updated_at": now,
        }

        data.update(kwargs)

        return data

    @staticmethod
    def build_model(**kwargs) -> User:
        """Build User model without database."""

        return User(
            **UserFactory.build_dict(**kwargs),
        )
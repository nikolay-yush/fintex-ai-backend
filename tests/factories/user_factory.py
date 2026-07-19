from uuid import uuid4

from app.features.users.models import User


class UserFactory:

    @staticmethod
    def build_dict(**kwargs) -> dict:
        """Build user data for tests."""

        data = {
            "email": f"{uuid4().hex}@example.com",
            "hashed_password": "hashed_password",
            "full_name": "Test User",
        }

        data.update(kwargs)

        return data
    
    @staticmethod
    def build_model(**kwargs) -> User:
        """Build User model without database."""

        return User(
            **UserFactory.build_dict(**kwargs)
        )
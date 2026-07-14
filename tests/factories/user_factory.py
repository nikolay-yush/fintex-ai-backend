from uuid import uuid4


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
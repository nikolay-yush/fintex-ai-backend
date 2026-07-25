from app.features.auth.exceptions import InvalidCredentialsException, UserAlreadyExistsException
from app.features.auth.schemas import TokenResponse, UserLogin, UserRegister
from app.features.auth.security import create_access_token, hash_password, verify_password
from app.features.users.repo import UserRepository


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
    ) -> None:
        self.user_repo = user_repo

    async def register(
        self,
        data: UserRegister,
    ):
        # Check if user already exists
        existing_user = await self.user_repo.get_user_by_email(
            data.email,
        )

        if existing_user is not None:
            raise UserAlreadyExistsException()

        # Prepare data
        values = data.model_dump()

        # Hash password
        values["hashed_password"] = hash_password(
            values.pop("password"),
        )

        # Create user
        return await self.user_repo.create_one(values)

    async def login(
        self,
        data: UserLogin,
        ) -> TokenResponse:
            user = await self.user_repo.get_user_by_email(
                data.email,
            )

            if user is None:
                raise InvalidCredentialsException()

            if not verify_password(
                data.password,
                user.hashed_password,
            ):
                raise InvalidCredentialsException()

            access_token = create_access_token(
                user.id,
            )

            return TokenResponse(
                access_token=access_token,
            )
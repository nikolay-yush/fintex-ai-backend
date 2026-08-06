from fastapi import HTTPException, status


class UserAlreadyExistsException(HTTPException):
    def __init__(
        self,
        detail: str = "User with this email already exists",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class FailedToCreateUserException(HTTPException):
    def __init__(
        self,
        detail: str = "Failed to create user",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
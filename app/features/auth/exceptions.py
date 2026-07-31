from fastapi import HTTPException, status


class UserAlreadyExistsException(HTTPException):
    def __init__(self, detail: str = "User with this email already exists") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = "Invalid email or password") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

class FailedToCreateUserException(HTTPException):
    def __init__(self, detail: str = "Failed to create user") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )

class EmailVerificationTokenExpiredException(HTTPException):
    def __init__(self, detail: str = "Email verification token has expired") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

class EmailVerificationTokenNotFoundException(HTTPException):
    def __init__(self, detail: str = "Email verification token not found") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )

class EmailAlreadyVerifiedException(HTTPException):
    def __init__(self, detail: str = "Email already verified") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )   
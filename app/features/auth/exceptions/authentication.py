from fastapi import HTTPException, status


class InvalidCredentialsException(HTTPException):
    def __init__(
        self,
        detail: str = "Invalid email or password",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserInactiveException(HTTPException):
    def __init__(
        self,
        detail: str = "User account is inactive",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class UserBannedException(HTTPException):
    def __init__(
        self,
        detail: str = "User account is banned",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
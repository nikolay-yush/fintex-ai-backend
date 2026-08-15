from fastapi import HTTPException, status


class InvalidRefreshTokenException(HTTPException):
    def __init__(
        self,
        detail: str = "Invalid refresh token",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class RefreshTokenExpiredException(HTTPException):
    def __init__(
        self,
        detail: str = "Refresh token has expired",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class RefreshTokenNotFoundException(HTTPException):
    def __init__(
        self,
        detail: str = "Refresh token not found",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
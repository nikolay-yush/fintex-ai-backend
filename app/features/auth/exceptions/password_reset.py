from fastapi import HTTPException, status


class PasswordResetTokenExpiredException(HTTPException):
    def __init__(
        self,
        detail: str = "Password reset token has expired",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class PasswordResetTokenNotFoundException(HTTPException):
    def __init__(
        self,
        detail: str = "Password reset token not found",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )
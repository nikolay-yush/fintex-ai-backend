from fastapi import HTTPException, status


class EmailVerificationTokenExpiredException(HTTPException):
    def __init__(
        self,
        detail: str = "Email verification token has expired",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class EmailVerificationTokenNotFoundException(HTTPException):
    def __init__(
        self,
        detail: str = "Email verification token not found",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class EmailAlreadyVerifiedException(HTTPException):
    def __init__(
        self,
        detail: str = "Email already verified",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class FailedToCreateVerificationTokenException(HTTPException):
    def __init__(
        self,
        detail: str = "Failed to create email verification token",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
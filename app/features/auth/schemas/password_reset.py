from pydantic import BaseModel, EmailStr, Field, field_validator

from app.shared.validators import validate_password_strength


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")


class PasswordReset(BaseModel):
    token: str = Field(..., min_length=8, max_length=128, description="Reset token")
    password: str = Field(..., min_length=8, max_length=128, description="New password")

class PasswordResetConfirm(BaseModel):
    token: str = Field(..., min_length=8, max_length=128, description="Reset token")

    password: str = Field(
        min_length=8,
        max_length=128,
        description="New password"
    )

    @field_validator("password")
    @classmethod
    def validate_password(
        cls,
        value: str,
    ) -> str:
        return validate_password_strength(value)
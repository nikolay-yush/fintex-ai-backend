from pydantic import BaseModel, EmailStr, Field, field_validator

from app.shared.validators import validate_password_strength


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    password: str
    
class PasswordResetConfirm(BaseModel):
    token: str

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    @field_validator("password")
    @classmethod
    def validate_password(
        cls,
        value: str,
    ) -> str:
        return validate_password_strength(value)
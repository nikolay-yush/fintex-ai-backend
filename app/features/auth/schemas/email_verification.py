from pydantic import BaseModel, EmailStr, Field


class EmailVerificationRequest(BaseModel):
    token: str = Field(..., min_length=8, description="Email verification token")


class ResendVerificationRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
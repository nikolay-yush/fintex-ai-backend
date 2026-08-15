from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email address")

    password: str = Field(
        min_length=8,
        max_length=128,
        description="User's password"
    )


class TokenResponse(BaseModel):
    access_token: str = Field(..., min_length=8, description="Access token")
    refresh_token: str = Field(..., min_length=8, description="Refresh token")
    token_type: str = "bearer"
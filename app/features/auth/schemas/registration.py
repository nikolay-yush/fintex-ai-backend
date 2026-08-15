from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr = Field(..., description="User's email address")

    password: str = Field(
        min_length=8,
        max_length=128,
        description="User's password"
    )

    full_name: str = Field(
        min_length=1,
        max_length=100,
        description="User's full name"
    )
from pydantic import BaseModel, Field


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., min_length=8, description="Refresh token")


class LogoutAllRequest(BaseModel):
    user_id: int = Field(..., min_length=1, description="User's ID")

class LogoutSessionRequest(BaseModel):
    token_family: str = Field(..., min_length=8, description="Token family")